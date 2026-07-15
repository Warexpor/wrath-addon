"""Compat re-export → wrath.journal."""

from __future__ import annotations

import _bootstrap  # noqa: F401
from wrath.journal import (  # noqa: F401
    append_event,
    count_tool_path,
    counts,
    journal_path,
    last_denies,
    session_id_from_env,
    session_stats,
    tail,
)
