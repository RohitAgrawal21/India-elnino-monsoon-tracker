import requests
from datetime import datetime, timezone

SOURCE_NAME = "NOAA/PSL DMI (IOD)"
SOURCE_URL = "https://psl.noaa.gov/gcos_wgsp/Timeseries/Data/dmi.had.long.data"

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
                if val > -9000:
                    latest_year = year
                    latest_month = month_idx
                    latest_value = round(val, 3)
                    break
            if latest_value is not None:
                break

        if latest_value is None:
            raise ValueError("No valid DMI data found")

        if latest_value > 0.4:
            phase = "Positive"
            india_note = "Positive IOD tends to OFFSET El Niño drought risk for India (more rain)"
        elif latest_value < -0.4:
            phase = "Negative"
            india_note = "Negative IOD tends to AMPLIFY El Niño drought risk for India (less rain)"
        else:
            phase = "Neutral"
            india_note = "Neutral IOD — El Niño impact on India monsoon depends on other factors"

        return {
            "metric": "IOD / DMI",
            "value": latest_value,
            "unit": "°C",
            "phase": phase,
            "india_impact_note": india_note,
            "period": f"{MONTH_NAMES[latest_month]} {latest_year}",
            "source": SOURCE_NAME,
            "source_url": SOURCE_URL,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "status": "ok",
            "note": "DMI data lags 1-2 months; this is normal for this dataset"
        }
    except Exception as e:
        return {
            "metric": "IOD / DMI",
            "value": None,
            "source": SOURCE_NAME,
            "source_url": SOURCE_URL,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "status": "error",
            "error": str(e)
        }
