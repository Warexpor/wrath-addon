# Wrath addon bug audit

## Fixed in 1.0.0
1. MCP cwd bug — Grok started server with cwd=home → `mcp/run.py` missing. Fixed by `install.ps1` absolute path patch + `mcp/run.py` chdir to plugin root.
2. Hardcoded `C:\Users\amicu\...` in skills — removed; use env / plugin details / MCP.
3. DROP policy returned mixed Decision fields — split strict deny vs warn.
4. Journal full-file tail on large files — reverse-chunk tail.
5. No rotation — soft rotate at 8 MiB / 50k lines.
6. Multi-command `echo; rm -rf /` slipped past single-line-only patterns — segment split.
7. Missing remote pipe-to-shell and git clean -fdx gates.

## Fixed in 0.4.1
1. Mid-session ON toggle injects full drive pack.
2. Disabled hooks drain stdin before short-circuit.
3. Broader UserPromptSubmit field shapes.
4. session_id prefers payload over env.
5. MCP `run.py` launcher without `${GROK_PLUGIN_ROOT}` expansion.
6. Policy: format C:, rd/del drive root.
7. `.gitignore` for pytest/venv.

## Residual risks
1. Deny list is heuristic — not a full sandbox. Advanced PowerShell can still slip.
2. UserPromptSubmit unknown payload shapes may miss auto-toggle (skills/MCP still work).
3. Absolute MCP path in installed copy must be re-patched after `install.ps1` (done automatically).
4. Journal/data fallback to `~/.wrath-addon/data` if `GROK_PLUGIN_DATA` unset.
