# Release Notes: `v0.1.0-rc1` Draft

## Status

This document prepares the first bounded release candidate. The repository remains private, the pull request remains draft, and no release tag has been created.

- Evidence commit: `c9ea63775775f7e8aa2b5cb67bfa0da6b3902f89`
- Candidate name: `0.1.0-rc1`
- Public visibility: blocked pending final legal/IP review and final release inspection
- Authoritative private archive: `Parveen117/quantum-classical-provisional`

## Included technical scope

The candidate is limited to the Multi-Ledger Operator-Memory Benchmark v1 and the material required to inspect, reproduce, and falsify its bounded representation claim:

- benchmark and declared control circuits;
- fixed per-run and cross-run metric thresholds;
- deterministic positive and adversarial self-tests;
- three selected IBM Quantum hardware result bundles;
- per-run certificates, summaries, and SHA-256 manifests;
- a cross-backend replication certificate, summary, and manifest;
- source and evidence provenance records;
- offline verification, promotion, and release-summary tooling.

## Selected hardware evidence

All selected jobs were executed on July 14, 2026, with 4,096 shots per circuit configuration and three transpiler seeds (`11`, `29`, and `47`) inside each independent hardware job. Transpiler-seed repeats are treated as within-job sampling and not as independent replications.

| Public run ID | Backend | IBM job identifier | Certificate created UTC | Classification | Raw-results SHA-256 |
|---|---|---|---|---|---|
| `20260714T113925Z` | `ibm_kingston` | `d9b1vvm6hjac73ff43gg` | `2026-07-14T11:40:41.867511+00:00` | `MULTI_LEDGER_OPERATOR_MEMORY_DECOMPOSITION` | `9525a9ff1ef4e8dd118153d4583e59f090c0be76966f8ed63e9ba363a25ce6c3` |
| `20260714T114146Z` | `ibm_fez` | `d9b212u6hjac73ff44j0` | `2026-07-14T11:43:03.699314+00:00` | `MULTI_LEDGER_OPERATOR_MEMORY_DECOMPOSITION` | `2940f2ce0a24a4bfb14a3a7042b4cfaad460ee13df22ae8a17db9d6f55e80b0a` |
| `20260714T120705Z` | `ibm_marrakesh` | `d9b2ct6g26ic73dfd8s0` | `2026-07-14T12:08:16.087545+00:00` | `MULTI_LEDGER_OPERATOR_MEMORY_DECOMPOSITION` | `9038b059703c5d460369c805ff7d108677afb82129e6761074e0260bd96e17e7` |

All six declared gates passed for every selected run:

1. hidden memory;
2. selective erase;
3. projection causal;
4. reset projection;
5. model comparison;
6. visible RK/KR equality.

## Campaign result

The strict offline evaluator produced:

```text
classification = CROSS_BACKEND_REPLICATION
run_count = 3
passing_run_count = 3
backend_count = 3
duplicate_job_ids = []
duplicate_result_hashes = []
cross_run_stability.pass = true
```

Cross-run statistics recorded in the evidence release manifest:

| Statistic | Value |
|---|---:|
| Full-readout mean | `0.9746907552083334` |
| Full-readout range | `0.015869140625` |
| Projection-erased readout mean | `0.0015462239583333335` |
| Projection-erased readout range | `0.0011393229166666665` |
| Control-ledger ceiling mean | `0.009006076388888888` |
| Control-ledger ceiling range | `0.004394531249999999` |
| Maximum visible RK/KR TVD | `0.012044270833333325` |
| Minimum reset-signature spread | `0.04280598958333326` |
| Maximum full multi-ledger MAE | `0.02916856582482192` |

## Evidence custody and file audit

The selected evidence was staged outside Git, re-evaluated, manifest-verified, scanned for sensitive content, promoted into tracked paths, committed, pushed to the private draft branch, and verified again through GitHub Actions.

The pre-commit file audit recorded:

- 17 tracked evidence files;
- 217,998 total bytes;
- largest file: `evidence/selected_runs/20260714T120705Z/results.json` at 53,809 bytes;
- no duplicate job identifiers;
- no duplicate raw-result hashes;
- no detected credentials, account identifiers, email addresses, private keys, local user paths, or workstation-folder references;
- the local intake audit and its absolute workstation path were excluded from Git history.

## Reproduction commands

Verify source, schemas, scans, self-tests, and tracked evidence:

```bash
python tools/verify_release.py
python tools/verify_tracked_evidence.py --expected-runs 3
```

Regenerate the release evidence tables from tracked certificates and the release manifest:

```bash
python tools/generate_release_summary.py --format markdown
python tools/generate_release_summary.py --format json
```

These commands perform no IBM hardware submission.

## Runtime and queue limitation

The selected public files preserve certificate creation times, backend names, job identifiers, circuit statistics, and result data. They do not preserve authoritative IBM queue-entry, execution-start, execution-end, or billing-duration fields. Queue delay and runtime therefore cannot be reconstructed reliably from this release candidate and must not be inferred from directory names or certificate creation timestamps. Future evidence campaigns should record those fields explicitly when the service exposes them safely.

## Scientific boundary

This release candidate may support a reproducible cross-backend quantum representation of decomposable operator-order memory under the declared circuits, controls, metrics, thresholds, and selected evidence.

It does not establish:

- a fabricated transistor or physical memory device;
- a material memory mechanism;
- thermodynamic entropy production;
- quantum computational advantage;
- fault-tolerant quantum computing;
- commercial readiness or safety;
- a universal recognition law or other new universal physical law.

## Deliberately excluded material

The candidate excludes:

- IBM credentials, account configuration, private instances, and tokens;
- local filesystem paths and machine-specific configuration;
- the complete private development history;
- unrelated provisional experiments and exploratory evidence;
- fabrication packets, device architecture, transistor design, material selection, cryogenic-control details, and laboratory handover documents;
- patent claims, claim charts, examiner strategy, continuation strategy, filing records, and unpublished claim strategy;
- private calibration records not necessary for the bounded representation claim.

Failed or excluded experiments remain part of the private research history and are not silently reclassified as passing evidence.

## Remaining gates before tagging or public visibility

- final comparison against active patent filings and unpublished claim strategy by the appropriate human reviewer or counsel;
- final internal-link and Markdown rendering audit;
- repository description and topic review against the bounded claim;
- freeze of the final release-candidate commit;
- creation of the `v0.1.0-rc1` tag only after all required gates pass;
- offline verification from the exact tagged commit;
- recording of the final tag, commit SHA, and evidence-manifest hash in these notes;
- final repository visibility review.

Until those gates are closed, the pull request remains draft and the repository remains private.
