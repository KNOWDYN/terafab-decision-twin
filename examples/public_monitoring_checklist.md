# Public Monitoring Checklist

Use this checklist to monitor public progress signals without turning public signals into private claims.

## 1. Collect only admissible public signals

Useful public signals may include:

- public filings
- public agency records
- utility or grid planning disclosures
- water authority documents
- permitting notices
- public statements
- reported media claims
- user-declared assumptions

Do not use restricted, leaked, confidential, or private-source material.

## 2. Classify the evidence status

Use the narrowest honest status:

| Status | Use when |
|---|---|
| `verified_project_fact` | The repo has an admitted public fact supporting it. |
| `filed_claimed` | A public filing or formal public record states it. |
| `reported` | A public report attributes it, but the project has not independently verified it. |
| `user_provided` | A user supplies it for their own scenario. |
| `scenario_assumption` | It is a model assumption for testing consequences. |
| `stress_test_assumption` | It is intentionally severe or exploratory. |
| `unknown` | The value should not be inferred. |

## 3. Map the signal to model variables

Common mappings:

| Public signal | Possible model variable |
|---|---|
| Utility interconnection, grid plan, or power procurement signal | `energy.firm_capacity_MW` |
| Public load or demand assumption | `energy.site_electric_load_MW` |
| Cooling infrastructure or thermal-management claim | `cooling.heat_rejection_capacity_MW` |
| Water permit, water allocation, or withdrawal record | `water.permit_withdrawal_m3_per_day` |
| Discharge permit or wastewater record | `water.permit_discharge_m3_per_day` |
| Manufacturing readiness or qualification statement | `manufacturing.qualification_readiness` |
| Governance or partnership update | `governance.partner_count`, `governance.decision_latency_months` |
| Public legitimacy or permitting conflict signal | `policy.public_legitimacy_index` |

## 4. Run the model only after labeling uncertainty

Every material input should have:

- `value`
- `unit`
- `status`
- `source_ref`
- `confidence`
- `notes`

## 5. What this does not prove

A public monitoring scenario does not prove:

- private Terafab schedules
- confidential contracts
- construction status
- operational readiness
- financing status
- official Terafab endorsement
- actual site load
- actual water use
- actual production yield
- verified economics

It only shows the consequences of declared, evidence-labeled inputs.
