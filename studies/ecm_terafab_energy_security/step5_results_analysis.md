# Step 5 — results analysis and publication bundle

## Result-level conclusion

The publicly announced Terafab concept cannot presently be classified as realistic or unrealistic from admitted public evidence. Its realism is **not demonstrated** because the public record does not define the `1 TW/year` output dimension, phase manufacturing capacity, facility electrical load, thermal capacity, water entitlement, executable interconnection, or probabilistic ERCOT adequacy consequences. This is an indeterminate evidence result, not proof of physical impossibility.

Under the primary conditional interpretation—aggregate rated power embodied in good compute devices manufactured per year—the resource requirements are large enough to be material to regional and national electricity planning. The model therefore answers what the announcement would imply under transparent assumptions, while refusing to convert those implications into an official project-feasibility finding.

## Central conditional trajectory

The accelerated, grid-dominant, normal-stress pathway gives the following central requirements:

| Year | Target fraction | Wafer starts (million/year) | Electricity (TWh/year) | Coincident peak (GW) | Water withdrawal (million m³/year) | Share of AEO baseline US electricity |
|---:|---:|---:|---:|---:|---:|---:|
| 2029 | 0.25 | 17.07 | 33.79 | 4.15 | 142.18 | 0.75% |
| 2032 | 0.50 | 34.15 | 67.59 | 8.29 | 284.36 | 1.45% |
| 2035 | 0.75 | 51.22 | 101.38 | 12.44 | 426.54 | 2.05% |
| 2037 | 1.00 | 68.29 | 135.17 | 16.58 | 568.72 | 2.64% |
| 2050 | 1.00 | 68.29 | 135.17 | 16.58 | 568.72 | 2.25% |

These values are conditional model outputs, not disclosed Terafab design values. The apparent decline in national share after full realization comes from growth in the EIA denominator, not from lower modeled facility demand.

## Uncertainty envelope

For the full target under the locked correlated design and 32,768 confirmation samples:

- median wafer starts: 50.45 million/year;
- median facility electricity: 125.11 TWh/year;
- p95 facility coincident peak: 91.54 GW;
- p95 external water withdrawal: 1.571 billion m³/year;
- feasibility probability: unavailable, because required project-capacity and probabilistic-adequacy evidence is absent.

The p95 values are marginal output quantiles and must not be combined as a single joint design point. The wide peak-load tail is driven by the predeclared architecture, die, yield, power, and electricity-intensity uncertainty ranges.

## ERCOT screening result

The accelerated pathway is at 25% of the conditional target in 2029–2030, implying 4.15 GW of coincident load before onsite accreditation. In 2030, the matched normal supply portfolios produce:

| Portfolio | Onsite accredited capacity (GW) | Net grid peak (GW) | Protocol-case reserve-margin change (percentage points) |
|---|---:|---:|---:|
| Firm low-carbon hybrid | 0.00 | 4.15 | +0.81 |
| Firm onsite | 3.32 | 0.83 | +0.17 |
| Grid dominant | 0.00 | 4.15 | +0.81 |
| Renewable-storage-grid | 2.78 | 1.37 | +0.27 |

The firm low-carbon hybrid has no accredited onsite capacity in 2030 because its predeclared commissioning date is later. The positive protocol-case reserve-margin changes do not indicate improved reliability: the scenario assigns new grid capacity at a 15% reserve fraction, which exceeds the negative protocol-prescribed counterfactual margin. Under the more favorable SB6 counterfactual, the same grid-dominant increment reduces reserve margin. This sign reversal demonstrates counterfactual dependence and is why reserve margin remains a screening quantity rather than an adequacy verdict.

No official ERCOT counterfactual was extrapolated beyond 2030. LOLE, event duration, load-shed magnitude, and expected unserved energy were not invented.

## Gate results

Across 20,720 active-case gate evaluations:

- 8,724 pass;
- 2,228 fail under explicit schedule, supply, thermal, or water stresses;
- 9,768 remain indeterminate.

Manufacturing throughput, evidence sufficiency, and regional adequacy are indeterminate for every active case. Thermal and water capacity are indeterminate in ordinary cases and fail only in the declared 80%-capacity stress. Schedule precedence and supply deliverability fail in 818 evaluations. Consequently, all 336 nonzero trajectories remain indeterminate and no first joint-pass year exists.

## Sensitivity and convergence

The final 16,384→32,768 sample doubling test passes under independence, baseline correlation, and both ±0.20 correlation stresses. The worst relative change is 0.2900%, below the locked 1% limit.

For the independent conditional facility-peak diagnostic, the leading total-order inputs are:

1. logic dies per module: 0.5397;
2. fab electricity intensity: 0.2404;
3. die area: 0.1495;
4. module rated power: 0.0371;
5. effective yield: 0.0324.

The top two account for 78.0212% of normalized total-order mass, below the predeclared 80% diagnostic threshold. Bootstrap ranks are stable. The correlated Shapley analysis retains logic dies per module, fab electricity intensity, and die area as the leading three and has a linear-surrogate `R²` of 0.9405. H4 nevertheless remains indeterminate because its locked outcome is realization year or joint feasibility, not conditional facility peak.

## Publication artifacts

The final bundle contains:

- ten numbered figures in PNG and PDF;
- one machine-readable CSV for every figure;
- six prespecified tables;
- the full 337-trajectory matrix, 2,825 annual rows, and 20,720 gate rows;
- final uncertainty and hypothesis-disposition JSON;
- SHA-256 hashes for every generated publication artifact;
- explicit replacement/limitation records for every unavailable prespecified metric.

Figure 3 is a benchmark diagnostic rather than an independent measured-versus-modeled validation figure. Figure 7 replaces unavailable LOLE/EUE with accredited-capacity and reserve-margin screening. Figure 8 is limited to EIA annual-electricity context because national peak, fuel, and emissions outputs are not identified. These replacements are scientific constraints, not presentation choices.

## Step 6 writing boundary

The manuscript may conclude that current public evidence does not demonstrate the realism of the announcement and that the admitted interpretation implies energy-security-material resource requirements. It may not conclude that Terafab is officially feasible, infeasible, validated, endorsed, or certain to be built. The method must be described as a prospective conditional constraint analysis, not as a validated digital twin of Terafab.
