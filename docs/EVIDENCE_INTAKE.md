# Controlled Evidence Intake

## Status entering this phase

The private campaign has reported three valid runs on three distinct IBM backends, no duplicate job identifiers or raw-result hashes, and a passing `CROSS_BACKEND_REPLICATION` certificate with cross-run stability.

This phase does not publish or commit those files. It creates a local, git-ignored staging tree and an audit report.

## Jupyter intake cell

Run from the private `quantum-classical-provisional` working directory after updating the public release-candidate checkout:

```python
from pathlib import Path
import json
import subprocess
import sys

PRIVATE_REPO = Path.cwd().resolve()
RUNS_ROOT = PRIVATE_REPO / "multi_ledger_operator_memory_v1" / "runs"
REPLICATION_ROOT = PRIVATE_REPO / "multi_ledger_operator_memory_v1" / "replication"
PUBLIC_REPO = PRIVATE_REPO.parent / "Quantum-Classical-public"
STAGING_ROOT = PUBLIC_REPO / "evidence" / "intake_staging"

subprocess.run(
    ["git", "-C", str(PUBLIC_REPO), "pull", "--ff-only", "origin", "agent/public-release-foundation"],
    check=True,
)

subprocess.run(
    [
        sys.executable,
        str(PUBLIC_REPO / "tools" / "stage_evidence_intake.py"),
        "--runs-root",
        str(RUNS_ROOT),
        "--replication-root",
        str(REPLICATION_ROOT),
        "--staging-root",
        str(STAGING_ROOT),
        "--expected-runs",
        "3",
    ],
    cwd=PUBLIC_REPO,
    check=True,
)

audit = json.loads((STAGING_ROOT / "intake_audit.json").read_text(encoding="utf-8"))
print(json.dumps({
    "classification": audit["classification"],
    "run_count": audit["run_count"],
    "passing_run_count": audit["passing_run_count"],
    "backend_count": audit["backend_count"],
    "backends": audit["backends"],
    "cross_run_stability": audit["cross_run_stability"]["pass"],
    "content_scan": audit["content_scan"]["pass"],
    "job_identifier_publication_review": audit["job_identifier_publication_review"],
}, indent=2))
```

## Required staging result

```text
classification = CROSS_BACKEND_REPLICATION
run_count = 3
passing_run_count = 3
backend_count = 3
cross_run_stability = true
content_scan = true
job_identifier_publication_review = PENDING_FINAL_APPROVAL
```

The pending job-identifier decision is intentional. IBM job identifiers may help reproducibility, but they are not promoted merely because the rest of the evidence passed.

## What the tool verifies

- recomputes the campaign with the public evaluator;
- requires three valid passing runs on three distinct backends;
- rejects duplicate job identifiers and duplicate result hashes;
- verifies every run and replication manifest;
- confirms copied files retain their exact SHA-256 hashes;
- copies only `results.json`, `certificate.json`, `summary.md`, `manifest.json`, `replication_certificate.json`, `replication_summary.md`, and `replication_manifest.json`;
- rejects local user paths, workstation-folder references, email addresses, private keys, and populated credential/account fields;
- writes `intake_audit.json` and `intake_audit.md`.

## Promotion boundary

The staging directory is ignored by Git. Do not force-add it. Promotion into the tracked `evidence/selected_runs` and `evidence/replication` directories occurs only after final review of:

- job-identifier publication necessity;
- execution and calibration metadata;
- patent and unpublished-claim boundaries;
- scientific wording and exclusions;
- exact public file list and aggregate release notes.
