# Step 2 Evidence Review

**Study ID:** `ecm_terafab_us_energy_security`
**Evidence freeze:** 2026-08-01
**Permitted claim level:** Prospective constraint analysis

This review tests whether public evidence is sufficient to construct the
predeclared model without converting project claims, public filings, or
industry comparators into verified Terafab facts.

## Empirical kill-test decisions

| Kill test | Decision | Evidence admitted | Binding limitation and model consequence |
|---|---|---|---|
| Target semantics | Conditional pass | The public website reports “Terafab output 1 TW/Year” and separately refers to more than 1 TW of solar | The output dimension is not defined. The primary `W_rated/year` interpretation is a model identity, not a verified project meaning. Alternative interpretations and an `indeterminate` outcome remain mandatory. |
| Throughput translation | Conditional pass | Public accelerator power analogs, 300 mm exposure geometry, lithography-tool throughput, and foundry-scale capacity comparators | Terafab product mix, die area, yield, packaging architecture, and phase wafer capacity are undisclosed. Throughput can be bounded only as scenario-conditioned calculation output. |
| Facility resource intensities | Conditional pass | Independent corporate aggregate electricity data, a measured component-level fab study, US cleanroom benchmarks, and two water references | Sources differ in node, product, site boundary, mask layers, wafer starts versus shipments, and vintage. Broad predictive intervals are mandatory; a validated Terafab twin is prohibited. |
| Geographic attribution | Conditional pass | Eight Texas JETI applications place four proposed phases in Grimes County school districts | A Texas site does not prove the final ERCOT point, available transmission capacity, or interconnection date. ERCOT results are explicitly conditional on interconnection, and deliverability remains a required gate. |
| Official adequacy standard | Pass | PUCT's three-part frequency, duration, and magnitude rule; the annually versioned 2026 magnitude; and both protocol-prescribed and SB6 ERCOT CDR cases | Planning reserve margin is screening evidence only. A regulatory pass requires the rule's probabilistic measures; the 2026 magnitude cannot be held constant through 2050. |
| Supply deliverability | Conditional pass | EIA generic technology lead times and ERCOT portfolio/season-dependent ELCC evidence | The generic times omit site control, permitting, interconnection, transmission, fuel, water, commissioning, and supply-chain delay. Any pathway without identified adders and accredited availability fails the deliverability gate rather than receiving unlimited onsite supply. |

## Material project facts not established

No public source admitted in Step 2 establishes any of the following as a
verified project value:

- phase wafer starts or good-device throughput;
- facility MW, annual electricity, hourly load shape, or final point of
  interconnection;
- process recipe, mask-layer count, die size, yield, package design, or product
  rated-power mix;
- water entitlement, withdrawal, consumption, recycling definition, or
  wastewater capacity;
- commissioned onsite generation, storage, transmission, firm fuel, or
  accredited capacity.

These fields remain `null` in the frozen registry. Step 3 may calculate
scenario envelopes, but it may not relabel those outputs as announced or filed
project specifications.

## Evidence-driven scope decision

The evidence supports building a **prospective, conditional constraint model**.
It does not support building or claiming a validated digital twin of Terafab.
The scientific question remains answerable because the model contract already
permits `conditionally_feasible`, `not_demonstrated`, and `indeterminate`
classifications. A single unconditional yes/no verdict would exceed the
evidence.

No Step 1 hypothesis is retired. H3 can be tested only where accredited
capacity or hourly adequacy evidence is sufficient; otherwise its predeclared
result is `indeterminate`. H4's bootstrap stability rule is now numerically
locked in `uncertainty_dependencies.json` before any model results are run.
