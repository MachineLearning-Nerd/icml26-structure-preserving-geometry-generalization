# EVAL

Evidence run: `bc430eb2-ddfb-4bee-9711-de47f41cf4e5` at Git
`5533c695765767ab00cffd30bce03e19420c0781`.

- Claim 1: VERIFIED — exact FEEC/incidence identities and perturbation control pass.
- Claim 2: BLOCKED — the released Pipe raw arrays lack the Geo-NeW Pipe preprocessor, training contract, and checkpoint.
- Claim 3: BLOCKED — the released Elasticity raw arrays lack the Geo-NeW FEM preprocessor, training contract, and checkpoint.
- Claim 4: BLOCKED — processed Poly-Poisson OOD and custom NS2d-c++ data/models are absent.
- Claim 5: VERIFIED — exact Dirichlet construction and unconstrained control pass.
- Claim 6: BLOCKED — custom angled-step data/models are absent and “meaningful” has no numerical threshold.
- Source metric audit: PASS (audit only; it does not decide model performance).
- Public-release asset audit: PASS; two scanners agree and the injected complete-release control clears every blocker.
- Independent suite: 13/13 tests pass.

Fixed command: `uv sync --frozen && uv run python repro/src/run_all.py`.
Local CPU runtime: 12.279662 seconds. Hugging Face compute was not used.
