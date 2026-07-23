#!/usr/bin/env python3
"""Fixed cumulative reproduction entrypoint for every OpenResearch node."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import time
import urllib.request


ROOT = Path(__file__).resolve().parents[2]
ARTIFACTS = ROOT / ".openresearch" / "artifacts"
CACHE = ROOT / ".openresearch" / "cache"
SOURCE_URL = "https://arxiv.org/e-print/2602.02788v2"
SOURCE_SHA256 = "c88523e66a538dc8001be383172f919aeac9e359e3c2294a26889c6ffc0ed724"
USER_AGENT = "OpenResearch-Reproduction/1.0 (paper 2602.02788; project RtnSbA5AUV)"
FIXED_COMMAND = "uv sync --frozen && uv run python repro/src/run_all.py"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def fetch_source() -> Path:
    CACHE.mkdir(parents=True, exist_ok=True)
    target = CACHE / "2602.02788v2.tar"
    if target.exists() and sha256(target) == SOURCE_SHA256:
        return target
    temporary = target.with_suffix(".download")
    request = urllib.request.Request(SOURCE_URL, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=120) as response, temporary.open("wb") as output:
        shutil.copyfileobj(response, output)
    observed = sha256(temporary)
    if observed != SOURCE_SHA256:
        temporary.unlink(missing_ok=True)
        raise RuntimeError(f"paper source SHA-256 mismatch: {observed}")
    temporary.replace(target)
    return target


def run_stage(name: str, command: list[str]) -> float:
    print(f"\n--- stage: {name} ---", flush=True)
    started = time.monotonic()
    completed = subprocess.run(command, cwd=ROOT, check=False)
    elapsed = time.monotonic() - started
    print(f"--- stage_result: {name} exit={completed.returncode} seconds={elapsed:.6f} ---")
    if completed.returncode != 0:
        raise RuntimeError(f"stage failed: {name}")
    return elapsed


def git_value(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def main() -> int:
    started = time.monotonic()
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    source = fetch_source()
    metadata = {
        "fixed_command": FIXED_COMMAND,
        "git_sha": git_value("rev-parse", "HEAD"),
        "git_branch": git_value("rev-parse", "--abbrev-ref", "HEAD"),
        "paper_source_url": SOURCE_URL,
        "paper_source_sha256": sha256(source),
        "paper_source_user_agent": USER_AGENT,
        "python": sys.version,
        "platform": platform.platform(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "cpu_count": os.cpu_count(),
        "uv_lock_sha256": sha256(ROOT / "uv.lock"),
        "deterministic_seeds": [0],
    }
    write_json(ARTIFACTS / "runtime_metadata.json", metadata)

    durations: dict[str, float] = {}
    durations["claim_1"] = run_stage(
        "claim_1_feec_conservation", [sys.executable, "repro/src/run_geo_new.py"]
    )
    claim_1 = json.loads((ROOT / "outputs" / "geo_new_summary.json").read_text())
    if not all(item["ok"] for item in claim_1.values()):
        raise RuntimeError("claim 1 verifier rejected its evidence")
    write_json(ARTIFACTS / "claim_1" / "raw_results.json", claim_1)
    write_json(
        ARTIFACTS / "claim_1" / "negative_control_output.json",
        {"perturbed_incidence_detected": claim_1["neg_control"]["ok"]},
    )

    durations["claim_5"] = run_stage(
        "claim_5_exact_dirichlet", [sys.executable, "repro/src/verify_bc.py"]
    )
    claim_5 = json.loads((ROOT / "outputs" / "bc_results.json").read_text())
    if claim_5["verdict"] != "VERIFIED":
        raise RuntimeError("claim 5 verifier rejected its evidence")
    write_json(ARTIFACTS / "claim_5" / "raw_results.json", claim_5)
    write_json(
        ARTIFACTS / "claim_5" / "negative_control_output.json",
        {
            "unconstrained_error": claim_5["boundary_max_abs_error_unconstrained"],
            "violation_detected": claim_5["unconstrained_violates_bc"],
        },
    )

    metric_output = ARTIFACTS / "source_metric_audit" / "raw_results.json"
    durations["source_metric_audit"] = run_stage(
        "source_metric_audit",
        [
            sys.executable,
            "repro/src/run_ood_metric_audit.py",
            "--source-tar",
            str(source),
            "--output",
            str(metric_output),
        ],
    )
    release_output = ARTIFACTS / "release_asset_audit" / "raw_results.json"
    durations["release_asset_audit"] = run_stage(
        "release_asset_audit",
        [
            sys.executable,
            "repro/src/run_release_asset_audit.py",
            "--output",
            str(release_output),
        ],
    )
    release_audit = json.loads(release_output.read_text())
    toy_output = ARTIFACTS / "toy_mechanism_suite" / "raw_results.json"
    toy_csv = ARTIFACTS / "toy_mechanism_suite" / "raw_cases.csv"
    durations["toy_mechanism_suite"] = run_stage(
        "toy_mechanism_suite",
        [
            sys.executable,
            "repro/src/run_toy_mechanism_suite.py",
            "--output",
            str(toy_output),
            "--csv",
            str(toy_csv),
        ],
    )
    toy_suite = json.loads(toy_output.read_text())
    if toy_suite["scale_label"] != "TOY":
        raise RuntimeError("toy mechanism suite lost its mandatory scope label")
    if not toy_suite["independent_checker"]["passed"]:
        raise RuntimeError("toy mechanism suite independent checker failed")
    expected_verdicts = {
        "1": "VERIFIED",
        "2": "BLOCKED",
        "3": "BLOCKED",
        "4": "BLOCKED",
        "5": "VERIFIED",
        "6": "BLOCKED",
    }
    if release_audit["claim_verdicts"] != expected_verdicts:
        raise RuntimeError("release asset audit produced unexpected claim verdicts")
    for claim in ("2", "3", "4", "6"):
        write_json(
            ARTIFACTS / f"claim_{claim}" / "raw_results.json",
            {
                "verdict": "BLOCKED",
                "missing_requirements": release_audit[
                    "missing_requirements_by_claim"
                ][claim],
                "official_git_sha": release_audit["audit_scope"][
                    "official_git_sha"
                ],
            },
        )
        write_json(
            ARTIFACTS / f"claim_{claim}" / "independent_checker_output.json",
            release_audit["independent_checker_output"],
        )
        write_json(
            ARTIFACTS / f"claim_{claim}" / "negative_control_output.json",
            release_audit["negative_control_output"],
        )
    durations["independent_tests"] = run_stage(
        "independent_tests",
        [
            sys.executable,
            "-m",
            "pytest",
            "-q",
            "repro/tests",
            "--geo-new-source-tar",
            str(source),
        ],
    )

    summary = {
        "baseline_regressions": {"claim_1": "VERIFIED", "claim_5": "VERIFIED"},
        "source_metric_audit": "PASS_AUDIT_ONLY",
        "release_asset_audit": "PASS",
        "toy_mechanism_suite": {
            "scale_label": "TOY",
            "claims": ["2", "3", "4", "6"],
            "headline_verdicts_unchanged": True,
        },
        "claim_verdicts": expected_verdicts,
        "independent_tests": "PASS",
        "durations_seconds": durations,
        "total_runtime_seconds": time.monotonic() - started,
        "metadata": metadata,
    }
    write_json(ARTIFACTS / "baseline_summary.json", summary)
    eval_md = (
        "# EVAL\n\n"
        "- Claim 1: VERIFIED — exact FEEC/incidence identities and perturbation control pass.\n"
        "- Claim 5: VERIFIED — exact Dirichlet construction and unconstrained control pass.\n"
        "- Claims 2, 3, 4, 6: BLOCKED — required empirical assets are absent from the pinned public release.\n"
        "- Toy mechanism suite: PASS — four CPU analogues and damaged-structure controls pass; no headline verdict changes.\n"
        "- Source metric audit: PASS (audit only) — pinned arXiv source contract is unchanged.\n"
        "- Release asset audit: PASS — both scanners agree; injected complete-release control clears every blocker.\n"
        "- Independent test suite: PASS.\n\n"
        f"Total runtime: {summary['total_runtime_seconds']:.6f} seconds.\n"
        f"Git SHA: `{metadata['git_sha']}`.\n"
    )
    (ARTIFACTS / "EVAL.md").write_text(eval_md, encoding="utf-8")

    print("\n=== CUMULATIVE EVAL ===")
    print(eval_md)
    print("BASELINE_SUMMARY_JSON=" + json.dumps(summary, sort_keys=True))
    for path in sorted(ARTIFACTS.rglob("*")):
        if path.is_file():
            print(f"ARTIFACT {path.relative_to(ROOT)} sha256={sha256(path)}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"FATAL_REPRODUCTION_ERROR: {exc}", file=sys.stderr)
        raise
