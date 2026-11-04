"""Factories for the fifteen regressors evaluated in the experiment.

Random-state behaviour intentionally mirrors the *factory implementation*, not
only the model specs.  The source factory applied 42 to RandomForestRegressor,
LGBMRegressor, and the outer BaggingRegressor.  It omitted ``random_state``
when constructing DecisionTreeRegressor and ExtraTreesRegressor even though
their specs contained 42; it also omitted it for GradientBoostingRegressor and
MLPRegressor.  Bagging's base decision tree was built without a seed.  Those
omissions are preserved here because changing them can change reported fits.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from lightgbm import LGBMRegressor
from sklearn.ensemble import (
    BaggingRegressor,
    ExtraTreesRegressor,
    GradientBoostingRegressor,
    HistGradientBoostingRegressor,
    RandomForestRegressor,
)
from sklearn.kernel_ridge import KernelRidge
from sklearn.linear_model import ElasticNet, Lasso, LinearRegression, Ridge
from sklearn.neighbors import KNeighborsRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.svm import SVR
from sklearn.tree import DecisionTreeRegressor

from .grids import (
    MODEL_NAMES,
    get_estimator_param_grid,
    get_model_param_grid,
)


@dataclass(frozen=True, slots=True)
class ModelDefinition:
    """A fresh base estimator and its unprefixed source hyperparameter grid."""

    name: str
    label: str
    estimator: Any
    param_grid: dict[str, list[Any]]


def _bagging_regressor() -> BaggingRegressor:
    base_estimator = DecisionTreeRegressor(
        max_depth=None,
        min_samples_split=2,
    )
    kwargs = {
        "n_estimators": 20,
        "max_samples": 0.6,
        "max_features": 0.6,
        "bootstrap": True,
        "bootstrap_features": False,
        "random_state": 42,
    }
    try:
        return BaggingRegressor(estimator=base_estimator, **kwargs)
    except TypeError:  # scikit-learn < 1.2, as handled by the source API
        return BaggingRegressor(base_estimator=base_estimator, **kwargs)


def get_model_definitions() -> tuple[ModelDefinition, ...]:
    """Return fresh estimators in the exact training-datasource order."""

    definitions = (
        ModelDefinition(
            "linear_regression",
            "Linear Regression",
            LinearRegression(fit_intercept=True),
            get_model_param_grid("linear_regression"),
        ),
        ModelDefinition(
            "ridge",
            "Ridge",
            Ridge(alpha=0.01, fit_intercept=True),
            get_model_param_grid("ridge"),
        ),
        ModelDefinition(
            "lasso",
            "Lasso",
            Lasso(alpha=0.0005, fit_intercept=True),
            get_model_param_grid("lasso"),
        ),
        ModelDefinition(
            "elastic_net",
            "Elastic Net",
            ElasticNet(alpha=0.01, l1_ratio=0.2, fit_intercept=True),
            get_model_param_grid("elastic_net"),
        ),
        ModelDefinition(
            "svr",
            "Support Vector Regression",
            SVR(kernel="rbf", C=0.1, epsilon=0.01),
            get_model_param_grid("svr"),
        ),
        # random_state=42 existed in this spec, but the source factory omitted
        # it; leave the sklearn default (None) intact.
        ModelDefinition(
            "decision_tree_regressor",
            "Decision Tree Regressor",
            DecisionTreeRegressor(max_depth=3, min_samples_split=5),
            get_model_param_grid("decision_tree_regressor"),
        ),
        ModelDefinition(
            "random_forest_regressor",
            "Random Forest Regressor",
            RandomForestRegressor(
                n_estimators=100,
                max_depth=5,
                min_samples_split=5,
                random_state=42,
            ),
            get_model_param_grid("random_forest_regressor"),
        ),
        # As with DecisionTree, the source ExtraTrees factory did not forward
        # the spec's random_state=42.
        ModelDefinition(
            "extra_trees_regressor",
            "Extra Trees Regressor",
            ExtraTreesRegressor(n_estimators=100, max_depth=5),
            get_model_param_grid("extra_trees_regressor"),
        ),
        ModelDefinition(
            "gradient_boosting_regressor",
            "Gradient Boosting Regressor",
            GradientBoostingRegressor(
                learning_rate=0.05,
                n_estimators=100,
                max_depth=2,
            ),
            get_model_param_grid("gradient_boosting_regressor"),
        ),
        ModelDefinition(
            "hist_gradient_boosting_regressor",
            "Histogram Gradient Boosting Regressor",
            HistGradientBoostingRegressor(
                learning_rate=0.05,
                max_iter=100,
                max_depth=3,
            ),
            get_model_param_grid("hist_gradient_boosting_regressor"),
        ),
        ModelDefinition(
            "kneighbors_regressor",
            "K-Neighbors Regressor",
            KNeighborsRegressor(n_neighbors=3, weights="uniform"),
            get_model_param_grid("kneighbors_regressor"),
        ),
        ModelDefinition(
            "mlp_regressor",
            "MLP Regressor",
            MLPRegressor(
                hidden_layer_sizes=(50,),
                activation="relu",
                alpha=0.0001,
                max_iter=500,
            ),
            get_model_param_grid("mlp_regressor"),
        ),
        ModelDefinition(
            "lgbm_regressor",
            "LightGBM Regressor",
            LGBMRegressor(
                n_estimators=200,
                learning_rate=0.05,
                objective="regression",
                boosting_type="gbdt",
                num_leaves=15,
                max_depth=-1,
                min_child_samples=5,
                subsample=0.8,
                colsample_bytree=0.8,
                reg_alpha=0.0,
                reg_lambda=0.0,
                random_state=42,
                verbose=-1,
            ),
            get_model_param_grid("lgbm_regressor"),
        ),
        ModelDefinition(
            "kernel_ridge_regressor",
            "Kernel Ridge Regressor",
            KernelRidge(
                alpha=0.01,
                kernel="rbf",
                gamma=None,
                degree=2,
                coef0=0.0,
            ),
            get_model_param_grid("kernel_ridge_regressor"),
        ),
        ModelDefinition(
            "bagging_regressor",
            "Bagging Regressor",
            _bagging_regressor(),
            get_model_param_grid("bagging_regressor"),
        ),
    )
    if tuple(definition.name for definition in definitions) != MODEL_NAMES:
        raise RuntimeError("Model registry order diverged from the source experiment.")
    return definitions


def get_model_definition(model_name: str) -> ModelDefinition:
    """Return a fresh definition for one named model."""

    for definition in get_model_definitions():
        if definition.name == model_name:
            return definition
    raise KeyError(f"Unknown model: {model_name}")


def make_pipeline_param_grid(
    definition_or_name: ModelDefinition | str,
    *,
    step_name: str = "est",
) -> dict[str, list[Any]]:
    """Prefix the effective GridSearchCV space for an sklearn Pipeline.

    This reproduces both the ``est__`` prefix used for a single target and the
    nested Bagging base-estimator translation.  The study has one target, so no
    MultiOutputRegressor ``estimator__`` wrapper is added.
    """

    model_name = (
        definition_or_name.name
        if isinstance(definition_or_name, ModelDefinition)
        else definition_or_name
    )
    return {
        f"{step_name}__{key}": values
        for key, values in get_estimator_param_grid(model_name).items()
    }


# Convenient read-only-by-convention snapshots for discovery.  Training code
# should call get_model_definitions() to receive fresh, unfitted estimators.
MODEL_DEFINITIONS: tuple[ModelDefinition, ...] = get_model_definitions()
MODEL_REGISTRY: dict[str, ModelDefinition] = {
    definition.name: definition for definition in MODEL_DEFINITIONS
}
