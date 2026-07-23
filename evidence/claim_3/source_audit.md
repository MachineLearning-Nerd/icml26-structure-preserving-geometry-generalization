# Claim 3 source audit

Table 2 reports Elasticity `0.35` (x1e-2, derived-quantity dagger) for
Geo-NeW and `0.50` for LaMO; the prose gives `0.351e-2` and a 29% reduction.
Appendix Tables 5–6 specify P=32, 10000 epochs, batch size 16, learning rate
1e-3, 1000 training samples, 200 test samples, and 972 mesh nodes. The metric
is the Section 4.4 mean per-sample normalized L2 error.

The standard Geo-FNO raw Elasticity arrays are public. The authors' Geo-NeW
release does not provide the conversion to its FEM/Whitney input tuple, an
Elasticity training entrypoint, or a checkpoint.
