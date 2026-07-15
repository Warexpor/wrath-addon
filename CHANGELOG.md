# Changelog

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
