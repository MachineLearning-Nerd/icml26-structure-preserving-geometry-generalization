"""Measure CPU reachability of each Geo-NeW benchmark from the official release.

Runs the released Geo-NeW forward model + differentiable Newton solve at the
mesh size / reduced dimension P / batch size the paper reports for each
benchmark, then extrapolates the measured per-step cost to the paper's own
epoch budget (Table: Geo-NeW hyperparameters).

The point is to replace the assertion "GPU training is out of scope" with a
measured, reproducible cost figure per benchmark, so that a BLOCKED verdict is
evidence-backed rather than an excuse.

Exits nonzero if any configuration fails to run or fails to converge, so the
artifact cannot silently record a broken measurement.
"""
import argparse
import json
import os
import platform
import statistics
import subprocess
import sys
import time

import numpy as np
import skfem
import torch
from skfem.models.poisson import laplace, mass

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(REPO_ROOT, "upstream"))

import src.utils as utils  # noqa: E402  (official Geo-NeW release)

# Paper Table "Geo-NeW hyperparameters" + Table "Dataset sizes and mesh resolutions".
# refine is chosen so the structured mesh node count brackets the paper's N.
BENCHMARKS = [
    # name,            refine, N_paper, P,  batch, train, epochs
    ("poly_poisson",        5,    952,  8,    16,  4498,  2000),
    ("ns2d_cpp",            6,   3565, 16,     8,  3490,  1000),
    ("elasticity",          5,    972, 32,    16,  1000, 10000),
    ("pipe",                7,  16641, 32,    16,  1000,  5000),
]

TOKEN_DIM = 13  # matches the official _compute_tokens feature width used in demo.py


def build_operators(n_refine):
    m = skfem.MeshTri().refined(n_refine)
    basis = skfem.Basis(m, skfem.ElementTriP1())
    K = skfem.asm(laplace, basis).tocoo()
    M = skfem.asm(mass, basis).tocoo()
    return K, M, m.p.T.astype(np.float32), m.boundary_nodes()


def to_torch_sparse(A):
    idx = torch.tensor(np.vstack([A.row, A.col]), dtype=torch.long)
    val = torch.tensor(A.data, dtype=torch.float32)
    return torch.sparse_coo_tensor(idx, val, A.shape).coalesce()


def measure(refine, n_pou, batch, steps, seed=0):
    torch.manual_seed(seed)
    np.random.seed(seed)

    Kc, Mc, coords, bnodes = build_operators(refine)
    N = coords.shape[0]
    Kt, Mt = to_torch_sparse(Kc), to_torch_sparse(Mc)
    K_list = [Kt] * batch
    M_list = [Mt] * batch

    tokens = torch.randn(batch, N, TOKEN_DIM)
    dirichlet = torch.zeros(batch, N, 1, dtype=torch.bool)
    dirichlet[:, bnodes, :] = True
    u_true = torch.randn(batch, N, 1)
    boundary_vals = u_true * dirichlet.to(u_true.dtype)
    n_orig = torch.full((batch,), N, dtype=torch.long)

    model = utils.setup_GeoNew_model(
        n_pou=n_pou, n_fields=1, encoder_in_dim=TOKEN_DIM
    )
    opt = torch.optim.Adam(model.parameters(), lr=1e-3)

    times, convs, iters = [], [], []
    for _ in range(steps):
        t0 = time.perf_counter()
        opt.zero_grad(set_to_none=True)
        out = model(
            in_tokens=tokens, K_list=K_list, M_list=M_list,
            dirichlet_nodes=dirichlet, boundary_vals=boundary_vals,
        )
        loss = utils.relative_l2_error_unpadded(u_true, out["u_fine"], n_orig)
        loss.backward()
        opt.step()
        times.append(time.perf_counter() - t0)
        cv, ni = out["converged"], out["n_iters"]
        convs.append(float(cv.float().mean()) if torch.is_tensor(cv) else float(cv))
        iters.append(float(ni.float().mean()) if torch.is_tensor(ni) else float(ni))

    warm = times[1:] or times
    return {
        "N_nodes": int(N),
        "n_pou": n_pou,
        "batch": batch,
        "params": int(model.get_full_parameter_count()),
        "step_times_s": [round(t, 4) for t in times],
        "median_warm_step_s": round(float(statistics.median(warm)), 4),
        "newton_iters_mean": iters,
        "converged_frac": convs,
    }


def environment():
    try:
        cpu = subprocess.run(
            ["sysctl", "-n", "machdep.cpu.brand_string"],
            capture_output=True, text=True, check=False,
        ).stdout.strip()
    except Exception:
        cpu = platform.processor()
    try:
        sha = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=REPO_ROOT,
            capture_output=True, text=True, check=False,
        ).stdout.strip()
    except Exception:
        sha = "unknown"
    return {
        "cpu": cpu,
        "platform": platform.platform(),
        "python": sys.version.split()[0],
        "torch": torch.__version__,
        "torch_threads": torch.get_num_threads(),
        "numpy": np.__version__,
        "skfem": skfem.__version__,
        "repo_git_sha": sha,
        "upstream_geo_new_sha": "9c30e9320428c10c9a4721c19a9bc0a1639b6716",
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--steps", type=int, default=3)
    ap.add_argument("--out", default=os.path.join(
        REPO_ROOT, ".openresearch/artifacts/compute_reachability/raw_results.json"))
    ap.add_argument("--only", default=None, help="comma-separated benchmark names")
    args = ap.parse_args()

    only = set(args.only.split(",")) if args.only else None
    results, failures = [], []

    for name, refine, n_paper, P, batch, train, epochs in BENCHMARKS:
        if only and name not in only:
            continue
        print(f"[measure] {name}: refine={refine} P={P} B={batch} ...", flush=True)
        try:
            r = measure(refine, P, batch, args.steps)
        except Exception as exc:  # a config that cannot run is itself a finding
            failures.append({"benchmark": name, "error": repr(exc)})
            print(f"[measure] {name} FAILED: {exc!r}", flush=True)
            continue

        if min(r["converged_frac"]) < 0.8:
            failures.append({"benchmark": name,
                             "error": f"Newton convergence below 0.8: {r['converged_frac']}"})

        steps_per_epoch = -(-train // batch)
        total_steps = steps_per_epoch * epochs
        wall_s = total_steps * r["median_warm_step_s"]
        r.update({
            "benchmark": name,
            "N_paper": n_paper,
            "paper_train_samples": train,
            "paper_epochs": epochs,
            "steps_per_epoch": steps_per_epoch,
            "paper_total_train_steps": total_steps,
            "projected_wall_clock_s": round(wall_s, 1),
            "projected_wall_clock_h": round(wall_s / 3600.0, 1),
        })
        results.append(r)
        print(f"[measure] {name}: {r['median_warm_step_s']}s/step -> "
              f"{r['projected_wall_clock_h']}h for paper budget", flush=True)

    payload = {
        "description": "Measured CPU cost of the official Geo-NeW release per benchmark, "
                       "extrapolated to the paper's own epoch budget.",
        "environment": environment(),
        "seed": 0,
        "results": results,
        "failures": failures,
    }
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w") as fh:
        json.dump(payload, fh, indent=2)
    print(f"[measure] wrote {args.out}")

    if failures:
        print(f"[measure] FAIL: {len(failures)} configuration(s) failed", file=sys.stderr)
        return 1
    if not results:
        print("[measure] FAIL: no results produced", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
