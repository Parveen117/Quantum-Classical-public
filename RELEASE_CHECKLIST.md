# Public Release Checklist

The repository must remain private until every **required** gate below is closed. A dramatic README is not a substitute for reproducibility, although the internet continues to conduct that experiment daily.

## 1. Scope and claims

- [x] First release target is limited to the Multi-Ledger Operator-Memory Benchmark v1.
- [x] Representation evidence is separated from physical device, material, thermodynamic, and universal-law claims.
- [ ] `docs/CLAIM_SCOPE.md` maps every public claim to evidence, code, tests, limitations, and falsification conditions.
- [ ] All language has been checked for accidental overclaiming.

## 2. Source transport

- [ ] Freeze the selected source commit from `Parveen117/quantum-classical-provisional`.
- [ ] Copy only approved files listed in `TRANSFER_MANIFEST.md`.
- [ ] Remove local filesystem paths and development-only comments.
- [ ] Remove unrelated provisional experiments and incomplete imports.
- [ ] Preserve source provenance and original file hashes.
- [ ] Record any public-release modifications and their new hashes.

## 3. Code and environment

- [ ] Public benchmark runner passes `--self-test` in a clean environment.
- [ ] Offline replication evaluator passes `--self-test` in a clean environment.
- [ ] Python version is declared.
- [ ] Dependencies are pinned or bounded and installation is tested.
- [ ] A single non-credentialed command runs all public self-tests.
- [ ] IBM execution instructions use environment variables and never expose tokens.
- [ ] Failure paths return nonzero process codes and do not label runtime failures as scientific negatives.

## 4. Evidence

- [ ] At least two selected passing hardware runs from distinct backends are reviewed.
- [ ] Run identifiers are assessed for privacy and publication necessity.
- [ ] Raw result files are immutable and SHA-256 hashed.
- [ ] Each run includes `results.json`, `certificate.json`, `summary.md`, and `manifest.json`.
- [ ] Cross-backend replication includes a certificate, summary, and manifest.
- [ ] Duplicate job identifiers and duplicate raw-result hashes are rejected.
- [ ] Calibration and execution dates are stated where available.
- [ ] Negative controls and reduced-model comparisons are included.
- [ ] No evidence file contains credentials, account identifiers, local paths, or private notes.

## 5. Reproducibility

- [ ] One command verifies every selected manifest and certificate offline.
- [ ] One command reproduces summary tables from selected evidence.
- [ ] Deterministic fixtures are included for CI self-tests.
- [ ] Machine-generated outputs identify the software version and source commit.
- [ ] Expected runtimes and hardware-access requirements are documented.

## 6. Intellectual property and licensing

- [x] Patent notice exists.
- [x] Controlled public-inspection licence exists.
- [x] Public/private release boundary exists.
- [ ] Final release contents are checked against active patent filings and unpublished claim strategy.
- [ ] No fabrication, cryogenic-control, device-architecture, examiner-response, or unpublished laboratory material is included unintentionally.

## 7. Repository hygiene

- [x] Citation metadata scaffold exists.
- [ ] `.gitignore` covers credentials, environments, notebooks, caches, generated runs, and local configuration.
- [ ] Secret scan is clean.
- [ ] Personal-information scan is clean.
- [ ] Large-file and duplicate-file audit is clean.
- [ ] Links and Markdown render correctly.
- [ ] Repository description and topics match the bounded claim.

## 8. Release

- [ ] Freeze release candidate commit.
- [ ] Create release notes summarizing included evidence and exclusions.
- [ ] Tag `v0.1.0-rc1` only after all required gates pass.
- [ ] Re-run offline verification from the tagged commit.
- [ ] Record the tag, commit SHA, and evidence-manifest hashes in the release notes.
- [ ] Change repository visibility only after the final inspection.
