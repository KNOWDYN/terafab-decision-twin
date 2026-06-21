# Investor Monitoring Example

## Stakeholder question

Which public signals change modeled cost, readiness, delay, and legitimacy exposure?

## Public signals to monitor

- public capital-cost or incentive claims
- power-price assumptions or utility-rate disclosures
- water-price or infrastructure-cost disclosures
- emissions-price assumptions
- public governance or partner complexity signals
- readiness or delay signals

## Model variables to review

| Signal | Model variable |
|---|---|
| Capital cost assumption | `economics.capex_USD` |
| Electricity price | `economics.electricity_price_USD_per_MWh` |
| Water price | `economics.water_price_USD_per_m3` |
| Delay or governance complexity | `governance.decision_latency_months` |
| Yield assumption | `manufacturing.baseline_yield` |
| Public incentive | `economics.incentive_public_USD` |

## Outputs to inspect

- `annualized_capex_USD`
- `total_opex_USD`
- `total_cost_USD`
- `cost_per_good_die_USD`
- `cost_per_compute_watt_USD`
- `maximum_governance_risk_index`
- `gate_matrix`

## What this does not prove

This workflow does not prove investment quality, financing status, valuation, acquisition interest, or actual commercial performance.
