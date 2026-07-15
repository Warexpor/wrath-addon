"""Multi-depth nested shell unwrap."""

from __future__ import annotations

import re

_NESTED = re.compile(
    r"^\s*(?:"
    r"(?:powershell|pwsh)(?:\.exe)?\s+(?:-\w+\s+)*-(?:c|Command|command)\s+"
    r"|(?:bash|sh|zsh)(?:\.exe)?\s+(?:-l\s+)?-c\s+"
    r"|cmd(?:\.exe)?\s+/c\s+"
    r")(?P<q>['\"])(?P<body>.*)(?P=q)\s*$",
    re.I | re.DOTALL,
)


def unwrap_once(cmd: str) -> str | None:
    m = _NESTED.match((cmd or "").strip())
    if not m:
        return None
    return m.group("body")


def unwrap_nested_shell(cmd: str, max_depth: int = 1) -> str:
    """Extract inner payload from powershell/bash/cmd wrappers up to max_depth."""
    cur = cmd
    for _ in range(max(max_depth, 0)):
        inner = unwrap_once(cur)
        if inner is None:
            break
        cur = inner
    return cur


def fully_unwrap(cmd: str, max_depth: int = 3) -> list[str]:
    """Return chain [outer, ..., innermost] for evaluation of each layer."""
    chain = [cmd]
    cur = cmd
    for _ in range(max(max_depth, 0)):
        inner = unwrap_once(cur)
        if inner is None:
            break
        chain.append(inner)
        cur = inner
    return chain
