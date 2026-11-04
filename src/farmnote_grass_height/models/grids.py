"""Hyperparameter grids passed by the pasturage training datasource."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

MODEL_NAMES: tuple[str, ...] = (
    "linear_regression",
    "ridge",
    "lasso",
    "elastic_net",
    "svr",
    "decision_tree_regressor",
    "random_forest_regressor",
    "extra_trees_regressor",
    "gradient_boosting_regressor",
    "hist_gradient_boosting_regressor",
    "kneighbors_regressor",
    "mlp_regressor",
    "lgbm_regressor",
    "kernel_ridge_regressor",
    "bagging_regressor",
)

# Dict insertion order matches the model-spec construction order and field
# order in TrainPasturageModelDatasourceImpl.
MODEL_PARAM_GRIDS: dict[str, dict[str, list[Any]]] = {
    "linear_regression": {
        "fit_intercept": [True, False],
    },
    "ridge": {
        "alpha": [0.01, 0.1, 1.0, 10.0],
        "fit_intercept": [True, False],
    },
    "lasso": {
        "alpha": [0.0005, 0.001, 0.01, 0.1, 1.0],
        "fit_intercept": [True, False],
    },
    "elastic_net": {
        "alpha": [0.01, 0.1, 1.0, 10.0],
        "l1_ratio": [0.2, 0.5, 0.8],
        "fit_intercept": [True, False],
    },
    "svr": {
        "kernel": ["rbf", "linear"],
        "C": [0.1, 1, 10],
        "epsilon": [0.01, 0.1, 0.5],
    },
    "decision_tree_regressor": {
        "max_depth": [3, 5, 8],
        "min_samples_split": [5, 10, 15],
    },
    "random_forest_regressor": {
        "n_estimators": [100, 300],
        "max_depth": [5, 10, 20],
        "min_samples_split": [5, 10],
    },
    "extra_trees_regressor": {
        "n_estimators": [100, 300],
        "max_depth": [5, 10, 20],
    },
    "gradient_boosting_regressor": {
        "learning_rate": [0.05, 0.1],
        "n_estimators": [100, 300],
        "max_depth": [2, 3],
    },
    "hist_gradient_boosting_regressor": {
        "learning_rate": [0.05, 0.1],
        "max_iter": [100, 300],
        "max_depth": [3, 6],
    },
    "kneighbors_regressor": {
        "n_neighbors": [3, 5, 7],
        "weights": ["uniform", "distance"],
    },
    "mlp_regressor": {
        "hidden_layer_sizes": [(50,), (100,), (50, 50)],
        "activation": ["relu", "tanh"],
        "alpha": [0.0001, 0.001, 0.01],
    },
    "lgbm_regressor": {
        "n_estimators": [200, 500],
        "learning_rate": [0.05, 0.1],
        "objective": ["regression", "huber"],
        "boosting_type": ["gbdt"],
        "num_leaves": [15, 31, 63],
        "max_depth": [-1, 6, 10],
        "min_child_samples": [5, 10, 20],
        "subsample": [0.8, 1.0],
        "colsample_bytree": [0.8, 1.0],
        "reg_alpha": [0.0, 0.1],
        "reg_lambda": [0.0, 0.1],
        "early_stopping_rounds": [10],
    },
    "kernel_ridge_regressor": {
        "alpha": [0.01, 0.1, 1.0, 10.0],
        "kernel": ["rbf", "polynomial", "linear"],
        "gamma": [None, 0.01, 0.1, 1.0],
        "degree": [2, 3, 4],
        "coef0": [0.0, 1.0],
    },
    "bagging_regressor": {
        "n_estimators": [20, 50, 100],
        "max_samples": [0.6, 0.8, 1.0],
        "max_features": [0.6, 0.8, 1.0],
        "bootstrap": [True],
        "bootstrap_features": [False],
        "base_estimator_max_depth": [None, 5, 10],
        "base_estimator_min_samples_split": [2, 5, 10],
    },
}


def get_model_param_grid(model_name: str) -> dict[str, list[Any]]:
    """Return a defensive copy of the raw source spec for ``model_name``."""

    try:
        return deepcopy(MODEL_PARAM_GRIDS[model_name])
    except KeyError as error:
        raise KeyError(f"Unknown model: {model_name}") from error


def get_estimator_param_grid(model_name: str) -> dict[str, list[Any]]:
    """Return parameters as they were effectively exposed to GridSearchCV.

    The source removed LightGBM's singleton ``early_stopping_rounds`` from the
    search grid and passed its first value during final fitting.  Bagging's two
    base-tree pseudo-fields were translated into nested estimator parameters.
    """

    raw_grid = get_model_param_grid(model_name)
    raw_grid.pop("early_stopping_rounds", None)
    if model_name != "bagging_regressor":
        return raw_grid

    translated: dict[str, list[Any]] = {}
    for key, values in raw_grid.items():
        if key == "base_estimator_max_depth":
            translated["estimator__max_depth"] = values
        elif key == "base_estimator_min_samples_split":
            translated["estimator__min_samples_split"] = values
        else:
            translated[key] = values
    return translated


if tuple(MODEL_PARAM_GRIDS) != MODEL_NAMES:
    raise RuntimeError("Model-grid order diverged from the source experiment.")
