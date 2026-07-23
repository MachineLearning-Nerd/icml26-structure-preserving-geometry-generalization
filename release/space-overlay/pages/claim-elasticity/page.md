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

Exploratory route (`TOY`): a 1D axial-stress analogue over 19 areas obtained
mean normalized L2 `0` for the constrained reciprocal-area law, `0.06279` for
an affine regressor, and `0.47368` for the damaged law. These are not the
paper's 2D Elasticity data or models.

The displayed centers imply a 29.8% reduction, which rounds half-up to 30%;
29% remains compatible with the intervals implied by display precision, so
this is not a falsification.
