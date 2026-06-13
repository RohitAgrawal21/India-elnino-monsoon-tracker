# India El Nino Monsoon Tracker

A daily-updating public dashboard that tracks how the 2026 El Nino is likely to affect the Indian monsoon season.

**Live Dashboard:** [https://RohitAgrawal21.github.io/india-elnino-monsoon-tracker/](https://RohitAgrawal21.github.io/india-elnino-monsoon-tracker/)

---

## How to Read This Dashboard

The dashboard has three zones:

### Zone A: ENSO Ocean State (left)
This tracks El Nino itself — the warming of the Pacific Ocean that drives global weather changes.

- **ENSO Alert**: Official NOAA status (Watch → Advisory → Warning means increasing confidence)
- **Nino-3.4 Anomaly**: Temperature departure in the key Pacific region. Above +0.5 C = El Nino conditions. Above +1.5 C = strong El Nino.
- **ONI**: 3-month running average of Nino-3.4. This is the "official" El Nino strength number.
- **SOI**: Atmospheric pressure difference. Negative = El Nino tendency.

### Zone B: IOD Modifier (middle)
The Indian Ocean Dipole (IOD) decides whether El Nino actually hurts India's monsoon or not.

- **Positive IOD**: Tends to bring MORE rain to India, offsetting El Nino drought
- **Negative IOD**: Tends to bring LESS rain, making El Nino's drought impact worse
- **Neutral IOD**: El Nino impact depends on other factors

### Zone C: India Ground Impact (right)
Real measurements from India showing what's actually happening on the ground.

- **All-India Rainfall Departure**: How much more or less rain than normal (negative = deficit)
- **Subdivision Breakdown**: Color bar showing how many regions have excess vs deficient rain
- **IMD Season Forecast**: Official government prediction for the full monsoon season (% of long-period average; 96-104% = normal)
- **Reservoir Storage**: How full India's major reservoirs are compared to normal
- **Kharif Sowing**: How much farmland has been planted (kharif = monsoon-season crops)

### The "Current Read" (top)
Combines all three zones into one plain-English summary. It includes a reminder that the El Nino-monsoon link is only moderate (~-0.5 correlation) — El Nino makes drought more likely, but it's NOT a certainty.

---

## Data Update Schedule

| Metric | Updates | Source |
|--------|---------|--------|
| ENSO Alert and Forecast | Monthly (2nd Thursday) | NOAA/CPC |
| Nino-3.4 Anomaly | Monthly | NOAA/CPC |
| ONI | Monthly (seasonal) | NOAA/CPC |
| SOI | Monthly | NOAA/PSL |
| IOD / DMI | Monthly (lags 1-2 months) | NOAA/PSL |
| Subdivision Rainfall | Daily (monsoon season only) | IMD |
| IMD Season Forecast | 1-2 times before monsoon | IMD |
| Reservoir Storage | Weekly (Thursdays) | CWC |
| Kharif Sowing | Weekly (Fridays, Jun-Oct) | Dept of Agriculture |

**The dashboard scraper runs every day at 4 AM IST.** If a metric shows "STALE / UNREACHABLE", it means the source website was down or unreachable — NOT that the data is wrong. The metric will update automatically once the source is back online.

Some metrics (like ONI or ENSO Alert) only update monthly, so seeing the same number for days is expected behavior, not a bug.

---

## How to Share

Copy and share this link with anyone:

**https://RohitAgrawal21.github.io/india-elnino-monsoon-tracker/**

No login or account needed to view it — it's a public webpage.

---

## Technical Details

- **Scraper**: Python scripts in `/scraper/` that fetch from official government/scientific sources
- **Data**: Stored as JSON in `/data/` (latest values + daily history)
- **Dashboard**: Static HTML/CSS/JS in `/docs/` served via GitHub Pages
- **Automation**: GitHub Actions runs the scraper daily and commits updated data
- **No fabricated data**: If a source can't be reached, the dashboard shows "STALE" — never a guessed number
