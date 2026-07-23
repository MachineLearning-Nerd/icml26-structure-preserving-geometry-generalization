# Claim-by-claim Geo-NeW reproduction (local CPU)

> **Publication status:** Evidence is published to the existing
> [Hugging Face logbook](https://huggingface.co/spaces/DineshAI/RtnSbA5AUV/tree/cd77f568e5ef0d62f3dd2bc3366dade64bbf4406)
> at revision `cd77f568e5ef0d62f3dd2bc3366dade64bbf4406` and is **awaiting live
> judge evaluation**. The current judged score remains 4/12; no increase is
> claimed before a new verdict.

This project tests six judged claims from *Structure-Preserving Learning
Improves Geometry Generalization in Neural PDEs* (arXiv
[2602.02788](https://arxiv.org/abs/2602.02788), OpenReview `RtnSbA5AUV`).
The strongest result is architectural: exact FEEC conservation and exact
Dirichlet enforcement both survive independent checkers and negative
controls. The four trained benchmark claims remain **BLOCKED**, because the
pinned official release does not include the required checkpoints, faithful
preprocessors, benchmark entrypoints, or custom OOD data. No toy result is
presented as full-scale evidence. Each unresolved claim now also has an
executable falsification route and an explicitly `TOY` CPU mechanism test.

| Claim | Paper number / statement | Observed | Assessment |
|---|---|---|---|
| C1 conservation | exact | all exact residuals `0`; `1e-9` perturbation detected | **VERIFIED** |
| C2 Pipe | `0.112e-2` vs `0.38e-2` | exact model unavailable; toy structured/direct `0` / `0.08192` | **BLOCKED** + TOY |
| C3 Elasticity | `0.351e-2` vs `0.50e-2` | exact model unavailable; toy `0` / `0.06279` | **BLOCKED** + TOY |
| C4 OOD pair | `2.14` vs `4.60`; `42.2` vs `91.40` | source audited; toy polygon OOD `6.84e-16` / `0.35789` | **BLOCKED** + TOY |
| C5 boundary | `0.00` | `1.78e-15` vs `9.3071` control | **VERIFIED** |
| C6 angles | Transolver past 20°; Geo-NeW through 30° | exact sweep unavailable; toy direct through 25°, structured through 30° | **BLOCKED** + TOY |

Compute was the local 8-core arm64 CPU. The successful cumulative run took
12.279662 seconds and cost $0; Hugging Face `cpu-upgrade` was not needed.
The paper's H200 training was not downscaled into a proxy.

Read the [illustrated technical report](reports/geo-new-claim-by-claim-2026-07-23/report.md)
or the [self-contained marimo notebook](notebooks/geo_new_claims.py).

[![Open in molab](https://marimo.io/molab-shield.svg)](https://molab.marimo.io/github/MachineLearning-Nerd/icml26-repro-RtnSbA5AUV-geo-new-conservation/blob/master/notebooks/geo_new_claims.py)

Local notebook commands:

```bash
uvx marimo edit notebooks/geo_new_claims.py
uvx marimo run notebooks/geo_new_claims.py
```

## Experiment log

| Branch / experiment | Purpose | Exact run command | Assessment / outcome | Compute |
|---|---|---|---|---|
| `master` | publication surface | Not run as an experiment (publication surface) | landing page only | — |
| [`orx/validated-4-12-baseline`](https://github.com/MachineLearning-Nerd/icml26-repro-RtnSbA5AUV-geo-new-conservation/tree/orx/validated-4-12-baseline) | freeze existing verified claims and uv lock | `uv sync --frozen && uv run python repro/src/run_all.py` | C1/C5 pass; 10 tests | local CPU |
| [`orx/exact-claim-contracts-and-public-asset-audit`](https://github.com/MachineLearning-Nerd/icml26-repro-RtnSbA5AUV-geo-new-conservation/tree/orx/exact-claim-contracts-and-public-asset-audit) | exact contracts and public-release audit | `uv sync --frozen && uv run python repro/src/run_all.py` | C1/C5 VERIFIED; C2/C3/C4/C6 BLOCKED; 13 tests | local CPU |
| [`orx/durable-evidence-and-release-candidate`](https://github.com/MachineLearning-Nerd/icml26-repro-RtnSbA5AUV-geo-new-conservation/tree/orx/durable-evidence-and-release-candidate) | durable artifacts, report, notebook, additive Space candidate | `uv sync --frozen && uv run python repro/src/run_all.py` | release-gate rerun | local CPU |
| [`orx/preregistered-falsifiability-and-counterexample`](https://github.com/MachineLearning-Nerd/icml26-repro-RtnSbA5AUV-geo-new-conservation/tree/orx/preregistered-falsifiability-and-counterexample) | executable numeric contracts and counterexamples | `uv sync --frozen && uv run python repro/src/run_all.py` | C2–C4 counterexamples rejected; C6 underdefined; 18 tests | local CPU |
| [`orx/cpu-toy-geometry-mechanism-suite`](https://github.com/MachineLearning-Nerd/icml26-repro-RtnSbA5AUV-geo-new-conservation/tree/orx/cpu-toy-geometry-mechanism-suite) | four explicit toy mechanism analogues | `uv sync --frozen && uv run python repro/src/run_all.py` | all controls pass; formal verdicts unchanged; 17 tests | local CPU |
| [`orx/integrated-multi-route-evidence-candidate`](https://github.com/MachineLearning-Nerd/icml26-repro-RtnSbA5AUV-geo-new-conservation/tree/orx/integrated-multi-route-evidence-candidate) | integrate exact, falsifiability, and toy routes | `uv sync --frozen && uv run python repro/src/run_all.py` | cumulative final rerun | local CPU |

Fixed reproduction:

```bash
uv sync --frozen && uv run python repro/src/run_all.py
```

The environment is locked by `uv.lock`. Claim contracts, raw evidence,
independent checker output, controls, and limitations are under
`.openresearch/artifacts/`.

## Historical upstream README

> The material below is retained for provenance. Its earlier
> “FALSIFIED AS WRITTEN” label applied to a separate 65%-MSE wording audit,
> not to the six empirical claims evaluated above. The current empirical
> verdict for the OOD benchmark claim is `BLOCKED`.

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
