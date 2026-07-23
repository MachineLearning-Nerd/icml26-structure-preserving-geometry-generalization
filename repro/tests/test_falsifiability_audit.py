from decimal import Decimal

from falsifiability_audit import (
    COMPARISONS,
    audit_numeric_comparison,
    evaluate_observation,
    independently_check,
    run_audit,
)


def test_all_numeric_claims_reject_deliberate_counterexamples():
    for spec in COMPARISONS:
        result = audit_numeric_comparison(spec)
        assert result["counterexample_rejected"]
        assert not result["counterexample_control"]["contract_accepts"]


def test_reported_reductions_are_compatible_with_display_precision():
    for spec in COMPARISONS:
        result = audit_numeric_comparison(spec)
        assert result["reported_reduction_compatible_with_display_precision"]


def test_elasticity_center_rounds_to_30_but_29_remains_interval_compatible():
    elasticity = next(spec for spec in COMPARISONS if spec.name == "elasticity")
    result = audit_numeric_comparison(elasticity)
    assert result["center_reduction_rounded_half_up"] == 30
    assert 29 in result["possible_rounded_reduction_integers"]


def test_out_of_interval_observation_is_rejected():
    pipe = next(spec for spec in COMPARISONS if spec.name == "pipe")
    result = evaluate_observation(
        pipe, observed_target=Decimal("0.002"), observed_comparator=pipe.comparator
    )
    assert not result["contract_accepts"]


def test_qualitative_angle_claim_is_not_machine_falsifiable_as_written():
    result = run_audit()
    assert not result["claim_6"]["machine_falsifiable_as_written"]
    assert result["claim_6"]["formal_claim_verdict"] == "BLOCKED"
    assert independently_check(result)["passed"]

