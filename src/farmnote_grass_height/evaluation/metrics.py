"""Regression metrics and transparent ranking fields used by the experiments."""

from __future__ import annotations

import math
from collections.abc import Sequence
from typing import Any

import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


def regression_metrics(y_true: Sequence[float], y_pred: Sequence[float]) -> dict[str, float]:
    """Compute the four regression metrics retained by the original service."""

    true = np.asarray(y_true, dtype=float)
    pred = np.asarray(y_pred, dtype=float)
    mse = float(mean_squared_error(true, pred))
    return {
        "r2": float(r2_score(true, pred)),
        "mse": mse,
        "rmse": float(math.sqrt(mse)),
        "mae": float(mean_absolute_error(true, pred)),
    }


def finite_or_none(value: Any) -> float | None:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    return parsed if math.isfinite(parsed) else None


def article_ranking_key(row: dict[str, Any]) -> tuple[float, str]:
    """Reproduce the model-family ranking that generated the manuscript tables.

    The private implementation called the fallback holdout value "group_cv_rmse".
    Sorting by holdout RMSE therefore reproduces the published order; the public
    reports also retain the genuine GridSearchCV score in ``search_cv_rmse``.
    """

    value = finite_or_none(row.get("holdout_rmse"))
    return (value if value is not None else float("inf"), str(row.get("model", "")))


def search_cv_ranking_key(row: dict[str, Any]) -> tuple[float, str]:
    value = finite_or_none(row.get("search_cv_rmse"))
    return (value if value is not None else float("inf"), str(row.get("model", "")))
