import requests
import pdfplumber
import re
import io
from datetime import datetime, timezone

SOURCE_NAME = "IMD Subdivision Rainfall"
SOURCE_URL = "https://mausam.imd.gov.in/Rainfall/SUBDIVISION_RAINFALL_DISTRIBUTION_COUNTRY_INDIA_cd.pdf"

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
                    cat_map = {"LE": "Large Excess", "E": "Excess", "N": "Normal",
                               "D": "Deficient", "LD": "Large Deficient", "NR": "No Rain"}
                    country_category = cat_map.get(cat_code, cat_code)
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

        return {
            "metric": "IMD Subdivision Rainfall",
            "country_actual_mm": country_actual,
            "country_normal_mm": country_normal,
            "country_departure_pct": country_departure,
            "country_category": country_category,
            "category_counts": category_counts if category_counts else None,
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
            "source": SOURCE_NAME,
            "source_url": SOURCE_URL,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "status": "error",
            "error": str(e),
            "note": "This source is only updated during monsoon season (Jun-Sep). Off-season STALE is expected."
        }
