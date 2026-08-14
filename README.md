# Structure-Preserving Geometry Generalization — ICML 2026

Clean-room reproduction audit for **Geo-NeW** and the paper *Structure-Preserving
Learning Improves Geometry Generalization in Neural PDEs*.

- Canonical repository: [MachineLearning-Nerd/icml26-structure-preserving-geometry-generalization](https://github.com/MachineLearning-Nerd/icml26-structure-preserving-geometry-generalization)
- Former repository: `icml26-repro-RtnSbA5AUV-geo-new-conservation`
- Paper: [arXiv:2602.02788v2](https://arxiv.org/abs/2602.02788) · [OpenReview:RtnSbA5AUV](https://openreview.net/forum?id=RtnSbA5AUV)
- Official implementation: [PIMILab/Geo-NeW](https://github.com/PIMILab/Geo-NeW) pinned at [`9c30e932`](https://github.com/PIMILab/Geo-NeW/tree/9c30e9320428c10c9a4721c19a9bc0a1639b6716)

## What this repository establishes

The audit separates exact architectural properties from full benchmark claims.
Two structural claims are reproducible from the clean-room implementation and
independent controls. Four trained benchmark claims remain explicitly blocked
because the public official release does not contain the required checkpoints,
faithful preprocessors, or custom OOD data. Small CPU experiments are labeled
`TOY`; they are mechanism illustrations and are never used as benchmark proof.

| Claim | Paper claim | Local assessment | Evidence producer |
| --- | --- | --- | --- |
| C1 | FEEC/Whitney structure exactly preserves discrete conservation | **VERIFIED** | `repro/src/run_geo_new.py` + `repro/src/geo_new.py` |
| C2 | Pipe benchmark: `0.112e-2` versus `0.38e-2` | **BLOCKED** | `repro/src/release_asset_audit.py` |
| C3 | Elasticity benchmark: `0.351e-2` versus `0.50e-2` | **BLOCKED** | `repro/src/release_asset_audit.py` |
| C4 | Poly-Poisson and NS2d-c++ OOD improvements | **BLOCKED** | `repro/src/release_asset_audit.py` |
| C5 | Exact Dirichlet boundary enforcement | **VERIFIED** | `repro/src/verify_bc.py` |
| C6 | Geo-NeW remains useful through the tested angled-step range | **BLOCKED** | `repro/src/release_asset_audit.py` |

The machine-readable claim contracts and their limitations are in
[`docs/CLAIM_EVIDENCE.md`](docs/CLAIM_EVIDENCE.md). The concise publication
status is in [`STATUS.md`](STATUS.md).

## How each claim is produced

### C1 — exact FEEC conservation (`VERIFIED`)

`geo_new.construct_delta0` builds the oriented complete-graph incidence used by
the official implementation. `run_geo_new.py` checks, for several values of
`P`, that `delta_0 @ 1` is exactly zero, checks global conservation over 150
seeded random fluxes, checks the triangle identity `delta_1 @ delta_0 = 0`,
cross-checks the edge set with an independently constructed incidence matrix,
and applies a one-entry perturbation that must break conservation. The raw
results, independent checker, and negative control are under
`evidence/claim_1/`.

This verifies the structural mechanism; it does not claim that a trained model
matches every reported PDE error.

### C2 — Pipe benchmark (`BLOCKED`)

The paper reports a mean per-sample normalized-L2 error of `0.112e-2` for
Geo-NeW versus `0.38e-2` for LaMO. The release-asset audit pins the official
repository and checks for the standard data, Geo-NeW preprocessing, training
entrypoint, and checkpoint. Those inputs are absent, so a faithful evaluation
cannot be produced from this checkout. `evidence/claim_2/` records the exact
contract, missing inputs, source anchor, and the non-vacuous synthetic-manifest
control.

### C3 — Elasticity benchmark (`BLOCKED`)

The paper reports `0.351e-2` versus `0.50e-2`. The same audit requires the
Elasticity data conversion to the paper's FEM/Whitney inputs, the exact training
configuration, and a checkpoint or feasible faithful retraining. These are not
released. The result remains `BLOCKED`, not an estimate based on a proxy;
see `evidence/claim_3/`.

### C4 — OOD benchmark pair (`BLOCKED`)

The paper reports `2.14e-2` versus `4.60e-2` on Poly-Poisson OOD and `42.2e-2`
versus `91.40e-2` on NS2d-c++ OOD. The custom processed data/generators,
reference solves, and trained models are absent from the official release.
The source-only arithmetic audit in
[`docs/CLAIM2_OOD_METRIC_AUDIT.md`](docs/CLAIM2_OOD_METRIC_AUDIT.md) is useful
provenance, but it does not decide model performance. The empirical status and
missing-asset checks are in `evidence/claim_4/`.

### C5 — exact Dirichlet boundary condition (`VERIFIED`)

`verify_bc.py` uses seeded random network weights and 4,000 points on the
boundary. It evaluates the paper-style constrained parameterization, checks
that the boundary error is at numerical roundoff (`1.776e-15`), confirms a
nontrivial interior field, and compares it with an unconstrained control whose
maximum error is `9.3071`. The result and controls are in `evidence/claim_5/`.

This verifies the boundary-enforcement mechanism, not the full benchmark
accuracy claim.

### C6 — angled-step generalization (`BLOCKED`)

The paper's comparison says that Transolver degrades past 20 degrees while
Geo-NeW remains useful through the tested 30-degree range. The exact custom
NS2d-c++ data, reference solves, model checkpoints, and a numerical definition
of “meaningful” are unavailable. The falsifiability and toy routes document
what a valid future test would need; neither substitutes for the paper's
experiment. See `evidence/claim_6/`.

## Reproduce the audit

Use Python 3.11 or 3.12 and the locked environment:

```bash
uv sync --frozen
uv run python repro/src/run_all.py
uv run python -m pytest -q repro/tests/
```

`run_all.py` downloads arXiv `2602.02788v2`, verifies its SHA-256, runs the
C1/C5 producers, the source metric audit, the official-release asset audit,
the explicitly `TOY` mechanism suite, the falsifiability checks, and the
independent tests. C1 and C5 can also be run without the paper archive:

```bash
uv run python repro/src/run_geo_new.py
uv run python repro/src/verify_bc.py
```

After the evidence is generated, the repository integrity checks are:

```bash
python3 repro/src/verify_results.py
python3 repro/src/publication_gate.py --skip-producers
```

## Repository contents

- `repro/src/` — clean-room producers, source audits, asset inventory, toy route, and falsifiability route.
- `repro/tests/` — independent checks and negative controls.
- `evidence/` — committed claim contracts, methods, source audits, raw results, and controls.
- `docs/` — claim ledger, source boundary, branch audit, research log, and publication gate.
- `reports/` — the historical illustrated claim-by-claim report; its toy results remain labeled `TOY`.
- `notebooks/` — an optional marimo presentation of the claim evidence.
- `release/` and `pages/` — historical external-publication artifacts retained for provenance; they are not required inputs for the local gate.

## Branch map

The public branch names are normalized and describe their purpose. The old
`orx/` names are recorded only for provenance in
[`docs/BRANCH_AUDIT.md`](docs/BRANCH_AUDIT.md).

| Final branch | Former branch | Purpose |
| --- | --- | --- |
| `main` | `master` | integrated publication surface and current claim ledger |
| `baseline/validated-4-12` | `orx/validated-4-12-baseline` | freeze the first validated C1/C5 baseline |
| `audit/exact-claim-contracts` | `orx/exact-claim-contracts-and-public-asset-audit` | claim contracts and public-asset inventory |
| `release/durable-evidence-candidate` | `orx/durable-evidence-and-release-candidate` | durable evidence and release packaging |
| `audit/falsifiability-counterexamples` | `orx/preregistered-falsifiability-and-counterexample` | executable counterexamples and C6 identifiability |
| `experiment/toy-geometry-mechanisms` | `orx/cpu-toy-geometry-mechanism-suite` | explicitly downscaled CPU mechanism analogues |
| `release/integrated-evidence-candidate` | `orx/integrated-multi-route-evidence-candidate` | integrated exact, falsifiability, and toy evidence |
| `audit/official-code-reachability` | `orx/official-code-cost-and-reachability` | official-code structure and benchmark reachability audit |

## Source and evidence boundary

The paper source is pinned to arXiv `2602.02788v2` with SHA-256
`c88523e66a538dc8001be383172f919aeac9e359e3c2294a26889c6ffc0ed724`. The
official code is audited at commit
`9c30e9320428c10c9a4721c19a9bc0a1639b6716`. The historical Hugging Face Space
[`DineshAI/RtnSbA5AUV`](https://huggingface.co/spaces/DineshAI/RtnSbA5AUV)
is external context, not a substitute for a GitHub checkpoint or dataset.

No full-scale trained benchmark result is claimed unless the exact data,
preprocessing, model, split, metric, and evaluation protocol are available.

## Citation

```bibtex
@article{shaffer2026structure,
  title         = {Structure-Preserving Learning Improves Geometry Generalization in Neural PDEs},
  author        = {Benjamin D. Shaffer and Shawn Koohy and Brooks Kinch and M. Ani Hsieh and Nathaniel Trask},
  journal       = {arXiv preprint arXiv:2602.02788},
  year          = {2026},
  doi           = {10.48550/arXiv.2602.02788},
  eprint        = {2602.02788},
  archivePrefix = {arXiv},
  primaryClass  = {cs.LG}
}
```

## Thank you

Thank you to Benjamin D. Shaffer, Shawn Koohy, Brooks Kinch, M. Ani Hsieh,
and Nathaniel Trask for sharing the Geo-NeW implementation and the paper's
architectural details. This audit is intended as a respectful, traceable
reproduction record: it reports what can be checked from public artifacts and
leaves the remaining claims blocked where those artifacts are insufficient.
