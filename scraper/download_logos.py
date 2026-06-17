"""
Download company logos for all watchlist stocks.
Tries multiple sources, saves to docs/logos/{TICKER}.png
Falls back to generating SVG badges for any that fail.
"""
import os
import sys
import hashlib
import requests

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGOS_DIR = os.path.join(ROOT_DIR, "docs", "logos")
os.makedirs(LOGOS_DIR, exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
}

# Ticker -> company website domain
TICKER_DOMAINS = {
    'M&M.NS': 'mahindra.com',
    'HINDUNILVR.NS': 'unilever.com',
    'HEROMOTOCO.NS': 'heromotocorp.com',
    'DABUR.NS': 'dabur.com',
    'ICICIBANK.NS': 'icicibank.com',
    'SBIN.NS': 'sbi.co.in',
    'TITAN.NS': 'titan.co.in',
    'BAJAJ-AUTO.NS': 'bajajauto.com',
    'MARICO.NS': 'marico.com',
    'UPL.NS': 'upl-ltd.com',
    'NESTLEIND.NS': 'nestle.in',
    'BRITANNIA.NS': 'britannia.co.in',
    'TCS.NS': 'tcs.com',
    'INFY.NS': 'infosys.com',
    'SUNPHARMA.NS': 'sunpharma.com',
    'ITC.NS': 'itcportal.com',
    'RELIANCE.NS': 'ril.com',
    'NTPC.NS': 'ntpc.co.in',
    'ESCORTS.NS': 'escortsgroup.com',
    'TVSMOTOR.NS': 'tvsmotor.com',
    'GODREJCP.NS': 'godrejcp.com',
    'EMAMILTD.NS': 'emamiltd.in',
    'BALRAMCHIN.NS': 'chinimill.com',
    'COROMANDEL.NS': 'coromandel.biz',
    'PIIND.NS': 'piindustries.com',
    'MANAPPURAM.NS': 'manappuram.com',
    'CANBK.NS': 'canarabank.com',
    'FEDERALBNK.NS': 'federalbank.co.in',
    'WABAG.NS': 'wabag.com',
    'SHAKTIPUMP.NS': 'shaktipumps.com',
    'KSB.NS': 'ksbpumps.com',
    'CGPOWER.NS': 'cgglobal.com',
    'TATAPOWER.NS': 'tatapower.com',
    'PERSISTENT.NS': 'persistent.com',
    'TORNTPHARM.NS': 'torrentpharma.com',
    'CONCOR.NS': 'concorindia.co.in',
    'DHAMPURSUG.NS': 'dhampursugar.com',
    'TRIVENI.NS': 'trivenigroup.com',
    'RALLIS.NS': 'rallis.co.in',
    'GNFC.NS': 'gnfc.in',
    'VSTTILLERS.NS': 'vsttillers.com',
    'BASF.NS': 'basf.com',
    'RCF.NS': 'rcfltd.com',
    'CHAMBLFERT.NS': 'chambalfertilisers.com',
    'IONEXCHANG.NS': 'ionexchange.co.in',
    'KIRLOSBROS.NS': 'kirloskar.com',
    'KRBL.NS': 'krbl.com',
    'HATSUN.NS': 'hatsun.com',
    'BECTORFOOD.NS': 'mrsbectors.com',
    'PRIVISCL.NS': 'privi.com',
    'GPPL.NS': 'gppl.co.in',
    'SJVN.NS': 'sjvn.nic.in',
    'SUNTV.NS': 'suntv.in',
    'CESC.NS': 'cesc.co.in',
    'WATERBASE.NS': 'waterbaseindia.com',
    'JISLJALEQS.NS': 'jains.com',
}

# Known hash of Google's generic globe favicon (16x16 and other sizes)
GENERIC_GLOBE_HASHES = set()


def is_generic_icon(data):
    """Check if downloaded image is too small or a known generic icon."""
    if len(data) < 500:
        return True
    h = hashlib.md5(data).hexdigest()
    if h in GENERIC_GLOBE_HASHES:
        return True
    return False


def try_download(url, timeout=10):
    """Try to download an image, return bytes or None."""
    try:
        r = requests.get(url, headers=HEADERS, timeout=timeout, allow_redirects=True)
        if r.status_code == 200 and len(r.content) > 500:
            ct = r.headers.get("Content-Type", "")
            if "image" in ct or "svg" in ct or "octet" in ct:
                return r.content
    except Exception:
        pass
    return None


def generate_svg_badge(label, color):
    """Generate a clean SVG badge as bytes."""
    fs = 28 if len(label) > 3 else 32 if len(label) > 2 else 38
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="128" height="128">
<rect width="128" height="128" rx="20" fill="{color}"/>
<text x="64" y="50%" dy="0.36em" text-anchor="middle" fill="#fff"
  font-size="{fs}" font-weight="800" font-family="Inter,system-ui,sans-serif">{label}</text>
</svg>'''
    return svg.encode("utf-8")


# Ticker -> (short label, brand color) for SVG fallback
TICKER_BADGE = {
    'M&M.NS': ('M&amp;M', '#e03131'), 'HINDUNILVR.NS': ('HUL', '#1864ab'),
    'HEROMOTOCO.NS': ('HMC', '#c92a2a'), 'DABUR.NS': ('DAB', '#2b8a3e'),
    'ICICIBANK.NS': ('ICICI', '#f76707'), 'SBIN.NS': ('SBI', '#364fc7'),
    'TITAN.NS': ('TTN', '#862e9c'), 'BAJAJ-AUTO.NS': ('BAJ', '#1864ab'),
    'MARICO.NS': ('MRC', '#087f5b'), 'UPL.NS': ('UPL', '#0b7285'),
    'NESTLEIND.NS': ('NES', '#e8590c'), 'BRITANNIA.NS': ('BRT', '#d9480f'),
    'TCS.NS': ('TCS', '#364fc7'), 'INFY.NS': ('INFY', '#1864ab'),
    'SUNPHARMA.NS': ('SUN', '#e67700'), 'ITC.NS': ('ITC', '#2b8a3e'),
    'RELIANCE.NS': ('RIL', '#1864ab'), 'NTPC.NS': ('NTPC', '#5f3dc4'),
    'ESCORTS.NS': ('ESC', '#c92a2a'), 'TVSMOTOR.NS': ('TVS', '#1864ab'),
    'GODREJCP.NS': ('GCP', '#2b8a3e'), 'EMAMILTD.NS': ('EMA', '#0b7285'),
    'BALRAMCHIN.NS': ('BRC', '#e67700'), 'COROMANDEL.NS': ('COR', '#087f5b'),
    'PIIND.NS': ('PI', '#5c7cfa'), 'MANAPPURAM.NS': ('MFL', '#e67700'),
    'CANBK.NS': ('CNB', '#364fc7'), 'FEDERALBNK.NS': ('FBK', '#1864ab'),
    'WABAG.NS': ('WAB', '#0b7285'), 'SHAKTIPUMP.NS': ('SKP', '#e03131'),
    'KSB.NS': ('KSB', '#2b8a3e'), 'CGPOWER.NS': ('CGP', '#862e9c'),
    'TATAPOWER.NS': ('TPW', '#1864ab'), 'PERSISTENT.NS': ('PSYS', '#5f3dc4'),
    'TORNTPHARM.NS': ('TRP', '#c92a2a'), 'CONCOR.NS': ('CCR', '#364fc7'),
    'DHAMPURSUG.NS': ('DHS', '#e67700'), 'TRIVENI.NS': ('TRV', '#087f5b'),
    'RALLIS.NS': ('RAL', '#2b8a3e'), 'GNFC.NS': ('GNFC', '#0b7285'),
    'VSTTILLERS.NS': ('VST', '#c92a2a'), 'BASF.NS': ('BASF', '#364fc7'),
    'RCF.NS': ('RCF', '#087f5b'), 'CHAMBLFERT.NS': ('CFL', '#e67700'),
    'IONEXCHANG.NS': ('ION', '#0b7285'), 'KIRLOSBROS.NS': ('KBL', '#862e9c'),
    'KRBL.NS': ('KRBL', '#e67700'), 'HATSUN.NS': ('HAT', '#1864ab'),
    'BECTORFOOD.NS': ('BEC', '#d9480f'), 'PRIVISCL.NS': ('PRI', '#5f3dc4'),
    'GPPL.NS': ('GPPL', '#087f5b'), 'SJVN.NS': ('SJVN', '#364fc7'),
    'SUNTV.NS': ('STV', '#e03131'), 'CESC.NS': ('CESC', '#c92a2a'),
    'WATERBASE.NS': ('WTR', '#0b7285'), 'JISLJALEQS.NS': ('JAIN', '#2b8a3e'),
}


def download_logo(ticker, domain):
    """Try multiple sources, return (bytes, ext) or None."""
    safe_ticker = ticker.replace('.NS', '')

    # Source 1: Google faviconV2 (128px)
    url1 = f"https://t2.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&url=https://{domain}&size=128"
    data = try_download(url1)
    if data and not is_generic_icon(data):
        return data, "png"

    # Source 2: Google faviconV2 with www prefix
    url2 = f"https://t2.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&url=https://www.{domain}&size=128"
    data = try_download(url2)
    if data and not is_generic_icon(data):
        return data, "png"

    # Source 3: Direct favicon from the company website
    url3 = f"https://{domain}/favicon.ico"
    data = try_download(url3)
    if data and not is_generic_icon(data):
        return data, "ico"

    # Source 4: Apple touch icon (usually higher quality)
    url4 = f"https://{domain}/apple-touch-icon.png"
    data = try_download(url4)
    if data and not is_generic_icon(data):
        return data, "png"

    url5 = f"https://www.{domain}/apple-touch-icon.png"
    data = try_download(url5)
    if data and not is_generic_icon(data):
        return data, "png"

    return None


def run():
    print("=== Logo Downloader ===\n")

    # First, download Google's generic globe to learn its hash
    print("  Learning generic globe hash...")
    globe_url = "https://t2.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&url=https://thisdomaindoesnotexist12345.com&size=128"
    globe_data = try_download(globe_url)
    if globe_data:
        globe_hash = hashlib.md5(globe_data).hexdigest()
        GENERIC_GLOBE_HASHES.add(globe_hash)
        print(f"  Globe hash: {globe_hash} ({len(globe_data)} bytes)\n")

    ok = 0
    fallback = 0

    for ticker, domain in TICKER_DOMAINS.items():
        safe = ticker.replace('.NS', '').replace('&', '_').replace('-', '_')
        print(f"  {ticker:20s} ({domain:30s}) ... ", end="", flush=True)

        result = download_logo(ticker, domain)
        if result:
            data, ext = result
            out_path = os.path.join(LOGOS_DIR, f"{safe}.png")
            with open(out_path, "wb") as f:
                f.write(data)
            print(f"OK ({len(data)} bytes)")
            ok += 1
        else:
            # Generate SVG fallback
            badge = TICKER_BADGE.get(ticker, (safe[:3], '#555'))
            svg_data = generate_svg_badge(badge[0], badge[1])
            out_path = os.path.join(LOGOS_DIR, f"{safe}.svg")
            with open(out_path, "wb") as f:
                f.write(svg_data)
            print(f"FALLBACK (SVG badge)")
            fallback += 1

    print(f"\n  Done: {ok} real logos, {fallback} SVG badges")
    print(f"  Saved to: {LOGOS_DIR}")


if __name__ == "__main__":
    run()
