# Claim 2 — OOD MSE-reduction metric audit

---
<!-- trackio-cell
{"type": "markdown", "id": "cell_gc2_01", "created_at": "2026-07-19T12:52:00+00:00", "title": "Claim and verdict"}
-->
**Claim (verbatim):** “Achieves up to 65% MSE reduction compared with best-performing alternatives
on out-of-distribution geometries.”

**Verdict: FALSIFIED AS WRITTEN.** The camera-ready paper's executable source contract uses mean
per-sample normalized L2 error, not MSE. Its `main.tex` contains zero case-insensitive MSE mentions
and zero standalone numeric 65 mentions. The broader claim that Geo-NeW improves OOD error is
supported, but this particular metric/value pair is not.

---
<!-- trackio-cell
{"type": "code", "id": "cell_gc2_02", "created_at": "2026-07-19T12:52:10+00:00", "title": "Pinned-source verifier", "command": ["python", "repro/src/run_ood_metric_audit.py", "--source-tar", "/tmp/2602.02788v2.tar"], "exit_code": 0}
-->
````bash
$ python repro/src/run_ood_metric_audit.py --source-tar /tmp/2602.02788v2.tar
````

- arXiv source archive SHA-256:
  `c88523e66a538dc8001be383172f919aeac9e359e3c2294a26889c6ffc0ed724` ✓
- Metric formula, Table 1 rows, and mild-regime values read directly from that archive ✓
- `MSE`/“mean-squared error” mentions in `main.tex`: **0**
- standalone numeric `65` mentions in `main.tex`: **0**

| OOD evaluation | Geo-NeW | Best alternative | Reduction in reported normalized L2 |
| --- | ---: | ---: | ---: |
| Poly-Poisson | 2.14 | 4.60, Linear Attention | **53.478261%** |
| NS2d-c++ | 42.2 | 83.08, GNOT | **49.205585%** |

The paper's mild regime reports 7.87% versus 13.1%: a **39.923664%** normalized-L2 reduction.
Squaring those aggregates produces 63.908339%, not 65%; more importantly, squaring a mean of
per-sample L2 norms is not a mean squared error and cannot recover the unreported MSE.

Machine-readable evidence: `outputs/ood_metric_audit.json`.

---
<!-- trackio-cell
{"type": "markdown", "id": "cell_gc2_03", "created_at": "2026-07-19T12:52:20+00:00", "title": "Source-scale replay boundary and controls"}
-->
The official code commit `9c30e9320428c10c9a4721c19a9bc0a1639b6716` names
`data/processed_polypoisson_id.pt`, but publishes no data file, OOD data, checkpoints, baseline
outputs, or raw Figure 6 values. The repository has one branch and no tags/releases; public GitHub
and Hugging Face searches found no author-published assets elsewhere.

Two controls prevent headline inflation: the verifier chooses the minimum alternative error before
computing each reduction, and it reports the invalid squared-aggregate proxy separately rather than
silently relabeling it MSE. Asset absence blocks source-scale retraining, but does not weaken this
falsification: the challenged statistic is incompatible with the paper's metric and exact values.

