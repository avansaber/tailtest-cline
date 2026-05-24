# tailtest-cline -- AI software testing for Cline (8+ editors)

[![License: MIT](https://img.shields.io/badge/License-MIT-emerald.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/tests-162_passing-emerald)](https://github.com/avansaber/tailtest-cline)
[![Version](https://img.shields.io/badge/version-1.0.1-blue)](https://github.com/avansaber/tailtest-cline/releases/latest)
[![MCP](https://img.shields.io/badge/MCP-tailtest_server-purple)](https://glama.ai/mcp/servers/avansaber/tailtest-cline)
[![Editors](https://img.shields.io/badge/editors-8%2B_via_Cline-orange)](https://cline.bot)

> You build. Claude builds. tailtest makes sure it works -- across 8+ editors at once.

**tailtest-cline** is the open-source AI software testing layer for [Cline](https://cline.bot), the autonomous coding agent that runs across 8+ editors (VS Code, Cursor, JetBrains IDEs, Antigravity, Zed, Neovim, VSCodium, Windsurf, plus the Cline CLI). MCP-driven test generation: every time Cline edits a file, tailtest's MCP server picks up the change, generates production-shaped scenarios via the R1-R15 rule layer, runs them, and returns structured failure data to Cline. Adversarial mode (R15) included from day one.

Open source (MIT), no telemetry, no SaaS account. Same R1-R15 rule layer + adversarial mode as the Claude Code, Cursor, and Codex CLI variants -- 1,234 plugin tests total across the four hosts.

**[Read more on tailtest.com](https://www.tailtest.com/) · [Platform overview](https://www.tailtest.com/platform/) · [Agent-edit testing deep dive](https://www.tailtest.com/platform/agent-edits/) · [Cline docs](https://www.tailtest.com/docs/cline/)**

**Cline reach:** VS Code, Cursor, JetBrains IDEs, Antigravity, Zed, Neovim, VSCodium, Windsurf, plus the Cline CLI. One plugin, eight-plus editors.

## What's different from the other variants

Cline does not have hooks (Claude Code's `PostToolUse`, Cursor's `afterFileEdit`, Codex's `Stop`). Instead, tailtest-cline uses three Cline-native primitives:

- **`.clinerules/`** carries the rule layer (R1-R14 + R15 adversarial mode)
- **`tailtest-mcp` server** (this repo) provides structured tools for the agent: `tailtest_setup`, `tailtest_scenario_plan`, `tailtest_classify_failures`, `tailtest_pick_template`, `tailtest_ping`
- **Memory Bank** (`tailtestContext.md`) holds the per-project profile across Cline sessions

The deterministic policy (depth tiers, R15 adversarial counts, framework templates, file paths) lives in MCP server code rather than rule text. The agent calls the tools when it needs scaffolding rather than relying on rule recall over long sessions.

## Install

Three install paths:

### 1. Cline MCP Marketplace (recommended; one click)

Open Cline's Extensions panel inside your IDE. Search `tailtest`. Click install. Cline clones, installs deps, registers the server in `cline_mcp_settings.json` automatically.

### 2. Direct GitHub install

Paste `https://github.com/avansaber/tailtest-cline` into Cline's MCP server install dialog. Cline does the same clone + install + register flow.

### 3. Manual `cline_mcp_settings.json` edit

```json
{
  "mcpServers": {
    "tailtest": {
      "command": "python",
      "args": ["-m", "src.server"],
      "cwd": "/path/to/tailtest-cline/mcp_server",
      "alwaysAllow": [
        "tailtest_ping",
        "tailtest_scenario_plan",
        "tailtest_classify_failures",
        "tailtest_pick_template"
      ]
    }
  }
}
```

## First run

After install, type in Cline chat: **"set up tailtest in this project"**.

Cline calls `tailtest_setup`. The tool detects language / framework / runner, writes `.clinerules/`, writes `.clinerules/workflows/`, seeds `memory-bank/tailtestContext.md`, and initialises `.tailtest/config.json` + `.tailtest/session.json`. Idempotent: existing files preserved.

**Important:** Cline does not auto-reload `.clinerules` mid-conversation. Start a new conversation (or reload the window) to activate.

## Two operating modes

### Manual mode (default)

You invoke the test cycle explicitly:

- `/tailtest-test <file>` -- run the cycle on a specific file
- `/tailtest hunt <file>` -- one-shot adversarial pass on a specific file
- Or natural language ("test the file I just edited")

Each step (file write, terminal command, MCP call) prompts for approval. Safer default for first-time users.

### Auto mode (opt-in)

Enable Cline auto-approve for: Edit files (workspace), Execute safe commands, Use MCP servers. Then run `/tailtest-mode auto` and reload. After every edit, tailtest fires the test cycle automatically.

## Plan / Act mode (Cline-native UX bonus)

Cline's Plan / Act toggle maps to tailtest's SCENARIO PLAN convention: Plan mode produces the SCENARIO PLAN (read-only); review and amend; Act mode writes the test file, runs it, and applies R12 classification. Recommended for high-stakes files.

## Configuration

`.tailtest/config.json`:

```json
{
  "depth": "standard",
  "mode": "manual"
}
```

Depth options:
- `simple` -- 2-3 happy-path scenarios
- `standard` -- 5-8 scenarios including 2+ adversarial probes (default)
- `thorough` -- 10-15 scenarios including 4+ adversarial probes
- `adversarial` -- 8-12 scenarios biased toward breakage

See [tailtest.com/docs/config](https://tailtest.com/docs/config) for all options and [tailtest.com/docs/adversarial](https://tailtest.com/docs/adversarial) for adversarial mode details.

## Other tailtest variants

Same R1-R15 rule layer, same adversarial test mode, different host integration. **This repo is the Cline variant.**

- **[tailtest](https://github.com/avansaber/tailtest)** -- Claude Code plugin (hook-driven)
- **[tailtest-cursor](https://github.com/avansaber/tailtest-cursor)** -- Cursor plugin (hook-driven)
- **[tailtest-codex](https://github.com/avansaber/tailtest-codex)** -- Codex CLI plugin (hook-driven)
- **[tailtest-cline](https://github.com/avansaber/tailtest-cline)** -- Cline plugin (MCP-driven; this repo)

See [tailtest.com/demo/cline](https://tailtest.com/demo/cline) for a live walkthrough of this variant, or [tailtest.com/comparison](https://tailtest.com/comparison) for a feature matrix across all four.

## License

MIT.
