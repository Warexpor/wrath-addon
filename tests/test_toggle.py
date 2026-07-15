import json
import os
from pathlib import Path

from toggle import is_wrath_enabled, parse_toggle_intent, set_wrath_enabled


def test_parse_toggle_intent():
    assert parse_toggle_intent("turn wrath off") is False
    assert parse_toggle_intent("Turn Wrath On") is True
    assert parse_toggle_intent("/wrath-off") is False
    assert parse_toggle_intent("/wrath-on") is True
    assert parse_toggle_intent("disable wrath") is False
    assert parse_toggle_intent("enable wrath please") is True
    assert parse_toggle_intent("turn forge off") is False  # legacy
    assert parse_toggle_intent("turn vanta off") is False  # legacy
    assert parse_toggle_intent("turn wrath off") is False
    assert parse_toggle_intent("fix the bug") is None


def test_set_enabled_roundtrip(tmp_path: Path, monkeypatch):
    monkeypatch.delenv("WRATH_OFF", raising=False)
    monkeypatch.delenv("WRATH_ON", raising=False)
    set_wrath_enabled(False, data_dir=tmp_path, source="test")
    assert is_wrath_enabled(tmp_path) is False
    set_wrath_enabled(True, data_dir=tmp_path, source="test")
    assert is_wrath_enabled(tmp_path) is True


def test_env_force_off(tmp_path: Path, monkeypatch):
    set_wrath_enabled(True, data_dir=tmp_path)
    monkeypatch.setenv("WRATH_OFF", "1")
    assert is_wrath_enabled(tmp_path) is False


def test_pre_allows_when_disabled(tmp_path: Path, monkeypatch):
    import subprocess
    import sys

    monkeypatch.delenv("WRATH_OFF", raising=False)
    set_wrath_enabled(False, data_dir=tmp_path)
    env = {**os.environ, "GROK_PLUGIN_DATA": str(tmp_path)}
    hooks = Path(__file__).resolve().parents[1] / "hooks"
    proc = subprocess.run(
        [sys.executable, str(hooks / "pre_tool_use.py")],
        input=json.dumps(
            {"toolName": "run_terminal_command", "toolInput": {"command": "rm -rf /"}}
        ),
        capture_output=True,
        text=True,
        env=env,
        cwd=str(hooks),
        check=False,
    )
    assert proc.returncode == 0
    out = json.loads(proc.stdout)
    assert out.get("decision") == "allow"


def test_user_prompt_toggles(tmp_path: Path, monkeypatch):
    import subprocess
    import sys

    monkeypatch.delenv("WRATH_OFF", raising=False)
    env = {**os.environ, "GROK_PLUGIN_DATA": str(tmp_path)}
    hooks = Path(__file__).resolve().parents[1] / "hooks"
    set_wrath_enabled(True, data_dir=tmp_path)
    proc = subprocess.run(
        [sys.executable, str(hooks / "user_prompt_submit.py")],
        input=json.dumps({"prompt": "turn wrath off"}),
        capture_output=True,
        text=True,
        env=env,
        cwd=str(hooks),
        check=False,
    )
    assert proc.returncode == 0
    out = json.loads(proc.stdout)
    assert "OFF" in out.get("systemMessage", "")
    assert is_wrath_enabled(tmp_path) is False


def test_user_prompt_toggle_on_injects_drive(tmp_path: Path, monkeypatch):
    import subprocess
    import sys

    monkeypatch.delenv("WRATH_OFF", raising=False)
    env = {**os.environ, "GROK_PLUGIN_DATA": str(tmp_path)}
    hooks = Path(__file__).resolve().parents[1] / "hooks"
    set_wrath_enabled(False, data_dir=tmp_path)
    proc = subprocess.run(
        [sys.executable, str(hooks / "user_prompt_submit.py")],
        input=json.dumps({"prompt": "turn wrath on"}),
        capture_output=True,
        text=True,
        env=env,
        cwd=str(hooks),
        check=False,
    )
    assert proc.returncode == 0
    out = json.loads(proc.stdout)
    msg = out.get("systemMessage", "")
    assert "Wrath mode" in msg
    assert "Ladder" in msg
    assert is_wrath_enabled(tmp_path) is True


def test_user_prompt_toggle_nested_content(tmp_path: Path, monkeypatch):
    import subprocess
    import sys

    monkeypatch.delenv("WRATH_OFF", raising=False)
    env = {**os.environ, "GROK_PLUGIN_DATA": str(tmp_path)}
    hooks = Path(__file__).resolve().parents[1] / "hooks"
    set_wrath_enabled(True, data_dir=tmp_path)
    proc = subprocess.run(
        [sys.executable, str(hooks / "user_prompt_submit.py")],
        input=json.dumps({"content": [{"text": "turn wrath off"}]}),
        capture_output=True,
        text=True,
        env=env,
        cwd=str(hooks),
        check=False,
    )
    assert proc.returncode == 0
    assert is_wrath_enabled(tmp_path) is False


def test_post_drains_stdin_when_disabled(tmp_path: Path, monkeypatch):
    import subprocess
    import sys

    monkeypatch.delenv("WRATH_OFF", raising=False)
    set_wrath_enabled(False, data_dir=tmp_path)
    env = {**os.environ, "GROK_PLUGIN_DATA": str(tmp_path)}
    hooks = Path(__file__).resolve().parents[1] / "hooks"
    proc = subprocess.run(
        [sys.executable, str(hooks / "post_tool_use.py")],
        input=json.dumps({"toolName": "read_file", "toolInput": {"path": "x"}}),
        capture_output=True,
        text=True,
        env=env,
        cwd=str(hooks),
        check=False,
    )
    assert proc.returncode == 0
    journal = tmp_path / "journal.jsonl"
    assert not journal.is_file()
