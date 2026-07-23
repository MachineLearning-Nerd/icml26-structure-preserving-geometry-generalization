# Method

This auxiliary audit converts the numeric portions of Claims 2–4 into
executable accept/reject rules. Displayed values are interpreted as rounded
measurements, with half a final displayed unit on either side. The checker
recomputes every reduction, tests whether the stated integer percentage is
compatible with those intervals, and injects a target error 20% worse than the
comparator as a counterexample that must be rejected.

Claim 6 is audited separately because the paper uses the qualitative predicate
“meaningful” without a numerical threshold. The audit lists the minimum
preregistration required to make that statement machine-checkable. It does not
invent a threshold.

This is a decision-rule and negative-control audit, not a Geo-NeW evaluation.
It cannot change a headline claim verdict.

