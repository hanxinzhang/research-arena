# Start OASIS Demo

Please run Research Arena on `data/OASIS_cross_tbl_df.csv`.

If the CSV is missing, stop and ask me to follow `data/README.md` to download or
export it locally. Do not download, redistribute, or invent the dataset unless I
explicitly confirm the source and licensing terms.

Follow `program.md` and all agent rules under `agents/`.

Use:

- two Researchers: `researcher_1`, `researcher_2`
- one Integrity Checker: `integrity_checker`
- two Referees: `referee_1`, `referee_2`
- one Editor/Publisher: `editor_publisher`

If additional `researcher_<n>` or `referee_<n>` folders are named by the user, include
them in the same run and have every Referee review every Researcher submission unless
the user specifies a different assignment.

Researchers share the same dataset, but they do not need to share the same target,
metric, or research question. Run one initial submission plus one revision round.
Researchers may use recent literature for context, but must generate original ideas,
cite sources, and avoid plagiarism. Integrity Checker and Referees should assess
originality, citation quality, and plagiarism risk.
Each Researcher should include `literature_notes.md` and `analysis_plan.md` in the
submission folder before final manuscript writing.

Write artifacts under:

- `runs/oasis_demo/`
- `submissions/oasis_demo/`
- `agents/<agent-id>/workspace/oasis_demo/`

At the end, summarize the final editorial decision and provide the accepted
manuscript path if a manuscript is accepted.
