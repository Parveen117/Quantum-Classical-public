# Public Release Checklist

The repository must remain private until every **required pre-public** gate below is closed. A dramatic README is not a substitute for reproducibility, although the internet continues to conduct that experiment daily.

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

- [x] Three selected passing hardware runs from distinct backends are reviewed in local intake staging.
- [x] Run identifiers are assessed for privacy and approved for public provenance.
- [x] Raw result files are immutable and SHA-256 hashed in the staged intake.
- [x] Each selected staged run includes `results.json`, `certificate.json`, `summary.md`, and `manifest.json`.
- [x] The staged cross-backend replication includes a certificate, summary, and manifest.
- [x] Duplicate job identifiers and duplicate raw-result hashes are rejected by the evaluator.
- [x] Certificate creation dates are stated for all selected runs; authoritative queue/runtime fields were not retained and this limitation is documented.
- [x] Negative controls and reduced-model comparisons are included in the benchmark design.
- [x] The staged selected evidence contains no detected credentials, account identifiers, local paths, or private notes.
- [x] Approved evidence is promoted into tracked release paths and reverified from a clean checkout.

## 5. Reproducibility

- [x] One command verifies public source syntax, schemas, scans, and executable self-tests offline.
- [x] One command verifies every tracked evidence manifest and certificate after promotion.
- [x] One command reproduces release summary tables from tracked evidence.
- [x] Deterministic positive and adversarial fixtures are included in evaluator self-tests.
- [x] Machine-generated outputs identify the software version and private-source provenance.
- [x] Hardware-access requirements and execution commands are documented.
- [x] Queue/runtime variability and the absence of authoritative duration fields are documented without inferring duration from directory or certificate timestamps.

## 6. Intellectual property and licensing

- [x] Patent notice exists.
- [x] Controlled public-inspection licence exists.
- [x] Public/private release boundary exists.
- [x] Final release contents are checked against active patent filings and unpublished claim strategy by the repository owner; decision recorded in issue #3.
- [x] Current public branch contains no fabrication, cryogenic-control, examiner-response, or unpublished laboratory packet.
- [x] Technical selected-file boundary limits evidence to results, certificates, summaries, and manifests.
- [x] The public licence identifies Monty Dabas only and excludes the private legal name.

## 7. Repository hygiene

- [x] Citation metadata and package metadata use the publication identity Monty Dabas with ORCID `0009-0005-6948-209X`.
- [x] `.gitignore` covers credentials, environments, notebooks, caches, generated runs, and local configuration.
- [x] Local-path and hardcoded-secret scan passes on the locally reconstructed public tree.
- [x] CI secret/path scan passes on the GitHub branch.
- [x] Personal-information and sensitive-field scan is clean for staged selected evidence.
- [x] Large-file and duplicate-file audit is clean after tracked evidence promotion.
- [x] Repository-local Markdown links and heading anchors pass the offline checker in CI.
- [x] Proposed repository description and topics match the bounded claim and are approved in issue #3.
- [ ] Apply the approved description and topics in GitHub repository settings.

## 8. Release

- [x] Freeze the approved release-candidate content on the PR head.
- [x] Create release notes summarizing included evidence and exclusions.
- [x] Complete final human legal/IP review.
- [ ] Mark PR #1 ready and merge into `main` while the repository remains private.
- [ ] Re-run verification and CI on the exact merged `main` commit.
- [ ] Perform the final repository visibility inspection.
- [ ] Change the repository to public.
- [ ] Enable `Parveen117/Quantum-Classical-public` in Zenodo before publishing the GitHub release.
- [ ] Create and publish the `v0.1.0-rc1` GitHub prerelease from the exact verified `main` commit.
- [ ] Verify the Zenodo archive, creator, ORCID, version, files, and DOI.
- [ ] Record the final tag, commit SHA, evidence-manifest hash, and Zenodo DOI in a post-release metadata update.
