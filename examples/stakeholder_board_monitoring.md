# Board Monitoring Example

## Stakeholder question

Before capital is committed, what public signals would change the modeled risk picture?

## Public signals to monitor

- grid capacity or power-procurement disclosures
- water permit or allocation records
- public construction or readiness statements
- public partner or governance announcements
- public legitimacy or permitting controversy indicators

## Model variables to review

| Signal | Model variable |
|---|---|
| Firm power availability | `energy.firm_capacity_MW` |
| Site electric load assumption | `energy.site_electric_load_MW` |
| Cooling reserve | `cooling.heat_rejection_capacity_MW` |
| Water withdrawal permit | `water.permit_withdrawal_m3_per_day` |
| Governance complexity | `governance.governance_complexity_index` |
| Public legitimacy | `policy.public_legitimacy_index` |

## Outputs to inspect

- `minimum_firm_capacity_margin_MW`
- `minimum_heat_rejection_margin_MW`
- `minimum_water_withdrawal_margin_m3_per_day`
- `legitimacy_margin`
- `maximum_governance_risk_index`
- `gate_matrix`

## What this does not prove

This workflow does not prove official Terafab progress, board approval, financing, private schedules, construction status, operation status, or endorsement.
