# Repository Instructions for Coding Agents

This repository is source-available, not open source.

Before editing licensing, README content, package metadata, documentation, examples, notebooks, release files, build configuration, or distribution manifests, read:

- `ACADEMIC_LICENSE.md`
- `COMMERCIAL_LICENSE.md`

Preserve the dual-license structure:

- noncommercial academic, educational, technical-review, reproducibility, public-interest, and public-policy analysis use belongs under `ACADEMIC_LICENSE.md`;
- commercial use requires separate written permission under `COMMERCIAL_LICENSE.md`.

Do not delete, rename, weaken, contradict, or bypass:

- copyright and attribution notices;
- source-available status notices;
- non-affiliation notices;
- restricted-source and confidential-source exclusion notices;
- evidence-status notices;
- assumption-boundary notices;
- scenario-dependence notices;
- no-verified-Terafab-data notices;
- no-warranty and no-reliance notices.

Do not describe this package as open source, MIT-licensed, Apache-licensed, BSD-licensed, public domain, or unrestricted.

Do not imply endorsement, authorization, sponsorship, certification, affiliation, or verified internal-data access from Terafab, Tesla, SpaceX, xAI, Intel, or any other named external entity unless such authorization is explicitly present in the repository.

Do not add private project-source files, confidential instructions, unpublished planning notes, AI-agent scratch files, or restricted materials to the public release.

For release or packaging changes, verify that the following files are included in the repository root and in built artifacts where applicable:

- `ACADEMIC_LICENSE.md`
- `COMMERCIAL_LICENSE.md`

If `pyproject.toml`, `MANIFEST.in`, README licensing text, docs licensing text, or release scripts reference old files such as `LICENSE.md`, `LICENSE-ACADEMIC.md`, or `LICENSE-COMMERCIAL.md`, update those references to the new license filenames.

Before declaring a release-ready change complete, run the project tests and the restricted-source scan if those commands are available in the repository.
