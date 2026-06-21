# Engineering Monitoring Example

## Stakeholder question

Which public infrastructure signals indicate that energy, heat rejection, water, and manufacturing readiness assumptions should be revised?

## Public signals to monitor

- interconnection or grid capacity records
- cooling infrastructure disclosures
- water and wastewater capacity records
- public statements about tool qualification or readiness
- public supply-chain or packaging readiness signals

## Model variables to review

| Signal | Model variable |
|---|---|
| Grid capacity | `energy.firm_capacity_MW` |
| Load assumption | `energy.site_electric_load_MW` |
| Cooling capacity | `cooling.heat_rejection_capacity_MW` |
| UPW demand assumption | `water.upw_m3_per_wafer` |
| Qualification readiness | `manufacturing.qualification_readiness` |
| Packaging readiness | `manufacturing.packaging_readiness` |

## Outputs to inspect

- `energy_MWh`
- `heat_rejection_required_MW`
- `minimum_heat_rejection_margin_MW`
- `water_withdrawal_m3`
- `average_effective_yield`
- `average_readiness_index`
- `gate_matrix`

## What this does not prove

This workflow does not prove site design, tool availability, process qualification, yield, uptime, or actual operating data.
