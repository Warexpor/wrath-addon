# Changelog

## 2.0.1 - 2026-07-16

### Removed
- Local bytecode/tool caches from working tree; tighten `.gitignore`
- Dead `Decision.with_warning` / unused `warnings` field; unused journal `KINDS` constant
- Machine-absolute path in repo `.mcp.json` (portable relative launcher; install still patches absolute)

### Fixed
- Hook tests no longer rewrite source-tree `.mcp.json` via SessionStart MCP heal (isolated `GROK_PLUGIN_ROOT`)

### Changed
- CI ruff scope includes `src/`

## 2.0.0 - 2026-07-16

### Added
- **V2 architecture**: `src/wrath/` package (policy, journal, modes, hooks_impl, mcp); thin hook shims
- **Profiles**: `default` · `thin` · `strict` · `privacy` · `fleet` · `max` (`/wrath-profile`, MCP `wrath_set_profile`)
- **Privacy mode**: bulk git bundle/archive, home tar/zip, cloud sync heuristics; `/wrath-privacy`, `WRATH_PRIVACY`
- **Nested shell depth 3** (configurable): multi-layer powershell/bash/cmd unwrap
- **Spawn orch gate**: warn/deny `spawn_subagent` without `model=` when orchestrate on
- **Full lifecycle hooks**: PermissionDenied, SubagentStart/Stop, Pre/PostCompact, SessionEnd, StopFailure
- **Journal schema v2**: `rule_id`, harness denies, subagent soft-return flags, session counters sidecar
- **MCP**: `wrath_status`, `wrath_last_deny`, `wrath_set_privacy`, `wrath_set_profile`, `wrath_session_report`; multi-tool `wrath_policy_check`
- Config schema v2 (`.wrath.toml` `version = 2`, `[policy]`, profiles); v1 still loads
- `docs/HOOK_CONTRACT.md` — Grok Build hook contract notes
- Skills: `/wrath-privacy`, `/wrath-profile`

### Changed
- Policy engine modularized into rule packs under `src/wrath/policy/rules/`
- Drive pack / status line include profile + privacy
- Doctor reports hook events + nested-shell smoke
- Plugin/package version **2.0.0**

### Fixed
- Re-read counting uses session counter sidecar (avoids full journal scan)
- Policy: preserve `rule_id` on warn decisions; canonicalize tool aliases (`Task`/`MultiEdit`/…)
- install.ps1 post-install hints aligned with V2 commands
- Tests cover privacy/profile toggles, nested PreToolUse, MCP V2 tool list

## 1.3.2 - 2026-07-15

### Fixed
- CI: ruff E501/I001 and format so GitHub Actions `ci` goes green again

## 1.3.1 — 2026-07-15

### Changed
- IL child return hard rules: one line only, no markdown fences, require `S:`+`Δ:` (or fail wire)
- Drive pack `IL_BODY` + skill/lexicon: lead must put return skeleton in `O:` for glm/deepseek; soft/fenced → `X:soft`
- LEXICON notes measured model compliance (composer high, deepseek medium, glm freeform low)

## 1.3.0 — 2026-07-15

### Added
- Wrath IL agent-wire dialect: `/wrath-il` · `il on` / off
- State flag `il` + env `WRATH_IL`
- Drive pack injects IL lexicon when il=on (SessionStart + toggle)
- Skill `wrath-il` (+ `LEXICON.md`); MCP `wrath_set_il`; CLI `il-on|off`
- Status line field `il=on|off`

### Changed
- Status line / set_enabled status / wrath_config report `il`
- Toggle parser ignores IL phrases for full runtime on/off

## 1.2.0 — 2026-07-15

### Added
- Multi-model fleet mode: `/wrath-orchestrate` · `multi-model on` / off
- State flag `orchestrate` + env `WRATH_ORCHESTRATE`
- Drive pack injects lead/specialist routing when orch=on (SessionStart + toggle)
- Skill `wrath-orchestrate`; MCP `wrath_set_orchestrate`; CLI `orchestrate-on|off`
- Status line field `orch=on|off`

### Changed
- Status line includes orchestrate; set_enabled status reports `orchestrate`

## 1.1.1 — 2026-07-15

### Fixed
- MCP failed after Grok restart when local-plugin sync reset `.mcp.json` to relative `mcp/run.py` / `mcp/launch.cmd` (Grok cwd ≠ plugin root)
- `install.ps1` now registers wrath in `~/.grok/config.toml` with absolute `launch.cmd` path (survives sync)
- SessionStart `ensure_mcp_config()` self-heals installed `.mcp.json` when paths drift
- Strict vs on/off toggle collision (`/wrath-strict` no longer parsed as turn-off)

### Added
- `mcp/launch.cmd` / `mcp/launch.sh` — cwd-independent MCP launchers (`%~dp0` / `$0`)

### Changed
- `install.ps1` patches absolute `launch.cmd` instead of `run.py`
- Doctor reports `mcp_command` + launcher path health

## 1.1.0 — 2026-07-15

### Added
- Project config `.wrath.toml` / `.wrath.json` (`deny`, `budget_tools`, `reread_warn`, `strict`)
- Nested shell unwrap (one level): powershell/pwsh -Command, bash -c, cmd /c
- SessionStart status line (version · ON/OFF · strict · budget · config)
- Soft same-path re-read warn; journal records `path`
- Write-guard: deny writes under `.git/`
- Strict state + `/wrath-strict` / phrases; `/wrath-why`
- MCP `wrath_config`; doctor reports MCP absolute path + fix

### Changed
- Shorter drive pack; skills MCP-first (status/ship/doctor)
- stop budget reads project config + env

## 1.0.1 — 2026-07-15

### Fixed / polished
- Tests use `tmp_path` only; untracked `tests/_data` (no dirty journal after pytest)
- Secret-path detector: `.env.*`, `service_account*.json`, `-sa.json`
- Version single-sourced from `.claude-plugin/plugin.json`
- Segment-splitter docstring: bare `|` is not split
- MCP dead `is_err` assignment removed
- `install.ps1`: prefer `plugin.json` name=wrath; drop empty `commands/`
- Hook fail-open errors → stderr + `hook_errors.jsonl`
- `WRATH_BUDGET_TOOLS`; STRICT force-push without branch
