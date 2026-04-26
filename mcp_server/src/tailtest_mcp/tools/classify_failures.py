"""tailtest_classify_failures tool.

Parses runner output (pytest, jest, mocha, etc.) into structured failure
records and applies a heuristic R12 classification. Returns scaffolding the
agent can verify or override; the agent makes the final R12 call.

Design rationale: R12 classification (real_bug vs environment vs test_bug) is
fundamentally a reasoning task, not pure pattern-matching. The tool gives
the agent a strong starting point so it does not have to parse runner
output from scratch each time, while preserving the agent's authority to
override the heuristic when context warrants.

Heuristics implemented:
- ImportError, ModuleNotFoundError, ConnectionError, subprocess errors -> environment
- AssertionError -> likely real_bug or test_bug (depends on traceback context)
- TypeError, AttributeError, KeyError -> likely real_bug
- pytest.fixture / setup errors -> test_bug or environment
"""

from __future__ import annotations

import re
from typing import Any


# Error patterns -> heuristic classification
ENV_ERRORS = {
    "ImportError",
    "ModuleNotFoundError",
    "ConnectionError",
    "ConnectionRefusedError",
    "ConnectionResetError",
    "TimeoutError",
    "FileNotFoundError",
    "PermissionError",
    "OSError",
}

LIKELY_REAL_BUG_ERRORS = {
    "AttributeError",
    "TypeError",
    "KeyError",
    "ValueError",
    "IndexError",
    "ZeroDivisionError",
    "RecursionError",
    "OverflowError",
}

# AssertionError is ambiguous: real_bug if assertion is on source behavior,
# test_bug if assertion is on test fixture / setup.
AMBIGUOUS_ERRORS = {
    "AssertionError",
}


# --- pytest output parsing ---

# Short summary line: "FAILED tests/test_x.py::test_name - ErrorType: message"
_PYTEST_SHORT_FAILURE_RE = re.compile(
    r"^FAILED\s+(?P<file>[^\s:]+)::(?P<test>\S+?)(?:\s+-\s+(?P<error_type>\w+)(?::\s*(?P<message>.+))?)?$",
    re.MULTILINE,
)

# Verbose / long traceback: file:line: in test_name
_PYTEST_TB_LINE_RE = re.compile(
    r"^(?P<file>[^\s:]+\.py):(?P<line>\d+):\s+in\s+(?P<test>\S+)$",
    re.MULTILINE,
)


def _heuristic_classification(
    error_type: str, message: str, traceback_text: str
) -> tuple[str, str]:
    """Apply heuristic R12 classification.

    Returns (classification, reason) where classification is one of:
    real_bug, environment, test_bug, unknown.
    """
    if error_type in ENV_ERRORS:
        return ("environment", f"{error_type} typically indicates a missing dependency or system resource")

    if error_type in LIKELY_REAL_BUG_ERRORS:
        # Refine: if the traceback shows the error originated in test fixture
        # setup, flip to test_bug.
        if traceback_text and any(
            marker in traceback_text
            for marker in ("conftest.py", "fixture", "setup_method", "setUp(")
        ):
            return (
                "test_bug",
                f"{error_type} originated in test fixture or setup, not source under test",
            )
        return (
            "real_bug",
            f"{error_type} typically indicates a bug in the source under test",
        )

    if error_type in AMBIGUOUS_ERRORS:
        # AssertionError: try to disambiguate from message.
        msg_lower = (message or "").lower()
        # Common test_bug signals
        if any(
            phrase in msg_lower
            for phrase in (
                "fixture not found",
                "expected fixture",
                "wrong expectation",
                "stub",
                "mock not configured",
            )
        ):
            return ("test_bug", "Assertion message indicates the test setup is wrong")
        # Common real_bug signals
        if any(
            phrase in msg_lower
            for phrase in (
                "expected ",
                "got ",
                "should",
                "to equal",
                "to be",
            )
        ):
            return (
                "real_bug",
                "Assertion compares actual vs expected behavior of the source",
            )
        return (
            "real_bug",
            "AssertionError defaults to real_bug when ambiguous (per CLAUDE.md / mdc rule)",
        )

    return ("unknown", f"No heuristic for {error_type}; agent must classify")


def _parse_pytest_failures(output: str) -> list[dict[str, Any]]:
    """Extract failures from pytest stdout / stderr.

    Recognizes the FAILED short-form summary as the primary signal.
    Returns one record per failure.
    """
    failures: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()

    for match in _PYTEST_SHORT_FAILURE_RE.finditer(output):
        file_path = match.group("file")
        test_name = match.group("test")
        key = (file_path, test_name)
        if key in seen:
            continue
        seen.add(key)

        error_type = match.group("error_type") or ""
        message = match.group("message") or ""
        # Look for a traceback block following the test name elsewhere in output
        traceback_text = _find_traceback_for(output, test_name)
        classification, reason = _heuristic_classification(
            error_type, message, traceback_text
        )
        failures.append(
            {
                "type": classification,
                "reason": reason,
                "test_name": test_name,
                "file": file_path,
                "line": _find_failure_line(traceback_text or "", file_path),
                "error_type": error_type,
                "message": message,
            }
        )

    return failures


def _find_traceback_for(output: str, test_name: str) -> str:
    """Best-effort: pull the traceback block associated with a given test."""
    # Look for a verbose section header: "_______________ test_name _______________"
    pattern = re.compile(
        rf"_+\s*{re.escape(test_name)}\s*_+\n(.*?)(?=\n_+|\Z)", re.DOTALL
    )
    m = pattern.search(output)
    return m.group(1) if m else ""


def _find_failure_line(traceback_text: str, source_file: str) -> int | None:
    """Best-effort: pull line number from traceback for the source file."""
    pattern = re.compile(
        rf"{re.escape(source_file)}:(\d+):"
    )
    m = pattern.search(traceback_text)
    return int(m.group(1)) if m else None


def _parse_jest_failures(output: str) -> list[dict[str, Any]]:
    """Extract failures from jest output. Recognizes FAIL block summaries."""
    failures: list[dict[str, Any]] = []
    # Jest FAIL line: "FAIL src/foo.test.ts ... (123 ms)"
    # Followed by failed test names: "  ● TestSuite > test name"
    fail_block_re = re.compile(
        r"FAIL\s+(?P<file>\S+\.(?:test|spec)\.(?:ts|js|tsx|jsx))",
        re.MULTILINE,
    )
    test_name_re = re.compile(r"●\s+(?:[\w\s]+>\s+)*(?P<test>[^\n]+)")

    for fm in fail_block_re.finditer(output):
        file_path = fm.group("file")
        # Find test names in the section after this FAIL marker
        section_start = fm.end()
        next_fail = fail_block_re.search(output, section_start)
        section_end = next_fail.start() if next_fail else len(output)
        section = output[section_start:section_end]
        for tm in test_name_re.finditer(section):
            test_name = tm.group("test").strip()
            # jest doesn't always surface error type cleanly; default heuristic
            failures.append(
                {
                    "type": "real_bug",
                    "reason": "AssertionError defaults to real_bug; agent should verify",
                    "test_name": test_name,
                    "file": file_path,
                    "line": None,
                    "error_type": "AssertionError",
                    "message": "",
                }
            )
    return failures


def classify_failures(runner_output: str, runner: str = "pytest") -> dict[str, Any]:
    """Parse runner output and return structured R12-classified failures.

    Args:
        runner_output: stdout (and optionally stderr) from the test runner.
        runner: one of "pytest", "jest", "mocha", "vitest". Defaults to pytest.

    Returns:
        Dict with `failures` (list of failure records), `summary` (counts per
        R12 type), and `runner` echoed back for the agent's reference.

    Each failure record:
        {
            "type": "real_bug" | "environment" | "test_bug" | "unknown",
            "reason": str,
            "test_name": str,
            "file": str,
            "line": int | None,
            "error_type": str,
            "message": str,
        }
    """
    if runner in ("jest", "vitest"):
        failures = _parse_jest_failures(runner_output)
    else:
        failures = _parse_pytest_failures(runner_output)

    summary = {"real_bug": 0, "environment": 0, "test_bug": 0, "unknown": 0}
    for f in failures:
        summary[f["type"]] += 1

    return {
        "runner": runner,
        "failures": failures,
        "summary": summary,
        "total_failures": len(failures),
    }
