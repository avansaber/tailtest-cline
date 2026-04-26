---
description: Show tailtest's current state for this project: detected stack, depth, mode, last run, baseline count.
---

# /tailtest-status

Read `.tailtest/config.json`, `.tailtest/session.json`, `.tailtest/baseline.yaml` (if present), and `.tailtest/reports/latest.json` (if present). Output a compact status block in plain text, no markdown headers.

## Output format

```
tailtest status
Project root: {project_root}
Language: {language}  Framework: {framework or "(none)"}  Runner: {runner}
Depth: {depth}  Mode: {mode}  Paused: {true|false}

Last run: {timestamp or "(no run yet)"}
  Files covered: {generated_tests count}
  Real bugs: {real_bug count}
  Environment failures: {environment count}
  Test bugs: {test_bug count}

Baseline: {baseline entries count} accepted findings (.tailtest/baseline.yaml)
```

## Behavior

1. Read config from `.tailtest/config.json` (depth, mode).
2. Read session state from `.tailtest/session.json` (paused flag, generated_tests, runners).
3. If `.tailtest/reports/latest.json` exists, parse it for last-run R12 stats.
4. If `.tailtest/baseline.yaml` exists, count accepted entries.
5. Output the block above.

If `.tailtest/` does not exist: respond `tailtest not set up in this project. Type "set up tailtest" to bootstrap.`

This command is read-only. It does not modify any state.

## Trigger phrases

- `/tailtest-status`
- `tailtest status`
- `what is tailtest doing`
