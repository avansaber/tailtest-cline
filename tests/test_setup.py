"""V14.3 tests for tailtest_setup tool."""

import json
import os

import pytest

from tailtest_mcp.tools.setup import setup, MEMORY_BANK_CORE_FILES


# ---------------------------------------------------------------------------
# Detection
# ---------------------------------------------------------------------------


class TestDetection:
    def test_python_project(self, tmp_path):
        (tmp_path / "main.py").write_text("def x(): pass\n")
        (tmp_path / "pyproject.toml").write_text("[project]\nname='x'")
        result = setup(project_root=str(tmp_path))
        assert result["detected"]["language"] == "python"
        assert result["detected"]["runner"] == "pytest"

    def test_flask_framework_detected(self, tmp_path):
        (tmp_path / "app.py").write_text("from flask import Flask\napp = Flask(__name__)\n")
        (tmp_path / "requirements.txt").write_text("flask\n")
        result = setup(project_root=str(tmp_path))
        assert result["detected"]["framework"] == "flask"

    def test_typescript_with_jest(self, tmp_path):
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "x.ts").write_text("export const x = 1;\n")
        (tmp_path / "package.json").write_text('{"devDependencies":{"jest":"^29"}}')
        result = setup(project_root=str(tmp_path))
        assert result["detected"]["language"] == "typescript"
        assert result["detected"]["runner"] == "jest"

    def test_unknown_project(self, tmp_path):
        result = setup(project_root=str(tmp_path))
        assert result["detected"]["language"] == "unknown"


# ---------------------------------------------------------------------------
# File writing
# ---------------------------------------------------------------------------


class TestFilesWritten:
    def test_clinerules_baseline_written(self, tmp_path):
        (tmp_path / "main.py").write_text("")
        result = setup(project_root=str(tmp_path))
        assert os.path.exists(tmp_path / ".clinerules" / "01-tailtest-baseline.md")

    def test_workflows_written(self, tmp_path):
        (tmp_path / "main.py").write_text("")
        result = setup(project_root=str(tmp_path))
        assert os.path.exists(tmp_path / ".clinerules" / "workflows" / "tailtest-hunt.md")
        assert os.path.exists(tmp_path / ".clinerules" / "workflows" / "tailtest-test.md")

    def test_memory_bank_seeded(self, tmp_path):
        (tmp_path / "main.py").write_text("")
        result = setup(project_root=str(tmp_path))
        assert os.path.exists(tmp_path / "memory-bank" / "tailtestContext.md")

    def test_tailtest_config_written(self, tmp_path):
        (tmp_path / "main.py").write_text("")
        result = setup(project_root=str(tmp_path))
        config_path = tmp_path / ".tailtest" / "config.json"
        assert config_path.exists()
        with open(config_path) as f:
            cfg = json.load(f)
        assert cfg["depth"] == "standard"

    def test_tailtest_session_written(self, tmp_path):
        (tmp_path / "main.py").write_text("")
        result = setup(project_root=str(tmp_path))
        session_path = tmp_path / ".tailtest" / "session.json"
        assert session_path.exists()
        with open(session_path) as f:
            sess = json.load(f)
        assert sess["paused"] is False
        assert sess["pending_files"] == []


# ---------------------------------------------------------------------------
# Idempotence: existing files are not overwritten
# ---------------------------------------------------------------------------


class TestIdempotence:
    def test_existing_clinerules_not_overwritten(self, tmp_path):
        (tmp_path / "main.py").write_text("")
        # User has a custom rule already in place
        rules_dir = tmp_path / ".clinerules"
        rules_dir.mkdir()
        (rules_dir / "01-tailtest-baseline.md").write_text("CUSTOM")

        result = setup(project_root=str(tmp_path))
        assert (tmp_path / ".clinerules" / "01-tailtest-baseline.md").read_text() == "CUSTOM"
        skipped = " ".join(result["files_skipped"])
        assert "01-tailtest-baseline.md" in skipped

    def test_existing_config_not_overwritten(self, tmp_path):
        (tmp_path / "main.py").write_text("")
        tt_dir = tmp_path / ".tailtest"
        tt_dir.mkdir()
        (tt_dir / "config.json").write_text('{"depth":"adversarial"}')

        result = setup(project_root=str(tmp_path))
        with open(tt_dir / "config.json") as f:
            cfg = json.load(f)
        assert cfg["depth"] == "adversarial"  # untouched

    def test_existing_memory_bank_context_not_overwritten(self, tmp_path):
        (tmp_path / "main.py").write_text("")
        mb_dir = tmp_path / "memory-bank"
        mb_dir.mkdir()
        (mb_dir / "tailtestContext.md").write_text("USER NOTES PRESERVED")

        result = setup(project_root=str(tmp_path))
        assert (mb_dir / "tailtestContext.md").read_text() == "USER NOTES PRESERVED"


# ---------------------------------------------------------------------------
# Memory Bank co-existence: doesn't clobber the 6 core files
# ---------------------------------------------------------------------------


class TestMemoryBankCoexistence:
    def test_pre_existing_memory_bank_detected(self, tmp_path):
        (tmp_path / "main.py").write_text("")
        mb_dir = tmp_path / "memory-bank"
        mb_dir.mkdir()
        for fname in MEMORY_BANK_CORE_FILES:
            (mb_dir / fname).write_text(f"# {fname}")

        result = setup(project_root=str(tmp_path))
        assert result["memory_bank_pre_existed"] is True

    def test_no_memory_bank_marked_false(self, tmp_path):
        (tmp_path / "main.py").write_text("")
        result = setup(project_root=str(tmp_path))
        assert result["memory_bank_pre_existed"] is False

    def test_existing_core_files_not_touched(self, tmp_path):
        (tmp_path / "main.py").write_text("")
        mb_dir = tmp_path / "memory-bank"
        mb_dir.mkdir()
        for fname in MEMORY_BANK_CORE_FILES:
            (mb_dir / fname).write_text(f"# {fname} ORIGINAL")

        setup(project_root=str(tmp_path))
        for fname in MEMORY_BANK_CORE_FILES:
            assert (mb_dir / fname).read_text() == f"# {fname} ORIGINAL"


# ---------------------------------------------------------------------------
# Mode handling
# ---------------------------------------------------------------------------


class TestModeHandling:
    def test_default_mode_is_manual(self, tmp_path):
        (tmp_path / "main.py").write_text("")
        result = setup(project_root=str(tmp_path))
        assert result["mode"] == "manual"
        with open(tmp_path / ".tailtest" / "config.json") as f:
            cfg = json.load(f)
        assert cfg["mode"] == "manual"

    def test_auto_mode_records(self, tmp_path):
        (tmp_path / "main.py").write_text("")
        result = setup(project_root=str(tmp_path), mode="auto")
        assert result["mode"] == "auto"
        with open(tmp_path / ".tailtest" / "config.json") as f:
            cfg = json.load(f)
        assert cfg["mode"] == "auto"

    def test_invalid_mode_raises(self, tmp_path):
        (tmp_path / "main.py").write_text("")
        with pytest.raises(ValueError):
            setup(project_root=str(tmp_path), mode="enabled")


# ---------------------------------------------------------------------------
# Output contract
# ---------------------------------------------------------------------------


class TestOutputContract:
    def test_returns_required_keys(self, tmp_path):
        (tmp_path / "main.py").write_text("")
        result = setup(project_root=str(tmp_path))
        for key in (
            "project_root",
            "detected",
            "mode",
            "memory_bank_pre_existed",
            "files_written",
            "files_skipped",
            "reload_required",
            "next_steps",
        ):
            assert key in result

    def test_reload_required_always_true(self, tmp_path):
        (tmp_path / "main.py").write_text("")
        result = setup(project_root=str(tmp_path))
        assert result["reload_required"] is True

    def test_next_steps_mentions_reload(self, tmp_path):
        (tmp_path / "main.py").write_text("")
        result = setup(project_root=str(tmp_path))
        assert "reload" in result["next_steps"].lower() or "new conversation" in result["next_steps"].lower()

    def test_next_steps_includes_mode_specific_guidance(self, tmp_path):
        (tmp_path / "main.py").write_text("")
        manual = setup(project_root=str(tmp_path / "m"))
        # Re-create a sibling for auto
        (tmp_path / "m").mkdir(exist_ok=True)
        (tmp_path / "m" / "main.py").write_text("")
        manual = setup(project_root=str(tmp_path / "m"), mode="manual")
        assert "/tailtest-test" in manual["next_steps"]

        (tmp_path / "a").mkdir(exist_ok=True)
        (tmp_path / "a" / "main.py").write_text("")
        auto = setup(project_root=str(tmp_path / "a"), mode="auto")
        assert "auto-approve" in auto["next_steps"].lower()
