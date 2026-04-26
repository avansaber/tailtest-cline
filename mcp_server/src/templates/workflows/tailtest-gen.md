---
description: Generate a starter test file for a given source file. Writes a review-before-committing header. Runs a compile check before returning.
---

# /tailtest-gen <file>

Generate an initial test file for a source file. Useful for legacy code where no test file exists yet. Differs from `/tailtest-test`: gen produces a starter scaffold with a review header; test does the full cycle (write + run + classify).

## Behavior

1. Read the source file.
2. Call MCP tool `tailtest_pick_template(file_path)` to get the framework template.
3. Output a SCENARIO PLAN (apply R15 per the rule layer).
4. Write a starter test file at the framework-appropriate path.
5. Add a review header at the top of the test file:

   ```python
   # tailtest gen: starter scaffold
   # Review before committing. Each scenario is a hypothesis that should be either:
   #   - confirmed (run the test, verify it passes for a real bug it caught), or
   #   - removed (the scenario does not apply to this code).
   # Auto-generated 2026-04-25 by tailtest gen.
   ```

6. Run a compile check (`python3 -c "import ast; ast.parse(open('test_x.py').read())"` for Python; `tsc --noEmit` for TypeScript).
7. If compile check fails: report the error, do NOT delete the file (user can fix and re-run).
8. Do NOT execute the tests. Gen produces a scaffold for review; execution comes from the user running them manually or via `/tailtest-test`.

## When to use this vs /tailtest-test

- `/tailtest-gen <file>`: starter scaffold for review. Compile check only. No execution.
- `/tailtest-test <file>`: full cycle. Generate + write + run + classify. Use when the source is recent and you want immediate feedback.

## Trigger phrases

- `/tailtest-gen <file>`
- `tailtest gen <file>`
- `generate tests for <file>`
- `start tests for <file>`
