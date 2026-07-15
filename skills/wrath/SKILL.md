---
name: wrath
description: Wrath addon hub for Grok Build. Use when the user says /wrath, asks what Wrath does, or wants the better Grok workflow (status, thin, check, budget, ship, doctor, review).
---

# Wrath hub

You are running **inside Grok Build** with the Wrath plugin loaded.

## What Wrath adds

- Session drive: brief, verify, YAGNI (SessionStart pack)
- PreToolUse guards: root wipes, Format-Volume, force-push main, reset --hard, git clean -fdx, curl|sh
- Journal + session stats under plugin data
- MCP tools for doctor / policy dry-run / journal
- Slash workflows below

## On / off (real, not vibes)

| Phrase / command | Effect |
|------------------|--------|
| `/wrath-on` · “turn wrath on” | Runtime **enabled** |
| `/wrath-off` · “turn wrath off” | Runtime **disabled** (guards skip) |

UserPromptSubmit toggles those phrases automatically.

## Commands

| Command | Skill |
|---------|--------|
| `/wrath-on` / `/wrath-off` | wrath-on / wrath-off |
| `/wrath-status` | wrath-status |
| `/wrath-thin` | wrath-thin |
| `/wrath-check` | wrath-check |
| `/wrath-budget` | wrath-budget |
| `/wrath-ship` | wrath-ship |
| `/wrath-doctor` | wrath-doctor |
| `/wrath-review` | wrath-review |

If the user only said `/wrath`, reply with this table in ≤8 lines.
