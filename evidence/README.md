# Public Evidence

The private campaign has passed the declared three-run cross-backend gate, and the local intake staging audit has passed manifest, hash, duplicate, and sensitive-content checks.

No hardware evidence is tracked on this branch until the controlled promotion tool completes locally and the resulting Git diff is reviewed.

## Approved selected-run bundle

```text
selected_runs/<PUBLIC_RUN_ID>/
  results.json
  certificate.json
  summary.md
  manifest.json
```

## Approved replication bundle

```text
replication/<PUBLIC_REPLICATION_ID>/
  replication_certificate.json
  replication_summary.md
  replication_manifest.json
```

## Publication decisions

- IBM job identifiers are approved for public provenance because they distinguish independent executions and are not authentication credentials.
- The local intake audit is excluded from Git history because it can contain a workstation path.
- The selected technical file boundary excludes credentials, account identifiers, local paths, device implementation details, claim strategy, examiner material, and unrelated experiments.
- Final legal/IP review remains required before changing repository visibility.

## Promotion and verification

Use [`docs/EVIDENCE_INTAKE.md`](../docs/EVIDENCE_INTAKE.md) and `tools/promote_evidence_release.py`.

Promotion must reverify:

- the `CROSS_BACKEND_REPLICATION` classification;
- three passing runs on three distinct backends;
- manifest-declared SHA-256 hashes;
- distinct job identifiers and raw-result hashes;
- cross-run stability;
- exact agreement with the local intake audit;
- sensitive-content scanning before and after copying;
- exclusion of the local intake audit from tracked files.

The private repository remains the authoritative archive for unmodified and unselected research evidence. Failed or excluded runs must not be silently erased from the research history.
