import requests
from datetime import datetime, timezone

SOURCE_NAME = "NOAA/PSL SOI"
SOURCE_URL = "https://psl.noaa.gov/data/correlation/soi.data"

MONTH_NAMES = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun",
               "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

def fetch():
    try:
        r = requests.get(SOURCE_URL, timeout=30)
        r.raise_for_status()
        lines = r.text.strip().split("\n")

        latest_year = None
        latest_month = None
        latest_value = None

        for line in reversed(lines):
            parts = line.split()
            if len(parts) < 2:
                continue
            try:
                year = int(parts[0])
            except ValueError:
                continue
            if year < 1900 or year > 2100:
                continue
            for month_idx in range(min(12, len(parts) - 1), 0, -1):
                try:
                    val = float(parts[month_idx])
                except ValueError:
                    continue
                if val > -90:
                    latest_year = year
                    latest_month = month_idx
                    latest_value = val
                    break
            if latest_value is not None:
                break

        if latest_value is None:
            raise ValueError("No valid SOI data found")

        return {
            "metric": "SOI",
            "value": latest_value,
            "unit": "index",
            "period": f"{MONTH_NAMES[latest_month]} {latest_year}",
            "interpretation": "negative = El Niño tendency" if latest_value < -7 else
                            "positive = La Niña tendency" if latest_value > 7 else
                            "near neutral",
            "source": SOURCE_NAME,
            "source_url": SOURCE_URL,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "status": "ok"
        }
    except Exception as e:
        return {
            "metric": "SOI",
            "value": None,
            "source": SOURCE_NAME,
            "source_url": SOURCE_URL,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "status": "error",
            "error": str(e)
        }
