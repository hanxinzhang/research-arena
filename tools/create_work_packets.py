#!/usr/bin/env python3
"""Create explicit Research Arena work packets for agent turns.

Work packets are prompt inputs, not role artifacts. They help avoid hidden master
scripts by making each role's allowed inputs, outputs, and decision authority
visible before the role turn begins.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path
from textwrap import dedent


REFEREES = ["referee_1", "referee_2", "referee_3", "referee_4"]


def rel(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def common_header(run_id: str, title: str) -> str:
    created = datetime.now(timezone.utc).isoformat()
    return dedent(
        f"""\
        # {title}

        - Run id: `{run_id}`
        - Packet type: prompt input
        - Created at UTC: `{created}`

        This packet is an instruction artifact. It must not prewrite the role's
        conclusions, issue resolutions, acceptance decision, or scientific
        judgment. The receiving agent must inspect the cited inputs and write only
        the allowed outputs for its own role.

        """
    )


def proposal_gate_packet(run_id: str) -> str:
    return common_header(run_id, "Study Design Board Proposal-Gate Packet") + dedent(
        f"""\
        ## Allowed Role

        - Agent: `study_design_board`
        - Role: `study_design_board`

        ## Required Inputs

        - `runs/{run_id}/article_type_contract.md`
        - `runs/{run_id}/study_design_contract.md`
        - `runs/{run_id}/research_depth_contract.md`
        - `runs/{run_id}/compute_budget.md` or `.json`
        - `submissions/{run_id}/submission_*_*/proposal_gate/data_familiarization.md`
        - `submissions/{run_id}/submission_*_*/proposal_gate/pilot_study_plan.md`
        - `submissions/{run_id}/submission_*_*/proposal_gate/pilot_study_results.json`
        - `submissions/{run_id}/submission_*_*/proposal_gate/pilot_compute_log.csv` or `.json`
        - `submissions/{run_id}/submission_*_*/proposal_gate/pilot_lessons.md`
        - `submissions/{run_id}/submission_*_*/proposal_gate/candidate_studies.md`
        - `submissions/{run_id}/submission_*_*/proposal_gate/selected_proposal.md`
        - `submissions/{run_id}/submission_*_*/proposal_gate/compute_budget_estimate.md`

        ## Allowed Outputs

        - `agents/study_design_board/workspace/{run_id}/proposal_review_<submission-id>.md`
        - `runs/{run_id}/proposal_gate_summary.md`
        - one append-only event in `runs/{run_id}/event_log.jsonl`

        ## Required Decision Shape

        Use one of: `approve_for_analysis`, `revise_before_analysis`,
        `downgrade_article_type`, or `stop_before_analysis`.

        For every selected proposal, cite the exact artifacts read, state the
        article-type fit, compute realism, expected evidence, and blocking design
        risks. Do not write analysis code or manuscript text for Researchers.
        """
    )


def integrity_packet(run_id: str, round_id: str) -> str:
    return common_header(run_id, f"Integrity Checker Round {round_id} Packet") + dedent(
        f"""\
        ## Allowed Role

        - Agent: `integrity_checker`
        - Role: `integrity_checker`

        ## Required Inputs

        - `runs/{run_id}/event_log.jsonl`
        - `runs/{run_id}/proposal_gate_summary.md`
        - all latest `submissions/{run_id}/submission_*/revision_{round_id}/artifact_manifest.json`
        - all latest `submissions/{run_id}/submission_*/revision_{round_id}/compute_log.*`
        - all latest `submissions/{run_id}/submission_*/revision_{round_id}/verification_matrix.*`
        - all latest `human_readable_outputs/{run_id}/submission_*/revision_{round_id}/`
        - `runs/{run_id}/research_depth_audit.json` when available
        - `runs/{run_id}/artifact_authority_audit.json` when available
        - `runs/{run_id}/run_state_audit.json` when available
        - `runs/{run_id}/scripted_generation_audit.json` when available

        ## Allowed Outputs

        - `agents/integrity_checker/workspace/{run_id}/integrity_report_round_{round_id}.md`
        - rerun logs under `agents/integrity_checker/workspace/{run_id}/`
        - one append-only event in `runs/{run_id}/event_log.jsonl`

        ## Required Work

        Rerun or inspect each submitted analysis, verify manifests and hashes,
        check proposal-gate order, check the human-readable package, and identify
        issue IDs with severity, required evidence, acceptance criteria, and
        status. Do not resolve Referee-owned issues unless you verified the cited
        evidence directly.
        """
    )


def referee_packet(run_id: str, referee: str, round_id: str) -> str:
    issue_prefix = f"R{referee.split('_')[-1]}-"
    return common_header(run_id, f"{referee} Round {round_id} Packet") + dedent(
        f"""\
        ## Allowed Role

        - Agent: `{referee}`
        - Role: `referee`

        ## Required Inputs

        - `runs/{run_id}/article_type_contract.md`
        - `runs/{run_id}/manuscript_quality_contract.md`
        - `runs/{run_id}/proposal_gate_summary.md`
        - latest `human_readable_outputs/{run_id}/submission_*/revision_{round_id}/`
        - latest submission artifacts under `submissions/{run_id}/submission_*/revision_{round_id}/`
        - prior `{referee}` reviews and Researcher responses when `round_id` is not `00`
        - current Integrity Checker report when available

        ## Allowed Outputs

        - `agents/{referee}/workspace/{run_id}/review_round_{round_id}.md`
        - one append-only event in `runs/{run_id}/event_log.jsonl`

        ## Required Work

        Write evidence-linked review comments only after reading the artifacts.
        Use issue IDs beginning with `{issue_prefix}`. Every major or blocking
        issue must cite an exact path and state required evidence plus acceptance
        criterion. Include what changed since the previous revision and direct
        questions for the Researcher. Do not write another Referee's review,
        integrity report, or editorial decision.
        """
    )


def llm_audit_packet(run_id: str, audit_name: str) -> str:
    output_name = {
        "scientific-depth": "scientific_depth_review.md",
        "revision-trajectory": "revision_trajectory_review.md",
        "novelty-article-fit": "novelty_article_fit_review.md",
        "reviewer-quality": "reviewer_quality_review.md",
        "manuscript-article-voice": "manuscript_article_voice_review.md",
        "display-item-narrative": "display_item_narrative_review.md",
        "display-item-grouping": "display_item_grouping_review.md",
        "display-program-independence": "display_program_independence_review.md",
    }[audit_name]
    return common_header(run_id, f"{audit_name.replace('-', ' ').title()} Audit Packet") + dedent(
        f"""\
        ## Allowed Role

        - Agent: `auditor`
        - Role: `auditor`

        ## Required Inputs

        - relevant rubric under `audits/`
        - `runs/{run_id}/event_log.jsonl`
        - `runs/{run_id}/research_depth_audit.json`
        - `runs/{run_id}/review_similarity_audit.json` when available
        - `runs/{run_id}/trajectory_clerk.json` when available
        - all relevant Referee reviews, Integrity Checker reports, submissions,
          verification matrices, and human-readable packages

        ## Allowed Outputs

        - `runs/{run_id}/{output_name}`
        - one append-only event in `runs/{run_id}/event_log.jsonl`

        ## Required Work

        Make a judgment from the rubric and cited artifacts. Deterministic clerk
        outputs are evidence tables only. Do not prewrite acceptance or rejection;
        give the Editor a concise judgment, unresolved risks, and exact artifact
        citations.
        """
    )


def final_decision_packet(run_id: str) -> str:
    return common_header(run_id, "Editor Final-Decision Packet") + dedent(
        f"""\
        ## Allowed Role

        - Agent: `editor_publisher`
        - Role: `editor`

        ## Required Inputs

        - `runs/{run_id}/pre_decision_freeze_manifest.json`
        - `runs/{run_id}/pre_decision_freeze_verification.json` when verifying an existing pre-decision freeze
        - `runs/{run_id}/artifact_authority_audit.json`
        - `runs/{run_id}/run_state_audit.json`
        - `runs/{run_id}/scripted_generation_audit.json`
        - `runs/{run_id}/archive_hygiene_audit.json`
        - `runs/{run_id}/research_depth_audit.json`
        - `runs/{run_id}/review_similarity_audit.json`
        - `runs/{run_id}/trajectory_clerk.json` when applicable
        - all LLM-backed judgment outputs
        - latest Referee reviews, Integrity Checker reports, verification
          matrices, and proposal-gate summary

        ## Allowed Outputs

        - `runs/{run_id}/final_decision.md`
        - `runs/{run_id}/final_decision.json` when useful
        - `runs/{run_id}/summary.md` when useful
        - one final-decision event in `runs/{run_id}/event_log.jsonl`

        ## Required Work

        Decide by gates, not by round count. The decision must cite
        `runs/{run_id}/pre_decision_freeze_manifest.json` as a frozen evidence input and
        address unresolved proposal-gate, artifact-authority, state-order,
        scripted-generation, presentation, reproducibility, review-quality,
        novelty, and article-type risks. Do not write new research, review, audit,
        or package artifacts after the final decision unless the run is explicitly
        reopened and the stale decision is invalidated. After the final decision
        event is appended, create and verify
        `runs/{run_id}/post_decision_archive_manifest.json`.
        """
    )


def packet_specs(run_id: str, phase: str, round_id: str) -> dict[str, str]:
    specs: dict[str, str] = {}
    if phase in {"proposal-gate", "all"}:
        specs["proposal_gate.md"] = proposal_gate_packet(run_id)
    if phase in {"integrity", "all"}:
        specs[f"integrity_round_{round_id}.md"] = integrity_packet(run_id, round_id)
    if phase in {"referee-round", "all"}:
        for referee in REFEREES:
            specs[f"{referee}_round_{round_id}.md"] = referee_packet(run_id, referee, round_id)
    if phase in {"llm-audits", "all"}:
        for audit_name in [
            "scientific-depth",
            "revision-trajectory",
            "novelty-article-fit",
            "reviewer-quality",
            "manuscript-article-voice",
            "display-item-narrative",
            "display-item-grouping",
            "display-program-independence",
        ]:
            specs[f"{audit_name}_audit.md"] = llm_audit_packet(run_id, audit_name)
    if phase in {"final-decision", "all"}:
        specs["editor_final_decision.md"] = final_decision_packet(run_id)
    return specs


def main() -> int:
    parser = argparse.ArgumentParser(description="Create Research Arena work-packet prompts for role turns.")
    parser.add_argument("run_id", help="Run id.")
    parser.add_argument("--root", default=".", help="Research Arena repository root.")
    parser.add_argument(
        "--phase",
        choices=["proposal-gate", "integrity", "referee-round", "llm-audits", "final-decision", "all"],
        default="all",
        help="Packet phase to create.",
    )
    parser.add_argument("--round", dest="round_id", default="00", help="Two-digit revision or review round id.")
    parser.add_argument("--output-root", help="Output root. Defaults to work_packets/<run-id>.")
    parser.add_argument("--replace", action="store_true", help="Replace existing packet files.")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    output_root = Path(args.output_root) if args.output_root else root / "work_packets" / args.run_id
    if not output_root.is_absolute():
        output_root = root / output_root

    specs = packet_specs(args.run_id, args.phase, args.round_id)
    output_root.mkdir(parents=True, exist_ok=True)
    written: list[str] = []
    skipped: list[str] = []
    for filename, content in specs.items():
        path = output_root / filename
        if path.exists() and not args.replace:
            skipped.append(rel(path, root))
            continue
        path.write_text(content, encoding="utf-8")
        written.append(rel(path, root))

    print(f"Wrote {len(written)} packet(s) under {rel(output_root, root)}.")
    if skipped:
        print(f"Skipped {len(skipped)} existing packet(s); pass --replace to overwrite.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
