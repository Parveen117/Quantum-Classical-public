# Reproducibility Plan

## Objective

A reviewer should be able to verify the released code, controls, evidence integrity, run classifications, and cross-run certificate without access to the private development repository and without trusting a manually prepared summary.

## Reproducibility layers

### Layer 1: source self-tests

The public runner and evaluator must each expose a deterministic `--self-test` mode that:

- does not require IBM credentials;
- does not submit a hardware job;
- checks circuit width and declared modes;
- checks projection-weight invariants;
- checks distinguishable ideal reset signatures;
- checks certificate and manifest generation on fixtures;
- fails with a nonzero process status when an invariant is broken.

### Layer 2: offline evidence verification

A single command must:

1. enumerate selected run bundles;
2. validate each manifest and SHA-256 hash;
3. parse each run certificate;
4. recompute all declared per-run gates;
5. reject duplicate execution identifiers and raw-result hashes;
6. recompute cross-run stability statistics;
7. reproduce the replication certificate and summary;
8. compare regenerated hashes with the released records.

No IBM access should be required for this layer.

### Layer 3: summary regeneration

Tables and figures in the README, manuscript, or release notes must be generated from released machine-readable evidence. Hand-entered metrics may be explanatory, but they must not be the sole source of a public numerical claim.

### Layer 4: optional hardware rerun

An authorised user may execute the benchmark on an available IBM backend using their own account. A hardware rerun is not expected to reproduce identical bit counts. It should be evaluated under the same versioned gates and must preserve the full execution context needed for interpretation.

## Environment declaration

Before release, the repository must declare:

- supported Python version;
- tested Qiskit version range;
- tested `qiskit-ibm-runtime` version range;
- operating-system notes, if material;
- dependency installation command;
- self-test command;
- offline verification command;
- optional hardware execution command.

Dependency bounds must be derived from a tested clean environment, not guessed from whichever package versions happen to inhabit the development machine.

## Evidence provenance

Each public evidence bundle must record:

- private source repository and commit SHA in the internal provenance map;
- public release commit SHA;
- execution timestamp;
- backend identifier or documented public alias;
- execution identifier or documented public alias;
- number of shots;
- circuit and transpilation context available from the source record;
- software versions;
- raw-result SHA-256;
- certificate and manifest hashes;
- declared thresholds and benchmark version;
- scientific boundary.

If an identifier is pseudonymised for privacy, the public record must say so. The private repository must preserve the mapping and the unmodified source evidence.

## Selection policy

Selected runs must not be chosen only because they are visually attractive or support the preferred conclusion. The release must state:

- the eligible run population;
- inclusion and exclusion rules;
- failed runs and failure categories at an aggregate level;
- whether thresholds were fixed before the selected runs;
- whether any reruns occurred and why.

## Negative controls

The public package must include the declared commuting, order-erased, full-erasure, and projection-erased controls. At least one deterministic false or corrupted fixture should demonstrate that the offline evaluator rejects invalid evidence.

## Expected limitations

Hardware reruns may differ because of backend availability, calibration, transpilation, queueing, SDK changes, and finite-shot variation. Reproducibility therefore means that the released evidence is auditable and that new runs are judged by the same declared procedure, not that every backend returns identical counts forever. Even qubits refuse that level of bureaucratic obedience.

## Release verification record

The tagged release must include or link to a record containing:

```text
release tag
release commit SHA
Python and dependency versions
self-test result
selected evidence directories
run manifest hashes
replication manifest hash
regenerated certificate hash
secret-scan result
personal-information scan result
known limitations
```
