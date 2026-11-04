"""SHAP procedure extracted from the FarmNote service without API dependencies."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

import numpy as np
import shap


@dataclass(frozen=True)
class ShapImportance:
    explainer_type: str
    n_examples: int
    processed: list[dict[str, Any]]
    aggregated: list[dict[str, Any]]


def _dense(value: Any) -> np.ndarray:
    if hasattr(value, "toarray"):
        value = value.toarray()
    return np.asarray(value)


def _normalize_values(values: Any, n_samples: int) -> np.ndarray:
    array = np.asarray(values, dtype=float)
    if array.ndim == 2:
        if array.shape[0] == n_samples:
            return array
        if array.shape[1] == n_samples:
            return array.T
    if array.ndim == 3:
        # Single-output explainers may retain a singleton output axis.
        if array.shape[0] == n_samples and array.shape[2] == 1:
            return array[:, :, 0]
        if array.shape[0] == n_samples and array.shape[1] == 1:
            return array[:, 0, :]
    raise ValueError(f"Unexpected SHAP array shape: {array.shape}")


def _importance_rows(values: np.ndarray, names: Sequence[str]) -> list[dict[str, Any]]:
    mean_abs = np.mean(np.abs(values), axis=0)
    std_abs = np.std(np.abs(values), axis=0)
    mean_signed = np.mean(values, axis=0)
    order = np.argsort(-mean_abs)
    return [
        {
            "feature": str(names[index]) if index < len(names) else f"f{index}",
            "mean_abs_shap": float(mean_abs[index]),
            "std_abs_shap": float(std_abs[index]),
            "mean_shap": float(mean_signed[index]),
            "rank": rank,
            "feature_index": int(index),
        }
        for rank, index in enumerate(order, start=1)
    ]


def _original_raw_feature_mapping(
    processed_names: Sequence[str],
    raw_names: Sequence[str],
) -> list[list[int]]:
    """Reproduce the private service's prefix/token/substring aggregation order."""

    mapping: list[list[int]] = [[] for _ in raw_names]
    for processed_index, processed_name in enumerate(processed_names):
        matched = False
        for raw_index, raw_name in enumerate(raw_names):
            if str(processed_name).startswith(str(raw_name)):
                mapping[raw_index].append(processed_index)
                matched = True
                break
        if matched:
            continue
        if "__" in str(processed_name):
            token = str(processed_name).split("__", 1)[0]
            for raw_index, raw_name in enumerate(raw_names):
                if token == raw_name:
                    mapping[raw_index].append(processed_index)
                    matched = True
                    break
        if matched:
            continue
        for raw_index, raw_name in enumerate(raw_names):
            if str(raw_name) in str(processed_name):
                mapping[raw_index].append(processed_index)
                break
    return mapping


def compute_shap_importance(
    pipeline: Any,
    X: Sequence[Sequence[Any]],
    input_feature_names: Sequence[str],
    *,
    sample_size: int | None = 1000,
    background_size: int = 100,
    random_state: int = 0,
    max_evals: int | str | None = None,
) -> ShapImportance:
    """Explain a fitted pipeline in transformed space and aggregate to raw fields.

    Defaults match the experiment: up to 1,000 rows sampled with seed 0, the
    first 100 transformed rows as background, and ``shap.Explainer`` around the
    estimator prediction function. With the study's 67 rows no subsampling occurs.
    """

    rows = list(X)
    if not rows:
        raise ValueError("No rows available for SHAP.")
    rng = np.random.RandomState(seed=random_state)
    if sample_size is not None and sample_size < len(rows):
        indices = list(map(int, rng.choice(len(rows), size=sample_size, replace=False)))
        rows = [rows[index] for index in indices]

    preprocessor = pipeline.named_steps["preproc"]
    estimator = pipeline.named_steps["est"]
    transformed = _dense(preprocessor.transform(rows))
    try:
        processed_names = list(preprocessor.get_feature_names_out(input_feature_names))
    except Exception:
        processed_names = list(preprocessor.get_feature_names_out())
    if len(processed_names) != transformed.shape[1]:
        processed_names = [f"p{index}" for index in range(transformed.shape[1])]

    background = transformed[: min(background_size, transformed.shape[0])].copy()
    try:
        masker: Any = shap.maskers.Independent(background)
    except Exception:
        masker = background

    def predict_transformed(values: np.ndarray) -> np.ndarray:
        array = np.asarray(values)
        if array.ndim == 1:
            array = array.reshape(1, -1)
        return np.asarray(estimator.predict(array))

    explainer = shap.Explainer(predict_transformed, masker)
    if max_evals is None:
        explanation = explainer(transformed)
    else:
        explanation = explainer(transformed, max_evals=max_evals)
    values = _normalize_values(explanation.values, transformed.shape[0])
    processed_rows = _importance_rows(values, processed_names)

    mapping = _original_raw_feature_mapping(processed_names, input_feature_names)
    aggregated_values = np.zeros((values.shape[0], len(input_feature_names)), dtype=float)
    for raw_index, processed_indices in enumerate(mapping):
        if processed_indices:
            aggregated_values[:, raw_index] = np.sum(values[:, processed_indices], axis=1)
    aggregated_rows = _importance_rows(aggregated_values, input_feature_names)

    return ShapImportance(
        explainer_type=type(explainer).__name__,
        n_examples=transformed.shape[0],
        processed=processed_rows,
        aggregated=aggregated_rows,
    )


def consolidate_top_features(
    model_importances: dict[str, list[dict[str, Any]]],
    *,
    top_n: int = 10,
) -> list[dict[str, Any]]:
    """Consolidate top-N recurrence, mean rank, and mean absolute SHAP."""

    aggregate: dict[str, dict[str, list[float] | int]] = {}
    for rows in model_importances.values():
        for row in rows[:top_n]:
            feature = str(row["feature"])
            current = aggregate.setdefault(
                feature,
                {"count": 0, "ranks": [], "mean_abs_values": []},
            )
            current["count"] = int(current["count"]) + 1
            assert isinstance(current["ranks"], list)
            assert isinstance(current["mean_abs_values"], list)
            current["ranks"].append(float(row["rank"]))
            current["mean_abs_values"].append(float(row["mean_abs_shap"]))

    output = []
    for feature, values in aggregate.items():
        ranks = list(values["ranks"])
        mean_abs_values = list(values["mean_abs_values"])
        output.append(
            {
                "feature": feature,
                "top_n_frequency": int(values["count"]),
                "mean_rank": float(np.mean(ranks)),
                "mean_abs_shap_across_models": float(np.mean(mean_abs_values)),
            }
        )
    return sorted(
        output,
        key=lambda row: (
            -int(row["top_n_frequency"]),
            float(row["mean_rank"]),
            -float(row["mean_abs_shap_across_models"]),
            str(row["feature"]),
        ),
    )
