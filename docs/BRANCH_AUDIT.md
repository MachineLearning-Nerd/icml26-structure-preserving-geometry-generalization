# Branch audit

The repository was audited from the public state below. The original default
branch was `master`, and the experiment branches used the `orx/` namespace.
They are renamed to purpose-based public names as part of this cleanup; their
contents and experiment lineage are retained.

## Original public refs

| Original ref | Tip at audit start | What it contains |
| --- | --- | --- |
| `master` | `4d3bf088811abf0a5f24f64e216afe2a128463e8` | integrated publication surface and current claim ledger |
| `orx/validated-4-12-baseline` | `c9a5f24ba92de8e6302a22b3f3c0b543f9ba550f` | first validated C1/C5 baseline and locked runner |
| `orx/exact-claim-contracts-and-public-asset-audit` | `5533c695765767ab00cffd30bce03e19420c0781` | exact contracts and official-release inventory |
| `orx/durable-evidence-and-release-candidate` | `c96fed060ebea1ef7c48c8e0e9398c8615ffcf4b` | durable evidence, report, notebook, and release candidate |
| `orx/preregistered-falsifiability-and-counterexample` | `0912337502b8c046afc08d68ffcf52448e84f289` | executable counterexamples and C6 identifiability audit |
| `orx/cpu-toy-geometry-mechanism-suite` | `91274c1fd70b2b0613694f2d682d48ddc5c831cb` | explicitly downscaled CPU mechanism experiments |
| `orx/integrated-multi-route-evidence-candidate` | `45b2a55bdee067a4d9f71fb7ab76548fcf370987` | integrated exact, falsifiability, and toy evidence |
| `orx/official-code-cost-and-reachability` | `90ba5ccbdac55f96d9594d707864940d7d6ed6bc` | official-code structure and per-benchmark reachability audit |

## Final public names

| Final ref | Former ref | Purpose |
| --- | --- | --- |
| `main` | `master` | canonical publication surface |
| `baseline/validated-4-12` | `orx/validated-4-12-baseline` | validated baseline |
| `audit/exact-claim-contracts` | `orx/exact-claim-contracts-and-public-asset-audit` | claim contracts and asset inventory |
| `release/durable-evidence-candidate` | `orx/durable-evidence-and-release-candidate` | durable release candidate |
| `audit/falsifiability-counterexamples` | `orx/preregistered-falsifiability-and-counterexample` | falsifiability route |
| `experiment/toy-geometry-mechanisms` | `orx/cpu-toy-geometry-mechanism-suite` | CPU toy mechanism route |
| `release/integrated-evidence-candidate` | `orx/integrated-multi-route-evidence-candidate` | integrated evidence route |
| `audit/official-code-reachability` | `orx/official-code-cost-and-reachability` | official release reachability |

The final branch set is intentionally free of `orx/` names. Branch-specific
results are historical experiment surfaces; only `main` is the canonical
claim-status and documentation surface.

## Identity requirement

After the cleanup, every reachable commit on the published branch set must use
the exact author and committer identity:

```text
MachineLearning-Nerd <MachineLearning-Nerd@users.noreply.github.com>
```

The final GitHub branch list and commit identities are verified outside the
repository through the GitHub API and recorded in the collection tracker.
