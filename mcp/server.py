#!/usr/bin/env python3
"""Stdio MCP server for Wrath addon V2 (stdlib only)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "hooks"))

from wrath.io import plugin_version  # noqa: E402
from wrath.mcp.tools import TOOLS, handle_tool  # noqa: E402

VERSION = plugin_version()


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
            tname = params.get("name")
            targs = params.get("arguments") or {}
            try:
                text = handle_tool(str(tname), targs if isinstance(targs, dict) else {})
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
