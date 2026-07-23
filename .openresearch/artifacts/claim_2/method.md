# Claim 2 method and limitations

The public-release audit pins the authors' repository at
`9c30e9320428c10c9a4721c19a9bc0a1639b6716`, enumerates its full tree,
checks the authors' Hugging Face namespace, and verifies the exact demo input
contract. A second scanner independently looks for dataset, checkpoint,
preprocessing, and benchmark-training artifacts. A synthetic manifest
negative control must remove the corresponding blocker.

The standard raw arrays alone cannot evaluate Geo-NeW. Full paper training
used 5000 epochs on an H200, while this campaign is CPU-only. More
importantly, the released code omits the faithful Pipe preprocessing and
training pipeline. Therefore no scientifically valid Pipe model output can be
generated; the exact claim is `BLOCKED`, not approximated with a proxy.
