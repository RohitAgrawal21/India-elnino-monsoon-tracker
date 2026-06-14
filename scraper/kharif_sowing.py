import requests
import re
from datetime import datetime, timezone
from bs4 import BeautifulSoup

SOURCE_NAME = "Dept of Agriculture - Kharif Sowing"
SEARCH_URLS = [
    "https://agricoop.gov.in/en/StatisticsReport",
    "https://agricoop.gov.in/en/Major-Activites/crop-sowing",
    "https://pib.gov.in/allRel.aspx",
    "https://agriwelfare.gov.in/en/Major",
]

KHARIF_CROPS = "rice, pulses (arhar, moong, urad), oilseeds (soybean, groundnut), cotton, sugarcane, coarse cereals"
SOWING_WINDOW = "Kharif sowing runs June-August, peaking in July. Depends on monsoon onset and early rainfall."


def fetch():
    for url in SEARCH_URLS:
        try:
            r = requests.get(url, timeout=30,
                           headers={"User-Agent": "Mozilla/5.0 (compatible; monsoon-tracker/1.0)"})
            if r.status_code == 200:
                result = _try_parse(r.text, url)
                if result and result.get("status") == "ok":
                    return result
        except Exception:
            continue

    now = datetime.now(timezone.utc)
    month = now.month

    if month < 6:
        season_note = "Kharif sowing has not begun yet (starts in June with monsoon onset). Official data will be available from mid-June onwards."
        sowing_status = "pre_season"
    elif month == 6 and now.day <= 20:
        season_note = ("Kharif sowing just started (monsoon onset happened in early June). "
                      "The first weekly Crop Situation Report from DACFW typically publishes "
                      "around June 20-27. Early sowing is underway for rice, pulses, and oilseeds.")
        sowing_status = "early_season"
    elif month <= 10:
        season_note = ("Kharif sowing season is active (Jun-Oct). "
                      "Official weekly reports from the Dept of Agriculture are not reachable from this scraper. "
                      "Historically, sowing progress tracks closely with monsoon rainfall timing and coverage.")
        sowing_status = "in_season"
    else:
        season_note = "Kharif sowing season ended (Jun-Oct). Harvest is underway or complete."
        sowing_status = "post_season"

    # News-reported context (verified from Economic Times, Jun 9-13 2026)
    news_context = None
    if now.year == 2026 and 6 <= month <= 10:
        news_context = {
            "imd_forecast_lpa_pct": 90,
            "expected_output_change_pct": -3,
            "source": "Economic Times (Jun 9-13, 2026) citing IMD/agriculture ministry",
            "note": "IMD forecasts 90% of LPA rainfall; ~3% decline in kharif output expected due to El Nino"
        }

    return {
        "metric": "Kharif Sowing Progress",
        "value": None,
        "sowing_status": sowing_status,
        "season_note": season_note,
        "news_context": news_context,
        "crops": KHARIF_CROPS,
        "sowing_window": SOWING_WINDOW,
        "source": SOURCE_NAME,
        "source_url": SEARCH_URLS[0],
        "fetched_at": now.isoformat(),
        "status": "stale",
        "note": "Official kharif sowing data source (agricoop.gov.in) has persistent SSL issues. Weekly reports typically start late June."
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
                "crops": KHARIF_CROPS,
                "sowing_window": SOWING_WINDOW,
                "sowing_status": "in_season",
                "source": SOURCE_NAME,
                "source_url": url,
                "fetched_at": datetime.now(timezone.utc).isoformat(),
                "status": "ok"
            }
    except Exception:
        pass

    return None
