#!/usr/bin/env python3
"""Clerk-flag templated Research Arena referee reviews.

Usage examples:

  python tools/review_similarity_audit.py oasis_demo
  python tools/review_similarity_audit.py ptbxl --write-default
  python tools/review_similarity_audit.py ptbxl --threshold 0.86

This deterministic tool checks text similarity only. It does not judge whether a
review is scientifically useful. LLM-backed agents must make reviewer-quality
judgments from the review content and artifact citations.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from dataclasses import asdict, dataclass
from difflib import SequenceMatcher
from pathlib import Path


@dataclass
class ReviewDoc:
    referee: str
    round_id: str
    path: str
    normalized: str


@dataclass
class FlaggedPair:
    left_referee: str
    left_round: str
    left_path: str
    right_referee: str
    right_round: str
    right_path: str
    comparison_type: str
    similarity: float
    reason: str


def normalize_review(text: str) -> str:
    text = text.lower()
    text = re.sub(r"`referee_\d+`", "`referee_x`", text)
    text = re.sub(r"referee_\d+", "referee_x", text)
    text = re.sub(r"review_round_\d+", "review_round_x", text)
    text = re.sub(r"round/revision reviewed:\s*`\d+`", "round/revision reviewed: `x`", text)
    text = re.sub(r"revision[_ -]?\d+", "revision_x", text)
    text = re.sub(r"\bround\s+\d+\b", "round_x", text)
    text = re.sub(r"\b0?\d+\b", "n", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def read_reviews(root: Path, run_id: str) -> list[ReviewDoc]:
    docs: list[ReviewDoc] = []
    for path in sorted(root.glob(f"agents/referee_*/workspace/{run_id}/review_round_*.md")):
        referee = path.parts[-4]
        match = re.search(r"review_round_(\d+)\.md$", path.name)
        round_id = match.group(1) if match else "unknown"
        docs.append(
            ReviewDoc(
                referee=referee,
                round_id=round_id,
                path=str(path.relative_to(root)),
                normalized=normalize_review(path.read_text(encoding="utf-8")),
            )
        )
    return docs


def compare_reviews(docs: list[ReviewDoc], threshold: float) -> list[FlaggedPair]:
    flags: list[FlaggedPair] = []
    for idx, left in enumerate(docs):
        for right in docs[idx + 1 :]:
            if left.referee == right.referee and left.round_id == right.round_id:
                continue
            same_round = left.round_id == right.round_id
            same_referee = left.referee == right.referee
            if not (same_round or same_referee):
                continue

            similarity = SequenceMatcher(None, left.normalized, right.normalized).ratio()
            if similarity < threshold:
                continue

            comparison_type = "same_round_cross_referee" if same_round else "same_referee_cross_round"
            reason = (
                "Different Referees in the same round look near-duplicate after identity normalization."
                if same_round
                else "The same Referee's review changed very little across rounds."
            )
            flags.append(
                FlaggedPair(
                    left_referee=left.referee,
                    left_round=left.round_id,
                    left_path=left.path,
                    right_referee=right.referee,
                    right_round=right.round_id,
                    right_path=right.path,
                    comparison_type=comparison_type,
                    similarity=round(similarity, 4),
                    reason=reason,
                )
            )
    return flags


def write_csv(path: Path, rows: list[FlaggedPair]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(asdict(rows[0]).keys()) if rows else [
        "left_referee",
        "left_round",
        "left_path",
        "right_referee",
        "right_round",
        "right_path",
        "comparison_type",
        "similarity",
        "reason",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(asdict(row))


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit Research Arena referee review similarity.")
    parser.add_argument("run_id", help="Run id under agents/referee_*/workspace/<run_id>.")
    parser.add_argument("--root", default=".", help="Research Arena repository root.")
    parser.add_argument("--threshold", type=float, default=0.88, help="Similarity ratio to flag.")
    parser.add_argument("--output-json", help="Optional JSON output path.")
    parser.add_argument("--output-csv", help="Optional CSV output path.")
    parser.add_argument(
        "--write-default",
        action="store_true",
        help="Write runs/<run_id>/review_similarity_audit.json and .csv.",
    )
    args = parser.parse_args()

    root = Path(args.root).resolve()
    docs = read_reviews(root, args.run_id)
    flags = compare_reviews(docs, args.threshold)
    payload = {
        "run_id": args.run_id,
        "clerk_type": "review_text_similarity",
        "scientific_judgment": "not_evaluated",
        "threshold": args.threshold,
        "review_count": len(docs),
        "flagged_pair_count": len(flags),
        "status": "flagged" if flags else "pass",
        "notes": [
            "This deterministic clerk checks textual similarity, not scientific usefulness.",
            "A flag requires editorial review; it does not automatically prove the reviews are invalid.",
            "A pass does not prove that reviews were useful or evidence-linked.",
            "Acceptance should wait for LLM-backed reviewer-quality judgment or a documented override.",
        ],
        "flags": [asdict(flag) for flag in flags],
    }

    output_json = Path(args.output_json) if args.output_json else None
    output_csv = Path(args.output_csv) if args.output_csv else None
    if args.write_default:
        output_json = root / "runs" / args.run_id / "review_similarity_audit.json"
        output_csv = root / "runs" / args.run_id / "review_similarity_audit.csv"

    if output_json:
        output_json.parent.mkdir(parents=True, exist_ok=True)
        output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    else:
        print(json.dumps(payload, indent=2, sort_keys=True))

    if output_csv:
        write_csv(output_csv, flags)

    return 2 if flags else 0


if __name__ == "__main__":
    raise SystemExit(main())
