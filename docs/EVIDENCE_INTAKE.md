# Controlled Evidence Intake and Promotion

## Status entering this phase

The private campaign has reported three valid runs on three distinct IBM backends, no duplicate job identifiers or raw-result hashes, and a passing `CROSS_BACKEND_REPLICATION` certificate with cross-run stability.

The intake stage creates a local, git-ignored evidence tree and audit. The promotion stage re-verifies that tree and copies only approved evidence files into tracked paths. Neither tool commits, pushes, merges, tags, or changes repository visibility.

## Intake result required before promotion

```text
classification = CROSS_BACKEND_REPLICATION
run_count = 3
passing_run_count = 3
backend_count = 3
cross_run_stability = true
content_scan = true
job_identifier_publication_review = PENDING_FINAL_APPROVAL
```

The completed intake reported this result for `ibm_fez`, `ibm_kingston`, and `ibm_marrakesh`.

## Publication decisions

IBM job identifiers are retained because they distinguish independent IBM Runtime executions and are not authentication credentials. Their use is limited to evidence provenance.

The technical selected-file boundary is limited to:

```text
selected_runs/<PUBLIC_RUN_ID>/
  results.json
  certificate.json
  summary.md
  manifest.json

replication/<PUBLIC_REPLICATION_ID>/
  replication_certificate.json
  replication_summary.md
  replication_manifest.json
```

The local `intake_audit.json` and `intake_audit.md` are not promoted because the audit can contain a workstation staging path.

Technical promotion is not a legal patent opinion. Final legal/IP review remains required before public visibility.

## Jupyter promotion cell

Run from the private `quantum-classical-provisional` working directory after pulling the latest public release-candidate branch:

```python
from pathlib import Path
import json
import subprocess
import sys

PRIVATE_REPO = Path.cwd().resolve()
PUBLIC_REPO = PRIVATE_REPO.parent / "Quantum-Classical-public"
STAGING_ROOT = PUBLIC_REPO / "evidence" / "intake_staging"
EVIDENCE_ROOT = PUBLIC_REPO / "evidence"

subprocess.run(
    [
        "git", "-C", str(PUBLIC_REPO),
        "pull", "--ff-only", "origin", "agent/public-release-foundation",
    ],
    check=True,
)

result = subprocess.run(
    [
        sys.executable,
        str(PUBLIC_REPO / "tools" / "promote_evidence_release.py"),
        "--staging-root", str(STAGING_ROOT),
        "--evidence-root", str(EVIDENCE_ROOT),
        "--expected-runs", "3",
        "--approve-job-identifiers",
        "--approve-selected-file-boundary",
    ],
    cwd=PUBLIC_REPO,
    text=True,
    capture_output=True,
)

print(result.stdout)
if result.stderr:
    print(result.stderr)
if result.returncode != 0:
    raise RuntimeError("Evidence promotion failed. Do not stage or commit files.")

status = subprocess.run(
    ["git", "-C", str(PUBLIC_REPO), "status", "--short"],
    text=True,
    capture_output=True,
    check=True,
)
print("\nGIT STATUS")
print(status.stdout)
```

## Required promotion result

```text
classification = CROSS_BACKEND_REPLICATION
run_count = 3
passing_run_count = 3
backend_count = 3
cross_run_stability = true
job_identifier_publication = APPROVED_FOR_PUBLIC_PROVENANCE
selected_file_boundary = TECHNICAL_REVIEW_APPROVED
legal_ip_review = PENDING_BEFORE_PUBLIC_VISIBILITY
local_intake_audit_committed = false
```

The new tracked files should appear only under:

```text
evidence/selected_runs/
evidence/replication/
evidence/provenance/evidence_release_manifest.json
evidence/EVIDENCE_INDEX.md
```

`evidence/intake_staging/` must not appear in `git status` because it remains ignored.

## What promotion re-verifies

- intake audit schema and release-candidate version;
- three valid passing runs on three distinct backends;
- no duplicate job identifiers or raw-result hashes;
- passing cross-run stability;
- every staged manifest and SHA-256 hash;
- exact agreement between staged files and intake audit;
- sensitive-content scan before and after copying;
- campaign reevaluation from the promoted copy;
- exclusion of the local intake audit;
- generation of a public evidence release manifest and evidence index.

## Remaining gates after local promotion

- inspect `git diff --stat` and the generated evidence index;
- verify the exact files from a clean checkout;
- reproduce the campaign classification using tracked evidence;
- complete final legal/IP review;
- create release notes and freeze the release-candidate commit;
- keep the repository private until every required release gate is closed.
