---
description: Open the latest tailtest report. HTML view if available; falls back to JSON summary.
---

# /tailtest-report

Show the most recent tailtest run report.

## Behavior

1. Look for `.tailtest/reports/latest.html`. If present, summarise its key sections: file count, R12 stats, runner output snippet, any real_bug findings.
2. Otherwise read `.tailtest/reports/latest.json`. If present, format the JSON as a readable plain-text summary.
3. If neither exists: respond `No report yet. Run /tailtest-test <file> to produce one.`

## Output format

```
tailtest report ({report timestamp})

Files covered ({N}):
  {source_file} -> {test_file} ({pass | fail count})

Failures classified ({total}):
  real_bug ({count}):
    {failing test name} -- {one-line reason}
  environment ({count}):
    ...
  test_bug ({count}):
    ...

Pending:
  {N} fix attempts in progress
  {N} deferred failures
```

## Constraints

- Read-only. Does not modify any state.
- Truncate long output: if the report has > 50 entries, show the first 25 + a count of remaining.

## Trigger phrases

- `/tailtest-report`
- `tailtest report`
- `show last run`
- `what did tailtest find`
