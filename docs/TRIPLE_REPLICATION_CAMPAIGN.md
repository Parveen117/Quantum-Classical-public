# Triple IBM Replication Campaign

## Objective

The first public evidence release requires three independently submitted passing IBM Runtime jobs, preferably on three distinct physical backends, for the unchanged Multi-Ledger Operator-Memory Benchmark v1.

The existing private evidence includes one passing run:

```text
backend: ibm_fez
job_id: d9b212u6hjac73ff44j0
classification: MULTI_LEDGER_OPERATOR_MEMORY_DECOMPOSITION
```

This leaves two additional independent runs to acquire and review.

## Independence rules

A run counts as independent only when:

- it has a unique IBM Runtime job identifier;
- it has a unique raw `results.json` SHA-256 hash;
- it was submitted as a separate hardware job;
- its evidence bundle is complete and manifest-valid;
- all six declared benchmark gates pass independently;
- it was not reconstructed by copying or renaming an existing bundle.

Three transpiler seeds inside one IBM Runtime job are within-job robustness checks. They are not three independent replications.

## Preferred backend policy

The acquisition launcher must exclude any backend already represented by a completed local evidence bundle. The preferred final state is:

```text
passing_run_count: 3
backend_count: 3
classification: CROSS_BACKEND_REPLICATION
duplicate_job_ids: []
duplicate_result_hashes: []
cross_run_stability.pass: true
```

If only two distinct backends are available, a third unique job may be submitted on a previously used backend only as an explicitly labeled same-backend repeat. It does not satisfy the preferred three-backend release gate without a written limitation.

## Per-run acceptance

Every counted run must have:

```text
classification = MULTI_LEDGER_OPERATOR_MEMORY_DECOMPOSITION
hidden_memory = true
selective_erase = true
projection_causal = true
reset_projection = true
model_comparison = true
visible_rk_kr_equality = true
```

It must also pass the stricter replication evaluator limits for ledger floors, control ceiling, projection-erased readout, visible RK/KR distance, reset-signature spread, and full-model error.

## Evidence files

Each run must contain:

```text
results.json
certificate.json
summary.md
manifest.json
```

After all three runs are present, the evaluator must generate:

```text
replication_certificate.json
replication_summary.md
replication_manifest.json
```

## Publication rule

No run is transported into the public selected-evidence directory until its credentials, local paths, account metadata, patent-sensitive material, identifiers, hashes, and scientific claim boundary have been reviewed.
