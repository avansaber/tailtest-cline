---
description: Run tailtest's full test cycle on a specific file. Manual-mode counterpart to auto mode's automatic post-edit firing.
---

# /tailtest-test <file>

Trigger the tailtest cycle on the named file. Use this when not running in auto mode, or when you want to explicitly cover a legacy file that tailtest would normally skip.

## Behavior

Apply the rules in `.clinerules/01-tailtest-baseline.md` Steps 0 through 6:

1. Verify APIs (Step 0): read the source file and confirm imports and named attributes resolve.
2. Generate scenarios (Step 3): output a SCENARIO PLAN respecting the project's depth setting and R15. Prefer the MCP tool `tailtest_scenario_plan(file_path)` when the `tailtest-mcp` server is available.
3. Write the test file (Step 4): use the language-and-framework-appropriate path and naming.
4. Execute (Step 5): run the test file with the configured runner. Apply R12 classification on any failures (prefer `tailtest_classify_failures` MCP tool).
5. Report (Step 6).

## When to use this instead of auto mode

- Project has not enabled auto-approve for workspace edits (manual mode default).
- File is something tailtest would normally skip (e.g. legacy file with no existing tests). Slash invocation overrides Step 2 filters for the named file.
- You want a specific test cycle now without waiting for auto-mode to fire on next edit.

## Bypass behavior

`/tailtest-test` treats the named file as `new-file` regardless of git status. Step 2 filters do NOT apply to slash-invoked targets.

## Constraints

- **Do not auto-fix.** Always ask before fixing any failure.
- If a test file already exists for this source, update it (do not regenerate scenarios that already pass) per Step 4 rules.
- Update `.tailtest/session.json` `generated_tests` after writing.
