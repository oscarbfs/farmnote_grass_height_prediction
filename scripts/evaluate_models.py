"""Recompute train/holdout metrics from saved public model artifacts."""

from __future__ import annotations

import argparse
import math
import warnings
from pathlib import Path

import joblib
import pandas as pd

from _bootstrap import DEFAULT_DATASET, DEFAULT_RESULTS_ROOT  # noqa: F401

from farmnote_grass_height.data.features import EXPERIMENTS
from farmnote_grass_height.data.loader import file_sha256, load_analytical_dataset
from farmnote_grass_height.evaluation import regression_metrics
from farmnote_grass_height.preprocessing import records_to_matrix
from farmnote_grass_height.training.artifacts import read_json


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_RESULTS_ROOT)
    parser.add_argument("--experiment", choices=EXPERIMENTS, required=True)
    parser.add_argument("--run-kind", choices=["reproduced", "smoke"], default="reproduced")
    parser.add_argument("--models", nargs="+", help="Optional model-name subset.")
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    run_directory = args.output_root / args.run_kind / args.experiment
    manifest = read_json(run_directory / "manifest.json")
    actual_digest = file_sha256(args.dataset)
    if actual_digest != manifest["dataset_sha256"]:
        raise RuntimeError(
            "Dataset SHA-256 differs from the training manifest; refusing evaluation."
        )

    frame = load_analytical_dataset(args.dataset)
    feature_names = list(manifest["feature_names"])
    X_all = records_to_matrix(frame, feature_names)
    y_all = frame[manifest["target"]].astype(float).tolist()
    train_indices = list(map(int, manifest["train_indices"]))
    test_indices = list(map(int, manifest["test_indices"]))
    if frame.iloc[train_indices]["id"].astype(str).tolist() != manifest["train_row_ids"]:
        raise RuntimeError("Training row identities do not match the manifest.")
    if frame.iloc[test_indices]["id"].astype(str).tolist() != manifest["test_row_ids"]:
        raise RuntimeError("Holdout row identities do not match the manifest.")

    recorded = pd.read_csv(run_directory / "metrics.csv").set_index("model")
    selected = set(args.models or [model["name"] for model in manifest["models"]])
    rows = []
    for model_metadata in manifest["models"]:
        model_name = model_metadata["name"]
        if model_name not in selected:
            continue
        pipeline = joblib.load(run_directory / model_metadata["artifact"])
        X_train = [X_all[index] for index in train_indices]
        X_test = [X_all[index] for index in test_indices]
        y_train = [y_all[index] for index in train_indices]
        y_test = [y_all[index] for index in test_indices]
        with warnings.catch_warnings():
            warnings.filterwarnings(
                "ignore",
                message=r".*X does not have valid feature names.*",
                category=UserWarning,
            )
            train_predictions = pipeline.predict(X_train)
            test_predictions = pipeline.predict(X_test)
        train_metrics = regression_metrics(y_train, train_predictions)
        test_metrics = regression_metrics(y_test, test_predictions)
        expected = recorded.loc[model_name]
        rows.append(
            {
                "model": model_name,
                "train_r2": train_metrics["r2"],
                "train_rmse": train_metrics["rmse"],
                "test_r2": test_metrics["r2"],
                "test_rmse": test_metrics["rmse"],
                "train_r2_delta": train_metrics["r2"] - float(expected["train_r2"]),
                "train_rmse_delta": train_metrics["rmse"] - float(expected["train_rmse"]),
                "test_r2_delta": test_metrics["r2"] - float(expected["test_r2"]),
                "test_rmse_delta": test_metrics["rmse"] - float(expected["test_rmse"]),
            }
        )

    output = run_directory / "evaluation_recomputed.csv"
    pd.DataFrame(rows).to_csv(output, index=False, encoding="utf-8", float_format="%.15g")
    comparisons = []
    for row in rows:
        expected = recorded.loc[str(row["model"])]
        for metric in ("train_r2", "train_rmse", "test_r2", "test_rmse"):
            actual_value = float(row[metric])
            expected_value = float(expected[metric])
            comparisons.append((actual_value, expected_value))
    max_delta = max(
        (abs(actual - expected) for actual, expected in comparisons),
        default=0.0,
    )
    mismatches = [
        (actual, expected)
        for actual, expected in comparisons
        if not math.isclose(actual, expected, rel_tol=1e-12, abs_tol=1e-10)
    ]
    print(f"Models evaluated: {len(rows)}")
    print(f"Output: {output}")
    print(f"Maximum absolute metric delta: {max_delta:.3e}")
    print("Tolerance: rel=1e-12, abs=1e-10")
    return 0 if not mismatches else 1


if __name__ == "__main__":
    raise SystemExit(main())
