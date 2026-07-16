---
name: wrath-orchestrate
description: Enable style-dispatch orchestration mode. Use for /wrath-orchestrate, style dispatch on, wrath orchestrate.
---

# wrath-orchestrate

Activate **style-dispatch** mode for this machine (shared state under plugin data).

## Toggle

1. Prefer natural phrases (UserPromptSubmit handles them immediately):
   - on: `/wrath-orchestrate` · `style dispatch on` · `enable wrath orchestrate`
   - off: `/wrath-orchestrate-off` · `style dispatch off` · `wrath-orchestrate-off`
2. Prefer MCP `wrath_set_orchestrate` with `orchestrate: true|false` if available.
3. Else CLI from plugin hooks dir:

```text
python set_enabled.py orchestrate-on
python set_enabled.py orchestrate-off
python set_enabled.py status
```

Resolve hooks via `GROK_PLUGIN_ROOT/hooks` when set.

4. Confirm with MCP `wrath_config` (`orchestrate` field) or status (`orch=on`).
5. Precedence: env `WRATH_ORCHESTRATE` if set → else state.

## When ON — style dispatch

Same model, different prompt hat. **Pin `mode=` on every `spawn_subagent`.**

| mode= | Persona | Use for |
|-------|---------|--------|
| **coder** | Focused implementor — minimal working code, no essays | Impl, refactoring, bug fixes |
| **reviewer** | Adversarial reviewer — bugs, security, design issues | Code review, audit, pre-merge |
| **explorer** | Efficient reader — grep/list, concise reports | Exploration, code search |
| **planner** | Structured thinker — trade-offs, ordered steps | Design, architecture, plans |
| **architect** | System designer — interfaces, data flow, modules | Specs, API design, decomposition |

### Spawn rules

1. Explicit `mode=` always (no silent default).
2. Tight child prompts + clear I/O contracts.
3. Soft / wrong child output → escalate to lead, do not rubber-stamp.
4. Cap context per child; long horizon stays with lead or staged handoffs.

## Reply after toggle

≤5 lines: orchestrate on/off + one-line style reminder. Do not restate the full table unless asked.
