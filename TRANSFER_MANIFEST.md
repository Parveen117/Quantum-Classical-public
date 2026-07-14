# Provisional-to-Public Transfer Manifest

Source repository: `Parveen117/quantum-classical-provisional`  
Destination repository: `Parveen117/Quantum-Classical`

This manifest controls what may be transported. A file is not public-release material merely because it exists, runs once, or has an impressive name.

## Release unit A: framework and scientific boundaries

| Source | Public destination | Status | Required treatment |
|---|---|---|---|
| `README.md` | `docs/FRAMEWORK.md` and bounded material in root `README.md` | In progress | Extract only state, seam, residue, closure, evidence levels, reviewer tests, and falsification conditions. Remove provisional roadmap and unrelated claims. |
| `MULTI_LEDGER_OPERATOR_MEMORY_TEST.md` | `docs/MULTI_LEDGER_OPERATOR_MEMORY_TEST.md` | Approved for sanitised transfer | Preserve circuit purpose, controls, pass gates, classifications, and scientific boundary. |
| `MULTI_LEDGER_DEVICE_EVIDENCE_EXPORT_PROTOCOL.md` | `docs/EVIDENCE_FREEZE_PROTOCOL.md` | Hold | Rewrite as a public evidence-freeze protocol. Remove local device paths and device-repository operational instructions. |

## Release unit B: executable benchmark

| Source | Public destination | Status | Required treatment |
|---|---|---|---|
| `run_multi_ledger_operator_memory_test.py` | `src/run_multi_ledger_operator_memory_test.py` | Approved after sanitation | Remove local Jupyter path. Retain environment-variable authentication, self-test, controls, certificates, and manifests. Verify against current Qiskit APIs. |
| `evaluate_multi_ledger_replication.py` | `src/evaluate_multi_ledger_replication.py` | Approved after sanitation | Remove local path. Retain strict manifest checks, metric gates, duplicate rejection, cross-run stability, self-test, and certificate generation. |
| `export_multi_ledger_device_evidence.py` | Not in first release | Excluded | Device-facing transport is outside the initial public scope. A later generic evidence freezer may be derived without device paths or device claims. |

## Release unit C: schemas and verification

The following public files must be created or transported only after validation:

- `schemas/run_certificate.schema.json`
- `schemas/run_manifest.schema.json`
- `schemas/replication_certificate.schema.json`
- `schemas/replication_manifest.schema.json`
- `tests/test_public_self_tests.py` or an equivalent one-command test runner
- `requirements.txt` or `pyproject.toml` with tested dependency bounds

Status: **pending construction and clean-environment testing**.

## Release unit D: selected evidence

Expected private source structure:

```text
multi_ledger_operator_memory_v1/
  runs/<UTC_TIMESTAMP>/
    results.json
    certificate.json
    summary.md
    manifest.json
  replication/<UTC_TIMESTAMP>/
    replication_certificate.json
    replication_summary.md
    replication_manifest.json
```

Planned public destination:

```text
evidence/
  selected_runs/<PUBLIC_RUN_ID>/
  replication/<PUBLIC_REPLICATION_ID>/
  provenance/source_commit.json
```

Evidence status: **not yet approved for transfer**.

Before transport, each selected bundle must pass:

1. manifest and SHA-256 verification;
2. distinct-backend and distinct-job checks;
3. duplicate raw-results rejection;
4. credential and personal-information scan;
5. local-path scan;
6. patent and unpublished-architecture review;
7. claim-scope review;
8. independent offline regeneration of the replication certificate.

Public identifiers may be pseudonymous when the raw IBM job identifier is unnecessary for reproducibility. Any transformation must be documented while preserving an internal provenance map in the private repository.

## Explicit exclusions from the first release

Do not transport:

- IBM API tokens, saved-account files, service configuration, or credentials;
- local Windows paths or usernames;
- device-repository destinations or hardware handover paths;
- transistor, material, fabrication, cryogenic-control, or laboratory implementation material;
- patent specifications, claim charts, examiner support, or unpublished filing strategy;
- unrelated Bell, bridge, thermodynamic, AI, cryptography, atomic, or device experiments;
- generated caches, notebook checkpoints, virtual environments, raw debug logs, or failed exploratory runs;
- files with unresolved imports or development-only dependencies;
- claims that are not linked to released evidence and a falsification condition.

## Provenance record required for every transported file

For each file added from the provisional repository, record:

```text
private source path
private source commit SHA
private source blob SHA or SHA-256
public destination path
sanitisation or modification summary
public file SHA-256
review status
```

The final machine-readable version of this record will be stored as `evidence/provenance/transport_manifest.json` before release.
