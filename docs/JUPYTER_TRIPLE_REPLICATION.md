# Jupyter Triple-Replication Workflow

## Purpose

This workflow keeps raw IBM evidence in the private development repository while running the sanitised public release-candidate benchmark. Each invocation submits exactly one independent IBM Runtime job on a backend not already present in the campaign.

The target is three complete evidence bundles with distinct backend names, job identifiers, and raw-result hashes. The script does not silently reuse a backend.

## Starting assumption

Open Jupyter from the private `quantum-classical-provisional` working directory that already contains:

```text
multi_ledger_operator_memory_v1/runs/
```

That directory should include the existing passing `ibm_fez` evidence bundle.

## Cell 1: obtain or update the private public-release checkout

```python
from pathlib import Path
import subprocess

PRIVATE_REPO = Path.cwd().resolve()
RUNS_ROOT = PRIVATE_REPO / "multi_ledger_operator_memory_v1" / "runs"
PUBLIC_REPO = PRIVATE_REPO.parent / "Quantum-Classical-public"

assert RUNS_ROOT.exists(), f"Existing private runs directory not found: {RUNS_ROOT}"

if not PUBLIC_REPO.exists():
    subprocess.run(
        [
            "git",
            "clone",
            "--branch",
            "agent/public-release-foundation",
            "https://github.com/Parveen117/Quantum-Classical-public.git",
            str(PUBLIC_REPO),
        ],
        check=True,
    )
else:
    subprocess.run(["git", "-C", str(PUBLIC_REPO), "remote", "set-url", "origin", "https://github.com/Parveen117/Quantum-Classical-public.git"], check=True)
    subprocess.run(["git", "-C", str(PUBLIC_REPO), "fetch", "origin"], check=True)
    subprocess.run(["git", "-C", str(PUBLIC_REPO), "checkout", "agent/public-release-foundation"], check=True)
    subprocess.run(["git", "-C", str(PUBLIC_REPO), "pull", "--ff-only", "origin", "agent/public-release-foundation"], check=True)

print("Private evidence root:", RUNS_ROOT)
print("Public release checkout:", PUBLIC_REPO)
```

## Cell 2: verify the release candidate

```python
import subprocess
import sys

subprocess.run(
    [sys.executable, str(PUBLIC_REPO / "tools" / "verify_release.py")],
    cwd=PUBLIC_REPO,
    check=True,
)
```

## Cell 3: install the declared IBM environment when needed

```python
import importlib.metadata
import subprocess
import sys

required = {
    "qiskit": "2.5.0",
    "qiskit-ibm-runtime": "0.47.0",
}

installed = {}
for package in required:
    try:
        installed[package] = importlib.metadata.version(package)
    except importlib.metadata.PackageNotFoundError:
        installed[package] = None

if installed != required:
    subprocess.run(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "--upgrade",
            "qiskit==2.5.0",
            "qiskit-ibm-runtime==0.47.0",
        ],
        check=True,
    )

print("Declared IBM environment is installed.")
```

Restart the Jupyter kernel after installation if Python reports that the newly installed packages cannot be imported. Package managers and live kernels remain committed to making simple matters theatrical.

## Cell 4: dry-run backend selection

```python
import subprocess
import sys

subprocess.run(
    [
        sys.executable,
        str(PUBLIC_REPO / "src" / "run_replication_campaign_job.py"),
        "--runs-root",
        str(RUNS_ROOT),
        "--target-runs",
        "3",
        "--shots",
        "4096",
        "--dry-run",
    ],
    cwd=PUBLIC_REPO,
    check=True,
)
```

The output must show the existing completed-run count, previously used backends, and one unused selected backend. A dry run submits nothing.

## Cell 5: submit one independent replication job

```python
import subprocess
import sys

subprocess.run(
    [
        sys.executable,
        str(PUBLIC_REPO / "src" / "run_replication_campaign_job.py"),
        "--runs-root",
        str(RUNS_ROOT),
        "--target-runs",
        "3",
        "--shots",
        "4096",
    ],
    cwd=PUBLIC_REPO,
    check=True,
)
```

Run Cell 5 once. After the job completes, the script regenerates the replication evaluation. Run Cell 5 a second time only when the campaign still contains fewer than three complete bundles. The second invocation must select another unused backend.

## Cell 6: inspect the latest replication certificate

```python
from pathlib import Path
import json

replication_root = RUNS_ROOT.parent / "replication"
latest = max(
    (path for path in replication_root.iterdir() if path.is_dir()),
    key=lambda path: path.name,
)
certificate = json.loads((latest / "replication_certificate.json").read_text(encoding="utf-8"))

summary = {
    "classification": certificate["classification"],
    "run_count": certificate["run_count"],
    "passing_run_count": certificate["passing_run_count"],
    "backend_count": certificate["backend_count"],
    "backends": certificate["backends"],
    "duplicate_job_ids": certificate["duplicate_job_ids"],
    "duplicate_result_hashes": certificate["duplicate_result_hashes"],
    "cross_run_stability": certificate["cross_run_stability"],
}
summary
```

## Required publication result

The evidence is ready for public intake only when the latest certificate reports:

```text
classification = CROSS_BACKEND_REPLICATION
run_count >= 3
passing_run_count >= 3
backend_count >= 3
duplicate_job_ids = []
duplicate_result_hashes = []
cross_run_stability.pass = true
```

A completed IBM job that fails a scientific gate remains valid negative evidence. It must not be relabelled as a software failure or quietly removed from the private research history.

## Safety boundary

Do not paste IBM tokens into notebook cells, commit notebook outputs containing credentials, or copy the complete private runs directory into the public repository. Selected evidence is transported only after hash, privacy, provenance, scientific-scope, and patent-boundary review.
