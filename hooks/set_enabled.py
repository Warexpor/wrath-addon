#!/usr/bin/env python3
"""CLI: python set_enabled.py on|off|status|strict-on|strict-off|orchestrate-on|orchestrate-off"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from project_config import discover_start, load_project_config  # noqa: E402
from toggle import (  # noqa: E402
    is_orchestrate,
    is_strict,
    is_wrath_enabled,
    load_state,
    set_orchestrate,
    set_strict,
    set_wrath_enabled,
)


def main(argv: list[str]) -> int:
    if not argv or argv[0] in ("-h", "--help"):
        print(
            "usage: set_enabled.py on|off|status|strict-on|strict-off|"
            "orchestrate-on|orchestrate-off",
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
                    "strict": is_strict(project=cfg),
                    "orchestrate": is_orchestrate(),
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
    print(f"unknown: {cmd}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
