#!/usr/bin/env python3
"""Clean-room Geo-NeW conservation identities (ICML 2026, "Structure-Preserving Learning
Improves Geometry Generalization in Neural PDEs" / Geo-NeW; Shaffer, Koohy, Kinch, Hsieh,
Trask; arXiv 2602.02788; OpenReview RtnSbA5AUV).

Claim C1: Geo-NeW exactly preserves physical conservation laws through Finite Element Exterior
Calculus (FEEC). The conservation is a property of the discrete Whitney/incidence structure
(the complete-graph incidence delta_0 on P control volumes), holding for ANY partition-of-unity
(no training needed):

  (a) delta_0 @ 1 = 0   (integer-exact)  -- the incidence structure; each edge balances.
  (b) Global mass conservation: 1^T delta_0^T F = (delta_0 1)^T F = 0  for ANY edge flux F.
      With pairwise-antisymmetric fluxes F_ij = -F_ji the net flux out of every internal volume
      is balanced exactly (internal fluxes cancel telescopically).
  (c) FEEC exact sequence d^2 = 0: delta_1 delta_0 = 0  (boundary of a boundary is zero) on a
      small mesh -- the discrete grad-curl / div-curl identity.

Official code construct_delta0 (PIMILab/Geo-NeW src/utils.py) builds exactly this complete-graph
incidence; clean-room numpy here matches it.
"""
from __future__ import annotations
import numpy as np


def construct_delta0(P):
    """Complete-graph incidence (edges x nodes), edge (i<j): -1 at i, +1 at j.
    Matches official PIMILab/Geo-NeW construct_delta0(Npou)."""
    n1 = P * (P - 1) // 2
    d = np.zeros((n1, P))
    k = 0
    for i in range(P):
        for j in range(i + 1, P):
            d[k, i] = -1.0
            d[k, j] = 1.0
            k += 1
    return d


def edge_face_incidence_triangle():
    """Triangle mesh FEEC: nodes {0,1,2}, edges e01,e02,e12, one face f012.
    delta_0 (edges x nodes), delta_1 (faces x edges). delta_1 delta_0 = 0 (boundary^2=0)."""
    d0 = np.array([[-1, 1, 0], [-1, 0, 1], [0, -1, 1]], dtype=float)  # e01, e02, e12
    # face f012 boundary = e01 + e12 - e02  (oriented loop 0->1->2->0)
    d1 = np.array([[1, -1, 1]], dtype=float)  # 1 face x 3 edges
    return d0, d1


if __name__ == "__main__":
    P = 5
    d0 = construct_delta0(P)
    print("delta_0 @ 1 =", d0 @ np.ones(P), "(integer-exact zero -> mass conservation)")
    F = np.random.default_rng(0).standard_normal(d0.shape[0])
    print("1^T delta_0^T F =", np.ones(P) @ d0.T @ F, "(global conservation for any flux)")
