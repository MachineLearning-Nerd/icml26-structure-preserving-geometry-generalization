# Repro — Geo-NeW: FEEC Conservation in Neural PDEs (RtnSbA5AUV)

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

## Results (all CPU, integer-exact)

| Claim | Verdict | Headline evidence |
|---|---|---|
| **C1** exactly preserves conservation laws via FEEC | **VERIFIED** | `δ₀·1=0` integer-exact; global mass conservation `1ᵀδ₀ᵀF=0` over 150 random fluxes (max 0.0); FEEC `δ₁δ₀=0` integer-exact; manual-incidence cross-check; perturbation negative control. |

5/5 pytest tests pass. (C2 — up to 65% MSE reduction — requires ~3M-param transformer training, out of scope.)

## Reproduce
```bash
uv venv --python 3.12 .venv && source .venv/bin/activate
uv pip install numpy scipy pytest
python repro/src/run_geo_new.py
python -m pytest repro/tests/
```

## Verification method
- `δ₀·1=0` (integer-exact), cross-checked against an independent manual complete-graph incidence.
- Global conservation `1ᵀδ₀ᵀF=0` for arbitrary / antisymmetric fluxes (internal fluxes cancel telescopically).
- FEEC `δ₁δ₀=0` on a triangle mesh (discrete `∇×(∇·)=0`).
- Negative control: perturbing `δ₀` breaks `δ₀·1=0`.

## Scope & honest disclosures
- C1 (FEEC conservation) verified exactly — holds for any partition-of-unity (no training). C2 (MSE reduction) needs GPU transformer training — out of scope.
- Official code `PIMILab/Geo-NeW` (`construct_delta0` in `src/utils.py`) builds exactly this complete-graph incidence; clean-room numpy reproduces it.

Logbook: https://huggingface.co/spaces/DineshAI/RtnSbA5AUV
