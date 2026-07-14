#!/usr/bin/env python3
"""Generate deterministic release summary tables from tracked evidence.

The command reads only repository-relative evidence certificates and the public
release manifest. It performs no hardware submission and changes no evidence.
"""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path
from typing import Any, Mapping, Sequence

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_EVIDENCE_ROOT = REPO_ROOT / "evidence"


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path.name} must contain a JSON object")
    return data


def finite_number(value: Any, label: str) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{label} is not numeric: {value!r}") from exc
    if number != number or number in (float("inf"), float("-inf")):
        raise ValueError(f"{label} is not finite")
    return number


def build_summary(evidence_root: Path) -> dict[str, Any]:
    evidence_root = evidence_root.expanduser().resolve()
    manifest_path = evidence_root / "provenance" / "evidence_release_manifest.json"
    manifest = load_json(manifest_path)

    runs_record = manifest.get("runs")
    if not isinstance(runs_record, list) or not runs_record:
        raise RuntimeError("Release manifest has no runs list")

    runs: list[dict[str, Any]] = []
    for item in runs_record:
        if not isinstance(item, Mapping):
            raise RuntimeError("Release manifest contains a non-object run entry")
        run_id = str(item.get("public_run_id", "")).strip()
        if not run_id:
            raise RuntimeError("A release-manifest run is missing public_run_id")
        certificate_path = evidence_root / "selected_runs" / run_id / "certificate.json"
        certificate = load_json(certificate_path)
        metrics = certificate.get("primary_metrics")
        if not isinstance(metrics, Mapping):
            raise RuntimeError(f"primary_metrics is missing from {run_id}")
        model_mae = metrics.get("model_mae")
        if not isinstance(model_mae, Mapping):
            raise RuntimeError(f"model_mae is missing from {run_id}")

        runs.append({
            "public_run_id": run_id,
            "backend": str(certificate.get("backend", "")),
            "job_id": str(certificate.get("job_id", "")),
            "created_at_utc": str(certificate.get("created_at_utc", "")),
            "classification": str(certificate.get("classification", "")),
            "raw_results_sha256": str(certificate.get("raw_results_sha256", "")),
            "full_readout_p1": finite_number(
                metrics.get("full_readout_p1"), f"{run_id}.full_readout_p1"
            ),
            "projection_erased_readout_p1": finite_number(
                metrics.get("projection_erased_readout_p1"),
                f"{run_id}.projection_erased_readout_p1",
            ),
            "control_ledger_ceiling": finite_number(
                metrics.get("control_ledger_ceiling"), f"{run_id}.control_ledger_ceiling"
            ),
            "visible_rk_kr_tvd": finite_number(
                metrics.get("visible_rk_kr_tvd"), f"{run_id}.visible_rk_kr_tvd"
            ),
            "reset_signature_spread": finite_number(
                metrics.get("reset_signature_spread"), f"{run_id}.reset_signature_spread"
            ),
            "full_multi_ledger_mae": finite_number(
                model_mae.get("full_multi_ledger"), f"{run_id}.full_multi_ledger_mae"
            ),
            "all_declared_gates_pass": all(
                bool(value)
                for value in certificate.get("pass_gates", {}).values()
            ),
        })

    stability = manifest.get("cross_run_stability")
    if not isinstance(stability, Mapping):
        raise RuntimeError("Release manifest has no cross_run_stability object")

    return {
        "release_candidate": manifest.get("release_candidate"),
        "classification": manifest.get("classification"),
        "run_count": manifest.get("run_count"),
        "passing_run_count": manifest.get("passing_run_count"),
        "backend_count": manifest.get("backend_count"),
        "duplicate_job_ids": manifest.get("duplicate_job_ids"),
        "duplicate_result_hashes": manifest.get("duplicate_result_hashes"),
        "cross_run_stability": stability,
        "runs": runs,
        "scientific_boundary": manifest.get("scientific_boundary"),
    }


def format_number(value: Any) -> str:
    return f"{finite_number(value, 'table value'):.6f}"


def render_markdown(summary: Mapping[str, Any]) -> str:
    lines = [
        "# Release Evidence Summary",
        "",
        f"- Release candidate: `{summary['release_candidate']}`",
        f"- Classification: `{summary['classification']}`",
        f"- Passing runs: `{summary['passing_run_count']}/{summary['run_count']}`",
        f"- Distinct backends: `{summary['backend_count']}`",
        f"- Cross-run stability: `{summary['cross_run_stability']['pass']}`",
        f"- Duplicate job identifiers: `{len(summary['duplicate_job_ids'])}`",
        f"- Duplicate raw-result hashes: `{len(summary['duplicate_result_hashes'])}`",
        "",
        "## Selected runs",
        "",
        "| Run | Backend | Created UTC | Full readout P(1) | Projection-erased P(1) | Control ceiling | Visible RK/KR TVD | Reset spread | Full-model MAE | All gates |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|:---:|",
    ]
    for run in summary["runs"]:
        lines.append(
            "| {public_run_id} | {backend} | {created_at_utc} | {full} | {erased} | "
            "{control} | {visible} | {reset} | {mae} | {gates} |".format(
                public_run_id=run["public_run_id"],
                backend=run["backend"],
                created_at_utc=run["created_at_utc"],
                full=format_number(run["full_readout_p1"]),
                erased=format_number(run["projection_erased_readout_p1"]),
                control=format_number(run["control_ledger_ceiling"]),
                visible=format_number(run["visible_rk_kr_tvd"]),
                reset=format_number(run["reset_signature_spread"]),
                mae=format_number(run["full_multi_ledger_mae"]),
                gates="yes" if run["all_declared_gates_pass"] else "no",
            )
        )

    statistics = summary["cross_run_stability"].get("statistics", {})
    lines.extend([
        "",
        "## Cross-run statistics",
        "",
        "| Statistic | Value |",
        "|---|---:|",
    ])
    for name in sorted(statistics):
        lines.append(f"| `{name}` | {format_number(statistics[name])} |")

    lines.extend([
        "",
        "## Scientific boundary",
        "",
        str(summary["scientific_boundary"]),
        "",
    ])
    return "\n".join(lines)


def self_test() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        evidence = Path(tmp) / "evidence"
        selected = evidence / "selected_runs"
        provenance = evidence / "provenance"
        selected.mkdir(parents=True)
        provenance.mkdir()
        runs = []
        for index in range(3):
            run_id = f"run{index + 1}"
            run_dir = selected / run_id
            run_dir.mkdir()
            certificate = {
                "backend": f"backend_{index + 1}",
                "job_id": f"job_{index + 1}",
                "created_at_utc": f"2026-01-0{index + 1}T00:00:00+00:00",
                "classification": "MULTI_LEDGER_OPERATOR_MEMORY_DECOMPOSITION",
                "raw_results_sha256": str(index + 1) * 64,
                "pass_gates": {"a": True, "b": True},
                "primary_metrics": {
                    "full_readout_p1": 0.97 + index * 0.001,
                    "projection_erased_readout_p1": 0.002,
                    "control_ledger_ceiling": 0.01,
                    "visible_rk_kr_tvd": 0.005,
                    "reset_signature_spread": 0.08,
                    "model_mae": {"full_multi_ledger": 0.03},
                },
            }
            (run_dir / "certificate.json").write_text(
                json.dumps(certificate), encoding="utf-8"
            )
            runs.append({"public_run_id": run_id})
        manifest = {
            "release_candidate": "0.1.0-rc1",
            "classification": "CROSS_BACKEND_REPLICATION",
            "run_count": 3,
            "passing_run_count": 3,
            "backend_count": 3,
            "duplicate_job_ids": [],
            "duplicate_result_hashes": [],
            "cross_run_stability": {
                "pass": True,
                "statistics": {"full_readout_range": 0.002},
            },
            "runs": runs,
            "scientific_boundary": "fixture boundary",
        }
        (provenance / "evidence_release_manifest.json").write_text(
            json.dumps(manifest), encoding="utf-8"
        )
        summary = build_summary(evidence)
        markdown = render_markdown(summary)
        assert summary["run_count"] == 3
        assert "backend_3" in markdown
        assert "full_readout_range" in markdown
    print("Self-test passed: deterministic JSON and Markdown release summaries are generated.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--evidence-root", type=Path, default=DEFAULT_EVIDENCE_ROOT)
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    parser.add_argument("--output", type=Path)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.self_test:
        self_test()
        return 0
    summary = build_summary(args.evidence_root)
    text = (
        render_markdown(summary)
        if args.format == "markdown"
        else json.dumps(summary, indent=2, sort_keys=True) + "\n"
    )
    if args.output is None:
        print(text, end="" if text.endswith("\n") else "\n")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
        print(f"Release summary written to: {args.output}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        raise SystemExit(130)
    except Exception as exc:
        print(f"ERROR: {exc}")
        raise SystemExit(1)
