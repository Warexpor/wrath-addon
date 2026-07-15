#!/usr/bin/env python3
"""Launch Wrath MCP server with stable paths (cwd-independent)."""

from __future__ import annotations

import os
import runpy
import sys
from pathlib import Path

# Ensure plugin root is on path and is process cwd so relative imports stay sane
PLUGIN_ROOT = Path(__file__).resolve().parent.parent
os.environ.setdefault("GROK_PLUGIN_ROOT", str(PLUGIN_ROOT))
os.environ.setdefault("CLAUDE_PLUGIN_ROOT", str(PLUGIN_ROOT))
sys.path.insert(0, str(PLUGIN_ROOT / "hooks"))
try:
    os.chdir(PLUGIN_ROOT)
except OSError:
    pass

if __name__ == "__main__":
    runpy.run_path(str(Path(__file__).resolve().parent / "server.py"), run_name="__main__")
