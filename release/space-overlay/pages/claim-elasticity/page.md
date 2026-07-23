# Claim 3 — Elasticity benchmark

## Verdict: BLOCKED

**Paper:** Geo-NeW `0.351e-2`, LaMO `0.50e-2`, 29% reduction on the derived
von Mises quantity; mean per-sample normalized L2 over 1000/200 samples,
P=32, 10000 epochs.

The standard raw arrays are public, but the official release has no
Geo-NeW FEM/Whitney preprocessor, Elasticity train/eval entrypoint, optimizer
contract, or checkpoint. The exact paper training is H200-scale. CPU
downscaling would not test this claim.

Machine blocker set: `checkpoint`, `preprocessing`, `elasticity_training`.
