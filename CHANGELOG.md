# Changelog

## v1.0.1 -- 2026-04-26

Packaging fix. v1.0.0 shipped a broken entry point (`tailtest-mcp` script crashed with `ModuleNotFoundError: No module named 'tailtest_mcp'` because the source directory was not laid out as a package matching the entry point name).

**Restructure:** moved `mcp_server/src/{server.py, tools/, lib/, templates/}` into `mcp_server/src/tailtest_mcp/` so the package directory matches the wheel's package name. `pyproject.toml` `[tool.hatch.build.targets.wheel] packages` updated accordingly.

**Dependency cleanup:** removed the `[server]` extra from `mcp[server]>=1.0.0` (the extra does not exist on `mcp` 1.27.0 and triggered a pip warning).

**Test imports:** updated three test files (`test_classify_failures.py`, `test_pick_template.py`, `test_scenario_plan.py`) from `from tools.X` (sys.path hack) to `from tailtest_mcp.tools.X` (proper package import).

No behavior or feature changes. 162 tests still green. Anyone who installed v1.0.0 should upgrade.

## v1.0.0 -- 2026-04-26

Initial release.

**Architecture:** three Cline primitives carry the integration:

- `.clinerules/` rule pack (451-line baseline ports R1-R15 + 8 adversarial categories + framework templates from `tailtest-cursor v1.6.0`)
- `tailtest-mcp` Python server with 5 tools: `tailtest_scenario_plan`, `tailtest_classify_failures`, `tailtest_pick_template`, `tailtest_setup`, `tailtest_ping`
- Memory Bank integration via `tailtestContext.md` as 7th file alongside the 6 core ones

**11 slash workflows:** `/tailtest-test`, `/tailtest-hunt`, `/tailtest-status`, `/tailtest-debt`, `/tailtest-report`, `/tailtest-depth`, `/tailtest-gen`, `/tailtest-scan`, `/tailtest-security`, `/tailtest-mode`, `/tailtest-summary`.

**Two operating modes:** manual (default; user invokes `/tailtest-test` after edits) and auto (opt-in with Cline auto-approve enabled for "Edit files (workspace)", "Execute safe commands", "Use MCP servers").

**Adversarial mode (V13) shipped from day one.** R15 always-on at standard or higher depth; new `adversarial` depth tier; new `/tailtest hunt <file>` slash command; 8 adversarial scenario categories (boundary inputs, format / injection, type confusion, concurrent state, time / locale edges, partial failures, resource exhaustion, off-by-one logic).

**Vendored** `lib/` from `tailtest-cursor` (13 files, ~1900 lines of mature dogfood-tested code).

**162 tests** in the plugin's own suite at v1.0.0.

**Reach:** 8+ editors via Cline's host coverage: VS Code, Cursor, JetBrains IDEs, Antigravity, Zed, Neovim, VSCodium, Windsurf, plus the Cline CLI.

**Discovery context:** built after the V13 outreach pilot (2026-04-23) confirmed adversarial test generation finds real bugs that coverage tests miss. The same R15 layer that produced 25 real bugs in 6 popular Python repos at V13 ship is integrated into V14 from day one.

**Plan reference:** `private/plans/V14-cline.md` (architecture + simulation findings + cross-audit) and `private/plans/phase-14a-gate.md` (12-check live gate test).

**License:** MIT. Same as the other tailtest variants.
