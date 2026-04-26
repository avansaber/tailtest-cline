---
description: Review accepted-debt baseline. Shows findings tailtest has baselined (hidden from the hot loop) so the user can audit, re-open, or clean up stale entries.
---

# /tailtest-debt

Show the accepted-debt baseline. The baseline is the set of findings the user has explicitly chosen to defer or accept. These findings are hidden from the regular tailtest run loop so the user is not nagged about them every session.

## Behavior

1. Read `.tailtest/baseline.yaml`. If absent: respond `No baseline set. Type "tailtest accept <finding>" to baseline a finding.`
2. Output each entry in the baseline with:
   - File path
   - Description (truncated if long)
   - Acceptance date
   - Reason (if recorded)
3. After listing, ask: `Want to re-open any of these (re-surface in next run)? Type "tailtest reopen <file>" or "tailtest reopen all".`

## Optional commands the user can give next

- `tailtest reopen <file>` -- remove that file's entry from baseline; tailtest flags it again on next run.
- `tailtest reopen all` -- empty the baseline.
- `tailtest accept <finding>` -- add a finding to the baseline.

## Trigger phrases

- `/tailtest-debt`
- `tailtest debt`
- `show baseline`
- `what bugs has tailtest accepted`
