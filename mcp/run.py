#!/usr/bin/env python3
"""Launch Wrath MCP server with correct paths."""

from __future__ import annotations

import runpy
import sys
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PLUGIN_ROOT / "src"))
sys.path.insert(0, str(PLUGIN_ROOT / "hooks"))
# Ensure plugin root is process cwd so relative imports stay sane
try:
    import os

    os.chdir(PLUGIN_ROOT)
except OSError:
    pass

runpy.run_path(str(Path(__file__).resolve().parent / "server.py"), run_name="__main__")
