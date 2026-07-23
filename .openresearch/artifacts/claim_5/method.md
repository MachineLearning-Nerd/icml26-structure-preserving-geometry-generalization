# Claim 5 method

`repro/src/verify_bc.py` uses seeded large random weights to make accidental
agreement implausible, evaluates the constrained parameterization at all
boundary nodes, and compares it with an unconstrained network. The
independent checker requires the constrained error to remain within numerical
roundoff and the unconstrained control to violate the boundary.

The fixed cumulative command regenerates raw output, checker output, runtime
metadata, and the negative-control result.
