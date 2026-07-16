"""Persisted Wrath state: enabled, modes, profile."""

from __future__ import annotations

import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from wrath.config import PROFILES, EffectiveConfig, _profile_defaults
from wrath.io import plugin_data, plugin_version

STATE_NAME = "wrath_state.json"
DEFAULT_ENABLED = True
DEFAULT_STRICT = False
DEFAULT_ORCHESTRATE = False
DEFAULT_PRIVACY = False
DEFAULT_YOLO = False
DEFAULT_PROFILE = "default"

ENV_FORCE_OFF = "WRATH_OFF"
ENV_FORCE_ON = "WRATH_ON"
ENV_STRICT = "WRATH_STRICT"
ENV_ORCHESTRATE = "WRATH_ORCHESTRATE"
ENV_PRIVACY = "WRATH_PRIVACY"
ENV_YOLO = "WRATH_YOLO"


def state_path(data_dir: Path | None = None) -> Path:
    return (data_dir or plugin_data()) / STATE_NAME


def _defaults() -> dict[str, Any]:
    return {
        "enabled": DEFAULT_ENABLED,
        "strict": DEFAULT_STRICT,
        "orchestrate": DEFAULT_ORCHESTRATE,
        "privacy": DEFAULT_PRIVACY,
        "yolo": DEFAULT_YOLO,
        "profile": DEFAULT_PROFILE,
    }


def load_state(data_dir: Path | None = None) -> dict[str, Any]:
    path = state_path(data_dir)
    if not path.is_file():
        return _defaults()
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(raw, dict):
            base = _defaults()
            base.update({k: raw[k] for k in base if k in raw})
            # migrate missing keys
            for k, v in _defaults().items():
                base.setdefault(k, v)
            return base
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


def _preserve(prev: dict[str, Any], **overrides: Any) -> dict[str, Any]:
    base = {
        "enabled": bool(prev.get("enabled", DEFAULT_ENABLED)),
        "strict": bool(prev.get("strict", DEFAULT_STRICT)),
        "orchestrate": bool(prev.get("orchestrate", DEFAULT_ORCHESTRATE)),
        "privacy": bool(prev.get("privacy", DEFAULT_PRIVACY)),
        "yolo": bool(prev.get("yolo", DEFAULT_YOLO)),
        "profile": str(prev.get("profile") or DEFAULT_PROFILE),
    }
    base.update(overrides)
    return base


def is_wrath_enabled(data_dir: Path | None = None) -> bool:
    if os.environ.get(ENV_FORCE_OFF, "").strip().lower() in {"1", "true", "yes", "on"}:
        return False
    if os.environ.get(ENV_FORCE_ON, "").strip().lower() in {"1", "true", "yes", "on"}:
        return True
    return bool(load_state(data_dir).get("enabled", DEFAULT_ENABLED))


def set_wrath_enabled(
    enabled: bool, data_dir: Path | None = None, source: str = "cli"
) -> dict[str, Any]:
    data = data_dir or plugin_data()
    prev = load_state(data)
    return _write_state(data, _preserve(prev, enabled=bool(enabled), source=source))


def is_strict(
    data_dir: Path | None = None,
    project: EffectiveConfig | None = None,
) -> bool:
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
    return _write_state(data, _preserve(prev, strict=bool(strict), source=source))


def is_orchestrate(data_dir: Path | None = None) -> bool:
    env = os.environ.get(ENV_ORCHESTRATE)
    if env is not None and str(env).strip() != "":
        return str(env).strip().lower() in {"1", "true", "yes", "on"}
    return bool(load_state(data_dir).get("orchestrate", DEFAULT_ORCHESTRATE))


def set_orchestrate(
    orchestrate: bool, data_dir: Path | None = None, source: str = "cli"
) -> dict[str, Any]:
    data = data_dir or plugin_data()
    prev = load_state(data)
    return _write_state(data, _preserve(prev, orchestrate=bool(orchestrate), source=source))


def is_privacy(data_dir: Path | None = None) -> bool:
    env = os.environ.get(ENV_PRIVACY)
    if env is not None and str(env).strip() != "":
        return str(env).strip().lower() in {"1", "true", "yes", "on"}
    return bool(load_state(data_dir).get("privacy", DEFAULT_PRIVACY))


def set_privacy(privacy: bool, data_dir: Path | None = None, source: str = "cli") -> dict[str, Any]:
    data = data_dir or plugin_data()
    prev = load_state(data)
    # privacy and yolo are opposites for soft bulk-upload policy
    kwargs: dict[str, Any] = {"privacy": bool(privacy), "source": source}
    if privacy:
        kwargs["yolo"] = False
        if str(prev.get("profile") or "") == "yolo":
            kwargs["profile"] = "default"
    return _write_state(data, _preserve(prev, **kwargs))


def is_yolo(data_dir: Path | None = None, project: EffectiveConfig | None = None) -> bool:
    """Precedence: env WRATH_YOLO if set → else state.yolo OR profile==yolo."""
    env = os.environ.get(ENV_YOLO)
    if env is not None and str(env).strip() != "":
        return str(env).strip().lower() in {"1", "true", "yes", "on"}
    if bool(load_state(data_dir).get("yolo", DEFAULT_YOLO)):
        return True
    return get_profile(data_dir, project=project) == "yolo"


def set_yolo(yolo: bool, data_dir: Path | None = None, source: str = "cli") -> dict[str, Any]:
    data = data_dir or plugin_data()
    prev = load_state(data)
    if yolo:
        return _write_state(
            data,
            _preserve(
                prev,
                yolo=True,
                privacy=False,
                strict=False,
                profile="yolo",
                source=source,
            ),
        )
    # leave profile as default if was yolo
    prof = str(prev.get("profile") or DEFAULT_PROFILE)
    if prof == "yolo":
        prof = "default"
    return _write_state(
        data,
        _preserve(prev, yolo=False, profile=prof, source=source),
    )


def get_profile(data_dir: Path | None = None, project: EffectiveConfig | None = None) -> str:
    st = load_state(data_dir)
    p = str(st.get("profile") or "")
    if p in PROFILES:
        return p
    if project and project.profile in PROFILES:
        return project.profile
    return DEFAULT_PROFILE


def set_profile(profile: str, data_dir: Path | None = None, source: str = "cli") -> dict[str, Any]:
    name = (profile or "default").strip().lower()
    if name not in PROFILES:
        name = "default"
    data = data_dir or plugin_data()
    prev = load_state(data)
    pdata = _profile_defaults(name)
    payload = _preserve(
        prev,
        profile=name,
        strict=bool(pdata.get("strict")),
        orchestrate=bool(pdata.get("orchestrate")),
        privacy=bool(pdata.get("privacy")),
        yolo=bool(pdata.get("yolo")),
        source=source,
    )
    return _write_state(data, payload)


def parse_toggle_intent(text: str) -> bool | None:
    t = (text or "").strip().lower()
    if not t:
        return None
    t = re.sub(r"^/", "", t)
    if re.search(r"\bstrict\b", t):
        return None
    if re.search(r"\borchestrate\b", t) or re.search(r"\bmulti[\s_-]*model\b", t):
        return None
    if re.search(r"\bprivacy\b", t) or re.search(r"\bprofile\b", t):
        return None
    if re.search(r"\byolo\b", t):
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
    t = (text or "").strip().lower()
    if not t:
        return None
    t = re.sub(r"^/", "", t)
    if re.search(r"\bwrath[\s_-]*strict[\s_-]*off\b", t) or re.search(
        r"\bdisable\s+wrath\s+strict\b", t
    ):
        return False
    if re.search(r"\bwrath[\s_-]*strict\b", t) or re.search(r"\benable\s+wrath\s+strict\b", t):
        if re.search(r"strict[\s_-]*off\b", t):
            return False
        return True
    return None


def parse_orchestrate_intent(text: str) -> bool | None:
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


def parse_privacy_intent(text: str) -> bool | None:
    t = (text or "").strip().lower()
    if not t:
        return None
    t = re.sub(r"^/", "", t)
    if re.search(r"\bwrath[\s_-]*privacy[\s_-]*off\b", t) or re.search(
        r"\bdisable\s+wrath\s+privacy\b", t
    ):
        return False
    if re.search(r"\bprivacy[\s_-]*off\b", t):
        return False
    if (
        re.search(r"\bwrath[\s_-]*privacy\b", t)
        or re.search(r"\benable\s+wrath\s+privacy\b", t)
        or re.search(r"\bprivacy[\s_-]*on\b", t)
    ):
        return True
    return None


def parse_profile_intent(text: str) -> str | None:
    t = (text or "").strip().lower()
    if not t:
        return None
    t = re.sub(r"^/", "", t)
    m = re.search(r"\bwrath[\s_-]*profile\s+(\w+)\b", t)
    if m and m.group(1) in PROFILES:
        return m.group(1)
    m = re.search(r"\bprofile\s+(\w+)\b", t)
    if m and m.group(1) in PROFILES and re.search(r"wrath|profile", t):
        return m.group(1)
    return None


def parse_yolo_intent(text: str) -> bool | None:
    """Return True=yolo on, False=off, None=no intent."""
    t = (text or "").strip().lower()
    if not t:
        return None
    t = re.sub(r"^/", "", t)
    if re.search(r"\bwrath[\s_-]*yolo[\s_-]*off\b", t) or re.search(
        r"\bdisable\s+wrath\s+yolo\b", t
    ):
        return False
    if re.search(r"\byolo[\s_-]*off\b", t) or re.search(r"\bdisable\s+yolo\b", t):
        return False
    if (
        re.search(r"\bwrath[\s_-]*yolo\b", t)
        or re.search(r"\benable\s+wrath\s+yolo\b", t)
        or re.search(r"\byolo[\s_-]*on\b", t)
        or re.search(r"\benable\s+yolo\b", t)
        or re.search(r"(?:^|\b)yolo\s*$", t)
    ):
        return True
    return None
