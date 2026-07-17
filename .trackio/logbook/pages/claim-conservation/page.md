# Claim 1 — FEEC exact conservation

---
<!-- trackio-cell
{"type": "markdown", "id": "cell_gc1_01", "created_at": "2026-07-17T22:06:00+00:00", "title": "Claim & method"}
-->
**Claim (verbatim):** "Geo-NeW exactly preserves physical conservation laws through Finite Element
Exterior Calculus." (C1)

The discrete Whitney/incidence structure (`δ₀` = complete-graph incidence on P control volumes, matching
official `construct_delta0`) yields exact conservation for ANY partition-of-unity:
- **(a)** `δ₀·1 = 0` (integer-exact): the incidence structure — each edge balances.
- **(b)** Global mass conservation `1ᵀδ₀ᵀF = (δ₀1)ᵀF = 0` for any edge flux `F` (internal fluxes cancel telescopically).
- **(c)** FEEC exact sequence `d²=0`: `δ₁δ₀ = 0` (boundary of a boundary is zero).

---
<!-- trackio-cell
{"type": "code", "id": "cell_gc1_02", "created_at": "2026-07-17T22:06:10+00:00", "title": "Verifier", "command": ["python", "repro/src/run_geo_new.py"], "exit_code": 0}
-->
````bash
$ python repro/src/run_geo_new.py
````
- **(a)** `δ₀·1=0` integer-exact over P∈{3,4,5,8,12}. ✓
- **(b)** global `1ᵀδ₀ᵀF=0` max 0.0 over 150 random fluxes; antisymmetric flux per-volume net sums to 0. ✓
- **(c)** FEEC `δ₁δ₀=0` integer-exact. ✓
- **cross-check:** `construct_delta0` == manual complete-graph incidence. ✓
- **negative control:** perturbing `δ₀` breaks `δ₀·1=0`. ✓

**=> C1 VERIFIED.** Evidence: `outputs/geo_new_summary.json`.
