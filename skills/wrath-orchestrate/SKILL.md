---
name: wrath-orchestrate
description: Enable multi-model fleet orchestration mode. Use for /wrath-orchestrate, multi-model on, wrath orchestrate.
---

# wrath-orchestrate

Activate **multi-model fleet** mode for this machine (shared state under plugin data).

## Toggle

1. Prefer natural phrases (UserPromptSubmit handles them immediately):
   - on: `/wrath-orchestrate` · `multi-model on` · `enable wrath orchestrate`
   - off: `/wrath-orchestrate-off` · `multi-model off` · `wrath-orchestrate-off`
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

## When ON — you are LEAD

You stay the expensive judge. Specialists burn tokens. **Pin `model=` on every `spawn_subagent`.**

| Model | Use for | Avoid |
|-------|---------|--------|
| **Lead (you / session model)** | Spec, architecture, security, merge, final verify | Bulk grep, boilerplate dumps |
| **composer-2.5-fast** | Focused impl/refactor with bounded context | Long-horizon multi-file sagas (200k ceiling) — chunk or keep lead |
| **glm-5.2** | Brute quality sweeps, alternate opinions | Unscoped monologues; cap I/O in the spawn prompt |
| **deepseek-v4-flash** | Math, algorithms, pure text analysis | Images / any multimodal input |
| **mimo-v2.5** | Screenshots, UI, diagrams, video frames | Text-only work |

### Spawn rules

1. Explicit `model=` always (no silent inherit).
2. Tight child prompts + clear I/O contracts.
3. Soft / wrong specialist output → escalate to lead, do not rubber-stamp.
4. Composer tasks stay chunked; long horizon stays with lead or staged handoffs.

## Reply after toggle

≤5 lines: orchestrate on/off + one-line routing reminder. Do not restate the full table unless asked.
