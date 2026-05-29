# Contributing to tailtest-cline

Thanks for contributing to tailtest-cline. Here is how to get a change in.

## Code of conduct

Participation in this project is governed by the [Code of Conduct](CODE_OF_CONDUCT.md).

## Filing issues

Use the [issue tracker](https://github.com/avansaber/tailtest-cline/issues). When filing a bug, please include:

- tailtest-cline version (from the `README.md` badge or `pyproject.toml`)
- Cline version and the host editor you are running it in (VS Code, Cursor, JetBrains, etc.)
- Operating system and version (macOS or Linux)
- Repro steps, expected behavior, and actual behavior
- Relevant excerpts from `.tailtest/reports/latest.json` if applicable

## Submitting changes

1. Fork the repo and create a topic branch off `main`.
2. Make your change. Keep commits focused and the diff small where possible.
3. Run the test suite (see below) and confirm it is green.
4. Open a pull request against `main` with a clear description of what changed and why.

Contributor email is not required, and the project does not collect Co-Authored-By signing data.

## Running tests

The MCP server uses pytest with `pytest-asyncio` for the async tools.

```bash
pip install -e ".[dev]"
pytest -q
```

To run a single test file or test:

```bash
pytest tests/test_scenario_plan.py -q
pytest tests/test_scenario_plan.py::test_specific_case -q
```

## Adding a new R rule

The R1-R15 rule layer lives under `clinerules/`. New rules should extend that pack using the same shape as existing rules. The deterministic policy that backs the rules (depth tiers, adversarial counts, framework templates, file paths) lives in MCP server code under `mcp_server/src/tailtest_mcp/`.

## Adding a new language baseline or framework template

Framework templates and runner detection live inside `mcp_server/src/tailtest_mcp/`. Add the new template and its detection there, then add tests under `tests/` that mirror existing template tests.

## Release process

Releases are tagged from `main`. Update `CHANGELOG.md` in the same PR as the user-visible change, following the existing per-version section shape. Maintainers handle the GitHub Release upload after a tag lands.

## License of contributions

By submitting changes you agree they are MIT-licensed under the project [LICENSE](LICENSE).
