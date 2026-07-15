#!/usr/bin/env python3
"""Stdio MCP server for Wrath addon (stdlib only)."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "hooks"))

from common import plugin_version  # noqa: E402
from journal import (  # noqa: E402
    counts,
    journal_path,
    session_stats,
    tail,
)
from policy import evaluate  # noqa: E402
from toggle import is_wrath_enabled, load_state, set_wrath_enabled  # noqa: E402

VERSION = plugin_version()


def data_dir() -> Path:
    raw = os.environ.get("GROK_PLUGIN_DATA") or os.environ.get("CLAUDE_PLUGIN_DATA")
    if raw:
        p = Path(raw)
    else:
        p = Path.home() / ".wrath-addon" / "data"
    p.mkdir(parents=True, exist_ok=True)
    return p


TOOLS = [
    {
        "name": "wrath_journal_tail",
        "description": "Last N Wrath journal events. Optional kind and session_id filters.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "n": {"type": "integer", "default": 15},
                "kind": {"type": "string"},
                "session_id": {"type": "string"},
            },
        },
    },
    {
        "name": "wrath_doctor",
        "description": "Check Wrath plugin paths, enabled flag, journal health, and policy smoke.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "wrath_budget_tips",
        "description": "Budget tips plus journal tool/event counts for this machine.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "wrath_set_enabled",
        "description": "Enable or disable Wrath runtime. args: enabled bool.",
        "inputSchema": {
            "type": "object",
            "properties": {"enabled": {"type": "boolean"}},
            "required": ["enabled"],
        },
    },
    {
        "name": "wrath_policy_check",
        "description": "Dry-run Wrath PreToolUse policy against a shell command (no execution).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "command": {"type": "string"},
                "tool": {
                    "type": "string",
                    "default": "run_terminal_command",
                    "description": "Tool name (default run_terminal_command)",
                },
            },
            "required": ["command"],
        },
    },
    {
        "name": "wrath_session_stats",
        "description": "Per-session tool histogram and recent denies from the journal.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "session_id": {"type": "string"},
                "top_tools": {"type": "integer", "default": 8},
            },
            "required": ["session_id"],
        },
    },
]


def handle_tool(name: str, args: dict) -> str:
    d = data_dir()
    if name == "wrath_journal_tail":
        n = int(args.get("n") or 15)
        kind = args.get("kind")
        sid = args.get("session_id")
        rows = tail(
            d,
            n=n,
            kind=str(kind) if kind else None,
            session_id=str(sid) if sid else None,
        )
        return json.dumps(
            {
                "enabled": is_wrath_enabled(d),
                "path": str(journal_path(d)),
                "events": rows,
            },
            indent=2,
        )
    if name == "wrath_set_enabled":
        en = bool(args.get("enabled"))
        state = set_wrath_enabled(en, data_dir=d, source="mcp")
        return json.dumps(state, indent=2)
    if name == "wrath_doctor":
        root = os.environ.get("GROK_PLUGIN_ROOT") or str(ROOT)
        hooks = Path(root) / "hooks" / "hooks.json"
        pre = Path(root) / "hooks" / "pre_tool_use.py"
        mcp_run = Path(root) / "mcp" / "run.py"
        # policy smoke
        deny = evaluate("run_terminal_command", "rm -rf /")
        allow = evaluate("run_terminal_command", "git status")
        report = {
            "plugin_root": root,
            "data_dir": str(d),
            "enabled": is_wrath_enabled(d),
            "state": load_state(d),
            "hooks_json": hooks.is_file(),
            "pre_tool_use": pre.is_file(),
            "mcp_run": mcp_run.is_file(),
            "journal_exists": journal_path(d).is_file(),
            "counts": counts(d),
            "policy_smoke": {
                "deny_rm_root": (not deny.allow),
                "allow_git_status": allow.allow,
            },
            "python": sys.version.split()[0],
            "version": VERSION,
        }
        return json.dumps(report, indent=2)
    if name == "wrath_budget_tips":
        c = counts(d)
        tips = [
            "Grep before full-file reads; avoid re-read loops.",
            "Prefer small edits over rewriting large files.",
            "Use /wrath-thin for one-file fixes; /wrath-check before claiming done.",
            "Subagents only for independent parallel work.",
            "Call wrath_session_stats with the current session_id after long turns.",
        ]
        return json.dumps({"counts": c, "tips": tips, "version": VERSION}, indent=2)
    if name == "wrath_policy_check":
        cmd = str(args.get("command") or "")
        tool = str(args.get("tool") or "run_terminal_command")
        dec = evaluate(tool, cmd, {})
        return json.dumps(
            {
                "tool": tool,
                "command": cmd,
                "allow": dec.allow,
                "reason": dec.reason,
                "warning": dec.warning,
                "enabled": is_wrath_enabled(d),
            },
            indent=2,
        )
    if name == "wrath_session_stats":
        sid = str(args.get("session_id") or "")
        top = int(args.get("top_tools") or 8)
        if not sid:
            return json.dumps({"error": "session_id required"})
        return json.dumps(session_stats(d, sid, top_tools=top), indent=2)
    return json.dumps({"error": f"unknown tool {name}"})


def respond(msg_id, result=None, error=None):
    body = {"jsonrpc": "2.0", "id": msg_id}
    if error is not None:
        body["error"] = error
    else:
        body["result"] = result
    sys.stdout.write(json.dumps(body) + "\n")
    sys.stdout.flush()


def main() -> int:
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except json.JSONDecodeError:
            continue
        method = req.get("method")
        msg_id = req.get("id")
        params = req.get("params") or {}

        if method == "initialize":
            respond(
                msg_id,
                {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": "wrath-mcp", "version": VERSION},
                },
            )
        elif method == "notifications/initialized":
            continue
        elif method == "notifications/cancelled":
            continue
        elif method == "tools/list":
            respond(msg_id, {"tools": TOOLS})
        elif method == "tools/call":
            name = params.get("name")
            args = params.get("arguments") or {}
            try:
                text = handle_tool(str(name), args if isinstance(args, dict) else {})
                is_err = False
                try:
                    parsed = json.loads(text)
                    is_err = isinstance(parsed, dict) and "error" in parsed
                except json.JSONDecodeError:
                    pass
                respond(
                    msg_id,
                    {
                        "content": [{"type": "text", "text": text}],
                        "isError": bool(is_err),
                    },
                )
            except Exception as exc:  # noqa: BLE001
                respond(
                    msg_id,
                    {
                        "content": [{"type": "text", "text": json.dumps({"error": str(exc)})}],
                        "isError": True,
                    },
                )
        elif method == "ping":
            respond(msg_id, {})
        elif method == "resources/list":
            respond(msg_id, {"resources": []})
        elif method == "prompts/list":
            respond(msg_id, {"prompts": []})
        elif msg_id is not None:
            respond(msg_id, error={"code": -32601, "message": f"Method not found: {method}"})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
