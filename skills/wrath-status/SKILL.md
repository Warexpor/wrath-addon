---
name: wrath-status
description: Show Wrath plugin session health and recent journal events. Use for /wrath-status or when the user asks if Wrath is working.
---

# wrath-status

1. Prefer MCP `wrath_doctor` + `wrath_journal_tail` (n=12).
2. Else:

```text
python hooks/set_enabled.py status
```

and tail `journal.jsonl` under `GROK_PLUGIN_DATA` or `~/.wrath-addon/data`.

3. Report ≤8 bullets: **enabled?**, plugin present?, journal path, last events, deny count, any MCP issues.
4. Do not invent metrics.
