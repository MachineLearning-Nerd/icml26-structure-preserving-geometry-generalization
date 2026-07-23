"""Executable decision rules for the four unresolved empirical claims.

This module does not evaluate Geo-NeW.  It checks whether the paper's reported
numbers can be turned into falsifiable contracts, whether their displayed
precision is internally compatible with the stated percentage reductions, and
whether deliberately contradictory observations are rejected.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from itertools import product
from typing import Any


HUNDRED = Decimal("100")


@dataclass(frozen=True)
class NumericComparison:
    name: str
    claim_id: str
    target: Decimal
    target_quantum: Decimal
    comparator: Decimal
    comparator_quantum: Decimal
    reported_reduction_percent: int

    @property
    def target_interval(self) -> tuple[Decimal, Decimal]:
        half = self.target_quantum / 2
        return self.target - half, self.target + half

    @property
    def comparator_interval(self) -> tuple[Decimal, Decimal]:
        half = self.comparator_quantum / 2
        return self.comparator - half, self.comparator + half


COMPARISONS = (
    NumericComparison(
        name="pipe",
        claim_id="2",
        target=Decimal("0.00112"),
        target_quantum=Decimal("0.00001"),
        comparator=Decimal("0.0038"),
        comparator_quantum=Decimal("0.0001"),
        reported_reduction_percent=71,
    ),
    NumericComparison(
        name="elasticity",
        claim_id="3",
        target=Decimal("0.00351"),
        target_quantum=Decimal("0.00001"),
        comparator=Decimal("0.0050"),
        comparator_quantum=Decimal("0.0001"),
        reported_reduction_percent=29,
    ),
    NumericComparison(
        name="poly_poisson_ood",
        claim_id="4",
        target=Decimal("0.0214"),
        target_quantum=Decimal("0.0001"),
        comparator=Decimal("0.0460"),
        comparator_quantum=Decimal("0.0001"),
        reported_reduction_percent=53,
    ),
    NumericComparison(
        name="ns2d_cpp_ood",
        claim_id="4",
        target=Decimal("0.422"),
        target_quantum=Decimal("0.001"),
        comparator=Decimal("0.9140"),
        comparator_quantum=Decimal("0.0001"),
        reported_reduction_percent=54,
    ),
)


def reduction_percent(target: Decimal, comparator: Decimal) -> Decimal:
    return (comparator - target) / comparator * HUNDRED


def rounded_integer(value: Decimal) -> int:
    return int(value.quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def interval_reduction_bounds(spec: NumericComparison) -> tuple[Decimal, Decimal]:
    target_low, target_high = spec.target_interval
    comparator_low, comparator_high = spec.comparator_interval
    values = [
        reduction_percent(target, comparator)
        for target, comparator in product(
            (target_low, target_high), (comparator_low, comparator_high)
        )
    ]
    return min(values), max(values)


def interval_contains(value: Decimal, interval: tuple[Decimal, Decimal]) -> bool:
    low, high = interval
    return low <= value <= high


def evaluate_observation(
    spec: NumericComparison, observed_target: Decimal, observed_comparator: Decimal
) -> dict[str, Any]:
    observed_reduction = reduction_percent(observed_target, observed_comparator)
    target_matches = interval_contains(observed_target, spec.target_interval)
    comparator_matches = interval_contains(
        observed_comparator, spec.comparator_interval
    )
    reduction_matches = (
        rounded_integer(observed_reduction) == spec.reported_reduction_percent
    )
    return {
        "observed_target": str(observed_target),
        "observed_comparator": str(observed_comparator),
        "observed_reduction_percent": str(observed_reduction),
        "target_matches_displayed_interval": target_matches,
        "comparator_matches_displayed_interval": comparator_matches,
        "reduction_rounds_to_reported_integer": reduction_matches,
        "contract_accepts": target_matches and comparator_matches and reduction_matches,
    }


def audit_numeric_comparison(spec: NumericComparison) -> dict[str, Any]:
    reduction_low, reduction_high = interval_reduction_bounds(spec)
    possible_rounded_integers = list(
        range(rounded_integer(reduction_low), rounded_integer(reduction_high) + 1)
    )
    positive = evaluate_observation(spec, spec.target, spec.comparator)
    counterexample = evaluate_observation(
        spec, spec.comparator * Decimal("1.20"), spec.comparator
    )
    return {
        "claim_id": spec.claim_id,
        "paper_target": str(spec.target),
        "paper_comparator": str(spec.comparator),
        "paper_reported_reduction_percent": spec.reported_reduction_percent,
        "target_display_interval": [str(value) for value in spec.target_interval],
        "comparator_display_interval": [
            str(value) for value in spec.comparator_interval
        ],
        "center_reduction_percent": str(
            reduction_percent(spec.target, spec.comparator)
        ),
        "center_reduction_rounded_half_up": rounded_integer(
            reduction_percent(spec.target, spec.comparator)
        ),
        "reduction_interval_percent": [str(reduction_low), str(reduction_high)],
        "possible_rounded_reduction_integers": possible_rounded_integers,
        "reported_reduction_compatible_with_display_precision": (
            spec.reported_reduction_percent in possible_rounded_integers
        ),
        "positive_control": positive,
        "counterexample_control": counterexample,
        "counterexample_rejected": not counterexample["contract_accepts"],
    }


def run_audit() -> dict[str, Any]:
    numeric = {spec.name: audit_numeric_comparison(spec) for spec in COMPARISONS}
    numeric_claims_falsifiable = all(
        item["reported_reduction_compatible_with_display_precision"]
        and item["counterexample_rejected"]
        for item in numeric.values()
    )
    claim_6 = {
        "claim_id": "6",
        "paper_predicate": (
            "Transolver predictions cease to be meaningful beyond 20 degrees "
            "while Geo-NeW remains meaningful through 30 degrees."
        ),
        "machine_falsifiable_as_written": False,
        "reason": (
            "The paper supplies no numerical predicate for 'meaningful'; the "
            "figure is qualitative and no raw per-angle values are released."
        ),
        "minimum_preregistration_needed": [
            "fixed angle grid and sample count",
            "fixed error metric and aggregation",
            "numeric meaningful/not-meaningful threshold",
            "uncertainty rule at 20 and 30 degrees",
        ],
        "candidate_threshold_is_paper_anchored": False,
        "formal_claim_verdict": "BLOCKED",
    }
    return {
        "scope": "decision-rule audit only; no model or benchmark evaluation",
        "numeric_comparisons": numeric,
        "numeric_claims_have_executable_counterexamples": numeric_claims_falsifiable,
        "claim_6": claim_6,
        "formal_claim_verdicts_unchanged": {
            "2": "BLOCKED",
            "3": "BLOCKED",
            "4": "BLOCKED",
            "6": "BLOCKED",
        },
    }


def independently_check(result: dict[str, Any]) -> dict[str, Any]:
    failures: list[str] = []
    for name, item in result["numeric_comparisons"].items():
        if not item["counterexample_rejected"]:
            failures.append(f"{name}: injected counterexample was accepted")
        if item["counterexample_control"]["contract_accepts"]:
            failures.append(f"{name}: counterexample acceptance mismatch")
        if not item["reported_reduction_compatible_with_display_precision"]:
            failures.append(f"{name}: stated reduction incompatible with displayed values")
    if result["claim_6"]["machine_falsifiable_as_written"]:
        failures.append("claim 6 unexpectedly has a numerical predicate")
    return {
        "checker": "independent invariant checker",
        "passed": not failures,
        "failures": failures,
    }

