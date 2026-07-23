#!/usr/bin/env python3
"""CLI for the exact-claim public-release audit."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from release_asset_audit import build_audit


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = build_audit()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print("RELEASE_ASSET_AUDIT_JSON=" + json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
