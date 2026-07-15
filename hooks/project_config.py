"""Compat re-export → wrath.config."""

from __future__ import annotations

import _bootstrap  # noqa: F401
from wrath.config import (  # noqa: F401
    EffectiveConfig,
    budget_tools_effective,
    discover_start,
    find_config_file,
    load_project_config,
    nested_depth_effective,
    reread_warn_effective,
)
