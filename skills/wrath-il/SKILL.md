---
name: wrath-il
description: Enable Wrath IL agent-wire dialect. Use for /wrath-il, il on, wrath il mode.
---

# wrath-il

Activate **Wrath IL** — dense opcode wire for internal thought and agent handoffs (shared machine state).

## Toggle

1. Prefer natural phrases (UserPromptSubmit handles them immediately):
   - on: `/wrath-il` · `il on` · `enable wrath il` · `il mode on`
   - off: `/wrath-il-off` · `il off` · `wrath-il-off` · `disable il`
2. Prefer MCP `wrath_set_il` with `il: true|false` if available.
3. Else CLI from plugin hooks dir:

```text
python set_enabled.py il-on
python set_enabled.py il-off
python set_enabled.py status
```

Resolve hooks via `GROK_PLUGIN_ROOT/hooks` when set.

4. Confirm with MCP `wrath_config` (`il` field) or status (`il=on`).
5. Precedence: env `WRATH_IL` if set → else state.

## When ON

| Channel | Language |
|---------|----------|
| User-facing reply | Normal prose (unless user writes IL) |
| Internal reasoning | Wrath IL |
| `spawn_subagent` prompts | Wrath IL only |
| Specialist → lead returns | Wrath IL only |

### Wire shape

```
M:mode|P:pri|L:role|→:model
I:…  O:…  C:…  Δ:…  R:…  S:…  B:…  Q:…  X:…
```

| Slot | Meaning |
|------|---------|
| `M` | mode: impl \| fix \| rev \| plan \| explore \| merge \| math \| ui |
| `P` | priority: hi \| med \| lo |
| `L` | role: lead \| child |
| `→` | target model id (when spawning) |
| `I` | inputs / goal / in=paths |
| `O` | output contract (include return skeleton) |
| `C` | verification checks |
| `Δ` | facts or changes (one claim per unit) |
| `R` | refs by id (prefer cite over restate) |
| `S` | status: ok \| partial \| fail \| soft |
| `B` | blocked reason |
| `Q` | question to lead/user |
| `X` | escalate: soft \| wrong \| scope |

### Child return — hard rules

1. **One line only** — entire return is a single pipe-separated line.
2. **No fences** — never ` ``` `, no markdown headers, no bullets.
3. **No prose** — no full English sentences outside slot values.
4. **Required slots** — `S:` + `Δ:` on success; or `S:fail|B:…|X:…` on failure.
5. **Canonical success:** `S:ok|Δ:…|F:n|K:low|med|hi` (add `open:` if needed).
6. **Canonical fail:** `S:fail|B:…|X:soft|wrong|scope`

Lead **must** put that skeleton in spawn `O:` for glm / deepseek; composer may freeform but still one line / no fences.

### Lead validation (after child)

| Child output | Action |
|--------------|--------|
| One-line IL with `S:` | Accept |
| Multi-line wire | `X:soft` — re-ask or redo lead |
| Markdown fences / essay | `X:soft` — do not rubber-stamp |
| Wrong facts, valid IL | `X:wrong` |

### Rules

1. Cite `R:` instead of pasting prior context.
2. Soft/wrong specialist → escalate; do not rubber-stamp.
3. Combines with orchestrate: IL is the dialect; orchestrate is who runs.

## Reply after toggle

≤5 lines: il on/off + one-line wire reminder. Full lexicon only if asked.
