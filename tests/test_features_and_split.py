from __future__ import annotations

from farmnote_grass_height.data.features import (
    EXPERIMENT_WITH_MOVEMENT_OCCUPATION,
    EXPERIMENT_WITHOUT_MOVEMENT_OCCUPATION,
    LEAKAGE_AND_PROXY_COLUMNS,
    build_feature_names,
)
from farmnote_grass_height.training.split import original_holdout_indices


EXPECTED_WITHOUT_MOVEMENT = [
    "paddock_id",
    "started_at",
    "finished_at",
    "temp_avg_c_known",
    "temp_max_c_known",
    "temp_min_c_known",
    "humidity_avg_pct_known",
    "precip_total_mm_known",
    "start_grass_height_avg_cm_inferred",
    "size_m2",
    "temp_avg_c",
    "temp_max_c",
    "temp_min_c",
    "humidity_avg_pct",
    "precip_total_mm",
    "start_grass_height_avg_cm",
]


def test_article_feature_sets_and_leakage_exclusions_are_stable() -> None:
    with_movement = build_feature_names(EXPERIMENT_WITH_MOVEMENT_OCCUPATION)
    without_movement = build_feature_names(EXPERIMENT_WITHOUT_MOVEMENT_OCCUPATION)

    assert len(with_movement) == 60
    assert len(without_movement) == 16
    assert without_movement == EXPECTED_WITHOUT_MOVEMENT
    assert set(without_movement) < set(with_movement)
    assert not set(LEAKAGE_AND_PROXY_COLUMNS).intersection(with_movement)


def test_original_holdout_split_is_deterministic_and_has_54_13_rows() -> None:
    first_train, first_test = original_holdout_indices(67)
    second_train, second_test = original_holdout_indices(67)

    assert (first_train, first_test) == (second_train, second_test)
    assert len(first_train) == 54
    assert len(first_test) == 13
    assert set(first_train).isdisjoint(first_test)
    assert sorted(first_train + first_test) == list(range(67))

