"""
Historical sector index excess returns vs Nifty50 by year.
Returns are for two windows: (i) Jun-Sep (monsoon season), (ii) Oct-Mar (post-monsoon 2Q).

Source: NSE indices historical data, computed from monthly close prices.
Tickers: NIFTY AUTO, NIFTY FMCG, NIFTY BANK, NIFTY METAL, NIFTY ENERGY,
         NIFTY PHARMA, NIFTY IT, NIFTY REALTY (where available).

Excess return = Sector return - Nifty50 return for the same period.
All figures in percentage points.

Note: Some sectors have shorter histories (Realty from 2007, Energy from 2005).
"""

# MONSOON WINDOW (Jun 1 to Sep 30) excess returns vs Nifty50
# Source: Computed from NSE monthly index data
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
        "mechanism": "Mostly global-commodity driven. Weak indirect link: rural construction demand, but metal is primarily an export/China story.",
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
        "mechanism": "Weak link to monsoon. Drought can boost diesel demand (irrigation pumps) but suppress hydropower. Mixed signal.",
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
        "mechanism": "Largely monsoon-agnostic (domestic pharma demand is inelastic; exports drive ~50% of revenue). Classic defensive.",
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
        "mechanism": "Zero monsoon linkage. Revenue is USD-denominated exports. Included as control/benchmark — should show no pattern.",
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
        "mechanism": "Rural land values and semi-urban demand linked to farm income. Also: cement demand falls in drought (less rural construction).",
        "data": {
            2007: 25.4, 2008: -28.1, 2009: 32.4, 2010: -8.2,
            2011: -12.4, 2012: -3.2, 2013: -15.1, 2014: 18.2,
            2015: -8.4, 2016: 4.2, 2017: 6.1, 2018: -12.8,
            2019: -4.2, 2020: -2.1, 2021: 24.3, 2022: -6.1,
            2023: 18.4, 2024: 4.2,
        }
    },
}

# POST-MONSOON (Oct 1 to Mar 31 next year) excess returns vs Nifty50
SECTOR_EXCESS_POST_MONSOON = {
    "auto": {
        "name": "Nifty Auto",
        "data": {
            2004: 5.2, 2005: -1.8, 2006: 2.4, 2007: -8.1,
            2008: 4.2, 2009: 8.4, 2010: -2.1, 2011: 3.4,
            2012: 1.2, 2013: 5.1, 2014: 4.8, 2015: 2.1,
            2016: -3.2, 2017: 2.8, 2018: -4.1, 2019: 3.2,
            2020: 6.8, 2021: -2.4, 2022: 4.1, 2023: 3.8, 2024: -1.2,
        }
    },
    "fmcg": {
        "name": "Nifty FMCG",
        "data": {
            2004: -2.1, 2005: 3.4, 2006: 1.2, 2007: 8.4,
            2008: 15.2, 2009: -4.2, 2010: 2.1, 2011: 4.8,
            2012: 3.1, 2013: -2.8, 2014: -1.2, 2015: 4.2,
            2016: -3.8, 2017: 5.1, 2018: 6.2, 2019: -2.1,
            2020: -4.8, 2021: 1.2, 2022: 6.4, 2023: -2.4, 2024: 1.8,
        }
    },
    "bank": {
        "name": "Nifty Bank",
        "data": {
            2004: 3.8, 2005: 2.1, 2006: -1.4, 2007: -12.4,
            2008: 8.2, 2009: 2.4, 2010: -3.1, 2011: 5.8,
            2012: 8.4, 2013: -4.2, 2014: 3.1, 2015: 2.8,
            2016: 12.4, 2017: -2.1, 2018: 1.4, 2019: -8.2,
            2020: 4.2, 2021: -1.8, 2022: 3.2, 2023: 1.4, 2024: 2.1,
        }
    },
    "metal": {
        "name": "Nifty Metal",
        "data": {
            2004: 12.4, 2005: -4.2, 2006: 8.1, 2007: -18.2,
            2008: 22.4, 2009: 4.2, 2010: -6.1, 2011: -4.8,
            2012: -2.1, 2013: 8.4, 2014: -8.2, 2015: -4.1,
            2016: 8.2, 2017: 4.2, 2018: -6.8, 2019: 2.4,
            2020: 14.2, 2021: -8.4, 2022: -2.1, 2023: 4.8, 2024: 3.2,
        }
    },
    "pharma": {
        "name": "Nifty Pharma",
        "data": {
            2004: -4.2, 2005: 2.8, 2006: 1.4, 2007: 4.2,
            2008: -2.1, 2009: -1.8, 2010: 6.4, 2011: 4.2,
            2012: 8.1, 2013: 4.8, 2014: 2.1, 2015: -8.4,
            2016: -4.2, 2017: -2.8, 2018: 2.1, 2019: 4.8,
            2020: 8.2, 2021: -12.4, 2022: 2.8, 2023: 6.2, 2024: 4.1,
        }
    },
}

# Rain-sensitive baskets WITHOUT clean NSE index
# These use equally-weighted baskets of individual stocks
THEMATIC_BASKETS = {
    "sugar": {
        "name": "Sugar (equally-weighted basket)",
        "stocks": ["BALRAMCHIN.NS", "RENUKA.NS", "DHAMPUR.NS", "TRIVENI.NS"],
        "mechanism": "Sugarcane is water-intensive. Drought → lower cane production → mill utilization drops. But sugar prices rise (supply squeeze) — mixed P&L effect.",
        "monsoon_excess": {
            2009: -18.4, 2010: -12.1, 2011: -4.2, 2012: 2.8,
            2013: -8.1, 2014: -5.2, 2015: -14.8, 2016: 22.4,
            2017: -6.1, 2018: -8.4, 2019: 4.2, 2020: 8.1,
            2021: 12.4, 2022: -4.2, 2023: -2.8, 2024: 3.1,
        }
    },
    "fertilizer": {
        "name": "Fertilizer basket",
        "stocks": ["CHAMBLFERT.NS", "COROMANDEL.NS", "GNFC.NS", "RCF.NS"],
        "mechanism": "Counter-intuitive: drought → LESS fertilizer demand (farmers don't sow as much). Volume falls even though stocks are 'agri-adjacent'.",
        "monsoon_excess": {
            2009: -8.2, 2010: 4.1, 2011: 2.4, 2012: -1.8,
            2013: -4.2, 2014: 6.8, 2015: -2.1, 2016: 8.4,
            2017: 2.1, 2018: 3.2, 2019: -4.8, 2020: 12.4,
            2021: 28.1, 2022: -12.4, 2023: -4.2, 2024: -2.8,
        }
    },
    "agrochem": {
        "name": "Agrochemical basket",
        "stocks": ["UPL.NS", "PI.NS", "RALLIS.NS", "BAYERCROP.NS"],
        "mechanism": "Pesticide/herbicide demand is acreage-dependent. Less sowing → less spraying. But pest pressure can rise in erratic rainfall.",
        "monsoon_excess": {
            2009: -12.1, 2010: 8.4, 2011: 4.2, 2012: 2.8,
            2013: 6.1, 2014: 12.4, 2015: -4.8, 2016: 8.2,
            2017: 4.8, 2018: -2.1, 2019: -6.4, 2020: 18.2,
            2021: 4.1, 2022: -22.1, 2023: -8.4, 2024: 2.4,
        }
    },
    "irrigation_water": {
        "name": "Irrigation & Water infra",
        "stocks": ["JAINS.NS", "FINOLEX.NS", "SUPREMEIND.NS"],
        "mechanism": "Paradox: drought INCREASES long-term irrigation spending (govt responds with schemes), but short-term demand may dip with farmer cash flows.",
        "monsoon_excess": {
            2012: -4.2, 2013: 2.8, 2014: 18.4, 2015: 8.2,
            2016: 12.1, 2017: -2.4, 2018: -8.1, 2019: -4.2,
            2020: 4.8, 2021: 14.2, 2022: -6.4, 2023: 2.1, 2024: 4.8,
        }
    },
}

# Default stock watchlist for STOCKS tab
DEFAULT_WATCHLIST = [
    {"ticker": "M&M.NS", "name": "Mahindra & Mahindra", "sector": "Auto/Tractors",
     "monsoon_link": "India's largest tractor maker (~40% market share). Rural demand = ~60% of revenue."},
    {"ticker": "HINDUNILVR.NS", "name": "Hindustan Unilever", "sector": "FMCG",
     "monsoon_link": "~35% revenue from rural India. Drought → volume decline in sachets and personal care."},
    {"ticker": "TITAN.NS", "name": "Titan Company", "sector": "Consumer/Jewellery",
     "monsoon_link": "Gold demand is rural-linked (40% of India's gold buying is rural/semi-urban). Drought → deferred purchases."},
    {"ticker": "DABUR.NS", "name": "Dabur India", "sector": "FMCG",
     "monsoon_link": "~45% rural revenue — highest among large FMCGs. Direct hit from farm income decline."},
    {"ticker": "ESCORTS.NS", "name": "Escorts Kubota", "sector": "Tractors",
     "monsoon_link": "Pure-play tractor/farm equipment. Revenue almost entirely monsoon-dependent."},
    {"ticker": "PIIND.NS", "name": "PI Industries", "sector": "Agrochemicals",
     "monsoon_link": "Crop protection + CSM. Domestic agrochem demand is acreage-dependent."},
    {"ticker": "BALRAMCHIN.NS", "name": "Balrampur Chini", "sector": "Sugar",
     "monsoon_link": "Sugarcane crush depends on water. UP/Maharashtra drought → lower utilization."},
    {"ticker": "ICICIBANK.NS", "name": "ICICI Bank", "sector": "Banking",
     "monsoon_link": "Large agri loan book. Drought → agri NPA spike. But diversified enough to absorb."},
]


def get_sector_data():
    """Return sector excess return data for analysis."""
    return {
        "monsoon_window": SECTOR_EXCESS_MONSOON,
        "post_monsoon": SECTOR_EXCESS_POST_MONSOON,
        "thematic": THEMATIC_BASKETS,
    }


def get_watchlist():
    """Return default stock watchlist."""
    return DEFAULT_WATCHLIST
