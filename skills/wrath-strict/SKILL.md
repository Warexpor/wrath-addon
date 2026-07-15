---
name: wrath-strict
description: Toggle Wrath STRICT mode (extra denies). Use for /wrath-strict, wrath strict on/off.
---

# wrath-strict

1. Prefer natural phrases (UserPromptSubmit handles them):
   - on: `wrath-strict` or `/wrath-strict`
   - off: `wrath-strict-off`
2. Or CLI from plugin hooks dir:

```text
python set_enabled.py strict-on
python set_enabled.py strict-off
python set_enabled.py status
```

Resolve hooks via `GROK_PLUGIN_ROOT/hooks` when set.

3. Confirm with MCP `wrath_config` (`strict` field).
4. Precedence: env `WRATH_STRICT` if set → else state OR project `strict = true`.
5. STRICT adds: SQL DROP, infra destroy, force-push when branch omitted from argv.
