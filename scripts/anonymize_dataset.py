"""Create the publishable analytical dataset without retaining an ID mapping.

Only the four operational identifier columns are changed. All scientific values,
timestamps, missing values, column order, and row order are copied as text.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import re
import sys
import tempfile
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPOSITORY_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from farmnote_grass_height.data.schema import ALL_COLUMNS  # noqa: E402


IDENTIFIER_PREFIXES = {
    "id": "row",
    "user_id": "source",
    "paddock_id": "paddock",
    "pasturage_event_id": "event",
}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _mapping(values: set[str], prefix: str) -> dict[str, str]:
    ordered = sorted(value for value in values if value)
    width = max(2, len(str(len(ordered))))
    return {
        original: f"{prefix}_{index:0{width}d}"
        for index, original in enumerate(ordered, start=1)
    }


def anonymize(source: Path, output: Path, *, force: bool = False) -> dict[str, int]:
    """Pseudonymize the analytical CSV and return per-column cardinalities."""

    source = source.resolve()
    output = output.resolve()
    if source == output:
        raise ValueError("Source and output must be different files.")
    if output.exists() and not force:
        raise FileExistsError(f"Output already exists: {output}")

    with source.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream, delimiter=";")
        fieldnames = list(reader.fieldnames or [])
        if fieldnames != list(ALL_COLUMNS):
            missing = sorted(set(ALL_COLUMNS) - set(fieldnames))
            unexpected = sorted(set(fieldnames) - set(ALL_COLUMNS))
            raise ValueError(
                "Unexpected analytical dataset schema. "
                f"missing={missing}, unexpected={unexpected}, order_matches=False"
            )
        rows = list(reader)

    if not rows:
        raise ValueError("The source dataset has no rows.")

    mappings: dict[str, dict[str, str]] = {}
    for column, prefix in IDENTIFIER_PREFIXES.items():
        values = {str(row.get(column) or "").strip() for row in rows}
        if "" in values:
            raise ValueError(f"Identifier column {column!r} contains an empty value.")
        mappings[column] = _mapping(values, prefix)

    for row in rows:
        for column, mapping in mappings.items():
            original = str(row[column]).strip()
            row[column] = mapping[original]

    for column, prefix in IDENTIFIER_PREFIXES.items():
        expected = re.compile(rf"^{re.escape(prefix)}_\d+$")
        if any(not expected.fullmatch(str(row[column])) for row in rows):
            raise RuntimeError(f"Pseudonym validation failed for {column!r}.")

    output.parent.mkdir(parents=True, exist_ok=True)
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            "w",
            encoding="utf-8",
            newline="",
            dir=output.parent,
            prefix=f".{output.name}.",
            suffix=".tmp",
            delete=False,
        ) as stream:
            temporary_path = Path(stream.name)
            writer = csv.DictWriter(
                stream,
                fieldnames=fieldnames,
                delimiter=";",
                lineterminator="\n",
                extrasaction="raise",
            )
            writer.writeheader()
            writer.writerows(rows)
        temporary_path.replace(output)
    finally:
        if temporary_path is not None and temporary_path.exists():
            temporary_path.unlink()

    return {column: len(mapping) for column, mapping in mappings.items()}


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Pseudonymize the four operational IDs in a FarmNote analytical CSV. "
            "No reversible mapping is written."
        )
    )
    parser.add_argument("source", type=Path, help="Private analytical CSV to read.")
    parser.add_argument(
        "--output",
        type=Path,
        default=REPOSITORY_ROOT / "data" / "pasturages_anonymized.csv",
        help="Destination CSV (default: data/pasturages_anonymized.csv).",
    )
    parser.add_argument("--force", action="store_true", help="Replace an existing output file.")
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    counts = anonymize(args.source, args.output, force=args.force)
    print(f"Wrote {args.output.resolve()}")
    print(f"Source SHA-256: {_sha256(args.source.resolve())}")
    print(f"Public SHA-256: {_sha256(args.output.resolve())}")
    print("Pseudonymized cardinalities: " + ", ".join(f"{k}={v}" for k, v in counts.items()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
