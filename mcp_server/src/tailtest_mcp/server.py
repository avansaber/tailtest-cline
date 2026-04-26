"""tailtest-mcp server entry point.

Exposes tailtest's structured tools to Cline via MCP STDIO transport. Each
tool wraps existing Python logic in lib/ (vendored from tailtest-cursor's
scripts/lib/) plus a few Cline-specific tools (tailtest_setup, tailtest_pick_template).

V14.0 scope: skeleton with one ping tool to verify the MCP plumbing works.
V14.1 onward: progressively wire each lib/ function as a structured tool.
"""

import asyncio
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from . import __version__


server = Server("tailtest")


@server.list_tools()
async def list_tools() -> list[Tool]:
    """Return the list of tools exposed by tailtest-mcp."""
    return [
        Tool(
            name="tailtest_ping",
            description="Health check. Returns server version and confirms the MCP server is reachable.",
            inputSchema={
                "type": "object",
                "properties": {},
                "additionalProperties": False,
            },
        ),
        Tool(
            name="tailtest_scenario_plan",
            description=(
                "Return structured scaffolding the agent uses to write its SCENARIO PLAN: "
                "language, framework, depth, R15 adversarial count requirement, language and "
                "framework baseline scenarios, test file path, and prose instructions. The agent "
                "uses this scaffolding to compose the actual SCENARIO PLAN scenario lines."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Relative or absolute path to the source file under test.",
                    },
                    "project_root": {
                        "type": "string",
                        "description": "Project root directory. Defaults to the current working directory.",
                    },
                },
                "required": ["file_path"],
                "additionalProperties": False,
            },
        ),
        Tool(
            name="tailtest_classify_failures",
            description=(
                "Parse runner output (pytest, jest, etc.) into structured failure records and "
                "apply heuristic R12 classification. Returns failures with type "
                "(real_bug / environment / test_bug / unknown), reason, test name, file, "
                "line, error type, message, and a summary count per R12 category. The agent "
                "verifies or overrides the heuristic when context warrants."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "runner_output": {
                        "type": "string",
                        "description": "Stdout (and optionally stderr) from the test runner.",
                    },
                    "runner": {
                        "type": "string",
                        "enum": ["pytest", "jest", "vitest", "mocha"],
                        "description": "Runner name. Defaults to pytest.",
                    },
                },
                "required": ["runner_output"],
                "additionalProperties": False,
            },
        ),
        Tool(
            name="tailtest_pick_template",
            description=(
                "Return the full framework R2 template for a given source file: language "
                "baseline scenarios, framework baseline scenarios, framework-specific test "
                "pattern (e.g., NestJS Test.createTestingModule, Spring @WebMvcTest, Flask "
                "test_client), and test file path pattern. Returns just language baseline "
                "when no framework matches."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Relative or absolute path to the source file under test.",
                    },
                    "project_root": {
                        "type": "string",
                        "description": "Project root directory. Defaults to the current working directory.",
                    },
                },
                "required": ["file_path"],
                "additionalProperties": False,
            },
        ),
        Tool(
            name="tailtest_setup",
            description=(
                "Bootstrap entry point for tailtest in a Cline project. Detects language / "
                "framework / runner, writes the .clinerules/ rule pack, writes "
                ".clinerules/workflows/ slash workflows, seeds Memory Bank with "
                "tailtestContext.md (a 7th file alongside the 6 core ones; existing files are "
                "not overwritten), and initialises .tailtest/config.json + session.json. "
                "Returns a structured report including the user-facing 'reload required' "
                "warning (Cline does not auto-reload .clinerules mid-conversation)."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "project_root": {
                        "type": "string",
                        "description": "Project directory. Defaults to the current working directory.",
                    },
                    "mode": {
                        "type": "string",
                        "enum": ["manual", "auto"],
                        "description": (
                            "manual (default): user invokes /tailtest-test after edits. "
                            "auto: tailtest fires after every edit (requires Cline auto-approve)."
                        ),
                    },
                },
                "additionalProperties": False,
            },
        ),
        # V14.4+ tools registered here:
        # tailtest_baseline_state, tailtest_runner_for_lang, tailtest_security_status
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Dispatch tool invocation to the appropriate handler."""
    if name == "tailtest_ping":
        return [
            TextContent(
                type="text",
                text=f"tailtest-mcp v{__version__} reachable. V14.1 scenario_plan tool live.",
            )
        ]
    if name == "tailtest_scenario_plan":
        from .tools.scenario_plan import scenario_plan
        import json as _json

        result = scenario_plan(
            file_path=arguments["file_path"],
            project_root=arguments.get("project_root"),
        )
        return [TextContent(type="text", text=_json.dumps(result, indent=2))]
    if name == "tailtest_classify_failures":
        from .tools.classify_failures import classify_failures
        import json as _json

        result = classify_failures(
            runner_output=arguments["runner_output"],
            runner=arguments.get("runner", "pytest"),
        )
        return [TextContent(type="text", text=_json.dumps(result, indent=2))]
    if name == "tailtest_pick_template":
        from .tools.pick_template import pick_template
        import json as _json

        result = pick_template(
            file_path=arguments["file_path"],
            project_root=arguments.get("project_root"),
        )
        return [TextContent(type="text", text=_json.dumps(result, indent=2))]
    if name == "tailtest_setup":
        from .tools.setup import setup
        import json as _json

        result = setup(
            project_root=arguments.get("project_root"),
            mode=arguments.get("mode", "manual"),
        )
        return [TextContent(type="text", text=_json.dumps(result, indent=2))]
    raise ValueError(f"Unknown tool: {name}")


async def _async_main() -> None:
    """Run the MCP server over STDIO."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


def main() -> None:
    """Entry point for the tailtest-mcp console script."""
    asyncio.run(_async_main())


if __name__ == "__main__":
    main()
