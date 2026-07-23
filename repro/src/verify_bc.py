#!/usr/bin/env python3
"""Re-run the exact-Dirichlet negative-control evidence from the judged logbook."""
from __future__ import annotations

import hashlib
import json
import os

import numpy as np


def main() -> int:
    result = {"claim": "GeoNeW_exact_dirichlet_bc", "paper": "arXiv:2602.02788v2"}
    rng = np.random.default_rng(0)

    def boundary_data(points: np.ndarray) -> np.ndarray:
        return np.stack(
            [
                np.sin(2 * points[:, 0]) + points[:, 1],
                np.cos(points[:, 0] * points[:, 1]),
            ],
            axis=1,
        )

    def distance_factor(points: np.ndarray) -> np.ndarray:
        return 1.0 - (points[:, 0] ** 2 + points[:, 1] ** 2)

    weight_1 = rng.standard_normal((2, 32))
    bias_1 = rng.standard_normal(32)
    weight_2 = rng.standard_normal((32, 2))
    bias_2 = rng.standard_normal(2)

    def network(points: np.ndarray) -> np.ndarray:
        return np.tanh(points @ weight_1 + bias_1) @ weight_2 + bias_2

    def constrained(points: np.ndarray) -> np.ndarray:
        return boundary_data(points) + distance_factor(points)[:, None] * network(points)

    angles = np.linspace(0, 2 * np.pi, 4000, endpoint=False)
    boundary = np.stack([np.cos(angles), np.sin(angles)], axis=1)
    target = boundary_data(boundary)
    structured_error = float(np.max(np.abs(constrained(boundary) - target)))
    free_error = float(np.max(np.abs(network(boundary) - target)))

    interior = rng.uniform(-0.6, 0.6, (2000, 2))
    result.update(
        {
            "seed": 0,
            "boundary_nodes": 4000,
            "boundary_max_abs_error_structure_preserving": structured_error,
            "boundary_max_abs_error_unconstrained": round(free_error, 4),
            "exact_dirichlet_bc": structured_error < 1e-12,
            "unconstrained_violates_bc": free_error > 0.1,
            "interior_solution_nontrivial": bool(
                np.max(np.abs(constrained(interior) - boundary_data(interior))) > 1e-3
            ),
            "d_zero_on_boundary_max": float(np.max(np.abs(distance_factor(boundary)))),
        }
    )
    passed = bool(
        result["exact_dirichlet_bc"]
        and result["unconstrained_violates_bc"]
        and result["interior_solution_nontrivial"]
    )
    result["verdict"] = "VERIFIED" if passed else "BLOCKED"

    print("claim:", result["claim"])
    print(
        "boundary max|u-g|: constrained="
        f"{structured_error:.2e}; unconstrained={free_error:.4f}"
    )
    print(
        "distance-factor boundary residual="
        f"{result['d_zero_on_boundary_max']:.2e}; "
        f"interior nontrivial={result['interior_solution_nontrivial']}"
    )
    print("verdict:", result["verdict"])

    os.makedirs("outputs", exist_ok=True)
    payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
    with open("outputs/bc_results.json", "w", encoding="utf-8") as handle:
        handle.write(payload)
    print("RESULTS_SHA256=" + hashlib.sha256(payload.encode()).hexdigest())
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
