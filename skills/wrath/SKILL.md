---
name: wrath
description: Wrath V2 hub for Grok Build. Use when the user says /wrath, asks what Wrath does, or wants the better Grok workflow.
---

# Wrath V2 hub

You are running **inside Grok Build** with the Wrath plugin loaded.

## What Wrath adds

- Control plane: profiles, modular policy, full lifecycle journal
- PreToolUse guards (nested shell depth 3, privacy upload, spawn model pin, footguns)
- Drive pack + modes (strict / orch / il / privacy)
- MCP inspect tools

## On / off / modes

| Phrase / command | Effect |
|------------------|--------|
| `/wrath-on` · “turn wrath on” | Runtime **enabled** |
| `/wrath-off` · “turn wrath off” | Runtime **disabled** |
| `/wrath-profile <name>` | Profile: default·thin·strict·privacy·fleet·max |
| `/wrath-privacy` | Privacy bulk-upload deny |
| `/wrath-strict` | STRICT state on/off |
| `/wrath-orchestrate` | Fleet multi-model on/off |
| `/wrath-il` | Agent-wire IL dialect on/off |

## Commands

| Command | Skill |
|---------|--------|
| `/wrath-status` | wrath-status |
| `/wrath-thin` | wrath-thin |
| `/wrath-check` | wrath-check |
| `/wrath-budget` | wrath-budget |
| `/wrath-ship` | wrath-ship |
| `/wrath-doctor` | wrath-doctor |
| `/wrath-review` | wrath-review |
| `/wrath-why` | wrath-why |
| `/wrath-profile` | wrath-profile |
| `/wrath-privacy` | wrath-privacy |

If the user only said `/wrath`, reply with this table in ≤10 lines. Prefer MCP `wrath_status` / `wrath_doctor`.
