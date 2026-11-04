"""Regression-model registry and hyperparameter spaces."""

from .grids import (
    MODEL_NAMES,
    MODEL_PARAM_GRIDS,
    get_estimator_param_grid,
    get_model_param_grid,
)
from .registry import (
    MODEL_DEFINITIONS,
    MODEL_REGISTRY,
    ModelDefinition,
    get_model_definition,
    get_model_definitions,
    make_pipeline_param_grid,
)

__all__ = [
    "MODEL_DEFINITIONS",
    "MODEL_NAMES",
    "MODEL_PARAM_GRIDS",
    "MODEL_REGISTRY",
    "ModelDefinition",
    "get_estimator_param_grid",
    "get_model_definition",
    "get_model_definitions",
    "get_model_param_grid",
    "make_pipeline_param_grid",
]
