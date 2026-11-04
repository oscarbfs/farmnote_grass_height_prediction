"""Standalone copies of the custom transformers used in the source API."""

from __future__ import annotations

import math
from collections import Counter, defaultdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Sequence

import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.model_selection import GroupKFold, KFold

MISSING_CATEGORY = "__MISSING__"


def _parse_numeric_string(value: Any) -> Optional[float]:
    if value is None:
        return None
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return float(value)
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return None
        try:
            return float(text.replace(",", "."))
        except Exception:
            return None
    return None


def _source_datetime(value: Any) -> datetime:
    """Reproduce the private ``DateModel`` coercion needed by the transformer."""

    if isinstance(value, datetime):
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value

    if isinstance(value, str):
        text = value.strip()
        if any(char.isalpha() for char in text) or "T" in text or "-" in text:
            if text.endswith("Z"):
                text = text[:-1] + "+00:00"
            parsed = datetime.fromisoformat(text)
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=timezone.utc)
            return parsed
        # The source DateModel rejected numeric timestamp strings after parsing
        # them; preserve that executed behaviour rather than broadening inputs.
        raise TypeError("numeric datetime strings are not accepted")

    if isinstance(value, (int, float)) and not isinstance(value, bool):
        timestamp = float(value)
        if timestamp > 1e12:
            timestamp /= 1000.0
        return datetime.fromtimestamp(timestamp, tz=timezone.utc)

    raise TypeError("unsupported datetime value")


class DateTimeFeaturesTransformer(BaseEstimator, TransformerMixin):
    """Expand a timestamp into epoch, month, weekday, yearday, and weekend.

    Scaling statistics, when enabled, are fitted only on the supplied training
    fold.  This is the exact five-column order used in the FarmNote API.
    """

    def __init__(self, col_name: str, scale: bool = False):
        self.col_name = col_name
        self.scale = scale
        self._scaler_mean_: Optional[np.ndarray] = None
        self._scaler_scale_: Optional[np.ndarray] = None

    def fit(self, X, y=None):
        arr = np.asarray(X, dtype=object)
        if arr.ndim == 1:
            arr = arr.reshape(-1, 1)
        output = np.empty((arr.shape[0], 5), dtype=float)
        for index in range(arr.shape[0]):
            value = arr[index, 0] if arr.shape[1] > 0 else None
            output[index, :] = self._row_to_components(value)

        if self.scale:
            mean = np.nanmean(output, axis=0)
            standard_deviation = np.nanstd(output, axis=0)
            self._scaler_mean_ = mean
            self._scaler_scale_ = np.where(standard_deviation == 0, 1.0, standard_deviation)
        return self

    def _row_to_components(self, value: Any):
        timestamp = math.nan
        month = math.nan
        day_of_week = math.nan
        day_of_year = math.nan
        is_weekend = math.nan

        if value is None:
            return timestamp, month, day_of_week, day_of_year, is_weekend

        try:
            date_value = _source_datetime(value)
            timestamp = float(date_value.timestamp())
            utc_value = datetime.fromtimestamp(timestamp, tz=timezone.utc)
        except Exception:
            try:
                if isinstance(value, (int, float)) and not isinstance(value, bool):
                    timestamp = float(value)
                    utc_value = datetime.fromtimestamp(timestamp, tz=timezone.utc)
                elif isinstance(value, str):
                    utc_value = datetime.fromisoformat(value)
                    if utc_value.tzinfo is None:
                        utc_value = utc_value.replace(tzinfo=timezone.utc)
                    utc_value = utc_value.astimezone(timezone.utc)
                    timestamp = float(utc_value.timestamp())
                else:
                    return timestamp, month, day_of_week, day_of_year, is_weekend
            except Exception:
                return timestamp, month, day_of_week, day_of_year, is_weekend

        timestamp = float(timestamp)
        month = float(utc_value.month)
        day_of_week = float(utc_value.weekday())
        day_of_year = float(utc_value.timetuple().tm_yday)
        is_weekend = 1.0 if utc_value.weekday() >= 5 else 0.0
        return timestamp, month, day_of_week, day_of_year, is_weekend

    def transform(self, X):
        arr = np.asarray(X, dtype=object)
        if arr.ndim == 1:
            arr = arr.reshape(-1, 1)
        output = np.empty((arr.shape[0], 5), dtype=float)
        for index in range(arr.shape[0]):
            value = arr[index, 0] if arr.shape[1] > 0 else None
            output[index, :] = self._row_to_components(value)

        if (
            self.scale
            and self._scaler_mean_ is not None
            and self._scaler_scale_ is not None
        ):
            output = (output - self._scaler_mean_) / self._scaler_scale_
        return output

    def get_feature_names_out(self, input_features=None):
        base = self.col_name
        return [
            f"{base}_ts",
            f"{base}_month",
            f"{base}_day_of_week",
            f"{base}_day_of_year",
            f"{base}_is_weekend",
        ]


class FrequencyEncoder(BaseEstimator, TransformerMixin):
    """Frequency encoder retained for parity with the reusable API service."""

    def __init__(self):
        self.maps_: List[Dict[Any, float]] = []
        self.default_value_: float = 0.0
        self.n_features_in_: Optional[int] = None

    def _to_rows(self, X):
        if X is None:
            return []
        arr = np.asarray(X, dtype=object)
        if arr.ndim == 1:
            arr = arr.reshape(-1, 1)
        return arr.tolist()

    def get_feature_names_out(self, input_features=None):
        if input_features is not None:
            return list(input_features)
        if self.n_features_in_ is not None:
            return [f"x{index}" for index in range(self.n_features_in_)]
        return []

    def fit(self, X, y=None):
        rows = self._to_rows(X)
        if not rows:
            self.maps_ = []
            self.n_features_in_ = 0
            return self
        number_of_columns = len(rows[0])
        self.maps_ = []
        for column_index in range(number_of_columns):
            values = []
            for row in rows:
                value = row[column_index] if column_index < len(row) else None
                values.append(MISSING_CATEGORY if value is None else value)
            counts = Counter(values)
            total = sum(counts.values()) if sum(counts.values()) > 0 else 1
            self.maps_.append({key: count / total for key, count in counts.items()})
        self.default_value_ = 0.0
        self.n_features_in_ = number_of_columns
        return self

    def transform(self, X):
        rows = self._to_rows(X)
        if not rows:
            return np.empty((0, 0))
        output = np.zeros((len(rows), len(rows[0])), dtype=float)
        for column_index in range(len(rows[0])):
            mapping = self.maps_[column_index] if column_index < len(self.maps_) else {}
            for row_index, row in enumerate(rows):
                value = row[column_index] if column_index < len(row) else None
                key = value if value is not None else MISSING_CATEGORY
                output[row_index, column_index] = mapping.get(key, self.default_value_)
        return output


class KFoldTargetEncoder(BaseEstimator, TransformerMixin):
    """Smoothed out-of-fold target encoder used for categorical variables.

    The experiment constructs this transformer with ``n_splits=5``,
    ``smoothing=10.0``, and ``random_state=42``.  ``fit_transform`` emits
    out-of-fold values, while ``transform`` uses mappings fitted on all of the
    training data; consequently target statistics never learn from holdout
    rows.
    """

    def __init__(
        self,
        n_splits: int = 5,
        smoothing: float = 10.0,
        random_state: Optional[int] = 42,
    ):
        self.n_splits = n_splits
        self.smoothing = smoothing
        self.random_state = random_state
        self.mapping_per_col_: List[Dict[Any, float]] = []
        self.global_mean_: float = 0.0
        self.fitted_ = False
        self.n_features_in_: Optional[int] = None

    def _to_rows(self, X):
        if X is None:
            return []
        arr = np.asarray(X, dtype=object)
        if arr.ndim == 1:
            arr = arr.reshape(-1, 1)
        return arr.tolist()

    def _to_target_array(self, y):
        if y is None:
            raise ValueError("KFoldTargetEncoder requires y (target) to be provided.")
        if len(y) == 0:
            raise ValueError("y must have at least one element.")

        first_target = y[0]
        if isinstance(first_target, (list, tuple, np.ndarray)):
            target_matrix = np.asarray(
                [
                    [
                        _parse_numeric_string(value)
                        if not isinstance(value, (int, float))
                        else value
                        for value in target_row
                    ]
                    for target_row in y
                ],
                dtype=float,
            )
            return np.nanmean(target_matrix, axis=1)

        return np.asarray(
            [
                _parse_numeric_string(value)
                if not isinstance(value, (int, float))
                else value
                for value in y
            ],
            dtype=float,
        )

    def _calc_smooth(self, mean, count, global_mean):
        return (
            count * mean + self.smoothing * global_mean
        ) / (count + self.smoothing)

    def _make_splits(self, number_of_rows: int, groups: Optional[Sequence[Any]] = None):
        if number_of_rows < 2:
            return []

        use_groups = False
        if groups is not None:
            if len(groups) != number_of_rows:
                raise ValueError(
                    "groups length must match X length for KFoldTargetEncoder"
                )
            if len(set(groups)) > 1:
                use_groups = True

        if use_groups:
            unique_groups = len(set(groups))
            number_of_splits = min(self.n_splits, max(2, unique_groups))
            splitter = GroupKFold(n_splits=number_of_splits)
            return list(splitter.split(np.arange(number_of_rows), groups=groups))

        number_of_splits = min(self.n_splits, max(2, number_of_rows))
        splitter = KFold(
            n_splits=number_of_splits,
            shuffle=True,
            random_state=self.random_state,
        )
        return list(splitter.split(np.arange(number_of_rows)))

    def _fit_full_mapping(self, rows, target_array):
        if not rows:
            return []

        final_mappings: List[Dict[Any, float]] = []
        for column_index in range(len(rows[0])):
            sums: Dict[Any, float] = defaultdict(float)
            counts: Dict[Any, int] = defaultdict(int)
            for row_index, row in enumerate(rows):
                key = (
                    row[column_index]
                    if column_index < len(row) and row[column_index] is not None
                    else MISSING_CATEGORY
                )
                target_value = target_array[row_index]
                if np.isnan(target_value):
                    continue
                sums[key] += float(target_value)
                counts[key] += 1

            column_mapping: Dict[Any, float] = {}
            for key, count in counts.items():
                mean = sums[key] / count if count > 0 else self.global_mean_
                column_mapping[key] = self._calc_smooth(
                    mean,
                    count,
                    self.global_mean_,
                )
            final_mappings.append(column_mapping)
        return final_mappings

    def _build_oof_encoding(
        self,
        rows,
        target_array,
        groups: Optional[Sequence[Any]] = None,
    ):
        if not rows:
            return np.empty((0, 0), dtype=float)

        number_of_rows = len(rows)
        number_of_columns = len(rows[0])
        output = np.full(
            (number_of_rows, number_of_columns),
            self.global_mean_,
            dtype=float,
        )
        splits = self._make_splits(number_of_rows, groups=groups)
        if not splits:
            return output

        for column_index in range(number_of_columns):
            column_values = [
                row[column_index]
                if column_index < len(row) and row[column_index] is not None
                else MISSING_CATEGORY
                for row in rows
            ]
            for train_indices, validation_indices in splits:
                sums: Dict[Any, float] = defaultdict(float)
                counts: Dict[Any, int] = defaultdict(int)
                for train_index in train_indices:
                    key = column_values[train_index]
                    target_value = target_array[train_index]
                    if np.isnan(target_value):
                        continue
                    sums[key] += float(target_value)
                    counts[key] += 1

                smooth_mapping: Dict[Any, float] = {}
                for key, count in counts.items():
                    mean = sums[key] / count if count > 0 else self.global_mean_
                    smooth_mapping[key] = self._calc_smooth(
                        mean,
                        count,
                        self.global_mean_,
                    )
                for validation_index in validation_indices:
                    key = column_values[validation_index]
                    output[validation_index, column_index] = smooth_mapping.get(
                        key,
                        self.global_mean_,
                    )
        return output

    def get_feature_names_out(self, input_features=None):
        if input_features is not None:
            return list(input_features)
        if self.n_features_in_ is not None:
            return [f"x{index}" for index in range(self.n_features_in_)]
        return []

    def fit(self, X, y, groups: Optional[Sequence[Any]] = None):
        rows = self._to_rows(X)
        target_array = self._to_target_array(y)
        if len(rows) == 0:
            self.mapping_per_col_ = []
            self.global_mean_ = 0.0
            self.fitted_ = True
            self.n_features_in_ = 0
            return self

        if np.all(np.isnan(target_array)):
            self.global_mean_ = 0.0
            self.mapping_per_col_ = [{} for _ in range(len(rows[0]))]
            self.fitted_ = True
            self.n_features_in_ = len(rows[0])
            return self

        self.global_mean_ = float(np.nanmean(target_array))
        self.n_features_in_ = len(rows[0])
        self.mapping_per_col_ = self._fit_full_mapping(rows, target_array)
        self.fitted_ = True
        return self

    def fit_transform(
        self,
        X,
        y=None,
        groups: Optional[Sequence[Any]] = None,
        **fit_params,
    ):
        rows = self._to_rows(X)
        target_array = self._to_target_array(y)
        number_of_rows = len(rows)
        if number_of_rows == 0:
            self.mapping_per_col_ = []
            self.global_mean_ = 0.0
            self.fitted_ = True
            self.n_features_in_ = 0
            return np.empty((0, 0), dtype=float)

        if np.all(np.isnan(target_array)):
            self.global_mean_ = 0.0
            self.mapping_per_col_ = [{} for _ in range(len(rows[0]))]
            self.fitted_ = True
            self.n_features_in_ = len(rows[0])
            return np.zeros((number_of_rows, len(rows[0])), dtype=float)

        self.global_mean_ = float(np.nanmean(target_array))
        self.n_features_in_ = len(rows[0])
        out_of_fold = self._build_oof_encoding(
            rows,
            target_array,
            groups=groups,
        )
        self.mapping_per_col_ = self._fit_full_mapping(rows, target_array)
        self.fitted_ = True
        return out_of_fold

    def transform(self, X):
        if not self.fitted_:
            raise RuntimeError("KFoldTargetEncoder must be fitted before transform.")
        rows = self._to_rows(X)
        if not rows:
            return np.empty((0, 0))
        output = np.zeros((len(rows), len(rows[0])), dtype=float)
        for column_index in range(len(rows[0])):
            mapping = (
                self.mapping_per_col_[column_index]
                if column_index < len(self.mapping_per_col_)
                else {}
            )
            for row_index, row in enumerate(rows):
                value = row[column_index] if column_index < len(row) else None
                key = value if value is not None else MISSING_CATEGORY
                output[row_index, column_index] = mapping.get(
                    key,
                    self.global_mean_,
                )
        return output


class BoolToIntTransformer(BaseEstimator, TransformerMixin):
    """Convert source boolean representations to 1/0 and everything else to NaN."""

    def __init__(self):
        self.n_features_in_: Optional[int] = None

    def fit(self, X, y=None):
        arr = np.asarray(X, dtype=object)
        if arr.ndim == 1:
            arr = arr.reshape(-1, 1)
        self.n_features_in_ = arr.shape[1]
        return self

    def transform(self, X):
        arr = np.asarray(X, dtype=object)
        if arr.ndim == 1:
            arr = arr.reshape(-1, 1)
        output = np.empty(arr.shape, dtype=float)
        for row_index in range(arr.shape[0]):
            for column_index in range(arr.shape[1]):
                value = arr[row_index, column_index]
                if value is True:
                    output[row_index, column_index] = 1.0
                elif value is False:
                    output[row_index, column_index] = 0.0
                elif isinstance(value, str) and value.lower() in ("true", "1"):
                    output[row_index, column_index] = 1.0
                elif isinstance(value, str) and value.lower() in ("false", "0"):
                    output[row_index, column_index] = 0.0
                else:
                    output[row_index, column_index] = np.nan
        return output

    def get_feature_names_out(self, input_features=None):
        if input_features is not None:
            return list(input_features)
        if self.n_features_in_ is not None:
            return [f"x{index}" for index in range(self.n_features_in_)]
        return []
