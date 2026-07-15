"""Wrath enabled/disabled + strict + orchestrate flags under plugin data."""

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
DEFAULT_ORCHESTRATE = False

ENV_FORCE_OFF = "WRATH_OFF"
ENV_FORCE_ON = "WRATH_ON"
ENV_STRICT = "WRATH_STRICT"
ENV_ORCHESTRATE = "WRATH_ORCHESTRATE"


def state_path(data_dir: Path | None = None) -> Path:
    return (data_dir or plugin_data()) / STATE_NAME


def _defaults() -> dict[str, Any]:
    return {
        "enabled": DEFAULT_ENABLED,
        "strict": DEFAULT_STRICT,
        "orchestrate": DEFAULT_ORCHESTRATE,
    }


def load_state(data_dir: Path | None = None) -> dict[str, Any]:
    path = state_path(data_dir)
    if not path.is_file():
        return _defaults()
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(raw, dict):
            raw.setdefault("enabled", DEFAULT_ENABLED)
            raw.setdefault("strict", DEFAULT_STRICT)
            raw.setdefault("orchestrate", DEFAULT_ORCHESTRATE)
            return raw
    except (OSError, json.JSONDecodeError):
        pass
    return _defaults()


def _write_state(data_dir: Path, payload: dict[str, Any]) -> dict[str, Any]:
    data_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        **payload,
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "version": plugin_version(),
    }
    state_path(data_dir).write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return payload


def _preserve_flags(prev: dict[str, Any], **overrides: Any) -> dict[str, Any]:
    base = {
        "enabled": bool(prev.get("enabled", DEFAULT_ENABLED)),
        "strict": bool(prev.get("strict", DEFAULT_STRICT)),
        "orchestrate": bool(prev.get("orchestrate", DEFAULT_ORCHESTRATE)),
    }
    base.update(overrides)
    return base


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
    payload = _preserve_flags(prev, enabled=bool(enabled), source=source)
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
    payload = _preserve_flags(prev, strict=bool(strict), source=source)
    return _write_state(data, payload)


def is_orchestrate(data_dir: Path | None = None) -> bool:
    """Precedence: env WRATH_ORCHESTRATE if set → else state.orchestrate."""
    env = os.environ.get(ENV_ORCHESTRATE)
    if env is not None and str(env).strip() != "":
        return str(env).strip().lower() in {"1", "true", "yes", "on"}
    return bool(load_state(data_dir).get("orchestrate", DEFAULT_ORCHESTRATE))


def set_orchestrate(
    orchestrate: bool, data_dir: Path | None = None, source: str = "cli"
) -> dict[str, Any]:
    data = data_dir or plugin_data()
    prev = load_state(data)
    payload = _preserve_flags(prev, orchestrate=bool(orchestrate), source=source)
    return _write_state(data, payload)


def parse_toggle_intent(text: str) -> bool | None:
    """Return True=on, False=off, None=no toggle intent."""
    t = (text or "").strip().lower()
    if not t:
        return None
    t = re.sub(r"^/", "", t)
    # Mode phrases handled separately — never treat as full runtime off/on.
    if re.search(r"\bstrict\b", t):
        return None
    if re.search(r"\borchestrate\b", t) or re.search(r"\bmulti[\s_-]*model\b", t):
        return None

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


def parse_orchestrate_intent(text: str) -> bool | None:
    """Return True=orchestrate on, False=off, None=no intent."""
    t = (text or "").strip().lower()
    if not t:
        return None
    t = re.sub(r"^/", "", t)

    off_patterns = (
        r"\bwrath[\s_-]*orchestrate[\s_-]*off\b",
        r"\bdisable\s+wrath\s+orchestrate\b",
        r"\bwrath\s+orchestrate\s+off\b",
        r"\bmulti[\s_-]*model\s+off\b",
        r"\bturn\s+multi[\s_-]*model\s+off\b",
        r"\borchestrate[\s_-]*off\b",
        r"\bdisable\s+orchestrate\b",
        r"\bdisable\s+multi[\s_-]*model\b",
    )
    on_patterns = (
        r"\bwrath[\s_-]*orchestrate\b",
        r"\benable\s+wrath\s+orchestrate\b",
        r"\bwrath\s+orchestrate\s+on\b",
        r"\benable\s+orchestrate\b",
        r"\bmulti[\s_-]*model\s+on\b",
        r"\bturn\s+multi[\s_-]*model\s+on\b",
        r"\benable\s+multi[\s_-]*model\b",
        r"\borchestrate\s+mode\s+on\b",
    )
    for pat in off_patterns:
        if re.search(pat, t):
            return False
    for pat in on_patterns:
        if re.search(pat, t):
            if re.search(r"orchestrate[\s_-]*off\b", t) or re.search(
                r"multi[\s_-]*model[\s_-]*off\b", t
            ):
                return False
            return True
    return None
