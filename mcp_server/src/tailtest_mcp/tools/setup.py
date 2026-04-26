"""tailtest_setup tool.

Bootstrap entry point. The user invokes this via natural language
("set up tailtest in this project") OR a slash command -- the tool writes
the `.clinerules/` rule pack, the `.clinerules/workflows/` slash workflows,
and seeds Memory Bank with `tailtestContext.md`. Returns a structured
report of what was written, what was skipped, and the user-facing next
steps (Cline does not auto-reload .clinerules mid-conversation).
"""

from __future__ import annotations

import datetime as _dt
import json
import os
import shutil
import sys
from typing import Any

# vendored lib path
_LIB_PATH = os.path.join(os.path.dirname(__file__), "..", "lib")
if _LIB_PATH not in sys.path:
    sys.path.insert(0, _LIB_PATH)

from filter import detect_language  # noqa: E402

from .. import __version__  # noqa: E402  -- intentional package-relative


# Path to the templates directory bundled inside the package
_TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "..", "templates")


# Memory Bank: the documented 6 core files (per Cline convention)
MEMORY_BANK_CORE_FILES = (
    "projectbrief.md",
    "productContext.md",
    "activeContext.md",
    "systemPatterns.md",
    "techContext.md",
    "progress.md",
)


def _detect_runner(language: str, project_root: str) -> str:
    """Pick a sensible default runner per language. V14.3 lightweight."""
    if language == "python":
        if os.path.exists(os.path.join(project_root, "pyproject.toml")):
            return "pytest"
        if os.path.exists(os.path.join(project_root, "setup.py")):
            return "pytest"
        return "pytest"
    if language in ("typescript", "javascript"):
        pkg = os.path.join(project_root, "package.json")
        if os.path.exists(pkg):
            try:
                with open(pkg) as f:
                    text = f.read().lower()
                if "vitest" in text:
                    return "vitest"
                if "jest" in text:
                    return "jest"
            except OSError:
                pass
        return "vitest"
    if language == "go":
        return "go test"
    if language == "ruby":
        return "rspec"
    if language == "rust":
        return "cargo test"
    if language == "java":
        return "mvn test"
    if language == "kotlin":
        return "gradle test"
    if language == "csharp":
        return "dotnet test"
    if language == "php":
        return "phpunit"
    return "unknown"


def _detect_framework(language: str, project_root: str) -> str | None:
    """Match the lightweight detection used by pick_template / scenario_plan."""
    if language == "python":
        for f in ("requirements.txt", "pyproject.toml", "setup.py"):
            path = os.path.join(project_root, f)
            if os.path.exists(path):
                try:
                    with open(path) as fh:
                        text = fh.read().lower()
                    if "fastapi" in text:
                        return "fastapi"
                    if "flask" in text:
                        return "flask"
                    if "django" in text:
                        return "django"
                except OSError:
                    pass
    elif language == "typescript":
        pkg = os.path.join(project_root, "package.json")
        if os.path.exists(pkg):
            try:
                with open(pkg) as fh:
                    text = fh.read().lower()
                if "@nestjs/" in text:
                    return "nestjs"
            except OSError:
                pass
    elif language == "java":
        for f in ("pom.xml", "build.gradle"):
            path = os.path.join(project_root, f)
            if os.path.exists(path):
                try:
                    with open(path) as fh:
                        text = fh.read().lower()
                    if "spring-boot" in text or "springframework" in text:
                        return "spring"
                except OSError:
                    pass
    return None


def _detect_test_dir(language: str, project_root: str) -> str:
    """Default test directory per language. V14.3 lightweight."""
    if language == "python":
        if os.path.isdir(os.path.join(project_root, "tests")):
            return "tests/"
        if os.path.isdir(os.path.join(project_root, "test")):
            return "test/"
        return "tests/"
    if language in ("typescript", "javascript"):
        if os.path.isdir(os.path.join(project_root, "__tests__")):
            return "__tests__/"
        if os.path.isdir(os.path.join(project_root, "tests")):
            return "tests/"
        return "__tests__/"
    if language == "go":
        return "(co-located)"
    if language == "java":
        return "src/test/java/"
    if language == "kotlin":
        return "src/test/kotlin/"
    if language == "csharp":
        return "tests/"
    return "tests/"


def _detect_project_language(project_root: str) -> str:
    """Pick the dominant language by counting source files. V14.3 lightweight."""
    counts: dict[str, int] = {}
    for root, dirs, files in os.walk(project_root):
        # Skip noise dirs
        dirs[:] = [
            d
            for d in dirs
            if d not in {"node_modules", ".venv", "venv", ".git", "dist", "build", "__pycache__", "target"}
        ]
        for f in files:
            lang = detect_language(f)
            if lang:
                counts[lang] = counts.get(lang, 0) + 1
        if sum(counts.values()) > 200:
            break
    if not counts:
        return "unknown"
    return max(counts.items(), key=lambda kv: kv[1])[0]


def _copy_templates(template_subdir: str, dest_dir: str, results: dict[str, list[str]]) -> None:
    """Copy each .md file from the template subdirectory to dest_dir.

    Records each file in results['written'] or results['skipped'] (when the
    destination file already exists).
    """
    src_dir = os.path.join(_TEMPLATES_DIR, template_subdir)
    if not os.path.isdir(src_dir):
        results["skipped"].append(f"{template_subdir}/ (no templates bundled)")
        return
    os.makedirs(dest_dir, exist_ok=True)
    for fname in os.listdir(src_dir):
        if not fname.endswith(".md"):
            continue
        src = os.path.join(src_dir, fname)
        dst = os.path.join(dest_dir, fname)
        if os.path.exists(dst):
            results["skipped"].append(f"{dest_dir}/{fname} (exists; not overwritten)")
            continue
        shutil.copyfile(src, dst)
        results["written"].append(f"{dest_dir}/{fname}")


def _write_tailtest_context(
    project_root: str,
    language: str,
    framework: str | None,
    runner: str,
    test_dir: str,
    mode: str,
    results: dict[str, list[str]],
) -> None:
    """Seed Memory Bank with `tailtestContext.md`.

    Detects whether Memory Bank exists. If yes, writes alongside the 6 core
    files as a 7th file. If not, creates `memory-bank/` and writes only
    `tailtestContext.md` (we do not initialise the full Memory Bank to avoid
    cluttering projects that did not opt in).
    """
    mb_dir = os.path.join(project_root, "memory-bank")
    target = os.path.join(mb_dir, "tailtestContext.md")
    if os.path.exists(target):
        results["skipped"].append(f"{target} (exists; not overwritten)")
        return

    template_path = os.path.join(_TEMPLATES_DIR, "memory-bank", "tailtestContext.md")
    if not os.path.exists(template_path):
        results["skipped"].append(f"memory-bank/tailtestContext.md (template missing)")
        return

    with open(template_path) as f:
        content = f.read()

    content = (
        content.replace("{{detection_date}}", _dt.date.today().isoformat())
        .replace("{{plugin_version}}", __version__)
        .replace("{{mode}}", mode)
        .replace("{{language}}", language)
        .replace("{{framework}}", framework or "(none detected)")
        .replace("{{runner}}", runner)
        .replace("{{test_dir}}", test_dir)
        .replace("{{depth}}", "standard")
        .replace("{{baseline_count}}", "0")
    )

    os.makedirs(mb_dir, exist_ok=True)
    with open(target, "w") as f:
        f.write(content)
    results["written"].append(f"{target}")


def _write_tailtest_state(
    project_root: str,
    mode: str,
    results: dict[str, list[str]],
) -> None:
    """Initialise `.tailtest/config.json` and `.tailtest/session.json`."""
    tt_dir = os.path.join(project_root, ".tailtest")
    os.makedirs(tt_dir, exist_ok=True)

    config_path = os.path.join(tt_dir, "config.json")
    if not os.path.exists(config_path):
        with open(config_path, "w") as f:
            json.dump({"depth": "standard", "mode": mode}, f, indent=2)
        results["written"].append(f"{config_path}")
    else:
        results["skipped"].append(f"{config_path} (exists; not overwritten)")

    session_path = os.path.join(tt_dir, "session.json")
    if not os.path.exists(session_path):
        with open(session_path, "w") as f:
            json.dump(
                {
                    "pending_files": [],
                    "generated_tests": {},
                    "fix_attempts": {},
                    "deferred_failures": [],
                    "runners": {},
                    "ramp_up": False,
                    "paused": False,
                    "mode": mode,
                },
                f,
                indent=2,
            )
        results["written"].append(f"{session_path}")
    else:
        results["skipped"].append(f"{session_path} (exists; not overwritten)")


def setup(
    project_root: str | None = None,
    mode: str = "manual",
) -> dict[str, Any]:
    """Bootstrap tailtest in a Cline project.

    Args:
        project_root: project directory. Defaults to cwd.
        mode: "manual" (default) or "auto". Manual is safer for first-time
            users; auto requires Cline auto-approve enabled. The user can
            switch modes later via `/tailtest-mode auto` or `/tailtest-mode manual`.

    Returns:
        Dict with detected stack info, lists of files written and skipped,
        next-steps prose for the user, and a clear "reload required" warning.
    """
    project_root = project_root or os.getcwd()
    project_root = os.path.abspath(project_root)

    if mode not in ("manual", "auto"):
        raise ValueError(f"Invalid mode {mode!r}. Use 'manual' or 'auto'.")

    # Detection
    language = _detect_project_language(project_root)
    framework = _detect_framework(language, project_root) if language != "unknown" else None
    runner = _detect_runner(language, project_root) if language != "unknown" else "unknown"
    test_dir = _detect_test_dir(language, project_root)

    results: dict[str, list[str]] = {"written": [], "skipped": []}

    # 1. Write the .clinerules/ pack
    _copy_templates("clinerules", os.path.join(project_root, ".clinerules"), results)

    # 2. Write the .clinerules/workflows/ slash workflows
    _copy_templates(
        "workflows", os.path.join(project_root, ".clinerules", "workflows"), results
    )

    # 3. Seed Memory Bank tailtestContext.md
    _write_tailtest_context(
        project_root, language, framework, runner, test_dir, mode, results
    )

    # 4. Initialise .tailtest/ state files
    _write_tailtest_state(project_root, mode, results)

    next_steps = (
        f"Setup complete. Detected {language}"
        + (f" with {framework}" if framework else "")
        + f". Mode: {mode}.\n\n"
        "**Important:** Cline does not auto-reload .clinerules mid-conversation. "
        "Start a new conversation (or reload the window) to activate tailtest.\n\n"
        + (
            "After reload, edit any source file and tailtest will fire automatically.\n"
            "Auto mode requires Cline auto-approve enabled for: 'Edit files (workspace)', "
            "'Execute safe commands', 'Use MCP servers'.\n"
            if mode == "auto"
            else "After reload, run `/tailtest-test <file>` to test a specific file. "
            "To switch to auto mode later, run `/tailtest-mode auto`.\n"
        )
        + "\nFor advanced features:\n"
        "- `/tailtest hunt <file>` -- one-shot adversarial pass on a specific file\n"
        "- Set `\"depth\": \"adversarial\"` in `.tailtest/config.json` for project-wide bug-hunting"
    )

    memory_bank_existed = all(
        os.path.exists(os.path.join(project_root, "memory-bank", f))
        for f in MEMORY_BANK_CORE_FILES
    )

    return {
        "project_root": project_root,
        "detected": {
            "language": language,
            "framework": framework,
            "runner": runner,
            "test_dir": test_dir,
        },
        "mode": mode,
        "memory_bank_pre_existed": memory_bank_existed,
        "files_written": results["written"],
        "files_skipped": results["skipped"],
        "reload_required": True,
        "next_steps": next_steps,
    }
