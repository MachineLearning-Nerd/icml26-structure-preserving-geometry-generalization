# Geo-NeW claim-by-claim reproduction

This additive campaign preserves every file from judged revision
`8753eb9a662a446337f02a7773eddece8f64a3af` and adds exact contracts for all
six claims.

| Claim | Verdict | Evidence boundary |
|---|---|---|
| C1 FEEC conservation | **VERIFIED** | exact identities, independent incidence, perturbation control |
| C2 Pipe | **BLOCKED** | no released Geo-NeW Pipe preprocessor/checkpoint/training contract |
| C3 Elasticity | **BLOCKED** | no released Geo-NeW Elasticity preprocessor/checkpoint/training contract |
| C4 Poly / NS2d-c++ OOD | **BLOCKED** | custom OOD data/models absent |
| C5 exact Dirichlet BC | **VERIFIED** | `1.78e-15` vs `9.3071` unconstrained control |
| C6 angled steps | **BLOCKED** | custom data/models absent; “meaningful” has no numerical threshold |

Each blocked claim now has three separately labeled routes: exact public-asset
recovery, an executable falsification/readiness audit, and a CPU-scale `TOY`
mechanism experiment. The toy results do not change the formal verdicts.

The source-only OOD metric page remains available as protected historical
evidence. It does not decide empirical model performance. No new judge score
is claimed before a live verdict.
