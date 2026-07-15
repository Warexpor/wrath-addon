import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOOKS = ROOT / "hooks"


def _plugin_tree(tmp_path: Path) -> Path:
    """Isolated plugin root so SessionStart MCP patch cannot dirties the real repo."""
    root = tmp_path / "plugin"
    if root.is_dir():
        return root
    root.mkdir(parents=True)
    (root / ".claude-plugin").mkdir()
    (root / ".claude-plugin" / "plugin.json").write_text(
        json.dumps({"name": "wrath", "version": "0.0.0-test"}),
        encoding="utf-8",
    )
    mcp = root / "mcp"
    mcp.mkdir()
    # minimal launchers so ensure_mcp_config can resolve a path
    (mcp / "launch.cmd").write_text("@echo off\n", encoding="utf-8")
    (mcp / "run.py").write_text("# test stub\n", encoding="utf-8")
    # hooks live in real tree; bootstrap needs src on path via real hooks dir
    return root


def _run_hook(script: str, payload: dict, tmp_path: Path, env: dict | None = None) -> dict:
    data = tmp_path / "data"
    data.mkdir(exist_ok=True)
    plugin = _plugin_tree(tmp_path)
    e = {
        **os.environ,
        "GROK_PLUGIN_DATA": str(data),
        "GROK_PLUGIN_ROOT": str(plugin),
    }
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


def test_session_start_does_not_touch_repo_mcp(tmp_path: Path):
    """Regression: SessionStart must not rewrite the source-tree .mcp.json."""
    mcp_path = ROOT / ".mcp.json"
    before = mcp_path.read_text(encoding="utf-8") if mcp_path.is_file() else None
    _run_hook("session_start.py", {}, tmp_path)
    after = mcp_path.read_text(encoding="utf-8") if mcp_path.is_file() else None
    assert after == before


def test_session_start_orchestrate_injects_routing(tmp_path: Path):
    from toggle import set_orchestrate

    data = tmp_path / "data"
    data.mkdir(exist_ok=True)
    set_orchestrate(True, data_dir=data, source="test")
    res = _run_hook("session_start.py", {}, tmp_path)
    msg = res["systemMessage"]
    assert "orch=on" in msg
    assert "ORCHESTRATE" in msg or "LEAD" in msg


def test_session_start_il_injects_wire(tmp_path: Path):
    from toggle import set_il

    data = tmp_path / "data"
    data.mkdir(exist_ok=True)
    set_il(True, data_dir=data, source="test")
    res = _run_hook("session_start.py", {}, tmp_path)
    msg = res["systemMessage"]
    assert "il=on" in msg
    assert "IL" in msg or "agent wire" in msg.lower()


def test_session_start_privacy_injects_body(tmp_path: Path):
    from toggle import set_privacy

    data = tmp_path / "data"
    data.mkdir(exist_ok=True)
    set_privacy(True, data_dir=data, source="test")
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
