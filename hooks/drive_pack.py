"""Compact Wrath drive pack + status line for SessionStart."""

from __future__ import annotations

from pathlib import Path

from common import plugin_version

DRIVE_BODY = """Drive: cold, brief, ship. Key point first. No filler.
Ladder: need → reuse → stdlib → one line → min code. Delete > add.
Verify before done. Grep before re-read. /wrath-thin · /wrath-check · /wrath-ship
Safety: footgun guards on (force-push main, reset --hard, root wipe, curl|sh, …).
Strict: /wrath-strict or WRATH_STRICT=1. Config: .wrath.toml / .wrath.json
MCP: wrath_doctor · wrath_config · wrath_policy_check · wrath_journal_tail
"""

ORCHESTRATE_BODY = """ORCHESTRATE (multi-model fleet) ON.
You are LEAD — best quality, most expensive. Judge, merge, security, final verify.
Delegate volume; pin model= on every spawn_subagent (no silent inherit).
Routing:
- lead (you): architecture, hard judgment, security, merge of specialist output
- composer-2.5-fast: focused impl/refactor; chunk long-horizon (200k ceiling)
- glm-5.2: brute quality / broad sweeps; tight I/O contracts (tokenburner)
- deepseek-v4-flash: math + pure text only — never media
- mimo-v2.5: media/images/video frames only — not text-only work
Policy: tight child prompts; escalate soft quality to lead. Off: /wrath-orchestrate-off
"""

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


def status_line(
    *,
    enabled: bool,
    strict: bool,
    budget: int,
    config_path: Path | None = None,
    version: str | None = None,
    orchestrate: bool = False,
    il: bool = False,
) -> str:
    ver = version or plugin_version()
    on = "ON" if enabled else "OFF"
    st = "on" if strict else "off"
    orch = "on" if orchestrate else "off"
    il_s = "on" if il else "off"
    cfg = config_path.name if config_path else "none"
    return (
        f"[Wrath v{ver} · {on} · strict={st} · orch={orch} · il={il_s} · "
        f"budget={budget} · config={cfg}]"
    )


def drive_system_message(
    *,
    enabled: bool = True,
    strict: bool = False,
    budget: int = 80,
    config_path: Path | None = None,
    orchestrate: bool = False,
    il: bool = False,
) -> str:
    line = status_line(
        enabled=enabled,
        strict=strict,
        budget=budget,
        config_path=config_path,
        orchestrate=orchestrate,
        il=il,
    )
    if not enabled:
        return (
            f"{line}\n"
            "Guards, drive pack, and prompt nudges are disabled. "
            "/wrath-on or “turn wrath on” to re-enable."
        )
    body = DRIVE_BODY.strip()
    if orchestrate:
        body = f"{body}\n{ORCHESTRATE_BODY.strip()}"
    if il:
        body = f"{body}\n{IL_BODY.strip()}"
    return f"{line}\n{body}"
