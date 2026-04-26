# tailtest-cline

> You build. We cover. Across 8+ editors at once.

tailtest-cline is a [Cline](https://cline.bot) plugin that automatically generates and runs tests every time the agent edits a source file. Same R1-R15 rule layer as the other tailtest variants. Adversarial test mode (V13) shipped from day one.

**Cline reach:** VS Code, Cursor, JetBrains IDEs, Antigravity, Zed, Neovim, VSCodium, Windsurf, plus the Cline CLI. One plugin, eight-plus editors.

**[Full documentation at tailtest.com/docs/cline](https://tailtest.com/docs/cline)**

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

See [tailtest.com/comparison](https://tailtest.com/comparison) for a feature matrix.

## License

MIT.
