# Step 7 stress-test report

Date: 2026-08-01

Scope: final repository integration, staged-snapshot reproducibility, software
regression, frozen-evidence integrity, publication regeneration, manuscript
compilation, release packaging, licensing, and restricted-source exclusion.

## Release-gate results

| Test | Result | Evidence |
|---|---:|---|
| Staged diff integrity | Pass after hygiene correction | `git diff --cached --check` reports no whitespace errors. |
| Full repository regression | Pass | 112 tests passed in the working tree. |
| Clean staged snapshot regression | Pass | The same 112 tests passed after exporting only the staged Git tree to a new directory. |
| Frozen evidence | Pass | 26 sources, 22 parameters and 5 snapshots validate without live retrieval. |
| Publication regeneration | Pass | All 337 trajectories and 20,720 gate rows were regenerated from tracked inputs. |
| Manuscript traceability | Pass | 15 principal quantitative claims recompute from the generated bundle. |
| Manuscript structure | Pass | 232-word abstract, 7 keywords, 5 highlights, 10 figures, 6 tables and 17 citations. |
| LaTeX package | Pass | Main manuscript, supplement and cover letter compile from the clean staged snapshot. |
| Source distribution | Pass | Study contracts, evidence, notebook and manuscript sources are included; generated outputs are pruned. |
| Wheel distribution | Pass | Runtime packages, both CLI entry points and legal files are present. |
| Restricted-source scan | Pass | No prohibited private or unpublished source filename is present. |
| Generated-output guard | Pass | Publication bundles, compiled PDFs, build directories and caches remain ignored. |
| Root integration | Pass | README, repository map, install commands, scientific boundary and changelog expose the study. |

## Defects found and corrected

1. The root README still described only the two pre-existing overlays. It now
   exposes `terafab_energy_security`, the study layout, installation and
   reproduction commands, and the non-overclaiming boundary.
2. The changelog did not identify the new research surface or release guards.
   An unreleased entry now records the overlay, study, manuscript workflow and
   artifact verification.
3. The first staged-diff audit found trailing whitespace and extra blank lines
   in new study records. Those mechanical defects were normalized before the
   clean-snapshot gate.

## Clean-snapshot method

The complete intended change set was staged, converted to a Git tree with
`git write-tree`, exported into a new temporary directory with `git archive`,
and tested there. The snapshot contained no ignored publication output, local
PDF, build directory, Python cache or restricted source. From that snapshot the
workflow regenerated the final publication bundle, revalidated the manuscript,
compiled all LaTeX documents, built the source distribution and wheel, and
verified both archives.

## Decision

**CREATE THE DRAFT PULL REQUEST.**

Step 7 passes. There is no computational, scientific-contract, manuscript-build,
licensing, packaging or repository-hygiene defect that warrants revising Step 6.
The branch and pull request should remain a review surface: journal submission
still requires author-controlled correspondence, funding and competing-interest
details, the exact Codex model/version, a release/archival identifier, and final
human source and scientific review.
