# Wrath — Grok Build addon

**GPLv3.** Cold drive, real on/off, footgun guards, journal, project config, `/wrath-*` workflows, local MCP.

Not a second agent runtime. Heuristic guards — not a full sandbox ([SECURITY.md](SECURITY.md)).

## Install

```powershell
git clone https://github.com/Warexpor/wrath-addon.git
cd wrath-addon
.\install.ps1
.\install.ps1 -Rules   # optional ~/.grok/rules
```

Or: `grok plugin install . --trust` then reload plugins.

`install.ps1` reinstalls and **patches MCP to an absolute `run.py` path**.

## What you get

| Piece | Effect |
|-------|--------|
| SessionStart | Status line (version · ON/OFF · strict · orch · budget · config) + drive pack |
| PreToolUse | Footguns + nested `powershell`/`bash -c` unwrap + `.git/` write block |
| Project config | `.wrath.toml` or `.wrath.json` in repo |
| Re-read warn | Soft warn after N same-path reads (default 3) |
| Skills | `/wrath-*` including `/wrath-strict` `/wrath-orchestrate` `/wrath-why` |
| MCP | doctor, config, policy_check, journal_tail, session_stats, set_enabled, set_orchestrate |

### Project config (optional)

```toml
# .wrath.toml  (or .wrath.json)
strict = false
budget_tools = 80
reread_warn = 3          # 0 = off
deny = ["\\bnuke-prod\\b"]
```

Walks up from cwd / `GROK_PROJECT_DIR`.

### Overrides

| Env | Effect |
|-----|--------|
| `WRATH_ALLOW_FORCE=1` | Allow force-push main/master |
| `WRATH_ALLOW_HARD=1` | Allow `git reset --hard` |
| `WRATH_ALLOW_CLEAN=1` | Allow `git clean -f[dx]` |
| `WRATH_ALLOW_PIPE_EXEC=1` | Allow curl\|bash / iwr\|iex |
| `WRATH_STRICT=1` | Env force STRICT (overrides state) |
| `WRATH_ORCHESTRATE=1` | Env force multi-model orchestrate mode |
| `WRATH_BUDGET_TOOLS=N` | Budget nudge threshold |
| `WRATH_REREAD_WARN=N` | Re-read warn threshold |
| `WRATH_OFF=1` / `WRATH_ON=1` | Force runtime off/on |

**Strict precedence:** env (if set) → state (`/wrath-strict`) OR project `strict`.

**Orchestrate:** `/wrath-orchestrate` · `multi-model on` — lead model judges; pin specialists (`composer-2.5-fast`, `glm-5.2`, `deepseek-v4-flash`, `mimo-v2.5`) on spawn. Env `WRATH_ORCHESTRATE` overrides state.

## Verify

```powershell
python -m pytest
ruff check hooks mcp tests
grok plugin details wrath
```

## License

[GPL-3.0-or-later](LICENSE).
