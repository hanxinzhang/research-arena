"""Research Arena figure and Matplotlib-PDF style defaults.

Copy or import apply_research_arena_figure_style() in submitted analysis scripts
before creating figures or Matplotlib-rendered manuscript PDFs. The helper
registers the bundled open-source Inter files so typography does not depend on
each user's operating-system fonts.

This module is only a style and rendering utility. It may standardize fonts,
line widths, marker sizes, grids, label humanization, and save behavior, but it
must not be treated as a figure-concept template. Researchers choose their own
display program in `display_item_plan.md`; they should not infer a required
figure sequence, filename pattern, panel order, or plotting grammar from this
file.

The defaults are article-native: all in-figure text uses one size so titles,
subtitles, axis labels, tick labels, annotations, and legends survive insertion
into `article.pdf` without looking like a separate poster graphic.
"""

from __future__ import annotations

import re
from pathlib import Path

BUNDLED_FONT_FAMILY = "Inter"
BUNDLED_FONT_DIRNAME = Path("assets") / "fonts" / "inter"
BUNDLED_FONT_FILENAMES = [
    "Inter-Regular.ttf",
    "Inter-Bold.ttf",
    "Inter-Italic.ttf",
    "Inter-BoldItalic.ttf",
]
ARTICLE_FIGURE_TEXT_SIZE_PT = 8.5
ARTICLE_FIGURE_LINEWIDTH_PT = 0.95
ARTICLE_FIGURE_MARKER_SIZE_PT = 3.0
ARTICLE_FIGURE_BAR_EDGEWIDTH_PT = 0.55

PREFERRED_SANS_SERIF_FONTS = [
    BUNDLED_FONT_FAMILY,
    "TeX Gyre Heros",
    "Nimbus Sans",
    "Liberation Sans",
    "Noto Sans",
    "Source Sans 3",
    "Source Sans Pro",
]

DEFAULT_LABEL_TRANSLATIONS = {
    "auc": "AUC",
    "auroc": "ROC AUC",
    "auc_roc": "ROC AUC",
    "average_precision": "Average Precision",
    "age_only": "Age Only",
    "asf": "Atlas Scaling Factor",
    "brier": "Brier Score",
    "cdr": "Clinical Dementia Rating",
    "ci_2_5": "2.5% CI",
    "ci_97_5": "97.5% CI",
    "cognitive_morphometry": "Cognitive + Morphometry",
    "cognitive_morphometry_sparse_cdr_ge_1": "Sparse CDR >= 1 Model",
    "coefficient": "Coefficient",
    "comparison": "Comparison",
    "ci": "CI",
    "ecg": "ECG",
    "estimate": "Estimate",
    "educ": "Education",
    "etiv": "Estimated Total Intracranial Volume",
    "feature": "Feature",
    "folds": "Folds",
    "id": "ID",
    "m_f": "Sex",
    "m_f_m": "Male Sex",
    "mean_average_precision": "Mean Average Precision",
    "mean_auroc": "Mean ROC AUC",
    "mean_brier": "Mean Brier Score",
    "mean_predicted_probability": "Mean Predicted Probability",
    "metric": "Metric",
    "model": "Model",
    "mmse": "Mini-Mental State Examination",
    "morphometry_age": "Morphometry + Age",
    "mri": "MRI",
    "n": "n",
    "no_mmse_sensitivity": "No-MMSE Sensitivity",
    "nwbv": "Normalized Whole-Brain Volume",
    "observed_prevalence": "Observed Prevalence",
    "observed_sparse_ap": "Observed Sparse Average Precision",
    "observed_sparse_auroc": "Observed Sparse ROC AUC",
    "observed_sparse_vs_permutation": "Observed Sparse vs Permutation",
    "odds_ratio": "Odds Ratio",
    "permutation_negative_control": "Permutation Control",
    "permutation_ap": "Permutation Average Precision",
    "permutation_auroc": "Permutation ROC AUC",
    "positive_rows": "Positive Rows",
    "prevalence_baseline": "Prevalence Baseline",
    "pr": "PR",
    "roc": "ROC",
    "se": "SE",
    "sd": "SD",
    "sd_average_precision": "SD Average Precision",
    "sd_auroc": "SD ROC AUC",
    "sd_brier": "SD Brier Score",
    "ses": "Socioeconomic Status",
    "target": "Target",
    "target_sensitivity_cdr_gt_0": "CDR > 0 Sensitivity",
}


def _find_bundled_font_dir() -> Path | None:
    """Find the framework root whether this file is imported or copied."""
    start = Path(__file__).resolve()
    for parent in [start.parent, *start.parents]:
        candidate = parent / BUNDLED_FONT_DIRNAME
        if candidate.is_dir():
            return candidate
    return None


def bundled_font_paths() -> list[Path]:
    font_dir = _find_bundled_font_dir()
    if font_dir is None:
        return []
    return [font_dir / filename for filename in BUNDLED_FONT_FILENAMES if (font_dir / filename).is_file()]


def register_research_arena_fonts() -> str:
    import matplotlib.font_manager as font_manager

    for font_path in bundled_font_paths():
        font_manager.fontManager.addfont(str(font_path))
    return BUNDLED_FONT_FAMILY


def humanize_label(label: object, translations: dict[str, str] | None = None) -> str:
    """Turn code-style labels into readable figure/table text."""
    raw = str(label).strip()
    if not raw:
        return raw

    lookup = dict(DEFAULT_LABEL_TRANSLATIONS)
    if translations:
        lookup.update({str(key).lower(): value for key, value in translations.items()})

    key = re.sub(r"[^A-Za-z0-9]+", "_", raw).strip("_").lower()
    if key in lookup:
        return lookup[key]

    spaced = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", raw)
    spaced = re.sub(r"[_\-]+", " ", spaced)
    spaced = re.sub(r"\s+", " ", spaced).strip()
    if not spaced:
        return raw

    words = []
    for word in spaced.split(" "):
        lower = word.lower()
        if lower in lookup:
            words.append(lookup[lower])
        elif len(word) <= 3 and word.isupper():
            words.append(word)
        else:
            words.append(word[:1].upper() + word[1:])
    return " ".join(words)


def apply_research_arena_figure_style(text_size_pt: float = ARTICLE_FIGURE_TEXT_SIZE_PT, auto_normalize_on_save: bool = True) -> None:
    import matplotlib as mpl

    register_research_arena_fonts()
    text_size = float(text_size_pt)
    mpl.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": PREFERRED_SANS_SERIF_FONTS,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "svg.fonttype": "none",
            "figure.dpi": 160,
            "savefig.dpi": 300,
            "savefig.bbox": "tight",
            "font.size": text_size,
            "axes.titlesize": text_size,
            "axes.titleweight": "regular",
            "axes.labelsize": text_size,
            "axes.labelweight": "regular",
            "axes.linewidth": 0.72,
            "xtick.labelsize": text_size,
            "ytick.labelsize": text_size,
            "legend.fontsize": text_size,
            "legend.title_fontsize": text_size,
            "figure.titlesize": text_size,
            "figure.titleweight": "bold",
            "lines.linewidth": ARTICLE_FIGURE_LINEWIDTH_PT,
            "lines.markersize": ARTICLE_FIGURE_MARKER_SIZE_PT,
            "patch.linewidth": ARTICLE_FIGURE_BAR_EDGEWIDTH_PT,
            "errorbar.capsize": 2.2,
            "axes.grid": True,
            "grid.alpha": 0.25,
            "grid.linewidth": 0.45,
        }
    )
    if auto_normalize_on_save:
        install_research_arena_savefig_normalizer(text_size_pt=text_size)


def normalize_research_arena_axes(ax, text_size_pt: float = ARTICLE_FIGURE_TEXT_SIZE_PT) -> None:
    """Apply the one-size article figure contract to an existing Matplotlib axes."""
    text_size = float(text_size_pt)
    ax.title.set_fontsize(text_size)
    ax.xaxis.label.set_fontsize(text_size)
    ax.yaxis.label.set_fontsize(text_size)
    ax.tick_params(axis="both", which="major", labelsize=text_size, width=0.72, length=3.0)
    ax.tick_params(axis="both", which="minor", labelsize=text_size, width=0.55, length=2.0)
    for label in [*ax.get_xticklabels(), *ax.get_yticklabels()]:
        label.set_fontsize(text_size)
    for text in ax.texts:
        text.set_fontsize(text_size)
    legend = ax.get_legend()
    if legend is not None:
        for text in legend.get_texts():
            text.set_fontsize(text_size)
        title = legend.get_title()
        if title is not None:
            title.set_fontsize(text_size)
        legend.get_frame().set_linewidth(0.55)
    for line in ax.lines:
        line.set_linewidth(min(max(line.get_linewidth(), 0.85), 1.35))
        line.set_markersize(min(max(line.get_markersize(), 2.4), 4.0))
    for spine in ax.spines.values():
        spine.set_linewidth(0.72)


def normalize_research_arena_figure(fig, text_size_pt: float = ARTICLE_FIGURE_TEXT_SIZE_PT) -> None:
    """Normalize all text and marks in a figure before saving."""
    text_size = float(text_size_pt)
    for text in fig.texts:
        text.set_fontsize(text_size)
    for ax in fig.axes:
        normalize_research_arena_axes(ax, text_size_pt=text_size)
    fig.tight_layout()


def save_research_arena_figure(fig, path: str | Path, text_size_pt: float = ARTICLE_FIGURE_TEXT_SIZE_PT, **savefig_kwargs) -> None:
    """Save a Matplotlib figure after enforcing the Research Arena style contract."""
    normalize_research_arena_figure(fig, text_size_pt=text_size_pt)
    fig.savefig(path, **savefig_kwargs)


def install_research_arena_savefig_normalizer(text_size_pt: float = ARTICLE_FIGURE_TEXT_SIZE_PT) -> None:
    """Normalize Matplotlib figures whenever Figure.savefig is called."""
    import matplotlib.figure as matplotlib_figure

    text_size = float(text_size_pt)
    figure_cls = matplotlib_figure.Figure
    original = getattr(figure_cls, "_research_arena_original_savefig", None)
    if original is None:
        original = figure_cls.savefig
        setattr(figure_cls, "_research_arena_original_savefig", original)

    def research_arena_savefig(self, *args, **kwargs):
        normalize_research_arena_figure(self, text_size_pt=text_size)
        return original(self, *args, **kwargs)

    setattr(figure_cls, "savefig", research_arena_savefig)
