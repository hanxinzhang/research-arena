from __future__ import annotations

import csv
import json
from pathlib import Path


BASE = Path(__file__).resolve().parent
REPO = BASE.parents[1]
DATA = REPO / "data" / "OASIS_cross_tbl_df.csv"


def parse_value(value: str):
    if value == "":
        return None
    try:
        return float(value)
    except ValueError:
        return value


def mean(values: list[float]) -> float:
    return sum(values) / len(values)


def cdr_group_summary(rows: list[dict]) -> list[dict]:
    observed = [
        row
        for row in rows
        if isinstance(row["CDR"], float) and isinstance(row["MMSE"], float)
    ]
    summaries = []
    for cdr in sorted({row["CDR"] for row in observed}):
        group = [row for row in observed if row["CDR"] == cdr]
        summaries.append(
            {
                "CDR": cdr,
                "n": len(group),
                "mean_age": round(mean([row["Age"] for row in group]), 3),
                "mean_mmse": round(mean([row["MMSE"] for row in group]), 3),
                "mean_nwbv": round(mean([row["nWBV"] for row in group]), 3),
            }
        )
    return summaries


def threshold_metrics(rows: list[dict], threshold: float = 28.0) -> dict:
    observed = [
        row
        for row in rows
        if isinstance(row["CDR"], float) and isinstance(row["MMSE"], float)
    ]
    tp = fp = tn = fn = 0
    for row in observed:
        predicted = row["MMSE"] < threshold
        actual = row["CDR"] > 0
        if predicted and actual:
            tp += 1
        elif predicted and not actual:
            fp += 1
        elif not predicted and not actual:
            tn += 1
        else:
            fn += 1
    return {
        "true_positive": tp,
        "false_positive": fp,
        "true_negative": tn,
        "false_negative": fn,
        "sensitivity": round(tp / (tp + fn), 3),
        "specificity": round(tn / (tn + fp), 3),
        "accuracy": round((tp + tn) / len(observed), 3),
    }


def main() -> None:
    if not DATA.exists():
        raise SystemExit(
            "Missing data/OASIS_cross_tbl_df.csv. "
            "This repository does not commit raw third-party datasets; "
            "follow data/README.md to download or export the CSV locally."
        )

    with DATA.open(newline="") as f:
        rows = [
            {key: parse_value(value) for key, value in row.items()}
            for row in csv.DictReader(f)
        ]

    observed_count = sum(
        1
        for row in rows
        if isinstance(row["CDR"], float) and isinstance(row["MMSE"], float)
    )
    missingness = {
        col: sum(1 for row in rows if row[col] is None)
        for col in ["Educ", "SES", "MMSE", "CDR"]
    }
    group_summary = cdr_group_summary(rows)
    metrics = threshold_metrics(rows)

    results = {
        "run_id": "oasis_demo_tiny",
        "dataset": "data/OASIS_cross_tbl_df.csv",
        "rows_total": len(rows),
        "rows_with_observed_cdr_mmse": observed_count,
        "missingness": missingness,
        "researcher_1": {
            "question": "Do CDR strata show descriptive gradients in MMSE and nWBV?",
            "primary_metric": "monotone group-level descriptive gradient",
            "accepted": True,
            "cdr_group_summary": group_summary,
        },
        "researcher_2": {
            "question": "Can a simple MMSE threshold separate CDR > 0 from CDR = 0?",
            "primary_metric": "accuracy on observed rows",
            "accepted": False,
            "threshold_rule": "predict CDR > 0 when MMSE < 28",
            "performance": metrics,
            "editorial_reason_not_accepted": (
                "Useful baseline, but less original and vulnerable to "
                "criterion-overlap concerns."
            ),
        },
    }

    with (BASE / "results.json").open("w") as f:
        json.dump(results, f, indent=2)
        f.write("\n")

    table_path = BASE / "tables" / "cdr_group_summary.csv"
    table_path.parent.mkdir(exist_ok=True)
    with table_path.open("w", newline="") as f:
        writer = csv.DictWriter(
            f, fieldnames=["CDR", "n", "mean_age", "mean_mmse", "mean_nwbv"]
        )
        writer.writeheader()
        writer.writerows(group_summary)


if __name__ == "__main__":
    main()
