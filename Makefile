.PHONY: test validate run report

test:
	python -m unittest discover -s tests

validate:
	python -m terafab_decision_twin.cli validate scenarios/baseline_2026.json

run:
	python -m terafab_decision_twin.cli run scenarios/baseline_2026.json --output runs/baseline_2026.json --report runs/baseline_2026.md

report:
	python -m terafab_decision_twin.cli report scenarios/baseline_2026.json
