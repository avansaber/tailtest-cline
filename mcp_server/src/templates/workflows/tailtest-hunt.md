---
description: Run an adversarial pass on a specific file -- explicitly try to break the source code with R15 categories.
---

# /tailtest hunt <file>

Forces an adversarial-biased test pass on the named file regardless of project depth setting. Writes to a separate hunt test file so the main suite is not contaminated.

## Behavior

1. Read the source file at the named path.
2. Generate 8-12 adversarial scenarios drawn from the R15 categories (boundary inputs, format/injection, type confusion, concurrent state, time/locale edges, partial failures, resource exhaustion, off-by-one logic).
3. Pick categories that genuinely apply to this file. Skip categories that do not (state which were skipped and why).
4. Output a SCENARIO PLAN with each scenario labeled `[adversarial: <category>]`.
5. Write the test file at the **separate hunt path** (NOT the regular test file):

   | Source | Hunt test file |
   |---|---|
   | `services/billing.py` | `tests/test_billing_hunt.py` |
   | `app/Http/Controllers/OrderController.php` | `tests/Feature/OrderControllerHuntTest.php` |
   | `internal/handler.go` | `internal/handler_hunt_test.go` |
   | `components/Button.tsx` | `__tests__/Button_hunt.test.tsx` |

6. Run the hunt test file using the appropriate runner.
7. Apply R12 classification on any failures: `real_bug` / `environment` / `test_bug`.
   - Prefer the MCP tool `tailtest_classify_failures(runner_output)` when available.
8. Report:
   - All pass: `tailtest hunt: {N} adversarial scenarios on {file}, all passed.`
   - Any fail: list each failing scenario with its category and R12 classification, e.g. `[adversarial: type-confusion] real_bug -- function returns None on int input where str expected.`

## Bypass behavior

This skill bypasses `depth` from `.tailtest/config.json`. Even at `depth: simple` (which normally generates 0 adversarial scenarios per R15), `/tailtest hunt` runs the full 8-12 adversarial pass on the named file.

## Constraints

- **Do not auto-fix.** Always ask before fixing any `real_bug` found by hunt.
- **No update-existing-tests behavior.** Hunt always writes to the separate hunt test file. If the hunt file already exists, replace its contents (the user is asking for a fresh hunt).
- Treat the named file as `new-file` regardless of git status.
- Update `.tailtest/session.json` `generated_tests` to record the hunt test file mapping (source -> hunt test file).

## After the hunt

The user reviews the hunt test file and decides:
- Keep it (gitignore the `_hunt` suffix; the file is reference material)
- Merge selected hunt scenarios into the main test file
- Discard the hunt file
