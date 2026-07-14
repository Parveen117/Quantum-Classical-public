#!/usr/bin/env python3
"""Check repository-local Markdown links and heading anchors offline.

External URLs are reported as skipped because this release verifier is designed
to be deterministic and network-independent.
"""

from __future__ import annotations

import argparse
import re
import tempfile
from pathlib import Path
from typing import Iterable, Sequence
from urllib.parse import unquote

REPO_ROOT = Path(__file__).resolve().parents[1]
LINK_PATTERN = re.compile(r"!?(?:\[[^\]]*\])\(([^)]+)\)")
HEADING_PATTERN = re.compile(r"^(#{1,6})\s+(.+?)\s*#*\s*$")
EXTERNAL_PREFIXES = ("http://", "https://", "mailto:", "tel:")
EXCLUDED_PARTS = {".git", ".venv", "venv", "__pycache__", "intake_staging"}


def markdown_files(root: Path) -> Iterable[Path]:
    for path in sorted(root.rglob("*.md")):
        if path.is_file() and not any(part in EXCLUDED_PARTS for part in path.parts):
            yield path


def github_slug(text: str) -> str:
    value = re.sub(r"<[^>]+>", "", text.strip().lower())
    value = re.sub(r"[^\w\- ]", "", value, flags=re.UNICODE)
    value = re.sub(r"\s+", "-", value)
    value = re.sub(r"-+", "-", value).strip("-")
    return value


def heading_anchors(path: Path) -> set[str]:
    anchors: set[str] = set()
    counts: dict[str, int] = {}
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        match = HEADING_PATTERN.match(line)
        if not match:
            continue
        base = github_slug(match.group(2))
        if not base:
            continue
        count = counts.get(base, 0)
        counts[base] = count + 1
        anchors.add(base if count == 0 else f"{base}-{count}")
    return anchors


def split_target(raw_target: str) -> tuple[str, str]:
    target = raw_target.strip()
    if target.startswith("<") and ">" in target:
        target = target[1:target.index(">")]
    elif " " in target:
        target = target.split(" ", 1)[0]
    target = unquote(target)
    if "#" in target:
        file_part, anchor = target.split("#", 1)
    else:
        file_part, anchor = target, ""
    file_part = file_part.split("?", 1)[0]
    return file_part, anchor.lower()


def check_tree(root: Path) -> dict[str, object]:
    root = root.resolve()
    errors: list[str] = []
    checked_links = 0
    skipped_external = 0
    anchor_cache: dict[Path, set[str]] = {}

    for source in markdown_files(root):
        text = source.read_text(encoding="utf-8", errors="replace")
        for line_number, line in enumerate(text.splitlines(), start=1):
            for match in LINK_PATTERN.finditer(line):
                raw_target = match.group(1).strip()
                if not raw_target:
                    errors.append(f"{source.relative_to(root)}:{line_number}: empty link target")
                    continue
                if raw_target.lower().startswith(EXTERNAL_PREFIXES):
                    skipped_external += 1
                    continue

                file_part, anchor = split_target(raw_target)
                if file_part:
                    destination = (source.parent / file_part).resolve()
                    try:
                        destination.relative_to(root)
                    except ValueError:
                        errors.append(
                            f"{source.relative_to(root)}:{line_number}: link escapes repository: {raw_target}"
                        )
                        continue
                else:
                    destination = source.resolve()

                checked_links += 1
                if not destination.exists():
                    errors.append(
                        f"{source.relative_to(root)}:{line_number}: missing local target: {raw_target}"
                    )
                    continue

                if anchor:
                    anchor_target = destination
                    if destination.is_dir():
                        readme = destination / "README.md"
                        if not readme.is_file():
                            errors.append(
                                f"{source.relative_to(root)}:{line_number}: directory anchor has no README: {raw_target}"
                            )
                            continue
                        anchor_target = readme
                    if anchor_target.suffix.lower() != ".md":
                        errors.append(
                            f"{source.relative_to(root)}:{line_number}: anchor points to non-Markdown file: {raw_target}"
                        )
                        continue
                    if anchor_target not in anchor_cache:
                        anchor_cache[anchor_target] = heading_anchors(anchor_target)
                    if anchor not in anchor_cache[anchor_target]:
                        errors.append(
                            f"{source.relative_to(root)}:{line_number}: missing heading anchor: {raw_target}"
                        )

    return {
        "markdown_file_count": sum(1 for _ in markdown_files(root)),
        "checked_local_links": checked_links,
        "skipped_external_links": skipped_external,
        "errors": errors,
        "pass": not errors,
    }


def self_test() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        docs = root / "docs"
        docs.mkdir()
        (root / "README.md").write_text(
            "# Home\n\n[Guide](docs/guide.md#usage)\n", encoding="utf-8"
        )
        guide = docs / "guide.md"
        guide.write_text("# Guide\n\n## Usage\n", encoding="utf-8")
        passing = check_tree(root)
        assert passing["pass"] is True
        guide.write_text("# Guide\n\n## Different\n", encoding="utf-8")
        failing = check_tree(root)
        assert failing["pass"] is False
        assert any("missing heading anchor" in item for item in failing["errors"])
    print("Self-test passed: local Markdown paths, anchors, and repository escapes are checked.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--root", type=Path, default=REPO_ROOT)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.self_test:
        self_test()
        return 0
    result = check_tree(args.root)
    print(f"Markdown files: {result['markdown_file_count']}")
    print(f"Checked local links: {result['checked_local_links']}")
    print(f"Skipped external links: {result['skipped_external_links']}")
    if result["errors"]:
        for error in result["errors"]:
            print(f"ERROR: {error}")
        return 1
    print("Markdown local-link and anchor verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
