# Pilot Study Plan

Run id: `<run-id>`
Researcher: `<researcher-id>`

## Pilot Purpose

State what the pilot must teach before candidate studies are finalized.

## Pilot Questions

1. `<question about data structure, signal, feasibility, leakage, or compute>`

## Subset Or Sample

- Selection rule:
- Sample size:
- Split or grouping rule:
- Why this subset is representative enough for planning:

## Planned Pilot Actions

| component | command_or_method | expected_output | success_criterion | not_allowed_to_conclude |
| --- | --- | --- | --- | --- |
| data_load | `<command>` | shape/timing | loads without parser failures | final prevalence or performance |
| baseline_smoke_test | `<command>` | rough metric | exposes feasibility | publication claim |

## Resource Measurements

- Track wall seconds for every component.
- Track effective CPU cores and estimated CPU-core hours.
- Track GPU hours if a GPU is allocated.
- Record warnings, failures, memory pressure, and I/O bottlenecks.

## Stop Or Pivot Criteria

- Stop if:
- Revise candidate space if:
- Escalate to stronger model if:
- Request lower article type if:
