#!/usr/bin/env python3
"""Verify promoted or committed hardware evidence from repository-relative paths.

This verifier is designed for the state after controlled promotion and for a
fresh checkout after the evidence commit. It verifies release-manifest hashes,
rejects undeclared evidence payload files, reruns the scientific evaluator,
checks publication decisions, and repeats the sensitive-content scan.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import tempfile
from pathlib import Path
from typing import Any, Mapping, Sequence

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_EVIDENCE_ROOT = REPO_ROOT / "evidence"
EVALUATOR_PATH = REPO_ROOT / "src" / "evaluate_multi_ledger_replication.py"
STAGING_TOOL_PATH = REPO_ROOT / "tools" / "stage_evidence_intake.py"
PROMOTION_TOOL_PATH = REPO_ROOT / "tools" / "promote_evidence_release.py"
PASS_CLASSIFICATION = "CROSS_BACKEND_REPLICATION"
EXPECTED_RUN_FILES = {"results.json", "certificate.json", "summary.md", "manifest.json"}
EXPECTED_REPLICATION_FILES = {
    "replication_certificate.json",
    "replication_summary.md",
    "replication_manifest.json",
}


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load module from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path.name} must contain a JSON object")
    return data


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def payload_files(evidence_root: Path, repository_root: Path) -> dict[str, Path]:
    files: dict[str, Path] = {}
    for root_name in ("selected_runs", "replication"):
        root = evidence_root / root_name
        if not root.is_dir():
            raise RuntimeError(f"Tracked evidence directory is missing: {root}")
        for path in sorted(root.rglob("*")):
            if path.is_file():
                relative = path.relative_to(repository_root).as_posix()
                files[relative] = path
    return files


def verify_bundle_shapes(evidence_root: Path, expected_runs: int) -> None:
    selected = evidence_root / "selected_runs"
    run_dirs = sorted(
        path for path in selected.iterdir()
        if path.is_dir() and (path / "certificate.json").is_file()
    )
    if len(run_dirs) != expected_runs:
        raise RuntimeError(
            f"Expected {expected_runs} selected run directories, found {len(run_dirs)}"
        )
    for run_dir in run_dirs:
        actual = {path.name for path in run_dir.iterdir() if path.is_file()}
        if actual != EXPECTED_RUN_FILES:
            raise RuntimeError(
                f"Unexpected selected-run file set for {run_dir.name}: {sorted(actual)}"
            )

    replication = evidence_root / "replication"
    replication_dirs = sorted(path for path in replication.iterdir() if path.is_dir())
    if len(replication_dirs) != 1:
        raise RuntimeError(
            f"Expected one replication directory, found {len(replication_dirs)}"
        )
    actual_replication = {
        path.name for path in replication_dirs[0].iterdir() if path.is_file()
    }
    if actual_replication != EXPECTED_REPLICATION_FILES:
        raise RuntimeError(
            "Unexpected replication file set: " + str(sorted(actual_replication))
        )


def verify_publication_decisions(manifest: Mapping[str, Any]) -> None:
    decisions = manifest.get("publication_decisions")
    if not isinstance(decisions, Mapping):
        raise RuntimeError("Publication decisions are missing from the release manifest")
    expected = {
        "job_identifiers": "APPROVED_FOR_PUBLIC_PROVENANCE",
        "selected_file_boundary": "TECHNICAL_REVIEW_APPROVED",
        "legal_ip_review": "PENDING_BEFORE_PUBLIC_VISIBILITY",
        "local_intake_audit": "EXCLUDED_FROM_GIT_HISTORY",
    }
    for name, status in expected.items():
        record = decisions.get(name)
        if not isinstance(record, Mapping) or record.get("status") != status:
            raise RuntimeError(
                f"Unexpected publication decision for {name}: {record!r}"
            )


def verify_tracked_evidence(
    evidence_root: Path,
    *,
    expected_runs: int = 3,
) -> dict[str, Any]:
    evidence_root = evidence_root.resolve()
    repository_root = evidence_root.parent
    release_manifest_path = evidence_root / "provenance" / "evidence_release_manifest.json"
    index_path = evidence_root / "EVIDENCE_INDEX.md"
    if not release_manifest_path.is_file():
        raise RuntimeError(f"Evidence release manifest is missing: {release_manifest_path}")
    if not index_path.is_file():
        raise RuntimeError(f"Evidence index is missing: {index_path}")

    release_manifest = load_json(release_manifest_path)
    checks = {
        "schema": release_manifest.get("schema")
        == "QUANTUM_CLASSICAL_PUBLIC_EVIDENCE_RELEASE_MANIFEST_V1",
        "release_candidate": release_manifest.get("release_candidate") == "0.1.0-rc1",
        "classification": release_manifest.get("classification") == PASS_CLASSIFICATION,
        "run_count": release_manifest.get("run_count") == expected_runs,
        "passing_run_count": release_manifest.get("passing_run_count") == expected_runs,
        "backend_count": release_manifest.get("backend_count") == expected_runs,
        "no_duplicate_job_ids": release_manifest.get("duplicate_job_ids") == [],
        "no_duplicate_result_hashes": release_manifest.get("duplicate_result_hashes") == [],
        "cross_run_stability": bool(
            release_manifest.get("cross_run_stability", {}).get("pass")
        ),
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise RuntimeError("Evidence release manifest failed: " + ", ".join(failed))

    verify_publication_decisions(release_manifest)
    verify_bundle_shapes(evidence_root, expected_runs)

    declared_files = release_manifest.get("files")
    if not isinstance(declared_files, Mapping) or not declared_files:
        raise RuntimeError("Evidence release manifest has no files map")
    actual_files = payload_files(evidence_root, repository_root)
    if set(actual_files) != set(declared_files):
        missing = sorted(set(declared_files) - set(actual_files))
        extra = sorted(set(actual_files) - set(declared_files))
        raise RuntimeError(
            f"Evidence payload file set differs from manifest; missing={missing}, extra={extra}"
        )
    for relative, expected_hash in declared_files.items():
        if not isinstance(relative, str) or not isinstance(expected_hash, str):
            raise RuntimeError("Evidence manifest file entries must be string-to-string")
        actual_hash = sha256_file(actual_files[relative])
        if actual_hash != expected_hash:
            raise RuntimeError(f"Evidence release hash mismatch for {relative}")

    evaluator = load_module("tracked_evidence_evaluator", EVALUATOR_PATH)
    campaign = evaluator.evaluate(evidence_root / "selected_runs")
    scientific_checks = {
        "classification": campaign.get("classification") == PASS_CLASSIFICATION,
        "run_count": campaign.get("run_count") == expected_runs,
        "passing_run_count": campaign.get("passing_run_count") == expected_runs,
        "backend_count": campaign.get("backend_count") == expected_runs,
        "no_duplicate_job_ids": campaign.get("duplicate_job_ids") == [],
        "no_duplicate_result_hashes": campaign.get("duplicate_result_hashes") == [],
        "cross_run_stability": bool(campaign.get("cross_run_stability", {}).get("pass")),
        "every_run_valid": all(bool(run.get("valid")) for run in campaign.get("runs", [])),
    }
    scientific_failed = [
        name for name, passed in scientific_checks.items() if not passed
    ]
    if scientific_failed:
        raise RuntimeError(
            "Tracked evidence reevaluation failed: " + ", ".join(scientific_failed)
        )

    stage = load_module("tracked_evidence_scanner", STAGING_TOOL_PATH)
    findings = stage.scan_tree(evidence_root)
    if findings:
        raise RuntimeError(
            "Tracked evidence contains sensitive/local content: "
            + json.dumps(findings, sort_keys=True)
        )

    job_ids = [str(run.get("job_id", "")) for run in release_manifest.get("runs", [])]
    if len(job_ids) != expected_runs or len(set(job_ids)) != expected_runs or not all(job_ids):
        raise RuntimeError("Release manifest does not contain three distinct job identifiers")

    payload_bytes = sum(path.stat().st_size for path in actual_files.values())
    return {
        "classification": campaign["classification"],
        "run_count": campaign["run_count"],
        "passing_run_count": campaign["passing_run_count"],
        "backend_count": campaign["backend_count"],
        "backends": campaign["backends"],
        "cross_run_stability": campaign["cross_run_stability"]["pass"],
        "content_scan": True,
        "payload_file_count": len(actual_files),
        "tracked_evidence_file_count": len(actual_files) + 2,
        "payload_bytes": payload_bytes,
        "legal_ip_review": "PENDING_BEFORE_PUBLIC_VISIBILITY",
    }


def self_test() -> None:
    evaluator = load_module("tracked_fixture_evaluator", EVALUATOR_PATH)
    stage = load_module("tracked_fixture_stage", STAGING_TOOL_PATH)
    promote = load_module("tracked_fixture_promote", PROMOTION_TOOL_PATH)
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        private_runs = root / "private" / "runs"
        private_runs.mkdir(parents=True)
        evaluator.make_fixture(private_runs, name="run1", backend="backend_a", job_id="job1")
        evaluator.make_fixture(private_runs, name="run2", backend="backend_b", job_id="job2")
        evaluator.make_fixture(private_runs, name="run3", backend="backend_c", job_id="job3")
        private_replication = root / "private" / "replication"
        evaluator.write_outputs(evaluator.evaluate(private_runs), private_replication)
        staging = root / "repo" / "evidence" / "intake_staging"
        stage.stage_evidence(
            runs_root=private_runs,
            replication_root=private_replication,
            staging_root=staging,
            expected_runs=3,
            replace=False,
        )
        evidence = root / "repo" / "evidence"
        promote.promote(
            staging_root=staging,
            evidence_root=evidence,
            expected_runs=3,
            replace=False,
            approve_job_identifiers=True,
            approve_selected_file_boundary=True,
        )
        summary = verify_tracked_evidence(evidence, expected_runs=3)
        assert summary["classification"] == PASS_CLASSIFICATION
        assert summary["tracked_evidence_file_count"] == 17
        manifest = load_json(evidence / "provenance" / "evidence_release_manifest.json")
        first = next(iter(manifest["files"]))
        target = evidence.parent / first
        target.write_text(target.read_text(encoding="utf-8") + "\n", encoding="utf-8")
        try:
            verify_tracked_evidence(evidence, expected_runs=3)
        except RuntimeError as exc:
            assert "hash mismatch" in str(exc)
        else:
            raise AssertionError("Tampered tracked evidence was not rejected")
    print(
        "Self-test passed: promoted evidence, exact file sets, release hashes, "
        "scientific reevaluation, publication decisions, content scanning, and "
        "tamper rejection are enforced."
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--evidence-root", type=Path, default=DEFAULT_EVIDENCE_ROOT)
    parser.add_argument("--expected-runs", type=int, default=3)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.self_test:
        self_test()
        return 0
    summary = verify_tracked_evidence(
        args.evidence_root.expanduser().resolve(),
        expected_runs=args.expected_runs,
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        raise SystemExit(130)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
