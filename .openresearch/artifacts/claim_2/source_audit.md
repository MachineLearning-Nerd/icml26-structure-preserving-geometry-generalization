# Claim 2 source audit

Pinned `main.tex` Section 4.4 defines the metric as the mean of each sample's
normalized L2 error. Table 2 reports Pipe `0.11` (display precision, x1e-2)
for Geo-NeW and `0.38` for LaMO; the prose gives `0.112e-2` and a 71%
reduction. Appendix Tables 5–6 specify P=32, 5000 epochs, batch size 16,
learning rate 1e-3, 1000 training samples, 200 test samples, and 16641 mesh
nodes. The paper says all models were trained and evaluated on one H200 GPU.

The public standard Pipe arrays are linked by the Geo-FNO benchmark
repository, but the authors' Geo-NeW release does not contain a Pipe
preprocessor, Pipe training entrypoint, or Pipe checkpoint.
