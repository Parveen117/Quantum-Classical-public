#!/usr/bin/env python3
"""Stage selected hardware evidence for public audit without committing it.

The tool verifies the complete campaign using the public evaluator, copies only
the declared release files into a git-ignored staging directory, scans the
staged text for credentials and local/private paths, and writes an intake audit.
It never changes Git state or repository visibility.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

REPO_ROOT = Path(__file__).resolve().parents[1]
EVALUATOR_PATH = REPO_ROOT / "src" / "evaluate_multi_ledger_replication.py"
DEFAULT_STAGING_ROOT = REPO_ROOT / "evidence" / "intake_staging"
RUN_FILES = ("results.json", "certificate.json", "summary.md", "manifest.json")
REPLICATION_FILES = (
    "replication_certificate.json",
    "replication_summary.md",
    "replication_manifest.json",
)
PASS_CLASSIFICATION = "CROSS_BACKEND_REPLICATION"
SENSITIVE_KEY_PARTS = {
    "token", "api_key", "apikey", "secret", "password", "credential",
    "account_id", "email", "instance", "crn",
}
TEXT_PATTERNS = {
    "Windows user path": re.compile(r"[A-Za-z]:\\Users\\", re.IGNORECASE),
    "POSIX home path": re.compile(r"/(?:home|Users)/[^/\s]+/", re.IGNORECASE),
    "private workstation folder": re.compile(r"PROVISNAL RELATED", re.IGNORECASE),
    "email address": re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE),
    "PEM private key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
}


def load_evaluator() -> Any:
    spec = importlib.util.spec_from_file_location("public_replication_evaluator", EVALUATOR_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load evaluator: {EVALUATOR_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path.name} must contain a JSON object")
    return data


def safe_relative_name(name: str) -> bool:
    relative = Path(name)
    return bool(name) and not relative.is_absolute() and ".." not in relative.parts


def verify_manifest(directory: Path, manifest_name: str) -> dict[str, str]:
    manifest = load_json(directory / manifest_name)
    files = manifest.get("files")
    if not isinstance(files, Mapping) or not files:
        raise RuntimeError(f"{manifest_name} has no files map")
    verified: dict[str, str] = {}
    for name, expected in files.items():
        if not isinstance(name, str) or not isinstance(expected, str):
            raise RuntimeError(f"{manifest_name} contains a non-string file entry")
        if not safe_relative_name(name):
            raise RuntimeError(f"{manifest_name} contains an unsafe path: {name!r}")
        path = (directory / name).resolve()
        try:
            path.relative_to(directory.resolve())
        except ValueError as exc:
            raise RuntimeError(f"{manifest_name} path escapes its directory: {name!r}") from exc
        if not path.is_file():
            raise RuntimeError(f"{manifest_name} references a missing file: {name}")
        actual = sha256_file(path)
        if actual != expected:
            raise RuntimeError(f"{manifest_name} hash mismatch for {name}")
        verified[name] = actual
    return verified


def find_latest_replication_bundle(replication_root: Path) -> Path:
    candidates = sorted(
        path for path in replication_root.iterdir()
        if path.is_dir() and (path / "replication_certificate.json").is_file()
    ) if replication_root.exists() else []
    if not candidates:
        raise RuntimeError(f"No replication bundle found under {replication_root}")
    return max(candidates, key=lambda path: (path.stat().st_mtime_ns, path.name))


def iter_json_values(value: Any, path: str = "$") -> Iterable[tuple[str, Any]]:
    if isinstance(value, Mapping):
        for key, item in value.items():
            key_text = str(key)
            child = f"{path}.{key_text}"
            yield child, item
            yield from iter_json_values(item, child)
    elif isinstance(value, list):
        for index, item in enumerate(value):
            child = f"{path}[{index}]"
            yield child, item
            yield from iter_json_values(item, child)


def scan_file(path: Path) -> list[str]:
    findings: list[str] = []
    text = path.read_text(encoding="utf-8", errors="replace")
    for label, pattern in TEXT_PATTERNS.items():
        if pattern.search(text):
            findings.append(label)
    if path.suffix.lower() == ".json":
        try:
            data = json.loads(text)
        except json.JSONDecodeError as exc:
            findings.append(f"invalid JSON: {exc}")
            return findings
        for location, value in iter_json_values(data):
            key = location.rsplit(".", 1)[-1].lower()
            if any(part in key for part in SENSITIVE_KEY_PARTS):
                if value not in (None, "", [], {}, False):
                    findings.append(f"sensitive field populated at {location}")
    return sorted(set(findings))


def scan_tree(root: Path) -> dict[str, list[str]]:
    findings: dict[str, list[str]] = {}
    for path in sorted(root.rglob("*")):
        if path.is_file() and path.name not in {"intake_audit.json", "intake_audit.md"}:
            file_findings = scan_file(path)
            if file_findings:
                findings[path.relative_to(root).as_posix()] = file_findings
    return findings


def copy_exact_files(source: Path, destination: Path, names: Sequence[str]) -> dict[str, str]:
    destination.mkdir(parents=True, exist_ok=False)
    hashes: dict[str, str] = {}
    for name in names:
        source_file = source / name
        if not source_file.is_file():
            raise RuntimeError(f"Required evidence file is missing: {source_file}")
        destination_file = destination / name
        shutil.copyfile(source_file, destination_file)
        source_hash = sha256_file(source_file)
        destination_hash = sha256_file(destination_file)
        if source_hash != destination_hash:
            raise RuntimeError(f"Copied evidence changed unexpectedly: {name}")
        hashes[name] = destination_hash
    return hashes


def stage_evidence(*, runs_root: Path, replication_root: Path, staging_root: Path,
                   expected_runs: int, replace: bool) -> dict[str, Any]:
    evaluator = load_evaluator()
    campaign = evaluator.evaluate(runs_root)
    required = {
        "classification": campaign.get("classification") == PASS_CLASSIFICATION,
        "run_count": campaign.get("run_count") == expected_runs,
        "passing_run_count": campaign.get("passing_run_count") == expected_runs,
        "backend_count": campaign.get("backend_count") == expected_runs,
        "no_duplicate_job_ids": campaign.get("duplicate_job_ids") == [],
        "no_duplicate_result_hashes": campaign.get("duplicate_result_hashes") == [],
        "cross_run_stability": bool(campaign.get("cross_run_stability", {}).get("pass")),
        "every_run_valid": all(bool(run.get("valid")) for run in campaign.get("runs", [])),
    }
    failed = [name for name, passed in required.items() if not passed]
    if failed:
        raise RuntimeError("Campaign is not eligible for intake: " + ", ".join(failed))

    replication_bundle = find_latest_replication_bundle(replication_root)
    replication_certificate = load_json(replication_bundle / "replication_certificate.json")
    if replication_certificate.get("classification") != PASS_CLASSIFICATION:
        raise RuntimeError("Latest replication bundle is not CROSS_BACKEND_REPLICATION")
    if replication_certificate.get("run_count") != expected_runs:
        raise RuntimeError("Latest replication bundle has the wrong run count")
    verify_manifest(replication_bundle, "replication_manifest.json")

    if staging_root.exists():
        if not replace:
            raise RuntimeError(
                f"Staging directory already exists: {staging_root}. "
                "Use --replace only after reviewing the previous audit."
            )
        shutil.rmtree(staging_root)
    staging_root.mkdir(parents=True)

    selected_root = staging_root / "selected_runs"
    replication_destination_root = staging_root / "replication"
    selected_root.mkdir()
    replication_destination_root.mkdir()

    run_audit: list[dict[str, Any]] = []
    for run in campaign["runs"]:
        source_dir = runs_root / str(run["run_name"])
        destination_dir = selected_root / source_dir.name
        verify_manifest(source_dir, "manifest.json")
        hashes = copy_exact_files(source_dir, destination_dir, RUN_FILES)
        run_audit.append({
            "public_run_id": source_dir.name,
            "backend": run["backend"],
            "job_id": run["job_id"],
            "classification": run["classification"],
            "raw_results_sha256": run["raw_results_sha256"],
            "files": hashes,
        })

    replication_id = replication_bundle.name
    replication_destination = replication_destination_root / replication_id
    replication_hashes = copy_exact_files(
        replication_bundle, replication_destination, REPLICATION_FILES
    )

    findings = scan_tree(staging_root)
    if findings:
        report = "\n".join(
            f"{path}: {', '.join(items)}" for path, items in sorted(findings.items())
        )
        raise RuntimeError(
            "Sensitive or local content was detected in staged evidence:\n" + report
        )

    audit = {
        "schema": "QUANTUM_CLASSICAL_EVIDENCE_INTAKE_AUDIT_V1",
        "release_candidate": "0.1.0-rc1",
        "campaign_checks": required,
        "classification": campaign["classification"],
        "run_count": campaign["run_count"],
        "passing_run_count": campaign["passing_run_count"],
        "backend_count": campaign["backend_count"],
        "backends": campaign["backends"],
        "duplicate_job_ids": campaign["duplicate_job_ids"],
        "duplicate_result_hashes": campaign["duplicate_result_hashes"],
        "cross_run_stability": campaign["cross_run_stability"],
        "job_identifier_publication_review": "PENDING_FINAL_APPROVAL",
        "runs": run_audit,
        "replication": {
            "public_replication_id": replication_id,
            "files": replication_hashes,
        },
        "content_scan": {
            "pass": True,
            "findings": {},
            "patterns": sorted(TEXT_PATTERNS),
            "sensitive_json_key_parts": sorted(SENSITIVE_KEY_PARTS),
        },
        "scientific_boundary": (
            "The staged files support audit of a declared cross-backend quantum "
            "operator-order memory representation. They do not establish a fabricated "
            "device, material memory mechanism, thermodynamic proof, quantum advantage, "
            "fault tolerance, or a universal physical law."
        ),
        "next_gate": (
            "Human review of job identifiers, calibration/execution metadata, patent "
            "boundary, and final public file list before promotion from intake_staging."
        ),
    }
    audit_path = staging_root / "intake_audit.json"
    audit_path.write_text(json.dumps(audit, indent=2, sort_keys=True), encoding="utf-8")

    lines = [
        "# Evidence Intake Audit", "",
        f"- Classification: `{audit['classification']}`",
        f"- Runs: `{audit['run_count']}`",
        f"- Passing runs: `{audit['passing_run_count']}`",
        f"- Backends: `{', '.join(audit['backends'])}`",
        f"- Cross-run stability: `{audit['cross_run_stability']['pass']}`",
        "- Duplicate job identifiers: `none`",
        "- Duplicate raw-result hashes: `none`",
        "- Credential, personal-information, and local-path scan: `pass`",
        "- Job-identifier publication decision: `pending final approval`", "",
        "The staging directory is intentionally not ready to commit. Review the audit "
        "and evidence files before promotion into `evidence/selected_runs` and "
        "`evidence/replication`.", "",
    ]
    (staging_root / "intake_audit.md").write_text("\n".join(lines), encoding="utf-8")
    return audit


def self_test() -> None:
    evaluator = load_evaluator()
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        runs = root / "runs"
        runs.mkdir()
        evaluator.make_fixture(runs, name="run1", backend="backend_a", job_id="job1")
        evaluator.make_fixture(runs, name="run2", backend="backend_b", job_id="job2")
        evaluator.make_fixture(runs, name="run3", backend="backend_c", job_id="job3")
        replication = root / "replication"
        certificate = evaluator.evaluate(runs)
        assert certificate["classification"] == PASS_CLASSIFICATION
        evaluator.write_outputs(certificate, replication)
        staging = root / "staging"
        audit = stage_evidence(
            runs_root=runs, replication_root=replication, staging_root=staging,
            expected_runs=3, replace=False,
        )
        assert audit["content_scan"]["pass"] is True
        assert len(audit["runs"]) == 3
        assert (staging / "intake_audit.json").is_file()
    print(
        "Self-test passed: triple campaign verification, manifest checking, exact-copy "
        "hashing, staging, and sensitive-content scanning are enforced."
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--runs-root", type=Path)
    parser.add_argument("--replication-root", type=Path)
    parser.add_argument("--staging-root", type=Path, default=DEFAULT_STAGING_ROOT)
    parser.add_argument("--expected-runs", type=int, default=3)
    parser.add_argument("--replace", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.self_test:
        self_test()
        return 0
    if args.runs_root is None:
        raise ValueError("--runs-root is required")
    replication_root = (
        args.replication_root
        if args.replication_root is not None
        else args.runs_root.resolve().parent / "replication"
    )
    audit = stage_evidence(
        runs_root=args.runs_root.expanduser().resolve(),
        replication_root=replication_root.expanduser().resolve(),
        staging_root=args.staging_root.expanduser().resolve(),
        expected_runs=args.expected_runs,
        replace=args.replace,
    )
    print(json.dumps({
        "classification": audit["classification"],
        "run_count": audit["run_count"],
        "passing_run_count": audit["passing_run_count"],
        "backend_count": audit["backend_count"],
        "backends": audit["backends"],
        "cross_run_stability": audit["cross_run_stability"]["pass"],
        "content_scan": audit["content_scan"]["pass"],
        "job_identifier_publication_review": audit["job_identifier_publication_review"],
        "staging_root": str(args.staging_root.expanduser().resolve()),
    }, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        raise SystemExit(130)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
