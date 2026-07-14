# Public Evidence Intake

No hardware evidence has been approved for the tracked public branch yet.

The private campaign has now reported a passing three-backend `CROSS_BACKEND_REPLICATION` result. It is eligible for controlled local intake and publication audit, but not yet for commit or public visibility. Use [`docs/EVIDENCE_INTAKE.md`](../docs/EVIDENCE_INTAKE.md).

## Local staging boundary

The intake tool writes only to the git-ignored directory:

```text
intake_staging/
  intake_audit.json
  intake_audit.md
  selected_runs/
  replication/
```

Do not force-add this directory. It exists so hashes, identifiers, privacy, provenance, and patent boundaries can be reviewed before evidence enters Git history.

## Required selected-run bundle

```text
selected_runs/<PUBLIC_RUN_ID>/
  results.json
  certificate.json
  summary.md
  manifest.json
```

## Required replication bundle

```text
replication/<PUBLIC_REPLICATION_ID>/
  replication_certificate.json
  replication_summary.md
  replication_manifest.json
```

## Intake gates

Every bundle must pass:

- SHA-256 manifest verification;
- source-commit and source-path provenance recording;
- distinct execution and raw-result checks;
- fixed benchmark classification and metric gates;
- credential, local-path, personal-information, and unpublished-IP scans;
- review of backend and job identifiers for publication necessity;
- scientific-boundary review;
- offline regeneration of the replication result.

The private repository remains the authoritative archive for unmodified raw evidence. The public repository contains only selected, provenance-linked evidence necessary to audit the released claim.

Failed or excluded runs must not be silently erased from the research history. The release notes should report aggregate inclusion and exclusion categories without exposing private material.
