import numpy as np

from toy_mechanism_suite import (
    independently_check,
    normalized_l2,
    pipe_analogue,
    run_suite,
)


def test_normalized_l2_rejects_zero_target():
    with np.testing.assert_raises(ValueError):
        normalized_l2(np.zeros(3), np.zeros(3))


def test_pipe_damaged_geometry_is_detected():
    rows, diagnostics = pipe_analogue()
    structured = [
        row["normalized_l2"]
        for row in rows
        if row["method"] == "structured_analogue"
    ]
    damaged = [
        row["normalized_l2"]
        for row in rows
        if row["method"] == "damaged_geometry_control"
    ]
    assert max(structured) < 1e-12
    assert np.mean(damaged) > np.mean(structured)
    assert diagnostics["deviations"]


def test_suite_is_toy_and_cannot_change_headline_verdicts():
    result = run_suite()
    assert result["scale_label"] == "TOY"
    assert set(result["formal_claim_verdicts_unchanged"].values()) == {"BLOCKED"}
    assert all(result["negative_controls_pass"].values())
    assert independently_check(result)["passed"]


def test_angle_threshold_is_explicitly_toy_only():
    result = run_suite()
    deviations = result["diagnostics"]["6"]["deviations"]
    assert any("threshold" in item and "toy" in item for item in deviations)

