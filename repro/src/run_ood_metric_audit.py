#!/usr/bin/env python3
"""Run Geo-NeW's pinned-source OOD metric audit."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from ood_metric_audit import build_audit


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--source-tar",
        type=Path,
        help="Optional arXiv 2602.02788v2 e-print archive; SHA-256 is strictly pinned.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).resolve().parents[2] / "outputs" / "ood_metric_audit.json",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    audit = build_audit(args.source_tar)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")

    print("Geo-NeW OOD source metric-contract audit")
    print("empirical claim verdict:", audit["empirical_claim_verdict"])
    print("paper metric:", audit["metric_contract"]["paper_metric"])
    print("claim metric:", audit["metric_contract"]["claim_metric"])
    for row in audit["table_1_best_alternative_reductions"]:
        print(
            f"{row['benchmark']}: {row['geo_new']} vs {row['best_alternative_error']} "
            f"({row['best_alternative']}), direct reduction "
            f"{row['direct_l2_reduction_percent']}%"
        )
    mild = audit["mild_extrapolation_text_result"]
    print(
        "mild regime: direct normalized-L2 reduction "
        f"{mild['direct_l2_reduction_percent']}%; squared-aggregate proxy "
        f"{mild['squared_aggregate_proxy_percent']}% (not MSE)"
    )
    if "pinned_source_audit" in audit:
        source = audit["pinned_source_audit"]
        print("pinned arXiv source SHA-256:", source["archive_sha256"])
        print("source fragment checks:", all(source["fragment_checks"].values()))
        print("MSE mentions in main.tex:", source["case_insensitive_mse_mentions_in_main_tex"])
        print("standalone 65 mentions in main.tex:", source["standalone_65_mentions_in_main_tex"])
    print("wrote", args.output)


if __name__ == "__main__":
    main()
