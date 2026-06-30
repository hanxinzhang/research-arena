# OASIS demo example

This folder is a tiny Research Arena example output. It is intentionally compact:
it shows the shape of a completed one-round community run without committing a
large generated `runs/` and `submissions/` tree.

The example was generated from a local copy of `data/OASIS_cross_tbl_df.csv` and
simulates:

- two Researchers competing on the same shared dataset;
- one Integrity Checker;
- two Referees;
- one Editor/Publisher decision.

The accepted example manuscript is `accepted_manuscript.md` with a text-only PDF
render at `accepted_manuscript.pdf`. Figure and table artifacts are separate under
`figures/` and `tables/`.

`analysis.py` is a small standard-library script that regenerates `results.json`
and `tables/cdr_group_summary.csv` after you create the local shared OASIS CSV
following `../../data/README.md`.

This demo is exploratory only. It is not clinical advice, not a diagnostic system,
and not evidence that the protocol produces valid science without human review.
