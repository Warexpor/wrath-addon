# Wrath rules pack (opt-in)

Install with `install.ps1 -Rules` to copy into `~/.grok/rules/wrath.md`.

## Drive

- Cold, brief, ship. Key point first.
- Verify before done. No green without evidence.
- YAGNI ladder: need → reuse → stdlib → one line → min code.

## Safety

Hooks block root wipes, Format-Volume, force-push main, reset --hard, git clean -fdx, remote pipe-to-shell, writes into `.git/`. Nested `powershell -Command` / `bash -c` unwrapped one level.

Project: optional `.wrath.toml` / `.wrath.json` (`deny`, `budget_tools`, `reread_warn`, `strict`).

Strict: `/wrath-strict` or `WRATH_STRICT=1`.

Orchestrate (multi-model fleet): `/wrath-orchestrate` or `WRATH_ORCHESTRATE=1`. Off: `/wrath-orchestrate-off`.

IL (agent wire dialect): `/wrath-il` or `WRATH_IL=1`. Off: `/wrath-il-off`. User-facing stays prose; internal + spawn use IL. Child returns: **one line**, no markdown fences, must have `S:`+`Δ:` (or `S:fail|B:|X:`). Soft/fenced child → escalate, do not accept.

## Workflows

`/wrath-thin` `/wrath-check` `/wrath-budget` `/wrath-ship` `/wrath-status` `/wrath-doctor` `/wrath-review` `/wrath-strict` `/wrath-orchestrate` `/wrath-il` `/wrath-why`
