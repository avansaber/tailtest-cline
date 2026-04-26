# tailtest-cline

Tailtest for Cline. MCP server plus `.clinerules/` rule pack plus Memory Bank integration. Adversarial test generation across 8+ Cline-supported editors (VS Code, Cursor, JetBrains IDEs, Antigravity, Zed, Neovim, VSCodium, Windsurf, plus Cline CLI).

**Status:** V14.0 scaffold (2026-04-25). Not yet shipped. Tracking plan in private repo `plans/V14-cline.md`.

## What it is

Tailtest validates code AND probes for bugs. The Claude Code, Cursor, and Codex variants of tailtest already do this through host-specific hooks. Cline has no hook system, so this variant uses three Cline-native primitives instead:

- **`.clinerules/`** carries the rule layer (R1-R14 plus R15 adversarial mode)
- **`tailtest-mcp` server** (this repo) provides structured tools for the agent: scenario planning, R12 failure classification, framework template lookup, baseline state, and an installer
- **Memory Bank** (`tailtestContext.md`) holds the persistent project profile across Cline sessions

## What ships in V14.0 (this scaffold)

- Python MCP server skeleton with one health-check tool (`tailtest_ping`)
- Vendored `lib/` from `tailtest-cursor/scripts/lib/`
- `.clinerules/` directory placeholder for the V14.1 rule port
- pyproject.toml + .gitignore + tests/ directory

## What ships in V14.1 onward

V14.1 to V14.4 wire the actual MCP tools (one phase per tool group). V14.5 is the gate test (live VSCode-Cline + JetBrains-Cline). V14.6 is the marketplace launch.

See `plans/V14-cline.md` in the private repo for the full plan, simulation findings, and cross-audit notes.

## Install (eventual, post-V14.6 ship)

Cline MCP Marketplace install will be the canonical path. Direct GitHub install via `cline_mcp_settings.json` will also be supported.

## License

MIT (matches the other tailtest variants).
