"""Normalize Grok / Claude / Cursor hook envelopes."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any

TOOL_ALIASES = {
    "bash": "run_terminal_command",
    "shell": "run_terminal_command",
    "terminal": "run_terminal_command",
    "run_command": "run_terminal_command",
    "read": "read_file",
    "readfile": "read_file",
    "edit": "search_replace",
    "write": "write",
    "multiedit": "search_replace",
    "writefile": "write",
    "str_replace": "search_replace",
    "create_file": "write",
    "task": "spawn_subagent",
    "grep": "grep",
    "glob": "list_dir",
    "listdir": "list_dir",
}


@dataclass
class HookEvent:
    raw: dict[str, Any] = field(default_factory=dict)
    session_id: str = "unknown"
    cwd: str = ""
    workspace_root: str = ""
    tool_name: str = ""
    tool_input: dict[str, Any] = field(default_factory=dict)
    tool_use_id: str = ""
    tool_input_truncated: bool = False
    hook_event_name: str = ""
    prompt: str = ""
    reason: str = ""
    model: str = ""
    agent_id: str = ""

    @property
    def shell_command(self) -> str:
        ti = self.tool_input
        for key in ("command", "cmd", "shell_command"):
            if key in ti and ti[key]:
                return str(ti[key])
        return ""

    def path(self) -> str:
        ti = self.tool_input
        return str(
            ti.get("path")
            or ti.get("file_path")
            or ti.get("target_file")
            or ti.get("target_directory")
            or ""
        )


def canonicalize_tool(name: str) -> str:
    n = (name or "").strip()
    if not n:
        return ""
    low = n.lower()
    if low in TOOL_ALIASES:
        return TOOL_ALIASES[low]
    # Title-case Claude names
    for k, v in TOOL_ALIASES.items():
        if low == k:
            return v
    mapping = {
        "Bash": "run_terminal_command",
        "Shell": "run_terminal_command",
        "Read": "read_file",
        "Edit": "search_replace",
        "Write": "write",
        "MultiEdit": "search_replace",
        "Grep": "grep",
        "Glob": "list_dir",
        "ListDir": "list_dir",
        "Task": "spawn_subagent",
        "WebSearch": "web_search",
    }
    return mapping.get(n, n)


def _prompt_text(event: dict[str, Any]) -> str:
    for key in (
        "prompt",
        "userPrompt",
        "user_prompt",
        "message",
        "text",
        "content",
        "input",
        "userMessage",
        "user_message",
    ):
        val = event.get(key)
        if val is None:
            continue
        if isinstance(val, str) and val.strip():
            return val
        if isinstance(val, list):
            parts: list[str] = []
            for item in val:
                if isinstance(item, str) and item.strip():
                    parts.append(item)
                elif isinstance(item, dict):
                    chunk = str(item.get("text") or item.get("content") or "").strip()
                    if chunk:
                        parts.append(chunk)
            joined = "\n".join(parts)
            if joined.strip():
                return joined
    msg = event.get("message")
    if isinstance(msg, dict):
        nested = _prompt_text(msg)
        if nested:
            return nested
    return ""


def normalize(raw: dict[str, Any] | None) -> HookEvent:
    event = raw if isinstance(raw, dict) else {}
    ti = event.get("toolInput") or event.get("tool_input") or {}
    if not isinstance(ti, dict):
        ti = {}
    sid = (
        event.get("sessionId")
        or event.get("session_id")
        or os.environ.get("GROK_SESSION_ID")
        or os.environ.get("CLAUDE_SESSION_ID")
        or "unknown"
    )
    cwd = str(
        event.get("cwd") or event.get("workingDirectory") or event.get("working_directory") or ""
    )
    ws = str(
        event.get("workspaceRoot")
        or event.get("workspace_root")
        or os.environ.get("GROK_WORKSPACE_ROOT")
        or os.environ.get("CLAUDE_PROJECT_DIR")
        or cwd
    )
    name = str(event.get("toolName") or event.get("tool_name") or event.get("tool") or "")
    model = str(ti.get("model") or event.get("model") or event.get("agentModel") or "")
    agent_id = str(
        event.get("agentId")
        or event.get("agent_id")
        or event.get("subagentId")
        or ti.get("description")
        or ""
    )
    return HookEvent(
        raw=event,
        session_id=str(sid),
        cwd=cwd,
        workspace_root=ws,
        tool_name=name,
        tool_input=ti,
        tool_use_id=str(event.get("toolUseId") or event.get("tool_use_id") or ""),
        tool_input_truncated=bool(
            event.get("toolInputTruncated") or event.get("tool_input_truncated")
        ),
        hook_event_name=str(
            event.get("hookEventName")
            or event.get("hook_event_name")
            or os.environ.get("GROK_HOOK_EVENT")
            or ""
        ),
        prompt=_prompt_text(event),
        reason=str(
            event.get("reason")
            or event.get("stopReason")
            or event.get("message")
            or event.get("error")
            or ""
        ),
        model=model,
        agent_id=str(agent_id)[:120],
    )
