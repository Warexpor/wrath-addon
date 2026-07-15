---
name: wrath-on
description: Enable Wrath runtime (guards, drive pack, journal). Use for /wrath-on, "turn wrath on", "enable wrath".
---

# wrath-on

Enable Wrath for this machine (shared flag under plugin data).

1. Prefer MCP `wrath_set_enabled` with `enabled: true` if available.
2. Else run:

```text
python hooks/set_enabled.py on
```

Resolve `hooks/` via `GROK_PLUGIN_ROOT` when set, else `grok plugin details wrath` path.

3. Confirm stdout / MCP shows `"enabled": true`.
4. Tell the user: Wrath ON — guards + drive active. Mid-session “turn wrath on” also injects the drive pack via UserPromptSubmit.
