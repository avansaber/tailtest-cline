# tailtest-cline -- install and first run

Tailtest for Cline. MCP server + `.clinerules/` rule pack + Memory Bank integration.

## Install (three paths)

### Path 1: Cline MCP Marketplace (recommended; one click)

Open Cline's Extensions panel inside your IDE. Search for `tailtest`. Click install. Cline:

1. Clones this repo to `~/Documents/Cline/MCP/tailtest-cline/` (or `Documents\Cline\MCP\` on Windows)
2. Runs `pip install -e .` to install dependencies (`mcp[server]` + `pyyaml`)
3. Adds the server entry to `cline_mcp_settings.json` automatically
4. Server is ready immediately

### Path 2: Direct GitHub install

Paste `https://github.com/avansaber/tailtest-cline` into Cline's MCP server install dialog. Cline clones, installs, and registers the server. Same outcome as Path 1.

### Path 3: Manual `cline_mcp_settings.json` edit

Add the server entry yourself:

```json
{
  "mcpServers": {
    "tailtest": {
      "command": "python",
      "args": ["-m", "mcp_server.src.server"],
      "cwd": "/path/to/tailtest-cline",
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

Use Path 3 when running locally during development or when Path 1 is not yet possible (private repo phase).

## First run

After install, Cline shows `tailtest` in its tool list. To set up tailtest in a project:

1. Open the project in Cline.
2. Type in chat: **"set up tailtest in this project"**.
3. Cline calls the `tailtest_setup` MCP tool. The tool detects language / framework / runner, writes `.clinerules/` (rule pack), writes `.clinerules/workflows/` (slash commands), seeds `memory-bank/tailtestContext.md`, and initialises `.tailtest/config.json` + `.tailtest/session.json`.
4. **Important:** Cline does not auto-reload `.clinerules` mid-conversation. Start a new conversation (or reload the window) for tailtest to take effect.

That is the whole setup. No CLI commands. No config to edit by hand. The setup tool is idempotent: if you already have a `.clinerules/` or a Memory Bank, existing files are preserved.

## Two operating modes

### Manual mode (default)

You invoke the test cycle explicitly via:

- `/tailtest-test <file>` -- run the full cycle on a specific file
- `/tailtest hunt <file>` -- one-shot adversarial pass on a specific file
- Natural language ("test the file I just edited")

Manual mode requires no special Cline auto-approve setting. Each step (file write, terminal command, MCP call) prompts for approval. This is the safer default for first-time users.

### Auto mode (opt-in)

After every code edit, tailtest fires the test cycle automatically. To enable:

1. In Cline settings, enable auto-approve for:
   - **Edit files (workspace)**
   - **Execute safe commands**
   - **Use MCP servers**
2. Run `/tailtest-mode auto` (or invoke setup with `mode: "auto"`).
3. Reload the window.

After this, edit a source file and tailtest will write tests, run them, and surface any failures with R12 classification, all without prompting.

To switch back: `/tailtest-mode manual`.

## Plan mode + Act mode (Cline-native UX bonus)

Cline has a Plan / Act mode toggle that maps perfectly to tailtest's SCENARIO PLAN convention:

1. Toggle Plan mode in Cline.
2. Type `/tailtest-test <file>` (or natural language).
3. Cline produces a SCENARIO PLAN (read-only; no file edits yet).
4. Review the plan; amend if you want.
5. Toggle Act mode.
6. Cline writes the test file, runs it, and applies R12 classification.

This is one of the few axes on which Cline integration beats Claude Code's hook model: the human review gate between scenario design and test code is enforced by the UX, not by rule compliance. Recommended for high-stakes files.

## What gets installed in your project

After running `tailtest_setup`, you have:

```
your-project/
├── .clinerules/
│   ├── 01-tailtest-baseline.md      (the rule layer; 451 lines)
│   └── workflows/
│       ├── tailtest-hunt.md
│       └── tailtest-test.md
├── .tailtest/
│   ├── config.json                  ({"depth": "standard", "mode": "manual"})
│   └── session.json                 (runtime state; gitignored if you want)
└── memory-bank/
    └── tailtestContext.md           (project profile; agent reads each session)
```

Recommended `.gitignore` additions:

```
.tailtest/session.json
.tailtest/reports/
.tailtest/baseline.yaml
tests/test_*_hunt.py     # hunt test files (optional; commit if you want to keep them)
```

The `.clinerules/` directory itself is intended to be committed so the team-shared rule layer travels with the repo.

## Verifying the install works

After setup + reload, in Cline chat type: `tailtest ping`. The agent should call `tailtest_ping` and return:

```
tailtest-mcp v1.0.0-rc1 reachable. V14.1 scenario_plan tool live.
```

If you see this, the MCP server is reachable and tools are wired.

## What ships from V14.0 to V14.3

- 5 MCP tools: `tailtest_ping`, `tailtest_scenario_plan`, `tailtest_classify_failures`, `tailtest_pick_template`, `tailtest_setup`
- 2 slash workflows: `/tailtest hunt`, `/tailtest-test`
- 1 always-on rule file: `01-tailtest-baseline.md` (R1-R14 + R15 adversarial mode + 8 categories + framework templates for Flask / FastAPI / Django / NestJS / Spring Boot / Kotlin / C#)
- Memory Bank integration via 7th file `tailtestContext.md`

V14.4 adds 8 more slash workflows (`/tailtest-status`, `/tailtest-debt`, `/tailtest-report`, `/tailtest-depth`, `/tailtest-gen`, `/tailtest-scan`, `/tailtest-security`, `/tailtest-mode`).

## Troubleshooting

- **"tailtest does not respond after I edit a file"**: you may be in manual mode (the default). Run `/tailtest-test <file>` or switch to auto mode.
- **"`/tailtest-test` does not appear in the slash menu"**: the workflow files were written but Cline has not reloaded. Start a new conversation.
- **"the setup tool writes to a directory I do not want"**: `tailtest_setup` is idempotent; existing files are not overwritten. To start clean, delete `.clinerules/` + `memory-bank/tailtestContext.md` + `.tailtest/` and re-run.
- **MCP tools listed in Cline but agent does not call them**: in manual mode, the agent calls tools when the rule layer instructs it (e.g., during `/tailtest-test`). In auto mode, the agent calls them after every edit. Confirm `.clinerules/01-tailtest-baseline.md` exists and Cline has reloaded.

## Where to ask for help

GitHub issues: https://github.com/avansaber/tailtest-cline/issues
Docs: https://tailtest.com/docs/cline (V14.6+)

## License

MIT. Same as the other tailtest variants.
