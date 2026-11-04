"""Feature selection, leakage control, and the movement ablation.

This module mirrors ``TrainPasturageModelDatasourceImpl._build_feature_names``
from the source API.  Exclusions happen before preprocessing, so neither an
imputer nor an encoder can learn from the target, its end-of-event proxies, or
the columns removed by the ablation experiment.
"""

from __future__ import annotations

from .schema import FEATURE_COLUMNS, TARGET_COLUMN

EXPERIMENT_WITH_MOVEMENT_OCCUPATION = "with_movement_occupation"
EXPERIMENT_WITHOUT_MOVEMENT_OCCUPATION = "without_movement_occupation"
EXPERIMENTS: tuple[str, str] = (
    EXPERIMENT_WITH_MOVEMENT_OCCUPATION,
    EXPERIMENT_WITHOUT_MOVEMENT_OCCUPATION,
)

HERD_MOVEMENT_OCCUPATION_FEATURE_PREFIXES: tuple[str, ...] = (
    "start_bovine_",
    "end_bovine_",
    "delta_bovine_",
    "during_",
    "avg_seconds_from_",
    "avg_time_bovine_",
    "extra_paddocks_",
    "bovines_per_",
    "bovine_weight_per_",
)
HERD_MOVEMENT_OCCUPATION_EXACT_FEATURES: frozenset[str] = frozenset(
    {"duration_seconds"}
)

# Keep source order, including ``pasturage_event_id``.  That identifier was not
# returned by PasturageDTO.feature_names(), so excluding it was a harmless
# no-op; retaining it here makes the executed leakage policy auditable.
LEAKAGE_AND_PROXY_COLUMNS: list[str] = [
    "user_id",
    "pasturage_event_id",
    "end_grass_height_avg_cm",
    "end_grass_height_avg_cm_inferred",
    "snapshot_type",
    "snapshot_progress",
    "snapshot_cutoff_at",
    "end_bovine_count",
    "end_bovine_total_weight_kg",
    "end_bovine_total_weight_kg_inferred",
    "end_bovine_total_weight_kg_inferred_fraction",
    "end_bovine_total_weight_kg_age_hours",
    "delta_bovine_total_weight_kg",
    "delta_bovine_mean_weight_kg",
    "delta_bovine_total_weight_kg_per_day",
    "extra_paddocks_terminal_grass_height_avg_cm",
]


def is_movement_occupation_feature(feature_name: str) -> bool:
    """Return the exact prefix/exact-name decision used by the source API."""

    if feature_name in HERD_MOVEMENT_OCCUPATION_EXACT_FEATURES:
        return True
    return any(
        feature_name.startswith(prefix)
        for prefix in HERD_MOVEMENT_OCCUPATION_FEATURE_PREFIXES
    )


MOVEMENT_OCCUPATION_COLUMNS: list[str] = [
    feature_name
    for feature_name in FEATURE_COLUMNS
    if is_movement_occupation_feature(feature_name)
]


def build_feature_names(
    experiment: str = EXPERIMENT_WITH_MOVEMENT_OCCUPATION,
    *,
    target: str = TARGET_COLUMN,
    targets: tuple[str, ...] | list[str] = (TARGET_COLUMN,),
) -> list[str]:
    """Build the ordered model inputs for one of the two article experiments.

    Parameters match the historical routine even though the published study
    currently has one target.  Unknown experiment names fail early rather than
    silently selecting a scientifically different feature set.
    """

    if experiment not in EXPERIMENTS:
        expected = ", ".join(EXPERIMENTS)
        raise ValueError(f"Unknown experiment {experiment!r}; expected one of: {expected}")

    excluded = set(LEAKAGE_AND_PROXY_COLUMNS)
    excluded.add(target)
    excluded.update(set(targets) - {target})
    if experiment == EXPERIMENT_WITHOUT_MOVEMENT_OCCUPATION:
        excluded.update(MOVEMENT_OCCUPATION_COLUMNS)

    # Filtering instead of set subtraction preserves PasturageDTO.feature_names
    # order exactly.
    return [column for column in FEATURE_COLUMNS if column not in excluded]


def excluded_columns(
    experiment: str = EXPERIMENT_WITH_MOVEMENT_OCCUPATION,
) -> list[str]:
    """Return excluded DTO modelling columns in canonical feature order."""

    selected = set(build_feature_names(experiment))
    return [column for column in FEATURE_COLUMNS if column not in selected]
