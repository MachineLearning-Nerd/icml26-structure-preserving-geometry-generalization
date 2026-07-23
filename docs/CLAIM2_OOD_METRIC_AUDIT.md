# Claim 2 audit — “65% MSE reduction”

## Verdict

**FALSIFIED AS WRITTEN.** The camera-ready paper reports mean per-sample normalized L2 error,
not MSE, and no 65% statistic appears in its pinned TeX source. The published numeric results do
support an OOD advantage, but they do not support the challenge claim's metric/value pair.

## Pinned primary source

- arXiv `2602.02788v2`, source archive SHA-256
  `c88523e66a538dc8001be383172f919aeac9e359e3c2294a26889c6ffc0ed724`
- `main.tex` SHA-256
  `f51e45f1c59b12a63162c06f9579f8f7935f4687569b1c03bc4d6004a320c8d9`
- `figures/big_table.tex` SHA-256
  `33287c1729cbed1960ea33f4568f682f55c15b3eb9eec167a689852a65db2fbd`
- Figure 6 (`figures/comp_heatmap3.png`) SHA-256
  `4fde9ab44992ab607eefa4664f2ac44b0c67910ec3396fc0146ffa6eb6fc68ec`

The executable verifier checks the archive hash before reading any source member. It then verifies
the paper's metric formula, Table 1 values, and the 7.87%/13.1% mild-extrapolation values directly.

## Independent arithmetic

The paper defines its metric as the mean of per-sample normalized L2 norms. Against the
best-performing reported alternative in each OOD column:

| Evaluation | Geo-NeW | Best alternative | Direct normalized-L2 reduction |
| --- | ---: | ---: | ---: |
| Poly-Poisson OOD | 2.14 | 4.60 (Linear Attention) | 53.478261% |
| NS2d-c++ OOD | 42.2 | 83.08 (GNOT) | 49.205585% |

For the milder geometry regime, the paper reports 7.87% versus 13.1% for the strongest baseline.
That is a 39.923664% reduction in the reported normalized-L2 metric. Mechanically squaring the two
aggregate errors gives a 63.908339% proxy, not 65%; more importantly, the square of an average L2
error is not the unreported mean squared error.

## Source-availability audit

The public official code at `PIMILab/Geo-NeW`, pinned to
`9c30e9320428c10c9a4721c19a9bc0a1639b6716`, has one branch, no tags/releases, and no public pull
request refs. Its demo names `data/processed_polypoisson_id.pt`, but the repository excludes
`data/*.pt` and publishes no dataset, OOD split, model checkpoint, baseline checkpoint, or raw
evaluation output. Public GitHub code search finds only the official repository, its author mirror,
and the prior challenge reproduction; public Hugging Face model/dataset/Space search finds no
Geo-NeW assets from the authors.

This absence blocks a source-scale retraining replay, but it does not weaken the falsification:
the challenged statistic is contradicted by the metric contract and exact values in the paper's
own pinned source.

## Run

```bash
curl -L -o /tmp/2602.02788v2.tar https://arxiv.org/e-print/2602.02788v2
python3 repro/src/run_ood_metric_audit.py --source-tar /tmp/2602.02788v2.tar
python3 -m pytest repro/tests/ --geo-new-source-tar /tmp/2602.02788v2.tar
```

The machine-readable result is `outputs/ood_metric_audit.json`.
