---
name: wrath-off
description: Disable Wrath runtime (guards, drive pack, journal). Use for /wrath-off, "turn wrath off", "disable wrath". Plugin stays installed.
---

# wrath-off

Disable Wrath runtime without uninstalling the plugin.

1. Prefer MCP `wrath_set_enabled` with `enabled: false`.
2. Else:

```text
python hooks/set_enabled.py off
```

Use `GROK_PLUGIN_ROOT` or path from `grok plugin details wrath`.

3. Confirm `"enabled": false`.
4. Tell the user: Wrath OFF — no PreToolUse denies / drive pack / journal. `/wrath-on` or “turn wrath on” to re-enable. `grok plugin disable wrath` fully unloads the plugin.
