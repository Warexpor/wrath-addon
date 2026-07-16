from __future__ import annotations

from wrath.policy.decision import Decision

SPAWN_TOOLS = {
    "spawn_subagent",
    "Task",
    "task",
}

STYLES = ("coder", "reviewer", "explorer", "planner", "architect")


def check_spawn_mode(
    tool: str,
    tool_input: dict,
    *,
    orchestrate: bool,
    mode: str = "off",
) -> Decision | None:
    if not orchestrate or mode in ("", "off", "none"):
        return None
    name = (tool or "").strip()
    if name not in SPAWN_TOOLS and name.lower() not in {"spawn_subagent", "task"}:
        return None
    spawn_mode = str(tool_input.get("mode") or "").strip().lower()
    if spawn_mode in STYLES:
        return None
    if mode == "deny":
        return Decision(
            allow=False,
            reason=(
                "Wrath orch: spawn_subagent requires mode= pin "
                f"({' | '.join(STYLES)})"
            ),
            rule_id="spawn_mode",
            severity="deny",
        )
    return Decision(
        allow=True,
        warning=(
            "Wrath orch: spawn without mode= — pin a style "
            "(coder | reviewer | explorer | planner | architect); "
            "silent default wastes the style system."
        ),
        rule_id="spawn_mode_warn",
        severity="warn",
    )
