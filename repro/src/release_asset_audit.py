#!/usr/bin/env python3
"""Reproducible audit of inputs needed to test Geo-NeW benchmark claims."""
from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any
import urllib.request


OFFICIAL_REPO = "PIMILab/Geo-NeW"
OFFICIAL_SHA = "9c30e9320428c10c9a4721c19a9bc0a1639b6716"
GITHUB_TREE_URL = (
    "https://api.github.com/repos/PIMILab/Geo-NeW/git/trees/"
    f"{OFFICIAL_SHA}?recursive=1"
)
HF_URLS = {
    "models": "https://huggingface.co/api/models?author=PIMILab&limit=100",
    "datasets": "https://huggingface.co/api/datasets?author=PIMILab&limit=100",
}
USER_AGENT = "OpenResearch-Reproduction/1.0 (paper 2602.02788; asset audit)"


@dataclass(frozen=True)
class Requirement:
    name: str
    any_path_tokens: tuple[str, ...]


REQUIREMENTS = (
    Requirement("checkpoint", ("checkpoint", ".pt", ".pth", ".ckpt", "weights")),
    Requirement("preprocessing", ("preprocess", "processed_", "mesh", "fem")),
    Requirement("pipe_training", ("pipe",)),
    Requirement("elasticity_training", ("elastic",)),
    Requirement("poly_ood_data", ("polypoisson_ood", "poly_ood")),
    Requirement("ns2d_custom_data", ("ns2d", "angled", "comsol", "gmsh")),
)

CLAIM_REQUIREMENTS = {
    "2": ("checkpoint", "preprocessing", "pipe_training"),
    "3": ("checkpoint", "preprocessing", "elasticity_training"),
    "4": ("checkpoint", "preprocessing", "poly_ood_data", "ns2d_custom_data"),
    "6": ("checkpoint", "ns2d_custom_data"),
}


def _fetch_json(url: str) -> Any:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.load(response)


def scan_paths(paths: list[str]) -> dict[str, list[str]]:
    """Return matching released paths for each required asset class."""
    lowered = [(path, path.lower()) for path in paths]
    return {
        requirement.name: sorted(
            path
            for path, lower in lowered
            if any(token in lower for token in requirement.any_path_tokens)
        )
        for requirement in REQUIREMENTS
    }


def blockers(matches: dict[str, list[str]]) -> dict[str, list[str]]:
    return {
        claim: [name for name in required if not matches.get(name)]
        for claim, required in CLAIM_REQUIREMENTS.items()
    }


def independent_scan(paths: list[str]) -> dict[str, Any]:
    """Independent extension/entrypoint scan without the Requirement table."""
    low = [path.lower() for path in paths]
    weights = [path for path in low if Path(path).suffix in {".pt", ".pth", ".ckpt"}]
    benchmark_entries = [
        path
        for path in low
        if path.endswith(".py")
        and any(name in Path(path).name for name in ("train", "eval", "benchmark"))
    ]
    datasets = [
        path
        for path in low
        if Path(path).suffix in {".npy", ".npz", ".mat", ".h5", ".hdf5", ".pt"}
    ]
    return {
        "weight_files": weights,
        "benchmark_entrypoints": benchmark_entries,
        "dataset_files": datasets,
        "complete_for_empirical_claims": bool(weights and benchmark_entries and datasets),
    }


def build_audit() -> dict[str, Any]:
    tree = _fetch_json(GITHUB_TREE_URL)
    if tree.get("sha") != OFFICIAL_SHA or tree.get("truncated"):
        raise RuntimeError("official GitHub tree is not the pinned complete tree")
    paths = sorted(item["path"] for item in tree["tree"])
    matches = scan_paths(paths)
    missing = blockers(matches)

    hf_inventory = {kind: _fetch_json(url) for kind, url in HF_URLS.items()}
    hf_ids = {
        kind: sorted(item["id"] for item in items)
        for kind, items in hf_inventory.items()
    }
    if any(hf_ids.values()):
        raise RuntimeError("PIMILab Hugging Face inventory changed; review new assets")

    # Non-vacuity control: an injected manifest supplies every asset class.
    injected = paths + [
        "checkpoints/pipe.pt",
        "preprocessing/build_fem.py",
        "train_pipe.py",
        "train_elasticity.py",
        "data/polypoisson_ood.pt",
        "data/ns2d_angled_comsol.pt",
    ]
    injected_blockers = blockers(scan_paths(injected))
    if any(injected_blockers.values()):
        raise RuntimeError("negative control did not clear all missing-asset blockers")

    independent = independent_scan(paths)
    if independent["complete_for_empirical_claims"]:
        raise RuntimeError("independent scanner unexpectedly found a complete release")

    claim_verdicts = {
        "1": "VERIFIED",
        "2": "BLOCKED",
        "3": "BLOCKED",
        "4": "BLOCKED",
        "5": "VERIFIED",
        "6": "BLOCKED",
    }
    if any(not missing[claim] for claim in ("2", "3", "4", "6")):
        raise RuntimeError("a blocked claim no longer has an audited missing input")

    return {
        "audit_scope": {
            "official_repository": OFFICIAL_REPO,
            "official_git_sha": OFFICIAL_SHA,
            "github_tree_url": GITHUB_TREE_URL,
            "hugging_face_urls": HF_URLS,
            "user_agent": USER_AGENT,
        },
        "official_tree_paths": paths,
        "path_matches_by_asset_class": matches,
        "missing_requirements_by_claim": missing,
        "hugging_face_author_inventory_ids": hf_ids,
        "independent_checker_output": independent,
        "negative_control_output": {
            "injected_paths": injected[-6:],
            "remaining_blockers": injected_blockers,
            "all_blockers_cleared": not any(injected_blockers.values()),
        },
        "claim_verdicts": claim_verdicts,
        "interpretation": (
            "The public official release is a minimal forward/demo implementation. "
            "It does not contain the data, preprocessing, benchmark entrypoints, or "
            "checkpoints needed to decide Claims 2, 3, 4, or 6 faithfully."
        ),
    }
