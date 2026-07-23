#!/usr/bin/env python3
"""CLI wrapper for the unresolved-claim falsifiability audit."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from falsifiability_audit import independently_check, run_audit


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    result = run_audit()
    checker = independently_check(result)
    if not checker["passed"]:
        raise RuntimeError("; ".join(checker["failures"]))
    result["independent_checker"] = checker
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

