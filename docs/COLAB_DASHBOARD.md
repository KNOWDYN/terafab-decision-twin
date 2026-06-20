# Colab Dashboard

The repository ships the computational core and a lightweight notebook entry point at `notebooks/terafab_colab_dashboard.ipynb`.

A public Colab workflow should expose:

1. scenario upload/editor;
2. evidence-status checker;
3. simulation run button;
4. gate matrix;
5. scalar/vector tables;
6. unresolved-variable table;
7. export bundle download.

Notebook imports:

```python
from terafab_decision_twin import load_scenario, run_scenario
from terafab_decision_twin.report import markdown_report
```

The notebook is intentionally optional. The package, CLI, scenarios, and tests are the authoritative public release surface.
