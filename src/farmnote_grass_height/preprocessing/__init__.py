"""Leakage-safe preprocessing used by the FarmNote experiments."""

from .pipeline import build_preprocessor, records_to_matrix
from .transformers import (
    BoolToIntTransformer,
    DateTimeFeaturesTransformer,
    FrequencyEncoder,
    KFoldTargetEncoder,
)

__all__ = [
    "BoolToIntTransformer",
    "DateTimeFeaturesTransformer",
    "FrequencyEncoder",
    "KFoldTargetEncoder",
    "build_preprocessor",
    "records_to_matrix",
]
