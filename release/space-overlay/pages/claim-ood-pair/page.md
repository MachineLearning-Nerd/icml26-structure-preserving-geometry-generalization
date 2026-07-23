# Claim 4 — Poly-Poisson and NS2d-c++ OOD

## Verdict: BLOCKED

The pinned source reports Poly-Poisson OOD `2.14` vs Linear Attention `4.60`
and NS2d-c++ OOD `42.2` vs Transolver `91.40` (x1e-2 normalized L2). These
transcriptions and percentage calculations pass, but they are not an
independent model evaluation. GNOT is the stronger listed NS2d-c++
alternative at `83.08`.

The demo refers to `data/processed_polypoisson_id.pt`, which is absent.
Processed Poly OOD, custom NS2d-c++ COMSOL/Gmsh data, faithful generators,
and checkpoints are all absent.

Machine blocker set: `checkpoint`, `preprocessing`, `poly_ood_data`,
`ns2d_custom_data`.
