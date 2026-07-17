# Negative controls

---
<!-- trackio-cell
{"type": "markdown", "id": "cell_gn_01", "created_at": "2026-07-17T22:08:00+00:00", "title": "Perturbation"}
-->
**Perturbing `δ₀` breaks conservation.** Adding a small perturbation to one `δ₀` entry makes
`δ₀·1 ≠ 0` (‖·‖∞ = 1e-9 > 0), which in turn breaks global mass conservation (`1ᵀδ₀ᵀF ≠ 0`).
This confirms the conservation is a property of the exact incidence structure, not a coincidence.

---
<!-- trackio-cell
{"type": "markdown", "id": "cell_gn_02", "created_at": "2026-07-17T22:08:10+00:00", "title": "Independent incidence"}
-->
**Independent incidence cross-check.** A manually-constructed complete-graph incidence (different
edge ordering) produces the same edge-set as `construct_delta0` — confirming the structure is the
standard oriented complete-graph incidence, not an artifact of one implementation.
