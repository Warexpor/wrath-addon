"""Single version source: .claude-plugin/plugin.json."""

from __future__ import annotations

import json
import os
from pathlib import Path

__version__ = "2.1.0"


def _root() -> Path:
    raw = os.environ.get("GROK_PLUGIN_ROOT") or os.environ.get("CLAUDE_PLUGIN_ROOT")
    if raw:
        return Path(raw)
    return Path(__file__).resolve().parents[2]


def plugin_version() -> str:
    manifest = _root() / ".claude-plugin" / "plugin.json"
    try:
        data = json.loads(manifest.read_text(encoding="utf-8"))
        ver = data.get("version")
        if ver:
            return str(ver)
    except (OSError, json.JSONDecodeError, TypeError):
        pass
    return __version__
