# Executive summary

---
<!-- trackio-cell
{"type": "markdown", "id": "cell_gexec_20260719", "created_at": "2026-07-19T12:51:50+00:00", "title": "Executive summary", "pinned": true, "pinned_at": "2026-07-19T12:51:50+00:00"}
-->
This logbook evaluates both challenge claims for *Structure-Preserving Learning Improves Geometry
Generalization in Neural PDEs* (Geo-NeW; arXiv `2602.02788v2`; OpenReview `RtnSbA5AUV`).

- **C1 — VERIFIED.** FEEC incidence identities establish exact conservation for any
  partition-of-unity: `δ₀·1=0`, `1ᵀδ₀ᵀF=0`, and `δ₁δ₀=0`, with independent construction and
  perturbation controls.
- **C2 — FALSIFIED AS WRITTEN.** The challenge says “up to 65% MSE reduction,” but the
  SHA-pinned camera-ready source defines mean per-sample normalized L2 error, contains no MSE or
  standalone 65 statistic, and yields exact best-alternative reductions of 53.478261% and
  49.205585% in its two OOD columns.

The paper supports an OOD advantage in its reported normalized-L2 metric, but it does not report
or permit recovery of the challenged 65% MSE statistic. All 10 tests pass against the pinned arXiv
archive; computations are CPU-only.

Primary artifacts:

- `outputs/geo_new_summary.json`
- `outputs/ood_metric_audit.json`
- `docs/CLAIM2_OOD_METRIC_AUDIT.md`

---
<!-- trackio-cell
{"type": "figure", "id": "cell_geo_new_poster", "created_at": "2026-07-19T13:08:10+00:00", "title": "Two-claim audit poster", "pinned": true, "pinned_at": "2026-07-19T13:08:11+00:00"}
-->
````html
<!-- poster_embed.html -->
<iframe src="poster_embed.html" title="Geo-NeW two-claim reproduction audit poster" width="100%" height="760" loading="lazy"></iframe>
````
