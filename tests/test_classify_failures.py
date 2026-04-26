"""V14.2 tests for tailtest_classify_failures tool."""

import os
import sys

import pytest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO_ROOT, "mcp_server", "src"))

from tools.classify_failures import (
    classify_failures,
    _heuristic_classification,
    ENV_ERRORS,
    LIKELY_REAL_BUG_ERRORS,
    AMBIGUOUS_ERRORS,
)


# ---------------------------------------------------------------------------
# Heuristic classification (the load-bearing logic)
# ---------------------------------------------------------------------------


class TestHeuristicClassification:
    def test_import_error_is_environment(self):
        cls, reason = _heuristic_classification("ImportError", "no module 'foo'", "")
        assert cls == "environment"

    def test_module_not_found_is_environment(self):
        cls, _ = _heuristic_classification("ModuleNotFoundError", "", "")
        assert cls == "environment"

    def test_connection_error_is_environment(self):
        cls, _ = _heuristic_classification("ConnectionError", "refused", "")
        assert cls == "environment"

    def test_attribute_error_is_real_bug(self):
        cls, _ = _heuristic_classification(
            "AttributeError", "'NoneType' has no attribute 'foo'", ""
        )
        assert cls == "real_bug"

    def test_type_error_is_real_bug(self):
        cls, _ = _heuristic_classification("TypeError", "expected str", "")
        assert cls == "real_bug"

    def test_key_error_is_real_bug(self):
        cls, _ = _heuristic_classification("KeyError", "'missing'", "")
        assert cls == "real_bug"

    def test_real_bug_flips_to_test_bug_when_in_fixture(self):
        cls, reason = _heuristic_classification(
            "AttributeError", "", "in conftest.py:42 in fixture setup"
        )
        assert cls == "test_bug"

    def test_assertion_error_with_expected_signal_is_real_bug(self):
        cls, _ = _heuristic_classification(
            "AssertionError", "expected 5, got 3", ""
        )
        assert cls == "real_bug"

    def test_assertion_error_with_fixture_signal_is_test_bug(self):
        cls, _ = _heuristic_classification(
            "AssertionError", "fixture not found", ""
        )
        assert cls == "test_bug"

    def test_assertion_error_default_is_real_bug(self):
        cls, _ = _heuristic_classification("AssertionError", "", "")
        assert cls == "real_bug"

    def test_unknown_error_classified_unknown(self):
        cls, _ = _heuristic_classification("VeryRareError", "", "")
        assert cls == "unknown"


# ---------------------------------------------------------------------------
# pytest output parsing
# ---------------------------------------------------------------------------


class TestPytestOutputParsing:
    def test_single_failure_short_form(self):
        output = """
test session starts ===
collected 1 item

FAILED tests/test_billing.py::test_apply_discount - AssertionError: expected 0, got None
"""
        result = classify_failures(output)
        assert result["total_failures"] == 1
        f = result["failures"][0]
        assert f["test_name"] == "test_apply_discount"
        assert f["file"] == "tests/test_billing.py"
        assert f["error_type"] == "AssertionError"
        assert f["type"] == "real_bug"

    def test_multiple_failures(self):
        output = """
FAILED tests/test_a.py::test_one - AssertionError: bad
FAILED tests/test_b.py::test_two - TypeError: nope
FAILED tests/test_c.py::test_three - ImportError: missing
"""
        result = classify_failures(output)
        assert result["total_failures"] == 3
        types = [f["type"] for f in result["failures"]]
        assert "real_bug" in types  # AssertionError
        assert "real_bug" in types  # TypeError
        assert "environment" in types  # ImportError

    def test_summary_counts(self):
        output = """
FAILED tests/test_a.py::test_one - AssertionError: bad
FAILED tests/test_b.py::test_two - ImportError: nope
FAILED tests/test_c.py::test_three - ImportError: also nope
"""
        result = classify_failures(output)
        assert result["summary"]["real_bug"] == 1
        assert result["summary"]["environment"] == 2
        assert result["summary"]["test_bug"] == 0

    def test_no_failures_returns_empty(self):
        output = "test session starts ===\ncollected 5 items\n5 passed in 0.05s\n"
        result = classify_failures(output)
        assert result["total_failures"] == 0
        assert result["failures"] == []

    def test_dedups_failures_with_same_file_and_test_name(self):
        # Pytest sometimes echoes the same FAILED line twice (short summary + verbose)
        output = """
FAILED tests/test_a.py::test_one - AssertionError: bad
FAILED tests/test_a.py::test_one - AssertionError: bad
"""
        result = classify_failures(output)
        assert result["total_failures"] == 1


# ---------------------------------------------------------------------------
# jest output parsing
# ---------------------------------------------------------------------------


class TestJestOutputParsing:
    def test_jest_failure_basic(self):
        output = """
FAIL src/foo.test.ts
  ● MyTest > does the thing

    Expected 1
    Received 2
"""
        result = classify_failures(output, runner="jest")
        assert result["total_failures"] == 1
        assert result["failures"][0]["file"] == "src/foo.test.ts"
        assert "does the thing" in result["failures"][0]["test_name"]

    def test_jest_no_failures(self):
        output = "PASS src/foo.test.ts\n  MyTest (10 ms)\n"
        result = classify_failures(output, runner="jest")
        assert result["total_failures"] == 0


# ---------------------------------------------------------------------------
# Output contract
# ---------------------------------------------------------------------------


class TestOutputContract:
    def test_returns_dict_with_expected_keys(self):
        result = classify_failures("FAILED tests/x.py::t - TypeError: nope")
        assert "runner" in result
        assert "failures" in result
        assert "summary" in result
        assert "total_failures" in result

    def test_runner_echoed_back(self):
        result = classify_failures("", runner="pytest")
        assert result["runner"] == "pytest"

    def test_each_failure_has_required_fields(self):
        result = classify_failures(
            "FAILED tests/x.py::t - TypeError: nope"
        )
        f = result["failures"][0]
        for field in ("type", "reason", "test_name", "file", "error_type", "message"):
            assert field in f

    def test_summary_keys_match_R12_categories(self):
        result = classify_failures("")
        for key in ("real_bug", "environment", "test_bug", "unknown"):
            assert key in result["summary"]


# ---------------------------------------------------------------------------
# Integration -- realistic pytest output
# ---------------------------------------------------------------------------


class TestRealisticOutput:
    def test_jinja2_cli_style_output(self):
        # Mimics output that surfaced in the V13 batch 2 jinja2-cli run
        output = """
============================== FAILURES ===============================
___________ test_get_format_unknown_raises_invalid_data_format ___________
tests/test_cli_v13.py:42: in test_get_format_unknown_raises_invalid_data_format
    get_format("nonexistent")
KeyError: 'nonexistent'
=========================== short test summary ========================
FAILED tests/test_cli_v13.py::test_get_format_unknown_raises_invalid_data_format - KeyError: 'nonexistent'
FAILED tests/test_cli_v13.py::test_has_format_unknown_returns_false - KeyError: 'unknown'
"""
        result = classify_failures(output)
        assert result["total_failures"] == 2
        assert result["summary"]["real_bug"] == 2  # Both are KeyError -> real_bug
