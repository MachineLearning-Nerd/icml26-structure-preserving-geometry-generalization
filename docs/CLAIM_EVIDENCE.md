# Claim-to-evidence map

This file defines what each claim means in this audit, which producer creates
its evidence, and what would be required to change its status. `VERIFIED` is
reserved for a claim whose local producer and independent controls pass.
`BLOCKED` means that the exact empirical test cannot be performed from the
public artifacts available to this repository. A source transcription or a
toy analogue is never treated as a full-scale benchmark result.

| ID | Paper statement | Producer | Committed evidence | Status |
| --- | --- | --- | --- | --- |
| C1 | FEEC/Whitney structure preserves discrete conservation exactly | `repro/src/run_geo_new.py` | `evidence/claim_1/` | `VERIFIED` |
| C2 | Pipe error `0.112e-2` vs LaMO `0.38e-2` | `repro/src/release_asset_audit.py` | `evidence/claim_2/` | `BLOCKED` |
| C3 | Elasticity error `0.351e-2` vs LaMO `0.50e-2` | `repro/src/release_asset_audit.py` | `evidence/claim_3/` | `BLOCKED` |
| C4 | Poly-Poisson and NS2d-c++ OOD improvements | `repro/src/release_asset_audit.py` | `evidence/claim_4/` | `BLOCKED` |
| C5 | Dirichlet values are enforced exactly at boundary nodes | `repro/src/verify_bc.py` | `evidence/claim_5/` | `VERIFIED` |
| C6 | Geo-NeW remains useful through the tested angled-step range | `repro/src/release_asset_audit.py` | `evidence/claim_6/` | `BLOCKED` |

## C1 — FEEC conservation

`repro/src/geo_new.py` is a clean-room NumPy implementation of the official
complete-graph incidence construction. `run_geo_new.py` generates the result
record by checking:

1. `delta_0 @ 1 == 0` in exact floating representation for `P` in
   `{3, 4, 5, 8, 12}`;
2. `1^T delta_0^T F == 0` for 150 seeded random fluxes;
3. `delta_1 @ delta_0 == 0` on an oriented triangle;
4. equality with a separately ordered manual incidence construction; and
5. detection of a one-entry `1e-9` perturbation.

The raw result, independent checker, and negative control are committed in
`evidence/claim_1/`. This is a structural verification and requires no model
training.

## C2 — Pipe benchmark

The source contract in `evidence/claim_2/source_audit.md` records the paper's
metric, split, mesh size, and reported values. The executable asset audit then
checks the pinned official repository and the authors' public Hugging Face
inventory for:

- the standard Pipe data;
- the Geo-NeW mesh/FEM preprocessing;
- a Pipe training/evaluation entrypoint; and
- a released checkpoint.

The raw result records missing `checkpoint`, `preprocessing`, and
`pipe_training`. The injected complete-manifest control clears those blockers,
which tests the audit logic without pretending to evaluate the paper.

## C3 — Elasticity benchmark

The producer follows the same path for the reported `0.351e-2` versus
`0.50e-2` result. A valid evaluation needs the standard split, conversion to
the paper's FEM/Whitney representation, the exact training configuration, and
a checkpoint or a feasible faithful retraining. The official release lacks
the conversion, training path, and checkpoint, so the exact claim remains
`BLOCKED`. See `evidence/claim_3/`.

## C4 — OOD benchmark pair

The source audit records the paper's reported values:

- Poly-Poisson OOD: `2.14` for Geo-NeW and `4.60` for Linear Attention;
- NS2d-c++ OOD: `42.2` for Geo-NeW and `91.40` for Transolver.

The empirical producer requires the custom Poly-Poisson split, custom
NS2d-c++/COMSOL/Gmsh data or generators, faithful preprocessing, and trained
models. These are absent. The source-only arithmetic file
[`CLAIM2_OOD_METRIC_AUDIT.md`](CLAIM2_OOD_METRIC_AUDIT.md) explains why the
challenge wording “65% MSE” is not the paper's reported metric; it is an audit
of source wording, not a model-performance verdict.

## C5 — exact Dirichlet boundary condition

`repro/src/verify_bc.py` seeds a two-layer random network, samples 4,000 points
on a circular boundary, and evaluates the prescribed-boundary-plus-vanishing-
factor parameterization. It records:

- constrained maximum boundary error: `1.7763568394002505e-15`;
- unconstrained control maximum error: `9.3071`;
- boundary distance-factor residual: `2.220446049250313e-16`; and
- a nontrivial interior field.

The independent checker and negative control in `evidence/claim_5/` are part of
the acceptance condition. This verifies exact boundary enforcement, not the
reported trained PDE accuracy.

## C6 — angled-step generalization

The paper compares Transolver and Geo-NeW on custom angled-step geometries and
uses the qualitative word “meaningful.” A decisive reproduction needs the
custom geometry generator, reference solutions, exact angle grid, both trained
models, evaluation metric, and a predeclared numerical failure criterion.
The public release has none of the required data/model assets and does not
define that criterion. The exact claim is therefore `BLOCKED`.

`repro/src/falsifiability_audit.py` records why the wording is not machine-
falsifiable as written. `repro/src/toy_mechanism_suite.py` contains a clearly
labelled scalar toy route; its results are not C6 evidence.

## Reproduction command

```bash
uv sync --frozen && uv run python repro/src/run_all.py
```

The command pins and hashes arXiv `2602.02788v2`, regenerates local result
records, runs the asset and falsifiability audits, and executes the independent
test suite. It never turns a missing artifact into a proxy claim.
