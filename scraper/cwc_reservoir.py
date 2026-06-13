import requests
import pdfplumber
import re
import io
from datetime import datetime, timezone, timedelta
from bs4 import BeautifulSoup

SOURCE_NAME = "CWC Reservoir Storage"
BULLETIN_PAGE = "https://cwc.gov.in/en/reservoir-level-storage-bulletin"

def fetch():
    try:
        pdf_url = _find_latest_bulletin_url()
        if not pdf_url:
            raise ValueError("Could not find latest reservoir bulletin PDF URL")

        r = requests.get(pdf_url, timeout=60)
        r.raise_for_status()

        return _parse_pdf(r.content, pdf_url)
    except Exception as e:
        return {
            "metric": "Reservoir Storage",
            "value": None,
            "source": SOURCE_NAME,
            "source_url": BULLETIN_PAGE,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "status": "stale",
            "error": str(e),
            "note": "CWC reservoir bulletin is updated weekly (Thursdays). PDF parsing is brittle."
        }

def _find_latest_bulletin_url():
    try:
        r = requests.get(BULLETIN_PAGE, timeout=30)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        for link in soup.find_all("a", href=True):
            href = link["href"]
            if "fb-" in href.lower() and href.endswith(".pdf"):
                if href.startswith("http"):
                    return href
                return "https://cwc.gov.in" + href
    except Exception:
        pass

    now = datetime.now()
    for days_back in range(0, 30):
        d = now - timedelta(days=days_back)
        date_str = d.strftime("%d%m%Y")
        url = f"https://cwc.gov.in/sites/default/files/fb-{date_str}.pdf"
        try:
            r = requests.head(url, timeout=10)
            if r.status_code == 200:
                return url
        except Exception:
            continue
    return None

def _parse_pdf(content, url):
    try:
        pdf = pdfplumber.open(io.BytesIO(content))
        all_text = ""
        for page in pdf.pages:
            all_text += (page.extract_text() or "") + "\n"
        pdf.close()

        storage_match = re.search(
            r'(?:total|aggregate).*?(?:live\s+storage|storage).*?(\d+\.?\d*)\s*(?:BCM|bcm)',
            all_text, re.IGNORECASE
        )
        live_storage = float(storage_match.group(1)) if storage_match else None

        pct_match = re.search(
            r'(\d+\.?\d*)\s*%\s*(?:of|the)?\s*(?:total|full|FRL)',
            all_text, re.IGNORECASE
        )
        pct_capacity = float(pct_match.group(1)) if pct_match else None

        ly_match = re.search(
            r'(?:last\s+year|corresponding.*?last.*?year).*?(\d+\.?\d*)\s*(?:BCM|bcm)',
            all_text, re.IGNORECASE
        )
        last_year_storage = float(ly_match.group(1)) if ly_match else None

        avg_match = re.search(
            r'(?:average|normal|10.*?year).*?(\d+\.?\d*)\s*(?:BCM|bcm)',
            all_text, re.IGNORECASE
        )
        avg_storage = float(avg_match.group(1)) if avg_match else None

        date_match = re.search(
            r'(?:as\s+on|dated?)\s+(\d{1,2}[\s./-]+\d{1,2}[\s./-]+\d{4})',
            all_text, re.IGNORECASE
        )
        report_date = date_match.group(1).strip() if date_match else "see PDF"

        return {
            "metric": "Reservoir Storage",
            "live_storage_bcm": live_storage,
            "pct_capacity": pct_capacity,
            "last_year_bcm": last_year_storage,
            "avg_10yr_bcm": avg_storage,
            "report_date": report_date,
            "unit": "BCM",
            "source": SOURCE_NAME,
            "source_url": url,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "status": "ok" if live_storage else "stale"
        }
    except Exception as e:
        return {
            "metric": "Reservoir Storage",
            "value": None,
            "source": SOURCE_NAME,
            "source_url": url,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "status": "error",
            "error": str(e)
        }
