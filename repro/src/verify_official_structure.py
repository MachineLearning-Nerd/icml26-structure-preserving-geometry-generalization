"""Verify Claims 1 and 5 directly against the OFFICIAL Geo-NeW release.

The previously judged evidence for these two claims used a clean-room
reimplementation of the incidence structure. This verifier instead exercises the
released code (`upstream/`, pinned at 9c30e9320428c10c9a4721c19a9bc0a1639b6716)
end to end, so the structural guarantees are demonstrated on the artifact the
paper actually publishes.

Claim 1 (FEEC exact conservation). Checked at three increasing levels of
strength:
  C1.a  delta_0 @ 1 == 0 exactly, over a sweep of P, using the official
        `utils.construct_delta0`. Constant fields have zero coboundary.
  C1.b  delta_1 @ delta_0 == 0 exactly (the FEEC identity d^2 = 0).
  C1.c  The conservation identity as it appears inside the official residual:
        the flux contribution assembled by `GeoNew.G_residual`,
        `einsum("bji,bjf->bif", delta_0, flux)`, sums to exactly zero over the
        partition-of-unity index for arbitrary fluxes. This is the statement
        that the learned flux model can redistribute but never create or
        destroy the conserved quantity.

Claim 5 (exact Dirichlet enforcement). The official `GeoNew.forward` is run on a
real triangular mesh with randomly initialised weights, and the predicted field
is compared with the imposed boundary values at Dirichlet nodes. Random weights
are the worst case: they show the guarantee is architectural, not learned.

Every check has a negative control that must FAIL for the evidence to mean
anything. The script exits nonzero if any check fails or if any negative control
does not trip.
"""
import argparse
import json
import os
import platform
import subprocess
import sys

import numpy as np
import skfem
import torch
from skfem.models.poisson import laplace, mass

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(REPO_ROOT, "upstream"))

import src.utils as utils  # noqa: E402  (official Geo-NeW release)

UPSTREAM_SHA = "9c30e9320428c10c9a4721c19a9bc0a1639b6716"
P_SWEEP = [3, 4, 5, 8, 12, 16, 19, 35]
TOKEN_DIM = 13


# ---------------------------------------------------------------- Claim 1 ----
def build_delta1(P):
    """Coboundary from 1-forms (edges) to 2-forms (triangles) on the complete
    simplex, with orientation matching the official edge ordering (i<j)."""
    edges = [(i, j) for i in range(P) for j in range(i + 1, P)]
    eidx = {e: k for k, e in enumerate(edges)}
    tris = [(i, j, k) for i in range(P) for j in range(i + 1, P) for k in range(j + 1, P)]
    d1 = np.zeros((len(tris), len(edges)), dtype=np.int64)
    for t, (i, j, k) in enumerate(tris):
        d1[t, eidx[(j, k)]] += 1
        d1[t, eidx[(i, k)]] -= 1
        d1[t, eidx[(i, j)]] += 1
    return d1


def claim1(seed):
    rng = np.random.default_rng(seed)
    rows, ok = [], True

    for P in P_SWEEP:
        d0 = utils.construct_delta0(P).numpy()
        # Official delta_0 maps node values -> edge differences; entries are +-1.
        const_residual = int(np.abs(d0 @ np.ones(P, dtype=np.int64)).max())

        d1 = build_delta1(P)
        d2_residual = int(np.abs(d1 @ d0.astype(np.int64)).max())

        # Global conservation through the residual's flux assembly.
        flux = torch.tensor(rng.normal(size=(4, d0.shape[0], 3)), dtype=torch.float64)
        d0_t = torch.tensor(d0, dtype=torch.float64).unsqueeze(0).expand(4, -1, -1)
        flux_term = torch.einsum("bji,bjf->bif", d0_t, flux)
        global_imbalance = float(flux_term.sum(dim=1).abs().max())

        row = {
            "P": P,
            "n_edges": int(d0.shape[0]),
            "delta0_times_ones_max_abs": const_residual,
            "delta1_delta0_max_abs": d2_residual,
            "flux_global_imbalance_max_abs": global_imbalance,
            "entries_are_pm1": bool(set(np.unique(d0)).issubset({-1, 0, 1})),
        }
        # Integer-exact identities; float64 imbalance limited by summation roundoff.
        row["pass"] = (
            const_residual == 0
            and d2_residual == 0
            and global_imbalance < 1e-12
            and row["entries_are_pm1"]
        )
        ok = ok and row["pass"]
        rows.append(row)

    # Negative control: perturb one incidence entry; conservation must break.
    P = 8
    d0 = utils.construct_delta0(P).numpy().astype(np.int64).copy()
    d0[0, 0] += 1
    nc_const = int(np.abs(d0 @ np.ones(P, dtype=np.int64)).max())
    flux = torch.tensor(rng.normal(size=(4, d0.shape[0], 3)), dtype=torch.float64)
    d0_t = torch.tensor(d0, dtype=torch.float64).unsqueeze(0).expand(4, -1, -1)
    nc_imbalance = float(
        torch.einsum("bji,bjf->bif", d0_t, flux).sum(dim=1).abs().max()
    )
    neg = {
        "description": "single incidence entry perturbed by +1 at P=8",
        "delta0_times_ones_max_abs": nc_const,
        "flux_global_imbalance_max_abs": nc_imbalance,
        "tripped": nc_const != 0 and nc_imbalance > 1e-8,
    }
    return {"per_P": rows, "negative_control": neg,
            "pass": ok and neg["tripped"]}


# ---------------------------------------------------------------- Claim 5 ----
def mesh_inputs(refine, batch, seed):
    torch.manual_seed(seed)
    m = skfem.MeshTri().refined(refine)
    basis = skfem.Basis(m, skfem.ElementTriP1())
    K, M = skfem.asm(laplace, basis).tocoo(), skfem.asm(mass, basis).tocoo()

    def sp(A):
        idx = torch.tensor(np.vstack([A.row, A.col]), dtype=torch.long)
        return torch.sparse_coo_tensor(
            idx, torch.tensor(A.data, dtype=torch.float32), A.shape
        ).coalesce()

    N = m.p.shape[1]
    bnodes = m.boundary_nodes()
    dirichlet = torch.zeros(batch, N, 1, dtype=torch.bool)
    dirichlet[:, bnodes, :] = True
    u_true = torch.randn(batch, N, 1)
    return {
        "N": N, "bnodes": bnodes,
        "K_list": [sp(K)] * batch, "M_list": [sp(M)] * batch,
        "tokens": torch.randn(batch, N, TOKEN_DIM),
        "dirichlet": dirichlet,
        "u_true": u_true,
        "boundary_vals": u_true * dirichlet.to(u_true.dtype),
    }


def claim5(seeds, refine=4, batch=4, n_pou=8):
    rows, ok = [], True
    for seed in seeds:
        d = mesh_inputs(refine, batch, seed)
        model = utils.setup_GeoNew_model(
            n_pou=n_pou, n_fields=1, encoder_in_dim=TOKEN_DIM
        )
        with torch.no_grad():
            out = model(
                in_tokens=d["tokens"], K_list=d["K_list"], M_list=d["M_list"],
                dirichlet_nodes=d["dirichlet"], boundary_vals=d["boundary_vals"],
            )
        u_pred = out["u_fine"]
        bmask = d["dirichlet"]
        err = (u_pred - d["boundary_vals"]).abs()[bmask]
        max_bc_err = float(err.max())
        interior = (~bmask)
        rows.append({
            "seed": seed,
            "N_nodes": d["N"],
            "n_boundary_nodes": int(len(d["bnodes"])),
            "max_boundary_abs_err": max_bc_err,
            "mean_boundary_abs_err": float(err.mean()),
            "interior_pred_absmax": float(u_pred[interior].abs().max()),
            "dtype": str(u_pred.dtype),
            "pass": max_bc_err < 1e-5,  # float32 model; see method.md
        })
        ok = ok and rows[-1]["pass"]

    # Negative control: an unconstrained network of the same width, no
    # structure-preserving parameterisation, on the same boundary data.
    d = mesh_inputs(refine, batch, seeds[0])
    torch.manual_seed(seeds[0])
    net = torch.nn.Sequential(
        torch.nn.Linear(TOKEN_DIM, 64), torch.nn.GELU(), torch.nn.Linear(64, 1)
    )
    with torch.no_grad():
        u_unc = net(d["tokens"])
    nc_err = float((u_unc - d["boundary_vals"]).abs()[d["dirichlet"]].max())
    neg = {
        "description": "unconstrained MLP on identical tokens/boundary data",
        "max_boundary_abs_err": nc_err,
        "tripped": nc_err > 1e-3,
    }
    return {"per_seed": rows, "negative_control": neg, "pass": ok and neg["tripped"]}


# ------------------------------------------------------------------ main ----
def environment():
    def sh(cmd, cwd=None):
        return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True,
                              check=False).stdout.strip()
    return {
        "cpu": sh(["sysctl", "-n", "machdep.cpu.brand_string"]) or platform.processor(),
        "platform": platform.platform(),
        "python": sys.version.split()[0],
        "torch": torch.__version__,
        "numpy": np.__version__,
        "skfem": skfem.__version__,
        "torch_threads": torch.get_num_threads(),
        "repo_git_sha": sh(["git", "rev-parse", "HEAD"], cwd=REPO_ROOT),
        "upstream_geo_new_sha": UPSTREAM_SHA,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--seeds", default="0,1,2,3,4")
    ap.add_argument("--out", default=os.path.join(
        REPO_ROOT, ".openresearch/artifacts/official_structure/raw_results.json"))
    args = ap.parse_args()

    seeds = [int(s) for s in args.seeds.split(",")]
    c1 = claim1(args.seed)
    c5 = claim5(seeds)

    payload = {
        "description": "Claims 1 and 5 verified against the official Geo-NeW release.",
        "environment": environment(),
        "seed": args.seed,
        "claim_1_feec_conservation": c1,
        "claim_5_exact_dirichlet": c5,
        "overall_pass": bool(c1["pass"] and c5["pass"]),
    }
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w") as fh:
        json.dump(payload, fh, indent=2)

    print(f"C1 FEEC conservation : {'PASS' if c1['pass'] else 'FAIL'}")
    for r in c1["per_P"]:
        print(f"   P={r['P']:3d} edges={r['n_edges']:4d} "
              f"d0*1={r['delta0_times_ones_max_abs']} "
              f"d1d0={r['delta1_delta0_max_abs']} "
              f"flux_imbalance={r['flux_global_imbalance_max_abs']:.2e}")
    print(f"   negative control tripped: {c1['negative_control']['tripped']}")
    print(f"C5 exact Dirichlet   : {'PASS' if c5['pass'] else 'FAIL'}")
    for r in c5["per_seed"]:
        print(f"   seed={r['seed']} N={r['N_nodes']} "
              f"bnodes={r['n_boundary_nodes']} "
              f"max_bc_err={r['max_boundary_abs_err']:.3e} "
              f"interior_absmax={r['interior_pred_absmax']:.3e}")
    print(f"   negative control max_bc_err="
          f"{c5['negative_control']['max_boundary_abs_err']:.3e} "
          f"tripped={c5['negative_control']['tripped']}")
    print(f"wrote {args.out}")
    return 0 if payload["overall_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
