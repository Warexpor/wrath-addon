# Changelog

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
