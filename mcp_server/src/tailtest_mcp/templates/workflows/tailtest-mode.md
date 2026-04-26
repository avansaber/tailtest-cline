---
description: Switch tailtest between auto mode (fires after every edit) and manual mode (user invokes /tailtest-test).
---

# /tailtest-mode <auto|manual>

Toggle tailtest's operating mode.

## Modes

### Manual mode (default)

The user invokes the test cycle explicitly via:

- `/tailtest-test <file>` -- run the cycle on a specific file
- `/tailtest hunt <file>` -- one-shot adversarial pass

Each step (file write, terminal command, MCP call) prompts for approval. Safer for first-time users.

### Auto mode (opt-in)

After every code edit, tailtest fires the test cycle automatically. Requires Cline auto-approve to be enabled for:

- Edit files (workspace)
- Execute safe commands
- Use MCP servers

## Behavior

1. Parse the mode the user typed.
2. If invalid: respond `Invalid mode "{value}". Valid: auto, manual.`
3. Read `.tailtest/config.json`. Update `mode` field. Read `.tailtest/session.json` and update its `mode` field too. Write both back.
4. Respond:
   - For `auto`: `tailtest is now in auto mode. After every code edit, the test cycle will run automatically. This requires Cline auto-approve to be enabled for: 'Edit files (workspace)', 'Execute safe commands', 'Use MCP servers'. If you have not enabled those, tailtest will prompt for each step.`
   - For `manual`: `tailtest is now in manual mode. Run the test cycle by typing /tailtest-test <file> after edits. To enable hands-off auto firing, run /tailtest-mode auto and enable Cline auto-approve.`

## Trigger phrases

- `/tailtest-mode auto`
- `/tailtest-mode manual`
- `tailtest mode auto`
- `enable tailtest auto`
- `disable tailtest auto`
