import json
import os
import shutil
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scraper import noaa_oni, noaa_nino34, noaa_enso_discussion, noaa_soi
from scraper import noaa_dmi, imd_rainfall, imd_lrf, cwc_reservoir, kharif_sowing

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT_DIR, "data")
DOCS_DIR = os.path.join(ROOT_DIR, "docs")

SCRAPERS = [
    ("oni", noaa_oni),
    ("nino34", noaa_nino34),
    ("enso_status", noaa_enso_discussion),
    ("soi", noaa_soi),
    ("iod_dmi", noaa_dmi),
    ("imd_rainfall", imd_rainfall),
    ("imd_lrf", imd_lrf),
    ("cwc_reservoir", cwc_reservoir),
    ("kharif_sowing", kharif_sowing),
]

def run():
    os.makedirs(DATA_DIR, exist_ok=True)
    results = {}
    run_time = datetime.now(timezone.utc).isoformat()

    for key, module in SCRAPERS:
        print(f"  Fetching {key}...", end=" ", flush=True)
        try:
            results[key] = module.fetch()
            status = results[key].get("status", "unknown")
            print(f"[{status.upper()}]")
        except Exception as e:
            print(f"[CRASH]")
            results[key] = {
                "metric": key,
                "value": None,
                "status": "error",
                "error": f"Scraper crashed: {str(e)}",
                "fetched_at": run_time
            }

    latest = {
        "last_updated": run_time,
        "metrics": results
    }

    latest_path = os.path.join(DATA_DIR, "latest.json")
    with open(latest_path, "w", encoding="utf-8") as f:
        json.dump(latest, f, indent=2, ensure_ascii=False)
    print(f"\n  Saved latest.json")

    history_path = os.path.join(DATA_DIR, "history.json")
    if os.path.exists(history_path):
        with open(history_path, "r", encoding="utf-8") as f:
            try:
                history = json.load(f)
            except json.JSONDecodeError:
                history = []
    else:
        history = []

    snapshot = {
        "date": run_time,
        "oni": results.get("oni", {}).get("value"),
        "nino34": results.get("nino34", {}).get("value"),
        "soi": results.get("soi", {}).get("value"),
        "dmi": results.get("iod_dmi", {}).get("value"),
        "rainfall_departure_pct": results.get("imd_rainfall", {}).get("country_departure_pct"),
        "alert_status": results.get("enso_status", {}).get("alert_status"),
    }
    history.append(snapshot)

    with open(history_path, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)
    print(f"  Appended to history.json ({len(history)} entries)")

    shutil.copy2(latest_path, os.path.join(DOCS_DIR, "latest.json"))
    shutil.copy2(history_path, os.path.join(DOCS_DIR, "history.json"))
    print(f"  Copied data files to docs/")

    ok_count = sum(1 for v in results.values() if v.get("status") == "ok")
    total = len(results)
    print(f"\n  Done: {ok_count}/{total} sources OK")
    return results

if __name__ == "__main__":
    print("=== India El Niño Monsoon Tracker — Data Update ===\n")
    run()
