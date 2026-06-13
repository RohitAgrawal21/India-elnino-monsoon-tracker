import requests
import pdfplumber
import re
import io
from datetime import datetime, timezone

SOURCE_NAME = "IMD Long Range Forecast"
BASE_URL = "https://mausam.imd.gov.in/Forecast/marquee_data/"

KNOWN_URLS = [
    "https://mausam.imd.gov.in/Forecast/marquee_data/Long%20Range%20Forecast%20for%20Southwest%20Monsoon%20Season%20Rainfall_Press_release_13.4.2026.pdf",
    "https://mausam.imd.gov.in/Forecast/marquee_data/Long%20Range%20Forecast%20for%20Southwest%20Monsoon%20Season%20Rainfall_Press_release_13.4.2026",
]

def fetch():
    for url in KNOWN_URLS:
        try:
            r = requests.get(url, timeout=60)
            if r.status_code == 200 and len(r.content) > 1000:
                return _parse_pdf(r.content, url)
        except Exception:
            continue

    return {
        "metric": "IMD LRF (SW Monsoon)",
        "value": None,
        "source": SOURCE_NAME,
        "source_url": KNOWN_URLS[0],
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "status": "stale",
        "note": "Could not fetch or parse IMD LRF press release. This is updated infrequently (1-2 times before monsoon season)."
    }

def _parse_pdf(content, url):
    try:
        pdf = pdfplumber.open(io.BytesIO(content))
        all_text = ""
        for page in pdf.pages:
            all_text += (page.extract_text() or "") + "\n"
        pdf.close()

        lpa_match = re.search(
            r'(\d{2,3})\s*(?:%|percent)\s*(?:of\s*)?(?:the\s*)?(?:Long\s*Period\s*Average|LPA)',
            all_text, re.IGNORECASE
        )
        if not lpa_match:
            lpa_match = re.search(
                r'(?:Long\s*Period\s*Average|LPA).*?(\d{2,3})\s*(?:%|percent)',
                all_text, re.IGNORECASE
            )

        lpa_pct = int(lpa_match.group(1)) if lpa_match else None

        error_match = re.search(r'[±]\s*(\d+)\s*%', all_text)
        if not error_match:
            error_match = re.search(r'(?:error|margin|range).*?(\d+)\s*%', all_text, re.IGNORECASE)
        error_margin = int(error_match.group(1)) if error_match else None

        date_match = re.search(
            r'(\d{1,2}[\s./-]+(?:April|May|June|March|January|February)\s*,?\s*\d{4})',
            all_text, re.IGNORECASE
        )
        issue_date = date_match.group(1).strip() if date_match else "see PDF"

        if lpa_pct:
            if lpa_pct >= 104:
                category = "Above Normal"
            elif lpa_pct >= 96:
                category = "Normal"
            elif lpa_pct >= 90:
                category = "Below Normal"
            else:
                category = "Deficient"
        else:
            category = None

        return {
            "metric": "IMD LRF (SW Monsoon)",
            "value": lpa_pct,
            "unit": "% of LPA",
            "error_margin": error_margin,
            "category": category,
            "issue_date": issue_date,
            "source": SOURCE_NAME,
            "source_url": url,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "status": "ok" if lpa_pct else "stale"
        }
    except Exception as e:
        return {
            "metric": "IMD LRF (SW Monsoon)",
            "value": None,
            "source": SOURCE_NAME,
            "source_url": url,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "status": "error",
            "error": str(e)
        }
