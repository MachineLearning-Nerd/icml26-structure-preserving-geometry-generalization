# Reproduction: Structure-Preserving Learning Improves Geometry Generalization in Neural PDEs

Clean-room reproduction and pinned-source audit of *Geo-NeW* (Shaffer et al.;
[OpenReview `RtnSbA5AUV`](https://openreview.net/forum?id=RtnSbA5AUV), arXiv `2602.02788v2`).

- **C1 — VERIFIED.** FEEC incidence identities establish exact conservation for any
  partition-of-unity: `δ₀·1=0`, `1ᵀδ₀ᵀF=0`, and `δ₁δ₀=0`, with independent construction and
  perturbation controls.
- **C2 — FALSIFIED AS WRITTEN.** The challenge says “up to 65% MSE reduction,” but the
  SHA-pinned camera-ready source defines mean per-sample normalized L2 error, contains no MSE or
  standalone 65 statistic, and yields exact best-alternative reductions of 53.478261% and
  49.205585% in its two OOD columns.

This distinction is decisive: the paper supports an OOD advantage in its reported normalized-L2
metric, but it does not report or permit recovery of the challenged 65% MSE statistic.

## Claims
| Claim | Statement | Verdict |
| --- | --- | --- |
| **C1** | Exactly preserves conservation laws via FEEC | **VERIFIED** |
| **C2** | Up to 65% MSE reduction against best alternatives on OOD geometries | **FALSIFIED AS WRITTEN** |

## Pages

| Page |
| --- |
| [Executive summary](#/executive-summary) |
| [Claim 1 — FEEC exact conservation](#/claim-1-feec-conservation) |
| [Claim 2 — OOD metric audit](#/claim-2-ood-metric) |
| [Conclusion](#/conclusion) |

10/10 tests pass against the pinned arXiv archive. CPU only.
