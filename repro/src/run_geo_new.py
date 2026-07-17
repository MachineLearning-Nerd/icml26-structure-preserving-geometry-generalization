#!/usr/bin/env python3
"""Verify Geo-NeW conservation identities (RtnSbA5AUV, C1).

C1: Geo-NeW exactly preserves physical conservation laws through FEEC.
  (a) delta_0 @ 1 = 0  (integer-exact incidence structure).
  (b) global mass conservation 1^T delta_0^T F = 0 for any flux F (incl. antisymmetric pairwise).
  (c) FEEC d^2=0: delta_1 delta_0 = 0 on a triangle mesh.
Cross-checks: scipy incidence (complete graph); official construct_delta0 structure.
Negative control: perturbing delta_0 breaks conservation.
"""
import os, sys, json
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import geo_new as gn


def incidence_manual(P):
    """Independent complete-graph oriented incidence: edge (i,j), i<j, oriented i->j.
    Different construction (edge ordering by (j,i)) for an independent cross-check."""
    rows = []
    for j in range(P):
        for i in range(j):              # note: (j,i) ordering, i<j
            r = np.zeros(P); r[i] = -1.0; r[j] = 1.0
            rows.append(r)
    return np.array(rows)


def main():
    print("=" * 74)
    print("Geo-NeW conservation identities (RtnSbA5AUV, C1 -- FEEC exact conservation)")
    print("=" * 74)
    res = {}

    # (a) delta_0 @ 1 = 0  (integer-exact), several P
    print("\n(a) delta_0 @ 1 = 0  (incidence structure -> mass conservation), integer-exact:")
    a_ok = True; max_res = 0.0
    for P in [3, 4, 5, 8, 12]:
        d0 = gn.construct_delta0(P)
        r = float(np.max(np.abs(d0 @ np.ones(P))))
        max_res = max(max_res, r); a_ok &= r == 0.0
        print(f"  P={P:2d}: ||delta_0 @ 1||_inf = {r:.1e}  (integer-exact zero)")
    print(f"  -> max {max_res:.1e} (==0): {a_ok}")
    res["delta0_ones"] = dict(ok=bool(a_ok), max_residual=float(max_res))

    # (b) global mass conservation: 1^T delta_0^T F = 0 for ANY flux F
    print("\n(b) global mass conservation 1^T delta_0^T F = 0 (any edge flux F):")
    b_ok = True; max_gb = 0.0
    rng = np.random.default_rng(0)
    for P in [3, 5, 10]:
        d0 = gn.construct_delta0(P)
        for trial in range(50):
            F = rng.standard_normal(d0.shape[0])      # arbitrary flux (incl. antisymmetric)
            gb = abs(float(np.ones(P) @ d0.T @ F))
            max_gb = max(max_gb, gb); b_ok &= gb < 1e-12
    print(f"  max |1^T delta_0^T F| over 150 random fluxes = {max_gb:.2e} (<1e-12): {b_ok}")
    # also explicit antisymmetric pairwise flux on the P=4 complete graph
    P = 4; d0 = gn.construct_delta0(P)
    Fanti = np.zeros(d0.shape[0]); k = 0
    for i in range(P):
        for j in range(i + 1, P):
            Fanti[k] = rng.standard_normal(); k += 1   # F_ij; F_ji = -F_ij encoded by incidence
    net = d0.T @ Fanti                                  # net flux out of each volume
    print(f"  antisymmetric flux: per-volume net flux = {np.round(net, 4)}; global sum = {net.sum():.2e}")
    res["global_conservation"] = dict(ok=bool(b_ok), max_residual=float(max_gb))

    # (c) FEEC d^2 = 0: delta_1 delta_0 = 0 on a triangle mesh (boundary of boundary)
    print("\n(c) FEEC exact sequence d^2=0: delta_1 @ delta_0 = 0 (triangle mesh):")
    d0, d1 = gn.edge_face_incidence_triangle()
    prod = d1 @ d0
    c_ok = bool(np.max(np.abs(prod)) == 0.0)
    print(f"  delta_1 delta_0 = {prod.tolist()[0]},  ||.||_inf = {np.max(np.abs(prod)):.1e} (integer-exact zero)")
    res["feec_d2_zero"] = dict(ok=c_ok)

    # cross-check: independent manual complete-graph incidence matches construct_delta0
    print("\nCross-check: independent manual incidence (complete graph) matches construct_delta0:")
    P = 5; d0 = gn.construct_delta0(P)
    inc = incidence_manual(P)
    def rowsigned(M):
        return sorted(tuple(sorted([(int(np.where(M[k] == -1)[0][0]), -1),
                                    (int(np.where(M[k] == 1)[0][0]), 1)])) for k in range(M.shape[0]))
    cc_ok = rowsigned(d0) == rowsigned(inc)
    print(f"  construct_delta0 edge-set == manual complete-graph incidence: {cc_ok}")
    res["incidence_crosscheck"] = dict(ok=bool(cc_ok))

    # negative control: perturb one delta_0 entry -> conservation breaks
    print("\nNegative control: perturb one delta_0 entry -> delta_0 @ 1 != 0:")
    d0p = gn.construct_delta0(5).copy(); d0p[0, 0] += 1e-9
    nc = float(np.max(np.abs(d0p @ np.ones(5)))) > 0
    print(f"  perturbed ||delta_0 @ 1||_inf = {np.max(np.abs(d0p @ np.ones(5))):.2e} (>0: {nc})")
    res["neg_control"] = dict(ok=bool(nc))

    verified = bool(a_ok and b_ok and c_ok and cc_ok and nc)
    print("\n" + "=" * 74)
    print(f"C1 FEEC CONSERVATION: {'VERIFIED' if verified else 'PARTIAL'}")
    print("=" * 74)
    out = os.path.join(HERE, "..", "..", "outputs", "geo_new_summary.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    json.dump(res, open(out, "w"), indent=2)
    print("wrote", out)


if __name__ == "__main__":
    main()
