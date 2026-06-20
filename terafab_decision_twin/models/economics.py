from __future__ import annotations


def capital_recovery_factor(discount_rate: float, years: int) -> float:
    r = float(discount_rate)
    n = int(years)
    if n <= 0:
        return 1.0
    if abs(r) < 1e-12:
        return 1.0 / n
    return r * (1.0 + r) ** n / ((1.0 + r) ** n - 1.0)


def annualized_capex_USD(capex_USD: float, discount_rate: float, asset_life_years: int) -> float:
    return max(0.0, float(capex_USD) * capital_recovery_factor(discount_rate, asset_life_years))


def water_cost_USD(volume_m3: float, price_USD_per_m3: float) -> float:
    return max(0.0, float(volume_m3) * float(price_USD_per_m3))


def emissions_cost_USD(emissions_tCO2: float, price_USD_per_tCO2: float) -> float:
    return max(0.0, float(emissions_tCO2) * float(price_USD_per_tCO2))


def cost_per_good_die_USD(total_cost_USD: float, good_die: float) -> float:
    return float("inf") if good_die <= 0 else float(total_cost_USD) / float(good_die)


def cost_per_compute_watt_USD(total_cost_USD: float, compute_watts: float) -> float:
    return float("inf") if compute_watts <= 0 else float(total_cost_USD) / float(compute_watts)
