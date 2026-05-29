# Security

## Scope

tailtest-cline is an MCP server plus a `.clinerules/` pack for Cline. The server:

- Reads files and manifests in the user's project to detect test runners
- Reads and writes `.tailtest/` (config, session state, reports) and the Memory Bank file `tailtestContext.md`
- Does not make network requests
- Does not collect or transmit data
- Does not execute arbitrary code; it returns structured tool results that instruct Cline to run test commands that the user's own project defines

## Reporting vulnerabilities

To report a security vulnerability, email support@avansaber.com.

Please include:
- A description of the vulnerability
- Steps to reproduce
- Potential impact

We will respond within 72 hours and aim to release a fix within 14 days of confirmation. Please do not file security reports through public GitHub issues.

## Supported versions

Only the latest release receives security fixes.

| Version | Supported |
|---------|-----------|
| 1.x     | Yes       |
