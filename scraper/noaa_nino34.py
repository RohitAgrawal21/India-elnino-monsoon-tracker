import requests
from datetime import datetime, timezone

SOURCE_NAME = "NOAA/CPC Niño-3.4 Monthly"
SOURCE_URL = "https://www.cpc.ncep.noaa.gov/data/indices/sstoi.indices"

def fetch():
    try:
        r = requests.get(SOURCE_URL, timeout=30)
        r.raise_for_status()
        lines = [l.strip() for l in r.text.strip().split("\n") if l.strip()]
        last_line = lines[-1].split()
        year = int(last_line[0])
        month = int(last_line[1])
        nino34_anom = float(last_line[9])

        nino12_anom = float(last_line[3])
        nino3_anom = float(last_line[5])
        nino4_anom = float(last_line[7])

        prev_line = lines[-2].split()
        prev_nino34 = float(prev_line[9])
        if nino34_anom > prev_nino34:
            trend = "rising"
        elif nino34_anom < prev_nino34:
            trend = "falling"
        else:
            trend = "steady"

        month_names = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun",
                       "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

        return {
            "metric": "Niño-3.4 SST Anomaly",
            "value": nino34_anom,
            "unit": "°C",
            "period": f"{month_names[month]} {year}",
            "trend": trend,
            "previous_value": prev_nino34,
            "nino12_anom": nino12_anom,
            "nino3_anom": nino3_anom,
            "nino4_anom": nino4_anom,
            "source": SOURCE_NAME,
            "source_url": SOURCE_URL,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "status": "ok"
        }
    except Exception as e:
        return {
            "metric": "Niño-3.4 SST Anomaly",
            "value": None,
            "source": SOURCE_NAME,
            "source_url": SOURCE_URL,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "status": "error",
            "error": str(e)
        }
