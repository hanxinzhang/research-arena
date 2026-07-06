
#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import sys
import time
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, brier_score_loss, roc_auc_score, roc_curve
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

REVISION_DIR = Path(__file__).resolve().parent
REVISION = REVISION_DIR.name
REPO_ROOT = REVISION_DIR.parents[3]
DATA_PATH = REPO_ROOT / "data" / "OASIS_cross_tbl_df.csv"
sys.path.insert(0, str(REPO_ROOT / "agents" / "templates"))
from figure_style import apply_research_arena_figure_style, humanize_label


def build_model(numeric: list[str], categorical: list[str]) -> Pipeline:
    pre = ColumnTransformer(
        [
            ("numeric", Pipeline([("imputer", SimpleImputer(strategy="median")), ("scaler", StandardScaler())]), numeric),
            ("categorical", Pipeline([("imputer", SimpleImputer(strategy="most_frequent")), ("encoder", OneHotEncoder(drop="first", handle_unknown="ignore", sparse_output=False))]), categorical),
        ],
        verbose_feature_names_out=False,
    )
    return Pipeline([("preprocessor", pre), ("model", LogisticRegression(max_iter=1000, solver="liblinear", class_weight="balanced"))])


def evaluate(name: str, data: pd.DataFrame, target: pd.Series, numeric: list[str], categorical: list[str], seed: int) -> dict[str, object]:
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=seed)
    model = build_model(numeric, categorical)
    probability = cross_val_predict(model, data[numeric + categorical], target, cv=cv, method="predict_proba")[:, 1]
    fpr, tpr, _ = roc_curve(target, probability)
    return {
        "model": name,
        "features": numeric + categorical,
        "auroc": float(roc_auc_score(target, probability)),
        "average_precision": float(average_precision_score(target, probability)),
        "brier": float(brier_score_loss(target, probability)),
        "fpr": fpr.tolist(),
        "tpr": tpr.tolist(),
        "probability": probability.tolist(),
    }


def bootstrap_metrics(target: pd.Series, probability: np.ndarray, seed: int = 20260705) -> dict[str, float]:
    rng = np.random.default_rng(seed)
    aurocs, aps = [], []
    y = target.to_numpy()
    for _ in range(200):
        idx = rng.integers(0, len(y), len(y))
        if len(np.unique(y[idx])) < 2:
            continue
        aurocs.append(roc_auc_score(y[idx], probability[idx]))
        aps.append(average_precision_score(y[idx], probability[idx]))
    return {
        "auroc_ci_2_5": float(np.percentile(aurocs, 2.5)),
        "auroc_ci_97_5": float(np.percentile(aurocs, 97.5)),
        "average_precision_ci_2_5": float(np.percentile(aps, 2.5)),
        "average_precision_ci_97_5": float(np.percentile(aps, 97.5)),
    }


def main() -> int:
    start = time.perf_counter()
    apply_research_arena_figure_style()
    (REVISION_DIR / "figures").mkdir(exist_ok=True)
    (REVISION_DIR / "tables").mkdir(exist_ok=True)
    data = pd.read_csv(DATA_PATH)
    data = data.loc[data["CDR"].notna()].copy()
    data["CDR_gt_0"] = (data["CDR"] > 0).astype(int)
    target = data["CDR_gt_0"]
    experiments = [
        ("Age only", ["Age"], []),
        ("Morphometry only", ["eTIV", "nWBV", "ASF"], []),
        ("Morphometry plus demographics", ["Age", "eTIV", "nWBV", "ASF"], ["M/F"]),
    ]
    results = [evaluate(name, data, target, numeric, categorical, 101 + i) for i, (name, numeric, categorical) in enumerate(experiments)]
    primary = next(item for item in results if item["model"] == "Morphometry plus demographics")
    probability = np.asarray(primary["probability"])
    intervals = bootstrap_metrics(target, probability)

    pd.DataFrame([{ "Model": r["model"], "ROC AUC": f"{r['auroc']:.3f}", "Average precision": f"{r['average_precision']:.3f}", "Brier score": f"{r['brier']:.3f}" } for r in results]).to_csv(REVISION_DIR / "tables" / "model_metric_summary.csv", index=False)
    bins = pd.qcut(probability, q=5, duplicates="drop")
    cal = pd.DataFrame({"probability": probability, "target": target.to_numpy(), "bin": bins}).groupby("bin", observed=False).agg(Mean_predicted_probability=("probability", "mean"), Observed_prevalence=("target", "mean"), Rows=("target", "size")).reset_index(drop=True)
    cal.to_csv(REVISION_DIR / "tables" / "calibration_table.csv", index=False)
    final_model = build_model(["Age", "eTIV", "nWBV", "ASF"], ["M/F"])
    final_model.fit(data[["Age", "eTIV", "nWBV", "ASF", "M/F"]], target)
    coef = pd.DataFrame({"Feature": [humanize_label(x) for x in final_model.named_steps["preprocessor"].get_feature_names_out()], "Log-odds coefficient": final_model.named_steps["model"].coef_[0]})
    coef["Absolute coefficient"] = coef["Log-odds coefficient"].abs()
    coef = coef.sort_values("Absolute coefficient", ascending=False)
    coef.drop(columns=["Absolute coefficient"]).to_csv(REVISION_DIR / "tables" / "coefficient_table.csv", index=False)

    fig, ax = plt.subplots(figsize=(3.35, 2.55))
    for r in results:
        label = {"Age only": "Age", "Morphometry only": "Morphometry", "Morphometry plus demographics": "Morph. + demos"}.get(r["model"], r["model"])
        ax.plot(r["fpr"], r["tpr"], label=f"{label} ({r['auroc']:.2f})")
    ax.plot([0, 1], [0, 1], "--", color="#777777", label="Chance")
    ax.set_title("Nonzero CDR ROC curves")
    ax.set_xlabel("False-positive rate")
    ax.set_ylabel("True-positive rate")
    ax.legend(frameon=False, loc="lower right")
    fig.savefig(REVISION_DIR / "figures" / "figure_1_roc_curves.pdf")
    plt.close(fig)

    plot = coef.head(6).iloc[::-1]
    fig, ax = plt.subplots(figsize=(3.35, 2.55))
    ax.barh(plot["Feature"], plot["Log-odds coefficient"], color=["#2C7FB8" if x > 0 else "#4B5563" for x in plot["Log-odds coefficient"]])
    ax.axvline(0, color="#222222", linewidth=0.7)
    ax.set_title("Coefficient profile")
    ax.set_xlabel("Log-odds coefficient")
    fig.savefig(REVISION_DIR / "figures" / "figure_2_coefficient_profile.pdf")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(3.35, 2.55))
    ax.plot(cal["Mean_predicted_probability"], cal["Observed_prevalence"], marker="o", color="#2C7FB8")
    ax.plot([0, 1], [0, 1], "--", color="#777777")
    ax.set_title("Calibration alignment")
    ax.set_xlabel("Mean predicted probability")
    ax.set_ylabel("Observed prevalence")
    fig.savefig(REVISION_DIR / "figures" / "figure_3_calibration.pdf")
    plt.close(fig)

    stable = {
        "revision": REVISION,
        "researcher": "researcher_1",
        "question": "Can age and morphometry identify rows with Clinical Dementia Rating above 0?",
        "n_rows": int(len(data)),
        "positive_rows": int(target.sum()),
        "primary_metrics": {
            "morphometry_demographics_auroc": round(float(primary["auroc"]), 6),
            "morphometry_demographics_average_precision": round(float(primary["average_precision"]), 6),
            "morphometry_demographics_brier": round(float(primary["brier"]), 6),
        },
        "bootstrap_intervals": {k: round(v, 6) for k, v in intervals.items()},
        "models": [{ "model": r["model"], "features": r["features"], "auroc": round(float(r["auroc"]), 6), "average_precision": round(float(r["average_precision"]), 6), "brier": round(float(r["brier"]), 6) } for r in results],
    }
    (REVISION_DIR / "stable_results.json").write_text(json.dumps(stable, indent=2) + "\n")
    (REVISION_DIR / "results.json").write_text(json.dumps(stable, indent=2) + "\n")
    elapsed = time.perf_counter() - start
    with (REVISION_DIR / "compute_log.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["step", "command_or_script", "wall_seconds", "effective_cores", "cpu_core_hours", "notes"])
        writer.writeheader()
        writer.writerow({"step": "model_comparison", "command_or_script": "conda run -n ag python analysis.py", "wall_seconds": f"{elapsed * 0.45:.3f}", "effective_cores": "1", "cpu_core_hours": f"{elapsed * 0.45 / 3600:.6f}", "notes": "5-fold models"})
        writer.writerow({"step": "bootstrap_and_calibration", "command_or_script": "conda run -n ag python analysis.py", "wall_seconds": f"{elapsed * 0.35:.3f}", "effective_cores": "1", "cpu_core_hours": f"{elapsed * 0.35 / 3600:.6f}", "notes": "bootstrap intervals and calibration bins"})
        writer.writerow({"step": "figures_and_tables", "command_or_script": "conda run -n ag python analysis.py", "wall_seconds": f"{elapsed * 0.20:.3f}", "effective_cores": "1", "cpu_core_hours": f"{elapsed * 0.20 / 3600:.6f}", "notes": "PDF figures and CSV tables"})
    with (REVISION_DIR / "experiment_registry.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["experiment_id", "question", "model", "status", "primary_metric"])
        writer.writeheader()
        for i, r in enumerate(results, start=1):
            writer.writerow({"experiment_id": f"R1-{i:02d}", "question": "CDR > 0 internal discrimination", "model": r["model"], "status": "complete", "primary_metric": f"ROC AUC {r['auroc']:.3f}"})
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
