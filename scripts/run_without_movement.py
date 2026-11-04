"""Repeat training after removing herd movement and occupation attributes."""

from __future__ import annotations

import argparse
from pathlib import Path

from _bootstrap import DEFAULT_DATASET, DEFAULT_RESULTS_ROOT  # noqa: F401

from farmnote_grass_height.data.features import (
    EXPERIMENT_WITHOUT_MOVEMENT_OCCUPATION,
)
from farmnote_grass_height.models import MODEL_NAMES
from farmnote_grass_height.training import run_experiment


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_RESULTS_ROOT)
    parser.add_argument("--models", nargs="+", choices=MODEL_NAMES)
    parser.add_argument(
        "--smoke",
        action="store_true",
        help="Use one value per grid solely to validate execution; not a reproduction.",
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    run = run_experiment(
        args.dataset,
        args.output_root,
        experiment=EXPERIMENT_WITHOUT_MOVEMENT_OCCUPATION,
        model_names=args.models,
        smoke=args.smoke,
    )
    print(f"Experiment: {run.experiment}")
    print(f"Artifacts: {run.output_directory}")
    print(f"Models completed: {len(run.metrics)}")
    if args.smoke:
        print("Mode: smoke validation (results are not article-comparable)")
    else:
        print("Mode: full article-compatible grids")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
