# Changelog

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
- `pyproject.toml`, GitHub Actions CI, `SECURITY.md`, ruff format, LF for Python

## 1.0.0 — 2026-07-15

### Added
- GPLv3 license; public repo packaging
- MCP tools: `wrath_policy_check`, `wrath_session_stats`
- Journal: efficient reverse tail, kind/session filters, rotation, session stats
- Policy: multi-command segments, `git clean -fdx`, remote pipe-to-shell, branch delete main, SQL DROP warn/strict, infra destroy (strict)
- Hook: `PostToolUseFailure` journaling
- Skill: `/wrath-review`
- Stop-hook soft budget nudge after high tool volume
- `install.ps1` absolute MCP path patch (fixes cwd ≠ plugin root)

### Fixed
- MCP server failed when Grok started it with home cwd (`mcp/run.py` not found)
- Skills no longer hardcode a single user machine path
- Policy DROP decision no longer mixed allow+deny fields

### Changed
- Version 0.4.1 → 1.0.0
- Hardened agents/rules drive pack
- Doctor reports policy smoke + MCP path presence

## 0.4.1

- On/off flag, journal, footgun guards, basic MCP, install refresh
