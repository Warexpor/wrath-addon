---
name: wrath-doctor
description: Diagnose Wrath plugin install (hooks, python, MCP, data dir). Use for /wrath-doctor or when hooks/MCP seem missing.
---

# wrath-doctor

1. Prefer MCP `wrath_doctor` if available — print its JSON fields as a checklist.
2. Else check:
   - `python --version`
   - Plugin root (`GROK_PLUGIN_ROOT` or installed-plugins path with `mcp/run.py`)
   - `hooks/hooks.json` and `hooks/pre_tool_use.py`
   - Data dir writable (`GROK_PLUGIN_DATA` or `~/.wrath-addon/data`)
   - `.mcp.json` args point at an existing `run.py` (absolute preferred)
3. Dry-run: MCP `wrath_policy_check` with `rm -rf /` (expect deny) and `git status` (expect allow).
4. Pass/fail only. Fix: `.\install.ps1` or `grok plugin install <path> --trust` then reload plugins.
