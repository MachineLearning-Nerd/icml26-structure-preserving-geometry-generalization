#!/usr/bin/env python3
"""Fail-closed publication gate for the cleaned ICML reproduction repository."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[2]
EXPECTED_NAME = "icml26-structure-preserving-geometry-generalization"
EXPECTED_SOURCE_SHA = "c88523e66a538dc8001be383172f919aeac9e359e3c2294a26889c6ffc0ed724"


def run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=ROOT, text=True, check=False)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--skip-producers",
        action="store_true",
        help="verify committed evidence without downloading or regenerating it",
    )
    args = parser.parse_args()

    checks: dict[str, bool] = {}
    producer_ran = False
    if not args.skip_producers:
        producer_ran = True
        checks["producers"] = run(
            [sys.executable, "repro/src/run_all.py"]
        ).returncode == 0

    verification = run([sys.executable, "repro/src/verify_results.py"])
    checks["verification"] = verification.returncode == 0

    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    sources = json.loads((ROOT / "sources.json").read_text(encoding="utf-8"))
    checks["project_name"] = f'name = "{EXPECTED_NAME}"' in pyproject
    checks["source_pin"] = sources["paper"]["source_sha256"] == EXPECTED_SOURCE_SHA
    checks["no_stale_publication_state"] = not (
        (ROOT / ".trackio").exists() or (ROOT / "logbook.json").exists()
    )
    checks["diff_check"] = run(["git", "diff", "--check"]).returncode == 0

    result = {
        "repository": EXPECTED_NAME,
        "producer_ran": producer_ran,
        "checks": checks,
        "passed": all(checks.values()),
    }
    output = ROOT / "outputs" / "publication_gate.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    for name, passed in checks.items():
        print(f"{name}: {'PASS' if passed else 'FAIL'}")
    print(f"wrote {output}")
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
