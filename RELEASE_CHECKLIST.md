# Public Release Checklist

The repository must remain private until every **required** gate below is closed. A dramatic README is not a substitute for reproducibility, although the internet continues to conduct that experiment daily.

## 1. Scope and claims

- [x] First release target is limited to the Multi-Ledger Operator-Memory Benchmark v1.
- [x] Representation evidence is separated from physical device, material, thermodynamic, and universal-law claims.
- [x] `docs/CLAIM_SCOPE.md` maps every public claim to evidence, code, tests, limitations, and falsification conditions.
- [x] Current public-branch language has been checked for accidental overclaiming.

## 2. Source transport

- [x] Freeze the selected source commits from `Parveen117/quantum-classical-provisional`.
- [x] Copy only approved files listed in `TRANSFER_MANIFEST.md`.
- [x] Remove local filesystem paths and development-only comments from transported executables.
- [x] Remove unrelated provisional experiments and incomplete imports from the first release scope.
- [x] Preserve source provenance and original file blob hashes.
- [x] Record public-release modifications and new Git/SHA-256 hashes.

## 3. Code and environment

- [x] Public benchmark runner passes pure offline `--self-test` in a clean environment.
- [x] Offline replication evaluator passes `--self-test` in a clean environment.
- [x] Python version is declared.
- [x] Declared Qiskit dependency installation and full circuit construction pass in CI.
- [x] A single non-credentialed command runs all public self-tests.
- [x] IBM execution instructions use environment variables or SDK account discovery and never expose tokens.
- [x] Failure paths return nonzero process codes and do not label runtime failures as scientific negatives.

## 4. Evidence

- [ ] At least two selected passing hardware runs from distinct backends are reviewed.
- [ ] Run identifiers are assessed for privacy and publication necessity.
- [ ] Raw result files are immutable and SHA-256 hashed.
- [ ] Each selected run includes `results.json`, `certificate.json`, `summary.md`, and `manifest.json`.
- [ ] Cross-backend replication includes a certificate, summary, and manifest.
- [x] Duplicate job identifiers and duplicate raw-result hashes are rejected by the evaluator.
- [ ] Calibration and execution dates are stated where available.
- [x] Negative controls and reduced-model comparisons are included in the benchmark design.
- [ ] No selected evidence file contains credentials, account identifiers, local paths, or private notes.

## 5. Reproducibility

- [x] One command verifies public source syntax, schemas, scans, and executable self-tests offline.
- [ ] One command verifies every selected evidence manifest and certificate after evidence intake.
- [ ] One command reproduces release summary tables from selected evidence.
- [x] Deterministic positive and adversarial fixtures are included in evaluator self-tests.
- [x] Machine-generated outputs identify the software version and private-source provenance.
- [x] Hardware-access requirements and execution commands are documented.
- [ ] Expected hardware runtimes and likely queue-dependent variability are documented from a release run.

## 6. Intellectual property and licensing

- [x] Patent notice exists.
- [x] Controlled public-inspection licence exists.
- [x] Public/private release boundary exists.
- [ ] Final release contents are checked against active patent filings and unpublished claim strategy.
- [x] Current public branch contains no fabrication, cryogenic-control, examiner-response, or unpublished laboratory packet.

## 7. Repository hygiene

- [x] Citation metadata scaffold exists with Parveen attribution.
- [x] `.gitignore` covers credentials, environments, notebooks, caches, generated runs, and local configuration.
- [x] Local-path and hardcoded-secret scan passes on the locally reconstructed public tree.
- [x] CI secret/path scan passes on the GitHub branch.
- [ ] Personal-information scan is clean for selected evidence.
- [ ] Large-file and duplicate-file audit is clean after evidence intake.
- [ ] Links and Markdown render correctly.
- [ ] Repository description and topics match the bounded claim.

## 8. Release

- [ ] Freeze release candidate commit.
- [ ] Create release notes summarizing included evidence and exclusions.
- [ ] Tag `v0.1.0-rc1` only after all required gates pass.
- [ ] Re-run offline verification from the tagged commit.
- [ ] Record the tag, commit SHA, and evidence-manifest hashes in the release notes.
- [ ] Change repository visibility only after the final inspection.
