import requests
import re
from datetime import datetime, timezone
from bs4 import BeautifulSoup

SOURCE_NAME = "NOAA/CPC ENSO Discussion"
SOURCE_URL = "https://www.cpc.ncep.noaa.gov/products/analysis_monitoring/enso_advisory/ensodisc.shtml"

def fetch():
    try:
        r = requests.get(SOURCE_URL, timeout=30)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        text = soup.get_text(" ", strip=True)

        alert_status = "Unknown"
        for keyword in ["La Niña Advisory", "El Niño Warning", "El Niño Advisory",
                        "El Niño Watch", "La Niña Watch", "La Niña Warning",
                        "ENSO-neutral", "Not Active"]:
            if keyword.lower() in text.lower():
                alert_status = keyword
                break

        forecast_match = re.search(
            r'(\d{1,3})\s*%\s*(?:chance|probability).*?(?:very\s+)?strong\s+El\s*Ni[ñn]o',
            text, re.IGNORECASE
        )
        strong_probability = int(forecast_match.group(1)) if forecast_match else None

        elnino_prob_match = re.search(
            r'El\s*Ni[ñn]o.*?(\d{1,3})\s*%', text, re.IGNORECASE
        )
        elnino_probability = int(elnino_prob_match.group(1)) if elnino_prob_match else None

        nino34_match = re.search(
            r'Ni[ñn]o[\s-]*3\.4.*?([+-]?\d+\.?\d*)\s*°?\s*C', text, re.IGNORECASE
        )
        nino34_weekly = float(nino34_match.group(1)) if nino34_match else None

        return {
            "metric": "ENSO Alert Status",
            "alert_status": alert_status,
            "nino34_weekly": nino34_weekly,
            "elnino_probability": elnino_probability,
            "strong_elnino_probability": strong_probability,
            "unit": "%",
            "source": SOURCE_NAME,
            "source_url": SOURCE_URL,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "status": "ok"
        }
    except Exception as e:
        return {
            "metric": "ENSO Alert Status",
            "alert_status": None,
            "source": SOURCE_NAME,
            "source_url": SOURCE_URL,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "status": "error",
            "error": str(e)
        }
