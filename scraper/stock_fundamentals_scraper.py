"""
Fetches REAL stock fundamentals from Yahoo Finance for all watchlist stocks.
Revenue, EBITDA%, PAT%, CMP, PE, EV/EBITDA, analyst estimates, industry medians.
"""
import json
import os
import sys
import time
from datetime import datetime, timezone

try:
    import yfinance as yf
except ImportError:
    print("ERROR: yfinance not installed. Run: pip install yfinance")
    sys.exit(1)

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS_DIR = os.path.join(ROOT_DIR, "docs")


def fetch_period_return(ticker_obj, period, cmp):
    """Calculate return over a period (1y/2y/5y). Returns % or None."""
    try:
        hist = ticker_obj.history(period=period)
        if hist.empty or len(hist) < 2:
            return None
        old_price = hist["Close"].iloc[0]
        if old_price and old_price > 0 and cmp:
            return round(((cmp / old_price) - 1) * 100, 1)
    except Exception:
        pass
    return None


def fetch_stock_data(ticker_symbol):
    """Fetch fundamentals for one stock. Returns dict or None on failure."""
    try:
        t = yf.Ticker(ticker_symbol)
        info = t.info
        if not info or info.get("regularMarketPrice") is None and info.get("currentPrice") is None:
            return None

        cmp = info.get("currentPrice") or info.get("regularMarketPrice")
        total_revenue = info.get("totalRevenue")
        revenue_cr = round(total_revenue / 1e7, 1) if total_revenue else None
        ebitda = info.get("ebitda")
        ebitda_cr = round(ebitda / 1e7, 1) if ebitda else None

        ret_1y = fetch_period_return(t, "1y", cmp)
        ret_2y = fetch_period_return(t, "2y", cmp)
        ret_5y = fetch_period_return(t, "5y", cmp)

        result = {
            "ticker": ticker_symbol,
            "cmp": round(cmp, 2) if cmp else None,
            "market_cap_cr": round(info.get("marketCap", 0) / 1e7, 0) if info.get("marketCap") else None,
            "revenue_cr": revenue_cr,
            "revenue_growth_pct": round(info.get("revenueGrowth", 0) * 100, 1) if info.get("revenueGrowth") is not None else None,
            "ebitda_cr": ebitda_cr,
            "ebitda_margin_pct": round(info.get("ebitdaMargins", 0) * 100, 1) if info.get("ebitdaMargins") is not None else None,
            "pat_margin_pct": round(info.get("profitMargins", 0) * 100, 1) if info.get("profitMargins") is not None else None,
            "ttm_pe": round(info.get("trailingPE", 0), 1) if info.get("trailingPE") else None,
            "forward_pe": round(info.get("forwardPE", 0), 1) if info.get("forwardPE") else None,
            "ev_ebitda": round(info.get("enterpriseToEbitda", 0), 1) if info.get("enterpriseToEbitda") else None,
            "pb_ratio": round(info.get("priceToBook", 0), 1) if info.get("priceToBook") else None,
            "dividend_yield_pct": round(info.get("dividendYield", 0) * 100, 2) if info.get("dividendYield") else None,
            "beta": round(info.get("beta", 0), 2) if info.get("beta") else None,
            "52w_high": info.get("fiftyTwoWeekHigh"),
            "52w_low": info.get("fiftyTwoWeekLow"),
            "return_1y_pct": ret_1y,
            "return_2y_pct": ret_2y,
            "return_5y_pct": ret_5y,
            "analyst_target_mean": info.get("targetMeanPrice"),
            "analyst_target_low": info.get("targetLowPrice"),
            "analyst_target_high": info.get("targetHighPrice"),
            "analyst_recommendation": info.get("recommendationKey"),
            "analyst_rating": info.get("averageAnalystRating"),
            "analyst_count": info.get("numberOfAnalystOpinions"),
            "sector": info.get("sector"),
            "industry": info.get("industry"),
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "status": "ok",
        }

        if cmp and result["analyst_target_mean"]:
            upside = ((result["analyst_target_mean"] / cmp) - 1) * 100
            result["analyst_upside_pct"] = round(upside, 1)

        return result
    except Exception as e:
        return {
            "ticker": ticker_symbol,
            "status": "error",
            "error": str(e),
            "fetched_at": datetime.now(timezone.utc).isoformat(),
        }


def compute_industry_medians(all_data):
    """Compute median PE and EV/EBITDA per industry group."""
    from collections import defaultdict
    industry_groups = defaultdict(list)
    for ticker, data in all_data.items():
        if data.get("status") != "ok":
            continue
        industry = data.get("industry")
        if not industry:
            continue
        industry_groups[industry].append(data)

    medians = {}
    for industry, stocks in industry_groups.items():
        pe_vals = [s["ttm_pe"] for s in stocks if s.get("ttm_pe") and s["ttm_pe"] > 0]
        ev_vals = [s["ev_ebitda"] for s in stocks if s.get("ev_ebitda") and s["ev_ebitda"] > 0]
        medians[industry] = {
            "median_pe": round(sorted(pe_vals)[len(pe_vals) // 2], 1) if pe_vals else None,
            "median_ev_ebitda": round(sorted(ev_vals)[len(ev_vals) // 2], 1) if ev_vals else None,
            "count": len(stocks),
        }
    return medians


def get_all_tickers():
    """Get all tickers from the watchlist."""
    sys.path.insert(0, ROOT_DIR)
    from scraper.market_data import get_watchlist
    watchlist = get_watchlist()
    tickers = []
    seen = set()
    for cap_key in ["large_cap", "mid_cap", "small_cap"]:
        cap_data = watchlist.get(cap_key, {})
        for direction in ["hurt_by_drought", "benefit_from_drought"]:
            for stock in cap_data.get(direction, []):
                t = stock["ticker"]
                if t not in seen:
                    tickers.append({
                        "ticker": t,
                        "name": stock["name"],
                        "cap": cap_key,
                        "direction": direction,
                    })
                    seen.add(t)
    return tickers


def run():
    """Fetch fundamentals for all watchlist stocks."""
    print("=== Stock Fundamentals Scraper (Real Data) ===\n")

    tickers = get_all_tickers()
    print(f"  {len(tickers)} unique stocks to fetch\n")

    all_data = {}
    ok_count = 0
    err_count = 0

    for i, stock in enumerate(tickers):
        ticker = stock["ticker"]
        print(f"  [{i+1}/{len(tickers)}] {stock['name']} ({ticker})...", end=" ", flush=True)
        data = fetch_stock_data(ticker)

        if data and data.get("status") == "ok":
            all_data[ticker] = data
            print(f"CMP={data['cmp']}, PE={data['ttm_pe']}, EV/EBITDA={data['ev_ebitda']}")
            ok_count += 1
        else:
            all_data[ticker] = data or {"ticker": ticker, "status": "error", "error": "no data"}
            print("FAILED")
            err_count += 1

        if (i + 1) % 10 == 0:
            time.sleep(1)

    industry_medians = compute_industry_medians(all_data)

    for ticker, data in all_data.items():
        if data.get("status") == "ok" and data.get("industry"):
            med = industry_medians.get(data["industry"], {})
            data["industry_median_pe"] = med.get("median_pe")
            data["industry_median_ev_ebitda"] = med.get("median_ev_ebitda")

    output = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": "Yahoo Finance",
        "total_stocks": len(tickers),
        "ok": ok_count,
        "errors": err_count,
        "stocks": all_data,
        "industry_medians": industry_medians,
    }

    output_path = os.path.join(DOCS_DIR, "stock_fundamentals.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"\n  Saved stock_fundamentals.json ({os.path.getsize(output_path)} bytes)")
    print(f"  OK: {ok_count}, Errors: {err_count}")

    return output


if __name__ == "__main__":
    run()
