import requests
import re
from datetime import datetime, timezone
from bs4 import BeautifulSoup

SOURCE_NAME = "IRI/Columbia ENSO Forecast"
SOURCE_URL = "https://iri.columbia.edu/our-expertise/climate/forecasts/enso/current/"

def fetch():
    try:
        r = requests.get(SOURCE_URL, timeout=30,
                        headers={"User-Agent": "Mozilla/5.0 (compatible; monsoon-tracker/1.0)"})
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        text = soup.get_text(" ", strip=True)

        elnino_prob = None
        neutral_prob = None
        nina_prob = None

        en_match = re.search(
            r'(\d{1,3})\s*%\s*(?:probability\s*)?(?:to\s*)?El.Ni', text, re.IGNORECASE
        )
        if not en_match:
            en_match = re.search(
                r'El.Ni.o[:\s]*(\d{1,3})\s*%', text, re.IGNORECASE
            )
        if not en_match:
            en_match = re.search(
                r'(\d{2,3})\s*%.*?El.Ni', text, re.IGNORECASE
            )
        if en_match:
            elnino_prob = int(en_match.group(1))

        neut_match = re.search(
            r'[Nn]eutral[:\s]*(\d{1,3})\s*%', text
        )
        if neut_match:
            neutral_prob = int(neut_match.group(1))

        nina_match = re.search(
            r'La.Ni.a[:\s]*(\d{1,3})\s*%', text, re.IGNORECASE
        )
        if nina_match:
            nina_prob = int(nina_match.group(1))

        season_match = re.search(
            r'(?:for|during)\s+((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*\s*[-–]\s*(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*\s*\d{4})',
            text, re.IGNORECASE
        )
        forecast_season = season_match.group(1).strip() if season_match else None

        if not forecast_season:
            abbr_match = re.search(
                r'\b([JFMASOND]{3})\s+\d{4}\b', text
            )
            if abbr_match:
                forecast_season = abbr_match.group(0)

        if elnino_prob is None:
            return {
                "metric": "IRI ENSO Forecast",
                "source": SOURCE_NAME,
                "source_url": SOURCE_URL,
                "fetched_at": datetime.now(timezone.utc).isoformat(),
                "status": "stale",
                "note": "Could not parse probability values from IRI page"
            }

        return {
            "metric": "IRI ENSO Forecast",
            "elnino_probability": elnino_prob,
            "neutral_probability": neutral_prob,
            "nina_probability": nina_prob,
            "forecast_season": forecast_season,
            "source": SOURCE_NAME,
            "source_url": SOURCE_URL,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "status": "ok"
        }
    except Exception as e:
        return {
            "metric": "IRI ENSO Forecast",
            "source": SOURCE_NAME,
            "source_url": SOURCE_URL,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "status": "error",
            "error": str(e)
        }
