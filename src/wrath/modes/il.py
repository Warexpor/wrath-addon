IL_BODY = """IL (agent wire) ON.
User-facing replies: normal prose unless the user writes IL.
Internal reasoning, spawn_subagent prompts, specialist returns, lead↔child handoffs: Wrath IL only.
Shape (pipe slots, no fluff):
M:mode|P:pri|L:role|→:model
I:inputs  O:out-contract  C:checks  Δ:facts/changes  R:refs  S:status  B:blocked  Q:ask  X:escalate
Modes: impl|fix|rev|plan|explore|merge|math|ui
Pri: hi|med|lo  Status: ok|partial|fail|soft  Escalate: X:soft|X:wrong|X:scope
Child return HARD RULES:
- ONE line only (no multi-line wire, no blank lines)
- NO markdown fences (```), NO headers, NO bullets, NO prose sentences
- Must include S: and Δ: (or S:fail|B:…|X:…)
- Lead: put exact skeleton in O: for glm/deepseek; composer may freeform
Soft/wrong/fenced child → treat as X:soft; do not rubber-stamp.
Other: cite R:id not restate; one claim per Δ; no essay.
Ex spawn: M:impl|P:hi|L:lead|→:composer-2.5-fast
  I:goal=…;in=path/*  O:S:ok|Δ:…|F:n|K:med  C:pytest
Ex child: S:ok|Δ:root=…;fix=…|F:2|K:low
Off: /wrath-il-off
"""
