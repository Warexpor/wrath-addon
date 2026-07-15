# Wrath addon bug audit

## Fixed in 1.0.1 (polish)
1. Test pollution — hook/MCP tests use `tmp_path`; `tests/_data` untracked.
2. Secret paths — `.env.*`, service account JSON, `-sa.json`.
3. Version single-sourced from `plugin.json` via `plugin_version()`.
4. Segment splitter docstring matches behavior (no bare `|` split).
5. Empty `commands/` removed on install; not shipped.
6. Fail-open hooks log stderr + `hook_errors.jsonl`.
7. CI + pyproject + ruff; LF for Python.

## Fixed in 1.0.0
1. MCP cwd bug — absolute path patch + launcher chdir.
2. Hardcoded user paths in skills removed.
3. DROP policy Decision fields split.
4. Journal reverse-chunk tail + rotation.
5. Multi-command `;` / `&&` segments.
6. Remote pipe-to-shell and git clean -fdx gates.

## Residual risks
1. Deny list is heuristic — not a full sandbox.
2. UserPromptSubmit unknown shapes may miss auto-toggle (skills/MCP still work).
3. Absolute MCP path re-patched by `install.ps1` after each reinstall.
4. Nested shells (`powershell -c "rm -rf /"`) may slip.
5. Force-push without branch only denied under `WRATH_STRICT=1`.
