# Start OASIS Demo

```text
Please run Research Arena.

Dataset: data/OASIS_cross_tbl_df.csv
Run id: oasis_demo
Agents: 2 Researchers, 1 Study Design Board, 1 Integrity Checker, 4 Referees, 1 Editor
Research ambition: compact demo
Compute budget: target 0.25 CPU-core hours per Researcher; minimum 3 experiment rows per Researcher
Revision budget: revision_00 plus 1 evidence-linked revision
Research scope: Researchers may choose different questions; no shared target required
Pilot requirement: each Researcher must inspect the data and run a small Phase 0 pilot before proposing candidate studies

Use the framework defaults in AGENTS.md, program.md, and agents/ for proposal
gates, contracts, artifacts, audits, issue-ledger rules, presentation checks,
trajectory checks, artifact-authority checks, state-order checks,
scripted-generation checks, work packets when orchestration is used, freeze
manifest creation, the final editorial decision, and the clean final output bundle
under `outputs/oasis_demo/`. After the final bundle verifies, remove duplicate
run-specific workflow roots so `outputs/oasis_demo/` is the only completed-run
handoff folder left in the project root.
```

If `data/OASIS_cross_tbl_df.csv` is missing, stop and ask the user to follow
`data/README.md` to create it locally.
