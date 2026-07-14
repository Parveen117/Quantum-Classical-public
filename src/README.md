# Public Source Transport Status

The first public executable unit will contain two sanitised files derived from `Parveen117/quantum-classical-provisional`:

```text
run_multi_ledger_operator_memory_test.py
evaluate_multi_ledger_replication.py
```

They are not copied into this branch yet because the private source versions must first be processed through the following gate:

1. freeze the private source commit;
2. preserve the original source hash;
3. remove local Windows and Jupyter paths;
4. confirm that credentials are read only from environment variables or authorised SDK configuration;
5. remove device-facing export logic from the first release scope;
6. run both `--self-test` modes in a clean environment;
7. confirm compatibility with the declared Qiskit and `qiskit-ibm-runtime` versions;
8. compare the sanitised file against the private source and document every modification;
9. record both source and public hashes in the machine-readable transport manifest.

The public runner must produce manifest-verified evidence bundles. The public evaluator must operate offline and reject missing files, hash mismatches, duplicate evidence, failed gates, and unstable replication.
