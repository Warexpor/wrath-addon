import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOOKS = ROOT / "hooks"


def _run_hook(script: str, payload: dict, tmp_path: Path, env: dict | None = None) -> dict:
    e = {**os.environ, "GROK_PLUGIN_DATA": str(tmp_path)}
    if env:
        e.update(env)
    proc = subprocess.run(
        [sys.executable, str(HOOKS / script)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        cwd=str(HOOKS),
        env=e,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr
    out = (proc.stdout or "").strip()
    if not out:
        return {}
    return json.loads(out)


def test_pre_deny_rm_rf(tmp_path: Path):
    res = _run_hook(
        "pre_tool_use.py",
        {
            "toolName": "run_terminal_command",
            "toolInput": {"command": "rm -rf /"},
        },
        tmp_path,
    )
    assert res.get("decision") == "deny"


def test_pre_allow_git_status(tmp_path: Path):
    res = _run_hook(
        "pre_tool_use.py",
        {
            "toolName": "run_terminal_command",
            "toolInput": {"command": "git status"},
        },
        tmp_path,
    )
    assert res.get("decision", "allow") == "allow"


def test_session_start_has_drive(tmp_path: Path):
    res = _run_hook("session_start.py", {}, tmp_path)
    assert "systemMessage" in res
    msg = res["systemMessage"]
    assert "Wrath" in msg
    assert "v" in msg  # status line version
    assert "strict=" in msg
    assert "orch=" in msg
    assert "il=" in msg
    assert "privacy=" in msg
    assert "profile=" in msg


def test_session_start_orchestrate_injects_routing(tmp_path: Path):
    from toggle import set_orchestrate

    set_orchestrate(True, data_dir=tmp_path, source="test")
    res = _run_hook("session_start.py", {}, tmp_path)
    msg = res["systemMessage"]
    assert "orch=on" in msg
    assert "ORCHESTRATE" in msg or "LEAD" in msg


def test_session_start_il_injects_wire(tmp_path: Path):
    from toggle import set_il

    set_il(True, data_dir=tmp_path, source="test")
    res = _run_hook("session_start.py", {}, tmp_path)
    msg = res["systemMessage"]
    assert "il=on" in msg
    assert "IL" in msg or "agent wire" in msg.lower()


def test_session_start_privacy_injects_body(tmp_path: Path):
    from toggle import set_privacy

    set_privacy(True, data_dir=tmp_path, source="test")
    res = _run_hook("session_start.py", {}, tmp_path)
    msg = res["systemMessage"]
    assert "privacy=on" in msg
    assert "PRIVACY" in msg


def test_pre_deny_nested_powershell_bash(tmp_path: Path):
    res = _run_hook(
        "pre_tool_use.py",
        {
            "toolName": "run_terminal_command",
            "toolInput": {"command": "powershell -Command \"bash -c 'rm -rf /'\""},
        },
        tmp_path,
    )
    assert res.get("decision") == "deny"
