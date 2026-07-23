# Method

Four deterministic CPU-scale analogues test the mechanism suggested by the
paper without claiming to reproduce its benchmark numbers:

1. Pipe: analytic 1D parabolic profiles under out-of-range height changes.
2. Elasticity: a 1D axial-bar derived-stress law.
3. Poly-Poisson: finite-difference Poisson solves with train polygons of three
   or four sides and held-out polygons of six to eight sides.
4. Angled step: finite-difference scalar Poisson solves on domains swept from
   15 to 30 degrees after fitting on 0, 5, and 10 degrees.

Each analogue compares a geometry-aware constrained solve with a direct affine
or mean-template surrogate. A deliberately damaged geometry or constitutive
operator is the negative control. Mean per-case normalized L2 error receives a
deterministic 2,000-resample bootstrap interval.

The suite is labeled `TOY`. It substitutes the PDEs, data, architectures,
training sizes, and baselines, so it cannot verify or falsify Claims 2, 3, 4,
or 6.

