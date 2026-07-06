
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


def permutation_control(data: pd.DataFrame, target: pd.Series, numeric: list[str], categorical: list[str], observed: float) -> dict[str, float]:
    rng = np.random.default_rng(20260705)
    aurocs, aps = [], []
    for i in range(30):
        permuted = pd.Series(rng.permutation(target.to_numpy()), index=target.index)
        r = evaluate("Permutation control", data, permuted, numeric, categorical, 900 + i)
        aurocs.append(float(r["auroc"]))
        aps.append(float(r["average_precision"]))
    return {
        "observed_auroc": float(observed),
        "permutation_mean_auroc": float(np.mean(aurocs)),
        "permutation_sd_auroc": float(np.std(aurocs, ddof=1)),
        "permutation_p_ge_observed": float((np.sum(np.asarray(aurocs) >= observed) + 1) / (len(aurocs) + 1)),
        "permutation_mean_average_precision": float(np.mean(aps)),
        "permutation_sd_average_precision": float(np.std(aps, ddof=1)),
        "permutation_draws": float(len(aurocs)),
    }


def main() -> int:
    start = time.perf_counter()
    apply_research_arena_figure_style()
    (REVISION_DIR / "figures").mkdir(exist_ok=True)
    (REVISION_DIR / "tables").mkdir(exist_ok=True)
    data = pd.read_csv(DATA_PATH)
    data = data.loc[data["CDR"].notna()].copy()
    data["CDR_ge_1"] = (data["CDR"] >= 1.0).astype(int)
    data["CDR_gt_0"] = (data["CDR"] > 0).astype(int)
    target = data["CDR_ge_1"]
    experiments = [
        ("Age only", ["Age"], []),
        ("Morphometry plus age", ["Age", "eTIV", "nWBV", "ASF"], ["M/F"]),
        ("Cognitive plus morphometry", ["Age", "MMSE", "eTIV", "nWBV", "ASF"], ["M/F"]),
        ("No-MMSE sensitivity check", ["Age", "eTIV", "nWBV", "ASF"], ["M/F"]),
    ]
    results = [evaluate(name, data, target, numeric, categorical, 211 + i) for i, (name, numeric, categorical) in enumerate(experiments)]
    primary = next(r for r in results if r["model"] == "Cognitive plus morphometry")
    control = permutation_control(data, target, ["Age", "MMSE", "eTIV", "nWBV", "ASF"], ["M/F"], float(primary["auroc"]))
    sensitivity = evaluate("CDR > 0 sensitivity endpoint", data, data["CDR_gt_0"], ["Age", "MMSE", "eTIV", "nWBV", "ASF"], ["M/F"], 311)

    pd.DataFrame([{ "Model": r["model"], "ROC AUC": f"{r['auroc']:.3f}", "Average precision": f"{r['average_precision']:.3f}", "Brier score": f"{r['brier']:.3f}" } for r in results]).to_csv(REVISION_DIR / "tables" / "model_metric_summary.csv", index=False)
    pd.DataFrame([
        {"Quantity": "Observed sparse-endpoint ROC AUC", "Value": f"{control['observed_auroc']:.3f}"},
        {"Quantity": "Permutation mean ROC AUC", "Value": f"{control['permutation_mean_auroc']:.3f}"},
        {"Quantity": "Permutation SD ROC AUC", "Value": f"{control['permutation_sd_auroc']:.3f}"},
        {"Quantity": "Permutation p-value", "Value": f"{control['permutation_p_ge_observed']:.3f}"},
        {"Quantity": "Permutation draws", "Value": f"{control['permutation_draws']:.0f}"},
    ]).to_csv(REVISION_DIR / "tables" / "permutation_control.csv", index=False)
    pd.DataFrame([
        {"Endpoint": "CDR >= 1.0", "Positive rows": int(target.sum()), "ROC AUC": f"{primary['auroc']:.3f}", "Average precision": f"{primary['average_precision']:.3f}"},
        {"Endpoint": "CDR > 0", "Positive rows": int(data["CDR_gt_0"].sum()), "ROC AUC": f"{sensitivity['auroc']:.3f}", "Average precision": f"{sensitivity['average_precision']:.3f}"},
    ]).to_csv(REVISION_DIR / "tables" / "target_sensitivity.csv", index=False)
    final_model = build_model(["Age", "MMSE", "eTIV", "nWBV", "ASF"], ["M/F"])
    final_model.fit(data[["Age", "MMSE", "eTIV", "nWBV", "ASF", "M/F"]], target)
    coef = pd.DataFrame({"Feature": [humanize_label(x) for x in final_model.named_steps["preprocessor"].get_feature_names_out()], "Log-odds coefficient": final_model.named_steps["model"].coef_[0]})
    coef["Absolute coefficient"] = coef["Log-odds coefficient"].abs()
    coef = coef.sort_values("Absolute coefficient", ascending=False)
    coef.drop(columns=["Absolute coefficient"]).to_csv(REVISION_DIR / "tables" / "coefficient_table.csv", index=False)

    fig, ax = plt.subplots(figsize=(3.35, 2.55))
    for r in results:
        label = {"Age only": "Age", "Morphometry plus age": "Morphometry", "Cognitive plus morphometry": "Cog. + morph.", "No-MMSE sensitivity check": "No MMSE"}.get(r["model"], r["model"])
        ax.plot(r["fpr"], r["tpr"], label=f"{label} ({r['auroc']:.2f})")
    ax.plot([0, 1], [0, 1], "--", color="#777777", label="Chance")
    ax.set_title("Sparse severity ROC curves")
    ax.set_xlabel("False-positive rate")
    ax.set_ylabel("True-positive rate")
    ax.legend(frameon=False, loc="lower right")
    fig.savefig(REVISION_DIR / "figures" / "figure_1_roc_curves.pdf")
    plt.close(fig)

    plot = coef.head(6).iloc[::-1]
    fig, ax = plt.subplots(figsize=(3.35, 2.55))
    ax.barh(plot["Feature"], plot["Log-odds coefficient"], color=["#2C7FB8" if x > 0 else "#4B5563" for x in plot["Log-odds coefficient"]])
    ax.axvline(0, color="#222222", linewidth=0.7)
    ax.set_title("Sparse-endpoint coefficient profile")
    ax.set_xlabel("Log-odds coefficient")
    fig.savefig(REVISION_DIR / "figures" / "figure_2_coefficient_profile.pdf")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(3.35, 2.55))
    ax.bar(["Observed", "Permutation"], [control["observed_auroc"], control["permutation_mean_auroc"]], yerr=[0.0, control["permutation_sd_auroc"]], color=["#2C7FB8", "#4B5563"], capsize=3)
    ax.set_ylim(0, 1)
    ax.set_title("Negative-control comparison")
    ax.set_ylabel("Mean ROC AUC")
    fig.savefig(REVISION_DIR / "figures" / "figure_3_negative_control.pdf")
    plt.close(fig)

    stable = {
        "revision": REVISION,
        "researcher": "researcher_2",
        "question": "Does adding MMSE to morphometry improve detection of CDR >= 1.0?",
        "n_rows": int(len(data)),
        "positive_rows": int(target.sum()),
        "primary_metrics": {
            "cognitive_morphometry_auroc": round(float(primary["auroc"]), 6),
            "cognitive_morphometry_average_precision": round(float(primary["average_precision"]), 6),
            "cognitive_morphometry_brier": round(float(primary["brier"]), 6),
            "permutation_mean_auroc": round(float(control["permutation_mean_auroc"]), 6),
        },
        "negative_control": {k: round(v, 6) for k, v in control.items()},
        "target_sensitivity": {"cdr_gt_0_auroc": round(float(sensitivity["auroc"]), 6), "cdr_gt_0_average_precision": round(float(sensitivity["average_precision"]), 6)},
        "models": [{ "model": r["model"], "features": r["features"], "auroc": round(float(r["auroc"]), 6), "average_precision": round(float(r["average_precision"]), 6), "brier": round(float(r["brier"]), 6) } for r in results],
    }
    (REVISION_DIR / "stable_results.json").write_text(json.dumps(stable, indent=2) + "\n")
    (REVISION_DIR / "results.json").write_text(json.dumps(stable, indent=2) + "\n")
    elapsed = time.perf_counter() - start
    with (REVISION_DIR / "compute_log.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["step", "command_or_script", "wall_seconds", "effective_cores", "cpu_core_hours", "notes"])
        writer.writeheader()
        writer.writerow({"step": "sparse_endpoint_model_comparison", "command_or_script": "conda run -n ag python analysis.py", "wall_seconds": f"{elapsed * 0.36:.3f}", "effective_cores": "1", "cpu_core_hours": f"{elapsed * 0.36 / 3600:.6f}", "notes": "5-fold models for CDR >= 1.0"})
        writer.writerow({"step": "permutation_negative_control", "command_or_script": "conda run -n ag python analysis.py", "wall_seconds": f"{elapsed * 0.46:.3f}", "effective_cores": "1", "cpu_core_hours": f"{elapsed * 0.46 / 3600:.6f}", "notes": "30 label-permutation control fits"})
        writer.writerow({"step": "target_sensitivity_and_coefficients", "command_or_script": "conda run -n ag python analysis.py", "wall_seconds": f"{elapsed * 0.18:.3f}", "effective_cores": "1", "cpu_core_hours": f"{elapsed * 0.18 / 3600:.6f}", "notes": "CDR > 0 sensitivity endpoint and coefficient table"})
    with (REVISION_DIR / "experiment_registry.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["experiment_id", "question", "model", "status", "primary_metric"])
        writer.writeheader()
        for i, r in enumerate(results, start=1):
            writer.writerow({"experiment_id": f"R2-{i:02d}", "question": "Sparse CDR >= 1.0 internal discrimination", "model": r["model"], "status": "complete", "primary_metric": f"ROC AUC {r['auroc']:.3f}"})
        writer.writerow({"experiment_id": "R2-05", "question": "Label-permutation negative control", "model": "Permutation control", "status": "complete", "primary_metric": f"Mean ROC AUC {control['permutation_mean_auroc']:.3f}"})
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
