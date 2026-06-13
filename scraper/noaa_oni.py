import requests
from datetime import datetime, timezone

SOURCE_NAME = "NOAA/CPC ONI"
SOURCE_URL = "https://www.cpc.ncep.noaa.gov/data/indices/oni.ascii.txt"

def fetch():
    try:
        r = requests.get(SOURCE_URL, timeout=30)
        r.raise_for_status()
        lines = [l.strip() for l in r.text.strip().split("\n") if l.strip()]
        header = lines[0].split()
        last_line = lines[-1].split()
        season = last_line[0]
        year = last_line[1]
        total = float(last_line[2])
        anom = float(last_line[3])

        prev_line = lines[-2].split()
        prev_anom = float(prev_line[3])
        if anom > prev_anom:
            trend = "rising"
        elif anom < prev_anom:
            trend = "falling"
        else:
            trend = "steady"

        return {
            "metric": "ONI",
            "value": anom,
            "unit": "°C",
            "season": f"{season} {year}",
            "trend": trend,
            "previous_value": prev_anom,
            "source": SOURCE_NAME,
            "source_url": SOURCE_URL,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "status": "ok"
        }
    except Exception as e:
        return {
            "metric": "ONI",
            "value": None,
            "source": SOURCE_NAME,
            "source_url": SOURCE_URL,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "status": "error",
            "error": str(e)
        }
