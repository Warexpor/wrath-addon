"""Compat re-export → wrath.io."""

from __future__ import annotations

import _bootstrap  # noqa: F401
from wrath.event import normalize as _normalize
from wrath.io import (  # noqa: F401
    emit,
    ensure_mcp_config,
    log_hook_error,
    looks_like_secret_path,
    mcp_launcher_path,
    normalize_path_key,
    plugin_data,
    plugin_root,
    plugin_version,
    read_stdin_json,
    split_shell_segments,
)


def tool_name(event: dict) -> str:
    return _normalize(event).tool_name


def tool_input(event: dict) -> dict:
    return _normalize(event).tool_input


def shell_command(event: dict) -> str:
    return _normalize(event).shell_command


def prompt_text(event: dict) -> str:
    return _normalize(event).prompt
