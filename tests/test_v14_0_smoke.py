"""V14.0 smoke tests. Verifies scaffold pieces are in place.

Real MCP integration tests come in V14.1 once the mcp SDK is installed
and the first non-trivial tool (tailtest_scenario_plan) ships.
"""

import os
import importlib.util
import pytest


REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class TestV14ScaffoldComplete:
    def test_pyproject_toml_exists(self):
        assert os.path.exists(os.path.join(REPO_ROOT, "pyproject.toml"))

    def test_readme_exists(self):
        assert os.path.exists(os.path.join(REPO_ROOT, "README.md"))

    def test_gitignore_exists(self):
        assert os.path.exists(os.path.join(REPO_ROOT, ".gitignore"))

    def test_mcp_server_skeleton_exists(self):
        assert os.path.exists(
            os.path.join(REPO_ROOT, "mcp_server", "src", "tailtest_mcp", "server.py")
        )

    def test_clinerules_baseline_placeholder(self):
        assert os.path.exists(
            os.path.join(REPO_ROOT, "clinerules", "01-tailtest-baseline.md")
        )

    def test_lib_vendored_from_cursor(self):
        lib_dir = os.path.join(REPO_ROOT, "mcp_server", "src", "tailtest_mcp", "lib")
        # 13 lib files plus __init__.py expected (matches cursor's scripts/lib/)
        py_files = [f for f in os.listdir(lib_dir) if f.endswith(".py")]
        assert len(py_files) >= 13, f"Expected 13+ lib files, got {len(py_files)}: {py_files}"

    def test_vendored_lib_contains_runners(self):
        runners = os.path.join(
            REPO_ROOT, "mcp_server", "src", "tailtest_mcp", "lib", "runners.py"
        )
        with open(runners) as f:
            src = f.read()
        # V13 was shipped to cursor; the vendored copy should already have adversarial
        assert "adversarial" in src, "Vendored runners.py is missing V13 adversarial depth tier"


class TestV14ServerSkeleton:
    def test_server_module_imports(self):
        # The mcp SDK is not yet installed; we verify the file parses and key
        # symbols exist via AST instead of attempting an import.
        import ast

        server_path = os.path.join(
            REPO_ROOT, "mcp_server", "src", "tailtest_mcp", "server.py"
        )
        with open(server_path) as f:
            tree = ast.parse(f.read())

        names = {
            node.name for node in ast.walk(tree)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        }
        assert "list_tools" in names
        assert "call_tool" in names
        assert "main" in names

    def test_server_declares_tailtest_ping_tool(self):
        server_path = os.path.join(
            REPO_ROOT, "mcp_server", "src", "tailtest_mcp", "server.py"
        )
        with open(server_path) as f:
            src = f.read()
        assert '"tailtest_ping"' in src

    def test_init_declares_version(self):
        init_path = os.path.join(
            REPO_ROOT, "mcp_server", "src", "tailtest_mcp", "__init__.py"
        )
        with open(init_path) as f:
            src = f.read()
        assert "__version__" in src


class TestV14PyprojectMetadata:
    def test_pyproject_declares_mcp_dependency(self):
        with open(os.path.join(REPO_ROOT, "pyproject.toml")) as f:
            content = f.read()
        assert "mcp>=" in content or "mcp ==" in content or 'mcp"' in content

    def test_pyproject_declares_console_script(self):
        with open(os.path.join(REPO_ROOT, "pyproject.toml")) as f:
            content = f.read()
        assert "tailtest-mcp" in content
        assert "tailtest_mcp.server:main" in content

    def test_pyproject_python_3_10_minimum(self):
        with open(os.path.join(REPO_ROOT, "pyproject.toml")) as f:
            content = f.read()
        assert 'requires-python = ">=3.10"' in content
