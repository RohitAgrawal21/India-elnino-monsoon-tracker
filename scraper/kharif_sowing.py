import requests
import re
from datetime import datetime, timezone
from bs4 import BeautifulSoup

SOURCE_NAME = "Dept of Agriculture - Kharif Sowing"
SEARCH_URLS = [
    "https://agricoop.gov.in/en/StatisticsReport",
    "https://agricoop.gov.in/en/Major-Activites/crop-sowing",
    "https://pib.gov.in/allRel.aspx",
]

def fetch():
    for url in SEARCH_URLS:
        try:
            r = requests.get(url, timeout=30,
                           headers={"User-Agent": "Mozilla/5.0 (compatible; monsoon-tracker/1.0)"})
            if r.status_code == 200:
                return _try_parse(r.text, url)
        except Exception:
            continue

    return {
        "metric": "Kharif Sowing Progress",
        "value": None,
        "source": SOURCE_NAME,
        "source_url": SEARCH_URLS[0],
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "status": "stale",
        "note": "Kharif sowing data source is brittle. Updated weekly (Fridays) during Jun-Oct. Could not reach source."
    }

def _try_parse(html, url):
    try:
        soup = BeautifulSoup(html, "html.parser")
        text = soup.get_text(" ", strip=True)

        area_match = re.search(
            r'(?:area\s+sown|kharif.*?sowing).*?(\d+\.?\d*)\s*(?:lakh\s+ha|million\s+ha)',
            text, re.IGNORECASE
        )

        if area_match:
            area_current = float(area_match.group(1))
            ly_match = re.search(
                r'(?:last\s+year|previous\s+year|corresponding).*?(\d+\.?\d*)\s*(?:lakh\s+ha|million\s+ha)',
                text, re.IGNORECASE
            )
            area_last_year = float(ly_match.group(1)) if ly_match else None

            return {
                "metric": "Kharif Sowing Progress",
                "area_current_lakh_ha": area_current,
                "area_last_year_lakh_ha": area_last_year,
                "change_pct": round((area_current - area_last_year) / area_last_year * 100, 1) if area_last_year else None,
                "unit": "lakh hectares",
                "source": SOURCE_NAME,
                "source_url": url,
                "fetched_at": datetime.now(timezone.utc).isoformat(),
                "status": "ok"
            }
    except Exception:
        pass

    return {
        "metric": "Kharif Sowing Progress",
        "value": None,
        "source": SOURCE_NAME,
        "source_url": url,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "status": "stale",
        "note": "Could not parse kharif sowing data. This source is brittle and may require manual URL updates."
    }
