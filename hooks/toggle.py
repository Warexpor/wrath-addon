"""Compat re-export → wrath.state."""

from __future__ import annotations

import _bootstrap  # noqa: F401
from wrath.state import (  # noqa: F401
    get_profile,
    is_il,
    is_orchestrate,
    is_privacy,
    is_strict,
    is_wrath_enabled,
    load_state,
    parse_il_intent,
    parse_orchestrate_intent,
    parse_privacy_intent,
    parse_profile_intent,
    parse_strict_intent,
    parse_toggle_intent,
    set_il,
    set_orchestrate,
    set_privacy,
    set_profile,
    set_strict,
    set_wrath_enabled,
)
