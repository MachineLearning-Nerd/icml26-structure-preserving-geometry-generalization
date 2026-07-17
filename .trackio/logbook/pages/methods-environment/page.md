# Methods & environment

---
<!-- trackio-cell
{"type": "markdown", "id": "cell_gm_01", "created_at": "2026-07-17T22:07:00+00:00", "title": "Setup"}
-->
**FEEC discrete structure.** `δ₀` = complete-graph incidence on P control volumes (edge (i,j), i<j:
−1 at i, +1 at j) — matches official `construct_delta0`. `δ₁` = edge-face incidence (triangle mesh).

**Conservation identities:** `δ₀·1=0`; `1ᵀδ₀ᵀF=0` (any flux); `δ₁δ₀=0` (FEEC d²=0). All integer-exact,
holding for any partition-of-unity (no training).

**Environment.** Python 3.12, numpy/scipy, pytest. CPU only. 5/5 tests. Official code
`PIMILab/Geo-NeW` (`construct_delta0`); clean-room numpy.

**Scope.** C1 (conservation) exact. C2 (MSE reduction) = ~3M-param transformer training (out of scope).
