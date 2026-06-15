"""
Fetches REAL historical sector index returns from Yahoo Finance.
Computes actual Jun-Sep and Oct-Mar excess returns vs Nifty50 for each sector.
Replaces the estimated data in market_data.py with verified numbers.
"""
import json
import os
import sys
from datetime import datetime, timezone

try:
    import yfinance as yf
except ImportError:
    print("ERROR: yfinance not installed. Run: pip install yfinance")
    sys.exit(1)

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS_DIR = os.path.join(ROOT_DIR, "docs")

SECTOR_TICKERS = {
    "auto": {"ticker": "^CNXAUTO", "name": "Nifty Auto"},
    "bank": {"ticker": "^NSEBANK", "name": "Nifty Bank"},
    "fmcg": {"ticker": "^CNXFMCG", "name": "Nifty FMCG"},
    "it": {"ticker": "^CNXIT", "name": "Nifty IT"},
    "pharma": {"ticker": "^CNXPHARMA", "name": "Nifty Pharma"},
    "metal": {"ticker": "^CNXMETAL", "name": "Nifty Metal"},
    "energy": {"ticker": "^CNXENERGY", "name": "Nifty Energy"},
    "realty": {"ticker": "^CNXREALTY", "name": "Nifty Realty"},
}
NIFTY_TICKER = "^NSEI"


def fetch_monthly_closes(ticker_symbol, start="2004-01-01"):
    """Fetch monthly closing prices for a ticker."""
    try:
        t = yf.Ticker(ticker_symbol)
        hist = t.history(start=start, interval="1mo")
        if hist.empty:
            hist = t.history(start=start, interval="1d")
            if hist.empty:
                return {}
            hist = hist.resample("ME").last()

        closes = {}
        for date, row in hist.iterrows():
            key = (date.year, date.month)
            closes[key] = row["Close"]
        return closes
    except Exception as e:
        print(f"  WARNING: Could not fetch {ticker_symbol}: {e}")
        return {}


def compute_period_return(closes, year, start_month, end_month):
    """Compute return from start of start_month to end of end_month."""
    if start_month <= end_month:
        start_key = (year, start_month)
        end_key = (year, end_month)
    else:
        start_key = (year, start_month)
        end_key = (year + 1, end_month)

    prev_month = start_month - 1
    prev_year = year
    if prev_month < 1:
        prev_month = 12
        prev_year = year - 1
    open_key = (prev_year, prev_month)

    if open_key not in closes or end_key not in closes:
        return None

    open_price = closes[open_key]
    close_price = closes[end_key]
    if open_price <= 0:
        return None
    return ((close_price / open_price) - 1) * 100


def compute_excess_returns(sector_closes, nifty_closes, start_month, end_month):
    """Compute year-by-year excess returns (sector - nifty) for a period."""
    all_years = set()
    for (y, m) in sector_closes:
        all_years.add(y)

    excess = {}
    for year in sorted(all_years):
        sector_ret = compute_period_return(sector_closes, year, start_month, end_month)
        nifty_ret = compute_period_return(nifty_closes, year, start_month, end_month)
        if sector_ret is not None and nifty_ret is not None:
            excess[year] = round(sector_ret - nifty_ret, 2)
    return excess


def run():
    """Fetch all sector data and save to sector_returns.json."""
    print("=== Sector Returns Scraper (Real Data) ===\n")

    print("  Fetching Nifty 50 monthly closes...", flush=True)
    nifty_closes = fetch_monthly_closes(NIFTY_TICKER)
    if not nifty_closes:
        print("  ERROR: Could not fetch Nifty 50 data. Aborting.")
        return None
    years_available = sorted(set(y for y, m in nifty_closes.keys()))
    print(f"  Nifty 50: {len(nifty_closes)} monthly points, {years_available[0]}-{years_available[-1]}")

    results = {}
    for key, info in SECTOR_TICKERS.items():
        print(f"  Fetching {info['name']} ({info['ticker']})...", flush=True)
        sector_closes = fetch_monthly_closes(info["ticker"])
        if not sector_closes:
            print(f"    SKIPPED: no data for {info['ticker']}")
            continue

        monsoon_excess = compute_excess_returns(sector_closes, nifty_closes, 6, 9)
        post_monsoon_excess = compute_excess_returns(sector_closes, nifty_closes, 10, 3)

        results[key] = {
            "name": info["name"],
            "ticker": info["ticker"],
            "monsoon_excess": monsoon_excess,
            "post_monsoon_excess": post_monsoon_excess,
            "years_available": sorted(monsoon_excess.keys()),
            "data_points_monsoon": len(monsoon_excess),
            "data_points_post": len(post_monsoon_excess),
        }
        print(f"    {info['name']}: {len(monsoon_excess)} monsoon years, {len(post_monsoon_excess)} post-monsoon years")

        if monsoon_excess:
            vals = list(monsoon_excess.values())
            avg = sum(vals) / len(vals)
            print(f"    Average monsoon excess: {avg:+.2f}%")

    output = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": "Yahoo Finance (NSE sector indices)",
        "benchmark": "Nifty 50 (^NSEI)",
        "methodology": "Excess return = sector index % change - Nifty50 % change over same period. Monthly close-to-close.",
        "sectors": results,
    }

    output_path = os.path.join(DOCS_DIR, "sector_returns.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"\n  Saved sector_returns.json ({os.path.getsize(output_path)} bytes)")

    return output


if __name__ == "__main__":
    run()
