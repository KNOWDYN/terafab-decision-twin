# Policy Monitoring Example

## Stakeholder question

Which public infrastructure, permitting, and legitimacy signals would make a Terafab-scale scenario more or less decision-ready?

## Public signals to monitor

- water authority notices
- discharge permit records
- public grid or utility planning disclosures
- public incentive or permitting records
- public comments and community legitimacy signals

## Model variables to review

| Signal | Model variable |
|---|---|
| Water withdrawal allowance | `water.permit_withdrawal_m3_per_day` |
| Wastewater discharge allowance | `water.permit_discharge_m3_per_day` |
| Local water stress | `policy.local_water_stress_index` |
| Regulatory readiness | `policy.regulatory_readiness_index` |
| Public legitimacy | `policy.public_legitimacy_index` |
| Domestic supply benefit | `policy.domestic_supply_security_index` |

## Outputs to inspect

- `water_withdrawal_m3`
- `wastewater_m3`
- `minimum_water_withdrawal_margin_m3_per_day`
- `minimum_wastewater_discharge_margin_m3_per_day`
- `public_benefit_index`
- `public_burden_index`
- `legitimacy_margin`

## What this does not prove

This workflow does not prove permit approval, compliance, public acceptance, political support, or actual water use.
