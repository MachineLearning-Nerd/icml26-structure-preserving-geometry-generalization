#!/usr/bin/env python3
"""Independent unit checks for release-asset blocker logic."""
from release_asset_audit import blockers, independent_scan, scan_paths


def test_current_official_tree_shape_is_incomplete():
    paths = [
        "README.md",
        "demo.py",
        "src/geo_new.py",
        "src/models.py",
        "src/nonlinear_solver.py",
        "src/utils.py",
    ]
    missing = blockers(scan_paths(paths))
    assert set(missing) == {"2", "3", "4", "6"}
    assert all(missing.values())
    assert independent_scan(paths)["complete_for_empirical_claims"] is False


def test_injected_complete_manifest_clears_every_blocker():
    complete = [
        "checkpoints/pipe.pt",
        "preprocessing/build_fem.py",
        "train_pipe.py",
        "train_elasticity.py",
        "data/polypoisson_ood.pt",
        "data/ns2d_angled_comsol.pt",
    ]
    assert blockers(scan_paths(complete)) == {"2": [], "3": [], "4": [], "6": []}


def test_weights_without_data_or_entrypoint_remain_blocked():
    partial = ["checkpoints/all.pt", "src/geo_new.py"]
    missing = blockers(scan_paths(partial))
    assert missing["2"]
    assert missing["4"]
    assert independent_scan(partial)["complete_for_empirical_claims"] is False
