# Conclusion

---
<!-- trackio-cell
{"type": "markdown", "id": "cell_gexec_01", "created_at": "2026-07-17T22:09:00+00:00", "title": "Executive summary", "pinned": true, "pinned_at": "2026-07-17T22:09:05+00:00"}
-->
**Both challenge claims are now decided.** *Geo-NeW* (Shaffer et al.; `RtnSbA5AUV`) has one
verified claim and one claim falsified as written.

- **C1 (FEEC conservation) — VERIFIED.** Integer-exact conservation identities.
- **C2 (65% OOD MSE reduction) — FALSIFIED AS WRITTEN.** The pinned camera-ready source reports
  normalized L2, not MSE; no numeric 65 statistic occurs; exact direct reductions against the best
  alternatives are 53.478261% and 49.205585%.

10/10 pytest tests pass with the SHA-pinned arXiv source. CPU only.

## Scope & cost
| | This reproduction | Full replication |
| --- | --- | --- |
| Scope | C1 exact identities + C2 pinned-source metric audit | Source-scale empirical retraining |
| Hardware | CPU | GPU + unpublished COMSOL datasets/checkpoints |
| Time | < 1 min | Not runnable from released assets |
| Cost | 0 | — |
| Outcome | C1 VERIFIED; C2 FALSIFIED AS WRITTEN | Blocked by absent official assets |

## Honest deviations
- C1 conservation is verified exactly (any POU, no training).
- C2 is a claim-contract falsification, not a source-scale retraining. The official code omits its
  named Poly-Poisson file, OOD dataset, checkpoints, baseline outputs, and raw Figure 6 values.
- Official `PIMILab/Geo-NeW` cross-checks the incidence; clean-room numpy.

---
<!-- trackio-cell
{"type": "code", "id": "cell_geo_new_tests", "created_at": "2026-07-19T13:08:20+00:00", "title": "Full verification suite", "command": ["uv", "run", "--with", "pytest", "python", "-m", "pytest", "repro/tests/", "--geo-new-source-tar", "/tmp/2602.02788v2.tar", "-q"], "exit_code": 0, "duration_s": 3.19}
-->
````bash
$ uv run --with pytest python -m pytest repro/tests/ --geo-new-source-tar /tmp/2602.02788v2.tar -q
````

exit 0 · 3.2s

````output
..........                                                               [100%]
10 passed in 3.19s
````

---
<!-- trackio-cell
{"type": "artifact", "id": "cell_08009cb6b028", "created_at": "2026-07-19T12:59:53+00:00", "title": "Portable two-claim reproduction bundle", "artifact": "reproduction-geo-new-conservation/repro-bundle:v1", "artifact_type": "reproduction"}
-->
**📦 Artifact** `reproduction-geo-new-conservation/repro-bundle:v1` · reproduction · 0.5 MB

https://huggingface.co/buckets/DineshAI/RtnSbA5AUV-artifacts#reproduction-geo-new-conservation/repro-bundle:v1
