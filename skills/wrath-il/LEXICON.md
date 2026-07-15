# Wrath IL lexicon (v0.1)

BPE-friendly: short ASCII keys, common separators (`:`, `|`, `=`, `;`).

## Header (spawn / handoff)

```
M:<mode>|P:<pri>|L:<role>|→:<model>
```

Optional fields omitted when default. Multi-line **spawn prompts** are OK (one slot group per line). **Child returns are not** — see below.

## Body slots (order free)

| Key | Value | Example |
|-----|--------|---------|
| `I` | inputs | `I:goal=fix desync;in=src/Net/*` |
| `O` | output contract + return skeleton | `O:S:ok\|Δ:…\|F:n\|K:med` |
| `C` | checks | `C:pytest;build Release` |
| `Δ` | delta/fact | `Δ:root=race on join;fix=serialize tick` |
| `R` | reference ids | `R:spec#3,log#h-8841` |
| `S` | status | `S:ok` / `S:partial` / `S:fail` / `S:soft` |
| `B` | blocked | `B:missing API key` |
| `Q` | question | `Q:scope include client?` |
| `X` | escalate | `X:soft` / `X:wrong` / `X:scope` |
| `N` | constraint | `N:no deps;no fences;one line` |
| `F` | files touched | `F:2` |
| `K` | risk | `K:low` / `K:med` / `K:hi` |

## Modes (`M:`)

`impl` `fix` `rev` `plan` `explore` `merge` `math` `ui` `ship` `check`

## Child return (HARD)

**Exactly one line. No markdown fences. No prose wrapper.**

Success:

```
S:ok|Δ:…|F:n|K:med|open:…
```

Fail:

```
S:fail|B:…|X:scope
```

Soft (child should self-mark if it cannot stay in wire):

```
S:soft|B:cannot_il|X:soft
```

### Forbidden in child returns

- Multi-line slot dumps (echo of full M/I/O header)
- ` ``` ` fences or indented code blocks
- Markdown headings / bullets / numbered lists
- Greeting or essay paragraphs
- “Here is the answer:” prefixes

### Lead spawn recipe (weak models)

Always include skeleton in `O:` and ban fences in `N:`:

```
M:impl|P:hi|L:lead|→:glm-5.2
I:goal=…
O:S:ok|Δ:…|F:n|K:med
C:…
N:one line only;no fences;no prose
```

## Model compliance (measured)

| Model | Scaffolded IL | Freeform IL |
|-------|---------------|-------------|
| composer-2.5-fast | high | high |
| deepseek-v4-flash | high | medium (fences/multi-line) — force skeleton |
| glm-5.2 | high | low (prose) — force skeleton + re-ask on essay |

## Anti-patterns

- Restating full prior spawn instead of `R:`
- Prose paragraphs inside wire
- Inventing multi-token fantasy words (worse for BPE)
- User-facing answers in IL unless user used IL
- Accepting fenced multi-line child output as success
