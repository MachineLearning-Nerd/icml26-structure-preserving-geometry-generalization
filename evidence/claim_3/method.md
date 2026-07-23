# Claim 3 method and limitations

The same pinned release-inventory audit used for Claim 2 checks all files in
the official repository and the authors' Hugging Face namespace. An
independent scanner checks for weights, preprocessing, benchmark entrypoints,
and data. Its injected complete-manifest negative control must clear the
blocker.

Raw benchmark arrays are necessary but not sufficient. The missing Geo-NeW
preprocessing/training contract and checkpoint prevent faithful evaluation;
the reported 10000 H200 epochs are also outside the authorized CPU envelope.
The result is `BLOCKED`.
