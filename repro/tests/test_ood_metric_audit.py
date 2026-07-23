#!/usr/bin/env python3
"""Tests for Geo-NeW C2's OOD metric-contract audit."""
from decimal import Decimal

import pytest

from ood_metric_audit import build_audit, reduction, squared_aggregate_proxy


def test_reduction_rejects_invalid_inputs():
    with pytest.raises(ValueError):
        reduction(Decimal("1"), Decimal("0"))
    with pytest.raises(ValueError):
        reduction(Decimal("-1"), Decimal("2"))


def test_table_1_best_alternative_reductions_are_not_65_percent():
    audit = build_audit()
    rows = audit["table_1_best_alternative_reductions"]
    assert rows[0]["best_alternative"] == "Linear Attention"
    assert rows[0]["direct_l2_reduction_percent"] == "53.478261"
    assert rows[1]["best_alternative"] == "GNOT"
    assert rows[1]["direct_l2_reduction_percent"] == "49.205585"
    assert all(not row["matches_65_percent"] for row in rows)


def test_mild_regime_squaring_is_only_a_proxy_and_still_not_65():
    audit = build_audit()
    mild = audit["mild_extrapolation_text_result"]
    assert mild["direct_l2_reduction_percent"] == "39.923664"
    assert mild["squared_aggregate_proxy_percent"] == "63.908339"
    assert audit["metric_contract"]["same_metric"] is False
    assert audit["empirical_claim_verdict"] == "NOT_DECIDED_BY_SOURCE_AUDIT"


def test_squaring_changes_the_metric_and_the_result():
    candidate = Decimal("7.87")
    baseline = Decimal("13.1")
    assert reduction(candidate, baseline) != squared_aggregate_proxy(candidate, baseline)
    assert squared_aggregate_proxy(candidate, baseline) != Decimal("0.65")


def test_pinned_arxiv_source_contract_if_archive_is_provided(pytestconfig):
    source_tar = pytestconfig.getoption("--geo-new-source-tar", default=None)
    if source_tar is None:
        pytest.skip("pass --geo-new-source-tar to verify the pinned arXiv archive")
    audit = build_audit(source_tar)
    source = audit["pinned_source_audit"]
    assert all(source["fragment_checks"].values())
    assert source["case_insensitive_mse_mentions_in_main_tex"] == 0
    assert source["standalone_65_mentions_in_main_tex"] == 0
