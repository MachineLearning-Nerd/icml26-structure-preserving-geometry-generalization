#!/usr/bin/env python3
"""CLI for the CPU-only, explicitly toy mechanism suite."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from toy_mechanism_suite import independently_check, run_suite, write_outputs


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--csv", type=Path, required=True)
    args = parser.parse_args()
    result = run_suite()
    checker = independently_check(result)
    if not checker["passed"]:
        raise RuntimeError("; ".join(checker["failures"]))
    result["independent_checker"] = checker
    write_outputs(result, args.output, args.csv)
    printable = dict(result)
    printable.pop("rows")
    print("TOY_MECHANISM_SUITE_JSON=" + json.dumps(printable, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

