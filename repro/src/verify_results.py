#!/usr/bin/env python3
"""Verify the committed claim records and final repository hygiene."""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
EXPECTED_REPOSITORY = "icml26-structure-preserving-geometry-generalization"
EXPECTED_TITLE = "Structure-Preserving Learning Improves Geometry Generalization in Neural PDEs"
EXPECTED_AUTHORS = [
    "Benjamin D. Shaffer",
    "Shawn Koohy",
    "Brooks Kinch",
    "M. Ani Hsieh",
    "Nathaniel Trask",
]
EXPECTED_STATUSES = {
    "C1": "VERIFIED",
    "C2": "BLOCKED",
    "C3": "BLOCKED",
    "C4": "BLOCKED",
    "C5": "VERIFIED",
    "C6": "BLOCKED",
}


def load_json(relative: str) -> Any:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def tracked(path: str) -> bool:
    return subprocess.run(
        ["git", "ls-files", "--error-unmatch", "--", path],
        cwd=ROOT,
        text=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    ).returncode == 0


def main() -> int:
    sources = load_json("sources.json")
    checks: dict[str, bool] = {}

    paper = sources["paper"]
    checks["paper_identity"] = (
        paper["title"] == EXPECTED_TITLE
        and paper["authors"] == EXPECTED_AUTHORS
        and paper["arxiv_id"] == "2602.02788"
        and paper["arxiv_version"] == "v2"
        and paper["openreview_id"] == "RtnSbA5AUV"
    )
    checks["claim_statuses"] = sources["local_scope"]["claim_statuses"] == EXPECTED_STATUSES

    c1 = load_json("evidence/claim_1/raw_results.json")
    checks["claim_1_positive"] = bool(c1) and all(
        isinstance(value, dict) and value.get("ok") is True for value in c1.values()
    )
    c5 = load_json("evidence/claim_5/raw_results.json")
    checks["claim_5_positive"] = bool(
        c5["verdict"] == "VERIFIED"
        and c5["exact_dirichlet_bc"]
        and c5["unconstrained_violates_bc"]
        and c5["interior_solution_nontrivial"]
    )

    blocked_checks = {}
    for claim in ("2", "3", "4", "6"):
        result = load_json(f"evidence/claim_{claim}/raw_results.json")
        independent = load_json(
            f"evidence/claim_{claim}/independent_checker_output.json"
        )
        negative = load_json(
            f"evidence/claim_{claim}/negative_control_output.json"
        )
        blocked_checks[claim] = bool(
            result.get("verdict") == "BLOCKED"
            and result.get("missing_requirements")
            and independent.get("complete_for_empirical_claims") is False
            and negative.get("all_blockers_cleared") is True
        )
    checks["blocked_claim_records"] = all(blocked_checks.values())

    required_files = [
        "README.md",
        "STATUS.md",
        "sources.json",
        "docs/CLAIM_EVIDENCE.md",
        "docs/BRANCH_AUDIT.md",
        "docs/SOURCE_AUDIT.md",
        "docs/PUBLICATION_GATE.md",
        "docs/research_log.md",
        "repro/src/publication_gate.py",
    ]
    checks["documentation_surface"] = all((ROOT / path).is_file() for path in required_files)
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    checks["readme_contract"] = all(
        marker in readme
        for marker in (
            "## Citation",
            "## Thank you",
            "How each claim is produced",
            "## Branch map",
            "## Source and evidence boundary",
        )
    )
    checks["hygiene"] = not tracked(".trackio") and not tracked("logbook.json")

    current_branch = git("branch", "--show-current")
    remote_url = git("remote", "get-url", "origin")
    local_branches = git(
        "for-each-ref", "--format=%(refname:strip=2)", "refs/heads"
    ).splitlines()
    remote_branches = git(
        "for-each-ref", "--format=%(refname:strip=3)", "refs/remotes/origin"
    ).splitlines()
    checks["branch_surface"] = bool(
        current_branch == "main"
        and "master" not in local_branches
        and all(not branch.startswith("orx/") for branch in local_branches + remote_branches)
        and "master" not in remote_branches
    )
    checks["remote_name"] = EXPECTED_REPOSITORY in remote_url

    identities = git("log", "--all", "--format=%an%x00%ae").splitlines()
    expected_identity = "MachineLearning-Nerd\x00MachineLearning-Nerd@users.noreply.github.com"
    checks["commit_identity"] = bool(identities) and all(
        identity == expected_identity for identity in identities
    )

    result = {
        "repository": EXPECTED_REPOSITORY,
        "claim_statuses": EXPECTED_STATUSES,
        "blocked_claim_checks": blocked_checks,
        "checks": checks,
        "passed": all(checks.values()),
    }
    output = ROOT / "outputs" / "verification.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    for name, passed in checks.items():
        print(f"{name}: {'PASS' if passed else 'FAIL'}")
    print(f"wrote {output}")
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
