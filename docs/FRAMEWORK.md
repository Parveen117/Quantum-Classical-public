# Quantum-Classical Recognition Framework

## Purpose

This document defines the minimum state, comparison, residue, and closure language needed to interpret the public benchmark. It is a bounded projection framework, not a declaration that quantum experiments prove an entire foundational theory.

## Scientific statement levels

The repository distinguishes:

- **definition:** an object, metric, gate, or certificate is introduced;
- **derivation:** a result follows from declared assumptions;
- **computational verification:** code or tests confirm a result for specified inputs;
- **hardware observation:** a named backend returns data for a declared execution;
- **physical validation:** independent observations support a physical mechanism within uncertainty.

These levels must not be silently exchanged. A passing computational or hardware certificate is conditional evidence, not automatic proof of a universal physical law.

## Recognition state

The full quantum-classical state is represented as

\[
N_Q=(x_Q,\lambda_Q,\gamma_Q,\ell_Q,m_Q).
\]

The components are:

- \(x_Q\): visible physical state or observed distribution;
- \(\lambda_Q\): active response or recognition coordinates;
- \(\gamma_Q\): preparation, evolution, measurement, and backend protocol;
- \(\ell_Q\): declared dynamical, statistical, noise, calibration, and tolerance ledger;
- \(m_Q\): accumulated phase, cycle, history, or memory information.

A practical visible-state representation is

\[
x_Q=(\rho,H,\mathcal M,p_{\mathrm{obs}}),
\]

where \(\rho\) is a prepared density operator or declared classical probability state, \(H\) is the evolution generator, \(\mathcal M=\{M_i\}\) is the measurement model, and \(p_{\mathrm{obs}}\) is the observed outcome distribution.

For a declared quantum model,

\[
p_{\mathrm{exp}}(i)=\operatorname{Tr}(\rho M_i).
\]

Two runs may share a visible endpoint distribution while differing in phase history, backend, preparation, noise, or stored ledger information. Equality of selected visible outputs therefore does not imply equality of the full declared state.

## Recognition comparison

Let

\[
\Lambda_{\mathrm{ref}}(N_Q)
\]

be the response expected from the declared model and

\[
\Lambda_{\mathrm{obs}}(N_Q)
\]

be the observed or simulated response. Define

\[
\delta\Lambda_Q=\Lambda_{\mathrm{obs}}-\Lambda_{\mathrm{ref}}.
\]

A declared decomposition is

\[
\delta\Lambda_Q=P_+\delta\Lambda_Q+P_-\delta\Lambda_Q,
\]

where \(P_+\delta\Lambda_Q\) is explained by the registered physical and uncertainty ledger, while \(P_-\delta\Lambda_Q\) remains unresolved.

The projector, metric, tolerance, and lawful ledger must be declared before examining the result. Choosing them after seeing the data makes the certificate circular.

## Quantum-classical seam

A seam is a typed comparison across a physical or representational transition, including:

- preparation to measurement;
- ideal simulator to noisy simulator;
- simulator to hardware backend;
- one hardware backend to another;
- one control condition to another;
- one calibration or execution epoch to another;
- visible endpoint agreement to hidden-ledger disagreement.

Seam data are represented as

\[
\Sigma_Q=(\mathcal N_-,\mathcal N_+,E_{\Sigma_Q},L_{\Sigma_Q},\varepsilon_{\Sigma_Q}),
\]

where \(E_{\Sigma_Q}\) states which objects may be compared, \(L_{\Sigma_Q}\) is the declared lawful bridge, and \(\varepsilon_{\Sigma_Q}\) is the uncertainty model.

The open defect must be calculated after subtracting the declared lawful contribution:

\[
G_{\mathrm{open}}=G_{\mathrm{obs}}-L_{\Sigma_Q}.
\]

Without that subtraction, ordinary finite-shot variation, basis conversion, drift, or calibrated backend noise can be mislabeled as a novel effect.

## Residue vector

The public framework tracks

\[
G_Q=(G_{\mathrm{state}},G_{\mathrm{dist}},G_{\mathrm{dyn}},G_{\mathrm{bridge}},G_{\mathrm{phase}},G_{\mathrm{frame}},G_{\mathrm{mem}}).
\]

The sectors represent mismatch in prepared state, outcome distribution, evolution, model or backend bridge, phase or cycle, frame or basis, and history or memory.

A distribution residue may be written as

\[
G_{\mathrm{dist}}=D(p_{\mathrm{obs}},p_{\mathrm{exp}})-D_{\mathrm{lawful}},
\]

where the distance \(D\) and the lawful allowance must be named in every certificate. Quietly changing metrics until a preferred plot appears is not validation.

## Closure

Closure is declared only when all active residue sectors lie within the registered uncertainty budget:

\[
\lVert G_Q\rVert_W\leq\varepsilon_Q,
\]

where \(W\) is a declared weighting or covariance model.

Possible closure levels include distribution, dynamical, bridge, frame, memory, and full registered closure. A failed closure identifies an unresolved residue. It does not automatically identify the residue's physical cause.

## Projection dictionary

The bounded projection is written

\[
\Pi_Q:\mathfrak X_{\mathrm{EMK}}\rightarrow\mathfrak X_Q.
\]

The initial public dictionary is

\[
\Pi_Q(R)=P_+,
\]

\[
\Pi_Q(K)=K^Q_{\Sigma},
\]

\[
\Pi_Q(\Delta_N)=G_Q,
\]

\[
\Pi_Q(\mathrm{shadow})=P_-\delta\Lambda_Q,
\]

\[
\Pi_Q(\mathrm{closure})=\lVert G_Q\rVert_W\leq\varepsilon_Q.
\]

A projection certificate must record the preparation, expected model, measurement map, backend or simulator, bridge model, uncertainty ledger, sample count, residue metric, tolerance, software revision, and output hashes.

## Falsification conditions

The public projection is weakened or falsified if:

- the recognition projector or threshold is selected after observing the result;
- the lawful ledger is broad enough to absorb every discrepancy;
- conclusions change under physically equivalent frames without explanation;
- certificates cannot be regenerated from declared inputs;
- repeated runs reveal unexplained history dependence that is nevertheless labeled closure;
- a simpler classical or reduced-memory model performs equally well while the interpretation claims unique support;
- the same discrepancy is alternately labeled noise, memory, curvature, or new physics without a predeclared rule;
- selected evidence is not representative of the declared release population;
- no explicit map connects benchmark objects to the framework objects.
