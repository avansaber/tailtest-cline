"""tailtest-mcp -- MCP server for Cline integration.

Three-pillar architecture:
- .clinerules/ rule pack (delivered by tailtest_setup MCP tool)
- This MCP server (structured tools: scenario_plan, classify_failures, etc.)
- Memory Bank tailtestContext.md (delivered by tailtest_setup)

See V14-cline.md plan in the private repo for full architecture.
"""

__version__ = "1.0.0-rc1"
