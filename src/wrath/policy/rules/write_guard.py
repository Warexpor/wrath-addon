from __future__ import annotations

from wrath.policy.decision import Decision


def path_is_git_internal(path: str) -> bool:
    p = (path or "").replace("\\", "/").lower()
    return "/.git/" in f"/{p}/" or p.endswith("/.git") or p == ".git"


def check_write_git(path: str) -> Decision | None:
    if path and path_is_git_internal(path):
        return Decision(
            allow=False,
            reason="Wrath: blocked write into .git/ (internal git objects)",
            rule_id="write_git_internal",
            severity="deny",
        )
    return None
