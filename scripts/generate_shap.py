"""Generate the global SHAP tables used by the interpretation analysis."""

from __future__ import annotations

import argparse
from pathlib import Path

import joblib
import matplotlib
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from _bootstrap import DEFAULT_DATASET, DEFAULT_RESULTS_ROOT  # noqa: F401

from farmnote_grass_height.data.features import (
    EXPERIMENTS,
    EXPERIMENT_WITH_MOVEMENT_OCCUPATION,
)
from farmnote_grass_height.data.loader import file_sha256, load_analytical_dataset
from farmnote_grass_height.interpretation import (
    compute_shap_importance,
    consolidate_top_features,
)
from farmnote_grass_height.preprocessing import records_to_matrix
from farmnote_grass_height.training.artifacts import read_json, write_json


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_RESULTS_ROOT)
    parser.add_argument(
        "--experiment",
        choices=EXPERIMENTS,
        default=EXPERIMENT_WITH_MOVEMENT_OCCUPATION,
    )
    parser.add_argument("--run-kind", choices=["reproduced", "smoke"], default="reproduced")
    parser.add_argument(
        "--ranking",
        choices=["article", "search_cv"],
        default="article",
        help="Article reproduces the legacy holdout-based top five; search_cv uses real tuning CV.",
    )
    parser.add_argument("--top-models", type=int, default=5)
    parser.add_argument("--models", nargs="+", help="Explicit model names override ranking.")
    parser.add_argument("--sample-size", type=int, default=1000)
    parser.add_argument("--background-size", type=int, default=100)
    parser.add_argument(
        "--max-evals",
        type=int,
        help="Optional SHAP evaluation cap for diagnostics; omit for article behavior.",
    )
    return parser.parse_args()


def _save_plot(rows: list[dict], output: Path, model_label: str) -> None:
    top = rows[:15]
    figure, axis = plt.subplots(figsize=(9, 6))
    axis.barh(
        [str(row["feature"]) for row in reversed(top)],
        [float(row["mean_abs_shap"]) for row in reversed(top)],
    )
    axis.set_xlabel("mean(|SHAP value|)")
    axis.set_title(f"Global feature importance\n{model_label}", fontsize=11)
    figure.tight_layout()
    # Keep source attribution visible on exported images, not only in the README.
    figure.subplots_adjust(bottom=0.15)
    logo_path = Path(__file__).resolve().parents[1] / "assets" / "openweather" / "openweather-logo.png"
    logo_axis = figure.add_axes((0.02, 0.02, 0.13, 0.09))
    logo_axis.imshow(plt.imread(logo_path))
    logo_axis.set_axis_off()
    figure.text(
        0.18, 0.045,
        "Weather data provided by OpenWeather | https://openweathermap.org/\n"
        "Source database: ODbL 1.0 | https://opendatacommons.org/licenses/odbl/1-0/",
        fontsize=7, va="center",
    )
    figure.savefig(output, dpi=180)
    plt.close(figure)


def main() -> int:
    args = _parse_args()
    if args.top_models < 1:
        raise ValueError("--top-models must be positive.")
    run_directory = args.output_root / args.run_kind / args.experiment
    manifest = read_json(run_directory / "manifest.json")
    if file_sha256(args.dataset) != manifest["dataset_sha256"]:
        raise RuntimeError("Dataset SHA-256 differs from the training manifest.")

    metrics = pd.read_csv(run_directory / "metrics.csv")
    if args.models:
        selected_names = list(args.models)
    else:
        ranking_column = "holdout_rmse" if args.ranking == "article" else "search_cv_rmse"
        selected_names = (
            metrics.sort_values(ranking_column, kind="mergesort")
            .head(args.top_models)["model"]
            .astype(str)
            .tolist()
        )

    model_metadata = {model["name"]: model for model in manifest["models"]}
    missing = sorted(set(selected_names) - set(model_metadata))
    if missing:
        raise ValueError(f"Requested model artifact(s) not present: {missing}")

    frame = load_analytical_dataset(args.dataset)
    feature_names = list(manifest["feature_names"])
    X_all = records_to_matrix(frame, feature_names)
    shap_directory = run_directory / "shap"
    shap_directory.mkdir(parents=True, exist_ok=True)

    aggregated_by_model: dict[str, list[dict]] = {}
    metadata_rows = []
    for model_name in selected_names:
        metadata = model_metadata[model_name]
        pipeline = joblib.load(run_directory / metadata["artifact"])
        importance = compute_shap_importance(
            pipeline,
            X_all,
            feature_names,
            sample_size=args.sample_size,
            background_size=args.background_size,
            random_state=0,
            max_evals=args.max_evals,
        )
        pd.DataFrame(importance.aggregated).to_csv(
            shap_directory / f"{model_name}_global.csv",
            index=False,
            encoding="utf-8",
            float_format="%.15g",
        )
        pd.DataFrame(importance.processed).to_csv(
            shap_directory / f"{model_name}_processed.csv",
            index=False,
            encoding="utf-8",
            float_format="%.15g",
        )
        _save_plot(
            importance.aggregated,
            shap_directory / f"{model_name}_global.png",
            metadata["label"],
        )
        aggregated_by_model[model_name] = importance.aggregated
        metadata_rows.append(
            {
                "model": model_name,
                "explainer_type": importance.explainer_type,
                "n_examples": importance.n_examples,
            }
        )

    consolidated = consolidate_top_features(aggregated_by_model, top_n=10)
    pd.DataFrame(consolidated).to_csv(
        shap_directory / "top10_consolidated.csv",
        index=False,
        encoding="utf-8",
        float_format="%.15g",
    )
    write_json(
        shap_directory / "metadata.json",
        {
            "experiment": args.experiment,
            "ranking": args.ranking,
            "selected_models": selected_names,
            "sample_size_requested": args.sample_size,
            "background_size": args.background_size,
            "random_state": 0,
            "max_evals": args.max_evals,
            "models": metadata_rows,
            "privacy_note": "No local explanations or categorical ID mappings are exported.",
        },
    )
    print(f"Models explained: {len(selected_names)}")
    print(f"Output: {shap_directory}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
