# Claim 1 — FEEC exact conservation

---
<!-- trackio-cell
{"type": "markdown", "id": "cell_gc1_01", "created_at": "2026-07-17T22:06:00+00:00", "title": "Claim and method"}
-->
**Claim (verbatim):** “Geo-NeW exactly preserves physical conservation laws through Finite Element
Exterior Calculus.”

The discrete Whitney/incidence structure (`δ₀` = complete-graph incidence on P control volumes,
matching official `construct_delta0`) yields exact conservation for any partition-of-unity:

- `δ₀·1 = 0` (integer-exact): every oriented edge balances.
- Global mass conservation `1ᵀδ₀ᵀF = (δ₀1)ᵀF = 0` for any edge flux `F`.
- FEEC exact sequence `d²=0`: `δ₁δ₀ = 0` (boundary of a boundary is zero).

---
<!-- trackio-cell
{"type": "code", "id": "cell_gc1_02", "created_at": "2026-07-17T22:06:10+00:00", "title": "Exact verifier", "command": ["python", "repro/src/run_geo_new.py"], "exit_code": 0}
-->
````bash
$ python repro/src/run_geo_new.py
````

- `δ₀·1=0` integer-exact over P∈{3,4,5,8,12} ✓
- global `1ᵀδ₀ᵀF=0`, maximum 0.0 over 150 random fluxes ✓
- FEEC `δ₁δ₀=0` integer-exact ✓
- independent manual incidence matches the clean-room construction ✓
- perturbing one incidence entry by `1e-9` breaks conservation ✓

**C1 VERIFIED.** Machine-readable evidence: `outputs/geo_new_summary.json`.

---
<!-- trackio-cell
{"type": "markdown", "id": "cell_gc1_03", "created_at": "2026-07-19T13:08:00+00:00", "title": "Environment and controls"}
-->
Python 3.12, NumPy/SciPy, pytest; CPU only. The clean-room incidence is cross-checked against
`PIMILab/Geo-NeW@9c30e9320428c10c9a4721c19a9bc0a1639b6716`. The manual edge ordering differs from
the implementation ordering, and the deliberate perturbation confirms the zero residual is a
property of the exact incidence rather than a numerical coincidence.

