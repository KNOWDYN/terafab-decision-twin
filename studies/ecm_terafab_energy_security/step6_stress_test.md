# Step 6 stress-test report

Date: 2026-08-01
Scope: ECM manuscript completeness, quantitative traceability, reviewer
resistance, document rendering, reproducibility, licensing, restricted-source
exclusion, and release-artifact integrity.

## Build and automated checks

| Test | Result | Evidence |
|---|---:|---|
| ECM abstract limit | Pass | 232 words; current guide limit is 250. |
| ECM keyword limit | Pass | 7 keywords; current guide permits 1--7. |
| ECM highlight format | Pass | 5 highlights; lengths 78, 73, 72, 77 and 77 characters, each below 85. |
| Prespecified paper coverage | Pass | 10 figures and 6 compact main-text tables; full versions remain machine-readable. |
| Citation integrity | Pass | 17 cited bibliography records; no missing or uncited record. |
| Quantitative claim traceability | Pass | 15 principal manuscript claims recomputed from the final CSV/JSON bundle. |
| Scenario/gate traceability | Pass | 337 trajectories and all 20,720 gate rows checked; counts remain 8,724 pass, 2,228 fail and 9,768 indeterminate. |
| Hypothesis boundary | Pass | H1--H4 remain indeterminate in the final manifest and manuscript. |
| Replacement-figure boundary | Pass | Figures 3, 7 and 8 remain explicitly limited replacements; no empirical accuracy, LOLE/EUE, national peak, fuel or emissions value is invented. |
| Manuscript build | Pass | `main.pdf`: 18 pages; no unresolved references, citations, LaTeX errors or overfull boxes. |
| Supplement build | Pass | `supplement.pdf`: 3 pages; no unresolved references, LaTeX errors or overfull boxes. |
| Cover-letter build | Pass after visual revision | 1 page; compressed closing detected visually and corrected. |
| Visual PDF QA | Pass | All 22 rendered pages reviewed for clipping, overlap, legibility, page flow and missing glyphs. |
| Repository regression suite | Pass | 111 tests passed. |
| Evidence validator | Pass | Frozen evidence validates without live retrieval. |
| Restricted-source scan | Pass | No banned private or unpublished source filename is present. |
| Source distribution | Pass after manifest revision | Manuscript sources and study contracts are included; generated result directories are pruned. |
| Wheel distribution | Pass | Overlay package, console entry point, and both academic/commercial license files are present. |
| Release verifier | Pass | Source distribution and wheel satisfy the expanded artifact contract. |
| Git publication boundary | Pass | No commit, push, or pull request was created; those remain Step 7. |

## Defects found and corrected during stress testing

1. The Hu et al. DOI suffix was corrected from `ctz040` to the
   publisher-confirmed `ctz041`. This is a bibliographic correction; no parameter
   or result changed.
2. The publication manifest's reproduction command embedded the local absolute
   checkout path. It now uses the portable repository-relative study path and
   hashes the source registry.
3. LaTeX font expansion and unescaped license filenames initially prevented a
   portable build. The manuscript now compiles with the installed standard
   toolchain.
4. PDF visual QA detected a compressed cover-letter closing that compilation
   alone did not identify. The closing was reflowed and visually rechecked.
5. The broad study sdist rule initially captured ignored generated outputs. The
   manifest now prunes the output directory, and the release verifier rejects
   any future recurrence.

## Adversarial reviewer tests

### Does the paper answer whether Terafab is realistic?

Yes, within the evidence contract. It answers that current public evidence does
not demonstrate realism because indispensable target, manufacturing, utility,
interconnection and adequacy quantities remain unknown. It explicitly states
that this is not proof of infeasibility.

### Does the analysis confuse `1 TW/year` of product output with factory load?

No. The target is conditionally interpreted as aggregate rated power embodied
in good devices produced per calendar year and then translated through dies,
yield, wafer starts and facility intensity. Factory peak is a derived 16.58 GW
central output, not the public 1 TW wording.

### Can the manuscript be attacked as an empirically validated digital twin?

The limitation is exposed rather than concealed. The manuscript calls the
method a prospective conditional constraint analysis, reports zero independent
numeric holdouts, replaces the validation figure with a benchmark diagnostic,
and makes no Terafab accuracy claim. This reduces overclaiming risk but remains
the paper's main scientific limitation.

### Are extreme uncertainty values presented as forecasts or a joint worst case?

No. The 91.54 GW and 1.571 billion m³/year p95 values are identified as separate
marginal quantiles under broad epistemic scenario distributions. They are not
combined and are not called expected project values.

### Is reserve margin presented as reliability proof?

No. The text shows counterfactual sign reversal, restricts ERCOT results to the
official 2030 horizon, leaves LOLE/EUE null, and keeps regional adequacy
indeterminate.

### Does the paper fit *Energy Conversion and Management*?

The manuscript centers its contribution on the production-to-energy conversion,
facility electricity/heat/water balances, supply accreditation, energy-system
burden and uncertainty. Finance, policy scoring and governance are excluded from
the principal analysis. Journal fit is defensible, although no workflow can
guarantee editorial acceptance.

### Are there remaining submission blockers?

There are no computational or manuscript-architecture blockers. Before journal
upload, the author must confirm correspondence details, funding, the
competing-interest wording, the exact Codex model/version, and the Step 7
commit/release/archival identifier. These are author-controlled administrative
items and do not require revising the Step 6 calculations.

## Decision

**MOVE TO STEP 7.**

Step 6 is complete and passes its scientific, structural, build, visual,
licensing, restricted-source and release-artifact tests. The manuscript is a
submission-ready reproducibility draft, not a promise of acceptance and not yet
authorized for journal upload. Step 7 should create an intentional branch and
commit, push it, and open the draft pull request. Journal submission must wait
for the author-controlled checklist items and a final human scientific review.
