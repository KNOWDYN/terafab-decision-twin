from __future__ import annotations

import math
from typing import Any, Dict, List, Mapping, Sequence


def _vector_from(value: Mapping[str, float] | Sequence[float], names: Sequence[str], label: str) -> List[float]:
    if isinstance(value, Mapping):
        return [float(value.get(name, 0.0)) for name in names]
    values = [float(v) for v in value]
    if len(values) != len(names):
        raise ValueError(f"{label} length must equal number of state variables")
    return values


def _matrix(rows: Sequence[Sequence[float]], n_rows: int, n_cols: int, label: str) -> List[List[float]]:
    mat = [[float(v) for v in row] for row in rows]
    if len(mat) != n_rows or any(len(row) != n_cols for row in mat):
        raise ValueError(f"{label} must have shape {n_rows}x{n_cols}")
    return mat


def _mat_vec(mat: Sequence[Sequence[float]], vec: Sequence[float]) -> List[float]:
    return [sum(float(a) * float(b) for a, b in zip(row, vec)) for row in mat]


def _add(*vectors: Sequence[float]) -> List[float]:
    return [sum(vals) for vals in zip(*vectors)]


def _clip(vec: Sequence[float], lower: float | None, upper: float | None) -> List[float]:
    out = []
    for value in vec:
        x = float(value)
        if lower is not None:
            x = max(float(lower), x)
        if upper is not None:
            x = min(float(upper), x)
        out.append(x)
    return out


def _state_dict(names: Sequence[str], values: Sequence[float], step: int) -> Dict[str, Any]:
    row = {name: float(value) for name, value in zip(names, values)}
    row["step"] = step
    return row


def simulate_reduced_order_model(config: Mapping[str, Any]) -> Dict[str, Any]:
    """Simulate a transparent reduced-order state trajectory.

    The model is a low-dimensional decision abstraction:
        x[t+1] = A x[t] + B u[t] + c + shock[t]
    """
    names = list(config.get("state_variables", []))
    if not names:
        raise ValueError("ROM requires state_variables")
    n = len(names)
    controls = list(config.get("control_variables", []))
    m = len(controls)
    steps = int(config.get("steps", len(config.get("control_policy", [])) or 1))
    if steps <= 0:
        raise ValueError("ROM steps must be positive")
    A = _matrix(config.get("A", [[1.0 if i == j else 0.0 for j in range(n)] for i in range(n)]), n, n, "A")
    B = _matrix(config.get("B", [[0.0 for _ in range(m)] for _ in range(n)]), n, m, "B") if m else [[0.0] * 0 for _ in range(n)]
    x = _vector_from(config.get("x0", [0.0] * n), names, "x0")
    c = _vector_from(config.get("c", [0.0] * n), names, "c")
    policy = list(config.get("control_policy", []))
    shocks = list(config.get("shocks", []))
    lower = config.get("clip_lower")
    upper = config.get("clip_upper")

    trajectory: List[Dict[str, Any]] = [_state_dict(names, x, 0)]
    for t in range(steps):
        u_spec = policy[t] if t < len(policy) else {}
        if isinstance(u_spec, Mapping):
            u = [float(u_spec.get(name, 0.0)) for name in controls]
        else:
            u = [float(v) for v in u_spec]
            if len(u) != m:
                raise ValueError("control_policy vector length must equal control variable count")
        shock_spec = shocks[t] if t < len(shocks) else [0.0] * n
        shock = _vector_from(shock_spec, names, "shock")
        x_next = _add(_mat_vec(A, x), _mat_vec(B, u), c, shock)
        x_next = _clip(x_next, lower, upper)
        if any(not math.isfinite(v) for v in x_next):
            raise ValueError("ROM produced non-finite state")
        x = x_next
        trajectory.append(_state_dict(names, x, t + 1))

    values_only = [[row[name] for name in names] for row in trajectory]
    max_abs = max(abs(v) for row in values_only for v in row) if values_only else 0.0
    final = trajectory[-1]
    return {
        "kind": "reduced_order_model_result",
        "model_boundary": "Transparent reduced-order decision abstraction; not a high-fidelity fab physics simulator.",
        "state_variables": names,
        "control_variables": controls,
        "steps": steps,
        "trajectory": trajectory,
        "final_state": {name: final[name] for name in names},
        "diagnostics": {
            "max_abs_state": max_abs,
            "stability_warning": bool(max_abs > float(config.get("stability_warning_threshold", 10.0))),
            "trajectory_length": len(trajectory),
        },
    }
