# Repro — Geo-NeW: FEEC Conservation and OOD Metric Audit (RtnSbA5AUV)

Clean-room reproduction of *Structure-Preserving Learning Improves Geometry Generalization in
Neural PDEs* (Geo-NeW; Shaffer, Koohy, Kinch, Hsieh, Trask; arXiv [2602.02788](https://arxiv.org/abs/2602.02788)),
for the [ICML 2026 Agent Reproduction Challenge](https://huggingface.co/spaces/ICML-2026-agent-repro/challenge).
OpenReview `RtnSbA5AUV`.

**Claim C1 (exact conservation via FEEC).** The discrete Whitney/incidence structure (complete-graph
incidence `δ₀` on P control volumes) exactly preserves physical conservation laws for **any**
partition-of-unity (no training):
- `δ₀·1 = 0` (integer-exact) — the incidence structure.
- Global mass conservation: `1ᵀδ₀ᵀF = (δ₀1)ᵀF = 0` for any edge flux `F`.
- FEEC exact sequence `d²=0`: `δ₁δ₀ = 0` (boundary of a boundary is zero).

**Claim C2 (up to 65% MSE reduction on OOD geometries).** A SHA-pinned audit of the camera-ready
arXiv source finds that the paper reports mean per-sample normalized L2 error, not MSE, and contains
no numeric 65% result. Recomputing the reported values against each best-performing alternative gives
53.478261% (Poly-Poisson OOD) and 49.205585% (NS2d-c++ OOD) reductions in normalized L2 error. The
claim is therefore **falsified as written**; the paper's broader OOD-advantage conclusion remains
supported by its reported normalized-L2 results.

## Results (all CPU, integer-exact)

| Claim | Verdict | Headline evidence |
|---|---|---|
| **C1** exactly preserves conservation laws via FEEC | **VERIFIED** | `δ₀·1=0` integer-exact; global mass conservation `1ᵀδ₀ᵀF=0` over 150 random fluxes (max 0.0); FEEC `δ₁δ₀=0` integer-exact; manual-incidence cross-check; perturbation negative control. |
| **C2** up to 65% MSE reduction on OOD geometries | **FALSIFIED AS WRITTEN** | Pinned TeX defines normalized L2, not MSE; 0 MSE mentions and 0 standalone 65 mentions; exact best-baseline reductions are 53.478261% and 49.205585%. |

10/10 pytest tests pass with the pinned arXiv archive (one source-integrity test skips without it).

## Reproduce
```bash
uv venv --python 3.12 .venv && source .venv/bin/activate
uv pip install numpy scipy pytest
python repro/src/run_geo_new.py
curl -L -o /tmp/2602.02788v2.tar https://arxiv.org/e-print/2602.02788v2
python repro/src/run_ood_metric_audit.py --source-tar /tmp/2602.02788v2.tar
python -m pytest repro/tests/ --geo-new-source-tar /tmp/2602.02788v2.tar
```

## Verification method
- `δ₀·1=0` (integer-exact), cross-checked against an independent manual complete-graph incidence.
- Global conservation `1ᵀδ₀ᵀF=0` for arbitrary / antisymmetric fluxes (internal fluxes cancel telescopically).
- FEEC `δ₁δ₀=0` on a triangle mesh (discrete `∇×(∇·)=0`).
- Negative control: perturbing `δ₀` breaks `δ₀·1=0`.
- C2 source-integrity check: the arXiv v2 e-print must match SHA-256
  `c88523e66a538dc8001be383172f919aeac9e359e3c2294a26889c6ffc0ed724`.
- C2 metric-contract check: source formula and table/text values are verified before recomputing
  direct reductions and the explicitly invalid squared-aggregate proxy.

## Scope & honest disclosures
- C1 (FEEC conservation) is verified exactly and holds for any partition-of-unity (no training).
- C2 is falsified as written from the paper's pinned source. This is a metric/value falsification,
  not an independent source-scale retraining: the official repository does not publish its named
  Poly-Poisson data file, OOD dataset, checkpoints, baseline outputs, or raw Figure 6 values.
- Official code `PIMILab/Geo-NeW` (`construct_delta0` in `src/utils.py`) builds exactly this complete-graph incidence; clean-room numpy reproduces it.

Detailed C2 evidence: [`docs/CLAIM2_OOD_METRIC_AUDIT.md`](docs/CLAIM2_OOD_METRIC_AUDIT.md).

Logbook: https://huggingface.co/spaces/DineshAI/RtnSbA5AUV
