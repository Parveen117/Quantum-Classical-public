# Claim Scope and Evidence Matrix

This file is the controlling interpretation guide for the first public release. README language, release notes, figures, and certificate summaries must remain inside these boundaries.

## Claim C1: declared circuit construction

**Statement:** The released code constructs three RK/KR operator-order interferometers, stores their relative-order information in three ledger qubits, and applies a declared projection to a readout qubit.

**Evidence required:** source code, circuit-construction self-tests, qubit map, operator definitions, and projection weights.

**Status:** computational construction claim.

**Does not establish:** that the ledgers are a new physical memory substance or that the projection weights are physical constants.

## Claim C2: control separation

**Statement:** Under the declared benchmark, anticommuting-order modes can be compared with commuting, order-erased, full-erasure, and projection-erased controls.

**Evidence required:** circuit definitions, execution outputs, control metrics, and manifest-verified certificates.

**Status:** computational verification or hardware observation, depending on the evidence bundle.

**Falsified or weakened if:** control outputs are not separated under predeclared thresholds or separation vanishes under repeated runs.

## Claim C3: selective ledger erasure

**Statement:** Each declared ledger channel can be reset separately and evaluated for suppression of the targeted channel while the other declared channels remain active.

**Evidence required:** `erase_m1`, `erase_m2`, and `erase_m3` outputs, ledger marginals, thresholds, and run certificates.

**Status:** hardware observation when executed on a physical backend.

**Does not establish:** irreversible thermodynamic erasure or a fabricated electronic reset mechanism.

## Claim C4: causal projection test

**Statement:** The projection-erased control tests whether hidden ledger information can remain while the declared readout projection is suppressed.

**Evidence required:** full-memory and projection-erased results, ledger distributions, readout probabilities, and predeclared decision rules.

**Status:** benchmark-specific causal-control claim.

**Falsified or weakened if:** the projection-erased condition does not suppress readout, or if suppression can be explained by an uncontrolled circuit difference.

## Claim C5: reduced-model comparison

**Statement:** The full multi-ledger model can be compared against no-memory, single-ledger, and pair-ledger alternatives using a declared error metric.

**Evidence required:** model definitions, predictions, observed values, error table, and metric registration.

**Status:** computational model-comparison claim.

**Does not establish:** that the full model is uniquely true outside the released benchmark.

## Claim C6: matched selected visible outputs

**Statement:** Selected visible RK and KR endpoint distributions can remain close under a declared distance metric while ledger outputs retain order information.

**Evidence required:** visible RK and KR distributions, total-variation distance or another predeclared metric, and thresholds.

**Status:** benchmark-specific observation.

**Does not establish:** complete physical equivalence of RK and KR histories.

## Claim C7: cross-run or cross-backend stability

**Statement:** Multiple manifest-valid runs from distinct backends can be evaluated under fixed per-run and cross-run gates, with duplicate job identifiers and duplicate raw-result hashes rejected.

**Evidence required:** at least two selected valid runs, distinct backend identifiers, distinct job identifiers, distinct raw-result hashes, replication statistics, and a replication certificate.

**Status:** replication-evaluation claim.

**Falsified or weakened if:** fixed gates fail, results are unstable beyond thresholds, evidence is duplicated, or the selection process is biased and undisclosed.

## Permitted combined conclusion

When C1 through C7 are supported by the released evidence, the public release may state:

> The selected runs support a reproducible quantum representation of decomposable operator-order memory under the released circuit, controls, metrics, thresholds, and evidence-selection rules.

## Prohibited conclusions from the first release

The first release must not state or imply that it proves:

- a fabricated transistor or memory cell;
- a material phase-seam or memory mechanism;
- thermodynamic entropy production or Landauer erasure;
- a universal recognition law;
- quantum advantage or fault tolerance;
- an independently validated new law of physics;
- commercial readiness, device safety, or manufacturability.

## Required wording rule

Every result summary must identify whether it is a definition, derivation, computational verification, hardware observation, replication result, or physical validation. The phrase “validated” must include the object and level being validated. Bare claims such as “the theory is validated” are not permitted.
