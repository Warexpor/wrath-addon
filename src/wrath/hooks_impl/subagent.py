from __future__ import annotations

import re

from wrath.event import normalize
from wrath.io import log_hook_error, plugin_data, read_stdin_json
from wrath.journal import append_event
from wrath.state import is_il, is_orchestrate, is_wrath_enabled

_FENCE = re.compile(r"```")
_IL_OK = re.compile(r"\bS:(ok|partial|fail|soft)\b", re.I)


def main_start() -> int:
    try:
        event = read_stdin_json()
        if not is_wrath_enabled():
            return 0
        he = normalize(event)
        data = plugin_data()
        append_event(
            data,
            {
                "kind": "subagent_start",
                "session_id": he.session_id,
                "tool": he.tool_name or "spawn_subagent",
                "model": he.model or None,
                "agent_id": he.agent_id or None,
                "orchestrate": is_orchestrate(data),
                "il": is_il(data),
            },
        )
    except Exception as exc:  # noqa: BLE001
        log_hook_error("SubagentStart", exc)
    return 0


def main_stop() -> int:
    try:
        event = read_stdin_json()
        if not is_wrath_enabled():
            return 0
        he = normalize(event)
        data = plugin_data()
        result = str(
            he.raw.get("result")
            or he.raw.get("output")
            or he.raw.get("response")
            or he.reason
            or ""
        )
        soft = False
        if is_il(data) and result:
            if _FENCE.search(result) or (
                "\n" in result.strip() and not _IL_OK.search(result.split("\n")[0])
            ):
                soft = True
            elif not _IL_OK.search(result[:200]):
                # multi-line prose without S:
                if len(result) > 80 and "|" not in result[:120]:
                    soft = True
        append_event(
            data,
            {
                "kind": "subagent_stop",
                "session_id": he.session_id,
                "model": he.model or None,
                "agent_id": he.agent_id or None,
                "soft": soft,
                "reason": "X:soft" if soft else None,
            },
        )
    except Exception as exc:  # noqa: BLE001
        log_hook_error("SubagentStop", exc)
    return 0
