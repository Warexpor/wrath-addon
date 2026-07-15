---
name: wrath-doctor
description: Diagnose Wrath plugin install (hooks, python, MCP, data dir). Use for /wrath-doctor or when hooks/MCP seem missing.
---

# Wrath doctor

Call MCP **`wrath_doctor`**. Check:

- `src_package` true, `hooks_json` true, hook_events includes PreToolUse + Subagent*
- `policy_smoke.deny_rm_root` and `deny_nested_shell` true
- MCP absolute path (`fix` empty)
- version 2.x

If MCP broken: run `.\install.ps1` from the wrath-addon repo.
