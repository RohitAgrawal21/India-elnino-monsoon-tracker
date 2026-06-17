"""
Correlate India monsoon rainfall (JJAS) with post-monsoon stock returns.
For each stock: fetch 6-month and 1-year returns after each monsoon season,
run linear regression against rainfall, and project 2026 returns.

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
# P(LOW)=55% → ~760mm, P(NORMAL)=40% → ~880mm, P(HIGH)=5% → ~950mm
# Weighted estimate
ESTIMATED_2026_RAINFALL = round(0.55 * 760 + 0.40 * 880 + 0.05 * 950, 0)


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


def compute_returns(ticker_symbol):
    """For each monsoon year, compute 6M and 1Y post-monsoon returns."""
    try:
        t = yf.Ticker(ticker_symbol)
        hist = t.history(start="2014-01-01", end="2026-04-01")
        if hist.empty or len(hist) < 100:
            return None
    except Exception:
        return None

    results = {}
    for year in YEARS:
        sep_price = get_price_on_date(hist, year, 9, 30)
        mar_price = get_price_on_date(hist, year + 1, 3, 31)
        sep_next_price = get_price_on_date(hist, year + 1, 9, 30)

        if sep_price and sep_price > 0:
            ret_6m = ((mar_price / sep_price) - 1) * 100 if mar_price else None
            ret_1y = ((sep_next_price / sep_price) - 1) * 100 if sep_next_price else None
            results[year] = {
                "rainfall_mm": JJAS_RAINFALL_MM[year],
                "sep_price": round(sep_price, 2),
                "return_6m_pct": round(ret_6m, 2) if ret_6m is not None else None,
                "return_1y_pct": round(ret_1y, 2) if ret_1y is not None else None,
            }

    return results


def linear_regression(x_vals, y_vals):
    """Simple OLS: y = a + b*x. Returns (a, b, r_squared, correlation)."""
    n = len(x_vals)
    if n < 3:
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
        "r_squared": round(r_sq, 4),
        "correlation": round(corr, 4),
        "n_years": n,
    }


def analyze_stock(ticker, name):
    """Full analysis for one stock."""
    year_data = compute_returns(ticker)
    if not year_data:
        return None

    rain_6m, ret_6m_vals = [], []
    rain_1y, ret_1y_vals = [], []

    for year in YEARS:
        if year not in year_data:
            continue
        d = year_data[year]
        if d["return_6m_pct"] is not None:
            rain_6m.append(d["rainfall_mm"])
            ret_6m_vals.append(d["return_6m_pct"])
        if d["return_1y_pct"] is not None:
            rain_1y.append(d["rainfall_mm"])
            ret_1y_vals.append(d["return_1y_pct"])

    reg_6m = linear_regression(rain_6m, ret_6m_vals)
    reg_1y = linear_regression(rain_1y, ret_1y_vals)

    proj_6m = None
    proj_1y = None
    if reg_6m:
        proj_6m = round(reg_6m["intercept"] + reg_6m["slope"] * ESTIMATED_2026_RAINFALL, 1)
    if reg_1y:
        proj_1y = round(reg_1y["intercept"] + reg_1y["slope"] * ESTIMATED_2026_RAINFALL, 1)

    return {
        "ticker": ticker,
        "name": name,
        "year_data": year_data,
        "regression_6m": reg_6m,
        "regression_1y": reg_1y,
        "estimated_rainfall_2026_mm": ESTIMATED_2026_RAINFALL,
        "projected_return_6m_pct": proj_6m,
        "projected_return_1y_pct": proj_1y,
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
    print("=== Rainfall-Stock Correlation Analysis ===\n")
    print(f"  Monsoon years: {YEARS}")
    print(f"  Estimated 2026 rainfall: {ESTIMATED_2026_RAINFALL} mm\n")

    tickers = get_all_tickers()
    print(f"  {len(tickers)} stocks to analyze\n")

    all_results = {}
    ok = 0
    fail = 0

    for i, stock in enumerate(tickers):
        ticker = stock["ticker"]
        name = stock["name"]
        print(f"  [{i+1}/{len(tickers)}] {name:30s} ({ticker:20s}) ... ", end="", flush=True)

        result = analyze_stock(ticker, name)
        if result and result["regression_6m"]:
            all_results[ticker] = result
            corr6 = result["regression_6m"]["correlation"]
            corr1 = result["regression_1y"]["correlation"] if result["regression_1y"] else None
            p6 = result["projected_return_6m_pct"]
            p1 = result["projected_return_1y_pct"]
            c1s = f"{corr1:+.2f}" if corr1 is not None else "N/A"
            p1s = f"{p1:+.1f}%" if p1 is not None else "N/A"
            print(f"r6m={corr6:+.2f}  r1y={c1s}  proj6m={p6:+.1f}%  proj1y={p1s}")
            ok += 1
        else:
            print("INSUFFICIENT DATA")
            fail += 1

    output = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "methodology": {
            "description": "Linear regression of post-monsoon stock returns against JJAS monsoon rainfall",
            "rainfall_source": "India Meteorological Department (IMD)",
            "price_source": "Yahoo Finance",
            "years_used": YEARS,
            "excluded_years": [2020, 2021],
            "exclusion_reason": "COVID-19 pandemic distorted market behavior",
            "return_periods": {
                "6m": "September 30 to March 31 of next year",
                "1y": "September 30 to September 30 of next year"
            },
            "model": "Simple OLS linear regression: return = intercept + slope * rainfall_mm",
            "disclaimer": "This is an estimation based on historical trends, not a projection or investment advice. Correlation does not imply causation. Many factors beyond rainfall affect stock prices."
        },
        "estimated_rainfall_2026_mm": ESTIMATED_2026_RAINFALL,
        "rainfall_2026_basis": "Weighted estimate: P(LOW=760mm)=55%, P(NORMAL=880mm)=40%, P(HIGH=950mm)=5%",
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
