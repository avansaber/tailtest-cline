---
description: Change tailtest depth mode (simple, standard, thorough, adversarial). Soft-warns when picking adversarial without explanation.
---

# /tailtest-depth

Change the depth setting in `.tailtest/config.json`.

## Valid values

- `simple` -- 2-3 happy-path scenarios; R15 disabled (no adversarial scenarios)
- `standard` -- 5-8 scenarios including 2+ adversarial probes (default)
- `thorough` -- 10-15 scenarios including 4+ adversarial probes
- `adversarial` -- 8-12 scenarios biased toward breakage paths; bug-hunting as the default

## Behavior

1. Parse the value the user typed (`/tailtest-depth adversarial` or natural variants).
2. If the value is not in the list above: respond `Invalid depth "{value}". Valid: simple, standard, thorough, adversarial.`
3. Read `.tailtest/config.json`. Update `depth` to the new value. Write back.
4. Respond:
   - For simple: `tailtest depth set to simple. R15 adversarial scenarios are disabled. Tests will cover happy paths only.`
   - For standard: `tailtest depth set to standard. R15 fires with at least 2 adversarial scenarios per test.`
   - For thorough: `tailtest depth set to thorough. R15 fires with at least 4 adversarial scenarios per test.`
   - For adversarial: `tailtest depth set to adversarial. Every test will be 8-12 adversarial scenarios biased toward breakage. Use /tailtest-depth standard to revert.`

## Soft warnings

If the user picks `adversarial` and the project's runner is unproven (no recent passing test run), gently note: `Heads up: adversarial depth produces high-noise output until the codebase has a solid test foundation. You may prefer to start at standard.`

## Trigger phrases

- `/tailtest-depth <value>`
- `tailtest depth <value>`
- `set depth to <value>`
- `make tailtest more thorough`
