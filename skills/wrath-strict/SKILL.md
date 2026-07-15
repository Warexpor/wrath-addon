---
name: wrath-strict
description: Toggle Wrath STRICT mode (extra denies). Use for /wrath-strict, wrath strict on/off.
---

# wrath-strict

1. If user wants strict **off**: say “wrath-strict-off” intent — prefer writing state:

   Use MCP is not required; run:

   ```text
   python -c "import sys; sys.path.insert(0,'hooks'); from toggle import set_strict; print(set_strict(False, source='skill'))"
   ```

   Prefer from plugin root with `GROK_PLUGIN_ROOT` on path, or use UserPromptSubmit phrase `wrath-strict-off`.

2. If user wants strict **on** (default for bare `/wrath-strict`):

   Phrase `wrath-strict` or `set_strict(True)`.

3. Precedence: env `WRATH_STRICT` overrides state when set; else state OR project `.wrath.toml` `strict = true`.

4. Confirm effective strict via MCP `wrath_config`. Tell user what STRICT adds: SQL DROP, infra destroy, force-push without branch in argv.
