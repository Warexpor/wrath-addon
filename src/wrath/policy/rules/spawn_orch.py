from __future__ import annotations

from wrath.policy.decision import Decision

SPAWN_TOOLS = {
    "spawn_subagent",
    "Task",
    "task",
}


def check_spawn_model(
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
    model = str(tool_input.get("model") or "").strip()
    if model:
        return None
    if mode == "deny":
        return Decision(
            allow=False,
            reason=(
                "Wrath orch: spawn_subagent requires model= pin "
                "(composer-2.5-fast | glm-5.2 | deepseek-v4-flash | mimo-v2.5)"
            ),
            rule_id="spawn_model",
            severity="deny",
        )
    return Decision(
        allow=True,
        warning=(
            "Wrath orch: spawn without model= — pin a specialist; "
            "silent inherit wastes lead budget."
        ),
        rule_id="spawn_model_warn",
        severity="warn",
    )
