import requests
import pdfplumber
import re
import io
from datetime import datetime, timezone

SOURCE_NAME = "IMD Subdivision Rainfall"
SOURCE_URL = "https://mausam.imd.gov.in/Rainfall/SUBDIVISION_RAINFALL_DISTRIBUTION_COUNTRY_INDIA_cd.pdf"

SUBDIV_MATCH = [
    ("ANDAMAN", "andaman_nicobar"),
    ("ARUNACHAL", "arunachal_pradesh"),
    ("ASSAM", "assam_meghalaya"),
    ("NMMT", "nmmt"),
    ("SHWB", "shwb_sikkim"),
    ("GANGETIC", "gangetic_wb"),
    ("JHARKHAND", "jharkhand"),
    ("BIHAR", "bihar"),
    ("EAST UTTAR", "east_up"),
    ("WEST UTTAR", "west_up"),
    ("UTTARAKHAND", "uttarakhand"),
    ("DELHI", "haryana_delhi"),
    ("PUNJAB", "punjab"),
    ("HIMACHAL", "himachal_pradesh"),
    ("JAMMU", "jammu_kashmir"),
    ("WEST RAJASTHAN", "west_rajasthan"),
    ("EAST RAJASTHAN", "east_rajasthan"),
    ("ODISHA", "odisha"),
    ("WEST MADHYA", "west_mp"),
    ("EAST MADHYA", "east_mp"),
    ("GUJARAT REGION", "gujarat"),
    ("SAURASHTRA", "saurashtra_kutch"),
    ("KONKAN", "konkan_goa"),
    ("MADHYA MAHARASHTRA", "madhya_maharashtra"),
    ("MARATHWADA", "marathwada"),
    ("VIDARBHA", "vidarbha"),
    ("CHHATTISGARH", "chhattisgarh"),
    ("COASTAL ANDHRA", "coastal_ap"),
    ("TELANGANA", "telangana"),
    ("RAYALSEEMA", "rayalaseema"),
    ("TAMILNADU", "tamilnadu"),
    ("COASTAL KARNATAKA", "coastal_karnataka"),
    ("NORTHERN INTERIOR", "north_interior_karnataka"),
    ("SOUTHERN INTERIOR", "south_interior_karnataka"),
    ("KERALA", "kerala"),
    ("LAKSHADWEEP", "lakshadweep"),
]

CAT_MAP = {"LE": "Large Excess", "E": "Excess", "N": "Normal",
           "D": "Deficient", "LD": "Large Deficient", "NR": "No Rain"}

def _identify_subdivision(line_upper):
    for pattern, key in SUBDIV_MATCH:
        if pattern in line_upper:
            return key
    return None

def fetch():
    try:
        r = requests.get(SOURCE_URL, timeout=60)
        r.raise_for_status()

        pdf = pdfplumber.open(io.BytesIO(r.content))
        all_text = ""
        for page in pdf.pages:
            all_text += (page.extract_text() or "") + "\n"
        pdf.close()

        lines = all_text.split("\n")

        period_match = re.search(
            r'PERIOD:\s*([\d\-]+\s*to\s*[\d\-]+)',
            all_text, re.IGNORECASE
        )
        report_period = period_match.group(1).strip() if period_match else "see PDF"

        country_actual = None
        country_normal = None
        country_departure = None
        country_category = None

        for line in lines:
            if "country as a whole" in line.lower():
                nums = re.findall(r'-?\d+\.?\d*', line)
                if len(nums) >= 6:
                    country_actual = float(nums[3])
                    country_normal = float(nums[4])
                    country_departure = int(float(nums[5]))
                cat_matches = re.findall(r'\b(LE|E|N|D|LD|NR)\b', line)
                if cat_matches:
                    cat_code = cat_matches[-1]
                    country_category = CAT_MAP.get(cat_code, cat_code)
                break

        category_counts = {}
        for line in lines:
            line_upper = line.upper().strip()
            for cat_name, key in [("LARGE EXCESS", "Large Excess"),
                                   ("EXCESS", "Excess"),
                                   ("NORMAL", "Normal"),
                                   ("DEFICIENT", "Deficient"),
                                   ("LARGE DEFICIENT", "Large Deficient"),
                                   ("NO RAIN", "No Rain")]:
                if cat_name == "EXCESS" and ("LARGE EXCESS" in line_upper):
                    continue
                if cat_name == "DEFICIENT" and ("LARGE DEFICIENT" in line_upper):
                    continue
                if cat_name in line_upper and "CATEGORY" not in line_upper:
                    nums = re.findall(r'\d+', line)
                    if len(nums) >= 4:
                        category_counts[key] = {
                            "subdivisions": int(nums[-2]),
                            "pct_area": int(nums[-1]),
                        }
                    break

        subdivision_data = {}
        for line in lines:
            line_upper = line.upper().strip()
            if "REGION" in line_upper and ":" in line:
                continue
            if "COUNTRY" in line_upper:
                continue
            if "CATEGORY" in line_upper or "S.No" in line_upper:
                continue

            subdiv_key = _identify_subdivision(line_upper)
            if subdiv_key is None:
                continue

            nums = re.findall(r'-?\d+\.?\d*', line)
            cat_matches = re.findall(r'\b(LE|E|N|D|LD|NR)\b', line)

            if len(nums) >= 7 and len(cat_matches) >= 1:
                period_dep = int(float(nums[6]))
                period_cat = cat_matches[-1]
                subdivision_data[subdiv_key] = {
                    "departure_pct": period_dep,
                    "category": CAT_MAP.get(period_cat, period_cat),
                    "category_code": period_cat,
                }

        return {
            "metric": "IMD Subdivision Rainfall",
            "country_actual_mm": country_actual,
            "country_normal_mm": country_normal,
            "country_departure_pct": country_departure,
            "country_category": country_category,
            "category_counts": category_counts if category_counts else None,
            "subdivision_data": subdivision_data if subdivision_data else None,
            "report_period": report_period,
            "unit": "mm / %departure",
            "source": SOURCE_NAME,
            "source_url": SOURCE_URL,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "status": "ok"
        }
    except Exception as e:
        return {
            "metric": "IMD Subdivision Rainfall",
            "country_departure_pct": None,
            "category_counts": None,
            "subdivision_data": None,
            "source": SOURCE_NAME,
            "source_url": SOURCE_URL,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "status": "error",
            "error": str(e),
            "note": "This source is only updated during monsoon season (Jun-Sep). Off-season STALE is expected."
        }
