#!/usr/bin/env python3
"""Build human-readable Research Arena revision output folders.

The canonical analysis/review workspace remains under
submissions/<run-id>/<submission>/revision_*. This helper copies the human-readable
subset of each revision into human_readable_outputs/<run-id>/ so humans can open
the manuscript, figures, tables, and source code without navigating the full audit
package.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import shutil
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path


TEMPLATE_DIR = Path(__file__).resolve().parents[1] / "agents" / "templates"
if str(TEMPLATE_DIR) not in sys.path:
    sys.path.insert(0, str(TEMPLATE_DIR))

from figure_style import humanize_label


SOURCE_SUFFIXES = {
    ".py",
    ".r",
    ".R",
    ".jl",
    ".m",
    ".ipynb",
    ".qmd",
    ".Rmd",
    ".rmd",
    ".sh",
    ".sql",
    ".toml",
    ".yaml",
    ".yml",
}

SOURCE_NAMES = {
    "Dockerfile",
    "environment.yml",
    "environment.yaml",
    "requirements.txt",
    "requirements-dev.txt",
    "pyproject.toml",
    "setup.py",
    "setup.cfg",
    "Makefile",
    "Snakefile",
}

SOURCE_DIRS = {"src", "scripts", "code", "notebook", "notebooks"}
SKIP_NAMES = {".DS_Store", "__pycache__", ".ipynb_checkpoints"}
TABLE_SUFFIXES = {".csv", ".tsv"}
NUMERIC_PATTERN = re.compile(r"^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?%?$")


@dataclass
class CopiedItem:
    kind: str
    source: str
    destination: str
    bytes: int
    source_sha256: str
    destination_sha256: str


@dataclass
class PackageRecord:
    run_id: str
    submission: str
    revision: str
    source_revision: str
    output_folder: str
    require_article_pdf: bool
    copied_items: list[CopiedItem]
    missing_expected_items: list[str]


def repo_root_from(start: Path) -> Path:
    start = start.resolve()
    for parent in [start, *start.parents]:
        if (parent / "program.md").is_file() and (parent / "agents").is_dir():
            return parent
    return start


def rel(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def should_skip(path: Path) -> bool:
    return path.name in SKIP_NAMES or path.name.startswith(".")


def has_skipped_part(path: Path) -> bool:
    return any(part in SKIP_NAMES or part.startswith(".") for part in path.parts)


def copy_file(source: Path, destination: Path, kind: str, root: Path) -> CopiedItem:
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
    return CopiedItem(
        kind=kind,
        source=rel(source, root),
        destination=rel(destination, root),
        bytes=destination.stat().st_size,
        source_sha256=sha256(source),
        destination_sha256=sha256(destination),
    )


def should_preserve_table_cell(value: str) -> bool:
    text = value.strip()
    if not text:
        return True
    if NUMERIC_PATTERN.match(text):
        return True
    return False


def humanize_table_cell(value: str) -> str:
    if should_preserve_table_cell(value):
        return value
    return humanize_label(value)


def copy_table_file(source: Path, destination: Path, kind: str, root: Path) -> CopiedItem:
    destination.parent.mkdir(parents=True, exist_ok=True)
    delimiter = "\t" if source.suffix.lower() == ".tsv" else ","
    try:
        with source.open("r", newline="", encoding="utf-8") as handle:
            rows = list(csv.reader(handle, delimiter=delimiter))
    except UnicodeDecodeError:
        return copy_file(source, destination, kind, root)

    with destination.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, delimiter=delimiter, lineterminator="\n")
        for row in rows:
            writer.writerow([humanize_table_cell(cell) for cell in row])

    return CopiedItem(
        kind=kind,
        source=rel(source, root),
        destination=rel(destination, root),
        bytes=destination.stat().st_size,
        source_sha256=sha256(source),
        destination_sha256=sha256(destination),
    )


def copy_tree(source_dir: Path, destination_dir: Path, kind: str, root: Path) -> list[CopiedItem]:
    copied: list[CopiedItem] = []
    destination_dir.mkdir(parents=True, exist_ok=True)
    if not source_dir.is_dir():
        return copied
    for source in sorted(path for path in source_dir.rglob("*") if path.is_file()):
        if has_skipped_part(source.relative_to(source_dir)):
            continue
        destination = destination_dir / source.relative_to(source_dir)
        if kind == "table" and source.suffix.lower() in TABLE_SUFFIXES:
            copied.append(copy_table_file(source, destination, kind, root))
        else:
            copied.append(copy_file(source, destination, kind, root))
    return copied


def source_files(revision_dir: Path) -> list[Path]:
    sources: list[Path] = []
    for path in sorted(revision_dir.iterdir()):
        if should_skip(path):
            continue
        if path.is_file() and (path.suffix in SOURCE_SUFFIXES or path.name in SOURCE_NAMES):
            sources.append(path)
        elif path.is_dir() and path.name in SOURCE_DIRS:
            sources.extend(
                sorted(
                    file
                    for file in path.rglob("*")
                    if file.is_file() and not has_skipped_part(file.relative_to(path))
                )
            )
    return sources


def latest_revision(submission_dir: Path) -> Path | None:
    revisions = [path for path in submission_dir.glob("revision_*") if path.is_dir()]
    return sorted(revisions, key=revision_sort_key)[-1] if revisions else None


def revision_sort_key(path: Path) -> tuple[int, str]:
    suffix = path.name.removeprefix("revision_")
    if suffix.isdigit():
        return (int(suffix), path.name)
    return (-1, path.name)


def revision_dirs(submissions_root: Path, latest_only: bool) -> list[Path]:
    revisions: list[Path] = []
    for submission_dir in sorted(path for path in submissions_root.glob("submission_*") if path.is_dir()):
        if latest_only:
            latest = latest_revision(submission_dir)
            if latest is not None:
                revisions.append(latest)
        else:
            revisions.extend(
                sorted(
                    (path for path in submission_dir.glob("revision_*") if path.is_dir()),
                    key=revision_sort_key,
                )
            )
    return revisions


def write_readme(output_dir: Path, record: PackageRecord, root: Path) -> CopiedItem:
    article_line = (
        "- `article.pdf`: integrated journal-style article PDF copied from `article/article.pdf`."
        if record.require_article_pdf
        else "- `article.pdf`: optional only because the run contract explicitly opts out of integrated article PDFs."
    )
    text = f"""# Human-Readable Revision Output

Run id: `{record.run_id}`

Submission: `{record.submission}`

Revision: `{record.revision}`

Source revision folder: `{record.source_revision}`

## Contents

- `manuscript.pdf`: line-numbered manuscript PDF for review.
{article_line}
- `figures/`: standalone figure artifacts copied from the revision.
- `tables/`: standalone table artifacts copied from the revision.
- `source_code/`: source code and executable analysis files copied from the revision.
- `human_readable_package_manifest.json`: machine-readable copy manifest.

This folder is a human-readable view of the revision, not a replacement for the
full audit package. Use the source revision folder for issue ledgers, compute
logs, verification matrices, and other review artifacts.
"""
    readme = output_dir / "README.md"
    readme.write_text(text, encoding="utf-8")
    digest = sha256(readme)
    return CopiedItem("readme", rel(readme, root), rel(readme, root), readme.stat().st_size, digest, digest)


def contract_requires_article_pdf(root: Path, run_id: str) -> bool:
    path = root / "runs" / run_id / "manuscript_quality_contract.md"
    if not path.is_file():
        return True
    text = path.read_text(encoding="utf-8", errors="replace")
    match = re.search(r"^\s*require_integrated_article_pdf\s*:\s*(true|false|yes|no|1|0)\s*$", text, flags=re.IGNORECASE | re.MULTILINE)
    if not match:
        return True
    return match.group(1).strip().lower() in {"true", "yes", "1"}


def package_revision(revision_dir: Path, output_root: Path, root: Path, replace: bool, require_article_pdf: bool) -> PackageRecord:
    submission = revision_dir.parent.name
    revision = revision_dir.name
    run_id = revision_dir.parent.parent.name
    output_dir = output_root / submission / revision

    if output_dir.exists():
        if not replace:
            raise SystemExit(f"{rel(output_dir, root)} already exists; pass --replace to rebuild it.")
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    copied: list[CopiedItem] = []
    missing: list[str] = []

    manuscript = revision_dir / "manuscript.pdf"
    if manuscript.is_file():
        copied.append(copy_file(manuscript, output_dir / "manuscript.pdf", "manuscript_pdf", root))
    else:
        missing.append("manuscript.pdf")

    article_pdf = revision_dir / "article" / "article.pdf"
    if article_pdf.is_file():
        copied.append(copy_file(article_pdf, output_dir / "article.pdf", "article_pdf", root))
        article_meta_dir = output_dir / "article"
        for article_name in ["article.md", "article_build_report.json"]:
            article_source = revision_dir / "article" / article_name
            if article_source.is_file():
                copied.append(copy_file(article_source, article_meta_dir / article_name, "article_build_artifact", root))
    elif require_article_pdf:
        missing.append("article.pdf")

    figures_dir = revision_dir / "figures"
    tables_dir = revision_dir / "tables"
    copied.extend(copy_tree(figures_dir, output_dir / "figures", "figure", root))
    copied.extend(copy_tree(tables_dir, output_dir / "tables", "table", root))
    if not figures_dir.is_dir():
        missing.append("figures/")
        (output_dir / "figures").mkdir(exist_ok=True)
    if not tables_dir.is_dir():
        missing.append("tables/")
        (output_dir / "tables").mkdir(exist_ok=True)

    source_root = output_dir / "source_code"
    source_root.mkdir(exist_ok=True)
    source_paths = source_files(revision_dir)
    if not source_paths:
        missing.append("source_code/")
    for source in source_paths:
        destination = source_root / source.relative_to(revision_dir)
        copied.append(copy_file(source, destination, "source_code", root))

    record = PackageRecord(
        run_id=run_id,
        submission=submission,
        revision=revision,
        source_revision=rel(revision_dir, root),
        output_folder=rel(output_dir, root),
        require_article_pdf=require_article_pdf,
        copied_items=copied,
        missing_expected_items=missing,
    )
    copied.append(write_readme(output_dir, record, root))
    record.copied_items = copied

    manifest = output_dir / "human_readable_package_manifest.json"
    manifest.write_text(
        json.dumps(
            {
                **asdict(record),
                "created_at_utc": datetime.now(timezone.utc).isoformat(),
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    return record


def main() -> int:
    parser = argparse.ArgumentParser(description="Package human-readable Research Arena revision outputs.")
    parser.add_argument("--root", default=".", help="Research Arena repository root.")
    parser.add_argument("--run-id", required=True, help="Run id under submissions/<run-id>.")
    parser.add_argument(
        "--submissions-root",
        help="Override the submissions root. Defaults to submissions/<run-id>; useful for packaged examples.",
    )
    parser.add_argument(
        "--output-root",
        help="Output root. Defaults to human_readable_outputs/<run-id>.",
    )
    parser.add_argument("--latest-only", action="store_true", help="Package only the latest revision for each submission.")
    parser.add_argument("--replace", action="store_true", help="Replace existing generated output folders.")
    args = parser.parse_args()

    root = repo_root_from(Path(args.root))
    submissions_root = Path(args.submissions_root).resolve() if args.submissions_root else root / "submissions" / args.run_id
    if not submissions_root.is_dir():
        raise SystemExit(f"Missing submissions folder: {rel(submissions_root, root)}")

    output_root = Path(args.output_root).resolve() if args.output_root else root / "human_readable_outputs" / args.run_id
    output_root.mkdir(parents=True, exist_ok=True)

    revisions = revision_dirs(submissions_root, args.latest_only)
    if not revisions:
        raise SystemExit(f"No revision folders found under {rel(submissions_root, root)}")

    require_article_pdf = contract_requires_article_pdf(root, args.run_id)
    records = [package_revision(revision, output_root, root, args.replace, require_article_pdf) for revision in revisions]
    index = {
        "run_id": args.run_id,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "latest_only": bool(args.latest_only),
        "output_root": rel(output_root, root),
        "packages": [asdict(record) for record in records],
    }
    (output_root / "index.json").write_text(json.dumps(index, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(f"Packaged {len(records)} revision(s) under {rel(output_root, root)}")
    for record in records:
        status = "ok" if not record.missing_expected_items else "missing: " + ", ".join(record.missing_expected_items)
        print(f"- {record.submission}/{record.revision}: {record.output_folder} ({status})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
