# Step 6 manuscript and reproducibility package

This directory turns the frozen Step 1--5 scientific contract and publication
bundle into an editable initial-submission package for *Energy Conversion and
Management* (ECM). It is an independent, prospective conditional constraint
analysis. It is not a validated digital twin of Terafab and contains no
verified Terafab operating data.

The current ECM guide asks for editable source files, an abstract no longer
than 250 words, one to seven keywords, and three to five highlights of no more
than 85 characters each. The guide and Elsevier AI policy remain the controlling
sources at submission time:

- <https://www.sciencedirect.com/journal/energy-conversion-and-management/publish/guide-for-authors>
- <https://www.elsevier.com/about/policies-and-standards/generative-ai-policies-for-journals>

## Reproduce and build

Run from the repository root:

```bash
python -m terafab_energy_security build-publication \
  studies/ecm_terafab_energy_security \
  --mode final \
  --output-directory studies/ecm_terafab_energy_security/outputs/final/publication

python studies/ecm_terafab_energy_security/paper/validate_manuscript.py

make -C studies/ecm_terafab_energy_security/paper all
```

The `make` command compiles `main.pdf`, `supplement.pdf`, and
`cover_letter.pdf` with `latexmk`. Generated PDFs and LaTeX intermediates are
ignored. The manuscript deliberately uses the standard `article` class for a
portable, free-format initial submission; migrate it to the current Elsevier
template only if the live submission workflow requires that template.

## Files

- `main.tex`: complete manuscript with all ten prespecified figures and six
  compact main-text tables.
- `supplement.tex`: evidence, computation, replacement, and reproduction
  details.
- `references.bib`: bibliography built from the admitted public-source
  registry plus numerical-method references.
- `highlights.txt`: ECM-length-checked highlights.
- `cover_letter.tex`: journal-specific cover letter.
- `claim_traceability.csv`: auditable mapping from quantitative manuscript
  claims to generated machine-readable artifacts.
- `submission_checklist.md`: scientific and author-controlled submission
  checks.
- `validate_manuscript.py`: dependency-free structural and claim-boundary
  validator.

## Licensing and status

The repository is source-available, not open source. Noncommercial academic
use is governed by the root `ACADEMIC_LICENSE.md`; commercial use requires a
separate written license under `COMMERCIAL_LICENSE.md`. The analysis is not
affiliated with, endorsed by, authorized by, sponsored by, or connected to
Terafab or its employees. Outputs are scenario-dependent analytical estimates,
not verified operating facts, engineering certification, investment advice,
permitting advice, procurement advice, or regulatory findings.
