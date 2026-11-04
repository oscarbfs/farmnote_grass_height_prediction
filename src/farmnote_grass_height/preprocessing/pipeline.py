"""Construction of the experiment's fold-fitted preprocessing graph."""

from __future__ import annotations

import re
from collections.abc import Iterable, Mapping, Sequence
from typing import Any, Literal

import numpy as np
from sklearn import set_config as sklearn_set_config
from sklearn.compose import ColumnTransformer
from sklearn.impute import MissingIndicator, SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from ..data.schema import (
    BOOLEAN_COLUMNS,
    CATEGORICAL_COLUMNS,
    DATETIME_COLUMNS,
    NUMERIC_COLUMNS,
)
from .transformers import (
    MISSING_CATEGORY,
    BoolToIntTransformer,
    DateTimeFeaturesTransformer,
    FrequencyEncoder,
    KFoldTargetEncoder,
    _parse_numeric_string,
)

# Required for ``groups`` to be routed to the target encoder, exactly as in the
# sklearn service used for the reported experiment.
sklearn_set_config(enable_metadata_routing=True)

CategoricalEncoding = Literal["onehot", "frequency", "target"]


def _is_float_nan(value: Any) -> bool:
    return isinstance(value, (float, np.floating)) and bool(np.isnan(value))


def _normalise_record(record: Mapping[str, Any]) -> dict[str, Any]:
    # CSV readers commonly materialise missing values as NaN, whereas the API's
    # DTO rows used None.  Converting only for schema inspection preserves the
    # same imputer/indicator branch without changing scientific values.
    return {
        key: None if _is_float_nan(value) else value
        for key, value in record.items()
    }


def _records_from(training_frame_or_rows: Any) -> list[dict[str, Any]]:
    if training_frame_or_rows is None:
        raise ValueError("training_frame_or_rows must be provided")

    # pandas.DataFrame without making pandas a direct package dependency here.
    to_dict = getattr(training_frame_or_rows, "to_dict", None)
    if callable(to_dict):
        try:
            records = to_dict(orient="records")
            if isinstance(records, list):
                return [_normalise_record(record) for record in records]
        except TypeError:
            pass

    rows_method = getattr(training_frame_or_rows, "rows", None)
    if callable(rows_method):
        records = list(rows_method())
    elif isinstance(training_frame_or_rows, Mapping):
        records = [training_frame_or_rows]
    elif isinstance(training_frame_or_rows, Iterable):
        records = list(training_frame_or_rows)
    else:
        raise TypeError("expected a DataFrame-like object or an iterable of mappings")

    if not all(isinstance(record, Mapping) for record in records):
        raise TypeError("every training row must be a mapping")
    return [_normalise_record(record) for record in records]


def records_to_matrix(
    frame_or_rows: Any,
    feature_names: Sequence[str],
) -> list[list[Any]]:
    """Build the same ordered X matrix as the private ``DataframeModel``."""

    records = _records_from(frame_or_rows)
    return [
        [
            np.nan if record.get(feature_name) is None else record.get(feature_name)
            for feature_name in feature_names
        ]
        for record in records
    ]


def _has_any_observed_numeric(records: list[dict[str, Any]], column: str) -> bool:
    for record in records:
        if column not in record:
            continue
        value = record.get(column)
        if value is None:
            continue
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            return True
        if isinstance(value, str) and _parse_numeric_string(value) is not None:
            return True
    return False


def _has_missing_numeric(records: list[dict[str, Any]], column: str) -> bool:
    for record in records:
        if column not in record:
            return True
        value = record.get(column)
        if value is None:
            return True
        if isinstance(value, str) and value.strip() == "":
            return True
    return False


def _simple_imputer(*, strategy: str = "median", fill_value=None) -> SimpleImputer:
    try:
        if strategy == "constant":
            return SimpleImputer(
                strategy=strategy,
                fill_value=fill_value,
                keep_empty_features=True,
            )
        return SimpleImputer(strategy=strategy, keep_empty_features=True)
    except TypeError:  # scikit-learn versions before keep_empty_features
        if strategy == "constant":
            return SimpleImputer(strategy=strategy, fill_value=fill_value)
        return SimpleImputer(strategy=strategy)


def _one_hot_encoder(**kwargs):
    try:
        return OneHotEncoder(**{**kwargs, "sparse_output": False})
    except TypeError:  # scikit-learn < 1.2
        return OneHotEncoder(**{**kwargs, "sparse": False})


def _safe_transformer_name(prefix: str, column: str) -> str:
    clean = re.sub(r"[^0-9A-Za-z]+", "_", column)
    clean = re.sub(r"_+", "_", clean).strip("_")
    name = f"{prefix}_{clean}" if clean else prefix
    while "__" in name:
        name = name.replace("__", "_")
    if not re.match(r"^[A-Za-z]", name):
        name = f"{prefix}_{name}"
    return name


def build_preprocessor(
    training_frame_or_rows: Any,
    feature_names: Sequence[str],
    random_state: int | None = 42,
    *,
    add_missing_indicators: bool = True,
    categorical_encoding: CategoricalEncoding = "target",
    scale_datetime: bool = True,
) -> ColumnTransformer:
    """Return the exact column-wise preprocessor used by the experiment.

    ``training_frame_or_rows`` is inspected only to distinguish observed from
    all-missing numeric columns and to decide which missing indicators exist.
    Fit the returned transformer on an X matrix/DataFrame whose columns are in
    precisely ``feature_names`` order.  Median imputers, scalers, categorical
    mappings, and date scaling statistics are then learned inside each training
    fold, preventing preprocessing leakage.
    """

    records = _records_from(training_frame_or_rows)
    raw_feature_names = list(feature_names)
    transformers = []

    numeric_columns = [
        column for column in NUMERIC_COLUMNS if column in raw_feature_names
    ]
    numeric_with_observations = [
        column
        for column in numeric_columns
        if _has_any_observed_numeric(records, column)
    ]
    numeric_all_missing = [
        column
        for column in numeric_columns
        if column not in numeric_with_observations
    ]

    if numeric_with_observations:
        indices = [raw_feature_names.index(column) for column in numeric_with_observations]
        transformers.append(
            (
                "num",
                Pipeline(
                    [
                        ("imputer", _simple_imputer(strategy="median")),
                        ("scaler", StandardScaler()),
                    ]
                ),
                indices,
            )
        )

    if numeric_all_missing:
        indices = [raw_feature_names.index(column) for column in numeric_all_missing]
        transformers.append(
            (
                "num_const",
                Pipeline(
                    [
                        (
                            "imputer",
                            _simple_imputer(strategy="constant", fill_value=0.0),
                        ),
                        ("scaler", StandardScaler()),
                    ]
                ),
                indices,
            )
        )

    if add_missing_indicators and numeric_columns:
        missing_numeric_columns = [
            column
            for column in numeric_columns
            if _has_missing_numeric(records, column)
        ]
        if missing_numeric_columns:
            indices = [
                raw_feature_names.index(column)
                for column in missing_numeric_columns
            ]
            transformers.append(
                (
                    "num_missing_ind",
                    MissingIndicator(features="all"),
                    indices,
                )
            )

    datetime_columns = [
        column for column in DATETIME_COLUMNS if column in raw_feature_names
    ]
    for datetime_column in datetime_columns:
        transformers.append(
            (
                _safe_transformer_name("dt", datetime_column),
                Pipeline(
                    [
                        (
                            "imputer",
                            _simple_imputer(strategy="constant", fill_value=None),
                        ),
                        (
                            "dt",
                            DateTimeFeaturesTransformer(
                                datetime_column,
                                scale=scale_datetime,
                            ),
                        ),
                    ]
                ),
                [raw_feature_names.index(datetime_column)],
            )
        )

    boolean_columns = [
        column for column in BOOLEAN_COLUMNS if column in raw_feature_names
    ]
    if boolean_columns:
        indices = [raw_feature_names.index(column) for column in boolean_columns]
        transformers.append(
            (
                "bool",
                Pipeline(
                    [
                        ("to_int", BoolToIntTransformer()),
                        ("imputer", _simple_imputer(strategy="most_frequent")),
                    ]
                ),
                indices,
            )
        )

    categorical_columns = [
        column for column in CATEGORICAL_COLUMNS if column in raw_feature_names
    ]
    if categorical_columns:
        indices = [raw_feature_names.index(column) for column in categorical_columns]
        if categorical_encoding == "onehot":
            categorical_pipeline = Pipeline(
                [
                    (
                        "imputer",
                        _simple_imputer(
                            strategy="constant",
                            fill_value=MISSING_CATEGORY,
                        ),
                    ),
                    ("ohe", _one_hot_encoder(handle_unknown="ignore")),
                ]
            )
        elif categorical_encoding == "frequency":
            categorical_pipeline = Pipeline(
                [
                    (
                        "imputer",
                        _simple_imputer(
                            strategy="constant",
                            fill_value=MISSING_CATEGORY,
                        ),
                    ),
                    ("freq", FrequencyEncoder()),
                ]
            )
        elif categorical_encoding == "target":
            target_encoder = KFoldTargetEncoder(
                n_splits=5,
                smoothing=10.0,
                random_state=random_state,
            ).set_fit_request(groups=True)
            categorical_pipeline = Pipeline(
                [
                    (
                        "imputer",
                        _simple_imputer(
                            strategy="constant",
                            fill_value=MISSING_CATEGORY,
                        ),
                    ),
                    ("target_enc", target_encoder),
                ]
            )
        else:
            raise ValueError(f"Unknown categorical_encoding: {categorical_encoding}")

        transformers.append(("cat", categorical_pipeline, indices))

    if not transformers:
        return ColumnTransformer([], remainder="passthrough")
    return ColumnTransformer(
        transformers,
        remainder="drop",
        sparse_threshold=0.0,
    )
