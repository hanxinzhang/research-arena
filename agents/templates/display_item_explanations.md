# Display Item Explanations

Every revision must include this file. It is a bridge between the raw
figure/table artifacts and the manuscript narrative.

This file explains finished display items. It does not replace
`display_item_plan.md`, which records why the Researcher selected the display
program before or while plotting. Similar typography across Researchers can be
acceptable when it comes from a shared style helper, but similar figure concepts,
filenames, ordering, or plotting structure need a study-specific rationale in
the display plan and may require `runs/<run-id>/display_program_independence_review.md`.

For each figure and table, include one entry with:

- the artifact path;
- the manuscript section where it is explained;
- the matching `display_item_plan.md` item or a note that the display was added
  after the plan with a rationale;
- what the item is for;
- what every axis, label, legend, color, panel mark, annotation, or table column
  means;
- the short article-style explanation that should appear directly under the
  figure/table title in `article/article.pdf` for serious-pilot and full-research
  runs;
- for figures, the article grouping decision: `Article group: standalone` or a
  shared group id, plus panel labels and a rationale for why the figure should be
  standalone or combined;
- for figures, whether the source artifact was built with article-normalized
  typography and mark sizes;
- any raw identifier translations;
- the summary conclusion;
- the main caveat or limitation.

Raw internal labels such as `model_v3`, `lead_aVR_slope_rms`,
`ecg_plus_metadata_random_forest`, or `age_band_65_80` must either be replaced in
the artifact itself or paired with a human-readable translation here and in the
manuscript.

## Figure 1: `<human-readable title>`

Artifact path: `figures/<figure-file>.pdf`
Display type: figure
Where discussed in manuscript: `<section/subsection heading>`
Article group: `<standalone or short shared group name, e.g. model performance>`
Article group title: `<title used when two or more figures share this group>`
Article group explanation: `<one short paragraph for the combined multi-panel figure, when grouped>`
Article grouping rationale: `<why this figure should be grouped with related panels or kept standalone; this is an author/editor judgment, not a filename rule>`
Panel label: `<a, b, c, ... when grouped>`
Panel title: `<short panel-level title when grouped>`
Panel order: `<integer order within group when grouped>`
Panel columns: `<optional 1, 2, or 3 for grouped figures>`
Figure typography: `<article-normalized or limitation>`
Figure mark scale: `<article-normalized or limitation>`

### Article Explanation

`<One short paragraph for the integrated article: the substantive pattern,
contrast, model behavior, or limitation shown in the figure. Write like a normal
journal caption paragraph. Avoid meta-commentary about instructing or orienting
the reader.>`

### Purpose

`<What question this figure answers and why it belongs in the manuscript.>`

### Display Details

- x-axis:
- y-axis:
- panels:
- color/line/marker/legend:
- annotations or thresholds:
- sample size, denominator, or cohort definition:

### Raw Label Translation

- `<raw_label>` -> `<human-readable label and definition>`

### Summary Conclusion

`<One to three sentences stating the takeaway supported by this figure.>`

### Caveat

`<What the figure does not prove or what a reader could misread.>`

## Table 1: `<human-readable title>`

Artifact path: `tables/<table-file>`
Display type: table
Where discussed in manuscript: `<section/subsection heading>`

### Article Explanation

`<One short paragraph for the integrated article: the substantive denominator,
contrast, estimate, uncertainty, or limitation shown in the table. Write like a
normal journal caption paragraph. Avoid meta-commentary about instructing or
orienting the reader.>`

### Purpose

`<What question this table answers and why it belongs in the manuscript.>`

### Display Details

- rows:
- columns:
- units:
- denominators or sample sizes:
- abbreviations:
- sorting/filtering:

### Raw Label Translation

- `<raw_column_or_row_name>` -> `<human-readable label and definition>`

### Summary Conclusion

`<One to three sentences stating the takeaway supported by this table.>`

### Caveat

`<What the table does not prove or what a reader could misread.>`
