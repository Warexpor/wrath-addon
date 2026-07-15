---
name: wrath-budget
description: Spend SuperGrok/API tokens efficiently. Use for /wrath-budget, token waste, context bloat, or long sessions burning the weekly pool.
---

# wrath-budget

Operate to minimize tokens per feature shipped:

1. Grep/list before whole-file reads; avoid re-reading the same file.
2. Prefer small targeted edits over rewriting large files.
3. Subagents: only when parallel independent work; inherit parent model when project rules say so.
4. No filler progress essays; no multi-agent theater for a one-file fix.
5. If MCP available: `wrath_budget_tips` and optional `wrath_session_stats` with current session id.
6. Reply with ≤6 concrete actions for **this** session (not generic AI tips).
