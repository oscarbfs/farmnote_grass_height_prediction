"""Independent reproduction of the two FarmNote training experiments."""

from __future__ import annotations

import json
import math
import platform
import warnings
from dataclasses import dataclass
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any, Iterable

import joblib
import numpy as np
import pandas as pd
from lightgbm import LGBMRegressor
from sklearn.base import clone
from sklearn.exceptions import ConvergenceWarning
from sklearn.metrics import make_scorer, mean_squared_error
from sklearn.model_selection import GridSearchCV
from sklearn.pipeline import Pipeline

from ..data.features import (
    EXPERIMENTS,
    build_feature_names,
    excluded_columns,
)
from ..data.loader import file_sha256, load_analytical_dataset
from ..data.schema import TARGET_COLUMN
from ..evaluation.metrics import article_ranking_key, regression_metrics
from ..models import MODEL_NAMES, ModelDefinition, get_model_definitions, make_pipeline_param_grid
from ..preprocessing import build_preprocessor, records_to_matrix
from .artifacts import ExperimentPaths, write_json, write_metrics
from .split import original_holdout_indices


TEST_SIZE = 0.2
RANDOM_STATE = 42
SEARCH_CV_FOLDS = 5
TARGET_ENCODER_FOLDS = 5
TARGET_ENCODER_SMOOTHING = 10.0


def _rmse(y_true, y_pred) -> float:
    return math.sqrt(mean_squared_error(y_true, y_pred))


RMSE_SCORER = make_scorer(_rmse, greater_is_better=False)


@dataclass(frozen=True)
class ExperimentRun:
    experiment: str
    output_directory: Path
    metrics: list[dict[str, Any]]
    manifest: dict[str, Any]


def _package_versions() -> dict[str, str]:
    packages = [
        "joblib",
        "lightgbm",
        "matplotlib",
        "numpy",
        "pandas",
        "scikit-learn",
        "shap",
    ]
    output = {"python": platform.python_version()}
    for package in packages:
        try:
            output[package] = version(package)
        except PackageNotFoundError:
            output[package] = "not-installed"
    return output


def _selected_definitions(model_names: Iterable[str] | None) -> list[ModelDefinition]:
    requested = list(model_names or MODEL_NAMES)
    unknown = sorted(set(requested) - set(MODEL_NAMES))
    if unknown:
        raise ValueError(f"Unknown model name(s): {unknown}")
    by_name = {definition.name: definition for definition in get_model_definitions()}
    return [by_name[name] for name in MODEL_NAMES if name in requested]


def _smoke_grid(grid: dict[str, list[Any]]) -> dict[str, list[Any]]:
    return {key: [values[0]] for key, values in grid.items()}


def _attempt_final_fit(
    pipeline: Pipeline,
    X_train: list[list[Any]],
    y_train: list[float],
    *,
    sample_weight: list[float],
    eval_set: list[tuple[list[list[Any]], list[float]]] | None = None,
    early_stopping_rounds: int | None = None,
) -> Pipeline:
    """Use the private service's fallback sequence for final fitting.

    For LightGBM the raw-space ``eval_set`` is incompatible with the estimator's
    transformed feature space in the source pipeline. Failed metadata attempts
    therefore fall through to an ordinary fit, preserving the effective run.
    """

    attempts: list[dict[str, Any]] = []
    unprefixed: dict[str, Any] = {"sample_weight": sample_weight}
    prefixed: dict[str, Any] = {"est__sample_weight": sample_weight}
    nested: dict[str, Any] = {"est__estimator__sample_weight": sample_weight}
    if eval_set is not None:
        unprefixed["eval_set"] = eval_set
        prefixed["est__eval_set"] = eval_set
        nested["est__estimator__eval_set"] = eval_set
    if early_stopping_rounds is not None:
        unprefixed["early_stopping_rounds"] = early_stopping_rounds
        prefixed["est__early_stopping_rounds"] = early_stopping_rounds
        nested["est__estimator__early_stopping_rounds"] = early_stopping_rounds
    attempts.extend([unprefixed, prefixed, nested, {}])

    last_error: Exception | None = None
    for fit_parameters in attempts:
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", ConvergenceWarning)
                warnings.filterwarnings(
                    "ignore",
                    message=r".*X does not have valid feature names.*",
                    category=UserWarning,
                )
                pipeline.fit(X_train, y_train, **fit_parameters)
            return pipeline
        except Exception as error:  # intentionally mirrors the source fallback
            last_error = error
    assert last_error is not None
    raise RuntimeError("All final pipeline-fit attempts failed.") from last_error


def _friendly_best_params(best_params: dict[str, Any]) -> dict[str, Any]:
    output: dict[str, Any] = {}
    for key, value in best_params.items():
        clean = key.removeprefix("est__")
        if clean == "estimator__max_depth":
            clean = "base_estimator_max_depth"
        elif clean == "estimator__min_samples_split":
            clean = "base_estimator_min_samples_split"
        output[clean] = value
    return output


def _search_results_frame(search: GridSearchCV) -> pd.DataFrame:
    raw = pd.DataFrame(search.cv_results_)
    columns = [
        column
        for column in raw.columns
        if column == "params"
        or column.startswith("param_")
        or column.startswith("split") and column.endswith("_test_score")
        or column in {"mean_test_score", "std_test_score", "rank_test_score"}
    ]
    return raw.loc[:, columns]


def run_experiment(
    dataset_path: str | Path,
    output_root: str | Path,
    *,
    experiment: str,
    model_names: Iterable[str] | None = None,
    smoke: bool = False,
) -> ExperimentRun:
    """Train, tune, evaluate, and persist one feature-set experiment."""

    if experiment not in EXPERIMENTS:
        raise ValueError(f"Unknown experiment {experiment!r}; expected one of {EXPERIMENTS}")

    dataset_path = Path(dataset_path)
    frame = load_analytical_dataset(dataset_path)
    feature_names = build_feature_names(experiment)
    definitions = _selected_definitions(model_names)
    train_indices, test_indices = original_holdout_indices(
        len(frame), test_size=TEST_SIZE, random_state=RANDOM_STATE
    )

    X_all = records_to_matrix(frame, feature_names)
    y_all = frame[TARGET_COLUMN].astype(float).tolist()
    X_train = [X_all[index] for index in train_indices]
    X_test = [X_all[index] for index in test_indices]
    y_train = [y_all[index] for index in train_indices]
    y_test = [y_all[index] for index in test_indices]
    training_frame = frame.iloc[train_indices]

    run_kind = "smoke" if smoke else "reproduced"
    output_directory = Path(output_root) / run_kind / experiment
    paths = ExperimentPaths(output_directory)
    paths.ensure()
    search_directory = output_directory / "search_results"
    search_directory.mkdir(parents=True, exist_ok=True)

    metric_rows: list[dict[str, Any]] = []
    model_manifest: list[dict[str, Any]] = []

    for definition in definitions:
        preprocessor = build_preprocessor(
            training_frame,
            feature_names,
            random_state=RANDOM_STATE,
            categorical_encoding="target",
        )
        pipeline = Pipeline(
            [("preproc", preprocessor), ("est", clone(definition.estimator))]
        )
        parameter_grid = make_pipeline_param_grid(definition)
        if smoke:
            parameter_grid = _smoke_grid(parameter_grid)

        search = GridSearchCV(
            pipeline,
            param_grid=parameter_grid,
            cv=SEARCH_CV_FOLDS,
            scoring=RMSE_SCORER,
            n_jobs=1,
            refit=False,
        )
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", ConvergenceWarning)
            warnings.filterwarnings(
                "ignore",
                message=r".*X does not have valid feature names.*",
                category=UserWarning,
            )
            search.fit(X_train, y_train)

        best_params = dict(search.best_params_)
        pipeline.set_params(**best_params)
        is_lgbm = isinstance(pipeline.named_steps["est"], LGBMRegressor)
        fitted = _attempt_final_fit(
            pipeline,
            X_train,
            y_train,
            sample_weight=[1.0] * len(X_train),
            eval_set=[(X_test, y_test)] if is_lgbm else None,
            early_stopping_rounds=10 if is_lgbm else None,
        )

        with warnings.catch_warnings():
            warnings.filterwarnings(
                "ignore",
                message=r".*X does not have valid feature names.*",
                category=UserWarning,
            )
            train_predictions = np.asarray(fitted.predict(X_train), dtype=float)
            test_predictions = np.asarray(fitted.predict(X_test), dtype=float)
        train_metrics = regression_metrics(y_train, train_predictions)
        test_metrics = regression_metrics(y_test, test_predictions)
        search_cv_rmse = -float(search.best_score_)
        friendly_params = _friendly_best_params(best_params)

        model_path = paths.models / f"{definition.name}.joblib"
        joblib.dump(fitted, model_path)
        prediction_path = paths.predictions / f"{definition.name}.csv"
        pd.DataFrame(
            {
                "row_id": frame.iloc[test_indices]["id"].astype(str).tolist(),
                "pasturage_event_id": frame.iloc[test_indices]["pasturage_event_id"].astype(str).tolist(),
                "y_true": y_test,
                "y_pred": test_predictions,
            }
        ).to_csv(prediction_path, index=False, encoding="utf-8", float_format="%.15g")
        _search_results_frame(search).to_csv(
            search_directory / f"{definition.name}.csv",
            index=False,
            encoding="utf-8",
            float_format="%.15g",
        )

        row = {
            "experiment": experiment,
            "model": definition.name,
            "model_label": definition.label,
            "n_train": len(train_indices),
            "n_test": len(test_indices),
            "feature_count": len(feature_names),
            "train_r2": train_metrics["r2"],
            "train_mse": train_metrics["mse"],
            "train_rmse": train_metrics["rmse"],
            "train_mae": train_metrics["mae"],
            "test_r2": test_metrics["r2"],
            "test_mse": test_metrics["mse"],
            "test_rmse": test_metrics["rmse"],
            "test_mae": test_metrics["mae"],
            "holdout_rmse": test_metrics["rmse"],
            "legacy_reported_cv_rmse": test_metrics["rmse"],
            "search_cv_rmse": search_cv_rmse,
            "best_params": json.dumps(friendly_params, sort_keys=True, separators=(",", ":")),
        }
        metric_rows.append(row)
        model_manifest.append(
            {
                "name": definition.name,
                "label": definition.label,
                "artifact": str(model_path.relative_to(output_directory)).replace("\\", "/"),
                "predictions": str(prediction_path.relative_to(output_directory)).replace("\\", "/"),
                "search_results": f"search_results/{definition.name}.csv",
                "best_params": friendly_params,
                "search_cv_rmse": search_cv_rmse,
                "holdout_rmse": test_metrics["rmse"],
            }
        )

    metric_rows.sort(key=article_ranking_key)
    for rank, row in enumerate(metric_rows, start=1):
        row["article_compatible_rank"] = rank
    write_metrics(paths.metrics, metric_rows)

    manifest = {
        "schema_version": 1,
        "run_kind": run_kind,
        "experiment": experiment,
        "dataset_filename": dataset_path.name,
        "dataset_sha256": file_sha256(dataset_path),
        "target": TARGET_COLUMN,
        "feature_names": feature_names,
        "excluded_columns": excluded_columns(experiment),
        "test_size": TEST_SIZE,
        "random_state": RANDOM_STATE,
        "search_cv_folds": SEARCH_CV_FOLDS,
        "search_scoring": "negative root mean squared error",
        "search_refit": False,
        "target_encoder": {
            "folds": TARGET_ENCODER_FOLDS,
            "smoothing": TARGET_ENCODER_SMOOTHING,
            "random_state": RANDOM_STATE,
        },
        "split_strategy": "python_random_holdout",
        "train_indices": train_indices,
        "test_indices": test_indices,
        "train_row_ids": frame.iloc[train_indices]["id"].astype(str).tolist(),
        "test_row_ids": frame.iloc[test_indices]["id"].astype(str).tolist(),
        "ranking_for_manuscript": "holdout_rmse (legacy field named group_cv_rmse)",
        "runtime_versions": _package_versions(),
        "models": model_manifest,
    }
    write_json(paths.manifest, manifest)
    return ExperimentRun(experiment, output_directory, metric_rows, manifest)
