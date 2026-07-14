# Environment and Execution

## Supported Python

The release candidate requires Python 3.10 or newer.

Offline verification uses only the Python standard library. IBM hardware execution uses the optional dependency set declared in `pyproject.toml`:

```text
qiskit==2.5.0
qiskit-ibm-runtime==0.47.0
```

Install the hardware environment with:

```bash
python -m pip install --upgrade pip
python -m pip install "qiskit==2.5.0" "qiskit-ibm-runtime==0.47.0"
```

These exact versions define the `v0.1.0-rc1` API target. A future dependency update requires a new tested release revision rather than silently changing the execution environment.

## Offline verification

From the repository root:

```bash
python tools/verify_release.py
```

This command:

- compiles the public Python sources;
- checks the four JSON schemas;
- scans for local paths and hardcoded credentials;
- verifies public attribution;
- runs the benchmark's offline invariant tests;
- runs the replication evaluator's positive and adversarial fixtures.

No IBM account or Qiskit installation is required for the pure offline checks. When Qiskit is installed, the benchmark self-test also constructs every declared circuit and verifies its width.

## Optional IBM hardware execution

The public runner does not accept or store a token argument. IBM Runtime authentication is handled by the installed SDK using the user's own authorised account configuration.

The runner accepts:

```text
IBM_QUANTUM_BACKEND
IBM_QUANTUM_SHOTS
IBM_QUANTUM_CHANNEL
IBM_QUANTUM_INSTANCE
```

The default channel is:

```text
ibm_quantum_platform
```

Example execution:

```bash
export IBM_QUANTUM_BACKEND="<backend-name>"
export IBM_QUANTUM_SHOTS="4096"
python src/run_multi_ledger_operator_memory_test.py
```

A Windows PowerShell equivalent is:

```powershell
$env:IBM_QUANTUM_BACKEND = "<backend-name>"
$env:IBM_QUANTUM_SHOTS = "4096"
python src/run_multi_ledger_operator_memory_test.py
```

Do not commit IBM tokens, saved-account files, instance identifiers, shell history containing secrets, or local `.env` files. The repository `.gitignore` excludes common credential locations, but users remain responsible for their own account security.

## Offline replication evaluation

After approved run bundles are placed under `evidence/selected_runs/`:

```bash
python src/evaluate_multi_ledger_replication.py --no-write
```

To write a new hashed replication bundle:

```bash
python src/evaluate_multi_ledger_replication.py
```

The evaluator does not contact IBM. It verifies files and hashes, recomputes fixed gates, rejects duplicate evidence, and evaluates cross-run stability.

## CI coverage

The GitHub Actions workflow runs the offline verifier on Python 3.10, 3.12, and 3.14. A separate compatibility job installs the declared Qiskit versions and constructs every benchmark circuit without submitting a hardware job.
