# Claim 4 source audit

The pinned Table 1 source records Poly-Poisson OOD values 2.14 for Geo-NeW
and 4.60 for Linear Attention, giving 53.478% reduction. It records NS2d-c++
OOD values 42.2 for Geo-NeW and 91.40 for Transolver, giving 53.829%
reduction. However, GNOT is lower than Transolver at 83.08; against the
strongest listed alternative the NS2d-c++ reduction is 49.206%.

The source audit validates what the paper reports, not model performance.
The authors' demo names `data/processed_polypoisson_id.pt`, but that file is
absent. The custom NS2d-c++ data/generator, processed Poly OOD data, and
checkpoints are absent from the release.
