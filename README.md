# Quantum-Classical Recognition Validation

> **Release status:** private publication-staging repository. This repository is not ready for public release until every gate in [`RELEASE_CHECKLIST.md`](RELEASE_CHECKLIST.md) is closed.
>
> **Patent and rights boundary:** this is a selected technical inspection and citation release. Public visibility will not grant a patent licence or unrestricted software rights. See [`PATENT_NOTICE.md`](PATENT_NOTICE.md), [`LICENSE`](LICENSE), and [`PUBLIC_RELEASE_BOUNDARY.md`](PUBLIC_RELEASE_BOUNDARY.md).

## Purpose

This repository is the bounded public-release package for a quantum-classical projection of the broader EMK / Recognition Calculus programme.

The first release is intentionally narrow. It asks whether a declared quantum circuit can preserve operator-order information in separate memory ledgers while keeping selected visible endpoint distributions nearly matched, and whether those ledgers can be selectively erased and projected into a readout under predeclared tests.

The repository does **not** claim that one circuit proves a universal physical law, validates a fabricated device, establishes a material memory mechanism, demonstrates quantum advantage, or proves thermodynamics from quantum experiments.

## First publication target

The initial release candidate is the **Multi-Ledger Operator-Memory Benchmark v1**. Its public package is planned to contain:

- a seven-qubit IBM Quantum benchmark;
- three separately measured operator-order memory ledgers;
- selective-erasure, full-erasure, commuting, order-erased, and projection-erased controls;
- comparison of no-memory, single-ledger, pair-ledger, and full multi-ledger models;
- offline cross-run and cross-backend evaluation;
- machine-readable certificates and SHA-256 manifests;
- self-tests that do not require IBM credentials;
- selected hardware evidence only after privacy, provenance, patent, and claim-scope review.

## Scientific levels

| Level | Meaning in this repository |
|---|---|
| Definition | A state, operator, residue, invariant, gate, or certificate is explicitly introduced. |
| Derivation | A result follows from declared assumptions and equations. |
| Computational verification | Code or tests confirm a result for specified circuits, simulators, datasets, or backends. |
| Hardware observation | A named physical backend returned an observed distribution under a declared protocol. |
| Physical validation | Independent observations support a physical mechanism or device claim within stated uncertainty. |

A computational certificate or hardware run is evidence relative to its circuit, backend, sampling count, calibration context, metric, and tolerance. It is not automatically proof of a universal law.

## Core public claim boundary

The strongest intended first-release statement is:

> Under the declared circuit, controls, metrics, and thresholds, selected IBM Quantum hardware runs can be evaluated for a decomposable operator-order memory representation with selective ledger erasure, causal projection, reduced-model comparison, and cross-run stability.

A passing result supports the declared **quantum representation**. It does not establish a transistor, material memory, thermodynamic entropy production, quantum computational advantage, or new physical law.

## Planned repository structure

```text
.
├── README.md
├── RELEASE_CHECKLIST.md
├── TRANSFER_MANIFEST.md
├── PUBLIC_RELEASE_BOUNDARY.md
├── PATENT_NOTICE.md
├── LICENSE
├── CITATION.cff
├── docs/
│   ├── FRAMEWORK.md
│   ├── CLAIM_SCOPE.md
│   ├── MULTI_LEDGER_OPERATOR_MEMORY_TEST.md
│   └── REPRODUCIBILITY_PLAN.md
├── src/
├── tests/
├── schemas/
└── evidence/
    ├── manifests/
    ├── certificates/
    └── selected_runs/
```

## Publication discipline

Files are transported from the private development repository only after review. The public repository must not contain credentials, local filesystem paths, unpublished patent drafting, device fabrication details, private laboratory mappings, unrelated experiments, unverified outputs, or claims stronger than the included evidence.

Every released evidence file must be referenced by a manifest, tied to a source commit, and accompanied by a stated scientific boundary.

## Citation

Citation metadata will be finalized in [`CITATION.cff`](CITATION.cff) at the first tagged release. Cite the exact release tag or commit used.

## Author

Monty Dabas, Independent Researcher  
ORCID: 0009-0005-6948-209X
