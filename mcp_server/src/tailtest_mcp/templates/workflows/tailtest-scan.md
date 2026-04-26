---
description: Scan the project and report detected language, runner, framework, AI surface classification, and likely_vibe_coded flag.
---

# /tailtest-scan

Run the project scanner and present a structured snapshot of what tailtest sees in this project.

## Behavior

1. Walk the project directory (skipping `node_modules`, `.venv`, `.git`, `dist`, `build`, `__pycache__`, `target`).
2. Detect the dominant language by counting source files per extension.
3. Detect the runner using the same logic as `tailtest_setup` (pyproject.toml / package.json / pom.xml etc.).
4. Detect the framework where applicable (Flask, FastAPI, Django, NestJS, Spring Boot, etc.).
5. Detect AI-surface markers: `.claude-plugin/`, `.codex-plugin/`, `.cursor-plugin/`, `.clinerules/`, `memory-bank/`, `CLAUDE.md`, `AGENTS.md`.
6. Compute a `likely_vibe_coded` flag: true if the project has AI-surface markers AND no test directory.

## Output

```
tailtest scan
Project root: {root}
Languages detected: {lang1: {count}, lang2: {count}, ...}
Dominant language: {lang}
Runner: {runner}
Framework: {framework or "(none)"}
Test directory: {test_dir or "(none found)"}

AI surfaces:
  - .clinerules/ ({yes | no})
  - memory-bank/ ({yes | no})
  - CLAUDE.md ({yes | no})

Likely vibe-coded: {true | false}
```

If `likely_vibe_coded: true`, the agent gently surfaces: `tailtest noticed AI-surface markers but no test directory. Want me to set up tailtest and seed an initial coverage scan?` (links to `/tailtest-setup` and the ramp-up flow.)

## Constraints

- Read-only. Does not modify any state.
- Bound the walk: stop after 200 source files counted.

## Trigger phrases

- `/tailtest-scan`
- `tailtest scan`
- `what does tailtest see in this project`
- `analyze this project`
