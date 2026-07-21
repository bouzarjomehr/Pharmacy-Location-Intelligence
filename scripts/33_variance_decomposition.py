"""
33_variance_decomposition.py

Variance decomposition of the final score.

Purpose
-------
Estimate the independent explanatory contribution of each component
to the final score using linear regression.

Outputs
-------
outputs/
    validation/
        33_variance_decomposition.xlsx
        33_standardized_coefficients.png
"""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT))

import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt

from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler

import config.app_config as app_config


ROOT = Path(__file__).resolve().parents[1]

INPUT_FILE = (
    ROOT
    / "data"
    / "processed"
    / "best_areas.geojson"
)

OUTPUT_DIR = (
    ROOT
    / "outputs"
    / "validation"
)


def standardized_regression(X, y):
    """
    Standardized linear regression.

    Returns
    -------
    beta : standardized coefficients
    r2   : model R²
    """

    scaler_x = StandardScaler()
    scaler_y = StandardScaler()

    Xs = scaler_x.fit_transform(X)
    ys = scaler_y.fit_transform(
        y.to_numpy().reshape(-1, 1)
    ).ravel()

    model = LinearRegression()
    model.fit(Xs, ys)

    beta = pd.Series(
        model.coef_,
        index=X.columns,
    )

    return beta, model.score(Xs, ys)


def incremental_r2(X, y):
    """
    Calculate incremental R² for each variable by
    adding variables one-by-one.

    Returns
    -------
    DataFrame
    """

    results = []

    previous_r2 = 0

    for column in X.columns:

        subset = X[
            X.columns[
                : X.columns.get_loc(column) + 1
            ]
        ]

        model = LinearRegression()
        model.fit(subset, y)

        r2 = model.score(subset, y)

        results.append(
            {
                "Variable": column,
                "Model_R2": r2,
                "Incremental_R2": r2 - previous_r2,
            }
        )

        previous_r2 = r2

    return pd.DataFrame(results)

def main():

    print("=" * 70)
    print("Variance Decomposition Analysis")
    print("=" * 70)

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    df = (
        gpd.read_file(INPUT_FILE)
        .to_crs(app_config.TARGET_CRS)
    )

    features = [

        "prescription_component",
        "competition_component",
        "population_component",
        "road_component",

    ]

    X = df[features].copy()

    y = df["final_score"].copy()

    # --------------------------------------------------
    # Standardized regression
    # --------------------------------------------------

    beta, full_r2 = standardized_regression(
        X,
        y,
    )

    print()
    print(f"Full model R² = {full_r2:.4f}")

    # --------------------------------------------------
    # Marginal R²
    # --------------------------------------------------

    marginal = []

    for col in features:

        model = LinearRegression()

        model.fit(
            X[[col]],
            y,
        )

        r2 = model.score(
            X[[col]],
            y,
        )

        marginal.append(
            {
                "Variable": col,
                "Marginal_R2": r2,
            }
        )

    marginal = pd.DataFrame(marginal)

    # --------------------------------------------------
    # Drop-one analysis
    # --------------------------------------------------

    drop_results = []

    full_model = LinearRegression()

    full_model.fit(
        X,
        y,
    )

    full_r2 = full_model.score(
        X,
        y,
    )

    for col in features:

        subset = X.drop(
            columns=[col]
        )

        model = LinearRegression()

        model.fit(
            subset,
            y,
        )

        r2 = model.score(
            subset,
            y,
        )

        drop_results.append(
            {
                "Variable": col,
                "DropOne_R2": r2,
                "Delta_R2": full_r2 - r2,
            }
        )

    drop_results = pd.DataFrame(drop_results)

    # --------------------------------------------------
    # Incremental R²
    # --------------------------------------------------

    incremental = incremental_r2(
        X,
        y,
    )

    # --------------------------------------------------
    # Merge everything
    # --------------------------------------------------

    summary = (
        marginal
        .merge(
            drop_results,
            on="Variable",
        )
    )

    summary["Standardized_Beta"] = (
        beta.values
    )

    summary = summary[
        [
            "Variable",
            "Marginal_R2",
            "Delta_R2",
            "Standardized_Beta",
        ]
    ]

    outfile = (
        OUTPUT_DIR
        / "33_variance_decomposition.xlsx"
    )

    summary.to_excel(
        outfile,
        index=False,
    )

    print()
    print(summary)

    print()
    print("Saved:")
    print(outfile)

    # --------------------------------------------------
    # Figure 1
    # Standardized Beta
    # --------------------------------------------------

    plt.figure(figsize=(8, 4))

    plt.bar(
        summary["Variable"],
        summary["Standardized_Beta"],
    )

    plt.ylabel("Standardized Beta")

    plt.xticks(
        rotation=30,
        ha="right",
    )

    plt.tight_layout()

    fig1 = (
        OUTPUT_DIR
        / "33_standardized_coefficients.png"
    )

    plt.savefig(
        fig1,
        dpi=300,
    )

    plt.close()

    # --------------------------------------------------
    # Figure 2
    # Delta R²
    # --------------------------------------------------

    plt.figure(figsize=(8, 4))

    plt.bar(
        summary["Variable"],
        summary["Delta_R2"],
    )

    plt.ylabel("ΔR²")

    plt.xticks(
        rotation=30,
        ha="right",
    )

    plt.tight_layout()

    fig2 = (
        OUTPUT_DIR
        / "33_delta_r2.png"
    )

    plt.savefig(
        fig2,
        dpi=300,
    )

    plt.close()

    # --------------------------------------------------
    # Regression summary
    # --------------------------------------------------

    report = (
        OUTPUT_DIR
        / "33_regression_summary.txt"
    )

    with open(
        report,
        "w",
        encoding="utf-8",
    ) as f:

        f.write(
            "Variance Decomposition Analysis\n"
        )

        f.write("=" * 60 + "\n\n")

        f.write(
            f"Full model R² = {full_r2:.4f}\n\n"
        )

        f.write(
            summary.to_string(index=False)
        )

    print(fig1)
    print(fig2)
    print(report)

    print()
    print("=" * 70)
    print("Finished")
    print("=" * 70)


if __name__ == "__main__":
    main()    