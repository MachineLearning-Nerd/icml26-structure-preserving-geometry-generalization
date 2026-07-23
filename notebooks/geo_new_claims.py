import marimo

__generated_with = "0.23.14"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell
def _(mo):
    mo.md(r"""
    # Geo-NeW: what can actually be reproduced?

    This notebook opens with the already-produced evidence. It does not
    retrain a model or require repository-relative data.
    """)
    return


@app.cell
def _():
    claims = [
        {"id": 1, "topic": "FEEC conservation", "paper": "exact", "observed": "zero residuals; perturbation detected", "verdict": "VERIFIED"},
        {"id": 2, "topic": "Pipe", "paper": "0.112e-2 vs 0.38e-2", "observed": "required model pipeline unavailable", "verdict": "BLOCKED"},
        {"id": 3, "topic": "Elasticity", "paper": "0.351e-2 vs 0.50e-2", "observed": "required model pipeline unavailable", "verdict": "BLOCKED"},
        {"id": 4, "topic": "Poly / NS2d-c++ OOD", "paper": "2.14 vs 4.60; 42.2 vs 91.40", "observed": "custom data and models unavailable", "verdict": "BLOCKED"},
        {"id": 5, "topic": "exact boundary values", "paper": "0.00", "observed": "1.78e-15 vs 9.3071 control", "verdict": "VERIFIED"},
        {"id": 6, "topic": "angled steps", "paper": "20° vs 30° behavior", "observed": "custom data/models unavailable", "verdict": "BLOCKED"},
    ]
    return (claims,)


@app.cell
def _(claims, mo):
    mo.md("## Claim ledger")
    mo.ui.table(claims, selection=None)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Why the exact identities work

    If `δ₀` is an oriented incidence matrix, every row has one `-1` and
    one `+1`, so `δ₀ 1 = 0`. Consequently,

    \[
    1^\top δ₀^\top F = (δ₀1)^\top F = 0
    \]

    for every edge flux `F`. This algebraic cancellation is independent
    of training. The formal run also checked `δ₁δ₀=0` and an independent
    incidence implementation.
    """)
    return


@app.cell
def _():
    conservation = {
        "delta0_ones_max": 0.0,
        "global_flux_max_over_150": 0.0,
        "d_squared_max": 0.0,
        "perturbed_delta0_residual": 1e-9,
    }
    boundary = {
        "constrained_max_error": 1.7763568394002505e-15,
        "unconstrained_max_error": 9.3071,
        "boundary_nodes": 4000,
    }
    return boundary, conservation


@app.cell
def _(boundary, conservation, mo):
    mo.md(
        f"""
        ## Embedded formal-run evidence

        - Exact incidence residual: `{conservation["delta0_ones_max"]}`
        - Global flux residual over 150 seeded trials: `{conservation["global_flux_max_over_150"]}`
        - Perturbed-incidence control: `{conservation["perturbed_delta0_residual"]}`
        - Constrained boundary error: `{boundary["constrained_max_error"]:.3e}`
        - Unconstrained control: `{boundary["unconstrained_max_error"]}`
        - Boundary nodes: `{boundary["boundary_nodes"]}`
        """
    )
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## The empirical boundary of the release

    The pinned official repository has no checkpoints, datasets,
    benchmark train/eval entrypoints, or faithful benchmark preprocessors.
    The standard Pipe and Elasticity raw arrays alone do not define the
    paper's Geo-NeW inputs. The Poly-Poisson OOD and NS2d-c++ custom assets
    are absent. A toy replacement would test a nearby claim, not the one
    in the paper.

    Formal command:

    ```bash
    uv sync --frozen && uv run python repro/src/run_all.py
    ```

    Evidence run: `bc430eb2-ddfb-4bee-9711-de47f41cf4e5`, 12.279662
    seconds on local CPU, $0.
    """)
    return


if __name__ == "__main__":
    app.run()
