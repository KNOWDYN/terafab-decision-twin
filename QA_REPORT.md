# QA Report

Validation performed during artifact build:

```text
python -m unittest discover -s tests -v
```

Result:

```text
Ran 16 tests
OK
```

Coverage intent:

- schema validation;
- evidence-status audit;
- first-law heat-rejection equation;
- entropy and exergy functions;
- water permit margins;
- yield and good-die output;
- capital recovery factor;
- engine run outputs;
- multi-year quarterly time axis;
- one-terawatt stress-test status discipline;
- CLI validation and reporting.

Known v1 boundary: scenario numerical defaults are declared assumptions or stress-test assumptions unless later replaced with admissible verified inputs.
