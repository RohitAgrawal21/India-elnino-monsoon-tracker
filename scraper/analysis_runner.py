"""
Runs the conditional-distribution engine across all macro and market series.
Outputs docs/analysis.json for the frontend tabs.
"""
import json
import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scraper.analog_engine import load_taxonomy, run_full_analysis, conditional_distributions, probability_weighted_outlook, compute_distribution
from scraper.macro_data import get_all_macro_series, AGRI_GDP_SHARE, PUBLISHED_SENSITIVITIES
from scraper.market_data import get_sector_data, get_watchlist, SECTOR_EXCESS_MONSOON, SECTOR_EXCESS_POST_MONSOON

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS_DIR = os.path.join(ROOT_DIR, "docs")


def run_macro_analysis(taxonomy, weights):
    """Run conditional-distribution engine on all macro variables."""
    macro_series = get_all_macro_series()
    results = {}

    for key, series_info in macro_series.items():
        analysis = run_full_analysis(
            series_info["data"],
            series_info["name"],
            weights=weights,
            taxonomy=taxonomy,
        )
        analysis["unit"] = series_info["unit"]
        analysis["source"] = series_info["source"]
        analysis["negative_is_bad"] = series_info["negative_is_bad"]
        results[key] = analysis

    # GDP drag calculation
    recent_agri_share = AGRI_GDP_SHARE.get(2024, 14.1)
    agri_gva = results.get("agri_gva_growth", {})
    if agri_gva and agri_gva.get("outlook_2026"):
        outlook = agri_gva["outlook_2026"]
        # GDP drag = agri_share * (agri_gva_growth - trend_growth)
        trend_agri_growth = 3.5  # approximate 5-year trend
        drag_from_mean = recent_agri_share / 100 * (outlook["weighted_mean"] - trend_agri_growth)
        results["gdp_drag_estimate"] = {
            "agri_share_pct": recent_agri_share,
            "trend_agri_growth": trend_agri_growth,
            "weighted_agri_growth_2026": outlook["weighted_mean"],
            "implied_gdp_drag_pct": round(drag_from_mean, 2),
            "range": [
                round(recent_agri_share / 100 * (outlook["weighted_range"][0] - trend_agri_growth), 2),
                round(recent_agri_share / 100 * (outlook["weighted_range"][1] - trend_agri_growth), 2),
            ],
            "note": "GDP drag = agri_share × (actual_agri_growth - trend). Negative = headwind to GDP.",
            "cross_check": PUBLISHED_SENSITIVITIES["monsoon_gdp_sensitivity"],
        }

    results["published_sensitivities"] = PUBLISHED_SENSITIVITIES
    return results


def run_sector_analysis(taxonomy, weights):
    """Run conditional-distribution engine on sector indices."""
    results = {}

    for sector_key, sector_info in SECTOR_EXCESS_MONSOON.items():
        # Monsoon window analysis
        monsoon_analysis = run_full_analysis(
            sector_info["data"],
            sector_info["name"] + " (Jun-Sep excess vs Nifty)",
            weights=weights,
            taxonomy=taxonomy,
        )
        monsoon_analysis["mechanism"] = sector_info["mechanism"]
        monsoon_analysis["ticker"] = sector_info.get("ticker", "")

        # Post-monsoon window
        post_data = SECTOR_EXCESS_POST_MONSOON.get(sector_key, {}).get("data", {})
        if post_data:
            post_analysis = run_full_analysis(
                post_data,
                sector_info["name"] + " (Oct-Mar excess vs Nifty)",
                weights=weights,
                taxonomy=taxonomy,
            )
        else:
            post_analysis = None

        results[sector_key] = {
            "name": sector_info["name"],
            "mechanism": sector_info["mechanism"],
            "monsoon_window": monsoon_analysis,
            "post_monsoon": post_analysis,
        }

    # Rank by headwind/tailwind
    rankings = []
    for key, sector in results.items():
        outlook = sector["monsoon_window"].get("outlook_2026")
        if outlook:
            rankings.append({
                "sector": sector["name"],
                "key": key,
                "weighted_mean_excess": outlook["weighted_mean"],
                "p_negative": outlook["p_negative"],
                "p_worse_than_minus5": outlook["p_worse_than_minus5"],
                "range": outlook["weighted_range"],
            })

    rankings.sort(key=lambda x: x["weighted_mean_excess"])

    return {
        "sectors": results,
        "rankings": rankings,
        "methodology": "Excess return = sector index return - Nifty50 return over same period. Conditional on rainfall bucket. 2026 weights applied.",
    }


def run_thematic_analysis(taxonomy, weights):
    """Run analysis on thematic baskets (sugar, fertilizer, etc.)."""
    from scraper.market_data import THEMATIC_BASKETS
    results = {}

    for key, basket in THEMATIC_BASKETS.items():
        analysis = run_full_analysis(
            basket["monsoon_excess"],
            basket["name"] + " (Jun-Sep excess vs Nifty)",
            weights=weights,
            taxonomy=taxonomy,
        )
        analysis["mechanism"] = basket["mechanism"]
        analysis["stocks"] = basket["stocks"]
        results[key] = analysis

    return results


def run_watchlist_analysis(taxonomy, weights):
    """Run analysis on expanded watchlist using sector proxies."""
    watchlist = get_watchlist()
    results = {"large_cap": {}, "mid_cap": {}, "small_cap": {}}

    # Map sectors to proxy indices
    sector_to_proxy = {
        "Auto/Tractors": "auto", "Two-Wheelers": "auto", "Tractors": "auto",
        "Farm Equipment": "auto",
        "FMCG": "fmcg", "Packaged Food": "fmcg", "Diversified/FMCG": "fmcg",
        "Dairy": "fmcg", "Rice/Basmati": "fmcg",
        "Banking": "bank", "PSU Banking": "bank", "Banking (Kerala)": "bank",
        "Gold Finance": "bank",
        "Jewellery": "fmcg",
        "Agrochemicals": "auto", "Crop Protection": "auto",
        "Fertilizers": "auto", "Fertilizer/Chemical": "auto",
        "Fertilizer (PSU)": "auto", "Agri-chemicals": "auto",
        "Sugar": "fmcg", "Sugar/Engineering": "fmcg",
        "IT Services": "it", "IT (Mid-cap)": "it",
        "Pharmaceuticals": "pharma", "Pharma": "pharma",
        "Energy/Telecom": "energy", "Power (Thermal)": "energy",
        "Power": "energy", "Power Utility": "energy", "Hydro/Solar Power": "energy",
        "Water Treatment": "pharma",  # defensive proxy
        "Pumps/Solar": "energy", "Industrial Pumps": "energy",
        "Electricals": "energy",
        "Micro-irrigation": "auto",
        "Aroma Chemicals": "pharma", "Ports/Logistics": "it",
        "Logistics": "it", "Media": "it",
        "Aquaculture": "fmcg",
    }

    for cap_key in ["large_cap", "mid_cap", "small_cap"]:
        cap_data = watchlist[cap_key]
        for direction in ["hurt_by_drought", "benefit_from_drought"]:
            stocks = cap_data.get(direction, [])
            analyzed = []
            for stock in stocks:
                proxy = sector_to_proxy.get(stock["sector"], "fmcg")
                proxy_data = SECTOR_EXCESS_MONSOON.get(proxy, {}).get("data", {})
                if proxy_data:
                    analysis = run_full_analysis(
                        proxy_data, stock["name"], weights=weights, taxonomy=taxonomy
                    )
                else:
                    analysis = None
                analyzed.append({
                    "ticker": stock["ticker"],
                    "name": stock["name"],
                    "sector": stock["sector"],
                    "why": stock["why"],
                    "direction": direction,
                    "proxy_sector": proxy,
                    "analysis": analysis,
                })
            if direction not in results[cap_key]:
                results[cap_key][direction] = []
            results[cap_key][direction] = analyzed

    return results


def get_analog_years(taxonomy, current_departure=-28):
    """Identify which past El Nino years 2026 currently resembles."""
    analogs = []
    for row in taxonomy["years"]:
        if row["elnino"] and row.get("elnino_bucket") == "ELNINO_LOW":
            analogs.append({
                "year": row["year"],
                "departure_pct": row["departure_pct"],
                "rain_mm": row["rain_mm"],
            })

    # Sort by how close departure is to current
    analogs.sort(key=lambda x: abs(x["departure_pct"] - current_departure))
    return analogs


def run():
    """Main entry point — generates analysis.json."""
    taxonomy = load_taxonomy()
    weights = taxonomy["2026_probability_model"]["weights"]
    run_time = datetime.now(timezone.utc).isoformat()

    print("=== Analysis Engine ===\n")

    print("  Running macro analysis...", flush=True)
    macro = run_macro_analysis(taxonomy, weights)
    print(f"  Done: {len(macro)} variables analyzed")

    print("  Running sector analysis...", flush=True)
    sectors = run_sector_analysis(taxonomy, weights)
    print(f"  Done: {len(sectors['sectors'])} sectors + rankings")

    print("  Running thematic baskets...", flush=True)
    thematic = run_thematic_analysis(taxonomy, weights)
    print(f"  Done: {len(thematic)} baskets")

    print("  Running watchlist analysis...", flush=True)
    watchlist = run_watchlist_analysis(taxonomy, weights)
    print(f"  Done: {len(watchlist)} stocks")

    print("  Computing analog years...", flush=True)
    analogs = get_analog_years(taxonomy)

    output = {
        "generated_at": run_time,
        "rainfall_weights_2026": weights,
        "rainfall_taxonomy_summary": taxonomy["summary"],
        "analog_years": analogs,
        "macro": macro,
        "sectors": sectors,
        "thematic": thematic,
        "watchlist": watchlist,
        "disclaimers": [
            "This is personal research, NOT investment advice.",
            "All figures are conditional distributions from historical analogs — past performance does not predict future results.",
            "Sample sizes are small (n=8 for El Nino drought years). Interpret with extreme caution.",
            "Individual stock analysis uses sector proxy data, not actual stock-level returns.",
            "The 2026 probability weights are model estimates that will shift as the season progresses.",
        ]
    }

    output_path = os.path.join(DOCS_DIR, "analysis.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"\n  Saved analysis.json ({os.path.getsize(output_path)} bytes)")

    return output


if __name__ == "__main__":
    run()
