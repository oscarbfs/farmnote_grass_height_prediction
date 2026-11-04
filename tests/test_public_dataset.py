from __future__ import annotations

from pathlib import Path

from farmnote_grass_height.data.loader import file_sha256, load_analytical_dataset
from farmnote_grass_height.data.schema import ALL_COLUMNS, TARGET_COLUMN


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
DATASET = REPOSITORY_ROOT / "data" / "pasturages_anonymized.csv"
EXPECTED_SHA256 = "c68e057437c380e8f6ef29e053d33f139f8f95df4448c6563b3d9c89130cfeed"


def test_public_dataset_has_the_audited_shape_and_digest() -> None:
    frame = load_analytical_dataset(DATASET)

    assert frame.shape == (67, 77)
    assert frame.columns.tolist() == ALL_COLUMNS
    assert file_sha256(DATASET) == EXPECTED_SHA256


def test_public_identifiers_are_pseudonymous_and_relations_are_preserved() -> None:
    frame = load_analytical_dataset(DATASET)

    assert frame["id"].str.fullmatch(r"row_\d{2}").all()
    assert frame["user_id"].str.fullmatch(r"source_\d{2}").all()
    assert frame["paddock_id"].str.fullmatch(r"paddock_\d{2}").all()
    assert frame["pasturage_event_id"].str.fullmatch(r"event_\d{2}").all()
    assert frame["id"].nunique() == 67
    assert frame["user_id"].nunique() == 1
    assert frame["paddock_id"].nunique() == 5
    assert frame["pasturage_event_id"].nunique() == 67
    assert frame[TARGET_COLUMN].notna().all()

