---
name: wrath-status
description: Show Wrath plugin session health and recent journal events. Use for /wrath-status or when the user asks if Wrath is working.
---

# wrath-status

1. Prefer MCP in this order:
   - `wrath_config` — enabled, strict, budget, project config
   - `wrath_doctor` — paths + MCP absolute path + policy smoke
   - `wrath_journal_tail` with `n=12`
2. Only if MCP unavailable: `python hooks/set_enabled.py status` and tail journal under `GROK_PLUGIN_DATA` or `~/.wrath-addon/data`.
3. Report ≤8 bullets: **enabled?**, **strict?**, **orchestrate?**, **il?**, version, config path, journal denials, MCP fix if any.
4. Do not invent metrics.
