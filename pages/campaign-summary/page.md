# 2026-07-23 campaign summary

The cumulative local-CPU run used:

```bash
uv sync --frozen && uv run python repro/src/run_all.py
```

At Git `5533c695765767ab00cffd30bce03e19420c0781`, the run completed in
12.279662 seconds: 13/13 tests passed, Claims 1 and 5 were `VERIFIED`, and
Claims 2, 3, 4, and 6 were `BLOCKED`.

Two additive CPU routes were then run. The falsifiability node
`0912337502b8c046afc08d68ffcf52448e84f289` completed in 11.185 seconds
with 18 tests: Claims 2–4 rejected injected contradictory observations and
Claim 6 was shown to lack a numerical predicate. The `TOY` mechanism node
`91274c1fd70b2b0613694f2d682d48ddc5c831cb` completed in 22.045 seconds
with 17 tests: all four downscaled analogues and damaged-structure controls
passed. Neither route changed the formal headline verdicts.

The pinned official Geo-NeW repository
`9c30e9320428c10c9a4721c19a9bc0a1639b6716` has one branch, no release,
and a complete tree containing only a README, demo, and four core modules.
It has zero checkpoints, benchmark entrypoints, dataset files, or faithful
benchmark preprocessors. The authors' Hugging Face namespace exposes no
models or datasets. An independent scanner agrees.

Negative control: injecting paths for every required asset role clears every
blocker. This establishes the audit is sensitive to a complete release.
Hugging Face compute was not used because additional CPU cannot reconstruct
missing empirical inputs.
