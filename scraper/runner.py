import json
import math
import os
import shutil
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scraper import noaa_oni, noaa_nino34, noaa_enso_discussion, noaa_soi
from scraper import noaa_dmi, imd_rainfall, imd_lrf, cwc_reservoir, kharif_sowing
from scraper import iri_forecast, noaa_pdo


def _sigmoid(x, center=0.0, steepness=1.0):
    """Sigmoid mapping: returns 0..1 continuously."""
    return 1.0 / (1.0 + math.exp(-steepness * (x - center)))


def _clamp(v, lo=0.0, hi=100.0):
    return max(lo, min(hi, v))

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

    # Nino-3.4 signal → probability (20%) — sigmoid centered at 0.5°C
    nino34 = results.get("nino34", {}).get("value")
    if nino34 is not None:
        n_prob = _clamp(_sigmoid(nino34, center=0.5, steepness=2.5) * 100)
        components.append(("Nino-3.4", round(n_prob, 1), 0.20))

    # ONI → probability (12%) — sigmoid centered at 0.5°C
    oni = results.get("oni", {}).get("value")
    if oni is not None:
        o_prob = _clamp(_sigmoid(oni, center=0.5, steepness=2.5) * 100)
        components.append(("ONI", round(o_prob, 1), 0.12))

    # SOI → probability (8%) — negative SOI = El Nino; sigmoid centered at 0, inverted
    soi = results.get("soi", {}).get("value")
    if soi is not None:
        s_prob = _clamp(_sigmoid(-soi, center=5.0, steepness=0.3) * 100)
        components.append(("SOI", round(s_prob, 1), 0.08))

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
    Weighted blend of continuous sub-scores from Nino-3.4, SOI, IOD,
    rainfall departure, and PDO. Each factor maps to 0..1 via sigmoid
    or linear ramp, then combines with weights summing to ~1."""
    components = []
    weights = []

    # Nino-3.4: 0°C→low stress, 2°C→high stress (weight 30%)
    nino34 = results.get("nino34", {}).get("value")
    if nino34 is not None:
        components.append(_sigmoid(nino34, center=0.8, steepness=2.0))
        weights.append(0.30)

    # SOI: negative→El Nino stress; -15 is very strong signal (weight 10%)
    soi = results.get("soi", {}).get("value")
    if soi is not None:
        components.append(_sigmoid(-soi, center=5.0, steepness=0.25))
        weights.append(0.10)

    # IOD (DMI): negative→bad for India, positive→good (weight 15%)
    dmi = results.get("iod_dmi", {}).get("value")
    if dmi is not None:
        components.append(_sigmoid(-dmi, center=0.0, steepness=4.0))
        weights.append(0.15)

    # Rainfall departure: 0%→neutral, -50%→extreme stress (weight 35%)
    dep = results.get("imd_rainfall", {}).get("country_departure_pct")
    if dep is not None:
        components.append(_sigmoid(-dep, center=15.0, steepness=0.08))
        weights.append(0.35)

    # PDO: positive amplifies El Nino effect (weight 10%)
    pdo = results.get("pdo", {}).get("value")
    if pdo is not None:
        components.append(_sigmoid(pdo, center=0.0, steepness=2.0))
        weights.append(0.10)

    if not weights:
        return 50

    total_w = sum(weights)
    raw = sum(c * (w / total_w) for c, w in zip(components, weights))
    return round(_clamp(raw * 100))

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
