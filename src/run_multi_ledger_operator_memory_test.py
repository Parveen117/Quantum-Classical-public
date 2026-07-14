#!/usr/bin/env python3
"""IBM Quantum benchmark for a decomposable operator-order memory representation.

This public-release version is derived from the private development file
``run_multi_ledger_operator_memory_test.py`` while removing local paths and
making all hardware dependencies lazy. ``--self-test`` never submits a job and
can run without IBM credentials.

Scientific boundary: this benchmark evaluates a declared quantum representation.
It does not establish a fabricated transistor, material memory, thermodynamic
entropy production, quantum advantage, or a new physical law.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import math
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any, Iterable, Mapping, Sequence

PUBLIC_VERSION = "0.1.0-rc1"
PRIVATE_SOURCE_REPOSITORY = "Parveen117/quantum-classical-provisional"
PRIVATE_SOURCE_COMMIT = "fa873e508600f98516642e4a8800829c8497f2b4"
PRIVATE_SOURCE_BLOB_SHA = "00b258eba3bbb0d951ed6ad0a83f7e3b8ec47bc7"

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_ROOT = REPO_ROOT / "evidence" / "generated" / "runs"
DEFAULT_SHOTS = 4096
DEFAULT_CHANNEL = "ibm_quantum_platform"
SEEDS = (11, 29, 47)
TARGETS = (0, 1, 2)
LEDGERS = (3, 4, 5)
READOUT = 6

# Declared benchmark parameters, not physical constants. They sum to pi so the
# ideal three-ledger write has unit readout probability and selective resets
# have distinct ideal signatures.
PROJECTION_WEIGHTS = (3.0 * math.pi / 10.0, math.pi / 3.0, 11.0 * math.pi / 30.0)

MODES = (
    "full_memory",
    "erase_m1",
    "erase_m2",
    "erase_m3",
    "erase_all",
    "projection_erased",
    "single_m1",
    "single_m2",
    "single_m3",
    "commuting_control",
    "order_erased_control",
)
PROJECTION_ACTIVE_MODES = tuple(mode for mode in MODES if mode != "projection_erased")
REQUIRED_PASS_GATES = (
    "hidden_memory",
    "selective_erase",
    "projection_causal",
    "reset_projection",
    "model_comparison",
    "visible_rk_kr_equality",
)


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def installed_version(package: str) -> str | None:
    try:
        return importlib.metadata.version(package)
    except importlib.metadata.PackageNotFoundError:
        return None


def load_qiskit_api() -> tuple[Any, Any, Any, Any]:
    """Load hardware-only dependencies when hardware execution is requested."""
    try:
        from qiskit import QuantumCircuit, transpile
        from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2
    except ImportError as exc:
        raise RuntimeError(
            "Hardware execution requires the optional dependencies 'qiskit' and "
            "'qiskit-ibm-runtime'. Install the release's hardware dependency set."
        ) from exc
    return QuantumCircuit, transpile, QiskitRuntimeService, SamplerV2


def backend_name(backend: Any) -> str:
    value = getattr(backend, "name", "unknown")
    return str(value() if callable(value) else value)


def backend_qubit_count(backend: Any) -> int:
    direct = getattr(backend, "num_qubits", None)
    if direct is not None:
        return int(direct)
    configuration = getattr(backend, "configuration", None)
    if callable(configuration):
        return int(getattr(configuration(), "n_qubits", 0))
    return 0


def select_backend(service: Any, requested_name: str | None) -> Any:
    if requested_name:
        return service.backend(requested_name)
    candidates = [
        backend
        for backend in service.backends(simulator=False, operational=True)
        if backend_qubit_count(backend) >= 7
    ]
    if not candidates:
        raise RuntimeError("No operational IBM backend with at least seven qubits is available.")
    return min(candidates, key=lambda backend: backend.status().pending_jobs)


def counts_from_pub_result(pub_result: Any) -> dict[str, int]:
    data = pub_result.data
    for name in ("c", "meas"):
        register = getattr(data, name, None)
        if register is not None and hasattr(register, "get_counts"):
            return {str(key): int(value) for key, value in register.get_counts().items()}
    for value in vars(data).values():
        if hasattr(value, "get_counts"):
            return {str(key): int(count) for key, count in value.get_counts().items()}
    raise RuntimeError("Could not locate measurement counts in the Sampler result.")


def normalized_bits(bits: str) -> str:
    compact = bits.replace(" ", "")
    if len(compact) != 7 or any(bit not in "01" for bit in compact):
        raise ValueError(f"Expected a seven-bit result, received {bits!r}")
    return compact


def classical_bit_value(bits: str, classical_bit: int) -> int:
    if not 0 <= classical_bit < 7:
        raise ValueError(f"Classical bit index out of range: {classical_bit}")
    return int(normalized_bits(bits)[6 - classical_bit])


def bit_probability(counts: Mapping[str, int], classical_bit: int) -> float:
    total = sum(int(value) for value in counts.values())
    if total <= 0:
        return 0.0
    return sum(
        int(count)
        for bits, count in counts.items()
        if classical_bit_value(bits, classical_bit) == 1
    ) / total


def ledger_distribution(counts: Mapping[str, int]) -> dict[str, float]:
    total = sum(int(value) for value in counts.values())
    distribution = {f"{value:03b}": 0.0 for value in range(8)}
    if total <= 0:
        return distribution
    for bits, count in counts.items():
        pattern = "".join(str(classical_bit_value(bits, ledger)) for ledger in LEDGERS)
        distribution[pattern] += int(count) / total
    return distribution


def visible_distribution(counts: Mapping[str, int]) -> dict[str, float]:
    total = sum(int(value) for value in counts.values())
    distribution = {f"{value:03b}": 0.0 for value in range(8)}
    if total <= 0:
        return distribution
    for bits, count in counts.items():
        pattern = "".join(str(classical_bit_value(bits, target)) for target in TARGETS)
        distribution[pattern] += int(count) / total
    return distribution


def total_variation_distance(left: Mapping[str, float], right: Mapping[str, float]) -> float:
    keys = set(left) | set(right)
    return 0.5 * sum(abs(float(left.get(key, 0.0)) - float(right.get(key, 0.0))) for key in keys)


def mode_ledger_kinds(mode: str) -> tuple[str, str, str]:
    if mode in {"full_memory", "erase_m1", "erase_m2", "erase_m3", "erase_all", "projection_erased"}:
        return ("anticommuting", "anticommuting", "anticommuting")
    if mode == "single_m1":
        return ("anticommuting", "disabled", "disabled")
    if mode == "single_m2":
        return ("disabled", "anticommuting", "disabled")
    if mode == "single_m3":
        return ("disabled", "disabled", "anticommuting")
    if mode == "commuting_control":
        return ("commuting", "commuting", "commuting")
    if mode == "order_erased_control":
        return ("order_erased", "order_erased", "order_erased")
    raise ValueError(f"Unknown mode: {mode}")


def apply_branch_x(qc: Any, control: int, target: int, branch: int) -> None:
    if branch == 0:
        qc.x(control)
    qc.cx(control, target)
    if branch == 0:
        qc.x(control)


def apply_branch_z(qc: Any, control: int, target: int, branch: int) -> None:
    if branch == 0:
        qc.x(control)
    qc.cz(control, target)
    if branch == 0:
        qc.x(control)


def write_order_ledger(qc: Any, ledger: int, target: int, kind: str) -> None:
    if kind == "disabled":
        return
    qc.h(ledger)
    if kind == "anticommuting":
        apply_branch_x(qc, ledger, target, 0)
        apply_branch_z(qc, ledger, target, 1)
        apply_branch_z(qc, ledger, target, 0)
        apply_branch_x(qc, ledger, target, 1)
    elif kind == "commuting":
        apply_branch_x(qc, ledger, target, 0)
        apply_branch_x(qc, ledger, target, 1)
        apply_branch_x(qc, ledger, target, 0)
        apply_branch_x(qc, ledger, target, 1)
    elif kind == "order_erased":
        apply_branch_x(qc, ledger, target, 0)
        apply_branch_x(qc, ledger, target, 1)
        apply_branch_z(qc, ledger, target, 0)
        apply_branch_z(qc, ledger, target, 1)
    else:
        raise ValueError(f"Unknown ledger kind: {kind}")
    qc.h(ledger)


def initialise_targets(qc: Any) -> None:
    qc.h(TARGETS[0])
    qc.ry(0.43, TARGETS[1])
    qc.h(TARGETS[2])
    qc.rz(0.27, TARGETS[2])


def build_memory_circuit(mode: str, quantum_circuit_class: Any) -> Any:
    qc = quantum_circuit_class(7, 7, name=mode)
    initialise_targets(qc)
    for target, ledger, kind in zip(TARGETS, LEDGERS, mode_ledger_kinds(mode)):
        write_order_ledger(qc, ledger, target, kind)
    if mode == "erase_m1":
        qc.reset(LEDGERS[0])
    elif mode == "erase_m2":
        qc.reset(LEDGERS[1])
    elif mode == "erase_m3":
        qc.reset(LEDGERS[2])
    elif mode == "erase_all":
        for ledger in LEDGERS:
            qc.reset(ledger)
    if mode != "projection_erased":
        for ledger, weight in zip(LEDGERS, PROJECTION_WEIGHTS):
            qc.cry(weight, ledger, READOUT)
    qc.measure(range(7), range(7))
    return qc


def build_visible_order_circuit(order: str, quantum_circuit_class: Any) -> Any:
    qc = quantum_circuit_class(7, 7, name=f"visible_{order}")
    initialise_targets(qc)
    for target in TARGETS:
        if order == "rk":
            qc.x(target)
            qc.z(target)
        elif order == "kr":
            qc.z(target)
            qc.x(target)
        else:
            raise ValueError(f"Unknown visible order: {order}")
    qc.measure(range(7), range(7))
    return qc


def projection_probability(pattern: str, active_indices: Iterable[int]) -> float:
    if len(pattern) != 3 or any(bit not in "01" for bit in pattern):
        raise ValueError(f"Invalid ledger pattern: {pattern!r}")
    active = set(active_indices)
    if any(index not in {0, 1, 2} for index in active):
        raise ValueError(f"Invalid active ledger indices: {sorted(active)}")
    angle = sum(
        PROJECTION_WEIGHTS[index]
        for index, bit in enumerate(pattern)
        if index in active and bit == "1"
    )
    return math.sin(angle / 2.0) ** 2


def predict_from_distribution(distribution: Mapping[str, float], active_indices: Sequence[int]) -> float:
    return sum(
        float(probability) * projection_probability(pattern, active_indices)
        for pattern, probability in distribution.items()
    )


def mean_absolute_error(observed: Sequence[float], predicted: Sequence[float]) -> float:
    if len(observed) != len(predicted):
        raise ValueError("Observed and predicted lengths differ.")
    return mean(abs(left - right) for left, right in zip(observed, predicted)) if observed else 0.0


def ideal_reset_readout_probabilities() -> dict[str, float]:
    return {
        "full_memory": math.sin(sum(PROJECTION_WEIGHTS) / 2.0) ** 2,
        "erase_m1": math.sin(sum(PROJECTION_WEIGHTS[1:]) / 2.0) ** 2,
        "erase_m2": math.sin((PROJECTION_WEIGHTS[0] + PROJECTION_WEIGHTS[2]) / 2.0) ** 2,
        "erase_m3": math.sin(sum(PROJECTION_WEIGHTS[:2]) / 2.0) ** 2,
        "erase_all": 0.0,
    }


def self_test() -> None:
    if not math.isclose(sum(PROJECTION_WEIGHTS), math.pi, rel_tol=0.0, abs_tol=1e-12):
        raise AssertionError("Projection weights must sum to pi.")
    ideals = ideal_reset_readout_probabilities()
    if ideals["full_memory"] < 0.999:
        raise AssertionError("Full-memory ideal readout should be one.")
    reset_values = [ideals["erase_m1"], ideals["erase_m2"], ideals["erase_m3"]]
    if min(abs(a - b) for i, a in enumerate(reset_values) for b in reset_values[i + 1 :]) < 0.03:
        raise AssertionError("Selective-reset signatures are not distinguishable.")
    if set(MODES) != set(PROJECTION_ACTIVE_MODES) | {"projection_erased"}:
        raise AssertionError("Projection-active mode registration is inconsistent.")
    for mode in MODES:
        kinds = mode_ledger_kinds(mode)
        if len(kinds) != 3:
            raise AssertionError(f"Mode {mode} does not define three ledgers.")
    synthetic_counts = {"1111111": 3, "0000000": 1}
    if not math.isclose(bit_probability(synthetic_counts, 6), 0.75):
        raise AssertionError("Bit-probability extraction failed.")
    if not math.isclose(sum(ledger_distribution(synthetic_counts).values()), 1.0):
        raise AssertionError("Ledger distribution is not normalized.")
    try:
        QuantumCircuit, _, _, _ = load_qiskit_api()
    except RuntimeError:
        qiskit_status = "not installed; pure self-tests passed"
    else:
        for mode in MODES:
            circuit = build_memory_circuit(mode, QuantumCircuit)
            if circuit.num_qubits != 7 or circuit.num_clbits != 7:
                raise AssertionError(f"Unexpected circuit width for {mode}.")
        for order in ("rk", "kr"):
            circuit = build_visible_order_circuit(order, QuantumCircuit)
            if circuit.num_qubits != 7 or circuit.num_clbits != 7:
                raise AssertionError(f"Unexpected visible circuit width for {order}.")
        qiskit_status = "installed; circuit-construction tests passed"
    print("Self-test passed: ledger modes, projection invariants, distributions, and reset signatures are valid.")
    print(f"Qiskit status: {qiskit_status}")
    print(json.dumps(ideals, indent=2, sort_keys=True))


def summarize_records(records: Sequence[Mapping[str, Any]]) -> tuple[dict[str, Any], dict[str, Any]]:
    memory_records = [record for record in records if record["experiment_family"] == "memory_decomposition"]
    visible_records = [record for record in records if record["experiment_family"] == "visible_order_equality"]

    def records_for_mode(mode: str) -> list[Mapping[str, Any]]:
        group = [record for record in memory_records if record["mode"] == mode]
        if len(group) != len(SEEDS):
            raise ValueError(f"Mode {mode} has {len(group)} records; expected {len(SEEDS)}.")
        return group

    summaries: dict[str, Any] = {}
    for mode in MODES:
        group = records_for_mode(mode)
        summaries[mode] = {
            "ledger_p1": [mean(float(record["ledger_p1"][i]) for record in group) for i in range(3)],
            "readout_p1": mean(float(record["readout_p1"]) for record in group),
            "ledger_distribution": {
                pattern: mean(float(record["ledger_distribution"][pattern]) for record in group)
                for pattern in {f"{value:03b}" for value in range(8)}
            },
        }

    visible_by_order: dict[str, dict[str, float]] = {}
    for order in ("rk", "kr"):
        group = [record for record in visible_records if record["order"] == order]
        if len(group) != len(SEEDS):
            raise ValueError(f"Visible order {order} has {len(group)} records; expected {len(SEEDS)}.")
        visible_by_order[order] = {
            pattern: mean(float(record["visible_distribution"][pattern]) for record in group)
            for pattern in {f"{value:03b}" for value in range(8)}
        }
    return summaries, visible_by_order


def evaluate_summaries(summaries: Mapping[str, Any], visible_by_order: Mapping[str, Mapping[str, float]]) -> dict[str, Any]:
    visible_tvd = total_variation_distance(visible_by_order["rk"], visible_by_order["kr"])
    full_ledgers = list(summaries["full_memory"]["ledger_p1"])
    control_ceiling = max(
        max(summaries["commuting_control"]["ledger_p1"]),
        max(summaries["order_erased_control"]["ledger_p1"]),
    )
    hidden_memory_pass = min(full_ledgers) > 0.70 and control_ceiling < 0.30

    selective_details: dict[str, Any] = {}
    selective_checks: list[bool] = []
    for index, mode in enumerate(("erase_m1", "erase_m2", "erase_m3")):
        ledger_means = list(summaries[mode]["ledger_p1"])
        erased_low = ledger_means[index] < 0.30
        untouched_high = min(value for i, value in enumerate(ledger_means) if i != index) > 0.60
        selective_checks.extend((erased_low, untouched_high))
        selective_details[mode] = {
            "ledger_p1": ledger_means,
            "erased_channel_low": erased_low,
            "untouched_channels_high": untouched_high,
            "readout_p1": summaries[mode]["readout_p1"],
        }
    selective_checks.append(max(summaries["erase_all"]["ledger_p1"]) < 0.30)
    selective_erase_pass = all(selective_checks)

    projection_erased = summaries["projection_erased"]
    projection_causal_pass = (
        min(projection_erased["ledger_p1"]) > 0.60
        and projection_erased["readout_p1"] < 0.30
        and summaries["full_memory"]["readout_p1"] > 0.65
    )
    reset_readouts = [summaries[mode]["readout_p1"] for mode in ("erase_m1", "erase_m2", "erase_m3")]
    reset_signature_spread = max(reset_readouts) - min(reset_readouts)
    reset_projection_pass = (
        all(summaries["full_memory"]["readout_p1"] - value > 0.05 for value in reset_readouts)
        and reset_signature_spread > 0.025
    )

    model_rows: list[dict[str, float | str]] = []
    for mode in PROJECTION_ACTIVE_MODES:
        distribution = summaries[mode]["ledger_distribution"]
        observed = float(summaries[mode]["readout_p1"])
        model_rows.append(
            {
                "mode": mode,
                "observed": observed,
                "no_memory": 0.0,
                "single_m1": predict_from_distribution(distribution, (0,)),
                "single_m2": predict_from_distribution(distribution, (1,)),
                "single_m3": predict_from_distribution(distribution, (2,)),
                "pair_m12": predict_from_distribution(distribution, (0, 1)),
                "pair_m13": predict_from_distribution(distribution, (0, 2)),
                "pair_m23": predict_from_distribution(distribution, (1, 2)),
                "full_multi_ledger": predict_from_distribution(distribution, (0, 1, 2)),
            }
        )
    observed_values = [float(row["observed"]) for row in model_rows]
    model_keys = ("no_memory", "single_m1", "single_m2", "single_m3", "pair_m12", "pair_m13", "pair_m23", "full_multi_ledger")
    model_errors = {
        key: mean_absolute_error(observed_values, [float(row[key]) for row in model_rows])
        for key in model_keys
    }
    full_error = model_errors["full_multi_ledger"]
    best_single = min(model_errors[key] for key in ("single_m1", "single_m2", "single_m3"))
    best_pair = min(model_errors[key] for key in ("pair_m12", "pair_m13", "pair_m23"))
    model_comparison_pass = (
        full_error + 0.02 < best_single
        and full_error <= best_pair + 0.02
        and full_error < model_errors["no_memory"]
        and full_error < 0.20
    )
    pass_gates = {
        "hidden_memory": hidden_memory_pass,
        "selective_erase": selective_erase_pass,
        "projection_causal": projection_causal_pass,
        "reset_projection": reset_projection_pass,
        "model_comparison": model_comparison_pass,
        "visible_rk_kr_equality": visible_tvd < 0.08,
    }
    if all(pass_gates.values()):
        classification = "MULTI_LEDGER_OPERATOR_MEMORY_DECOMPOSITION"
    elif hidden_memory_pass and selective_erase_pass and pass_gates["visible_rk_kr_equality"]:
        classification = "HIDDEN_MULTI_LEDGER_MEMORY_WITHOUT_RELIABLE_PROJECTION"
    else:
        classification = "NO_REPRODUCIBLE_MULTI_LEDGER_MEMORY"
    return {
        "classification": classification,
        "pass_gates": pass_gates,
        "primary_metrics": {
            "full_ledger_p1": full_ledgers,
            "control_ledger_ceiling": control_ceiling,
            "full_readout_p1": summaries["full_memory"]["readout_p1"],
            "projection_erased_readout_p1": projection_erased["readout_p1"],
            "reset_readout_values": reset_readouts,
            "reset_signature_spread": reset_signature_spread,
            "visible_rk_kr_tvd": visible_tvd,
            "model_mae": model_errors,
        },
        "selective_erase_details": selective_details,
        "model_rows": model_rows,
    }


def run_hardware(args: argparse.Namespace) -> int:
    QuantumCircuit, transpile, QiskitRuntimeService, SamplerV2 = load_qiskit_api()
    shots = int(args.shots)
    if shots <= 0:
        raise ValueError("Shot count must be positive.")
    output_root = Path(args.output_root).resolve()
    out = output_root / utc_stamp()
    out.mkdir(parents=True, exist_ok=False)

    service_kwargs: dict[str, Any] = {"channel": args.channel}
    if args.instance:
        service_kwargs["instance"] = args.instance
    service = QiskitRuntimeService(**service_kwargs)
    backend = select_backend(service, args.backend)

    pubs: list[Any] = []
    metadata: list[dict[str, Any]] = []
    for mode in MODES:
        logical = build_memory_circuit(mode, QuantumCircuit)
        for seed in SEEDS:
            compiled = transpile(logical, backend=backend, optimization_level=3, seed_transpiler=seed)
            pubs.append(compiled)
            metadata.append({
                "experiment_family": "memory_decomposition",
                "mode": mode,
                "seed_transpiler": seed,
                "depth": compiled.depth(),
                "two_qubit_ops": sum(
                    count for gate_name, count in compiled.count_ops().items()
                    if gate_name in {"cx", "cz", "ecr", "rzz", "crx", "cry", "crz"}
                ),
            })
    for order in ("rk", "kr"):
        logical = build_visible_order_circuit(order, QuantumCircuit)
        for seed in SEEDS:
            compiled = transpile(logical, backend=backend, optimization_level=3, seed_transpiler=seed)
            pubs.append(compiled)
            metadata.append({
                "experiment_family": "visible_order_equality",
                "order": order,
                "seed_transpiler": seed,
                "depth": compiled.depth(),
                "two_qubit_ops": sum(
                    count for gate_name, count in compiled.count_ops().items()
                    if gate_name in {"cx", "cz", "ecr", "rzz", "crx", "cry", "crz"}
                ),
            })

    sampler = SamplerV2(mode=backend)
    job = sampler.run(pubs, shots=shots)
    result = job.result()
    records: list[dict[str, Any]] = []
    for meta, pub_result in zip(metadata, result):
        counts = counts_from_pub_result(pub_result)
        record = dict(meta)
        record["counts"] = counts
        if meta["experiment_family"] == "memory_decomposition":
            record["ledger_p1"] = [bit_probability(counts, ledger) for ledger in LEDGERS]
            record["readout_p1"] = bit_probability(counts, READOUT)
            record["ledger_distribution"] = ledger_distribution(counts)
        else:
            record["visible_distribution"] = visible_distribution(counts)
        records.append(record)

    raw_path = out / "results.json"
    raw_path.write_text(json.dumps(records, indent=2, sort_keys=True), encoding="utf-8")
    summaries, visible_by_order = summarize_records(records)
    evaluation = evaluate_summaries(summaries, visible_by_order)
    certificate = {
        "schema": "MULTI_LEDGER_OPERATOR_MEMORY_CERTIFICATE_V1",
        "benchmark_version": PUBLIC_VERSION,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "backend": backend_name(backend),
        "job_id": str(job.job_id()),
        "shots_per_circuit": shots,
        "transpiler_seeds": list(SEEDS),
        "operator_definition": {"R": "X", "K": "Z", "relation": "RK=-KR"},
        "projection_weights_radians": list(PROJECTION_WEIGHTS),
        "classification": evaluation["classification"],
        "pass_gates": evaluation["pass_gates"],
        "primary_metrics": evaluation["primary_metrics"],
        "selective_erase_details": evaluation["selective_erase_details"],
        "summary": summaries,
        "model_rows": evaluation["model_rows"],
        "visible_distributions": visible_by_order,
        "software": {
            "python": sys.version.split()[0],
            "qiskit": installed_version("qiskit"),
            "qiskit_ibm_runtime": installed_version("qiskit-ibm-runtime"),
            "public_runner_sha256": sha256_file(Path(__file__).resolve()),
        },
        "source_provenance": {
            "private_repository": PRIVATE_SOURCE_REPOSITORY,
            "private_commit": PRIVATE_SOURCE_COMMIT,
            "private_blob_sha": PRIVATE_SOURCE_BLOB_SHA,
        },
        "scientific_boundary": (
            "This benchmark tests a quantum representation of decomposable operator-order memory, "
            "selective ledger erasure, and declared memory-to-readout projection. It does not establish "
            "a fabricated transistor, a material memory effect, thermodynamic entropy production, "
            "quantum advantage, or a new physical law."
        ),
        "raw_results_sha256": sha256_file(raw_path),
    }
    cert_path = out / "certificate.json"
    cert_path.write_text(json.dumps(certificate, indent=2, sort_keys=True), encoding="utf-8")
    summary_lines = [
        "# Multi-Ledger Operator-Memory Benchmark v1",
        "",
        f"- Classification: `{certificate['classification']}`",
        f"- Backend: `{certificate['backend']}`",
        f"- Job ID: `{certificate['job_id']}`",
        *[f"- {gate.replace('_', ' ').title()}: `{value}`" for gate, value in certificate["pass_gates"].items()],
        "",
        "The benchmark is a quantum representation test, not physical device validation.",
    ]
    summary_path = out / "summary.md"
    summary_path.write_text("\n".join(summary_lines) + "\n", encoding="utf-8")
    manifest = {
        "schema": "MULTI_LEDGER_OPERATOR_MEMORY_MANIFEST_V1",
        "benchmark_version": PUBLIC_VERSION,
        "backend": certificate["backend"],
        "job_id": certificate["job_id"],
        "files": {
            raw_path.name: sha256_file(raw_path),
            cert_path.name: sha256_file(cert_path),
            summary_path.name: sha256_file(summary_path),
        },
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(certificate, indent=2, sort_keys=True))
    print(f"\nEvidence written to: {out}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true", help="Run offline invariant tests only.")
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
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
    return run_hardware(args)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        raise SystemExit(130)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
