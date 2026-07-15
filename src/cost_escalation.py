MODEL_COST_YEARS = {
    "abr1000": 2017,
    "ap1000": 2018,
    "heatpipe": 2018,
    "lfr": 2017,
    "lpsr": 2018,
    "pwr12-be": 2017,
    "fusion": 2015,
    "stellarator": 2015,
}

# CPI-U, U.S. city average, all items, annual average. Source: BLS CPI-U.
CPI_U_ANNUAL_AVERAGE = {
    2015: 237.017,
    2017: 245.120,
    2018: 251.107,
    2024: 313.689,
}

TARGET_DOLLAR_YEAR = 2024


def model_cost_year(ref_model: str) -> int:
    return MODEL_COST_YEARS.get(str(ref_model).lower(), 2017)


def cpi_escalation_factor(from_year: int, to_year: int = TARGET_DOLLAR_YEAR) -> float:
    return CPI_U_ANNUAL_AVERAGE[to_year] / CPI_U_ANNUAL_AVERAGE[from_year]
