# Claim 6 — angled-step geometry

## Verdict: BLOCKED

Figure 1 says Transolver predictions cease to be meaningful past 20 degrees,
while Geo-NeW remains meaningful throughout the tested range; Section 4.4
sets the range through 30 degrees.

A faithful test needs the custom NS2d-c++ geometry distribution, reference
PDE solutions, both trained models, and a paper-grounded operational
threshold for “meaningful.” None is released, and the qualitative threshold
is not numerically defined. An arbitrary CFD geometry or threshold would
change the claim.

Machine blocker set: `checkpoint`, `ns2d_custom_data`.

Exploratory route (`TOY`): on a scalar-Poisson angled-step analogue, a
toy-only threshold of normalized L2 `≤0.10` kept a direct angle extrapolator
acceptable through 25 degrees and a structure-aware solve through 30 degrees.
This does not reproduce the claimed 20-degree Transolver breakpoint.

The exact statement remains non-machine-falsifiable until “meaningful” is
assigned a paper-grounded numerical predicate.
