from __future__ import annotations

from farmnote_grass_height.models import (
    MODEL_NAMES,
    get_model_definitions,
    make_pipeline_param_grid,
)


def test_all_fifteen_model_families_are_registered_in_source_order() -> None:
    definitions = get_model_definitions()

    assert len(definitions) == 15
    assert tuple(definition.name for definition in definitions) == MODEL_NAMES
    assert all(definition.param_grid for definition in definitions)


def test_effective_seed_omissions_and_applied_seeds_are_preserved() -> None:
    definitions = {definition.name: definition for definition in get_model_definitions()}

    assert definitions["random_forest_regressor"].estimator.random_state == 42
    assert definitions["lgbm_regressor"].estimator.random_state == 42
    assert definitions["bagging_regressor"].estimator.random_state == 42
    assert definitions["decision_tree_regressor"].estimator.random_state is None
    assert definitions["extra_trees_regressor"].estimator.random_state is None
    assert definitions["gradient_boosting_regressor"].estimator.random_state is None
    assert definitions["hist_gradient_boosting_regressor"].estimator.random_state is None
    assert definitions["mlp_regressor"].estimator.random_state is None


def test_effective_grids_preserve_lightgbm_and_bagging_adaptations() -> None:
    lightgbm_grid = make_pipeline_param_grid("lgbm_regressor")
    bagging_grid = make_pipeline_param_grid("bagging_regressor")

    assert "est__early_stopping_rounds" not in lightgbm_grid
    assert "est__estimator__max_depth" in bagging_grid
    assert "est__estimator__min_samples_split" in bagging_grid
    assert "est__base_estimator_max_depth" not in bagging_grid

