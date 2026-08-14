# Research and audit log

## Paper identity

The repository identifier `RtnSbA5AUV` resolves to *Structure-Preserving
Learning Improves Geometry Generalization in Neural PDEs*. The primary paper
record is arXiv `2602.02788v2`; the authors are Benjamin D. Shaffer, Shawn
Koohy, Brooks Kinch, M. Ani Hsieh, and Nathaniel Trask. The paper introduces
General-Geometry Neural Whitney Forms (Geo-NeW), a geometry-conditioned neural
PDE method using learned reduced spaces and FEEC-compatible structure.

## Evidence decisions

1. The existing C1 conservation producer was retained and documented as a
   structural mechanism test. Its exact identities and perturbation control
   support `VERIFIED`.
2. The existing C5 boundary producer was retained and documented as an exact
   parameterization test. Its constrained/unconstrained comparison supports
   `VERIFIED`.
3. The source-only “65% MSE” audit was separated from empirical performance:
   the paper's pinned source defines mean per-sample normalized L2 error, so
   the audit is provenance and metric clarification, not a new model verdict.
4. The official-code inventory was used as the boundary for C2, C3, C4, and
   C6. Missing checkpoints, preprocessing, benchmark entrypoints, and custom
   OOD data make those claims `BLOCKED`; toy experiments remain explicitly
   labelled `TOY`.
5. Historical external publication state is retained only as provenance. It
   is not used to claim a current score or to fill missing GitHub evidence.

## Cleanup decisions

- The repository is renamed to `icml26-structure-preserving-geometry-generalization`.
- `master` becomes the sole canonical `main` branch.
- Historical `orx/` branches become purpose-based `baseline/`, `audit/`,
  `experiment/`, and `release/` branches.
- Tracked `.trackio` publication state and the stale root `logbook.json` are
  removed from the canonical GitHub surface.
- Reachable commit attribution is normalized to
  `MachineLearning-Nerd <MachineLearning-Nerd@users.noreply.github.com>`.

## Reproduction boundary

The final gate checks the committed claim contracts and results. A future
reproduction can upgrade a blocked claim only after acquiring the exact public
inputs and protocol recorded in that claim's evidence directory.
