#!/usr/bin/env python3
"""Submit one independent IBM replication job and re-evaluate the campaign.

The command is intentionally one-job-at-a-time. It reads existing evidence
bundles from a private runs directory, excludes previously used backends,
submits the unchanged public benchmark once, and regenerates the replication
certificate. Re-run the same command until the target number of runs is reached.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Iterable, Sequence

REPO_ROOT = Path(__file__).resolve().parents[1]
BENCHMARK = REPO_ROOT / "src" / "run_multi_ledger_operator_memory_test.py"
EVALUATOR = REPO_ROOT / "src" / "evaluate_multi_ledger_replication.py"
DEFAULT_TARGET_RUNS = 3
DEFAULT_SHOTS = 4096
DEFAULT_CHANNEL = "ibm_quantum_platform"


def load_completed_runs(runs_root: Path) -> list[dict[str, str]]:
    completed: list[dict[str, str]] = []
    if not runs_root.exists():
        return completed
    for certificate_path in sorted(runs_root.glob("*/certificate.json")):
        try:
            certificate = json.loads(certificate_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if not isinstance(certificate, dict):
            continue
        backend = str(certificate.get("backend", "")).strip()
        job_id = str(certificate.get("job_id", "")).strip()
        classification = str(certificate.get("classification", "")).strip()
        raw_hash = str(certificate.get("raw_results_sha256", "")).strip()
        if backend and job_id and raw_hash:
            completed.append(
                {
                    "run_name": certificate_path.parent.name,
                    "backend": backend,
                    "job_id": job_id,
                    "classification": classification,
                    "raw_results_sha256": raw_hash,
                }
            )
    return completed


def backend_name(backend: Any) -> str:
    value = getattr(backend, "name", "")
    return str(value() if callable(value) else value).strip()


def backend_qubit_count(backend: Any) -> int:
    direct = getattr(backend, "num_qubits", None)
    if isinstance(direct, int):
        return direct
    configuration = getattr(backend, "configuration", None)
    if callable(configuration):
        return int(getattr(configuration(), "n_qubits", 0) or 0)
    return 0


def backend_pending_jobs(backend: Any) -> int:
    try:
        status = backend.status()
    except Exception:
        return 10**9
    return int(getattr(status, "pending_jobs", 10**9) or 0)


def select_backend(
    backends: Iterable[Any],
    *,
    used_backends: set[str],
    requested_backend: str | None,
) -> Any:
    candidates: list[Any] = []
    for backend in backends:
        name = backend_name(backend)
        if not name:
            continue
        if requested_backend and name != requested_backend:
            continue
        if backend_qubit_count(backend) < 7:
            continue
        if name in used_backends:
            continue
        candidates.append(backend)

    if requested_backend and not candidates:
        if requested_backend in used_backends:
            raise RuntimeError(
                f"Backend {requested_backend!r} already appears in the evidence campaign."
            )
        raise RuntimeError(
            f"Backend {requested_backend!r} is unavailable, non-operational, "
            "or has fewer than seven qubits."
        )
    if not candidates:
        raise RuntimeError(
            "No unused operational IBM backend with at least seven qubits is currently available."
        )
    return min(candidates, key=backend_pending_jobs)


def run_checked(command: Sequence[str]) -> None:
    print("$", " ".join(str(item) for item in command), flush=True)
    completed = subprocess.run(list(command), cwd=REPO_ROOT, text=True)
    if completed.returncode != 0:
        raise RuntimeError(
            f"Command failed with return code {completed.returncode}: "
            + " ".join(str(item) for item in command)
        )


def resolve_runs_root(value: Path | None) -> Path:
    if value is not None:
        return value.expanduser().resolve()
    env_value = os.getenv("QUANTUM_CLASSICAL_RUNS_ROOT", "").strip()
    if env_value:
        return Path(env_value).expanduser().resolve()
    raise RuntimeError(
        "A private evidence directory is required. Pass --runs-root or set "
        "QUANTUM_CLASSICAL_RUNS_ROOT. It should contain the existing ibm_fez run."
    )


def submit_one(args: argparse.Namespace) -> int:
    runs_root = resolve_runs_root(args.runs_root)
    replication_root = (
        args.replication_output_root.expanduser().resolve()
        if args.replication_output_root
        else runs_root.parent / "replication"
    )
    runs_root.mkdir(parents=True, exist_ok=True)
    replication_root.mkdir(parents=True, exist_ok=True)

    completed_before = load_completed_runs(runs_root)
    if len(completed_before) >= args.target_runs:
        print(
            f"Campaign already contains {len(completed_before)} complete runs; "
            f"target is {args.target_runs}. No job submitted."
        )
        run_checked(
            [
                sys.executable,
                str(EVALUATOR),
                "--runs-root",
                str(runs_root),
                "--output-root",
                str(replication_root),
            ]
        )
        return 0

    used_backends = {run["backend"] for run in completed_before}
    if not BENCHMARK.is_file() or not EVALUATOR.is_file():
        raise FileNotFoundError("Public benchmark or replication evaluator is missing.")

    run_checked([sys.executable, str(BENCHMARK), "--self-test"])
    run_checked([sys.executable, str(EVALUATOR), "--self-test"])

    try:
        from qiskit_ibm_runtime import QiskitRuntimeService
    except ImportError as exc:
        raise RuntimeError(
            "Install qiskit==2.5.0 and qiskit-ibm-runtime==0.47.0 before hardware execution."
        ) from exc

    service_kwargs: dict[str, Any] = {"channel": args.channel}
    if args.instance:
        service_kwargs["instance"] = args.instance
    service = QiskitRuntimeService(**service_kwargs)
    backends = list(service.backends(simulator=False, operational=True))
    selected = select_backend(
        backends,
        used_backends=used_backends,
        requested_backend=args.backend,
    )
    selected_name = backend_name(selected)

    print("Existing complete runs:", len(completed_before))
    print("Previously used backends:", sorted(used_backends) or ["none"])
    print("Selected unused backend:", selected_name)
    print("Target complete runs:", args.target_runs)

    if args.dry_run:
        print("Dry run only. No IBM job submitted.")
        return 0

    run_checked(
        [
            sys.executable,
            str(BENCHMARK),
            "--backend",
            selected_name,
            "--shots",
            str(args.shots),
            "--output-root",
            str(runs_root),
        ]
    )
    run_checked(
        [
            sys.executable,
            str(EVALUATOR),
            "--runs-root",
            str(runs_root),
            "--output-root",
            str(replication_root),
        ]
    )

    completed_after = load_completed_runs(runs_root)
    if len(completed_after) != len(completed_before) + 1:
        raise RuntimeError(
            "The campaign did not gain exactly one complete evidence bundle after submission."
        )
    print(
        f"Campaign now contains {len(completed_after)} complete runs. "
        f"Run this command again if the target of {args.target_runs} has not been reached."
    )
    return 0


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
        _FakeBackend("used", 127, 0),
        _FakeBackend("too_small", 5, 0),
        _FakeBackend("fresh_busy", 127, 9),
        _FakeBackend("fresh_quiet", 127, 2),
    ]
    selected = select_backend(
        backends,
        used_backends={"used"},
        requested_backend=None,
    )
    assert backend_name(selected) == "fresh_quiet"
    requested = select_backend(
        backends,
        used_backends={"used"},
        requested_backend="fresh_busy",
    )
    assert backend_name(requested) == "fresh_busy"
    try:
        select_backend(
            backends,
            used_backends={"used"},
            requested_backend="used",
        )
    except RuntimeError:
        pass
    else:
        raise AssertionError("A previously used backend was not rejected.")

    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        run = root / "run1"
        run.mkdir()
        (run / "certificate.json").write_text(
            json.dumps(
                {
                    "backend": "backend_a",
                    "job_id": "job_a",
                    "classification": "PASS",
                    "raw_results_sha256": "a" * 64,
                }
            ),
            encoding="utf-8",
        )
        loaded = load_completed_runs(root)
        assert len(loaded) == 1 and loaded[0]["backend"] == "backend_a"

    print(
        "Self-test passed: completed runs are detected, used backends are excluded, "
        "small backends are rejected, and the least-busy eligible backend is selected."
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--runs-root", type=Path)
    parser.add_argument("--replication-output-root", type=Path)
    parser.add_argument("--target-runs", type=int, default=DEFAULT_TARGET_RUNS)
    parser.add_argument("--shots", type=int, default=int(os.getenv("IBM_QUANTUM_SHOTS", DEFAULT_SHOTS)))
    parser.add_argument("--backend", default=os.getenv("IBM_QUANTUM_BACKEND", "").strip() or None)
    parser.add_argument("--channel", default=os.getenv("IBM_QUANTUM_CHANNEL", DEFAULT_CHANNEL).strip())
    parser.add_argument("--instance", default=os.getenv("IBM_QUANTUM_INSTANCE", "").strip() or None)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.self_test:
        self_test()
        return 0
    if args.target_runs < 2:
        raise ValueError("target-runs must be at least two.")
    if args.shots <= 0:
        raise ValueError("shots must be positive.")
    return submit_one(args)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        raise SystemExit(130)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
