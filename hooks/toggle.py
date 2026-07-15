"""Wrath enabled/disabled flag under plugin data (hooks + skills share this)."""

from __future__ import annotations

import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from common import plugin_data

STATE_NAME = "wrath_state.json"
DEFAULT_ENABLED = True

# Env force-off without deleting flag (for CI / emergency)
ENV_FORCE_OFF = "WRATH_OFF"
ENV_FORCE_ON = "WRATH_ON"


def state_path(data_dir: Path | None = None) -> Path:
    return (data_dir or plugin_data()) / STATE_NAME


def load_state(data_dir: Path | None = None) -> dict[str, Any]:
    path = state_path(data_dir)
    if not path.is_file():
        return {"enabled": DEFAULT_ENABLED}
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(raw, dict):
            return raw
    except (OSError, json.JSONDecodeError):
        pass
    return {"enabled": DEFAULT_ENABLED}


def is_wrath_enabled(data_dir: Path | None = None) -> bool:
    if os.environ.get(ENV_FORCE_OFF, "").strip().lower() in {"1", "true", "yes", "on"}:
        return False
    if os.environ.get(ENV_FORCE_ON, "").strip().lower() in {"1", "true", "yes", "on"}:
        return True
    state = load_state(data_dir)
    return bool(state.get("enabled", DEFAULT_ENABLED))


def set_wrath_enabled(
    enabled: bool, data_dir: Path | None = None, source: str = "cli"
) -> dict[str, Any]:
    data = data_dir or plugin_data()
    data.mkdir(parents=True, exist_ok=True)
    payload = {
        "enabled": bool(enabled),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "source": source,
        "version": "1.0.0",
    }
    state_path(data).write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return payload


def parse_toggle_intent(text: str) -> bool | None:
    """Return True=on, False=off, None=no toggle intent."""
    t = (text or "").strip().lower()
    if not t:
        return None
    # strip leading slash commands
    t = re.sub(r"^/", "", t)

    # Brand + legacy aliases (vanta, forge)
    brand = r"(?:wrath|vanta|forge)"
    off_patterns = (
        rf"^{brand}[\s_-]*off\b",
        rf"^/{brand}-off\b",
        rf"\bturn\s+{brand}\s+off\b",
        rf"\bdisable\s+{brand}\b",
        rf"\b{brand}\s+disable\b",
        rf"\bswitch\s+{brand}\s+off\b",
        rf"\b{brand}\s+mode\s+off\b",
    )
    on_patterns = (
        rf"^{brand}[\s_-]*on\b",
        rf"^/{brand}-on\b",
        rf"\bturn\s+{brand}\s+on\b",
        rf"\benable\s+{brand}\b",
        rf"\b{brand}\s+enable\b",
        rf"\bswitch\s+{brand}\s+on\b",
        rf"\b{brand}\s+mode\s+on\b",
    )
    for pat in off_patterns:
        if re.search(pat, t):
            return False
    for pat in on_patterns:
        if re.search(pat, t):
            return True
    return None
