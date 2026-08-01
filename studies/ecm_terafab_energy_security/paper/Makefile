PYTHON ?= python3
LATEXMK ?= latexmk

.PHONY: all publication validate manuscript supplement cover-letter clean

all: validate manuscript supplement cover-letter

publication:
	cd ../../.. && $(PYTHON) -m terafab_energy_security build-publication \
		studies/ecm_terafab_energy_security --mode final \
		--output-directory studies/ecm_terafab_energy_security/outputs/final/publication

validate:
	$(PYTHON) validate_manuscript.py

manuscript:
	$(LATEXMK) -pdf -interaction=nonstopmode -halt-on-error main.tex

supplement:
	$(LATEXMK) -pdf -interaction=nonstopmode -halt-on-error supplement.tex

cover-letter:
	$(LATEXMK) -pdf -interaction=nonstopmode -halt-on-error cover_letter.tex

clean:
	$(LATEXMK) -C main.tex
	$(LATEXMK) -C supplement.tex
	$(LATEXMK) -C cover_letter.tex
