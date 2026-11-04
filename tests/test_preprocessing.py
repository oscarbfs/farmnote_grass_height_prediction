from __future__ import annotations

from pathlib import Path

import numpy as np

from farmnote_grass_height.data.features import (
    EXPERIMENT_WITH_MOVEMENT_OCCUPATION,
    EXPERIMENT_WITHOUT_MOVEMENT_OCCUPATION,
    build_feature_names,
)
from farmnote_grass_height.data.loader import load_analytical_dataset
from farmnote_grass_height.data.schema import TARGET_COLUMN
from farmnote_grass_height.preprocessing import build_preprocessor, records_to_matrix
from farmnote_grass_height.training.split import original_holdout_indices


DATASET = Path(__file__).resolve().parents[1] / "data" / "pasturages_anonymized.csv"


def test_both_preprocessors_fit_only_on_training_rows_and_transform_holdout() -> None:
    frame = load_analytical_dataset(DATASET)
    train_indices, test_indices = original_holdout_indices(len(frame))
    y_train = frame.iloc[train_indices][TARGET_COLUMN].astype(float).tolist()

    for experiment in (
        EXPERIMENT_WITH_MOVEMENT_OCCUPATION,
        EXPERIMENT_WITHOUT_MOVEMENT_OCCUPATION,
    ):
        features = build_feature_names(experiment)
        X_all = records_to_matrix(frame, features)
        X_train = [X_all[index] for index in train_indices]
        X_test = [X_all[index] for index in test_indices]
        preprocessor = build_preprocessor(frame.iloc[train_indices], features)

        transformed_train = np.asarray(preprocessor.fit_transform(X_train, y_train))
        transformed_test = np.asarray(preprocessor.transform(X_test))

        assert transformed_train.shape[0] == 54
        assert transformed_test.shape[0] == 13
        assert transformed_train.shape[1] == transformed_test.shape[1]
        assert transformed_train.shape[1] >= len(features)
        assert np.isfinite(transformed_train).all()
        assert np.isfinite(transformed_test).all()

