# Advanced Simulation Layer

The advanced simulation layer adds root-level tools under `strategic_simulation/`. It does not replace the deterministic decision twin. Instead, it treats `terafab_decision_twin.run_scenario()` as the kernel and builds higher-level stakeholder analysis around it.

## Architecture

```text
scenario JSON
  -> terafab_decision_twin.validate_scenario()
  -> terafab_decision_twin.run_scenario()
  -> strategic_simulation/monte_carlo.py
  -> strategic_simulation/game_theory.py
  -> strategic_simulation/reduced_order_model.py
  -> strategic_simulation/stakeholder_surface.py
  -> validation_lab/
```

## Monte Carlo

Monte Carlo propagates declared uncertainty through the deterministic model. It supports dependency-free distributions:

```text
fixed
uniform
triangular
normal_clipped
lognormal
discrete
```

Example use:

```python
import json
from pathlib import Path
from strategic_simulation import run_monte_carlo

config = json.loads(Path("strategic_simulation/examples/uncertainty_baseline_2026.json").read_text())
result = run_monte_carlo("scenarios/baseline_2026.json", config)
print(result["passed_probability"])
print(result["gate_failure_probability"])
```

Monte Carlo does not turn assumptions into facts. It only propagates declared uncertainty through the existing evidence-gated model.

## Game theory

The game-theory layer analyzes declared actor strategies and payoffs. It supports finite normal-form games, best responses, pure-strategy Nash-equilibrium detection, conflict index, and coordination-failure warnings.

Example use:

```python
import json
from pathlib import Path
from strategic_simulation import analyze_normal_form_game

config = json.loads(Path("strategic_simulation/examples/strategic_game_2026.json").read_text())
result = analyze_normal_form_game(config)
print(result["pure_strategy_nash_equilibria"])
```

Payoffs are declared assumptions unless independently sourced. The layer does not claim to know stakeholder preferences.

## Reduced-order model

The reduced-order model simulates a transparent low-dimensional state equation:

```text
x[t+1] = A x[t] + B u[t] + c + shock[t]
```

The state variables are decision abstractions such as power stress, heat-rejection stress, water stress, yield maturity, and policy legitimacy. This is not a high-fidelity fab physics simulator.

Example use:

```python
import json
from pathlib import Path
from strategic_simulation import simulate_reduced_order_model

config = json.loads(Path("strategic_simulation/examples/rom_transition_2026_2030.json").read_text())
result = simulate_reduced_order_model(config)
print(result["final_state"])
```

## Stakeholder decision surface

`strategic_simulation/stakeholder_surface.py` combines Monte Carlo, game, ROM, and validation outputs into a compact stakeholder-facing surface with board, investor, policy, and research views.
