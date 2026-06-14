"""
Conditional-distribution engine for monsoon-analog analysis.

Given a downstream time series (macro indicator, sector index, stock),
returns for EACH rainfall bucket the distribution of outcomes:
mean, median, min, max, std, n, and individual data points.

Then probability-weights across buckets using 2026 outlook weights.
"""
import json
import os
import statistics

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TAXONOMY_PATH = os.path.join(ROOT_DIR, "data", "rainfall_taxonomy.json")


def load_taxonomy():
    with open(TAXONOMY_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def get_year_buckets(taxonomy=None):
    """Returns dict: {year: bucket} and {year: elnino_bucket} for El Nino years."""
    if taxonomy is None:
        taxonomy = load_taxonomy()
    buckets = {}
    elnino_buckets = {}
    for row in taxonomy["years"]:
        buckets[row["year"]] = row["bucket"]
        if row["elnino"] and "elnino_bucket" in row:
            elnino_buckets[row["year"]] = row["elnino_bucket"]
    return buckets, elnino_buckets


def compute_distribution(values):
    """Compute stats for a list of numeric values."""
    if not values:
        return None
    n = len(values)
    result = {
        "n": n,
        "mean": round(statistics.mean(values), 2),
        "median": round(statistics.median(values), 2),
        "min": round(min(values), 2),
        "max": round(max(values), 2),
        "values": [round(v, 2) for v in values],
    }
    if n >= 2:
        result["std"] = round(statistics.stdev(values), 2)
    return result


def conditional_distributions(series_data, taxonomy=None, use_elnino_buckets=False):
    """
    Compute distributions of `series_data` by rainfall bucket.

    Args:
        series_data: dict {year: value} — the downstream variable
        taxonomy: loaded taxonomy JSON (or None to load from file)
        use_elnino_buckets: if True, use ELNINO_LOW/ELNINO_NORMAL/ELNINO_HIGH
                           instead of plain LOW/NORMAL/HIGH

    Returns:
        dict with keys for each bucket, each containing distribution stats
        and the list of (year, value) pairs in that bucket.
    """
    if taxonomy is None:
        taxonomy = load_taxonomy()

    buckets, elnino_buckets = get_year_buckets(taxonomy)
    bucket_source = elnino_buckets if use_elnino_buckets else buckets

    grouped = {}
    for year, value in series_data.items():
        year = int(year)
        if year in bucket_source:
            bucket = bucket_source[year]
            if bucket not in grouped:
                grouped[bucket] = []
            grouped[bucket].append({"year": year, "value": value})

    result = {}
    for bucket, items in grouped.items():
        values = [item["value"] for item in items]
        dist = compute_distribution(values)
        if dist:
            dist["years"] = items
        result[bucket] = dist

    return result


def probability_weighted_outlook(distributions, weights):
    """
    Given distributions per bucket and 2026 probability weights,
    compute the probability-weighted 2026 outlook.

    Args:
        distributions: dict {bucket: {mean, median, min, max, values, ...}}
        weights: dict {bucket: probability} e.g. {"LOW": 0.55, "NORMAL": 0.40, "HIGH": 0.05}

    Returns:
        dict with weighted mean, weighted range, and P(worse than threshold) estimates.
    """
    weighted_mean = 0.0
    all_values = []
    total_weight_used = 0.0

    for bucket, weight in weights.items():
        if bucket in distributions and distributions[bucket]:
            dist = distributions[bucket]
            weighted_mean += dist["mean"] * weight
            for v in dist["values"]:
                all_values.append((v, weight / dist["n"]))
            total_weight_used += weight

    if total_weight_used == 0:
        return None

    # Normalize if some buckets missing
    if total_weight_used < 0.99:
        weighted_mean /= total_weight_used
        all_values = [(v, w / total_weight_used) for v, w in all_values]

    # Probability of exceeding thresholds
    def p_worse_than(threshold):
        """P(value < threshold) for negative-is-bad metrics."""
        return round(sum(w for v, w in all_values if v < threshold) * 100, 1)

    def p_better_than(threshold):
        """P(value > threshold) for positive-is-good metrics."""
        return round(sum(w for v, w in all_values if v > threshold) * 100, 1)

    all_raw = [v for v, _ in all_values]

    return {
        "weighted_mean": round(weighted_mean, 2),
        "weighted_range": [round(min(all_raw), 2), round(max(all_raw), 2)] if all_raw else None,
        "p_negative": p_worse_than(0),
        "p_worse_than_minus5": p_worse_than(-5),
        "p_worse_than_minus10": p_worse_than(-10),
        "p_better_than_5": p_better_than(5),
        "p_better_than_10": p_better_than(10),
        "total_analog_n": sum(d["n"] for d in distributions.values() if d),
        "caveats": [
            f"Based on {sum(d['n'] for d in distributions.values() if d)} analog years — small sample, interpret with caution",
            "Past distributions are not guarantees of future outcomes",
            "El Nino years with clean data: n=8 for LOW bucket, n=11 for NORMAL"
        ]
    }


def run_full_analysis(series_data, series_name, weights=None, taxonomy=None):
    """
    Run complete analysis for one variable.

    Returns:
        Complete analysis dict with per-bucket distributions and 2026 outlook.
    """
    if taxonomy is None:
        taxonomy = load_taxonomy()
    if weights is None:
        weights = taxonomy["2026_probability_model"]["weights"]

    # Standard buckets (all years)
    dist_all = conditional_distributions(series_data, taxonomy, use_elnino_buckets=False)

    # El Nino-only buckets
    dist_elnino = conditional_distributions(series_data, taxonomy, use_elnino_buckets=True)

    # 2026 probability-weighted outlook
    outlook = probability_weighted_outlook(dist_all, weights)

    return {
        "variable": series_name,
        "by_rainfall_bucket": dist_all,
        "by_elnino_bucket": dist_elnino,
        "outlook_2026": outlook,
        "weights_used": weights,
    }
