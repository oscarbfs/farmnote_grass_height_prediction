"""Canonical schema of the analytical pasturage records.

The constants in this module are a dependency-free transcription of the
``PasturageDTO`` used by the FarmNote API when the reported experiments were
run.  ``ALL_COLUMNS`` follows declaration order in that DTO.  In contrast,
``FEATURE_COLUMNS`` follows the DTO's deliberate modelling order:
categorical, datetime, boolean, then numeric.

Every DTO field is nullable in the operational implementation.  ``python_type``
records the non-null Python type; ``datetime`` replaces the private API's
``DateModel`` with its standard-library base type.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(frozen=True, slots=True)
class PasturageField:
    """One nullable field from the source ``PasturageDTO``."""

    name: str
    python_type: type[Any]
    alias: str
    nullable: bool = True


# Declaration order is scientifically relevant when a complete analytical
# dataset is exported.  Preserve even the surprising plural in the alias of
# ``bovine_weight_per_paddock_time_weighted`` from the source DTO.
PASTURAGE_DTO_FIELDS: tuple[PasturageField, ...] = (
    PasturageField("id", str, "id"),
    PasturageField("user_id", str, "userId"),
    PasturageField("paddock_id", str, "paddockId"),
    PasturageField("pasturage_event_id", str, "pasturageEventId"),
    PasturageField("snapshot_type", str, "snapshotType"),
    PasturageField("snapshot_progress", float, "snapshotProgress"),
    PasturageField("snapshot_cutoff_at", datetime, "snapshotCutoffAt"),
    PasturageField("size_m2", float, "sizeM2"),
    PasturageField("started_at", datetime, "startedAt"),
    PasturageField("finished_at", datetime, "finishedAt"),
    PasturageField("duration_seconds", float, "durationSeconds"),
    PasturageField("temp_avg_c", float, "tempAvgC"),
    PasturageField("temp_max_c", float, "tempMaxC"),
    PasturageField("temp_min_c", float, "tempMinC"),
    PasturageField("humidity_avg_pct", float, "humidityAvgPct"),
    PasturageField("precip_total_mm", float, "precipTotalMm"),
    PasturageField("temp_avg_c_known", bool, "tempAvgCKnown"),
    PasturageField("temp_max_c_known", bool, "tempMaxCKnown"),
    PasturageField("temp_min_c_known", bool, "tempMinCKnown"),
    PasturageField("humidity_avg_pct_known", bool, "humidityAvgPctKnown"),
    PasturageField("precip_total_mm_known", bool, "precipTotalMmKnown"),
    PasturageField("start_grass_height_avg_cm", float, "startGrassHeightAvgCm"),
    PasturageField("end_grass_height_avg_cm", float, "endGrassHeightAvgCm"),
    PasturageField(
        "start_grass_height_avg_cm_inferred",
        bool,
        "startGrassHeightAvgCmInferred",
    ),
    PasturageField(
        "end_grass_height_avg_cm_inferred",
        bool,
        "endGrassHeightAvgCmInferred",
    ),
    PasturageField(
        "start_bovine_total_weight_kg_inferred",
        bool,
        "startBovineTotalWeightKgInferred",
    ),
    PasturageField(
        "end_bovine_total_weight_kg_inferred",
        bool,
        "endBovineTotalWeightKgInferred",
    ),
    PasturageField(
        "start_bovine_total_weight_kg_inferred_fraction",
        float,
        "startBovineTotalWeightKgInferredFraction",
    ),
    PasturageField(
        "end_bovine_total_weight_kg_inferred_fraction",
        float,
        "endBovineTotalWeightKgInferredFraction",
    ),
    PasturageField(
        "start_bovine_total_weight_kg_age_hours",
        float,
        "startBovineTotalWeightKgAgeHours",
    ),
    PasturageField(
        "end_bovine_total_weight_kg_age_hours",
        float,
        "endBovineTotalWeightKgAgeHours",
    ),
    PasturageField("start_bovine_count", int, "startBovineCount"),
    PasturageField("end_bovine_count", int, "endBovineCount"),
    PasturageField(
        "start_bovine_total_weight_kg",
        float,
        "startBovineTotalWeightKg",
    ),
    PasturageField(
        "end_bovine_total_weight_kg",
        float,
        "endBovineTotalWeightKg",
    ),
    PasturageField(
        "delta_bovine_total_weight_kg",
        float,
        "deltaBovineTotalWeightKg",
    ),
    PasturageField(
        "delta_bovine_mean_weight_kg",
        float,
        "deltaBovineMeanWeightKg",
    ),
    PasturageField(
        "delta_bovine_total_weight_kg_per_day",
        float,
        "deltaBovineTotalWeightKgPerDay",
    ),
    PasturageField("during_entry_bovine_count", int, "duringEntryBovineCount"),
    PasturageField("during_exit_bovine_count", int, "duringExitBovineCount"),
    PasturageField(
        "during_entry_total_weight_kg",
        float,
        "duringEntryTotalWeightKg",
    ),
    PasturageField(
        "during_exit_total_weight_kg",
        float,
        "duringExitTotalWeightKg",
    ),
    PasturageField(
        "during_entry_total_weight_kg_inferred",
        bool,
        "duringEntryTotalWeightKgInferred",
    ),
    PasturageField(
        "during_exit_total_weight_kg_inferred",
        bool,
        "duringExitTotalWeightKgInferred",
    ),
    PasturageField(
        "during_entry_total_weight_kg_inferred_fraction",
        float,
        "duringEntryTotalWeightKgInferredFraction",
    ),
    PasturageField(
        "during_exit_total_weight_kg_inferred_fraction",
        float,
        "duringExitTotalWeightKgInferredFraction",
    ),
    PasturageField(
        "during_entry_total_weight_kg_age_hours",
        float,
        "duringEntryTotalWeightKgAgeHours",
    ),
    PasturageField(
        "during_exit_total_weight_kg_age_hours",
        float,
        "duringExitTotalWeightKgAgeHours",
    ),
    PasturageField(
        "avg_seconds_from_start_to_entry",
        float,
        "avgSecondsFromStartToEntry",
    ),
    PasturageField(
        "avg_seconds_from_start_to_exit",
        float,
        "avgSecondsFromStartToExit",
    ),
    PasturageField(
        "avg_seconds_from_end_to_entry",
        float,
        "avgSecondsFromEndToEntry",
    ),
    PasturageField(
        "avg_seconds_from_end_to_exit",
        float,
        "avgSecondsFromEndToExit",
    ),
    PasturageField(
        "avg_time_bovine_in_start_segment_seconds",
        float,
        "avgTimeBovineInStartSegmentSeconds",
    ),
    PasturageField(
        "avg_time_bovine_in_during_entry_segment_seconds",
        float,
        "avgTimeBovineInDuringEntrySegmentSeconds",
    ),
    PasturageField(
        "avg_time_bovine_in_during_exit_segment_seconds",
        float,
        "avgTimeBovineInDuringExitSegmentSeconds",
    ),
    PasturageField(
        "avg_time_bovine_in_end_segment_seconds",
        float,
        "avgTimeBovineInEndSegmentSeconds",
    ),
    PasturageField("extra_paddocks_count", int, "extraPaddocksCount"),
    PasturageField(
        "extra_paddocks_total_size_m2",
        float,
        "extraPaddocksTotalSizeM2",
    ),
    PasturageField(
        "extra_paddocks_initial_grass_height_avg_cm",
        float,
        "extraPaddocksInitialGrassHeightAvgCm",
    ),
    PasturageField(
        "extra_paddocks_terminal_grass_height_avg_cm",
        float,
        "extraPaddocksTerminalGrassHeightAvgCm",
    ),
    PasturageField(
        "extra_paddocks_used_avg_seconds",
        float,
        "extraPaddocksUsedAvgSeconds",
    ),
    PasturageField(
        "bovines_per_paddocks_time_weighted",
        float,
        "bovinesPerPaddocksTimeWeighted",
    ),
    PasturageField(
        "bovines_per_size_time_weighted",
        float,
        "bovinesPerSizeTimeWeighted",
    ),
    PasturageField(
        "bovine_weight_per_paddock_time_weighted",
        float,
        "bovineWeightPerPaddocksTimeWeighted",
    ),
    PasturageField(
        "bovine_weight_per_size_time_weighted",
        float,
        "bovineWeightPerSizeTimeWeighted",
    ),
    PasturageField(
        "during_entry_bovine_count_known",
        bool,
        "duringEntryBovineCountKnown",
    ),
    PasturageField(
        "during_exit_bovine_count_known",
        bool,
        "duringExitBovineCountKnown",
    ),
    PasturageField(
        "during_entry_total_weight_kg_known",
        bool,
        "duringEntryTotalWeightKgKnown",
    ),
    PasturageField(
        "during_exit_total_weight_kg_known",
        bool,
        "duringExitTotalWeightKgKnown",
    ),
    PasturageField(
        "avg_seconds_from_start_to_entry_known",
        bool,
        "avgSecondsFromStartToEntryKnown",
    ),
    PasturageField(
        "avg_seconds_from_start_to_exit_known",
        bool,
        "avgSecondsFromStartToExitKnown",
    ),
    PasturageField(
        "avg_seconds_from_end_to_entry_known",
        bool,
        "avgSecondsFromEndToEntryKnown",
    ),
    PasturageField(
        "avg_seconds_from_end_to_exit_known",
        bool,
        "avgSecondsFromEndToExitKnown",
    ),
    PasturageField(
        "avg_time_bovine_in_start_segment_seconds_known",
        bool,
        "avgTimeBovineInStartSegmentSecondsKnown",
    ),
    PasturageField(
        "avg_time_bovine_in_during_entry_segment_seconds_known",
        bool,
        "avgTimeBovineInDuringEntrySegmentSecondsKnown",
    ),
    PasturageField(
        "avg_time_bovine_in_during_exit_segment_seconds_known",
        bool,
        "avgTimeBovineInDuringExitSegmentSecondsKnown",
    ),
    PasturageField(
        "avg_time_bovine_in_end_segment_seconds_known",
        bool,
        "avgTimeBovineInEndSegmentSecondsKnown",
    ),
)


ALL_COLUMNS: list[str] = [field.name for field in PASTURAGE_DTO_FIELDS]
COLUMN_TYPES: dict[str, type[Any]] = {
    field.name: field.python_type for field in PASTURAGE_DTO_FIELDS
}
COLUMN_ALIASES: dict[str, str] = {
    field.name: field.alias for field in PASTURAGE_DTO_FIELDS
}

IDENTIFIER_COLUMNS: list[str] = [
    "id",
    "user_id",
    "paddock_id",
    "pasturage_event_id",
]

CATEGORICAL_COLUMNS: list[str] = [
    "user_id",
    "paddock_id",
    "snapshot_type",
]

DATETIME_COLUMNS: list[str] = [
    "started_at",
    "finished_at",
    "snapshot_cutoff_at",
]

BOOLEAN_COLUMNS: list[str] = [
    "during_entry_bovine_count_known",
    "during_exit_bovine_count_known",
    "during_entry_total_weight_kg_known",
    "during_exit_total_weight_kg_known",
    "avg_seconds_from_start_to_entry_known",
    "avg_seconds_from_start_to_exit_known",
    "avg_seconds_from_end_to_entry_known",
    "avg_seconds_from_end_to_exit_known",
    "avg_time_bovine_in_start_segment_seconds_known",
    "avg_time_bovine_in_during_entry_segment_seconds_known",
    "avg_time_bovine_in_during_exit_segment_seconds_known",
    "avg_time_bovine_in_end_segment_seconds_known",
    "temp_avg_c_known",
    "temp_max_c_known",
    "temp_min_c_known",
    "humidity_avg_pct_known",
    "precip_total_mm_known",
    "start_grass_height_avg_cm_inferred",
    "end_grass_height_avg_cm_inferred",
    "start_bovine_total_weight_kg_inferred",
    "end_bovine_total_weight_kg_inferred",
    "during_entry_total_weight_kg_inferred",
    "during_exit_total_weight_kg_inferred",
]

NUMERIC_COLUMNS: list[str] = [
    "snapshot_progress",
    "size_m2",
    "duration_seconds",
    "temp_avg_c",
    "temp_max_c",
    "temp_min_c",
    "humidity_avg_pct",
    "precip_total_mm",
    "start_grass_height_avg_cm",
    "end_grass_height_avg_cm",
    "start_bovine_count",
    "end_bovine_count",
    "start_bovine_total_weight_kg",
    "end_bovine_total_weight_kg",
    "delta_bovine_total_weight_kg",
    "delta_bovine_mean_weight_kg",
    "delta_bovine_total_weight_kg_per_day",
    "during_entry_bovine_count",
    "during_exit_bovine_count",
    "during_entry_total_weight_kg",
    "during_exit_total_weight_kg",
    "start_bovine_total_weight_kg_inferred_fraction",
    "end_bovine_total_weight_kg_inferred_fraction",
    "during_entry_total_weight_kg_inferred_fraction",
    "during_exit_total_weight_kg_inferred_fraction",
    "start_bovine_total_weight_kg_age_hours",
    "end_bovine_total_weight_kg_age_hours",
    "during_entry_total_weight_kg_age_hours",
    "during_exit_total_weight_kg_age_hours",
    "avg_seconds_from_start_to_entry",
    "avg_seconds_from_start_to_exit",
    "avg_seconds_from_end_to_entry",
    "avg_seconds_from_end_to_exit",
    "avg_time_bovine_in_start_segment_seconds",
    "avg_time_bovine_in_during_entry_segment_seconds",
    "avg_time_bovine_in_during_exit_segment_seconds",
    "avg_time_bovine_in_end_segment_seconds",
    "extra_paddocks_count",
    "extra_paddocks_total_size_m2",
    "extra_paddocks_initial_grass_height_avg_cm",
    "extra_paddocks_terminal_grass_height_avg_cm",
    "extra_paddocks_used_avg_seconds",
    "bovines_per_paddocks_time_weighted",
    "bovines_per_size_time_weighted",
    "bovine_weight_per_paddock_time_weighted",
    "bovine_weight_per_size_time_weighted",
]

FEATURE_COLUMNS: list[str] = (
    CATEGORICAL_COLUMNS
    + DATETIME_COLUMNS
    + BOOLEAN_COLUMNS
    + NUMERIC_COLUMNS
)
TARGET_COLUMN = "end_grass_height_avg_cm"


class PasturageSchema:
    """Small standalone equivalent of the DTO's column-list methods."""

    @staticmethod
    def categorical_columns() -> list[str]:
        return list(CATEGORICAL_COLUMNS)

    @staticmethod
    def datetime_columns() -> list[str]:
        return list(DATETIME_COLUMNS)

    @staticmethod
    def bool_columns() -> list[str]:
        return list(BOOLEAN_COLUMNS)

    @staticmethod
    def numeric_columns() -> list[str]:
        return list(NUMERIC_COLUMNS)

    @staticmethod
    def feature_names(exclude: list[str] | tuple[str, ...] | None = None) -> list[str]:
        feature_names = list(FEATURE_COLUMNS)
        for column in exclude or []:
            if column in feature_names:
                feature_names.remove(column)
        return feature_names


_field_names = [field.name for field in PASTURAGE_DTO_FIELDS]
if len(_field_names) != len(set(_field_names)):
    raise RuntimeError("The transcribed PasturageDTO schema contains duplicate fields.")
if set(FEATURE_COLUMNS) - set(ALL_COLUMNS):
    raise RuntimeError("A modelling feature is absent from the PasturageDTO schema.")
