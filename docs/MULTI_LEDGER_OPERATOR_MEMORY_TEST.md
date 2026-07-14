# Multi-Ledger Operator-Memory Benchmark v1

## Purpose

This benchmark tests a quantum representation with:

- three separately measurable memory ledgers;
- selective reset of each ledger;
- full ledger erasure;
- a projection-erased control;
- commuting and order-erased controls;
- selected visible RK/KR endpoint comparison;
- no-memory, single-ledger, pair-ledger, and full multi-ledger projection models.

The benchmark is a quantum representation test. It is not physical transistor, material, thermodynamic, or universal-law validation.

## Operator core

The declared operators are

```text
R = X
K = Z
RK = -KR
```

Each ledger interferometer places RK on one branch and KR on the other. In the ideal declared construction, the selected visible target agrees up to global phase while the relative branch sign is converted into a ledger-qubit outcome.

## Qubit map

```text
q0 q1 q2 = visible target registers
q3 q4 q5 = memory ledgers M1 M2 M3
q6       = projection/readout register
```

## Test modes

```text
full_memory
erase_m1
erase_m2
erase_m3
erase_all
projection_erased
single_m1
single_m2
single_m3
commuting_control
order_erased_control
visible_rk
visible_kr
```

## Projection

The readout weights are declared before execution and sum to pi. They are selected to produce distinguishable ideal selective-reset signatures. They are benchmark parameters, not asserted physical constants.

The initial source implementation uses

\[
w_1=\frac{3\pi}{10},\qquad
w_2=\frac{\pi}{3},\qquad
w_3=\frac{11\pi}{30},
\]

so that

\[
w_1+w_2+w_3=\pi.
\]

The readout model must be published before the selected hardware evidence is evaluated.

## Required pass gates

A full run classification requires all of the following:

1. **hidden memory:** all three ledgers distinguish anticommuting order from declared controls;
2. **selective erase:** resetting one ledger suppresses that ledger while preserving the other two within threshold;
3. **projection causal:** the projection-erased condition retains ledger evidence while suppressing the declared readout;
4. **reset projection:** selective resets produce distinguishable readout changes;
5. **model comparison:** the full multi-ledger model outperforms declared reduced models under the registered metric;
6. **visible RK/KR equality gate:** selected visible RK and KR endpoint distributions remain within the declared distance threshold.

## Run classifications

```text
MULTI_LEDGER_OPERATOR_MEMORY_DECOMPOSITION
HIDDEN_MULTI_LEDGER_MEMORY_WITHOUT_RELIABLE_PROJECTION
NO_REPRODUCIBLE_MULTI_LEDGER_MEMORY
```

A scientifically negative classification can still mean that the hardware execution completed successfully. Runtime, authentication, dependency, service, parsing, or manifest failures must return a nonzero process status and must not be converted into a scientific negative result.

## Evidence bundle

Each hardware run must produce

```text
results.json
certificate.json
summary.md
manifest.json
```

The manifest must provide SHA-256 hashes for every declared payload file. The certificate must identify the backend, execution identifier or approved public alias, sample count, operator definition, pass gates, primary metrics, raw-result hash, software revision, and scientific boundary.

## Cross-run replication

The public evaluator must:

- require at least two passing runs;
- require at least two distinct backends for a cross-backend classification;
- reject duplicate job identifiers;
- reject duplicate raw-result hashes;
- verify all run manifests;
- re-evaluate fixed per-run metric gates;
- evaluate fixed cross-run stability gates;
- write a replication certificate, summary, and manifest.

Thresholds must be versioned. Changing a threshold after examining selected evidence requires a new benchmark version and an explicit explanation.

## Public execution interface

The benchmark runner is intended to use environment variables rather than hardcoded credentials:

```text
IBM_QUANTUM_BACKEND
IBM_QUANTUM_SHOTS
IBM_QUANTUM_CHANNEL
IBM_QUANTUM_INSTANCE
```

No IBM token, saved-account file, private instance identifier, or local machine path may be committed.

Planned commands:

```bash
python src/run_multi_ledger_operator_memory_test.py --self-test
python src/run_multi_ledger_operator_memory_test.py
python src/evaluate_multi_ledger_replication.py --self-test
python src/evaluate_multi_ledger_replication.py
```

The first two non-credentialed self-tests must pass in a clean environment before public release. Hardware execution naturally requires the user's own authorised IBM Quantum account and remains subject to IBM's terms and availability.

## Scientific boundary

This benchmark can test whether selected IBM hardware observations support a decomposable quantum operator-order memory representation with causal selective erasure, declared projection, reduced-model comparison, and fixed replication gates.

It cannot by itself establish a fabricated transistor, a material memory mechanism, irreversible thermodynamic erasure, quantum advantage, fault tolerance, or a new physical law.
