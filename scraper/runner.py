import json
import os
import shutil
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scraper import noaa_oni, noaa_nino34, noaa_enso_discussion, noaa_soi
from scraper import noaa_dmi, imd_rainfall, imd_lrf, cwc_reservoir, kharif_sowing
from scraper import iri_forecast, noaa_pdo

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
    ("iri_forecast", iri_forecast),
    ("pdo", noaa_pdo),
]

def calc_elnino_probability(results):
    """Blended El Nino probability from multiple sources.
    Weights: IRI 35%, NOAA CPC 25%, Nino-3.4 signal 20%, ONI 12%, SOI 8%."""
    components = []

    # IRI/Columbia (35%)
    iri_prob = results.get("iri_forecast", {}).get("elnino_probability")
    if iri_prob is not None:
        components.append(("IRI/Columbia", float(iri_prob), 0.35))

    # NOAA CPC from enso_discussion (25%)
    noaa_prob = results.get("enso_status", {}).get("elnino_probability")
    if noaa_prob is not None:
        components.append(("NOAA CPC", float(noaa_prob), 0.25))

    # Nino-3.4 signal → probability (20%)
    nino34 = results.get("nino34", {}).get("value")
    if nino34 is not None:
        if nino34 >= 2.0: n_prob = 95
        elif nino34 >= 1.5: n_prob = 85
        elif nino34 >= 1.0: n_prob = 70
        elif nino34 >= 0.5: n_prob = 55
        elif nino34 >= 0.0: n_prob = 30
        else: n_prob = 10
        components.append(("Nino-3.4", n_prob, 0.20))

    # ONI → probability (12%)
    oni = results.get("oni", {}).get("value")
    if oni is not None:
        if oni >= 2.0: o_prob = 95
        elif oni >= 1.5: o_prob = 85
        elif oni >= 1.0: o_prob = 70
        elif oni >= 0.5: o_prob = 55
        elif oni >= 0.0: o_prob = 30
        else: o_prob = 10
        components.append(("ONI", o_prob, 0.12))

    # SOI → probability (8%) - negative SOI = El Nino
    soi = results.get("soi", {}).get("value")
    if soi is not None:
        if soi <= -15: s_prob = 85
        elif soi <= -7: s_prob = 65
        elif soi <= 0: s_prob = 45
        elif soi <= 7: s_prob = 25
        else: s_prob = 10
        components.append(("SOI", s_prob, 0.08))

    if not components:
        return None

    # Normalize weights if some sources are missing
    total_weight = sum(w for _, _, w in components)
    blended = sum(prob * (w / total_weight) for _, prob, w in components)

    return {
        "blended_probability": round(blended, 1),
        "components": [{"source": s, "probability": p, "weight": round(w / total_weight * 100, 1)} for s, p, w in components],
        "confidence": "high" if total_weight >= 0.8 else "medium" if total_weight >= 0.5 else "low"
    }


def calc_stress_index(results):
    """Monsoon Stress Index: 0 (no concern) to 100 (extreme concern).
    Blends Nino-3.4, SOI, IOD, and rainfall departure."""
    score = 50
    nino34 = results.get("nino34", {}).get("value")
    if nino34 is not None:
        if nino34 >= 2.0: score += 25
        elif nino34 >= 1.5: score += 20
        elif nino34 >= 1.0: score += 15
        elif nino34 >= 0.5: score += 8
        elif nino34 >= 0: score += 2
        else: score -= 5

    soi = results.get("soi", {}).get("value")
    if soi is not None:
        if soi <= -15: score += 10
        elif soi <= -7: score += 5
        elif soi >= 7: score -= 5

    dmi = results.get("iod_dmi", {}).get("value")
    if dmi is not None:
        if dmi < -0.4: score += 8
        elif dmi > 0.4: score -= 8

    dep = results.get("imd_rainfall", {}).get("country_departure_pct")
    if dep is not None:
        if dep <= -50: score += 18
        elif dep <= -40: score += 14
        elif dep <= -30: score += 10
        elif dep <= -20: score += 6
        elif dep <= -10: score += 3
        elif dep >= 30: score -= 8
        elif dep >= 20: score -= 5
        elif dep >= 10: score -= 2

    pdo = results.get("pdo", {}).get("value")
    if pdo is not None:
        if pdo > 0.5: score += 5
        elif pdo < -0.5: score -= 5

    return max(0, min(100, score))

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

    stress = calc_stress_index(results)
    latest["stress_index"] = stress

    elnino_prob = calc_elnino_probability(results)
    latest["elnino_blended"] = elnino_prob

    with open(latest_path, "w", encoding="utf-8") as f:
        json.dump(latest, f, indent=2, ensure_ascii=False)

    snapshot = {
        "date": run_time,
        "oni": results.get("oni", {}).get("value"),
        "nino34": results.get("nino34", {}).get("value"),
        "soi": results.get("soi", {}).get("value"),
        "dmi": results.get("iod_dmi", {}).get("value"),
        "rainfall_departure_pct": results.get("imd_rainfall", {}).get("country_departure_pct"),
        "alert_status": results.get("enso_status", {}).get("alert_status"),
        "stress_index": stress,
        "iri_elnino_prob": results.get("iri_forecast", {}).get("elnino_probability"),
        "pdo": results.get("pdo", {}).get("value"),
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
