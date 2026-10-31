# Quantum-Classical Recognition Validation

<!-- patent-status-notice:start -->
> **Patent pending — rights reserved.** The repository owner confirms filed PCT and/or provisional patent applications in the related invention portfolio. This notice applies to subject matter supported by the applicable pending filings. Public disclosure is not intended to waive patent rights. Existing licences and permissions remain effective. See [PATENT_NOTICE.md](PATENT_NOTICE.md).
<!-- patent-status-notice:end -->

> **Research record:** [Dated snapshot, content hashes and archive links](RESEARCH_PROVENANCE.md) · [Canonical repository governance](GOVERNANCE.md). Cite the exact version used.


> **Release status:** bounded public release. The declared three-backend release gate has passed (see Current validation state); the release gates tracked in [`RELEASE_CHECKLIST.md`](RELEASE_CHECKLIST.md) govern any future expansion of scope.
>
> **Patent and rights boundary:** this is a selected technical inspection and citation release. Public visibility will not grant a patent licence or unrestricted software rights. See [`PATENT_NOTICE.md`](PATENT_NOTICE.md), [`LICENSE`](LICENSE), and [`PUBLIC_RELEASE_BOUNDARY.md`](PUBLIC_RELEASE_BOUNDARY.md).

## Purpose

This repository is the bounded public-release package for a quantum-classical projection of the broader EMK / Recognition Calculus programme.

The first release is intentionally narrow. It asks whether a declared quantum circuit can preserve operator-order information in separate memory ledgers while keeping selected visible endpoint distributions nearly matched, and whether those ledgers can be selectively erased and projected into a readout under predeclared tests.

The repository does **not** claim that one circuit proves a universal physical law, validates a fabricated device, establishes a material memory mechanism, demonstrates quantum advantage, or proves thermodynamics from quantum experiments.

## First publication target

The initial release candidate is the **Multi-Ledger Operator-Memory Benchmark v1**. Its public package contains:

- a seven-qubit IBM Quantum benchmark;
- three separately measured operator-order memory ledgers;
- selective-erasure, full-erasure, commuting, order-erased, and projection-erased controls;
- comparison of no-memory, single-ledger, pair-ledger, and full multi-ledger models;
- offline cross-run and cross-backend evaluation;
- machine-readable certificates and SHA-256 manifests;
- self-tests that do not require IBM credentials;
- selected hardware evidence after privacy, provenance, and claim-scope review.

## Current validation state

The committed campaign has passed the declared three-backend release gate:

```text
classification = CROSS_BACKEND_REPLICATION
run_count = 3
passing_run_count = 3
backend_count = 3
backends = ibm_fez, ibm_kingston, ibm_marrakesh
duplicate_job_ids = []
duplicate_result_hashes = []
cross_run_stability.pass = true
```

All six declared per-run gates passed on every backend. The tracked evidence passed manifest verification, exact hash checking, duplicate rejection, sensitive-content scanning, clean-checkout verification, deterministic release-summary generation, and a private public-like rehearsal.

IBM job identifiers are published as provenance because they distinguish independent executions and are not authentication credentials. This is a selected technical inspection and citation release; scope beyond it remains governed by the patent notice and release boundary documents.

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

> Under the declared circuit, controls, metrics, and thresholds, selected IBM Quantum hardware runs support a reproducible cross-backend quantum representation of decomposable operator-order memory with selective ledger erasure, causal projection, reduced-model comparison, and cross-run stability.

A passing result supports the declared **quantum representation**. It does not establish a transistor, material memory, thermodynamic entropy production, quantum computational advantage, or new physical law.

## Repository structure

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
│   ├── REPRODUCIBILITY_PLAN.md
│   ├── ENVIRONMENT.md
│   ├── JUPYTER_TRIPLE_REPLICATION.md
│   ├── EVIDENCE_INTAKE.md
│   └── RELEASE_NOTES_RC1.md
├── src/
├── tools/
├── schemas/
└── evidence/
    ├── provenance/
    ├── selected_runs/
    └── replication/
```

## Publication discipline

Files are transported from the private development repository only after review. The public repository must not contain credentials, local filesystem paths, unpublished patent drafting, device fabrication details, private laboratory mappings, unrelated experiments, unverified outputs, or claims stronger than the included evidence.

Every released evidence file must be referenced by a manifest, tied to a source record, and accompanied by a stated scientific boundary.

## Citation

Citation metadata is maintained in [`CITATION.cff`](CITATION.cff). Cite the exact release tag or commit used.

## Publication author

Monty Dabas, Independent Researcher  
ORCID: 0009-0005-6948-209X
