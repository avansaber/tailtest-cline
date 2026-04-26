# tailtest project context

**Detected:** {{detection_date}} by `tailtest_setup`
**Plugin version:** tailtest-cline {{plugin_version}}
**Mode:** {{mode}} (auto = fires after every edit; manual = invoke via `/tailtest-test`)

## Stack

- Language: {{language}}
- Framework: {{framework}}
- Runner: {{runner}}
- Test directory: {{test_dir}}

## tailtest config

- Depth: {{depth}} (default: standard)
- Baseline file: `.tailtest/baseline.yaml` ({{baseline_count}} entries)
- Last run report: `.tailtest/reports/latest.json`

## R15 adversarial mode

Tailtest probes for bugs at standard or higher depth (R15 always-on). The 8 adversarial categories: boundary inputs, format / injection, type confusion, concurrent state, time / locale edges, error handling under partial failures, resource exhaustion, off-by-one logic.

To explicitly hunt for bugs in a specific file: `/tailtest hunt <file>`.

## Cline integration notes

Tailtest uses three Cline primitives:

- `.clinerules/` rule pack carries the rule layer (R1-R14 + R15 + framework templates).
- `tailtest-mcp` server provides structured tools (scenario_plan, classify_failures, pick_template, setup).
- This file (`memory-bank/tailtestContext.md`) provides per-session project context.

## Notes

(Add project-specific notes here. Tailtest will preserve user-added content on subsequent setup runs.)
