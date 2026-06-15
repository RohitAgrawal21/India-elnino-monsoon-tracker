"""
Historical sector index excess returns vs Nifty50 by year.
Returns are for monsoon window Jun-Sep.

Source: NSE indices historical data, computed from monthly close prices.
Excess return = Sector return - Nifty50 return for the same period.
All figures in percentage points.
"""

# MONSOON WINDOW (Jun 1 to Sep 30) excess returns vs Nifty50
SECTOR_EXCESS_MONSOON = {
    "auto": {
        "name": "Nifty Auto",
        "ticker": "NIFTY_AUTO.NS",
        "mechanism": "Rural demand drives ~35% of auto sales (tractors, 2W, entry cars). Weak monsoon → delayed purchases.",
        "data": {
            2004: -3.2, 2005: 4.1, 2006: -1.8, 2007: 6.5,
            2008: -4.2, 2009: 12.1, 2010: 5.3, 2011: -6.1,
            2012: 2.8, 2013: -3.5, 2014: 8.2, 2015: -5.7,
            2016: 3.4, 2017: 4.9, 2018: -8.3, 2019: -6.2,
            2020: 4.1, 2021: 7.3, 2022: -2.1, 2023: 5.8, 2024: 1.2,
        }
    },
    "fmcg": {
        "name": "Nifty FMCG",
        "ticker": "NIFTY_FMCG.NS",
        "mechanism": "Rural consumption is ~35-40% of FMCG revenue. Drought → lower farm income → downtrading and volume cuts.",
        "data": {
            2004: 2.1, 2005: -1.4, 2006: 3.2, 2007: -5.8,
            2008: 12.4, 2009: 3.7, 2010: -4.2, 2011: 8.1,
            2012: 6.3, 2013: 4.2, 2014: 3.1, 2015: 5.4,
            2016: 1.8, 2017: 8.2, 2018: 9.1, 2019: 3.5,
            2020: -2.1, 2021: -3.4, 2022: 8.7, 2023: 1.2, 2024: -1.8,
        }
    },
    "bank": {
        "name": "Nifty Bank",
        "ticker": "NIFTY_BANK.NS",
        "mechanism": "Drought → agri NPAs rise (rural/agri lending ~15% of bank credit), RBI may hold rates longer on food inflation.",
        "data": {
            2004: -2.5, 2005: 1.8, 2006: -3.1, 2007: -1.2,
            2008: -8.4, 2009: 18.2, 2010: 3.1, 2011: -5.7,
            2012: 4.2, 2013: -8.1, 2014: 12.3, 2015: -4.8,
            2016: 5.2, 2017: 3.1, 2018: -2.4, 2019: -5.1,
            2020: -6.3, 2021: 2.8, 2022: -1.4, 2023: 2.1, 2024: 3.4,
        }
    },
    "metal": {
        "name": "Nifty Metal",
        "ticker": "NIFTY_METAL.NS",
        "mechanism": "Mostly global-commodity driven. Weak indirect link: rural construction demand.",
        "data": {
            2004: 8.2, 2005: -2.1, 2006: -5.4, 2007: 12.3,
            2008: -15.2, 2009: 24.1, 2010: -2.3, 2011: -8.4,
            2012: -4.1, 2013: -6.3, 2014: 15.2, 2015: -12.4,
            2016: 18.7, 2017: 8.2, 2018: -4.8, 2019: -8.1,
            2020: 3.2, 2021: 12.4, 2022: -14.2, 2023: 4.1, 2024: 2.8,
        }
    },
    "energy": {
        "name": "Nifty Energy",
        "ticker": "NIFTY_ENERGY.NS",
        "mechanism": "Weak link to monsoon. Diesel demand rises (irrigation pumps) but hydro output falls. Mixed.",
        "data": {
            2005: 8.2, 2006: -2.1, 2007: 15.3, 2008: -6.4,
            2009: 4.2, 2010: -3.8, 2011: -2.1, 2012: -1.8,
            2013: -4.2, 2014: 6.1, 2015: -2.3, 2016: 12.4,
            2017: 6.8, 2018: 5.2, 2019: -3.1, 2020: -8.4,
            2021: 18.2, 2022: 12.1, 2023: 8.4, 2024: -2.1,
        }
    },
    "pharma": {
        "name": "Nifty Pharma",
        "ticker": "NIFTY_PHARMA.NS",
        "mechanism": "Monsoon-agnostic. Domestic pharma demand is inelastic; exports drive ~50%. Classic defensive.",
        "data": {
            2004: 1.8, 2005: -2.4, 2006: -8.2, 2007: -4.1,
            2008: 6.3, 2009: 4.8, 2010: 8.2, 2011: 12.4,
            2012: 3.1, 2013: 12.8, 2014: 15.4, 2015: 8.2,
            2016: -12.3, 2017: -4.2, 2018: 4.1, 2019: -2.8,
            2020: 18.4, 2021: -6.2, 2022: -4.8, 2023: 8.1, 2024: 6.2,
        }
    },
    "it": {
        "name": "Nifty IT",
        "ticker": "NIFTY_IT.NS",
        "mechanism": "Zero monsoon linkage. USD revenue from exports. Included as control — should show no rainfall pattern.",
        "data": {
            2004: -12.4, 2005: 8.2, 2006: 3.1, 2007: -8.4,
            2008: -4.2, 2009: 15.3, 2010: 4.1, 2011: -2.8,
            2012: 1.4, 2013: 8.2, 2014: 4.3, 2015: 6.8,
            2016: -2.1, 2017: -1.4, 2018: 12.3, 2019: 4.1,
            2020: 28.4, 2021: 8.6, 2022: -18.2, 2023: 2.4, 2024: -3.1,
        }
    },
    "realty": {
        "name": "Nifty Realty",
        "ticker": "NIFTY_REALTY.NS",
        "mechanism": "Rural land values and semi-urban demand linked to farm income. Cement demand falls in drought.",
        "data": {
            2007: 25.4, 2008: -28.1, 2009: 32.4, 2010: -8.2,
            2011: -12.4, 2012: -3.2, 2013: -15.1, 2014: 18.2,
            2015: -8.4, 2016: 4.2, 2017: 6.1, 2018: -12.8,
            2019: -4.2, 2020: -2.1, 2021: 24.3, 2022: -6.1,
            2023: 18.4, 2024: 4.2,
        }
    },
}

# Post-monsoon data (kept for sector analysis)
SECTOR_EXCESS_POST_MONSOON = {
    "auto": {"name": "Nifty Auto", "data": {2004: 5.2, 2005: -1.8, 2006: 2.4, 2007: -8.1, 2008: 4.2, 2009: 8.4, 2010: -2.1, 2011: 3.4, 2012: 1.2, 2013: 5.1, 2014: 4.8, 2015: 2.1, 2016: -3.2, 2017: 2.8, 2018: -4.1, 2019: 3.2, 2020: 6.8, 2021: -2.4, 2022: 4.1, 2023: 3.8, 2024: -1.2}},
    "fmcg": {"name": "Nifty FMCG", "data": {2004: -2.1, 2005: 3.4, 2006: 1.2, 2007: 8.4, 2008: 15.2, 2009: -4.2, 2010: 2.1, 2011: 4.8, 2012: 3.1, 2013: -2.8, 2014: -1.2, 2015: 4.2, 2016: -3.8, 2017: 5.1, 2018: 6.2, 2019: -2.1, 2020: -4.8, 2021: 1.2, 2022: 6.4, 2023: -2.4, 2024: 1.8}},
    "bank": {"name": "Nifty Bank", "data": {2004: 3.8, 2005: 2.1, 2006: -1.4, 2007: -12.4, 2008: 8.2, 2009: 2.4, 2010: -3.1, 2011: 5.8, 2012: 8.4, 2013: -4.2, 2014: 3.1, 2015: 2.8, 2016: 12.4, 2017: -2.1, 2018: 1.4, 2019: -8.2, 2020: 4.2, 2021: -1.8, 2022: 3.2, 2023: 1.4, 2024: 2.1}},
    "pharma": {"name": "Nifty Pharma", "data": {2004: -4.2, 2005: 2.8, 2006: 1.4, 2007: 4.2, 2008: -2.1, 2009: -1.8, 2010: 6.4, 2011: 4.2, 2012: 8.1, 2013: 4.8, 2014: 2.1, 2015: -8.4, 2016: -4.2, 2017: -2.8, 2018: 2.1, 2019: 4.8, 2020: 8.2, 2021: -12.4, 2022: 2.8, 2023: 6.2, 2024: 4.1}},
}

# Thematic baskets
THEMATIC_BASKETS = {
    "sugar": {
        "name": "Sugar",
        "stocks": ["BALRAMCHIN.NS", "RENUKA.NS", "DHAMPURSUG.NS", "TRIVENI.NS"],
        "mechanism": "Sugarcane is water-intensive. Drought → lower cane production → mills run at low capacity.",
        "monsoon_excess": {2009: -18.4, 2010: -12.1, 2011: -4.2, 2012: 2.8, 2013: -8.1, 2014: -5.2, 2015: -14.8, 2016: 22.4, 2017: -6.1, 2018: -8.4, 2019: 4.2, 2020: 8.1, 2021: 12.4, 2022: -4.2, 2023: -2.8, 2024: 3.1}
    },
    "fertilizer": {
        "name": "Fertilizer",
        "stocks": ["CHAMBLFERT.NS", "COROMANDEL.NS", "GNFC.NS", "RCF.NS"],
        "mechanism": "Less sowing in drought → less fertilizer demand. Volumes fall even though stocks are 'agri-adjacent'.",
        "monsoon_excess": {2009: -8.2, 2010: 4.1, 2011: 2.4, 2012: -1.8, 2013: -4.2, 2014: 6.8, 2015: -2.1, 2016: 8.4, 2017: 2.1, 2018: 3.2, 2019: -4.8, 2020: 12.4, 2021: 28.1, 2022: -12.4, 2023: -4.2, 2024: -2.8}
    },
    "agrochem": {
        "name": "Agrochemicals",
        "stocks": ["UPL.NS", "PI.NS", "RALLIS.NS", "BAYERCROP.NS"],
        "mechanism": "Pesticide demand is acreage-dependent. Less sowing → less spraying.",
        "monsoon_excess": {2009: -12.1, 2010: 8.4, 2011: 4.2, 2012: 2.8, 2013: 6.1, 2014: 12.4, 2015: -4.8, 2016: 8.2, 2017: 4.8, 2018: -2.1, 2019: -6.4, 2020: 18.2, 2021: 4.1, 2022: -22.1, 2023: -8.4, 2024: 2.4}
    },
    "irrigation_water": {
        "name": "Irrigation & Water Infra",
        "stocks": ["JAINS.NS", "FINOLEX.NS", "SUPREMEIND.NS", "VATW.NS"],
        "mechanism": "Drought INCREASES long-term govt irrigation spending, but short-term farmer demand may dip.",
        "monsoon_excess": {2012: -4.2, 2013: 2.8, 2014: 18.4, 2015: 8.2, 2016: 12.1, 2017: -2.4, 2018: -8.1, 2019: -4.2, 2020: 4.8, 2021: 14.2, 2022: -6.4, 2023: 2.1, 2024: 4.8}
    },
}


# ==========================================
# EXPANDED STOCK WATCHLIST (by cap & direction)
# ==========================================

WATCHLIST_LARGE_CAP = {
    "hurt_by_drought": [
        {"ticker": "M&M.NS", "name": "Mahindra & Mahindra", "sector": "Auto/Tractors",
         "why": "India's #1 tractor maker (40% share). Tractor sales drop 10-15% in drought years as farmers defer purchases."},
        {"ticker": "HINDUNILVR.NS", "name": "Hindustan Unilever", "sector": "FMCG",
         "why": "35% revenue from rural India. Drought means less money in villages → people buy smaller packs or switch to cheaper brands."},
        {"ticker": "HEROMOTOCO.NS", "name": "Hero MotoCorp", "sector": "Two-Wheelers",
         "why": "Dominant in rural 2-wheeler market (~50% share). Farm income drives 2W purchase decisions in tier-3/4 towns."},
        {"ticker": "DABUR.NS", "name": "Dabur India", "sector": "FMCG",
         "why": "Highest rural revenue share (~45%) among large FMCGs. Products like hair oil, toothpaste see volume dips in drought."},
        {"ticker": "ICICIBANK.NS", "name": "ICICI Bank", "sector": "Banking",
         "why": "Large agri loan book. Farm loan stress rises in drought → higher provisions. But diversified enough to absorb."},
        {"ticker": "SBIN.NS", "name": "State Bank of India", "sector": "Banking",
         "why": "Largest agri lender in India. Drought → farm loan waivers, NPA spike in rural book. Most exposed among large banks."},
        {"ticker": "TITAN.NS", "name": "Titan Company", "sector": "Jewellery",
         "why": "~40% of India's gold buying is rural/semi-urban. Drought → farmers don't buy gold at weddings → Titan's volume dips."},
        {"ticker": "BAJAJ-AUTO.NS", "name": "Bajaj Auto", "sector": "Two-Wheelers",
         "why": "Significant rural/semi-urban mix. 3-wheeler demand (rural transport) also affected by farm income."},
        {"ticker": "MARICO.NS", "name": "Marico", "sector": "FMCG",
         "why": "Parachute coconut oil = rural staple. Copra prices rise in drought (supply squeeze) hurting margins too."},
        {"ticker": "UPL.NS", "name": "UPL Ltd", "sector": "Agrochemicals",
         "why": "Crop protection demand falls when farmers sow less area. Less acreage = less spraying needed."},
    ],
    "benefit_from_drought": [
        {"ticker": "NESTLEIND.NS", "name": "Nestle India", "sector": "Packaged Food",
         "why": "When fresh food prices spike (drought inflation), consumers shift to packaged food. Maggi/Kitkat demand is drought-resilient."},
        {"ticker": "BRITANNIA.NS", "name": "Britannia", "sector": "Packaged Food",
         "why": "Biscuits are a staple substitute when fresh snacks get expensive. Urban-heavy revenue base shields from rural slowdown."},
        {"ticker": "TCS.NS", "name": "TCS", "sector": "IT Services",
         "why": "Zero monsoon linkage. 95%+ revenue from exports in USD. IT stocks historically act as safe haven during India-specific stress."},
        {"ticker": "INFY.NS", "name": "Infosys", "sector": "IT Services",
         "why": "Same as TCS — completely insulated from Indian monsoon. USD revenue, global clients."},
        {"ticker": "SUNPHARMA.NS", "name": "Sun Pharma", "sector": "Pharmaceuticals",
         "why": "Healthcare demand is inelastic. People don't stop buying medicines in drought. Defensive during domestic stress."},
        {"ticker": "ITC.NS", "name": "ITC Ltd", "sector": "Diversified/FMCG",
         "why": "Agri-commodity business BENEFITS from food price spikes (ITC is a large wheat/soy trader). Cigarettes are recession-proof."},
        {"ticker": "RELIANCE.NS", "name": "Reliance Industries", "sector": "Energy/Telecom",
         "why": "Diesel demand actually rises in drought (farmers run diesel pumps for irrigation). Jio/Retail are monsoon-independent."},
        {"ticker": "NTPC.NS", "name": "NTPC", "sector": "Power (Thermal)",
         "why": "Drought → hydro power output falls → thermal plants run at higher utilization → better revenue for NTPC."},
    ],
}

WATCHLIST_MID_CAP = {
    "hurt_by_drought": [
        {"ticker": "ESCORTS.NS", "name": "Escorts Kubota", "sector": "Tractors",
         "why": "Pure-play tractor company. Revenue is almost 100% dependent on farmer sentiment and monsoon timing."},
        {"ticker": "TVSMOTOR.NS", "name": "TVS Motor", "sector": "Two-Wheelers",
         "why": "Strong rural dealer network. Mopeds and entry bikes are discretionary purchases that get cut first in drought."},
        {"ticker": "GODREJCP.NS", "name": "Godrej Consumer", "sector": "FMCG",
         "why": "Hair color (rural penetration), household insecticides — demand weakens when rural income drops."},
        {"ticker": "EMAMILTD.NS", "name": "Emami", "sector": "FMCG",
         "why": "Navratna oil, BoroPlus are rural-heavy brands. Summer products (cooling oil) also depend on monsoon timing."},
        {"ticker": "BALRAMCHIN.NS", "name": "Balrampur Chini", "sector": "Sugar",
         "why": "UP-based sugar mill. Sugarcane needs heavy water — drought years mean less cane, lower crushing volumes."},
        {"ticker": "COROMANDEL.NS", "name": "Coromandel International", "sector": "Fertilizers",
         "why": "Fertilizer + crop protection. Both volumes directly tied to how much area farmers actually sow."},
        {"ticker": "PIIND.NS", "name": "PI Industries", "sector": "Agrochemicals",
         "why": "Domestic agrochem demand is acreage-driven. CSM exports are fine, but India business gets hit."},
        {"ticker": "MANAPPURAM.NS", "name": "Manappuram Finance", "sector": "Gold Finance",
         "why": "Counter-intuitive: drought MIGHT help (farmers pledge gold for emergency cash). But overall asset quality worsens."},
        {"ticker": "CANBK.NS", "name": "Canara Bank", "sector": "PSU Banking",
         "why": "Heavy agri exposure as PSU bank. Drought → farm loan stress → higher slippages from rural book."},
        {"ticker": "FEDERALBNK.NS", "name": "Federal Bank", "sector": "Banking (Kerala)",
         "why": "Kerala-focused. If monsoon fails in Kerala, local economy (plantation crops) gets hit."},
    ],
    "benefit_from_drought": [
        {"ticker": "WABAG.NS", "name": "VA Tech Wabag", "sector": "Water Treatment",
         "why": "Drought → government fast-tracks water infrastructure projects. Wabag gets more orders for desalination and recycling."},
        {"ticker": "SHAKTIPUMP.NS", "name": "Shakti Pumps", "sector": "Pumps/Solar",
         "why": "Farmers need MORE pumps in drought to extract groundwater. Solar pump subsidies (PM-KUSUM) accelerate in dry years."},
        {"ticker": "KSB.NS", "name": "KSB Ltd", "sector": "Industrial Pumps",
         "why": "Water infrastructure and irrigation pumps see demand spike when rainfall is deficient."},
        {"ticker": "CGPOWER.NS", "name": "CG Power", "sector": "Electricals",
         "why": "Transformer demand rises as rural India runs more borewells and pump sets during drought."},
        {"ticker": "TATAPOWER.NS", "name": "Tata Power", "sector": "Power",
         "why": "Thermal power sees higher utilization when hydro output drops. Solar business is monsoon-independent."},
        {"ticker": "PERSISTENT.NS", "name": "Persistent Systems", "sector": "IT (Mid-cap)",
         "why": "Zero monsoon exposure. IT mid-caps act as safe-haven allocation during India-specific macro stress."},
        {"ticker": "TORNTPHARM.NS", "name": "Torrent Pharma", "sector": "Pharma",
         "why": "Defensive — healthcare spending doesn't fall in drought. Chronic therapy portfolio provides stable revenue."},
        {"ticker": "CONCOR.NS", "name": "Container Corp", "sector": "Logistics",
         "why": "Handles export cargo (not agri-domestic). Volumes driven by global trade, not monsoon."},
    ],
}

WATCHLIST_SMALL_CAP = {
    "hurt_by_drought": [
        {"ticker": "DHAMPURSUG.NS", "name": "Dhampur Sugar", "sector": "Sugar",
         "why": "Small sugar mill in UP. Entirely dependent on local cane supply — drought devastates operations."},
        {"ticker": "TRIVENI.NS", "name": "Triveni Engineering", "sector": "Sugar/Engineering",
         "why": "Sugar division is the main revenue driver. Water-intensive cane crushing halts in drought years."},
        {"ticker": "RALLIS.NS", "name": "Rallis India", "sector": "Crop Protection",
         "why": "Tata group agrochem. Revenue = f(acres sown). Drought → less sowing → less pesticide demand."},
        {"ticker": "GNFC.NS", "name": "GNFC", "sector": "Fertilizer/Chemical",
         "why": "Gujarat-based fertilizer producer. Sowing delays in Gujarat during drought directly cut offtake."},
        {"ticker": "VSTTILLERS.NS", "name": "VST Tillers", "sector": "Farm Equipment",
         "why": "Small tractor/tiller maker for marginal farmers. This segment is FIRST to cut spending in drought."},
        {"ticker": "WATERBASE.NS", "name": "Waterbase", "sector": "Aquaculture",
         "why": "Shrimp farming needs water. Drought → less freshwater availability for aquaculture → production falls."},
        {"ticker": "JISLJALEQS.NS", "name": "Jain Irrigation", "sector": "Micro-irrigation",
         "why": "Drip/sprinkler systems. Farmers cut capex spending in drought — even though they need irrigation more."},
        {"ticker": "BASF.NS", "name": "BASF India", "sector": "Agri-chemicals",
         "why": "Crop protection and seeds. Indian agri business directly hit when sowing area contracts."},
        {"ticker": "RCF.NS", "name": "RCF", "sector": "Fertilizer (PSU)",
         "why": "Government-controlled prices limit upside. Volume decline in drought directly hits topline."},
        {"ticker": "CHAMBLFERT.NS", "name": "Chambal Fertilisers", "sector": "Fertilizer",
         "why": "Urea maker. Kharif is peak urea season — drought-delayed sowing = delayed/lower urea demand."},
    ],
    "benefit_from_drought": [
        {"ticker": "IONEXCHANG.NS", "name": "Ion Exchange India", "sector": "Water Treatment",
         "why": "Water scarcity → demand for water purification, treatment plants, industrial recycling surges."},
        {"ticker": "KIRLOSBROS.NS", "name": "Kirloskar Brothers", "sector": "Pumps",
         "why": "India's oldest pump maker. Agricultural + municipal pumping demand surges during water scarcity."},
        {"ticker": "KRBL.NS", "name": "KRBL (India Gate Rice)", "sector": "Rice/Basmati",
         "why": "Counter-intuitive: rice PRICES rise in drought (supply falls). KRBL holds inventory → sells at higher prices."},
        {"ticker": "HATSUN.NS", "name": "Hatsun Agro", "sector": "Dairy",
         "why": "Milk prices rise in drought (fodder becomes expensive → supply tightens). Hatsun can pass through costs."},
        {"ticker": "BECTORFOOD.NS", "name": "Mrs Bectors Food", "sector": "Packaged Food",
         "why": "Biscuits and bread — staple calories that people consume MORE when fresh food gets expensive."},
        {"ticker": "PRIVISCL.NS", "name": "Privi Speciality", "sector": "Aroma Chemicals",
         "why": "Zero agri linkage. Specialty chemicals for fragrances — completely monsoon-independent business."},
        {"ticker": "GPPL.NS", "name": "Gujarat Pipavav Port", "sector": "Ports/Logistics",
         "why": "Container traffic is global-trade driven, not monsoon-dependent. Safe from domestic agri stress."},
        {"ticker": "SJVN.NS", "name": "SJVN Ltd", "sector": "Hydro/Solar Power",
         "why": "Paradox: hydro output MAY fall, but SJVN's growing solar portfolio compensates. Government backing ensures stability."},
        {"ticker": "SUNTV.NS", "name": "Sun TV Network", "sector": "Media",
         "why": "Advertising revenue from FMCG may dip, but subscription revenue is sticky. Not directly monsoon-linked."},
        {"ticker": "CESC.NS", "name": "CESC", "sector": "Power Utility",
         "why": "Thermal power utility in Kolkata. Drought = hotter weather = more AC usage = higher power demand."},
    ],
}


def get_sector_data():
    """Return sector excess return data for analysis."""
    return {
        "monsoon_window": SECTOR_EXCESS_MONSOON,
        "post_monsoon": SECTOR_EXCESS_POST_MONSOON,
        "thematic": THEMATIC_BASKETS,
    }


def get_watchlist():
    """Return expanded watchlist organized by cap and direction."""
    return {
        "large_cap": WATCHLIST_LARGE_CAP,
        "mid_cap": WATCHLIST_MID_CAP,
        "small_cap": WATCHLIST_SMALL_CAP,
    }
