#!/usr/bin/env python3
"""Build and validate the text-only, additive Hugging Face upload plan."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
OVERLAY = ROOT / "release" / "space-overlay"
TEXT_SUFFIXES = {".json", ".md", ".txt", ".tsv"}
SECRET_PATTERNS = (
    re.compile(r"hf_[A-Za-z0-9]{20,}"),
    re.compile(r"(?i)(api[_-]?key|access[_-]?token|secret)\s*[:=]\s*['\"][^'\"]+"),
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def mappings() -> list[tuple[Path, str]]:
    result = [
        (OVERLAY / "logbook.json", "logbook.json"),
    ]
    result.extend(
        (path, path.relative_to(OVERLAY).as_posix())
        for path in sorted((OVERLAY / "pages").rglob("*.md"))
    )
    artifacts = ROOT / ".openresearch" / "artifacts"
    result.extend(
        [
            (artifacts / "EVAL.md", "evidence/EVAL.md"),
            (artifacts / "runtime_metadata.json", "evidence/runtime_metadata.json"),
            (
                artifacts / "release_asset_audit" / "raw_results.json",
                "evidence/release_asset_audit/raw_results.json",
            ),
        ]
    )
    for claim in range(1, 7):
        for name in (
            "claim_contract.json",
            "source_audit.md",
            "method.md",
            "raw_results.json",
            "independent_checker_output.json",
            "negative_control_output.json",
        ):
            result.append(
                (
                    artifacts / f"claim_{claim}" / name,
                    f"evidence/claim_{claim}/{name}",
                )
            )
    return result


def load_protected_manifest(protected: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    prefix = str(protected.resolve()) + "/"
    for line in (protected / "manifest.sha256").read_text(encoding="utf-8").splitlines():
        digest, absolute = line.split("  ", 1)
        if not absolute.startswith(prefix):
            raise RuntimeError(f"protected manifest path escaped snapshot: {absolute}")
        result[absolute[len(prefix) :]] = digest
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protected", type=Path, required=True)
    args = parser.parse_args()
    protected = args.protected.resolve()
    old = load_protected_manifest(protected)

    entries = []
    remote_paths: set[str] = set()
    for source, remote in mappings():
        if not source.is_file():
            raise RuntimeError(f"missing upload source: {source}")
        if source.suffix.lower() not in TEXT_SUFFIXES:
            raise RuntimeError(f"non-text suffix in allowlist: {source}")
        if remote in remote_paths:
            raise RuntimeError(f"duplicate remote target: {remote}")
        text = source.read_text(encoding="utf-8")
        if any(pattern.search(text) for pattern in SECRET_PATTERNS):
            raise RuntimeError(f"possible secret in upload source: {source}")
        remote_paths.add(remote)
        entries.append(
            {
                "source": source.relative_to(ROOT).as_posix(),
                "remote": remote,
                "sha256": sha256(source),
                "bytes": source.stat().st_size,
            }
        )

    # All old paths remain on the Space because the upload is additive.
    union_paths = set(old) | remote_paths
    missing_old = sorted(set(old) - union_paths)
    protected_page_overwrites = sorted(
        path for path in remote_paths if path in old and path.startswith("pages/")
    )
    if missing_old or protected_page_overwrites:
        raise RuntimeError("candidate does not preserve protected pages additively")

    logbook = json.loads((OVERLAY / "logbook.json").read_text(encoding="utf-8"))
    referenced: set[str] = set()

    def visit(node: dict[str, object]) -> None:
        referenced.add(str(node["file"]))
        for child in node.get("children", []):
            visit(child)

    visit(logbook["root"])
    missing_references = sorted(referenced - union_paths)
    if missing_references:
        raise RuntimeError(f"logbook references missing candidate paths: {missing_references}")

    allowlist = ROOT / "release" / "hf_upload_allowlist.tsv"
    allowlist.write_text(
        "sha256\tbytes\tsource\tremote\n"
        + "".join(
            f"{entry['sha256']}\t{entry['bytes']}\t{entry['source']}\t{entry['remote']}\n"
            for entry in entries
        ),
        encoding="utf-8",
    )
    manifest = ROOT / "release" / "hf_upload_manifest.sha256"
    manifest.write_text(
        "".join(f"{entry['sha256']}  {entry['remote']}\n" for entry in entries),
        encoding="utf-8",
    )
    subset = {
        "judged_revision": "8753eb9a662a446337f02a7773eddece8f64a3af",
        "protected_file_count": len(old),
        "upload_file_count": len(entries),
        "candidate_union_file_count": len(union_paths),
        "old_paths_subset_of_candidate": not missing_old,
        "missing_old_paths": missing_old,
        "protected_page_overwrites": protected_page_overwrites,
        "logbook_references_valid": not missing_references,
        "missing_logbook_references": missing_references,
        "text_only_allowlist": True,
        "secret_scan_passed": True,
    }
    (ROOT / "release" / "old_new_subset_check.json").write_text(
        json.dumps(subset, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(subset, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
