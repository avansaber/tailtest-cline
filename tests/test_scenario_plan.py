"""V14.1 tests for tailtest_scenario_plan tool.

Tests cover: language detection, depth reading, adversarial count requirement,
framework detection, baseline scenarios, test file path resolution.
"""

import json
import os
import sys
import tempfile

import pytest

# Make the tools module importable
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO_ROOT, "mcp_server", "src"))

from tools.scenario_plan import (
    scenario_plan,
    ADVERSARIAL_BY_DEPTH,
    SCENARIO_COUNT_BY_DEPTH,
    ADVERSARIAL_CATEGORIES,
)


@pytest.fixture
def py_project(tmp_path):
    """A project with a Python source file and pyproject.toml."""
    src = tmp_path / "services" / "billing.py"
    src.parent.mkdir()
    src.write_text("def calc(): pass\n")
    return tmp_path, str(src)


# ---------------------------------------------------------------------------
# Constants / contracts
# ---------------------------------------------------------------------------


class TestR15Constants:
    def test_adversarial_count_simple_is_zero(self):
        assert ADVERSARIAL_BY_DEPTH["simple"] == 0

    def test_adversarial_count_standard_is_2(self):
        assert ADVERSARIAL_BY_DEPTH["standard"] == 2

    def test_adversarial_count_thorough_is_4(self):
        assert ADVERSARIAL_BY_DEPTH["thorough"] == 4

    def test_adversarial_count_adversarial_is_8(self):
        assert ADVERSARIAL_BY_DEPTH["adversarial"] == 8

    def test_scenario_count_simple_is_2_3(self):
        assert SCENARIO_COUNT_BY_DEPTH["simple"] == (2, 3)

    def test_scenario_count_standard_is_5_8(self):
        assert SCENARIO_COUNT_BY_DEPTH["standard"] == (5, 8)

    def test_scenario_count_thorough_is_10_15(self):
        assert SCENARIO_COUNT_BY_DEPTH["thorough"] == (10, 15)

    def test_scenario_count_adversarial_is_8_12(self):
        assert SCENARIO_COUNT_BY_DEPTH["adversarial"] == (8, 12)

    def test_eight_adversarial_categories(self):
        assert len(ADVERSARIAL_CATEGORIES) == 8

    def test_categories_match_R15_text(self):
        for cat in [
            "boundary inputs",
            "format / injection",
            "type confusion",
            "concurrent state",
            "time / locale edges",
            "error handling under partial failures",
            "resource exhaustion",
            "off-by-one logic",
        ]:
            assert cat in ADVERSARIAL_CATEGORIES


# ---------------------------------------------------------------------------
# Language detection
# ---------------------------------------------------------------------------


class TestLanguageDetection:
    def test_python_extension(self, tmp_path):
        f = tmp_path / "x.py"
        f.write_text("")
        result = scenario_plan(str(f), project_root=str(tmp_path))
        assert result["language"] == "python"

    def test_typescript_extension(self, tmp_path):
        f = tmp_path / "x.ts"
        f.write_text("")
        result = scenario_plan(str(f), project_root=str(tmp_path))
        assert result["language"] == "typescript"

    def test_go_extension(self, tmp_path):
        f = tmp_path / "x.go"
        f.write_text("")
        result = scenario_plan(str(f), project_root=str(tmp_path))
        assert result["language"] == "go"

    def test_java_extension(self, tmp_path):
        f = tmp_path / "X.java"
        f.write_text("")
        result = scenario_plan(str(f), project_root=str(tmp_path))
        assert result["language"] == "java"

    def test_csharp_extension(self, tmp_path):
        f = tmp_path / "X.cs"
        f.write_text("")
        result = scenario_plan(str(f), project_root=str(tmp_path))
        assert result["language"] == "csharp"

    def test_kotlin_extension(self, tmp_path):
        f = tmp_path / "X.kt"
        f.write_text("")
        result = scenario_plan(str(f), project_root=str(tmp_path))
        assert result["language"] == "kotlin"


# ---------------------------------------------------------------------------
# Depth reading
# ---------------------------------------------------------------------------


class TestDepthReading:
    def test_no_config_defaults_to_standard(self, tmp_path):
        f = tmp_path / "x.py"
        f.write_text("")
        result = scenario_plan(str(f), project_root=str(tmp_path))
        assert result["depth"] == "standard"

    def test_adversarial_depth_read_from_config(self, tmp_path):
        f = tmp_path / "x.py"
        f.write_text("")
        ttdir = tmp_path / ".tailtest"
        ttdir.mkdir()
        (ttdir / "config.json").write_text(json.dumps({"depth": "adversarial"}))
        result = scenario_plan(str(f), project_root=str(tmp_path))
        assert result["depth"] == "adversarial"

    def test_simple_depth_read_from_config(self, tmp_path):
        f = tmp_path / "x.py"
        f.write_text("")
        ttdir = tmp_path / ".tailtest"
        ttdir.mkdir()
        (ttdir / "config.json").write_text(json.dumps({"depth": "simple"}))
        result = scenario_plan(str(f), project_root=str(tmp_path))
        assert result["depth"] == "simple"

    def test_invalid_depth_falls_back_to_standard(self, tmp_path):
        f = tmp_path / "x.py"
        f.write_text("")
        ttdir = tmp_path / ".tailtest"
        ttdir.mkdir()
        (ttdir / "config.json").write_text(json.dumps({"depth": "supernova"}))
        result = scenario_plan(str(f), project_root=str(tmp_path))
        assert result["depth"] == "standard"


# ---------------------------------------------------------------------------
# R15 enforcement (the load-bearing logic)
# ---------------------------------------------------------------------------


class TestR15Enforcement:
    def test_simple_depth_requires_zero_adversarial(self, tmp_path):
        f = tmp_path / "x.py"
        f.write_text("")
        ttdir = tmp_path / ".tailtest"
        ttdir.mkdir()
        (ttdir / "config.json").write_text(json.dumps({"depth": "simple"}))
        result = scenario_plan(str(f), project_root=str(tmp_path))
        assert result["adversarial_count_required"] == 0

    def test_standard_depth_requires_2_adversarial(self, tmp_path):
        f = tmp_path / "x.py"
        f.write_text("")
        result = scenario_plan(str(f), project_root=str(tmp_path))
        assert result["adversarial_count_required"] == 2

    def test_thorough_depth_requires_4_adversarial(self, tmp_path):
        f = tmp_path / "x.py"
        f.write_text("")
        ttdir = tmp_path / ".tailtest"
        ttdir.mkdir()
        (ttdir / "config.json").write_text(json.dumps({"depth": "thorough"}))
        result = scenario_plan(str(f), project_root=str(tmp_path))
        assert result["adversarial_count_required"] == 4

    def test_adversarial_depth_requires_8_adversarial(self, tmp_path):
        f = tmp_path / "x.py"
        f.write_text("")
        ttdir = tmp_path / ".tailtest"
        ttdir.mkdir()
        (ttdir / "config.json").write_text(json.dumps({"depth": "adversarial"}))
        result = scenario_plan(str(f), project_root=str(tmp_path))
        assert result["adversarial_count_required"] == 8


# ---------------------------------------------------------------------------
# Framework detection
# ---------------------------------------------------------------------------


class TestFrameworkDetection:
    def test_flask_detected_from_requirements(self, tmp_path):
        f = tmp_path / "x.py"
        f.write_text("")
        (tmp_path / "requirements.txt").write_text("Flask==3.1.0\nrequests")
        result = scenario_plan(str(f), project_root=str(tmp_path))
        assert result["framework"] == "flask"

    def test_fastapi_detected_from_pyproject(self, tmp_path):
        f = tmp_path / "x.py"
        f.write_text("")
        (tmp_path / "pyproject.toml").write_text('dependencies = ["fastapi>=0.100"]')
        result = scenario_plan(str(f), project_root=str(tmp_path))
        assert result["framework"] == "fastapi"

    def test_no_framework_for_plain_python(self, tmp_path):
        f = tmp_path / "x.py"
        f.write_text("")
        result = scenario_plan(str(f), project_root=str(tmp_path))
        assert result["framework"] is None

    def test_no_framework_for_non_python(self, tmp_path):
        f = tmp_path / "x.go"
        f.write_text("")
        (tmp_path / "requirements.txt").write_text("Flask==3.1.0")  # noise
        result = scenario_plan(str(f), project_root=str(tmp_path))
        assert result["framework"] is None


# ---------------------------------------------------------------------------
# Test file path resolution
# ---------------------------------------------------------------------------


class TestTestFilePath:
    def test_python_test_path(self, tmp_path):
        f = tmp_path / "billing.py"
        f.write_text("")
        result = scenario_plan(str(f), project_root=str(tmp_path))
        assert result["test_file_path"].endswith(os.path.join("tests", "test_billing.py"))

    def test_typescript_test_path(self, tmp_path):
        f = tmp_path / "Button.ts"
        f.write_text("")
        result = scenario_plan(str(f), project_root=str(tmp_path))
        assert result["test_file_path"].endswith("Button.test.ts")

    def test_go_test_path_colocated(self, tmp_path):
        f = tmp_path / "internal" / "handler.go"
        f.parent.mkdir()
        f.write_text("")
        result = scenario_plan(str(f), project_root=str(tmp_path))
        assert result["test_file_path"].endswith(os.path.join("internal", "handler_test.go"))

    def test_csharp_test_path(self, tmp_path):
        f = tmp_path / "OrderService.cs"
        f.write_text("")
        result = scenario_plan(str(f), project_root=str(tmp_path))
        assert result["test_file_path"].endswith(os.path.join("tests", "OrderServiceTests.cs"))


# ---------------------------------------------------------------------------
# Baseline scenarios
# ---------------------------------------------------------------------------


class TestBaselineScenarios:
    def test_python_language_baseline(self, tmp_path):
        f = tmp_path / "x.py"
        f.write_text("")
        result = scenario_plan(str(f), project_root=str(tmp_path))
        assert "None input" in result["language_baseline"]
        assert "wrong type passed" in result["language_baseline"]

    def test_flask_framework_baseline(self, tmp_path):
        f = tmp_path / "x.py"
        f.write_text("")
        (tmp_path / "requirements.txt").write_text("flask")
        result = scenario_plan(str(f), project_root=str(tmp_path))
        assert any("Route returns 200" in s for s in result["framework_baseline"])

    def test_no_framework_baseline_when_no_framework(self, tmp_path):
        f = tmp_path / "x.go"
        f.write_text("")
        result = scenario_plan(str(f), project_root=str(tmp_path))
        assert result["framework_baseline"] == []


# ---------------------------------------------------------------------------
# Instructions field
# ---------------------------------------------------------------------------


class TestInstructions:
    def test_instructions_mention_depth(self, tmp_path):
        f = tmp_path / "x.py"
        f.write_text("")
        ttdir = tmp_path / ".tailtest"
        ttdir.mkdir()
        (ttdir / "config.json").write_text(json.dumps({"depth": "thorough"}))
        result = scenario_plan(str(f), project_root=str(tmp_path))
        assert "thorough" in result["instructions"]

    def test_instructions_mention_R15(self, tmp_path):
        f = tmp_path / "x.py"
        f.write_text("")
        result = scenario_plan(str(f), project_root=str(tmp_path))
        assert "R15" in result["instructions"]

    def test_simple_depth_skips_R15_note(self, tmp_path):
        f = tmp_path / "x.py"
        f.write_text("")
        ttdir = tmp_path / ".tailtest"
        ttdir.mkdir()
        (ttdir / "config.json").write_text(json.dumps({"depth": "simple"}))
        result = scenario_plan(str(f), project_root=str(tmp_path))
        assert "R15 does not apply" in result["instructions"]
