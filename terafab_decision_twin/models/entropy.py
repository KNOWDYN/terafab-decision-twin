from __future__ import annotations


def heat_transfer_entropy_generation_MW_per_K(heat_MW: float, hot_K: float, cold_K: float) -> float:
    if hot_K <= 0 or cold_K <= 0:
        raise ValueError("Reservoir temperatures must be positive Kelvin values.")
    # Positive when heat moves from hot_K to cold_K and cold_K <= hot_K.
    return max(0.0, float(heat_MW) * (1.0 / float(cold_K) - 1.0 / float(hot_K)))


def entropy_balance_rate_MW_per_K(s_in: float, s_out: float, heat_terms: list[tuple[float, float]], s_gen: float) -> float:
    heat_entropy = sum(q / T for q, T in heat_terms if T > 0)
    return float(s_in) - float(s_out) + heat_entropy + float(s_gen)
