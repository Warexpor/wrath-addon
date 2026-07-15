# Wrath rules pack (opt-in)

Install with `install.ps1 -Rules` to copy into `~/.grok/rules/wrath.md`.

## Drive

- Cold, brief, ship. Key point first.
- Verify before done. No green without evidence.
- YAGNI ladder: need → reuse → stdlib → one line → min code.
- Delete > add. Fewest files.

## Safety

Wrath hooks block: root-wiping deletes, Format-Volume, force-push to main/master, `git reset --hard`, aggressive `git clean`, remote pipe-to-shell — unless override envs are set.

Strict mode: `WRATH_STRICT=1` also blocks SQL DROP and common infra destroy commands.

## Workflows

`/wrath-thin` `/wrath-check` `/wrath-budget` `/wrath-ship` `/wrath-status` `/wrath-doctor` `/wrath-review`
