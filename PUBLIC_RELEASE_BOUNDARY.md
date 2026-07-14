# Public Release Boundary

## Public purpose

`Parveen117/Quantum-Classical` is a bounded technical inspection, reproducibility, scholarly discussion, and citation package. It is not a mirror of the private development repository.

The first public release is limited to a declared quantum benchmark, its controls, offline evaluation, selected evidence, manifests, certificates, and documentation necessary to understand and test the bounded claim.

## Included public layer

The initial release may include:

- the quantum-classical state, seam, residue, and closure definitions needed to interpret the benchmark;
- the Multi-Ledger Operator-Memory Benchmark v1 circuit and declared readout model;
- selective-erasure, full-erasure, projection-erased, commuting, order-erased, and visible-order controls;
- predeclared per-run and cross-run evaluation thresholds;
- no-memory, single-ledger, pair-ledger, and full multi-ledger model comparisons;
- self-tests and deterministic fixtures;
- selected IBM Quantum hardware observations after review;
- hashes, manifests, certificates, provenance records, and exact source revisions;
- limitations and falsification conditions.

## Excluded private layer

The public repository deliberately excludes:

- the complete `quantum-classical-provisional` development history;
- credentials, saved IBM accounts, access tokens, account metadata, private instances, and local configuration;
- local paths, usernames, private machine layouts, and device-repository destinations;
- unpublished patent specifications, claims, claim charts, examiner strategy, continuation strategy, and filing records;
- physical device architecture, transistor design, materials selection, fabrication details, cryogenic control electronics, and laboratory handover packets;
- private calibration records and unpublished laboratory mappings;
- provisional experiments that are unrelated to the first release claim;
- incomplete modules, unresolved imports, duplicated code, debugging artefacts, and failed exploratory evidence not needed for the declared audit trail;
- any result whose provenance, manifest, scientific status, or claim boundary cannot be stated clearly.

## Evidence boundary

A hardware observation means that a physical backend returned data for the declared circuit and protocol. It does not by itself identify a new physical mechanism.

A passing benchmark may support a quantum representation of operator-order memory under the declared tests. It does not establish:

- a fabricated transistor or electronic memory cell;
- a material memory mechanism;
- thermodynamic entropy production;
- a universal recognition law;
- quantum computational advantage;
- fault-tolerant quantum computing;
- commercial readiness or safety.

## Transport rule

No file is copied wholesale merely for completeness. Public material must be selected, sanitised, tested, provenance-linked, and listed in `TRANSFER_MANIFEST.md`.

If a public explanation can be reproduced without exposing a private implementation detail, the narrower explanation is preferred. Transparency requires enough information to evaluate the released claim, not publication of every adjacent invention.

## Version rule

Every public result must be tied to an immutable release tag or commit. Later changes must not silently replace the meaning of an earlier certificate or evidence bundle.

## Rights boundary

Public visibility permits only the uses stated in `LICENSE`. It does not grant a patent licence, waive patent rights, dedicate inventions to the public, or authorise commercial, production, device, or derivative use.
