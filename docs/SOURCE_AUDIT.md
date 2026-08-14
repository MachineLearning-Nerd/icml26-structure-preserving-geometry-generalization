# Source and provenance audit

## Primary paper

The primary paper record is:

- title: *Structure-Preserving Learning Improves Geometry Generalization in Neural PDEs*;
- authors: Benjamin D. Shaffer, Shawn Koohy, Brooks Kinch, M. Ani Hsieh, and Nathaniel Trask;
- arXiv: [`2602.02788v2`](https://arxiv.org/abs/2602.02788);
- OpenReview: [`RtnSbA5AUV`](https://openreview.net/forum?id=RtnSbA5AUV); and
- source archive SHA-256:
  `c88523e66a538dc8001be383172f919aeac9e359e3c2294a26889c6ffc0ed724`.

`repro/src/run_all.py` downloads the e-print with a fixed user agent and
refuses to read it if the hash does not match. The source-only metric audit
checks the metric formula and reported table fragments directly from that
archive.

## Official implementation

The official code is [PIMILab/Geo-NeW](https://github.com/PIMILab/Geo-NeW),
pinned at commit
`9c30e9320428c10c9a4721c19a9bc0a1639b6716`. At that snapshot, the release is a
minimal forward/demo implementation containing the model modules and a smoke
test. It does not publish the benchmark checkpoints, benchmark training
entrypoints, faithful Pipe/Elasticity preprocessing, or the custom OOD assets
needed by C2–C4 and C6.

The asset audit checks both the complete GitHub tree and the authors' public
Hugging Face model/dataset inventory. It also injects a synthetic complete
manifest and requires all blockers to clear, so a missing-asset result is not
caused by a broken checker.

## External publication context

The Hugging Face Space
[`DineshAI/RtnSbA5AUV`](https://huggingface.co/spaces/DineshAI/RtnSbA5AUV)
is retained in the repository's historical release artifacts and source
record. It is not treated as a canonical model, dataset, checkpoint, or
benchmark source. A historical judge score is not reported as a reproduction
result.

## What is and is not vendored

The repository commits source code, claim contracts, methods, controls, and
machine-readable audit records. It does not vendor the paper's private or
unreleased benchmark data, trained weights, or generated external-publication
state. The committed `.openresearch/artifacts/` and `evidence/` trees are the
canonical audit records; `.openresearch/cache/` and most generated `outputs/`
files remain local run products. The two gate outputs under `outputs/` are the
small tracked publication review surface.
