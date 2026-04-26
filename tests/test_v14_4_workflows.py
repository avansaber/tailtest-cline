"""V14.4 tests: 8 additional slash workflow files exist with expected content.

After V14.3 we have 2 workflows (tailtest-hunt, tailtest-test). V14.4 adds 8
more (tailtest-status, tailtest-debt, tailtest-report, tailtest-depth,
tailtest-gen, tailtest-scan, tailtest-security, tailtest-mode, tailtest-summary).

Note: counted as 9 here because tailtest-summary was carved out of the
baseline rule into its own workflow file. Total workflows after V14.4: 11.
"""

import os
import sys

import pytest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATES_WORKFLOWS = os.path.join(
    REPO_ROOT, "mcp_server", "src", "templates", "workflows"
)


# ---------------------------------------------------------------------------
# All workflows present
# ---------------------------------------------------------------------------


EXPECTED_WORKFLOWS = (
    "tailtest-hunt.md",
    "tailtest-test.md",
    "tailtest-status.md",
    "tailtest-debt.md",
    "tailtest-report.md",
    "tailtest-depth.md",
    "tailtest-gen.md",
    "tailtest-scan.md",
    "tailtest-security.md",
    "tailtest-mode.md",
    "tailtest-summary.md",
)


class TestWorkflowFilesPresent:
    @pytest.mark.parametrize("workflow", EXPECTED_WORKFLOWS)
    def test_workflow_file_exists(self, workflow):
        path = os.path.join(TEMPLATES_WORKFLOWS, workflow)
        assert os.path.exists(path), f"Missing workflow template: {workflow}"

    def test_eleven_workflows_total(self):
        files = [
            f for f in os.listdir(TEMPLATES_WORKFLOWS) if f.endswith(".md")
        ]
        assert len(files) >= 11, f"Expected 11+ workflows, got {len(files)}: {files}"


# ---------------------------------------------------------------------------
# Each workflow has YAML frontmatter with description
# ---------------------------------------------------------------------------


class TestWorkflowFrontmatter:
    @pytest.mark.parametrize("workflow", EXPECTED_WORKFLOWS)
    def test_has_frontmatter(self, workflow):
        path = os.path.join(TEMPLATES_WORKFLOWS, workflow)
        with open(path) as f:
            content = f.read()
        assert content.startswith("---\n"), f"{workflow} missing YAML frontmatter"
        assert "description:" in content[:300], f"{workflow} frontmatter missing description"

    @pytest.mark.parametrize("workflow", EXPECTED_WORKFLOWS)
    def test_has_trigger_phrases_section(self, workflow):
        path = os.path.join(TEMPLATES_WORKFLOWS, workflow)
        with open(path) as f:
            content = f.read()
        assert (
            "Trigger phrases" in content or "## Behavior" in content
        ), f"{workflow} missing trigger phrases / behavior section"


# ---------------------------------------------------------------------------
# Specific workflow content checks
# ---------------------------------------------------------------------------


class TestStatusWorkflow:
    def test_mentions_config_json(self):
        path = os.path.join(TEMPLATES_WORKFLOWS, "tailtest-status.md")
        with open(path) as f:
            content = f.read()
        assert ".tailtest/config.json" in content
        assert "Depth:" in content
        assert "Mode:" in content


class TestDepthWorkflow:
    def test_lists_4_depth_values(self):
        path = os.path.join(TEMPLATES_WORKFLOWS, "tailtest-depth.md")
        with open(path) as f:
            content = f.read()
        for v in ("simple", "standard", "thorough", "adversarial"):
            assert f"`{v}`" in content, f"depth value {v} not in workflow"


class TestModeWorkflow:
    def test_documents_auto_approve_requirement(self):
        path = os.path.join(TEMPLATES_WORKFLOWS, "tailtest-mode.md")
        with open(path) as f:
            content = f.read()
        assert "Edit files (workspace)" in content
        assert "Execute safe commands" in content
        assert "Use MCP servers" in content


class TestHuntWorkflow:
    def test_writes_to_separate_hunt_file(self):
        path = os.path.join(TEMPLATES_WORKFLOWS, "tailtest-hunt.md")
        with open(path) as f:
            content = f.read()
        assert "_hunt" in content
        assert "bypass" in content.lower() or "regardless" in content.lower()


class TestSecurityWorkflow:
    def test_mentions_baseline(self):
        path = os.path.join(TEMPLATES_WORKFLOWS, "tailtest-security.md")
        with open(path) as f:
            content = f.read()
        assert "baseline" in content.lower()


class TestGenWorkflow:
    def test_includes_review_header_guidance(self):
        path = os.path.join(TEMPLATES_WORKFLOWS, "tailtest-gen.md")
        with open(path) as f:
            content = f.read()
        assert "review" in content.lower()
        assert "compile check" in content.lower()


class TestScanWorkflow:
    def test_documents_likely_vibe_coded_flag(self):
        path = os.path.join(TEMPLATES_WORKFLOWS, "tailtest-scan.md")
        with open(path) as f:
            content = f.read()
        assert "likely_vibe_coded" in content


class TestReportWorkflow:
    def test_documents_html_then_json_fallback(self):
        path = os.path.join(TEMPLATES_WORKFLOWS, "tailtest-report.md")
        with open(path) as f:
            content = f.read()
        assert "latest.json" in content
        assert "report" in content.lower()


# ---------------------------------------------------------------------------
# tailtest_setup now copies all 11 workflows
# ---------------------------------------------------------------------------


class TestSetupCopiesAllWorkflows:
    def test_setup_writes_all_workflows(self, tmp_path):
        sys.path.insert(0, os.path.join(REPO_ROOT, "mcp_server"))
        from src.tools.setup import setup  # type: ignore

        (tmp_path / "main.py").write_text("")
        result = setup(project_root=str(tmp_path))

        workflows_dir = tmp_path / ".clinerules" / "workflows"
        for wf in EXPECTED_WORKFLOWS:
            assert (workflows_dir / wf).exists(), f"setup did not copy {wf}"

        # Sanity: at least 11 files written under .clinerules/workflows/
        written = sorted(workflows_dir.glob("*.md"))
        assert len(written) >= 11
