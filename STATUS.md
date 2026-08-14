# Audit status

This repository is the clean-room audit of *Structure-Preserving Learning
Improves Geometry Generalization in Neural PDEs* (Geo-NeW), OpenReview
`RtnSbA5AUV`, arXiv `2602.02788v2`.

| Claim | Status | Reason |
| --- | --- | --- |
| C1 — FEEC/Whitney exact conservation | `VERIFIED` | exact incidence identities, independent construction, and perturbation control pass |
| C2 — Pipe benchmark | `BLOCKED` | official release lacks faithful preprocessing, training path, and checkpoint |
| C3 — Elasticity benchmark | `BLOCKED` | official release lacks the FEM conversion, training path, and checkpoint |
| C4 — Poly-Poisson / NS2d-c++ OOD | `BLOCKED` | custom OOD assets and trained models are absent |
| C5 — exact Dirichlet boundary condition | `VERIFIED` | constrained parameterization passes seeded boundary and unconstrained negative-control checks |
| C6 — angled-step generalization | `BLOCKED` | custom data/models are absent and “meaningful” is not numerically defined |

The toy mechanism suite and source-only metric audit are supporting evidence
only. They do not upgrade a blocked full-scale claim.

The fixed reproduction command is:

```bash
uv sync --frozen && uv run python repro/src/run_all.py
```

See [`docs/CLAIM_EVIDENCE.md`](docs/CLAIM_EVIDENCE.md) for the claim-to-code
map and [`docs/SOURCE_AUDIT.md`](docs/SOURCE_AUDIT.md) for provenance limits.
