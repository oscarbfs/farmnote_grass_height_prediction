"""Load and validate the public analytical dataset."""

from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from .schema import (
    ALL_COLUMNS,
    BOOLEAN_COLUMNS,
    CATEGORICAL_COLUMNS,
    DATETIME_COLUMNS,
    IDENTIFIER_COLUMNS,
    NUMERIC_COLUMNS,
    TARGET_COLUMN,
)


PUBLIC_ID_PATTERNS = {
    "id": re.compile(r"^row_\d+$"),
    "user_id": re.compile(r"^source_\d+$"),
    "paddock_id": re.compile(r"^paddock_\d+$"),
    "pasturage_event_id": re.compile(r"^event_\d+$"),
}


def file_sha256(path: Path) -> str:
    """Return the SHA-256 digest of a file without loading it all in memory."""

    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _parse_bool(value: Any) -> bool | float:
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return np.nan
    if isinstance(value, (bool, np.bool_)):
        return bool(value)
    normalized = str(value).strip().lower()
    if normalized in {"true", "1"}:
        return True
    if normalized in {"false", "0"}:
        return False
    if normalized == "":
        return np.nan
    raise ValueError(f"Invalid boolean token: {value!r}")


def _validate_schema(frame: pd.DataFrame) -> None:
    actual = list(frame.columns)
    expected = list(ALL_COLUMNS)
    if actual != expected:
        missing = sorted(set(expected) - set(actual))
        unexpected = sorted(set(actual) - set(expected))
        raise ValueError(
            "Unexpected analytical dataset schema: "
            f"missing={missing}, unexpected={unexpected}, order_matches=False"
        )


def _coerce_numeric(frame: pd.DataFrame) -> None:
    for column in NUMERIC_COLUMNS:
        original = frame[column]
        converted = pd.to_numeric(original, errors="coerce")
        invalid = original.notna() & converted.isna()
        if bool(invalid.any()):
            raise ValueError(
                f"Column {column!r} contains {int(invalid.sum())} non-numeric value(s)."
            )
        frame[column] = converted


def _validate_datetimes(frame: pd.DataFrame) -> None:
    for column in DATETIME_COLUMNS:
        parsed = pd.to_datetime(frame[column], errors="coerce", utc=True)
        invalid = frame[column].notna() & parsed.isna()
        if bool(invalid.any()):
            raise ValueError(
                f"Column {column!r} contains {int(invalid.sum())} invalid timestamp(s)."
            )


def validate_public_identifiers(frame: pd.DataFrame) -> None:
    """Reject a dataset that still contains operational identifiers."""

    for column, pattern in PUBLIC_ID_PATTERNS.items():
        values = frame[column].astype("string")
        invalid = values.isna() | ~values.str.fullmatch(pattern.pattern, na=False)
        if bool(invalid.any()):
            raise ValueError(
                f"Column {column!r} is not fully pseudonymized; refusing public load."
            )


def load_analytical_dataset(
    path: str | Path,
    *,
    require_public_identifiers: bool = True,
) -> pd.DataFrame:
    """Read the semicolon/comma-decimal CSV and restore the original DTO types.

    Rows are sorted exactly as in the training datasource: finish time, start time,
    and event identifier. Timestamps remain ISO strings so the public temporal
    transformer receives the same kind of values as the original pipeline.
    """

    dataset_path = Path(path)
    frame = pd.read_csv(
        dataset_path,
        sep=";",
        decimal=",",
        dtype={column: "string" for column in IDENTIFIER_COLUMNS + CATEGORICAL_COLUMNS},
        keep_default_na=True,
    )
    _validate_schema(frame)
    _coerce_numeric(frame)

    for column in BOOLEAN_COLUMNS:
        frame[column] = frame[column].map(_parse_bool)

    _validate_datetimes(frame)
    if require_public_identifiers:
        validate_public_identifiers(frame)

    if frame["id"].duplicated().any():
        raise ValueError("Column 'id' must be unique.")
    if frame["pasturage_event_id"].duplicated().any():
        raise ValueError("Column 'pasturage_event_id' must be unique for event rows.")
    if frame[TARGET_COLUMN].isna().any():
        raise ValueError(f"Target {TARGET_COLUMN!r} contains missing values.")

    finish_key = pd.to_datetime(frame["finished_at"], utc=True)
    start_key = pd.to_datetime(frame["started_at"], utc=True)
    frame = (
        frame.assign(_finish_sort=finish_key, _start_sort=start_key)
        .sort_values(
            ["_finish_sort", "_start_sort", "pasturage_event_id"],
            kind="mergesort",
        )
        .drop(columns=["_finish_sort", "_start_sort"])
        .reset_index(drop=True)
    )
    return frame
