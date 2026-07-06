# Research Arena Final Output Bundle

Run id: `oasis_demo`

Start with `human_readable_outputs/`. It contains the final decision, run summary,
article PDFs, manuscript PDFs, figures, tables, and source code intended for
normal reading. Machine-readable package manifests are intentionally omitted
from this reader-facing area.

Use `diagnosis_process_files/` only when auditing how the run was produced. It
contains run records, submitted revisions, work packets, and role workspaces.

## Folder Layout

```text
human_readable_outputs/
  run_overview/
  <submission>/<revision>/
diagnosis_process_files/
  run_records/
  submitted_revisions/
  work_packets/
  agent_workspaces/
final_output_manifest.json
final_output_verification.json
```

This bundle is a post-decision handoff view. It does not rewrite scientific
claims, reviewer judgments, or editor decisions; it only separates reading
artifacts from process and diagnosis files.
