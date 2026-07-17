#!/usr/bin/env python3
"""Exact tests for Geo-NeW conservation identities (RtnSbA5AUV, C1)."""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "src"))
import geo_new as gn


def test_delta0_ones_zero_integer_exact():
    """delta_0 @ 1 = 0 (incidence structure -> mass conservation)."""
    for P in [3, 4, 5, 8]:
        assert np.max(np.abs(gn.construct_delta0(P) @ np.ones(P))) == 0.0


def test_global_mass_conservation_any_flux():
    """1^T delta_0^T F = 0 for any edge flux F."""
    rng = np.random.default_rng(0)
    for P in [3, 5, 10]:
        d0 = gn.construct_delta0(P)
        for _ in range(30):
            F = rng.standard_normal(d0.shape[0])
            assert abs(np.ones(P) @ d0.T @ F) < 1e-12


def test_feec_d_squared_zero():
    """FEEC exact sequence: delta_1 delta_0 = 0 (boundary of boundary)."""
    d0, d1 = gn.edge_face_incidence_triangle()
    assert np.max(np.abs(d1 @ d0)) == 0.0


def test_incidence_matches_manual_construction():
    """construct_delta0 matches an independent manual complete-graph incidence."""
    P = 6; d0 = gn.construct_delta0(P)
    rows = []
    for j in range(P):
        for i in range(j):
            r = np.zeros(P); r[i] = -1.0; r[j] = 1.0; rows.append(r)
    inc = np.array(rows)
    def rs(M): return sorted(tuple(sorted([(int(np.where(M[k] == -1)[0][0]), -1),
                                           (int(np.where(M[k] == 1)[0][0]), 1)])) for k in range(M.shape[0]))
    assert rs(d0) == rs(inc)


def test_negcontrol_perturbation_breaks_conservation():
    """Perturbing delta_0 breaks delta_0 @ 1 = 0."""
    d0 = gn.construct_delta0(5).copy(); d0[0, 0] += 1e-9
    assert np.max(np.abs(d0 @ np.ones(5))) > 0


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))
