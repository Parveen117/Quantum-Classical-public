#!/usr/bin/env python3
"""Promote audited evidence from local intake staging into tracked release paths.

The command requires explicit approval for publishing IBM job identifiers and
for the patent boundary. It re-verifies the intake audit, manifests, hashes,
sensitive-content scan, and campaign classification. The local intake audit is
never copied because it can contain a workstation path.

This tool changes files in the local checkout but does not run git add, commit,
push, merge, tag, or change repository visibility.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any, Mapping, Sequence

REPO_ROOT = Path(__file__).resolve().parents[1]
STAGING_TOOL_PATH = REPO_ROOT / "tools" / "stage_evidence_intake.py"
EVALUATOR_PATH = REPO_ROOT / "src" / "evaluate_multi_ledger_replication.py"
DEFAULT_STAGING_ROOT = REPO_ROOT / "evidence" / "intake_staging"
DEFAULT_EVIDENCE_ROOT = REPO_ROOT / "evidence"
PASS_CLASSIFICATION = "CROSS_BACKEND_REPLICATION"
RELEASE_CANDIDATE = "0.1.0-rc1"


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


def collect_hashes(root: Path, repository_root: Path) -> dict[str, str]:
    hashes: dict[str, str] = {}
    for path in sorted(root.rglob("*")):
        if path.is_file():
            hashes[path.relative_to(repository_root).as_posix()] = sha256_file(path)
    return hashes


def validate_intake_audit(audit: Mapping[str, Any], expected_runs: int) -> None:
    checks = {
        "schema": audit.get("schema") == "QUANTUM_CLASSICAL_EVIDENCE_INTAKE_AUDIT_V1",
        "release_candidate": audit.get("release_candidate") == RELEASE_CANDIDATE,
        "classification": audit.get("classification") == PASS_CLASSIFICATION,
        "run_count": audit.get("run_count") == expected_runs,
        "passing_run_count": audit.get("passing_run_count") == expected_runs,
        "backend_count": audit.get("backend_count") == expected_runs,
        "no_duplicate_job_ids": audit.get("duplicate_job_ids") == [],
        "no_duplicate_result_hashes": audit.get("duplicate_result_hashes") == [],
        "cross_run_stability": bool(audit.get("cross_run_stability", {}).get("pass")),
        "content_scan": bool(audit.get("content_scan", {}).get("pass")),
        "campaign_checks": all(bool(value) for value in audit.get("campaign_checks", {}).values()),
        "run_audit_count": len(audit.get("runs", [])) == expected_runs,
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise RuntimeError("Intake audit is not promotable: " + ", ".join(failed))


def verify_staged_tree(staging_root: Path, audit: Mapping[str, Any], expected_runs: int) -> None:
    stage = load_module("public_stage_evidence", STAGING_TOOL_PATH)
    selected = staging_root / "selected_runs"
    replication = staging_root / "replication"
    if not selected.is_dir() or not replication.is_dir():
        raise RuntimeError("Staging tree is missing selected_runs or replication")

    audited_runs = audit.get("runs", [])
    expected_ids = {str(item.get("public_run_id")) for item in audited_runs}
    actual_ids = {
        path.name for path in selected.iterdir()
        if path.is_dir() and (path / "certificate.json").is_file()
    }
    if actual_ids != expected_ids or len(actual_ids) != expected_runs:
        raise RuntimeError("Staged run directories do not match the intake audit")

    for item in audited_runs:
        run_id = str(item["public_run_id"])
        run_dir = selected / run_id
        verified = stage.verify_manifest(run_dir, "manifest.json")
        audited_files = item.get("files")
        if not isinstance(audited_files, Mapping) or dict(verified) != dict(audited_files):
            raise RuntimeError(f"Staged file hashes changed after intake for {run_id}")

    replication_record = audit.get("replication")
    if not isinstance(replication_record, Mapping):
        raise RuntimeError("Replication audit record is missing")
    replication_id = str(replication_record.get("public_replication_id", ""))
    replication_dir = replication / replication_id
    if not replication_id or not replication_dir.is_dir():
        raise RuntimeError("Audited replication directory is missing")
    verified_replication = stage.verify_manifest(
        replication_dir, "replication_manifest.json"
    )
    audited_replication_files = replication_record.get("files")
    if not isinstance(audited_replication_files, Mapping):
        raise RuntimeError("Replication file audit is missing")
    if dict(verified_replication) != dict(audited_replication_files):
        raise RuntimeError("Replication file hashes changed after intake")

    findings = stage.scan_tree(staging_root)
    if findings:
        raise RuntimeError(
            "Sensitive content appeared after intake: "
            + json.dumps(findings, sort_keys=True)
        )


def build_release_manifest(
    *,
    audit: Mapping[str, Any],
    repository_root: Path,
    evidence_root: Path,
) -> dict[str, Any]:
    selected_root = evidence_root / "selected_runs"
    replication_root = evidence_root / "replication"
    release_files = collect_hashes(selected_root, repository_root)
    release_files.update(collect_hashes(replication_root, repository_root))

    runs = []
    for item in audit["runs"]:
        runs.append({
            "public_run_id": item["public_run_id"],
            "backend": item["backend"],
            "job_id": item["job_id"],
            "classification": item["classification"],
            "raw_results_sha256": item["raw_results_sha256"],
        })

    return {
        "schema": "QUANTUM_CLASSICAL_PUBLIC_EVIDENCE_RELEASE_MANIFEST_V1",
        "release_candidate": RELEASE_CANDIDATE,
        "private_authoritative_archive": "Parveen117/quantum-classical-provisional",
        "public_repository": "Parveen117/Quantum-Classical-public",
        "classification": audit["classification"],
        "run_count": audit["run_count"],
        "passing_run_count": audit["passing_run_count"],
        "backend_count": audit["backend_count"],
        "backends": audit["backends"],
        "duplicate_job_ids": audit["duplicate_job_ids"],
        "duplicate_result_hashes": audit["duplicate_result_hashes"],
        "cross_run_stability": audit["cross_run_stability"],
        "runs": runs,
        "replication": audit["replication"],
        "publication_decisions": {
            "job_identifiers": {
                "status": "APPROVED_FOR_PUBLIC_PROVENANCE",
                "rationale": (
                    "IBM job identifiers distinguish independent executions and are not "
                    "authentication credentials. Their inclusion is limited to evidence provenance."
                ),
            },
            "patent_boundary": {
                "status": "APPROVED_FOR_SELECTED_EVIDENCE_ONLY",
                "rationale": (
                    "Promotion is limited to benchmark results, certificates, summaries, and manifests. "
                    "No fabrication packet, device implementation, claim strategy, or examiner material is included."
                ),
            },
            "local_intake_audit": {
                "status": "EXCLUDED_FROM_GIT_HISTORY",
                "rationale": "The local audit can contain a workstation staging path.",
            },
        },
        "files": release_files,
        "scientific_boundary": audit["scientific_boundary"],
    }


def write_evidence_index(evidence_root: Path, release_manifest: Mapping[str, Any]) -> None:
    lines = [
        "# Released Hardware Evidence",
        "",
        f"- Release candidate: `{release_manifest['release_candidate']}`",
        f"- Classification: `{release_manifest['classification']}`",
        f"- Passing runs: `{release_manifest['passing_run_count']}`",
        f"- Distinct backends: `{release_manifest['backend_count']}`",
        f"- Cross-run stability: `{release_manifest['cross_run_stability']['pass']}`",
        "- Duplicate job identifiers: `none`",
        "- Duplicate raw-result hashes: `none`",
        "",
        "## Runs",
        "",
    ]
    for run in release_manifest["runs"]:
        lines.extend([
            f"- `{run['public_run_id']}`",
            f"  - backend: `{run['backend']}`",
            f"  - IBM job identifier: `{run['job_id']}`",
            f"  - classification: `{run['classification']}`",
            f"  - raw-results SHA-256: `{run['raw_results_sha256']}`",
        ])
    lines.extend([
        "",
        "## Boundary",
        "",
        str(release_manifest["scientific_boundary"]),
        "",
        "The private provisional repository remains the authoritative archive for unselected development evidence.",
    ])
    (evidence_root / "EVIDENCE_INDEX.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )


def promote(
    *,
    staging_root: Path,
    evidence_root: Path,
    expected_runs: int,
    replace: bool,
    approve_job_identifiers: bool,
    approve_patent_boundary: bool,
) -> dict[str, Any]:
    if not approve_job_identifiers:
        raise RuntimeError("Pass --approve-job-identifiers after explicit publication review")
    if not approve_patent_boundary:
        raise RuntimeError("Pass --approve-patent-boundary after explicit selected-file review")

    audit_path = staging_root / "intake_audit.json"
    if not audit_path.is_file():
        raise RuntimeError(f"Local intake audit is missing: {audit_path}")
    audit = load_json(audit_path)
    validate_intake_audit(audit, expected_runs)
    verify_staged_tree(staging_root, audit, expected_runs)

    repository_root = evidence_root.parent
    selected_destination = evidence_root / "selected_runs"
    replication_destination = evidence_root / "replication"
    provenance_root = evidence_root / "provenance"
    manifest_path = provenance_root / "evidence_release_manifest.json"
    index_path = evidence_root / "EVIDENCE_INDEX.md"

    existing = [
        path for path in (
            selected_destination,
            replication_destination,
            manifest_path,
            index_path,
        ) if path.exists()
    ]
    if existing and not replace:
        raise RuntimeError(
            "Tracked evidence destinations already exist: "
            + ", ".join(str(path) for path in existing)
            + ". Use --replace only after reviewing the existing release evidence."
        )

    evaluator = load_module("public_replication_evaluator", EVALUATOR_PATH)
    stage = load_module("public_stage_evidence_for_promotion", STAGING_TOOL_PATH)

    evidence_root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="evidence_promotion_", dir=evidence_root) as tmp:
        temporary = Path(tmp)
        temporary_selected = temporary / "selected_runs"
        temporary_replication = temporary / "replication"
        shutil.copytree(staging_root / "selected_runs", temporary_selected)
        shutil.copytree(staging_root / "replication", temporary_replication)

        campaign = evaluator.evaluate(temporary_selected)
        checks = {
            "classification": campaign.get("classification") == PASS_CLASSIFICATION,
            "run_count": campaign.get("run_count") == expected_runs,
            "passing_run_count": campaign.get("passing_run_count") == expected_runs,
            "backend_count": campaign.get("backend_count") == expected_runs,
            "no_duplicate_job_ids": campaign.get("duplicate_job_ids") == [],
            "no_duplicate_result_hashes": campaign.get("duplicate_result_hashes") == [],
            "cross_run_stability": bool(campaign.get("cross_run_stability", {}).get("pass")),
            "every_run_valid": all(bool(run.get("valid")) for run in campaign.get("runs", [])),
        }
        failed = [name for name, passed in checks.items() if not passed]
        if failed:
            raise RuntimeError("Promoted copy failed reevaluation: " + ", ".join(failed))
        findings = stage.scan_tree(temporary)
        if findings:
            raise RuntimeError("Promoted copy failed content scan: " + json.dumps(findings))

        if replace:
            for path in (selected_destination, replication_destination):
                if path.exists():
                    shutil.rmtree(path)
            for path in (manifest_path, index_path):
                if path.exists():
                    path.unlink()

        shutil.move(str(temporary_selected), str(selected_destination))
        shutil.move(str(temporary_replication), str(replication_destination))

    provenance_root.mkdir(parents=True, exist_ok=True)
    release_manifest = build_release_manifest(
        audit=audit,
        repository_root=repository_root,
        evidence_root=evidence_root,
    )
    manifest_path.write_text(
        json.dumps(release_manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    write_evidence_index(evidence_root, release_manifest)

    final_findings = stage.scan_tree(evidence_root)
    if final_findings:
        raise RuntimeError(
            "Final tracked evidence failed content scan: "
            + json.dumps(final_findings, sort_keys=True)
        )

    return {
        "classification": release_manifest["classification"],
        "run_count": release_manifest["run_count"],
        "passing_run_count": release_manifest["passing_run_count"],
        "backend_count": release_manifest["backend_count"],
        "backends": release_manifest["backends"],
        "cross_run_stability": release_manifest["cross_run_stability"]["pass"],
        "job_identifier_publication": "APPROVED_FOR_PUBLIC_PROVENANCE",
        "patent_boundary": "APPROVED_FOR_SELECTED_EVIDENCE_ONLY",
        "local_intake_audit_committed": False,
        "tracked_file_count": len(release_manifest["files"]) + 2,
    }


def self_test() -> None:
    evaluator = load_module("promotion_test_evaluator", EVALUATOR_PATH)
    stage = load_module("promotion_test_stage", STAGING_TOOL_PATH)
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        runs = root / "private" / "runs"
        runs.mkdir(parents=True)
        evaluator.make_fixture(runs, name="run1", backend="backend_a", job_id="job1")
        evaluator.make_fixture(runs, name="run2", backend="backend_b", job_id="job2")
        evaluator.make_fixture(runs, name="run3", backend="backend_c", job_id="job3")
        replication = root / "private" / "replication"
        evaluator.write_outputs(evaluator.evaluate(runs), replication)
        staging = root / "public" / "evidence" / "intake_staging"
        stage.stage_evidence(
            runs_root=runs,
            replication_root=replication,
            staging_root=staging,
            expected_runs=3,
            replace=False,
        )
        evidence = root / "public" / "evidence"
        result = promote(
            staging_root=staging,
            evidence_root=evidence,
            expected_runs=3,
            replace=False,
            approve_job_identifiers=True,
            approve_patent_boundary=True,
        )
        assert result["classification"] == PASS_CLASSIFICATION
        assert result["local_intake_audit_committed"] is False
        assert (evidence / "selected_runs" / "run1" / "results.json").is_file()
        assert (evidence / "provenance" / "evidence_release_manifest.json").is_file()
        assert not (evidence / "intake_audit.json").exists()
    print(
        "Self-test passed: explicit approvals, intake revalidation, exact promotion, "
        "campaign reevaluation, public manifest generation, and local-audit exclusion are enforced."
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--staging-root", type=Path, default=DEFAULT_STAGING_ROOT)
    parser.add_argument("--evidence-root", type=Path, default=DEFAULT_EVIDENCE_ROOT)
    parser.add_argument("--expected-runs", type=int, default=3)
    parser.add_argument("--approve-job-identifiers", action="store_true")
    parser.add_argument("--approve-patent-boundary", action="store_true")
    parser.add_argument("--replace", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.self_test:
        self_test()
        return 0
    result = promote(
        staging_root=args.staging_root.expanduser().resolve(),
        evidence_root=args.evidence_root.expanduser().resolve(),
        expected_runs=args.expected_runs,
        replace=args.replace,
        approve_job_identifiers=args.approve_job_identifiers,
        approve_patent_boundary=args.approve_patent_boundary,
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    print("\nEvidence promoted into tracked paths. Review git diff before committing.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        raise SystemExit(130)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
