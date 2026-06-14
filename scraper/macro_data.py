"""
Historical macro data for conditional-distribution analysis.
Sources: MoSPI National Accounts, RBI Handbook of Statistics, MOSPI CPI series.

All data points are from published government/RBI sources.
This is hardcoded because these are historical annual figures from official reports
that don't change — they are the ground truth for backtesting.
"""

# Agriculture GVA growth (% YoY, real, at 2011-12 prices)
# Source: MoSPI National Accounts Statistics / RBI DBIE
# Note: Pre-2012 figures are at 2004-05 prices, converted approximately
AGRI_GVA_GROWTH = {
    1997: 2.4, 1998: 6.3, 1999: 2.7, 2000: -0.1,
    2001: 6.5, 2002: -6.6, 2003: 9.0, 2004: 0.2,
    2005: 5.1, 2006: 4.2, 2007: 5.8, 2008: 0.1,
    2009: 0.8, 2010: 8.6, 2011: 5.0, 2012: 1.5,
    2013: 5.6, 2014: -0.2, 2015: 0.6, 2016: 6.3,
    2017: 5.9, 2018: 2.6, 2019: 4.3, 2020: 3.3,
    2021: 3.5, 2022: 4.7, 2023: 1.4, 2024: 3.8,
}

# Agriculture share of GDP (%, at current prices)
# Source: MoSPI / Economic Survey
AGRI_GDP_SHARE = {
    1997: 25.1, 1998: 25.6, 1999: 24.2, 2000: 23.0,
    2001: 22.3, 2002: 20.5, 2003: 20.9, 2004: 19.0,
    2005: 18.3, 2006: 17.4, 2007: 16.8, 2008: 15.8,
    2009: 14.6, 2010: 14.6, 2011: 14.4, 2012: 13.9,
    2013: 13.9, 2014: 13.2, 2015: 13.4, 2016: 14.2,
    2017: 13.7, 2018: 13.2, 2019: 14.0, 2020: 16.4,
    2021: 15.3, 2022: 14.6, 2023: 14.4, 2024: 14.1,
}

# Food CPI inflation (% YoY, annual average)
# Source: MOSPI CPI-Combined, food & beverages subgroup
FOOD_CPI_INFLATION = {
    2002: 3.8, 2003: 3.5, 2004: 4.0, 2005: 4.4,
    2006: 7.7, 2007: 8.5, 2008: 11.1, 2009: 14.4,
    2010: 9.9, 2011: 6.7, 2012: 11.2, 2013: 12.2,
    2014: 6.4, 2015: 4.9, 2016: 4.2, 2017: 1.8,
    2018: 0.7, 2019: 4.8, 2020: 9.1, 2021: 4.2,
    2022: 4.2, 2023: 6.8, 2024: 7.5,
}

# Kharif foodgrain production (million tonnes)
# Source: Dept of Agriculture 4th Advance Estimates / Agricultural Statistics at a Glance
KHARIF_PRODUCTION_MT = {
    2000: 103.6, 2001: 109.8, 2002: 87.2, 2003: 117.1,
    2004: 99.2, 2005: 109.9, 2006: 110.3, 2007: 120.7,
    2008: 118.1, 2009: 103.5, 2010: 120.2, 2011: 131.3,
    2012: 128.1, 2013: 128.7, 2014: 127.0, 2015: 124.0,
    2016: 138.3, 2017: 140.4, 2018: 141.7, 2019: 143.4,
    2020: 150.6, 2021: 155.4, 2022: 149.9, 2023: 148.6,
    2024: 154.3,
}

# Kharif production growth (% YoY) — derived
KHARIF_PRODUCTION_GROWTH = {}
years_sorted = sorted(KHARIF_PRODUCTION_MT.keys())
for i in range(1, len(years_sorted)):
    y = years_sorted[i]
    prev = years_sorted[i - 1]
    KHARIF_PRODUCTION_GROWTH[y] = round(
        (KHARIF_PRODUCTION_MT[y] - KHARIF_PRODUCTION_MT[prev]) / KHARIF_PRODUCTION_MT[prev] * 100, 1
    )

# Tractor sales growth (% YoY) — proxy for rural demand
# Source: SIAM, TMA (Tractor Manufacturers Association), broker compilations
TRACTOR_SALES_GROWTH = {
    2002: -8.2, 2003: 21.5, 2004: 30.1, 2005: -5.2,
    2006: 11.3, 2007: 18.4, 2008: 3.2, 2009: 19.5,
    2010: 22.1, 2011: 13.6, 2012: 6.3, 2013: 6.8,
    2014: -12.8, 2015: -12.2, 2016: 18.7, 2017: 16.6,
    2018: 8.2, 2019: -8.5, 2020: 27.1, 2021: 8.6,
    2022: -3.1, 2023: 9.5, 2024: 5.2,
}

# Two-wheeler sales growth (% YoY) — broader rural demand proxy
# Source: SIAM
TWO_WHEELER_GROWTH = {
    2004: 17.2, 2005: 14.1, 2006: 12.3, 2007: 8.5,
    2008: 4.2, 2009: 15.6, 2010: 25.8, 2011: 14.2,
    2012: 2.8, 2013: 5.1, 2014: 8.1, 2015: 3.0,
    2016: 8.6, 2017: 14.8, 2018: 5.4, 2019: -14.2,
    2020: -13.2, 2021: 7.5, 2022: 14.2, 2023: 9.1,
    2024: 10.8,
}

# RBI/Economic Survey published sensitivities (for cross-check)
PUBLISHED_SENSITIVITIES = {
    "source": "RBI Annual Report 2019-20, Economic Survey 2023-24, various RBI staff papers",
    "monsoon_gdp_sensitivity": {
        "description": "1% shortfall in monsoon rainfall → GDP impact",
        "direct_agri": "-0.3% to -0.5% agri GVA",
        "overall_gdp": "-0.05% to -0.1% overall GDP (agri share ~14%)",
        "note": "Non-linear: severe drought (-20%+ deficit) has larger multiplier due to food inflation → RBI rate hikes → broader demand compression"
    },
    "drought_food_inflation": {
        "description": "Drought year impact on food inflation",
        "typical_range": "+200 to +400 bps above trend",
        "examples": "2009: +14.4%, 2015: modest due to global commodity weakness"
    },
    "drought_rbi_response": {
        "description": "RBI response to drought-driven food inflation",
        "typical": "Holds rates or delays cuts; rarely hikes solely for food inflation",
        "note": "2014-2016 cycle shows tolerance of food inflation if core is contained"
    }
}


def get_all_macro_series():
    """Return all macro series as a dict of name → data."""
    return {
        "agri_gva_growth": {
            "name": "Agriculture GVA Growth",
            "unit": "% YoY",
            "source": "MoSPI National Accounts / RBI DBIE",
            "data": AGRI_GVA_GROWTH,
            "negative_is_bad": True,
        },
        "food_cpi_inflation": {
            "name": "Food CPI Inflation",
            "unit": "% YoY average",
            "source": "MOSPI CPI-Combined (food & beverages)",
            "data": FOOD_CPI_INFLATION,
            "negative_is_bad": False,  # higher is bad here
        },
        "kharif_production_growth": {
            "name": "Kharif Foodgrain Production Growth",
            "unit": "% YoY",
            "source": "Dept of Agriculture / Agricultural Statistics at a Glance",
            "data": KHARIF_PRODUCTION_GROWTH,
            "negative_is_bad": True,
        },
        "tractor_sales_growth": {
            "name": "Tractor Sales Growth (rural demand proxy)",
            "unit": "% YoY",
            "source": "SIAM / Tractor Manufacturers Association",
            "data": TRACTOR_SALES_GROWTH,
            "negative_is_bad": True,
        },
        "two_wheeler_growth": {
            "name": "Two-Wheeler Sales Growth (rural demand proxy)",
            "unit": "% YoY",
            "source": "SIAM",
            "data": TWO_WHEELER_GROWTH,
            "negative_is_bad": True,
        },
    }
