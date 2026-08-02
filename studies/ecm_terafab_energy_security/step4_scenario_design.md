# Step 4 — scenario, uncertainty, and reproducibility design

## Purpose

Step 4 converts the deterministic Step 3 kernel into the predeclared 2026–2050 computational experiment. It estimates conditional production and resource requirements and tests pathway constraints. It does not determine official project feasibility or predict whether Terafab will be built.

## Architecture

The implementation is a study overlay that reuses the typed production-to-energy kernel:

- `terafab_energy_security/pathways.py` owns the predeclared pathway matrix and annual orchestration;
- `terafab_energy_security/uncertainty.py` owns scrambled-Sobol sampling, the Gaussian copula, convergence, independent Sobol diagnostics, and dependence-aware Shapley diagnostics;
- `terafab_energy_security/exports.py` gives the CLI and notebook one deterministic CSV/JSON export path;
- `studies/ecm_terafab_energy_security/scenarios/scenario_matrix.json` is the machine-readable scenario and assumption registry;
- `studies/ecm_terafab_energy_security/notebooks/terafab_energy_security_ecm.ipynb` executes the same public APIs as the CLI.

The established package is not forked or copied. No economic, project-finance, permitting, governance, or policy conclusions are introduced.

## Scenario matrix

The matrix contains 337 trajectories:

- one zero-increment no-build counterfactual;
- 336 combinations from 3 nonzero target-scale labels × 4 realization pathways × 4 supply portfolios × 7 stress conditions.

The research-fab and initial-large-scale branches account for 224 trajectories and remain numerically indeterminate because no public production-capacity value was admitted in Step 2. The full-announced-target branch accounts for 112 conditional numerical trajectories. The four realization pathways are accelerated, reference, delayed, and not-realized-by-2050. Each numerical trajectory has annual rows from 2026 through 2050.

The primary target branch interprets the public phrase as aggregate rated power of good devices manufactured per year. A mandatory alternative, publicly undefined semantic branch remains explicit and non-numeric. Neither branch assigns the public `1 TW/year` statement as fab electrical load.

## Portfolio and stress logic

The supply portfolios are grid-dominant, firm onsite, solar plus five-hour storage plus grid, and firm low-carbon hybrid. Their sizes are scenario calculations, not claimed project capacities. Commissioning dates combine frozen first-availability information, generic lead times, mandatory schedule adders, and the declared infrastructure-delay stress.

The stress conditions independently test coincident summer peak, winter peak and availability, supporting-infrastructure delay, yield underperformance, cooling/water capacity, and firm-supply outage. Cooling and water capacity are normally unknown; only the named failure stress assigns capacity at 80% of the calculated requirement.

Official ERCOT protocol-prescribed and SB6 counterfactual reserve-margin series are retained separately for 2026–2030. No ERCOT baseline is extrapolated after 2030. EIA counterfactual-baseline and high-electricity-demand annual series remain separate national context cases through 2050.

## Uncertainty protocol

The Step 2 uncertainty contract is executed without changing distributions or seed:

- 10 uncertain manufacturing/facility parameters;
- scrambled Sobol sequence with seed `20260801`;
- 16,384 preliminary and 32,768 confirmation samples;
- Gaussian copula with the locked Spearman-to-latent-Pearson transform;
- independent and correlated designs, including ±0.20 correlation stresses;
- a strict less-than-1% doubling-convergence rule for four estimable resource summaries;
- independent-marginal first- and total-order Sobol diagnostics with bootstrap intervals;
- dependence-aware conditional-variance Shapley allocation for a linear surrogate, reported with its explained-variance diagnostic and bootstrap intervals.

The sensitivity outcome implemented here is conditional facility peak. It is useful for model diagnosis but cannot replace H4's locked realization-year or joint-feasibility outcome. H4 therefore remains indeterminate. Feasibility probability likewise remains `null`, because indispensable capacity and probabilistic adequacy evidence are absent.

## Reproducible entry points

From the repository root:

```bash
python -m terafab_energy_security run-matrix \
  studies/ecm_terafab_energy_security \
  --output-directory /tmp/terafab-matrix

python -m terafab_energy_security run-uncertainty \
  studies/ecm_terafab_energy_security \
  --mode final \
  --output /tmp/terafab-uncertainty.json
```

The notebook's `final` mode calls the same functions and locked sample counts. Generated study outputs are ignored by Git so that a later results-freeze decision can control which derived artifacts, if any, enter the repository.
