---
description: Show a compact summary of the current tailtest session: files covered, fix attempts, deferred failures, unresolved.
---

# /tailtest-summary

Output a plain-text session summary block.

## Behavior

Read `.tailtest/session.json`. If the file does not exist: respond `No tailtest session active in this directory.` If `generated_tests` is empty: respond `No tests were generated this session.`

## Output format

```
tailtest session summary
Runner: {language}/{command}  Depth: {depth}

{N} file(s) covered:
  {source_file}  →  {test_file}  {status}
  ...

{N} fixed, {N} deferred, {N} unresolved.
```

Status per file:

- `passed` -- file is in `generated_tests` and NOT in `fix_attempts`
- `fixed (N attempt(s))` -- file is in `fix_attempts` with count 1 or 2, and NOT in `deferred_failures`
- `deferred` -- file is in `deferred_failures`
- `unresolved` -- file is in `fix_attempts` with count = 3 and NOT in `deferred_failures`

After the in-conversation summary, also write the same block to the file at `report_path` in session.json (default `.tailtest/reports/`). Create the directory if it does not exist.

## Trigger phrases

- `/tailtest-summary`
- `tailtest summary`
- `what did tailtest do`
- `what did you test`
