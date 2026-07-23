"""Deterministic CPU-scale mechanism analogues for unresolved empirical claims.

These experiments deliberately do not impersonate Geo-NeW or its baselines.
They test whether geometry-aware constrained solves can help in small related
problems and label every result TOY.
"""
from __future__ import annotations

from dataclasses import dataclass
import csv
import json
import math
from pathlib import Path
from typing import Any, Iterable

import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.linalg import spsolve


SEED = 20260202788
BOOTSTRAP_REPLICATES = 2000
TOY_THRESHOLD = 0.10


def normalized_l2(prediction: np.ndarray, truth: np.ndarray) -> float:
    denominator = float(np.linalg.norm(truth.ravel()))
    if denominator == 0:
        raise ValueError("normalized L2 is undefined for a zero target")
    return float(np.linalg.norm((prediction - truth).ravel()) / denominator)


def bootstrap_mean_interval(values: Iterable[float]) -> dict[str, float]:
    samples = np.asarray(list(values), dtype=float)
    if samples.size == 0:
        raise ValueError("cannot bootstrap an empty sample")
    rng = np.random.default_rng(SEED)
    draws = rng.choice(samples, size=(BOOTSTRAP_REPLICATES, samples.size), replace=True)
    means = draws.mean(axis=1)
    return {
        "mean": float(samples.mean()),
        "ci95_low": float(np.quantile(means, 0.025)),
        "ci95_high": float(np.quantile(means, 0.975)),
        "n_cases": int(samples.size),
        "bootstrap_replicates": BOOTSTRAP_REPLICATES,
    }


def pipe_analogue() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Parabolic flow profiles with an OOD height extrapolation."""
    s = np.linspace(0.0, 1.0, 65)
    train_heights = np.linspace(0.80, 1.20, 17)
    test_heights = np.linspace(1.25, 1.60, 15)

    def truth(height: float) -> np.ndarray:
        return height**2 * 4.0 * s * (1.0 - s)

    train_targets = np.stack([truth(height) for height in train_heights])
    structured_features = np.stack(
        [height**2 * 4.0 * s * (1.0 - s) for height in train_heights]
    )
    learned_constitutive_scale = float(
        np.vdot(structured_features, train_targets)
        / np.vdot(structured_features, structured_features)
    )

    design = np.column_stack([np.ones_like(train_heights), train_heights])
    direct_coefficients = np.linalg.lstsq(design, train_targets, rcond=None)[0]
    mean_train_height_sq = float(np.mean(train_heights**2))

    rows: list[dict[str, Any]] = []
    for case_index, height in enumerate(test_heights):
        target = truth(float(height))
        structured = (
            learned_constitutive_scale
            * height**2
            * 4.0
            * s
            * (1.0 - s)
        )
        direct = np.array([1.0, height]) @ direct_coefficients
        damaged = mean_train_height_sq * 4.0 * s * (1.0 - s)
        for method, prediction in (
            ("structured_analogue", structured),
            ("direct_affine_analogue", direct),
            ("damaged_geometry_control", damaged),
        ):
            rows.append(
                {
                    "claim_id": "2",
                    "case": case_index,
                    "parameter": float(height),
                    "method": method,
                    "normalized_l2": normalized_l2(prediction, target),
                }
            )
    diagnostics = {
        "task": "1D analytic parabolic profile; OOD pipe-height extrapolation",
        "learned_constitutive_scale": learned_constitutive_scale,
        "train_height_range": [float(train_heights.min()), float(train_heights.max())],
        "test_height_range": [float(test_heights.min()), float(test_heights.max())],
        "hard_boundary_max_abs": 0.0,
        "deviations": [
            "analytic 1D profiles instead of the 2D standard Pipe dataset",
            "scalar constitutive fit instead of Geo-NeW",
            "affine direct regressor instead of LaMO",
            "17 train and 15 test cases instead of 1000/200",
        ],
    }
    return rows, diagnostics


def elasticity_analogue() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Axial-bar stress analogue with an exactly constrained constitutive law."""
    train_areas = np.linspace(0.70, 1.30, 25)
    test_areas = np.linspace(0.55, 1.45, 19)
    train_stress = 1.0 / train_areas
    learned_load = float(np.mean(train_stress * train_areas))
    design = np.column_stack([np.ones_like(train_areas), train_areas])
    direct_coefficients = np.linalg.lstsq(design, train_stress, rcond=None)[0]

    rows: list[dict[str, Any]] = []
    for case_index, area in enumerate(test_areas):
        target = np.asarray([1.0 / area])
        structured = np.asarray([learned_load / area])
        direct = np.asarray([np.array([1.0, area]) @ direct_coefficients])
        damaged = np.asarray([learned_load * area])
        for method, prediction in (
            ("structured_analogue", structured),
            ("direct_affine_analogue", direct),
            ("damaged_constitutive_control", damaged),
        ):
            rows.append(
                {
                    "claim_id": "3",
                    "case": case_index,
                    "parameter": float(area),
                    "method": method,
                    "normalized_l2": normalized_l2(prediction, target),
                }
            )
    diagnostics = {
        "task": "1D axial-bar derived stress over cross-sectional area",
        "learned_load": learned_load,
        "train_area_range": [float(train_areas.min()), float(train_areas.max())],
        "test_area_range": [float(test_areas.min()), float(test_areas.max())],
        "deviations": [
            "1D axial stress instead of the 2D Elasticity point-cloud benchmark",
            "analytic reciprocal-area law instead of Geo-NeW",
            "affine direct regressor instead of LaMO",
            "25 train and 19 test cases instead of 1000/200",
        ],
    }
    return rows, diagnostics


def points_in_regular_polygon(
    x: np.ndarray,
    y: np.ndarray,
    sides: int,
    radius: float,
    rotation: float,
) -> np.ndarray:
    angles = rotation + np.arange(sides) * 2.0 * np.pi / sides
    vertices = np.column_stack(
        [0.5 + radius * np.cos(angles), 0.5 + radius * np.sin(angles)]
    )
    inside = np.zeros_like(x, dtype=bool)
    previous = vertices[-1]
    for current in vertices:
        x1, y1 = previous
        x2, y2 = current
        crosses = (y1 > y) != (y2 > y)
        intersection_x = (x2 - x1) * (y - y1) / (y2 - y1 + 1e-300) + x1
        inside ^= crosses & (x < intersection_x)
        previous = current
    return inside


def poisson_matrix(mask: np.ndarray) -> tuple[Any, np.ndarray, float]:
    grid_size = mask.shape[0]
    unknown = mask.copy()
    unknown[[0, -1], :] = False
    unknown[:, [0, -1]] = False
    coordinates = np.argwhere(unknown)
    index = -np.ones_like(mask, dtype=int)
    index[unknown] = np.arange(coordinates.shape[0])
    row: list[int] = []
    column: list[int] = []
    data: list[float] = []
    for matrix_row, (i, j) in enumerate(coordinates):
        row.append(matrix_row)
        column.append(matrix_row)
        data.append(4.0)
        for di, dj in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            neighbor = index[i + di, j + dj]
            if neighbor >= 0:
                row.append(matrix_row)
                column.append(int(neighbor))
                data.append(-1.0)
    matrix = coo_matrix(
        (data, (row, column)), shape=(coordinates.shape[0], coordinates.shape[0])
    ).tocsr()
    spacing = 1.0 / (grid_size - 1)
    return matrix, unknown, spacing


def solve_poisson(mask: np.ndarray, diffusivity: float = 1.0) -> np.ndarray:
    matrix, unknown, spacing = poisson_matrix(mask)
    rhs = np.full(matrix.shape[0], spacing**2 / diffusivity)
    solution = np.zeros_like(mask, dtype=float)
    solution[unknown] = spsolve(matrix, rhs)
    return solution


def infer_diffusivity(mask_solution_pairs: Iterable[tuple[np.ndarray, np.ndarray]]) -> float:
    residual_values: list[np.ndarray] = []
    for mask, solution in mask_solution_pairs:
        matrix, unknown, spacing = poisson_matrix(mask)
        residual_values.append(matrix @ solution[unknown] / spacing**2)
    inverse_diffusivity = float(np.concatenate(residual_values).mean())
    return 1.0 / inverse_diffusivity


def polygon_poisson_analogue(
    grid_size: int = 29,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    axis = np.linspace(0.0, 1.0, grid_size)
    x, y = np.meshgrid(axis, axis, indexing="ij")
    train_specs = [
        (sides, radius, rotation)
        for sides in (3, 4)
        for radius in (0.13, 0.17, 0.21)
        for rotation in (0.0, 0.31)
    ]
    test_specs = [
        (sides, radius, rotation)
        for sides in (6, 7, 8)
        for radius in (0.14, 0.18, 0.22)
        for rotation in (0.17, 0.39)
    ]

    train_pairs: list[tuple[np.ndarray, np.ndarray]] = []
    for sides, radius, rotation in train_specs:
        mask = ~points_in_regular_polygon(x, y, sides, radius, rotation)
        train_pairs.append((mask, solve_poisson(mask)))
    learned_diffusivity = infer_diffusivity(train_pairs)
    direct_template = np.mean([solution for _, solution in train_pairs], axis=0)

    rows: list[dict[str, Any]] = []
    for case_index, (sides, radius, rotation) in enumerate(test_specs):
        mask = ~points_in_regular_polygon(x, y, sides, radius, rotation)
        target = solve_poisson(mask)
        structured = solve_poisson(mask, learned_diffusivity)
        direct = direct_template
        damaged = solve_poisson(mask, learned_diffusivity * 0.70)
        parameter = f"sides={sides};radius={radius:.2f};rotation={rotation:.2f}"
        for method, prediction in (
            ("structured_analogue", structured),
            ("direct_template_analogue", direct),
            ("damaged_operator_control", damaged),
        ):
            rows.append(
                {
                    "claim_id": "4",
                    "case": case_index,
                    "parameter": parameter,
                    "method": method,
                    "normalized_l2": normalized_l2(prediction, target),
                }
            )
    diagnostics = {
        "task": "finite-difference scalar Poisson with polygonal holes",
        "learned_diffusivity": learned_diffusivity,
        "train_polygon_sides": [3, 4],
        "test_polygon_sides": [6, 7, 8],
        "grid_size": grid_size,
        "deviations": [
            "synthetic finite-difference data instead of the paper's processed FEM data",
            "one learned scalar operator instead of Geo-NeW",
            "mean-field template instead of Linear Attention",
            "18 OOD cases rather than the paper's unreleased split",
        ],
    }
    return rows, diagnostics


def angled_step_mask(
    x: np.ndarray, y: np.ndarray, angle_degrees: float
) -> np.ndarray:
    angle_radians = np.deg2rad(angle_degrees)
    step_floor = np.where(
        x < 0.45, 0.0, 0.12 + np.tan(angle_radians) * (x - 0.45)
    )
    return y >= step_floor


def angled_step_analogue(
    grid_size: int = 29,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    axis = np.linspace(0.0, 1.0, grid_size)
    x, y = np.meshgrid(axis, axis, indexing="ij")
    train_angles = np.asarray([0.0, 5.0, 10.0])
    test_angles = np.asarray([15.0, 20.0, 25.0, 30.0])
    train_pairs = [
        (angled_step_mask(x, y, float(angle)), None) for angle in train_angles
    ]
    train_pairs = [(mask, solve_poisson(mask)) for mask, _ in train_pairs]
    learned_diffusivity = infer_diffusivity(train_pairs)

    train_stack = np.stack([solution for _, solution in train_pairs])
    design = np.column_stack([np.ones_like(train_angles), train_angles])
    direct_coefficients = np.linalg.lstsq(
        design, train_stack.reshape(train_angles.size, -1), rcond=None
    )[0]

    rows: list[dict[str, Any]] = []
    per_angle: dict[str, dict[str, float]] = {}
    for case_index, angle in enumerate(test_angles):
        mask = angled_step_mask(x, y, float(angle))
        target = solve_poisson(mask)
        structured = solve_poisson(mask, learned_diffusivity)
        direct = (
            np.array([1.0, angle]) @ direct_coefficients
        ).reshape(target.shape)
        damaged = solve_poisson(angled_step_mask(x, y, 0.0), learned_diffusivity)
        angle_results: dict[str, float] = {}
        for method, prediction in (
            ("structured_analogue", structured),
            ("direct_angle_extrapolation_analogue", direct),
            ("wrong_geometry_control", damaged),
        ):
            error = normalized_l2(prediction, target)
            angle_results[method] = error
            rows.append(
                {
                    "claim_id": "6",
                    "case": case_index,
                    "parameter": float(angle),
                    "method": method,
                    "normalized_l2": error,
                }
            )
        per_angle[str(int(angle))] = angle_results

    last_meaningful: dict[str, int | None] = {}
    for method in (
        "structured_analogue",
        "direct_angle_extrapolation_analogue",
    ):
        accepted = [
            int(angle)
            for angle in test_angles
            if per_angle[str(int(angle))][method] <= TOY_THRESHOLD
        ]
        last_meaningful[method] = max(accepted) if accepted else None
    diagnostics = {
        "task": "finite-difference scalar Poisson on angled-step domains",
        "learned_diffusivity": learned_diffusivity,
        "train_angles_degrees": train_angles.tolist(),
        "test_angles_degrees": test_angles.tolist(),
        "toy_preregistered_meaningful_threshold_normalized_l2": TOY_THRESHOLD,
        "last_meaningful_angle_degrees": last_meaningful,
        "per_angle_errors": per_angle,
        "grid_size": grid_size,
        "deviations": [
            "scalar Poisson instead of steady incompressible Navier-Stokes",
            "synthetic finite-difference geometries instead of NS2d-c++ COMSOL/Gmsh",
            "one learned scalar operator instead of Geo-NeW",
            "linear angle extrapolation instead of Transolver",
            "the 0.10 meaningful threshold is preregistered for this toy only",
        ],
    }
    return rows, diagnostics


@dataclass(frozen=True)
class ToyResult:
    rows: list[dict[str, Any]]
    diagnostics: dict[str, Any]


def summarize_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    summary: dict[str, Any] = {}
    for claim_id in ("2", "3", "4", "6"):
        claim_rows = [row for row in rows if row["claim_id"] == claim_id]
        methods = sorted({row["method"] for row in claim_rows})
        method_summary = {
            method: bootstrap_mean_interval(
                row["normalized_l2"]
                for row in claim_rows
                if row["method"] == method
            )
            for method in methods
        }
        structured_mean = method_summary["structured_analogue"]["mean"]
        direct_method = next(method for method in methods if method.startswith("direct_"))
        direct_mean = method_summary[direct_method]["mean"]
        method_summary["structured_vs_direct_relative_reduction_percent"] = (
            100.0 * (direct_mean - structured_mean) / direct_mean
        )
        summary[claim_id] = method_summary
    return summary


def run_suite() -> dict[str, Any]:
    experiments = {
        "2": pipe_analogue(),
        "3": elasticity_analogue(),
        "4": polygon_poisson_analogue(),
        "6": angled_step_analogue(),
    }
    rows = [row for experiment_rows, _ in experiments.values() for row in experiment_rows]
    diagnostics = {
        claim_id: experiment_diagnostics
        for claim_id, (_, experiment_diagnostics) in experiments.items()
    }
    summary = summarize_rows(rows)
    negative_controls_pass = {}
    for claim_id, claim_summary in summary.items():
        structured_mean = claim_summary["structured_analogue"]["mean"]
        control_method = next(
            method
            for method in claim_summary
            if isinstance(claim_summary[method], dict)
            and (method.endswith("_control"))
        )
        negative_controls_pass[claim_id] = (
            claim_summary[control_method]["mean"] > structured_mean + 1e-10
        )
    result = {
        "scale_label": "TOY",
        "scope": "mechanism analogues; not the paper benchmarks or models",
        "seed": SEED,
        "summary": summary,
        "diagnostics": diagnostics,
        "negative_controls_pass": negative_controls_pass,
        "formal_claim_verdicts_unchanged": {
            "2": "BLOCKED",
            "3": "BLOCKED",
            "4": "BLOCKED",
            "6": "BLOCKED",
        },
        "rows": rows,
    }
    return result


def independently_check(result: dict[str, Any]) -> dict[str, Any]:
    failures: list[str] = []
    if result["scale_label"] != "TOY":
        failures.append("scale label is not TOY")
    if set(result["formal_claim_verdicts_unchanged"].values()) != {"BLOCKED"}:
        failures.append("toy evidence changed a formal verdict")
    if not all(result["negative_controls_pass"].values()):
        failures.append("at least one damaged-structure control was not detected")
    for row in result["rows"]:
        error = row["normalized_l2"]
        if not math.isfinite(error) or error < 0:
            failures.append(f"invalid error in claim {row['claim_id']}")
    return {
        "checker": "independent toy-scope and invariant checker",
        "passed": not failures,
        "failures": failures,
    }


def write_outputs(result: dict[str, Any], json_path: Path, csv_path: Path) -> None:
    json_path.parent.mkdir(parents=True, exist_ok=True)
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    serializable = dict(result)
    rows = serializable.pop("rows")
    json_path.write_text(
        json.dumps(serializable, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["claim_id", "case", "parameter", "method", "normalized_l2"],
        )
        writer.writeheader()
        writer.writerows(rows)

