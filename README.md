# Wrath V2 — Grok Build control plane

**GPLv3.** Cold drive, profiles, modular policy engine, full lifecycle journal, privacy/fleet/IL modes, `/wrath-*` + MCP.

Not a second agent runtime. Heuristic guards — not a full sandbox ([SECURITY.md](SECURITY.md)).

## Install

```powershell
git clone https://github.com/Warexpor/wrath-addon.git
cd wrath-addon
.\install.ps1
.\install.ps1 -Rules   # optional ~/.grok/rules
```

Or: `grok plugin install . --trust` then reload plugins.

`install.ps1` reinstalls and **patches MCP to an absolute launcher path**.

Requires **Python 3.10+** and the `src/wrath` package (ships with the plugin).

## What you get (V2)

| Piece | Effect |
|-------|--------|
| SessionStart | Status line + drive pack + MCP self-heal |
| PreToolUse | Modular policy (nested shell depth 3, privacy, spawn model pin, footguns) |
| Full lifecycle | PermissionDenied, SubagentStart/Stop, Compact, SessionEnd, StopFailure |
| Profiles | `default` · `thin` · `strict` · `privacy` · `fleet` · `max` |
| Journal schema 2 | rule_id denials, subagents, harness denials |
| MCP | status, last_deny, policy_check (any tool), set_profile/privacy, session_report |

### Profiles

| Profile | Modes |
|---------|--------|
| default | Baseline guards, privacy upload **warn** |
| thin | Lighter privacy |
| strict | Strict denials + spawn model warn |
| privacy | Strict + privacy upload **deny** |
| fleet | orchestrate + il + spawn model warn |
| max | All of the above hard |

```toml
# .wrath.toml
version = 2
profile = "default"

[policy]
nested_shell_depth = 3
budget_tools = 80
reread_warn = 3
privacy_upload = "warn"   # off | warn | deny
require_spawn_model = "off"
deny = ["\\bnuke-prod\\b"]

[modes]
strict = false
```

Walks up from cwd / `GROK_PROJECT_DIR`. v1 configs still load.

### Overrides

| Env | Effect |
|-----|--------|
| `WRATH_ALLOW_FORCE=1` | Allow force-push main/master |
| `WRATH_ALLOW_HARD=1` | Allow `git reset --hard` |
| `WRATH_ALLOW_CLEAN=1` | Allow `git clean -f[dx]` |
| `WRATH_ALLOW_PIPE_EXEC=1` | Allow curl\|bash / iwr\|iex |
| `WRATH_STRICT=1` | Force STRICT |
| `WRATH_ORCHESTRATE=1` | Force fleet mode |
| `WRATH_IL=1` | Force IL dialect |
| `WRATH_PRIVACY=1` | Force privacy (bulk upload deny) |
| `WRATH_BUDGET_TOOLS=N` | Budget nudge threshold |
| `WRATH_REREAD_WARN=N` | Re-read warn threshold |
| `WRATH_NESTED_DEPTH=N` | Shell unwrap depth (1–8) |
| `WRATH_OFF=1` / `WRATH_ON=1` | Force runtime off/on |

## Commands

| Command | Effect |
|---------|--------|
| `/wrath` | Hub |
| `/wrath-on` / `/wrath-off` | Runtime |
| `/wrath-profile <name>` | Profile switch |
| `/wrath-privacy` | Privacy mode |
| `/wrath-strict` | Strict mode |
| `/wrath-orchestrate` | Fleet multi-model |
| `/wrath-il` | IL agent wire |
| `/wrath-status` · `/wrath-doctor` · `/wrath-why` | Inspect |
| `/wrath-thin` · `/wrath-check` · `/wrath-ship` · `/wrath-budget` · `/wrath-review` | Workflows |

## Verify

```powershell
python -m pytest
ruff check src hooks mcp tests
grok plugin details wrath
```

## Docs

- [HOOK_CONTRACT.md](docs/HOOK_CONTRACT.md) — Grok Build hook surface
- [SECURITY.md](SECURITY.md) — residual risk

## License

[GPL-3.0-or-later](LICENSE).
