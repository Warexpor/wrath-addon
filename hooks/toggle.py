"""Wrath enabled/disabled + strict flags under plugin data."""

from __future__ import annotations

import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from common import plugin_data, plugin_version
from project_config import EffectiveConfig

STATE_NAME = "wrath_state.json"
DEFAULT_ENABLED = True
DEFAULT_STRICT = False

ENV_FORCE_OFF = "WRATH_OFF"
ENV_FORCE_ON = "WRATH_ON"
ENV_STRICT = "WRATH_STRICT"


def state_path(data_dir: Path | None = None) -> Path:
    return (data_dir or plugin_data()) / STATE_NAME


def load_state(data_dir: Path | None = None) -> dict[str, Any]:
    path = state_path(data_dir)
    if not path.is_file():
        return {"enabled": DEFAULT_ENABLED, "strict": DEFAULT_STRICT}
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(raw, dict):
            raw.setdefault("enabled", DEFAULT_ENABLED)
            raw.setdefault("strict", DEFAULT_STRICT)
            return raw
    except (OSError, json.JSONDecodeError):
        pass
    return {"enabled": DEFAULT_ENABLED, "strict": DEFAULT_STRICT}


def _write_state(data_dir: Path, payload: dict[str, Any]) -> dict[str, Any]:
    data_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        **payload,
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "version": plugin_version(),
    }
    state_path(data_dir).write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return payload


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
    prev = load_state(data)
    payload = {
        "enabled": bool(enabled),
        "strict": bool(prev.get("strict", DEFAULT_STRICT)),
        "source": source,
    }
    return _write_state(data, payload)


def is_strict(
    data_dir: Path | None = None,
    project: EffectiveConfig | None = None,
) -> bool:
    """Precedence: env WRATH_STRICT if set → else (state.strict OR project.strict)."""
    env = os.environ.get(ENV_STRICT)
    if env is not None and str(env).strip() != "":
        return str(env).strip().lower() in {"1", "true", "yes", "on"}
    if bool(load_state(data_dir).get("strict", DEFAULT_STRICT)):
        return True
    if project is not None and project.strict:
        return True
    return False


def set_strict(strict: bool, data_dir: Path | None = None, source: str = "cli") -> dict[str, Any]:
    data = data_dir or plugin_data()
    prev = load_state(data)
    payload = {
        "enabled": bool(prev.get("enabled", DEFAULT_ENABLED)),
        "strict": bool(strict),
        "source": source,
    }
    return _write_state(data, payload)


def parse_toggle_intent(text: str) -> bool | None:
    """Return True=on, False=off, None=no toggle intent."""
    t = (text or "").strip().lower()
    if not t:
        return None
    t = re.sub(r"^/", "", t)

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


def parse_strict_intent(text: str) -> bool | None:
    """Return True=strict on, False=strict off, None=no intent."""
    t = (text or "").strip().lower()
    if not t:
        return None
    t = re.sub(r"^/", "", t)
    if re.search(r"\bwrath[\s_-]*strict[\s_-]*off\b", t) or re.search(
        r"\bdisable\s+wrath\s+strict\b", t
    ):
        return False
    if re.search(r"\bwrath[\s_-]*strict\b", t) or re.search(r"\benable\s+wrath\s+strict\b", t):
        # bare /wrath-strict → on
        if re.search(r"strict[\s_-]*off\b", t):
            return False
        return True
    return None
