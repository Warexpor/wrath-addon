---
name: wrath-why
description: Explain the last Wrath deny(s). Use for /wrath-why, why blocked, why denied.
---

# Wrath why

1. MCP **`wrath_last_deny`** (n=5) — prefer `rule_id` + reason.
2. If empty, `wrath_journal_tail` kind=`deny` or `harness_deny`.
3. Explain rule in one line; mention override env if applicable (`WRATH_ALLOW_*`, profile, privacy).
