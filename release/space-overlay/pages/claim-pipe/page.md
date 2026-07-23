# Claim 2 — Pipe benchmark

## Verdict: BLOCKED

**Paper:** Geo-NeW `0.112e-2`, LaMO `0.38e-2`, 71% reduction; mean
per-sample normalized L2 over the standard 1000/200 split, P=32, 5000 epochs.

The standard raw Pipe arrays are public, but the official release has no
Geo-NeW Pipe preprocessor, Pipe training/evaluation entrypoint, optimizer
contract, or checkpoint. The paper reports training on one H200; this
campaign is CPU-only. A substitute preprocessor, architecture, split, or
short training run would be a proxy and cannot decide the exact claim.

Machine blocker set: `checkpoint`, `preprocessing`, `pipe_training`.
