# Colab Dashboard Stub

The blueprint calls for a free-tier Google Colab dashboard. This v1 repo ships the computational core and CLI that a notebook should call.

A future notebook should expose:

1. scenario upload/editor;
2. evidence-status checker;
3. run button;
4. gate dashboard;
5. scalar/vector plots;
6. report export.

The notebook should import:

```python
from terafab_decision_twin import load_scenario, run_scenario
from terafab_decision_twin.report import markdown_report
```

No notebook is required for the core package tests to pass.
