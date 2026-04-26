# Changelog

## v1.0.0 -- (target 2026-04-XX, awaiting V14.5 gate pass)

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
