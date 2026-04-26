"""V14.2 tests for tailtest_pick_template tool."""

import pytest

from tailtest_mcp.tools.pick_template import (
    pick_template,
    FRAMEWORK_TEMPLATES,
    LANGUAGE_BASELINES,
)


# ---------------------------------------------------------------------------
# Constants / contracts
# ---------------------------------------------------------------------------


class TestTemplateConstants:
    def test_seven_framework_templates(self):
        # flask, fastapi, django, nestjs, spring, kotlin, csharp
        assert len(FRAMEWORK_TEMPLATES) >= 7

    def test_each_template_has_required_keys(self):
        for name, t in FRAMEWORK_TEMPLATES.items():
            for key in ("language", "baseline_scenarios", "test_pattern", "test_file_path"):
                assert key in t, f"Framework {name} missing {key}"

    def test_ten_language_baselines(self):
        # 9 languages currently (per V12 + V13 ship)
        assert len(LANGUAGE_BASELINES) >= 9


# ---------------------------------------------------------------------------
# Framework detection
# ---------------------------------------------------------------------------


class TestFrameworkDetection:
    def test_flask_via_requirements(self, tmp_path):
        f = tmp_path / "app.py"
        f.write_text("")
        (tmp_path / "requirements.txt").write_text("Flask==3.1\nrequests")
        result = pick_template(str(f), project_root=str(tmp_path))
        assert result["framework"] == "flask"

    def test_fastapi_via_pyproject(self, tmp_path):
        f = tmp_path / "main.py"
        f.write_text("")
        (tmp_path / "pyproject.toml").write_text('dependencies = ["fastapi>=0.100"]')
        result = pick_template(str(f), project_root=str(tmp_path))
        assert result["framework"] == "fastapi"

    def test_django_via_setup_py(self, tmp_path):
        f = tmp_path / "views.py"
        f.write_text("")
        (tmp_path / "setup.py").write_text('install_requires=["django>=4.2"]')
        result = pick_template(str(f), project_root=str(tmp_path))
        assert result["framework"] == "django"

    def test_nestjs_via_package_json(self, tmp_path):
        f = tmp_path / "users.controller.ts"
        f.write_text("")
        (tmp_path / "package.json").write_text(
            '{"dependencies":{"@nestjs/core":"^10"}}'
        )
        result = pick_template(str(f), project_root=str(tmp_path))
        assert result["framework"] == "nestjs"

    def test_spring_via_pom(self, tmp_path):
        f = tmp_path / "OrderController.java"
        f.write_text("")
        (tmp_path / "pom.xml").write_text(
            "<dependency><groupId>org.springframework.boot</groupId></dependency>"
        )
        result = pick_template(str(f), project_root=str(tmp_path))
        assert result["framework"] == "spring"

    def test_no_framework_for_plain_python(self, tmp_path):
        f = tmp_path / "x.py"
        f.write_text("")
        result = pick_template(str(f), project_root=str(tmp_path))
        assert result["framework"] is None


# ---------------------------------------------------------------------------
# Output contract
# ---------------------------------------------------------------------------


class TestOutputContract:
    def test_python_no_framework_returns_language_baseline(self, tmp_path):
        f = tmp_path / "x.py"
        f.write_text("")
        result = pick_template(str(f), project_root=str(tmp_path))
        assert "None input" in result["language_baseline"]
        assert result["framework_template"] is None

    def test_flask_returns_full_template(self, tmp_path):
        f = tmp_path / "app.py"
        f.write_text("")
        (tmp_path / "requirements.txt").write_text("flask")
        result = pick_template(str(f), project_root=str(tmp_path))
        assert result["framework_template"] is not None
        assert "Route returns 200 on valid path" in result["framework_template"]["baseline_scenarios"]

    def test_test_file_path_pattern_set_when_framework(self, tmp_path):
        f = tmp_path / "app.py"
        f.write_text("")
        (tmp_path / "requirements.txt").write_text("fastapi")
        result = pick_template(str(f), project_root=str(tmp_path))
        assert result["test_file_path_pattern"] == "tests/test_{basename}.py"

    def test_test_file_path_pattern_none_when_no_framework(self, tmp_path):
        f = tmp_path / "x.py"
        f.write_text("")
        result = pick_template(str(f), project_root=str(tmp_path))
        assert result["test_file_path_pattern"] is None

    def test_instructions_field_present(self, tmp_path):
        f = tmp_path / "x.py"
        f.write_text("")
        result = pick_template(str(f), project_root=str(tmp_path))
        assert "language baseline" in result["instructions"].lower()


# ---------------------------------------------------------------------------
# Framework template content sanity
# ---------------------------------------------------------------------------


class TestTemplateContent:
    def test_flask_test_pattern_mentions_test_client(self):
        assert "test_client" in FRAMEWORK_TEMPLATES["flask"]["test_pattern"]

    def test_fastapi_test_pattern_mentions_TestClient(self):
        assert "TestClient" in FRAMEWORK_TEMPLATES["fastapi"]["test_pattern"]

    def test_nestjs_test_pattern_mentions_createTestingModule(self):
        assert "createTestingModule" in FRAMEWORK_TEMPLATES["nestjs"]["test_pattern"]

    def test_spring_test_pattern_mentions_SpringBootTest(self):
        assert "@SpringBootTest" in FRAMEWORK_TEMPLATES["spring"]["test_pattern"]

    def test_csharp_test_pattern_mentions_xunit(self):
        assert "xunit" in FRAMEWORK_TEMPLATES["csharp"]["test_pattern"].lower()


# ---------------------------------------------------------------------------
# Language detection coverage
# ---------------------------------------------------------------------------


class TestLanguageBaselines:
    def test_python_baseline_has_None(self):
        assert "None input" in LANGUAGE_BASELINES["python"]

    def test_typescript_baseline_has_undefined(self):
        assert "undefined" in LANGUAGE_BASELINES["typescript"]

    def test_csharp_baseline_has_default_T(self):
        assert "default(T)" in LANGUAGE_BASELINES["csharp"]

    def test_kotlin_baseline_has_Result_failure(self):
        assert "Result.failure" in LANGUAGE_BASELINES["kotlin"]
