"""
Correlate India monsoon rainfall (JJAS) with post-monsoon EXCESS stock returns.
Excess return = stock return - Nifty 50 return (isolates monsoon-specific effect).

For each stock: fetch 6-month and 1-year excess returns after each monsoon season,
run linear regression against rainfall, and project 2026 excess returns.

Uses last 10 years of data (2014-2024), excluding COVID years (2020, 2021).
"""
import json
import os
import sys
import math
from datetime import datetime, timezone

try:
    import yfinance as yf
except ImportError:
    print("ERROR: yfinance not installed. Run: pip install yfinance")
    sys.exit(1)

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS_DIR = os.path.join(ROOT_DIR, "docs")

# India Monsoon Season (June-September) total rainfall in mm
# Source: India Meteorological Department (IMD) official records
# https://mausam.imd.gov.in/
JJAS_RAINFALL_MM = {
    2014: 781.9,
    2015: 766.0,
    2016: 862.6,
    2017: 840.5,
    2018: 804.1,
    2019: 968.3,
    # 2020 excluded (COVID)
    # 2021 excluded (COVID)
    2022: 925.4,
    2023: 820.4,
    2024: 934.8,
}

YEARS = sorted(JJAS_RAINFALL_MM.keys())

# 2026 estimated rainfall from our probability model
ESTIMATED_2026_RAINFALL = round(0.55 * 760 + 0.40 * 880 + 0.05 * 950, 0)

NIFTY_TICKER = "^NSEI"


def get_price_on_date(hist, target_year, target_month, target_day=30):
    """Get closing price nearest to a target date from historical data."""
    import pandas as pd
    tz = hist.index.tz
    target = pd.Timestamp(target_year, target_month, min(target_day, 28), tz=tz)
    window_start = target - pd.Timedelta(days=15)
    window_end = target + pd.Timedelta(days=15)
    mask = (hist.index >= window_start) & (hist.index <= window_end)
    subset = hist[mask]
    if subset.empty:
        return None
    idx = (subset.index - target).map(abs).argmin()
    return float(subset["Close"].iloc[idx])


def compute_returns_for_hist(hist):
    """Given a price history, compute 6M and 1Y returns for each monsoon year."""
    results = {}
    for year in YEARS:
        sep_price = get_price_on_date(hist, year, 9, 30)
        mar_price = get_price_on_date(hist, year + 1, 3, 31)
        sep_next_price = get_price_on_date(hist, year + 1, 9, 30)

        if sep_price and sep_price > 0:
            ret_6m = ((mar_price / sep_price) - 1) * 100 if mar_price else None
            ret_1y = ((sep_next_price / sep_price) - 1) * 100 if sep_next_price else None
            results[year] = {
                "return_6m_pct": round(ret_6m, 2) if ret_6m is not None else None,
                "return_1y_pct": round(ret_1y, 2) if ret_1y is not None else None,
            }
    return results


def linear_regression(x_vals, y_vals):
    """Simple OLS: y = a + b*x. Returns dict or None if <2 data points."""
    n = len(x_vals)
    if n < 2:
        return None

    sum_x = sum(x_vals)
    sum_y = sum(y_vals)
    sum_xy = sum(x * y for x, y in zip(x_vals, y_vals))
    sum_x2 = sum(x * x for x in x_vals)
    sum_y2 = sum(y * y for y in y_vals)

    denom = n * sum_x2 - sum_x * sum_x
    if denom == 0:
        return None

    b = (n * sum_xy - sum_x * sum_y) / denom
    a = (sum_y - b * sum_x) / n

    ss_res = sum((y - (a + b * x)) ** 2 for x, y in zip(x_vals, y_vals))
    ss_tot = sum((y - sum_y / n) ** 2 for y in y_vals)
    r_sq = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0

    denom_r = math.sqrt((n * sum_x2 - sum_x ** 2) * (n * sum_y2 - sum_y ** 2))
    corr = (n * sum_xy - sum_x * sum_y) / denom_r if denom_r > 0 else 0

    return {
        "intercept": round(a, 4),
        "slope": round(b, 4),
        "r_squared": round(max(0, r_sq), 4),
        "correlation": round(corr, 4),
        "n_years": n,
    }


def analyze_stock(ticker, name, nifty_returns):
    """Full analysis for one stock using excess returns."""
    try:
        t = yf.Ticker(ticker)
        hist = t.history(start="2014-01-01", end="2026-04-01")
        if hist.empty or len(hist) < 50:
            return None
    except Exception:
        return None

    stock_returns = compute_returns_for_hist(hist)
    if not stock_returns:
        return None

    # Compute excess returns (stock - Nifty)
    year_data = {}
    for year in YEARS:
        if year not in stock_returns or year not in nifty_returns:
            continue
        sr = stock_returns[year]
        nr = nifty_returns[year]

        excess_6m = None
        excess_1y = None
        if sr["return_6m_pct"] is not None and nr["return_6m_pct"] is not None:
            excess_6m = round(sr["return_6m_pct"] - nr["return_6m_pct"], 2)
        if sr["return_1y_pct"] is not None and nr["return_1y_pct"] is not None:
            excess_1y = round(sr["return_1y_pct"] - nr["return_1y_pct"], 2)

        year_data[year] = {
            "rainfall_mm": JJAS_RAINFALL_MM[year],
            "stock_return_6m": sr["return_6m_pct"],
            "stock_return_1y": sr["return_1y_pct"],
            "nifty_return_6m": nr["return_6m_pct"],
            "nifty_return_1y": nr["return_1y_pct"],
            "excess_return_6m": excess_6m,
            "excess_return_1y": excess_1y,
        }

    # Build regression data
    rain_6m, exc_6m_vals = [], []
    rain_1y, exc_1y_vals = [], []

    for year in YEARS:
        if year not in year_data:
            continue
        d = year_data[year]
        if d["excess_return_6m"] is not None:
            rain_6m.append(d["rainfall_mm"])
            exc_6m_vals.append(d["excess_return_6m"])
        if d["excess_return_1y"] is not None:
            rain_1y.append(d["rainfall_mm"])
            exc_1y_vals.append(d["excess_return_1y"])

    reg_6m = linear_regression(rain_6m, exc_6m_vals)
    reg_1y = linear_regression(rain_1y, exc_1y_vals)

    proj_6m = None
    proj_1y = None
    if reg_6m:
        raw = reg_6m["intercept"] + reg_6m["slope"] * ESTIMATED_2026_RAINFALL
        proj_6m = round(max(-50, min(50, raw)), 1)
    if reg_1y:
        raw = reg_1y["intercept"] + reg_1y["slope"] * ESTIMATED_2026_RAINFALL
        proj_1y = round(max(-80, min(80, raw)), 1)

    # Determine sample quality flag
    n6 = reg_6m["n_years"] if reg_6m else 0
    n1 = reg_1y["n_years"] if reg_1y else 0

    sample_flag_6m = None
    sample_flag_1y = None
    if 0 < n6 <= 3:
        sample_flag_6m = f"Very small sample ({n6} yr{'s' if n6 > 1 else ''}) — treat with caution"
    elif 3 < n6 <= 5:
        sample_flag_6m = f"Small sample ({n6} yrs)"
    if 0 < n1 <= 3:
        sample_flag_1y = f"Very small sample ({n1} yr{'s' if n1 > 1 else ''}) — treat with caution"
    elif 3 < n1 <= 5:
        sample_flag_1y = f"Small sample ({n1} yrs)"

    return {
        "ticker": ticker,
        "name": name,
        "year_data": year_data,
        "regression_6m": reg_6m,
        "regression_1y": reg_1y,
        "estimated_rainfall_2026_mm": ESTIMATED_2026_RAINFALL,
        "projected_excess_return_6m_pct": proj_6m,
        "projected_excess_return_1y_pct": proj_1y,
        "sample_flag_6m": sample_flag_6m,
        "sample_flag_1y": sample_flag_1y,
    }


def get_all_tickers():
    """Get all tickers from the watchlist."""
    sys.path.insert(0, ROOT_DIR)
    from scraper.market_data import get_watchlist
    watchlist = get_watchlist()
    tickers = []
    seen = set()
    skip = {"SJVN.NS", "CESC.NS"}
    for cap_key in ["large_cap", "mid_cap", "small_cap"]:
        cap_data = watchlist.get(cap_key, {})
        for direction in ["benefit_from_drought", "hurt_by_drought"]:
            for stock in cap_data.get(direction, []):
                t = stock["ticker"]
                if t not in seen and t not in skip:
                    tickers.append({"ticker": t, "name": stock["name"]})
                    seen.add(t)
    return tickers


def run():
    print("=== Rainfall-Stock Correlation (Excess Returns) ===\n")
    print(f"  Monsoon years: {YEARS}")
    print(f"  Estimated 2026 rainfall: {ESTIMATED_2026_RAINFALL} mm\n")

    # First fetch Nifty 50 returns as benchmark
    print("  Fetching Nifty 50 benchmark returns...", flush=True)
    try:
        nifty = yf.Ticker(NIFTY_TICKER)
        nifty_hist = nifty.history(start="2014-01-01", end="2026-04-01")
        nifty_returns = compute_returns_for_hist(nifty_hist)
        print(f"  Nifty data: {len(nifty_returns)} years\n")
    except Exception as e:
        print(f"  FAILED to fetch Nifty: {e}")
        return

    tickers = get_all_tickers()
    print(f"  {len(tickers)} stocks to analyze\n")

    all_results = {}
    ok = 0
    fail = 0

    for i, stock in enumerate(tickers):
        ticker = stock["ticker"]
        name = stock["name"]
        print(f"  [{i+1}/{len(tickers)}] {name:30s} ({ticker:20s}) ... ", end="", flush=True)

        result = analyze_stock(ticker, name, nifty_returns)
        if result and (result["regression_6m"] or result["regression_1y"]):
            all_results[ticker] = result
            n6 = result["regression_6m"]["n_years"] if result["regression_6m"] else 0
            n1 = result["regression_1y"]["n_years"] if result["regression_1y"] else 0
            c6 = result["regression_6m"]["correlation"] if result["regression_6m"] else 0
            c1 = result["regression_1y"]["correlation"] if result["regression_1y"] else 0
            p6 = result["projected_excess_return_6m_pct"]
            p1 = result["projected_excess_return_1y_pct"]
            p6s = f"{p6:+.1f}%" if p6 is not None else "N/A"
            p1s = f"{p1:+.1f}%" if p1 is not None else "N/A"
            flag = ""
            if n6 <= 3 or n1 <= 3:
                flag = " ** SMALL SAMPLE"
            print(f"n={n6}/{n1}  r6m={c6:+.2f}  r1y={c1:+.2f}  exc6m={p6s}  exc1y={p1s}{flag}")
            ok += 1
        else:
            print("INSUFFICIENT DATA")
            fail += 1

    output = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "methodology": {
            "description": "Linear regression of post-monsoon EXCESS stock returns (stock return minus Nifty 50 return) against JJAS monsoon rainfall. Excess returns isolate the monsoon-specific effect by stripping out the broader market movement.",
            "rainfall_source": "India Meteorological Department (IMD)",
            "price_source": "Yahoo Finance",
            "benchmark": "Nifty 50 (^NSEI)",
            "years_used": YEARS,
            "excluded_years": [2020, 2021],
            "exclusion_reason": "COVID-19 pandemic distorted market behavior",
            "return_periods": {
                "6m": "September 30 to March 31 of next year",
                "1y": "September 30 to September 30 of next year"
            },
            "model": "Simple OLS linear regression: excess_return = intercept + slope × rainfall_mm",
            "projection_caps": "6M capped at ±50%, 1Y capped at ±80% to limit outlier influence",
            "disclaimer": "This is an estimation based on historical trends, not a projection or investment advice. Correlation does not imply causation. Many factors beyond rainfall affect stock prices."
        },
        "estimated_rainfall_2026_mm": ESTIMATED_2026_RAINFALL,
        "rainfall_2026_basis": "Weighted estimate: P(Low=760mm)=55%, P(Normal=880mm)=40%, P(High=950mm)=5%",
        "nifty_returns": nifty_returns,
        "stocks": all_results,
        "total_analyzed": ok,
        "insufficient_data": fail,
    }

    output_path = os.path.join(DOCS_DIR, "rainfall_correlation.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"\n  Saved rainfall_correlation.json ({os.path.getsize(output_path)} bytes)")
    print(f"  OK: {ok}, Insufficient data: {fail}")

    return output


if __name__ == "__main__":
    run()
