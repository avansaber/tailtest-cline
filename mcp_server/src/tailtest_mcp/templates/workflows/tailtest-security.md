---
description: Show the current security posture for this project. Reports which scanners are enabled, how many new and baselined security findings exist, and which ruleset/depth is active.
---

# /tailtest-security

Show tailtest's security posture for this project.

## Behavior

1. Read `.tailtest/config.yaml` (or `.tailtest/config.json`) for security scanner config.
2. Read `.tailtest/baseline.yaml` for baselined security findings (the ones the user has accepted).
3. Read `.tailtest/reports/latest.json` for new security findings from the last run.
4. Output a structured report.

## Output format

```
tailtest security
Project root: {root}
Depth: {depth}  Hot-loop ruleset: {ruleset}

Scanners enabled:
  - {scanner_name}: {on | off}
  ...

Findings:
  New ({count}):
    {file}:{line} -- {finding description}
    ...
  Baselined ({count}):
    (use /tailtest-debt to review)
```

## Constraints

- Read-only. Does not modify any state.
- If `.tailtest/` does not exist: respond `tailtest not set up. Type "set up tailtest" first.`

## Trigger phrases

- `/tailtest-security`
- `tailtest security`
- `security posture`
- `what security issues has tailtest found`
