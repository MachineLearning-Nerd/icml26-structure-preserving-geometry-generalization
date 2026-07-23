# Claim 4 method and limitations

The verifier checks the exact source archive and independently recomputes all
percentage reductions using decimal arithmetic. The release audit then
checks whether the data, preprocessing, and model outputs required for an
independent empirical test exist. A synthetic complete release is the
negative control for blocker detection.

The old source-only metric audit is retained as useful provenance but cannot
decide this empirical claim. Since neither custom OOD benchmark can be
reconstructed from the public release, the result is `BLOCKED`.
