---
name: wrath-why
description: Explain the last Wrath deny(s). Use for /wrath-why, why blocked, why denied.
---

# wrath-why

1. MCP `wrath_journal_tail` with `kind=deny` and `n=5`.
2. For the latest deny: tool, command/path, reason — one short paragraph.
3. If override exists (WRATH_ALLOW_*), name it; do not enable it without user ask.
4. Optional: MCP `wrath_policy_check` with the same command to reconfirm.
5. If no denies: say so. Do not invent history.
