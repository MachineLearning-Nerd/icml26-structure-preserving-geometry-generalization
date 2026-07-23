#!/usr/bin/env python3
"""Claim-contract audit for Geo-NeW's OOD error-reduction claim.

The challenge claim says that Geo-NeW achieves "up to 65% MSE reduction"
against the best-performing alternatives on out-of-distribution geometries.
The camera-ready paper instead defines and reports the mean per-sample
normalized L2 error.  This module re-computes every relevant reduction from
the published values and, when given the pinned arXiv source archive, verifies
the metric definition and values directly against that archive.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, getcontext
from hashlib import sha256
from pathlib import Path
import re
import tarfile
from typing import Any


getcontext().prec = 40

ARXIV_ID = "2602.02788"
ARXIV_VERSION = "v2"
ARXIV_SOURCE_SHA256 = "c88523e66a538dc8001be383172f919aeac9e359e3c2294a26889c6ffc0ed724"
CLAIM = (
    "Achieves up to 65% MSE reduction compared with best-performing "
    "alternatives on out-of-distribution geometries."
)


@dataclass(frozen=True)
class Benchmark:
    name: str
    geo_new: Decimal
    alternatives: dict[str, Decimal]


PUBLISHED_OOD_BENCHMARKS = (
    Benchmark(
        name="Poly-Poisson OOD",
        geo_new=Decimal("2.14"),
        alternatives={
            "GNOT": Decimal("5.24"),
            "Transolver": Decimal("7.04"),
            "Linear Attention": Decimal("4.60"),
            "Inducing Point": Decimal("8.90"),
        },
    ),
    Benchmark(
        name="NS2d-c++ OOD",
        geo_new=Decimal("42.2"),
        alternatives={
            "GNOT": Decimal("83.08"),
            "Transolver": Decimal("91.40"),
            "Linear Attention": Decimal("91.84"),
        },
    ),
)


def reduction(candidate: Decimal, baseline: Decimal) -> Decimal:
    """Fractional reduction in a lower-is-better error metric."""
    if candidate < 0 or baseline <= 0:
        raise ValueError("errors must be non-negative and baseline must be positive")
    return Decimal(1) - candidate / baseline


def squared_aggregate_proxy(candidate: Decimal, baseline: Decimal) -> Decimal:
    """Square two aggregate L2 errors; this is *not* an observed MSE reduction."""
    return Decimal(1) - (candidate / baseline) ** 2


def percent(value: Decimal) -> str:
    return f"{value * 100:.6f}"


def _sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _read_tar_member(archive: tarfile.TarFile, name: str) -> bytes:
    member = archive.getmember(name)
    handle = archive.extractfile(member)
    if handle is None:
        raise ValueError(f"arXiv member is not a regular file: {name}")
    return handle.read()


def audit_arxiv_source(source_tar: Path | str) -> dict[str, Any]:
    """Verify the metric contract and table values in the pinned arXiv source."""
    source_tar = Path(source_tar)
    observed_sha = _sha256(source_tar)
    if observed_sha != ARXIV_SOURCE_SHA256:
        raise ValueError(
            f"unexpected arXiv source SHA-256: {observed_sha}; expected {ARXIV_SOURCE_SHA256}"
        )

    with tarfile.open(source_tar, "r:gz") as archive:
        main_bytes = _read_tar_member(archive, "main.tex")
        table_bytes = _read_tar_member(archive, "figures/big_table.tex")
        heatmap_bytes = _read_tar_member(archive, "figures/comp_heatmap3.png")

    main_tex = main_bytes.decode("utf-8")
    table_tex = table_bytes.decode("utf-8")
    compact_main = re.sub(r"\s+", " ", main_tex)
    compact_table = re.sub(r"\s+", " ", table_tex)

    expected_source_fragments = {
        "metric_formula": (
            r"\epsilon = \frac{1}{N_{samples}}\sum^{N_{samples}}_{i=1}"
            r"\frac{ || u'_i-u_i ||_2}{|| u_i ||_2}."
        ),
        "mild_ood_values": (
            r"Geo-NeW achieves $7.87\%$ error compared to $13.1\%$ "
            r"for the strongest baseline."
        ),
        "poly_ood_row": r"Linear Attention (\hyperlink{cite.katharopoulos2020transformers}{2020}) & 0.055 & 4.60",
        "geo_new_ood_values": r"& \textbf{2.14*} & 1.10 & \textbf{1.93} & \textbf{42.2}",
        "gnot_ns2d_ood": r"GNOT (\hyperlink{cite.hao2023gnot}{2023}) & 0.074 & 5.24 & 0.93 & 5.30 & 83.08",
    }
    fragment_checks = {
        "metric_formula": expected_source_fragments["metric_formula"] in main_tex,
        "mild_ood_values": expected_source_fragments["mild_ood_values"] in compact_main,
        "poly_ood_row": expected_source_fragments["poly_ood_row"] in compact_table,
        "geo_new_ood_values": expected_source_fragments["geo_new_ood_values"] in compact_table,
        "gnot_ns2d_ood": expected_source_fragments["gnot_ns2d_ood"] in compact_table,
    }
    if not all(fragment_checks.values()):
        failed = [name for name, ok in fragment_checks.items() if not ok]
        raise ValueError(f"pinned source contract changed or parser failed: {failed}")

    return {
        "arxiv_id": ARXIV_ID,
        "version": ARXIV_VERSION,
        "archive_sha256": observed_sha,
        "main_tex_sha256": sha256(main_bytes).hexdigest(),
        "big_table_tex_sha256": sha256(table_bytes).hexdigest(),
        "figure_6_heatmap_sha256": sha256(heatmap_bytes).hexdigest(),
        "fragment_checks": fragment_checks,
        "case_insensitive_mse_mentions_in_main_tex": len(
            re.findall(r"(?i)\bmse\b|mean[- ]squared error", main_tex)
        ),
        "standalone_65_mentions_in_main_tex": len(
            re.findall(r"(?<![\d.])65(?!\d)", main_tex)
        ),
    }


def build_audit(source_tar: Path | None = None) -> dict[str, Any]:
    table_rows: list[dict[str, Any]] = []
    for benchmark in PUBLISHED_OOD_BENCHMARKS:
        best_name, best_value = min(benchmark.alternatives.items(), key=lambda item: item[1])
        direct = reduction(benchmark.geo_new, best_value)
        squared_proxy = squared_aggregate_proxy(benchmark.geo_new, best_value)
        table_rows.append(
            {
                "benchmark": benchmark.name,
                "reported_metric": "mean per-sample normalized L2 error (x1e-2)",
                "geo_new": str(benchmark.geo_new),
                "best_alternative": best_name,
                "best_alternative_error": str(best_value),
                "direct_l2_reduction_percent": percent(direct),
                "squared_aggregate_proxy_percent": percent(squared_proxy),
                "matches_65_percent": direct == Decimal("0.65"),
            }
        )

    mild_geo = Decimal("7.87")
    mild_baseline = Decimal("13.1")
    mild_direct = reduction(mild_geo, mild_baseline)
    mild_squared_proxy = squared_aggregate_proxy(mild_geo, mild_baseline)

    result: dict[str, Any] = {
        "paper": {
            "title": "Structure-Preserving Learning Improves Geometry Generalization in Neural PDEs",
            "arxiv_id": ARXIV_ID,
            "arxiv_version": ARXIV_VERSION,
        },
        "claim": CLAIM,
        "empirical_claim_verdict": "NOT_DECIDED_BY_SOURCE_AUDIT",
        "metric_contract": {
            "claim_metric": "MSE",
            "paper_metric": "mean per-sample normalized L2 error",
            "same_metric": False,
            "reason": (
                "The paper averages per-sample normalized L2 norms. Squaring an aggregate "
                "mean L2 error is not the mean squared error and cannot recover unreported MSE."
            ),
        },
        "table_1_best_alternative_reductions": table_rows,
        "mild_extrapolation_text_result": {
            "geo_new_normalized_l2_percent": str(mild_geo),
            "strongest_baseline_normalized_l2_percent": str(mild_baseline),
            "direct_l2_reduction_percent": percent(mild_direct),
            "squared_aggregate_proxy_percent": percent(mild_squared_proxy),
            "proxy_distance_from_65_percentage_points": percent(
                abs(Decimal("0.65") - mild_squared_proxy)
            ),
        },
        "decisive_checks": {
            "paper_reports_mse": False,
            "paper_reports_numeric_65_percent": False,
            "table_1_direct_best_baseline_reduction_is_65_percent": False,
            "mild_regime_direct_reduction_is_65_percent": False,
            "squaring_aggregate_l2_is_valid_mse_recovery": False,
        },
        "interpretation": (
            "The paper supports an OOD advantage in normalized L2 error, but the challenge's "
            "specific 65% MSE statement is not a reported or derivable statistic. This source "
            "audit does not verify or falsify model performance."
        ),
    }
    if source_tar is not None:
        result["pinned_source_audit"] = audit_arxiv_source(source_tar)
    return result
