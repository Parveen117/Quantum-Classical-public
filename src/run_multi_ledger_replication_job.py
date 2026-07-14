#!/usr/bin/env python3
"""Submit one independent benchmark job on an unused IBM backend.

The launcher inspects local evidence bundles, excludes backends already used by
completed runs, submits exactly one new benchmark job, and then invokes the
offline replication evaluator. It never accepts or stores an IBM token.

Run ``--self-test`` without IBM credentials to test backend-selection logic.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Iterable, Sequence

PUBLIC_VERSION = "0.1.0-rc1"
PRIVATE_SOURCE_REPOSITORY = "Parveen117/quantum-classical-provisional"
PRIVATE_SOURCE_COMMIT = "136ac54b4093d96f57ab0fd19506d002b3b9068a"
PRIVATE_SOURCE_BLOB_SHA = "cc3159662e0810b80de269bab35cf52de2ccf411"

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RUNS_ROOTS = (
    REPO_ROOT / "evidence" / "selected_runs",
    REPO_ROOT / "evidence" / "generated" / "runs",
)
BENCHMARK = REPO_ROOT / "src" / "run_multi_ledger_operator_memory_test.py"
EVALUATOR = REPO_ROOT / "src" / "evaluate_multi_ledger_replication.py"
DEFAULT_CHANNEL = "ibm_quantum_platform"


def load_used_backends(runs_roots: Iterable[Path] = DEFAULT_RUNS_ROOTS) -> set[str]:
    used: set[str] = set()
    for root in runs_roots:
        if not root.exists():
            continue
        for certificate_path in sorted(root.glob("*/certificate.json")):
            try:
                certificate = json.loads(certificate_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            backend = str(certificate.get("backend", "")).strip()
            job_id = str(certificate.get("job_id", "")).strip()
            if backend and job_id:
                used.add(backend)
    return used


def backend_qubits(backend: Any) -> int:
    value = getattr(backend, "num_qubits", None)
    if isinstance(value, int):
        return value
    configuration = getattr(backend, "configuration", None)
    if callable(configuration):
        try:
            return int(getattr(configuration(), "n_qubits", 0) or 0)
        except Exception:
            return 0
    return 0


def backend_pending_jobs(backend: Any) -> int:
    try:
        return int(getattr(backend.status(), "pending_jobs", 10**9) or 0)
    except Exception:
        return 10**9


def backend_name(backend: Any) -> str:
    name = getattr(backend, "name", "")
    return str(name() if callable(name) else name).strip()


def select_backend(
    backends: Iterable[Any],
    *,
    used_backends: set[str],
    requested_backend: str = "",
    allow_used_backend: bool = False,
) -> Any:
    candidates: list[Any] = []
    for backend in backends:
        name = backend_name(backend)
        if not name:
            continue
        if requested_backend and name != requested_backend:
            continue
        if backend_qubits(backend) < 7:
            continue
        if not allow_used_backend and name in used_backends:
            continue
        candidates.append(backend)

    if requested_backend and not candidates:
        if requested_backend in used_backends and not allow_used_backend:
            raise RuntimeError(
                f"{requested_backend} already has local evidence. Choose another "
                "backend or explicitly allow same-backend replication."
            )
        raise RuntimeError(
            f"Requested backend {requested_backend!r} is unavailable, "
            "non-operational, or has fewer than seven qubits."
        )
    if not candidates:
        if used_backends and not allow_used_backend:
            raise RuntimeError(
                "No unused operational backend with at least seven qubits is "
                "currently available. Retry later rather than silently reusing evidence."
            )
        raise RuntimeError("No operational backend with at least seven qubits is available.")
    return min(candidates, key=backend_pending_jobs)


def run_checked(command: Sequence[str], *, env: dict[str, str] | None = None) -> None:
    completed = subprocess.run(list(command), cwd=REPO_ROOT, env=env, text=True)
    if completed.returncode != 0:
        raise RuntimeError(
            f"Command failed with return code {completed.returncode}: {' '.join(command)}"
        )


def submit_replication(
    *,
    requested_backend: str = "",
    allow_used_backend: bool = False,
) -> str:
    if not BENCHMARK.is_file() or not EVALUATOR.is_file():
        raise FileNotFoundError("Public benchmark or evaluator is missing.")
    try:
        from qiskit_ibm_runtime import QiskitRuntimeService
    except ImportError as exc:
        raise RuntimeError(
            "Install the declared hardware dependencies from pyproject.toml first."
        ) from exc

    channel = os.getenv("IBM_QUANTUM_CHANNEL", DEFAULT_CHANNEL).strip()
    instance = os.getenv("IBM_QUANTUM_INSTANCE", "").strip() or None
    used = load_used_backends()
    service_kwargs: dict[str, Any] = {"channel": channel}
    if instance:
        service_kwargs["instance"] = instance
    service = QiskitRuntimeService(**service_kwargs)
    selected = select_backend(
        service.backends(simulator=False, operational=True),
        used_backends=used,
        requested_backend=requested_backend,
        allow_used_backend=allow_used_backend,
    )
    selected_name = backend_name(selected)
    print("Previously used backends:", sorted(used) or ["none"])
    print("Selected replication backend:", selected_name)
    print("Submitting exactly one independent benchmark job.")

    child_env = os.environ.copy()
    child_env["IBM_QUANTUM_BACKEND"] = selected_name
    run_checked([sys.executable, str(BENCHMARK)], env=child_env)
    run_checked([sys.executable, str(EVALUATOR), "--no-write"], env=child_env)
    return selected_name


class _FakeStatus:
    def __init__(self, pending_jobs: int):
        self.pending_jobs = pending_jobs


class _FakeBackend:
    def __init__(self, name: str, qubits: int, pending_jobs: int):
        self.name = name
        self.num_qubits = qubits
        self._pending_jobs = pending_jobs

    def status(self) -> _FakeStatus:
        return _FakeStatus(self._pending_jobs)


def self_test() -> None:
    backends = [
        _FakeBackend("used_backend", 127, 0),
        _FakeBackend("small_backend", 5, 0),
        _FakeBackend("fresh_busy", 127, 12),
        _FakeBackend("fresh_quiet", 127, 2),
    ]
    selected = select_backend(backends, used_backends={"used_backend"})
    assert backend_name(selected) == "fresh_quiet"
    requested = select_backend(
        backends,
        used_backends={"used_backend"},
        requested_backend="fresh_busy",
    )
    assert backend_name(requested) == "fresh_busy"
    try:
        select_backend(
            backends,
            used_backends={"used_backend"},
            requested_backend="used_backend",
        )
    except RuntimeError:
        pass
    else:
        raise AssertionError("A previously used backend was not rejected.")
    print(
        "Self-test passed: used and undersized backends are rejected, and the "
        "least-busy unused eligible backend is selected."
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--backend", default="")
    parser.add_argument("--allow-used-backend", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args(argv)
    if args.self_test:
        self_test()
        return 0
    submit_replication(
        requested_backend=args.backend.strip(),
        allow_used_backend=args.allow_used_backend,
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        raise SystemExit(130)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
