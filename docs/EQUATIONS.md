# Equation Coverage

This implementation preserves the locked blueprint's model coverage in executable v1 form.

## Mass and species

`models.mass.species_balance` implements:

```text
dM_k/dt = inflows_k - outflows_k + reaction_sources_k
```

`campus_mass_residual_mdot` returns total input minus total output mass flow.

## First law and heat rejection

`models.first_law.heat_rejection_required_MW` implements the practical fab-scale theorem:

```text
Q_reject ≈ W_e * heat_rejection_fraction + Q_waste - E_stored_product
```

The thermodynamic gate requires heat-rejection capacity to cover this load.

## Entropy and exergy

`models.entropy.heat_transfer_entropy_generation_MW_per_K` computes heat-transfer entropy generation:

```text
S_gen = Q * (1/T_c - 1/T_h)
```

`models.exergy.exergy_destroyed_MW` computes:

```text
X_destroyed = T_0 * S_gen
```

## Power

The power model computes energy consumption, firm-capacity margin, emissions, and electricity cost.

## Cooling and water

The cooling model computes auxiliary cooling power and heat-rejection margins. The water model computes withdrawal, consumptive use, wastewater, UPW demand, and permit margins.

## Manufacturing and yield

The manufacturing model computes learned yield, contamination-adjusted effective yield, good-die output, and compute-output proxy.

## Economics

The economics model computes annualized capex, opex terms, emissions cost, cost per good die, and cost per compute watt.

## Governance, policy, and real options

Governance and policy modules produce indices for governance risk, governance readiness, public benefit, public burden, legitimacy margin, and phase-gate action.
