"""tailtest_scenario_plan tool.

Returns structured scaffolding the agent uses to write its SCENARIO PLAN.
This tool does NOT generate the scenarios themselves -- it provides the
language / framework / depth / R15 policy context. The agent (LLM) does
the creative work of writing scenario lines using this context.

Design rationale: separating the policy layer (deterministic, in this tool)
from the creative layer (LLM) is what gives Cline integration its
reliability advantage over pure-rule-text approaches. Even if the agent
forgets details of R15, this tool always returns the correct adversarial
count requirement.
"""

from __future__ import annotations

import json
import os
import sys
from typing import Any

# vendored lib path -- mcp_server/src/lib is package-relative
_LIB_PATH = os.path.join(os.path.dirname(__file__), "..", "lib")
if _LIB_PATH not in sys.path:
    sys.path.insert(0, _LIB_PATH)

from filter import detect_language  # noqa: E402


# R15 policy: required adversarial count per depth tier
ADVERSARIAL_BY_DEPTH = {
    "simple": 0,
    "standard": 2,
    "thorough": 4,
    "adversarial": 8,  # min; max is 12
}

SCENARIO_COUNT_BY_DEPTH = {
    "simple": (2, 3),
    "standard": (5, 8),
    "thorough": (10, 15),
    "adversarial": (8, 12),
}

LANGUAGE_BASELINE = {
    "python": ["None input", "empty list/dict", "zero", "negative number", "wrong type passed"],
    "typescript": ["undefined", "null", "NaN", "wrong type", "empty string"],
    "javascript": ["undefined", "null", "NaN", "wrong type", "empty string"],
    "go": ["zero value", "empty struct", "nil pointer"],
    "ruby": ["nil", "empty array", "zero"],
    "java": ["null", "empty collection", "zero", "negative"],
    "kotlin": ["null", "empty collection", "zero", "negative", "Result.failure"],
    "csharp": [
        "null",
        "default(T)",
        "empty IEnumerable<T>",
        "ArgumentNullException on invalid input",
        "zero / negative numeric",
    ],
    "php": ["null", "empty array", "zero", "empty string"],
    "rust": ["empty input", "boundary values (0, u32::MAX or equivalent)"],
}

ADVERSARIAL_CATEGORIES = [
    "boundary inputs",
    "format / injection",
    "type confusion",
    "concurrent state",
    "time / locale edges",
    "error handling under partial failures",
    "resource exhaustion",
    "off-by-one logic",
]


def _read_depth(project_root: str) -> str:
    """Read depth from .tailtest/config.json. Defaults to 'standard'."""
    config_path = os.path.join(project_root, ".tailtest", "config.json")
    if os.path.exists(config_path):
        try:
            with open(config_path) as f:
                cfg = json.load(f)
            value = cfg.get("depth")
            if value in ADVERSARIAL_BY_DEPTH:
                return value
        except (json.JSONDecodeError, OSError):
            pass
    return "standard"


def _detect_framework(language: str, file_path: str, project_root: str) -> str | None:
    """Best-effort framework detection. Returns None when ambiguous.

    V14.1 keeps this lightweight; V14.2 expands to use lib.runners detection
    once the runner detection wiring is plumbed.
    """
    if language != "python":
        return None
    py_files_to_check = [
        os.path.join(project_root, "requirements.txt"),
        os.path.join(project_root, "pyproject.toml"),
    ]
    text = ""
    for f in py_files_to_check:
        if os.path.exists(f):
            try:
                with open(f) as fh:
                    text += fh.read().lower()
            except OSError:
                pass
    if "flask" in text:
        return "flask"
    if "fastapi" in text:
        return "fastapi"
    if "django" in text:
        return "django"
    return None


def _test_file_path(file_path: str, language: str, framework: str | None) -> str:
    """Default test file path per language conventions. Pre-V14.2 simple version."""
    base = os.path.basename(file_path)
    stem = os.path.splitext(base)[0]
    if language == "python":
        return os.path.join("tests", f"test_{stem}.py")
    if language in ("typescript", "javascript"):
        ext = ".tsx" if file_path.endswith(".tsx") else ".test.ts"
        return os.path.join("__tests__", f"{stem}{ext}")
    if language == "go":
        directory = os.path.dirname(file_path) or "."
        return os.path.join(directory, f"{stem}_test.go")
    if language in ("java", "kotlin"):
        ext = "kt" if language == "kotlin" else "java"
        return os.path.join("src", "test", language, f"{stem}Test.{ext}")
    if language == "csharp":
        return os.path.join("tests", f"{stem}Tests.cs")
    return os.path.join("tests", f"test_{stem}.{language}")


def scenario_plan(file_path: str, project_root: str | None = None) -> dict[str, Any]:
    """Return structured scaffolding the agent uses to write its SCENARIO PLAN.

    Args:
        file_path: relative or absolute path to the source file.
        project_root: project root for reading config.json. Defaults to cwd.

    Returns:
        Dict with: file_path, language, framework, depth, scenario_count_target,
        adversarial_count_required, adversarial_categories, language_baseline,
        framework_baseline, test_file_path, instructions.
    """
    project_root = project_root or os.getcwd()

    language = detect_language(file_path) or "unknown"
    framework = _detect_framework(language, file_path, project_root)
    depth = _read_depth(project_root)
    count_min, count_max = SCENARIO_COUNT_BY_DEPTH[depth]
    adv_required = ADVERSARIAL_BY_DEPTH[depth]
    test_path = _test_file_path(file_path, language, framework)

    instructions = (
        f"Generate a SCENARIO PLAN for {file_path}. "
        f"Depth is {depth}: produce {count_min} to {count_max} scenarios total. "
        f"R15 requires at least {adv_required} adversarial scenarios labeled "
        f"[adversarial: <category>]. Pick categories from the 8-category list "
        f"that genuinely apply to this file; document any skipped category with "
        f"a reason. Include the language baseline scenarios. "
    )
    if framework:
        instructions += (
            f"Include the {framework} framework baseline scenarios on top of the "
            f"language baseline. "
        )
    if depth == "simple":
        instructions += (
            "Note: at depth: simple, R15 does not apply -- generate happy-path "
            "scenarios only. "
        )

    return {
        "file_path": file_path,
        "language": language,
        "framework": framework,
        "depth": depth,
        "scenario_count_target": [count_min, count_max],
        "adversarial_count_required": adv_required,
        "adversarial_categories": ADVERSARIAL_CATEGORIES,
        "language_baseline": LANGUAGE_BASELINE.get(language, []),
        "framework_baseline": _framework_baseline(framework),
        "test_file_path": test_path,
        "instructions": instructions,
    }


def _framework_baseline(framework: str | None) -> list[str]:
    """Framework baseline scenarios from R2 templates."""
    if framework is None:
        return []
    if framework == "flask":
        return [
            "Route returns 200 on valid path",
            "404 on unknown route",
            "Blueprint registration binds the correct prefix",
            "test_client fixture used within app context",
            "Validation rejects bad input",
        ]
    if framework == "fastapi":
        return [
            "Valid request body returns expected response",
            "Missing required field returns 422",
            "Wrong field type returns 422",
            "Dependency override works in test (app.dependency_overrides)",
        ]
    if framework == "django":
        return [
            "Request with valid auth",
            "Request without auth (expect 403/redirect)",
            "Model field validation rejects invalid data",
            "URL routes to the correct view",
        ]
    return []
