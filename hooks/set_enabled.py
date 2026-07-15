#!/usr/bin/env python3
"""CLI: python set_enabled.py on|off|status"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from toggle import is_wrath_enabled, load_state, set_wrath_enabled  # noqa: E402


def main(argv: list[str]) -> int:
    if not argv or argv[0] in ("-h", "--help"):
        print("usage: set_enabled.py on|off|status", file=sys.stderr)
        return 2
    cmd = argv[0].lower()
    if cmd in ("status", "get", "state"):
        print(json.dumps({"enabled": is_wrath_enabled(), **load_state()}, indent=2))
        return 0
    if cmd in ("on", "1", "true", "enable"):
        print(json.dumps(set_wrath_enabled(True, source="set_enabled.py"), indent=2))
        return 0
    if cmd in ("off", "0", "false", "disable"):
        print(json.dumps(set_wrath_enabled(False, source="set_enabled.py"), indent=2))
        return 0
    print(f"unknown: {cmd}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
