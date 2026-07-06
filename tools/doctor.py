#!/usr/bin/env python3
"""User-facing dependency doctor for Research Arena.

This script sits above ``check_render_toolchain.py``. The checker stays
deterministic and non-installing; the doctor explains the difference between
tools staged beside the repo, tools installed on the machine, and tools visible
to the runtime that Research Arena will actually use.
"""

from __future__ import annotations

import argparse
import json
import os
import shlex
import shutil
import subprocess
from pathlib import Path

import check_render_toolchain as render_tools


BREW_TOOL_MAP = {
    "pdfinfo": "poppler",
    "pdftoppm": "poppler",
    "pdftotext": "poppler",
    "qpdf": "qpdf",
    "fc-match": "fontconfig",
}


def command_line(command: list[str]) -> str:
    return " ".join(shlex.quote(part) for part in command)


def status_word(ok: bool) -> str:
    return "ok" if ok else "missing"


def command_by_name(report: dict[str, object]) -> dict[str, dict[str, object]]:
    return {
        str(item["name"]): item
        for item in report.get("commands", [])  # type: ignore[union-attr]
        if isinstance(item, dict)
    }


def print_staged_tools(report: dict[str, object]) -> None:
    staged = report.get("staged_tools", {})
    if not isinstance(staged, dict):
        staged = {}
    print("Staged Tools")
    folder = staged.get("required_tools_folder")
    pandoc = staged.get("local_pandoc")
    basictex_pkg = staged.get("basictex_package")
    basictex_installed = bool(staged.get("basictex_installed"))
    conda_env = staged.get("conda_env")
    conda_bin = staged.get("conda_env_bin")
    print(f"  [{status_word(bool(folder))}] required tools folder: {folder or 'not found'}")
    print(f"  [{status_word(bool(pandoc))}] local Pandoc binary: {pandoc or 'not staged'}")
    print(f"  [{status_word(bool(basictex_pkg))}] BasicTeX package: {basictex_pkg or 'not staged'}")
    print(f"  [{status_word(basictex_installed)}] BasicTeX installed: {'yes' if basictex_installed else 'no'}")
    if conda_env:
        print(f"  [{status_word(bool(conda_bin))}] conda runtime {conda_env}: {conda_bin or 'not found'}")


def print_toolchain(report: dict[str, object], title: str) -> None:
    print(title)
    print(f"  status: {report.get('status')}")
    runtime = report.get("runtime", {})
    if isinstance(runtime, dict):
        mode = runtime.get("mode")
        conda_env = runtime.get("conda_env")
        if conda_env:
            print(f"  runtime: {mode} ({conda_env})")
        elif mode:
            print(f"  runtime: {mode}")

    for item in report.get("commands", []):  # type: ignore[union-attr]
        if not isinstance(item, dict):
            continue
        label = status_word(bool(item.get("found")))
        print(f"  [{label}] {item.get('name')}: {item.get('path') or item.get('error')}")

    missing_packages = report.get("missing_latex_packages", [])
    if missing_packages:
        print("  missing LaTeX packages:")
        for package in missing_packages:  # type: ignore[union-attr]
            print(f"    - {package}")


def unique_preserving_order(values: list[str]) -> list[str]:
    return list(dict.fromkeys(values))


def fix_commands(root: Path, report: dict[str, object], conda_env: str | None) -> list[list[str]]:
    commands = command_by_name(report)
    missing_commands = [str(name) for name in report.get("missing_commands", [])]  # type: ignore[union-attr]
    missing_packages = [str(name) for name in report.get("missing_latex_packages", [])]  # type: ignore[union-attr]
    staged = report.get("staged_tools", {})
    if not isinstance(staged, dict):
        staged = {}

    planned: list[list[str]] = []
    basictex_pkg = staged.get("basictex_package")
    if "xelatex" in missing_commands and basictex_pkg:
        planned.append(["sudo", "installer", "-pkg", str(basictex_pkg), "-target", "/"])

    xelatex_found = bool(commands.get("xelatex", {}).get("found"))
    if xelatex_found and ("latexmk" in missing_commands or missing_packages):
        env, _ = render_tools.augmented_env(root, conda_env)
        tlmgr = shutil.which("tlmgr", path=env.get("PATH")) or "/Library/TeX/texbin/tlmgr"
        packages: list[str] = []
        if "latexmk" in missing_commands:
            packages.append("latexmk")
        packages.extend(render_tools.tex_package_install_names(missing_packages))
        if packages:
            planned.append(["sudo", tlmgr, "install", *unique_preserving_order(packages)])

    brew_packages = [BREW_TOOL_MAP[name] for name in missing_commands if name in BREW_TOOL_MAP]
    if brew_packages:
        brew = shutil.which("brew") or "/opt/homebrew/bin/brew"
        planned.append([brew, "install", *unique_preserving_order(sorted(brew_packages))])

    if "pandoc" in missing_commands and not staged.get("local_pandoc"):
        brew = shutil.which("brew") or "/opt/homebrew/bin/brew"
        planned.append([brew, "install", "pandoc"])

    return planned


def print_fix_plan(commands: list[list[str]], apply: bool) -> None:
    print("Fix Plan")
    if not commands:
        print("  No missing render dependencies detected.")
        return
    if apply:
        print("  Applying these commands:")
    else:
        print("  Dry run. Re-run with `--fix --apply` to execute these commands:")
    for command in commands:
        print(f"  - {command_line(command)}")


def run_fix_commands(commands: list[list[str]]) -> int:
    for command in commands:
        print()
        print(f"Running: {command_line(command)}")
        completed = subprocess.run(command, check=False)
        if completed.returncode != 0:
            print(f"Command failed with exit code {completed.returncode}: {command_line(command)}")
            return completed.returncode
    return 0


def write_run_report(root: Path, run_id: str, report: dict[str, object]) -> Path:
    output_path = root / "runs" / run_id / "render_toolchain_report.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return output_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Check and explain Research Arena rendering dependencies.")
    parser.add_argument("--root", default=".", help="Research Arena repository root.")
    parser.add_argument(
        "--conda-env",
        default=os.environ.get("RESEARCH_ARENA_CONDA_ENV", "ag"),
        help="Conda environment used by the run. Use 'none' to check only the current shell.",
    )
    parser.add_argument("--fix", action="store_true", help="Print a concrete fix plan for missing dependencies.")
    parser.add_argument("--apply", action="store_true", help="Execute the fix plan. Requires --fix.")
    parser.add_argument("--run-id", help="Run id for --write-default output.")
    parser.add_argument("--write-default", action="store_true", help="Write runs/<run-id>/render_toolchain_report.json from the runtime report.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable doctor output.")
    args = parser.parse_args()

    if args.apply and not args.fix:
        raise SystemExit("--apply requires --fix")

    root = render_tools.repo_root_from(Path(args.root))
    conda_env = render_tools.normalize_conda_env(args.conda_env)
    system_report = render_tools.build_report(root, None)
    runtime_report = render_tools.build_report(root, conda_env)
    planned_commands = fix_commands(root, runtime_report, conda_env) if args.fix else []

    payload = {
        "doctor": "research-arena-dependency-doctor",
        "root": str(root),
        "system_report": system_report,
        "runtime_report": runtime_report,
        "fix_plan": [command_line(command) for command in planned_commands],
    }

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print("Research Arena Dependency Doctor")
        print(f"Root: {root}")
        print()
        print_staged_tools(runtime_report)
        print()
        print_toolchain(system_report, "Installed Toolchain")
        print()
        print_toolchain(runtime_report, "Runtime Toolchain")
        print()
        if runtime_report.get("status") == "pass":
            print("Result: runtime dependencies are ready.")
        else:
            print("Result: runtime dependencies are incomplete.")
        if args.fix:
            print()
            print_fix_plan(planned_commands, args.apply)

    if args.write_default:
        if not args.run_id:
            raise SystemExit("--write-default requires --run-id")
        output_path = write_run_report(root, args.run_id, runtime_report)
        if not args.json:
            print()
            print(f"Wrote runtime report: {output_path}")

    if args.apply and planned_commands:
        apply_status = run_fix_commands(planned_commands)
        if apply_status != 0:
            return apply_status
        refreshed = render_tools.build_report(root, conda_env)
        if not args.json:
            print()
            print_toolchain(refreshed, "Runtime Toolchain After Fix")
        return 0 if refreshed.get("status") == "pass" else 2

    return 0 if runtime_report.get("status") == "pass" else 2


if __name__ == "__main__":
    raise SystemExit(main())
