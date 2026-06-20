HOURS_PER_YEAR = 8760.0
DAYS_PER_YEAR = 365.0
SECONDS_PER_HOUR = 3600.0
MW_TO_W = 1_000_000.0
MWH_TO_MJ = 3600.0
MWH_TO_KWH = 1000.0
TWH_TO_MWH = 1_000_000.0
KG_PER_TONNE = 1000.0


def nonnegative(name: str, value: float) -> float:
    value = float(value)
    if value < 0:
        raise ValueError(f"{name} must be non-negative; got {value}")
    return value


def clamp(value: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, float(value)))


def safe_div(numerator: float, denominator: float, default: float = 0.0) -> float:
    return default if denominator == 0 else numerator / denominator
