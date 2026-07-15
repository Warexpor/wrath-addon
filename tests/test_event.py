import json
from pathlib import Path

from wrath.event import normalize


def test_normalize_fixture():
    p = Path(__file__).parent / "fixtures" / "hooks" / "pre_tool_use_shell.json"
    raw = json.loads(p.read_text(encoding="utf-8"))
    he = normalize(raw)
    assert he.session_id == "test-session-1"
    assert he.tool_name == "run_terminal_command"
    assert he.shell_command == "git status"
