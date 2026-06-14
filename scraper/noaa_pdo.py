import requests
import re
from datetime import datetime, timezone

SOURCE_NAME = "NOAA/PSL PDO"
SOURCE_URL = "https://psl.noaa.gov/data/correlation/pdo.data"

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

def fetch():
    try:
        r = requests.get(SOURCE_URL, timeout=20)
        r.raise_for_status()
        lines = r.text.strip().split("\n")

        latest_year = None
        latest_month_idx = None
        latest_value = None

        for line in lines:
            parts = line.split()
            if len(parts) < 2:
                continue
            try:
                year = int(parts[0])
            except ValueError:
                continue
            if year < 1948 or year > 2100:
                continue
            for i, val_str in enumerate(parts[1:13], 0):
                try:
                    val = float(val_str)
                except ValueError:
                    continue
                if val <= -9.0:
                    continue
                latest_year = year
                latest_month_idx = i
                latest_value = val

        if latest_value is None:
            return {
                "metric": "PDO",
                "value": None,
                "source": SOURCE_NAME,
                "source_url": SOURCE_URL,
                "fetched_at": datetime.now(timezone.utc).isoformat(),
                "status": "stale",
                "note": "Could not find valid PDO data"
            }

        period = f"{MONTHS[latest_month_idx]} {latest_year}"
        phase = "Positive" if latest_value > 0.5 else "Negative" if latest_value < -0.5 else "Neutral"

        if phase == "Negative":
            india_note = "Negative PDO can weaken El Nino's drought effect on India — a mitigating factor"
        elif phase == "Positive":
            india_note = "Positive PDO amplifies El Nino's drought effect on India — an aggravating factor"
        else:
            india_note = "Neutral PDO — minimal modulation of El Nino's impact on India"

        return {
            "metric": "PDO",
            "value": latest_value,
            "unit": "index",
            "period": period,
            "phase": phase,
            "india_impact_note": india_note,
            "source": SOURCE_NAME,
            "source_url": SOURCE_URL,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "status": "ok"
        }
    except Exception as e:
        return {
            "metric": "PDO",
            "value": None,
            "source": SOURCE_NAME,
            "source_url": SOURCE_URL,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "status": "error",
            "error": str(e)
        }
