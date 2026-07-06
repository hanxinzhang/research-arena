#!/usr/bin/env python3
"""Check the local manuscript rendering and PDF QA toolchain.

The checker is intentionally deterministic. It does not install anything; it
reports what is available, where it was found, and how to install missing
free/open-source tools.
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import re
import shutil
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path


REQUIRED_COMMANDS = [
    ("pandoc", ["--version"], "Markdown/LaTeX conversion"),
    ("xelatex", ["--version"], "XeLaTeX PDF engine with fontspec support"),
    ("latexmk", ["-v"], "Reliable multi-pass LaTeX build driver"),
    ("pdfinfo", ["-v"], "Poppler PDF metadata inspection"),
    ("pdftoppm", ["-v"], "Poppler PDF-to-PNG rendering for visual QA"),
    ("pdftotext", ["-v"], "Poppler PDF text extraction for QA"),
    ("qpdf", ["--version"], "PDF structural validation"),
    ("fc-match", ["--version"], "fontconfig font discovery"),
]

REQUIRED_LATEX_PACKAGES = [
    "amsmath.sty",
    "amssymb.sty",
    "mathtools.sty",
    "booktabs.sty",
    "caption.sty",
    "fancyhdr.sty",
    "float.sty",
    "fontspec.sty",
    "geometry.sty",
    "graphicx.sty",
    "hyperref.sty",
    "lineno.sty",
    "microtype.sty",
    "sansmath.sty",
    "titlesec.sty",
    "xcolor.sty",
]

LATEX_PACKAGE_INSTALL_NAMES = {
    "amsmath.sty": "amsmath",
    "amssymb.sty": "amsmath",
    "mathtools.sty": "mathtools",
    "booktabs.sty": "booktabs",
    "caption.sty": "caption",
    "fancyhdr.sty": "fancyhdr",
    "float.sty": "float",
    "fontspec.sty": "fontspec",
    "geometry.sty": "geometry",
    "graphicx.sty": "graphics",
    "hyperref.sty": "hyperref",
    "lineno.sty": "lineno",
    "microtype.sty": "microtype",
    "sansmath.sty": "sansmath",
    "titlesec.sty": "titlesec",
    "xcolor.sty": "xcolor",
}


@dataclass
class CommandCheck:
    name: str
    purpose: str
    found: bool
    path: str | None
    version: str | None
    error: str | None


@dataclass
class LatexPackageCheck:
    name: str
    found: bool
    path: str | None


def normalize_conda_env(value: str | None) -> str | None:
    if not value:
        return None
    value = value.strip()
    if not value or value.lower() in {"none", "current", "false", "0"}:
        return None
    return value


def repo_root_from(start: Path) -> Path:
    start = start.resolve()
    for parent in [start, *start.parents]:
        if (parent / "program.md").is_file() and (parent / "agents").is_dir():
            return parent
    return start


def conda_env_bin_path(env_name: str | None) -> Path | None:
    env_name = normalize_conda_env(env_name)
    if not env_name:
        return None

    candidates: list[Path] = []
    conda = shutil.which("conda")
    if conda:
        try:
            completed = subprocess.run(
                [conda, "info", "--base"],
                check=False,
                capture_output=True,
                text=True,
                timeout=20,
            )
        except Exception:
            completed = None
        if completed and completed.returncode == 0:
            base = Path(completed.stdout.strip())
            candidates.append(base / "bin" if env_name == "base" else base / "envs" / env_name / "bin")

    for base in [
        Path("/opt/anaconda3"),
        Path("/opt/miniconda3"),
        Path.home() / "anaconda3",
        Path.home() / "miniconda3",
    ]:
        candidates.append(base / "bin" if env_name == "base" else base / "envs" / env_name / "bin")

    for candidate in candidates:
        if candidate.is_dir():
            return candidate
    return None


def candidate_tool_paths(root: Path, conda_env: str | None = None) -> list[Path]:
    paths: list[Path] = []
    required_tools = root.parent / "required tools"
    conda_bin = conda_env_bin_path(conda_env)
    candidates = [
        required_tools / "pandoc-3.10-arm64" / "bin",
        Path("/usr/local/texlive/2026basic/bin/universal-darwin"),
        Path("/Library/TeX/texbin"),
        conda_bin,
        Path("/opt/homebrew/bin"),
        Path("/usr/local/bin"),
    ]
    for path in candidates:
        if path and path.is_dir() and path not in paths:
            paths.append(path)
    return paths


def augmented_env(root: Path, conda_env: str | None = None) -> tuple[dict[str, str], list[str]]:
    env = os.environ.copy()
    extra_paths = [str(path) for path in candidate_tool_paths(root, conda_env)]
    current_path = env.get("PATH", "")
    env["PATH"] = os.pathsep.join([*extra_paths, current_path]) if extra_paths else current_path
    required_tools = root.parent / "required tools"
    if required_tools.is_dir():
        env.setdefault("XDG_CACHE_HOME", str(required_tools / ".cache"))
        env.setdefault("MPLCONFIGDIR", str(required_tools / ".cache" / "matplotlib"))
    return env, extra_paths


def run_version(command: str, args: list[str], env: dict[str, str]) -> tuple[str | None, str | None]:
    try:
        completed = subprocess.run(
            [command, *args],
            check=False,
            capture_output=True,
            text=True,
            env=env,
            timeout=20,
        )
    except Exception as exc:
        return None, str(exc)
    output = (completed.stdout + "\n" + completed.stderr).strip()
    if completed.returncode != 0 and not output:
        return None, f"exit code {completed.returncode}"
    lines = [line for line in output.splitlines() if line.strip()]
    return "\n".join(lines[:3]) if lines else None, None


def check_command(name: str, args: list[str], purpose: str, env: dict[str, str]) -> CommandCheck:
    path = shutil.which(name, path=env.get("PATH"))
    if not path:
        return CommandCheck(name=name, purpose=purpose, found=False, path=None, version=None, error="not found on PATH")
    version, error = run_version(path, args, env)
    return CommandCheck(name=name, purpose=purpose, found=True, path=path, version=version, error=error)


def check_latex_package(name: str, env: dict[str, str]) -> LatexPackageCheck:
    kpsewhich = shutil.which("kpsewhich", path=env.get("PATH"))
    if not kpsewhich:
        return LatexPackageCheck(name=name, found=False, path=None)
    completed = subprocess.run(
        [kpsewhich, name],
        check=False,
        capture_output=True,
        text=True,
        env=env,
        timeout=20,
    )
    path = completed.stdout.strip()
    return LatexPackageCheck(name=name, found=completed.returncode == 0 and bool(path), path=path or None)


def staged_tool_status(root: Path, conda_env: str | None = None) -> dict[str, object]:
    required_tools = root.parent / "required tools"
    basictex_pkg = required_tools / "downloads" / "macos-arm64" / "BasicTeX.pkg"
    local_pandoc = required_tools / "pandoc-3.10-arm64" / "bin" / "pandoc"
    texlive_xelatex = Path("/usr/local/texlive/2026basic/bin/universal-darwin/xelatex")
    texbin_xelatex = Path("/Library/TeX/texbin/xelatex")
    conda_env = normalize_conda_env(conda_env)
    conda_bin = conda_env_bin_path(conda_env)
    return {
        "required_tools_folder": str(required_tools) if required_tools.is_dir() else None,
        "local_pandoc": str(local_pandoc) if local_pandoc.is_file() else None,
        "basictex_package": str(basictex_pkg) if basictex_pkg.is_file() else None,
        "basictex_installed": texlive_xelatex.is_file() or texbin_xelatex.exists(),
        "texlive_xelatex": str(texlive_xelatex) if texlive_xelatex.is_file() else None,
        "texbin_xelatex": str(texbin_xelatex) if texbin_xelatex.exists() else None,
        "conda_env": conda_env,
        "conda_env_bin": str(conda_bin) if conda_bin else None,
    }


def tool_path(commands: list[CommandCheck], name: str) -> str | None:
    for command in commands:
        if command.name == name:
            return command.path
    return None


def tex_package_install_names(missing_packages: list[str]) -> list[str]:
    names = [LATEX_PACKAGE_INSTALL_NAMES.get(name, name.removesuffix(".sty")) for name in missing_packages]
    return sorted(dict.fromkeys(names))


def sanitize_report_paths(value: object, root: Path) -> object:
    if isinstance(value, dict):
        return {key: sanitize_report_paths(item, root) for key, item in value.items()}
    if isinstance(value, list):
        return [sanitize_report_paths(item, root) for item in value]
    if not isinstance(value, str):
        return value

    replacements = [
        ((root.parent / "required tools").resolve().as_posix(), "<required_tools>"),
        (root.resolve().as_posix(), "<research_arena_root>"),
        (Path.home().resolve().as_posix(), "<home>"),
    ]
    text = value
    for source, replacement in sorted(set(replacements), key=lambda item: len(item[0]), reverse=True):
        if source:
            text = text.replace(source, replacement)
    text = re.sub(r"/private/var/folders/[^\s\"']+", "<local_temp>", text)
    text = re.sub(r"/var/folders/[^\s\"']+", "<local_temp>", text)
    text = re.sub(r"/private/tmp/[^\s\"']+", "<local_temp>", text)
    text = re.sub(r"/tmp/[^\s\"']+", "<local_temp>", text)
    return text


def installation_hints(
    root: Path,
    commands: list[CommandCheck],
    missing_commands: list[str],
    missing_packages: list[str],
    env: dict[str, str],
    conda_env: str | None = None,
) -> list[str]:
    hints: list[str] = []
    required_tools = root.parent / "required tools"
    basictex = required_tools / "downloads" / "macos-arm64" / "BasicTeX.pkg"
    xelatex_path = tool_path(commands, "xelatex")
    tlmgr = shutil.which("tlmgr", path=env.get("PATH")) or "/Library/TeX/texbin/tlmgr"
    tex_install_names = tex_package_install_names(missing_packages)

    if "xelatex" in missing_commands:
        if basictex.is_file():
            hints.append(f"Install BasicTeX from `{basictex}` to provide XeLaTeX and core TeX packages.")
        else:
            hints.append("Install BasicTeX or TeX Live to provide XeLaTeX and core TeX packages.")

    if xelatex_path and ("latexmk" in missing_commands or tex_install_names):
        packages = ["latexmk"] if "latexmk" in missing_commands else []
        packages.extend(tex_install_names)
        packages = sorted(dict.fromkeys(packages))
        hints.append(f"Install missing TeX packages: `sudo {tlmgr} install {' '.join(packages)}`.")

    brew_packages: list[str] = []
    if any(name in missing_commands for name in ["pdfinfo", "pdftoppm", "pdftotext"]):
        brew_packages.append("poppler")
    if "qpdf" in missing_commands:
        brew_packages.append("qpdf")
    if "fc-match" in missing_commands:
        brew_packages.append("fontconfig")
    if brew_packages:
        hints.append(f"Install missing PDF QA tools with Homebrew: `brew install {' '.join(sorted(dict.fromkeys(brew_packages)))}`.")

    if "pdftotext" in missing_commands and not normalize_conda_env(conda_env):
        hints.append("If you run Research Arena in a conda environment, rerun this checker with `--conda-env <env_name>`.")

    if "pandoc" in missing_commands:
        local_pandoc = required_tools / "pandoc-3.10-arm64" / "bin" / "pandoc"
        if local_pandoc.is_file():
            hints.append("Run `source \"../required tools/scripts/env.sh\"` or add the staged Pandoc binary to PATH.")
        else:
            hints.append("Download Pandoc or install it with Homebrew/conda before rendering manuscripts.")
    if not hints:
        hints.append("No missing tools detected.")
    return hints


def build_report(root: Path, conda_env: str | None = None) -> dict[str, object]:
    conda_env = normalize_conda_env(conda_env)
    env, extra_paths = augmented_env(root, conda_env)
    commands = [check_command(name, args, purpose, env) for name, args, purpose in REQUIRED_COMMANDS]
    missing_commands = [item.name for item in commands if not item.found]

    latex_packages: list[LatexPackageCheck] = []
    if shutil.which("kpsewhich", path=env.get("PATH")):
        latex_packages = [check_latex_package(name, env) for name in REQUIRED_LATEX_PACKAGES]
    missing_packages = [item.name for item in latex_packages if not item.found]

    status = "pass" if not missing_commands and not missing_packages else "flagged"
    required_tools = root.parent / "required tools"
    report = {
        "checker": "research-arena-render-toolchain",
        "status": status,
        "runtime": {
            "mode": "conda" if conda_env else "current-shell",
            "conda_env": conda_env,
            "conda_env_bin": str(conda_env_bin_path(conda_env)) if conda_env_bin_path(conda_env) else None,
        },
        "platform": {
            "system": platform.system(),
            "machine": platform.machine(),
            "python": platform.python_version(),
        },
        "root": str(root),
        "required_tools_folder": str(required_tools) if required_tools.is_dir() else None,
        "staged_tools": staged_tool_status(root, conda_env),
        "path_prefixes_added": extra_paths,
        "commands": [asdict(item) for item in commands],
        "missing_commands": missing_commands,
        "latex_packages": [asdict(item) for item in latex_packages],
        "missing_latex_packages": missing_packages,
        "installation_hints": installation_hints(root, commands, missing_commands, missing_packages, env, conda_env),
        "notes": [
            "This checker only verifies the rendering/QA toolchain. It does not judge manuscript quality.",
            "Pandoc and XeLaTeX are required for publication-quality manuscript rendering unless the run contract explicitly allows a fallback renderer.",
            "Poppler, qpdf, and fontconfig are required for final PDF visual/text/font QA.",
        ],
    }
    return sanitize_report_paths(report, root)  # type: ignore[return-value]


def print_text_report(report: dict[str, object]) -> None:
    print(f"Research Arena render toolchain: {report['status']}")
    print(f"Root: {report['root']}")
    runtime = report.get("runtime", {})
    if isinstance(runtime, dict):
        mode = runtime.get("mode")
        conda_env = runtime.get("conda_env")
        if conda_env:
            print(f"Runtime: {mode} ({conda_env})")
        elif mode:
            print(f"Runtime: {mode}")
    required_tools = report.get("required_tools_folder")
    if required_tools:
        print(f"Required tools folder: {required_tools}")
    print()
    for item in report["commands"]:  # type: ignore[index]
        status = "ok" if item["found"] else "missing"
        print(f"[{status}] {item['name']}: {item.get('path') or item.get('error')}")
        if item.get("version"):
            print(str(item["version"]).splitlines()[0])
    missing_packages = report.get("missing_latex_packages", [])
    if missing_packages:
        print()
        print("Missing LaTeX packages:")
        for name in missing_packages:
            print(f"- {name}")
    print()
    print("Installation hints:")
    for hint in report["installation_hints"]:  # type: ignore[index]
        print(f"- {hint}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Check the Research Arena manuscript rendering toolchain.")
    parser.add_argument("--root", default=".", help="Research Arena repository root.")
    parser.add_argument("--run-id", help="Run id for --write-default output.")
    parser.add_argument("--output-json", help="Optional JSON report path.")
    parser.add_argument("--write-default", action="store_true", help="Write runs/<run-id>/render_toolchain_report.json.")
    parser.add_argument("--text", action="store_true", help="Print a concise human-readable report.")
    parser.add_argument("--json", action="store_true", help="Print the full JSON report to stdout.")
    parser.add_argument("--conda-env", help="Check with a conda environment's bin directory prepended to PATH; use 'none' for current shell only.")
    args = parser.parse_args()

    root = repo_root_from(Path(args.root))
    report = build_report(root, args.conda_env)

    output_path: Path | None = Path(args.output_json) if args.output_json else None
    if args.write_default:
        if not args.run_id:
            raise SystemExit("--write-default requires --run-id")
        output_path = root / "runs" / args.run_id / "render_toolchain_report.json"
    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    elif args.text or not output_path:
        print_text_report(report)
    return 0 if report["status"] == "pass" else 2


if __name__ == "__main__":
    raise SystemExit(main())
