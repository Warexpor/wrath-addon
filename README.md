# Wrath — Grok Build addon

**GPLv3.** Makes stock [Grok Build](https://x.ai) sharper: cold drive, real on/off, hardened footgun guards, JSONL journal + session stats, `/wrath-*` workflows, local MCP.

Not a second agent runtime. Stays inside `grok`. Heuristic guards — not a full sandbox (see [SECURITY.md](SECURITY.md)).

## Install

```powershell
git clone https://github.com/Warexpor/wrath-addon.git
cd wrath-addon
.\install.ps1
# optional rules pack into ~/.grok/rules
.\install.ps1 -Rules
```

Or:

```powershell
grok plugin validate .
grok plugin install . --trust
```

`install.ps1` uninstalls+reinstalls (local installs are copies) and **patches MCP to an absolute `run.py` path** so the server starts even when Grok’s cwd is not the plugin root.

Reload plugins in the TUI (`Ctrl+L` → Plugins → `r`) or start a new session.

## What you get

| Piece | Effect |
|-------|--------|
| SessionStart drive pack | Brief / verify / YAGNI every session (when ON) |
| PreToolUse guards | Blocks root wipes, Format-Volume, force-push main, `reset --hard`, `git clean -fdx`, `curl\|sh` / `iwr\|iex`, drive-root `rd`/`del` (when ON) |
| Multi-command awareness | Policy evaluates `;` / `&&` / `\|\|` segments |
| **On/off flag** | “turn wrath on/off”, `/wrath-on`, `/wrath-off` — real hook skip |
| Journal | Tool/deny/fail/stop events; rotation; efficient tail |
| Skills | `/wrath` `/wrath-on` `/wrath-off` `/wrath-status` `/wrath-thin` `/wrath-check` `/wrath-budget` `/wrath-ship` `/wrath-doctor` `/wrath-review` |
| Agents | `wrath-reviewer`, `wrath-explorer` |
| MCP `wrath` | `wrath_journal_tail`, `wrath_doctor`, `wrath_budget_tips`, `wrath_set_enabled`, `wrath_policy_check`, `wrath_session_stats` |

### On / off

```text
turn wrath off          # UserPromptSubmit sets flag → guards stop
turn wrath on
/wrath-off
/wrath-on
python hooks/set_enabled.py status|on|off
```

Flag file: `$GROK_PLUGIN_DATA/wrath_state.json` (or `~/.wrath-addon/data/wrath_state.json`).

Full unload: `grok plugin disable wrath`.

### Overrides

| Env | Effect |
|-----|--------|
| `WRATH_ALLOW_FORCE=1` | Allow force-push to main/master (and STRICT force-push) |
| `WRATH_ALLOW_HARD=1` | Allow `git reset --hard` |
| `WRATH_ALLOW_CLEAN=1` | Allow `git clean -f[dx]` |
| `WRATH_ALLOW_PIPE_EXEC=1` | Allow `curl\|bash` / `iwr\|iex` |
| `WRATH_STRICT=1` | SQL DROP, infra destroy, force-push when branch omitted |
| `WRATH_BUDGET_TOOLS=N` | Soft stop-hook budget nudge after N tool events (default 80) |
| `WRATH_OFF=1` | Force runtime off (env) |
| `WRATH_ON=1` | Force runtime on (env) |

## Verify

```powershell
python -m pytest
ruff check hooks mcp tests
grok plugin details wrath
```

## Layout

```
wrath-addon/
  .claude-plugin/plugin.json   # version single source
  hooks/          # policy + journal + lifecycle
  skills/         # /wrath-*
  agents/
  mcp/            # stdio MCP (cwd-independent launcher)
  rules/WRATH.md
  install.ps1
  LICENSE         # GPL-3.0
```

## License

[GNU General Public License v3.0 or later](LICENSE).
