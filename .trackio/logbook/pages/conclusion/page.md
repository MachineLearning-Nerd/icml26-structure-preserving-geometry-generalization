# Conclusion

---
<!-- trackio-cell
{"type": "markdown", "id": "cell_gexec_01", "created_at": "2026-07-17T22:09:00+00:00", "title": "Executive summary", "pinned": true, "pinned_at": "2026-07-17T22:09:05+00:00"}
-->
**C1 reproduced.** *Geo-NeW* (Shaffer et al.; `RtnSbA5AUV`) — exact conservation via FEEC — is verified:
`δ₀·1=0` integer-exact, global mass conservation (`1ᵀδ₀ᵀF=0` over 150 fluxes), and the FEEC exact
sequence `δ₁δ₀=0`, all holding for any partition-of-unity (no training), cross-checked against the
official `construct_delta0` and an independent incidence, with a perturbation negative control.

- **C1 (FEEC conservation) — VERIFIED.** Integer-exact conservation identities.

5/5 pytest tests pass. CPU only, exact.

## Scope & cost
| | This reproduction | Full replication |
| --- | --- | --- |
| Scope | C1 FEEC conservation (exact) | + C2 MSE-reduction (GPU training) |
| Hardware | 4 vCPU CPU | GPU |
| Time | < 1 min | — |
| Cost | 0 | — |
| Outcome | C1 VERIFIED | — |

## Honest deviations
- C1 (conservation) verified exactly (any POU, no training). C2 (MSE reduction) needs ~3M-param
  transformer training (SOAP/Muon, COMSOL data) — out of scope.
- Official `PIMILab/Geo-NeW` cross-checks the incidence; clean-room numpy.
