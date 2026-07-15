---
name: wrath-doctor
description: Diagnose Wrath plugin install (hooks, python, MCP, data dir). Use for /wrath-doctor or when hooks/MCP seem missing.
---

# wrath-doctor

1. Call MCP `wrath_doctor` — treat JSON as checklist.
2. Call MCP `wrath_config` for effective strict/budget/project file.
3. If `mcp_args_absolute` is false or `mcp_run_exists` is false: run the `fix` field (usually `.\install.ps1`) then reload plugins.
4. Smoke: MCP `wrath_policy_check` with `rm -rf /` (deny) and `git status` (allow).
5. Pass/fail bullets only. No essay.
