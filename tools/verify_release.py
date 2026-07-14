#!/usr/bin/env python3
"""Run offline public-release checks without IBM credentials."""

from __future__ import annotations

import argparse
import json
import py_compile
import re
import subprocess
import sys
from pathlib import Path
from typing import Iterable, Sequence

REPO_ROOT = Path(__file__).resolve().parents[1]
MARKDOWN_CHECKER = REPO_ROOT / "tools" / "check_markdown_links.py"
SOURCE_FILES = (
    REPO_ROOT / "src" / "run_multi_ledger_operator_memory_test.py",
    REPO_ROOT / "src" / "evaluate_multi_ledger_replication.py",
    REPO_ROOT / "src" / "run_multi_ledger_replication_job.py",
    REPO_ROOT / "src" / "run_replication_campaign_job.py",
    REPO_ROOT / "tools" / "stage_evidence_intake.py",
    REPO_ROOT / "tools" / "promote_evidence_release.py",
    REPO_ROOT / "tools" / "verify_tracked_evidence.py",
    REPO_ROOT / "tools" / "generate_release_summary.py",
    MARKDOWN_CHECKER,
)
SCHEMA_DIR = REPO_ROOT / "schemas"
TEXT_SUFFIXES = {".py", ".md", ".toml", ".cff", ".json", ".txt", ".yml", ".yaml"}
SCAN_EXCLUDED_FILES = {
    Path(__file__).resolve(),
    (REPO_ROOT / "tools" / "stage_evidence_intake.py").resolve(),
}
FORBIDDEN_LITERAL_PATTERNS = {
    "local Windows user path": re.compile(r"[A-Za-z]:\\Users\\", re.IGNORECASE),
    "private development folder": re.compile(r"PROVISNAL RELATED", re.IGNORECASE),
    "hardcoded IBM token": re.compile(r"QISKIT_IBM_TOKEN\s*=\s*['\"][^<\s][^'\"]+['\"]", re.IGNORECASE),
    "hardcoded API key": re.compile(r"(?:api[_-]?key|token|secret)\s*=\s*['\"][A-Za-z0-9_\-]{20,}['\"]", re.IGNORECASE),
}
INCORRECT_PUBLICATION_IDENTITIES = (
    "Parveen Dabas",
    "Kajal Dabas",
)


def run(command: Sequence[str]) -> None:
    result = subprocess.run(command, cwd=REPO_ROOT, text=True, capture_output=True)
    if result.stdout:
        print(result.stdout, end="")
    if result.stderr:
        print(result.stderr, end="", file=sys.stderr)
    if result.returncode != 0:
        raise RuntimeError(f"Command failed ({result.returncode}): {' '.join(command)}")


def iter_text_files() -> Iterable[Path]:
    excluded = {
        ".git", ".venv", "venv", "__pycache__", ".pytest_cache",
        "generated", "intake_staging",
    }
    for path in REPO_ROOT.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        if path.resolve() in SCAN_EXCLUDED_FILES:
            continue
        if any(part in excluded for part in path.parts):
            continue
        yield path


def validate_schemas() -> None:
    if not SCHEMA_DIR.exists():
        raise RuntimeError("schemas directory is missing")
    schemas = sorted(SCHEMA_DIR.glob("*.schema.json"))
    if len(schemas) < 4:
        raise RuntimeError("Expected at least four public JSON schemas")
    for schema in schemas:
        data = json.loads(schema.read_text(encoding="utf-8"))
        if data.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
            raise RuntimeError(f"{schema.name} does not declare JSON Schema 2020-12")
        if not data.get("title") or data.get("type") != "object":
            raise RuntimeError(f"{schema.name} is missing a title or object type")


def scan_forbidden_content() -> None:
    findings: list[str] = []
    for path in iter_text_files():
        text = path.read_text(encoding="utf-8", errors="replace")
        for label, pattern in FORBIDDEN_LITERAL_PATTERNS.items():
            if pattern.search(text):
                findings.append(f"{path.relative_to(REPO_ROOT)}: {label}")
    if findings:
        raise RuntimeError("Forbidden public content detected:\n" + "\n".join(findings))


def verify_attribution() -> None:
    full_name_files = (
        REPO_ROOT / "README.md",
        REPO_ROOT / "LICENSE",
        REPO_ROOT / "pyproject.toml",
        REPO_ROOT / "docs" / "RELEASE_NOTES_RC1.md",
    )
    for path in full_name_files:
        if not path.is_file():
            raise RuntimeError(f"Required attribution file is missing: {path.relative_to(REPO_ROOT)}")
        text = path.read_text(encoding="utf-8")
        if "Monty Dabas" not in text:
            raise RuntimeError(
                f"Monty Dabas publication attribution is missing from {path.relative_to(REPO_ROOT)}"
            )

    citation_path = REPO_ROOT / "CITATION.cff"
    if not citation_path.is_file():
        raise RuntimeError("Required release file is missing: CITATION.cff")
    citation = citation_path.read_text(encoding="utf-8")
    required_citation_fields = (
        'family-names: "Dabas"',
        'given-names: "Monty"',
        'orcid: "https://orcid.org/0009-0005-6948-209X"',
        'affiliation: "Independent Researcher"',
    )
    for field in required_citation_fields:
        if field not in citation:
            raise RuntimeError(f"CITATION.cff is missing required publication field: {field}")

    findings: list[str] = []
    wrong_cff_given_name = re.compile(
        r"given-names\s*:\s*['\"](?:Parveen|Kajal)['\"]",
        re.IGNORECASE,
    )
    for path in iter_text_files():
        text = path.read_text(encoding="utf-8", errors="replace")
        for identity in INCORRECT_PUBLICATION_IDENTITIES:
            if identity.lower() in text.lower():
                findings.append(
                    f"{path.relative_to(REPO_ROOT)}: incorrect publication identity {identity!r}"
                )
        if wrong_cff_given_name.search(text):
            findings.append(
                f"{path.relative_to(REPO_ROOT)}: incorrect CFF publication given-name"
            )
    if findings:
        raise RuntimeError("Incorrect publication attribution detected:\n" + "\n".join(findings))


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skip-self-tests", action="store_true")
    args = parser.parse_args(argv)

    for source in SOURCE_FILES:
        if not source.is_file():
            raise RuntimeError(f"Missing public source file: {source.relative_to(REPO_ROOT)}")
        py_compile.compile(str(source), doraise=True)
    print("PASS: Python syntax compilation")

    validate_schemas()
    print("PASS: JSON schema structure")

    scan_forbidden_content()
    print("PASS: local-path and hardcoded-secret scan")

    verify_attribution()
    print("PASS: Monty Dabas publication attribution")

    run([sys.executable, str(MARKDOWN_CHECKER), "--root", str(REPO_ROOT)])
    print("PASS: Markdown local links and anchors")

    if not args.skip_self_tests:
        for source in SOURCE_FILES:
            run([sys.executable, str(source), "--self-test"])
        print("PASS: executable self-tests")

    print("Public-release offline verification passed.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
