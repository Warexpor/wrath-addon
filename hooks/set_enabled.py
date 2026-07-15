#!/usr/bin/env python3
"""CLI: python set_enabled.py on|off|status|strict-*|orchestrate-*|il-*|privacy-*|profile <name>"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import _bootstrap  # noqa: E402, F401
from project_config import discover_start, load_project_config  # noqa: E402
from toggle import (  # noqa: E402
    get_profile,
    is_il,
    is_orchestrate,
    is_privacy,
    is_strict,
    is_wrath_enabled,
    load_state,
    set_il,
    set_orchestrate,
    set_privacy,
    set_profile,
    set_strict,
    set_wrath_enabled,
)


def main(argv: list[str]) -> int:
    if not argv or argv[0] in ("-h", "--help"):
        print(
            "usage: set_enabled.py on|off|status|strict-on|strict-off|"
            "orchestrate-on|orchestrate-off|il-on|il-off|"
            "privacy-on|privacy-off|profile <name>",
            file=sys.stderr,
        )
        return 2
    cmd = argv[0].lower()
    cfg = load_project_config(discover_start())
    if cmd in ("status", "get", "state"):
        state = load_state()
        print(
            json.dumps(
                {
                    "enabled": is_wrath_enabled(),
                    "profile": get_profile(project=cfg),
                    "strict": is_strict(project=cfg),
                    "orchestrate": is_orchestrate(),
                    "il": is_il(),
                    "privacy": is_privacy(),
                    "state": state,
                    "project_config": str(cfg.path) if cfg.path else None,
                },
                indent=2,
            )
        )
        return 0
    if cmd in ("on", "1", "true", "enable"):
        print(json.dumps(set_wrath_enabled(True, source="set_enabled.py"), indent=2))
        return 0
    if cmd in ("off", "0", "false", "disable"):
        print(json.dumps(set_wrath_enabled(False, source="set_enabled.py"), indent=2))
        return 0
    if cmd in ("strict-on", "strict_on", "strict"):
        print(json.dumps(set_strict(True, source="set_enabled.py"), indent=2))
        return 0
    if cmd in ("strict-off", "strict_off"):
        print(json.dumps(set_strict(False, source="set_enabled.py"), indent=2))
        return 0
    if cmd in ("orchestrate-on", "orchestrate_on", "orchestrate", "orch-on", "orch_on"):
        print(json.dumps(set_orchestrate(True, source="set_enabled.py"), indent=2))
        return 0
    if cmd in ("orchestrate-off", "orchestrate_off", "orch-off", "orch_off"):
        print(json.dumps(set_orchestrate(False, source="set_enabled.py"), indent=2))
        return 0
    if cmd in ("il-on", "il_on", "il"):
        print(json.dumps(set_il(True, source="set_enabled.py"), indent=2))
        return 0
    if cmd in ("il-off", "il_off"):
        print(json.dumps(set_il(False, source="set_enabled.py"), indent=2))
        return 0
    if cmd in ("privacy-on", "privacy_on", "privacy"):
        print(json.dumps(set_privacy(True, source="set_enabled.py"), indent=2))
        return 0
    if cmd in ("privacy-off", "privacy_off"):
        print(json.dumps(set_privacy(False, source="set_enabled.py"), indent=2))
        return 0
    if cmd == "profile":
        if len(argv) < 2:
            print("usage: set_enabled.py profile <name>", file=sys.stderr)
            return 2
        print(json.dumps(set_profile(argv[1], source="set_enabled.py"), indent=2))
        return 0
    print(f"unknown: {cmd}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
