import json
import os
from pathlib import Path

from toggle import (
    get_profile,
    is_orchestrate,
    is_privacy,
    is_strict,
    is_wrath_enabled,
    is_yolo,
    parse_orchestrate_intent,
    parse_privacy_intent,
    parse_profile_intent,
    parse_strict_intent,
    parse_toggle_intent,
    parse_yolo_intent,
    set_orchestrate,
    set_privacy,
    set_profile,
    set_strict,
    set_wrath_enabled,
    set_yolo,
)


def test_parse_toggle_intent():
    assert parse_toggle_intent("turn wrath off") is False
    assert parse_toggle_intent("Turn Wrath On") is True
    assert parse_toggle_intent("/wrath-off") is False
    assert parse_toggle_intent("/wrath-on") is True
    assert parse_toggle_intent("disable wrath") is False
    assert parse_toggle_intent("enable wrath please") is True
    assert parse_toggle_intent("turn forge off") is False
    assert parse_toggle_intent("turn vanta off") is False
    assert parse_toggle_intent("turn wrath off") is False
    assert parse_toggle_intent("fix the bug") is None


def test_parse_strict_intent():
    assert parse_strict_intent("/wrath-strict") is True
    assert parse_strict_intent("wrath-strict-off") is False
    assert parse_strict_intent("hello") is None
    assert parse_toggle_intent("disable wrath strict") is None
    assert parse_toggle_intent("wrath-strict-off") is None
    assert parse_strict_intent("disable wrath strict") is False


def test_parse_orchestrate_intent():
    assert parse_orchestrate_intent("/wrath-orchestrate") is True
    assert parse_orchestrate_intent("wrath-orchestrate-off") is False
    assert parse_orchestrate_intent("multi-model on") is True
    assert parse_orchestrate_intent("multi-model off") is False
    assert parse_orchestrate_intent("hello") is None
    assert parse_toggle_intent("/wrath-orchestrate") is None
    assert parse_toggle_intent("multi-model on") is None
    assert parse_toggle_intent("disable multi-model") is None


def test_parse_privacy_intent():
    assert parse_privacy_intent("/wrath-privacy") is True
    assert parse_privacy_intent("wrath-privacy-off") is False
    assert parse_privacy_intent("privacy on") is True
    assert parse_privacy_intent("privacy off") is False
    assert parse_privacy_intent("hello") is None
    assert parse_toggle_intent("/wrath-privacy") is None
    assert parse_toggle_intent("privacy on") is None


def test_parse_profile_intent():
    assert parse_profile_intent("/wrath-profile fleet") == "fleet"
    assert parse_profile_intent("wrath profile privacy") == "privacy"
    assert parse_profile_intent("/wrath-profile yolo") == "yolo"
    assert parse_profile_intent("hello") is None
    assert parse_toggle_intent("/wrath-profile fleet") is None


def test_parse_yolo_intent():
    assert parse_yolo_intent("/wrath-yolo") is True
    assert parse_yolo_intent("wrath-yolo-off") is False
    assert parse_yolo_intent("yolo on") is True
    assert parse_yolo_intent("yolo off") is False
    assert parse_yolo_intent("hello") is None
    assert parse_toggle_intent("/wrath-yolo") is None


def test_set_strict_roundtrip(tmp_path: Path, monkeypatch):
    monkeypatch.delenv("WRATH_STRICT", raising=False)
    set_strict(True, data_dir=tmp_path, source="test")
    assert is_strict(tmp_path) is True
    set_strict(False, data_dir=tmp_path, source="test")
    assert is_strict(tmp_path) is False


def test_set_privacy_roundtrip(tmp_path: Path, monkeypatch):
    monkeypatch.delenv("WRATH_PRIVACY", raising=False)
    set_privacy(True, data_dir=tmp_path, source="test")
    assert is_privacy(tmp_path) is True
    set_privacy(False, data_dir=tmp_path, source="test")
    assert is_privacy(tmp_path) is False


def test_set_profile_roundtrip(tmp_path: Path, monkeypatch):
    monkeypatch.delenv("WRATH_STRICT", raising=False)
    monkeypatch.delenv("WRATH_ORCHESTRATE", raising=False)
    monkeypatch.delenv("WRATH_PRIVACY", raising=False)
    monkeypatch.delenv("WRATH_YOLO", raising=False)
    set_profile("fleet", data_dir=tmp_path, source="test")
    assert get_profile(tmp_path) == "fleet"
    assert is_orchestrate(tmp_path) is True
    set_profile("default", data_dir=tmp_path, source="test")
    assert get_profile(tmp_path) == "default"


def test_set_yolo_profile(tmp_path: Path, monkeypatch):
    monkeypatch.delenv("WRATH_YOLO", raising=False)
    monkeypatch.delenv("WRATH_PRIVACY", raising=False)
    set_yolo(True, data_dir=tmp_path, source="test")
    assert is_yolo(tmp_path) is True
    assert get_profile(tmp_path) == "yolo"
    assert is_privacy(tmp_path) is False
    set_profile("yolo", data_dir=tmp_path, source="test")
    assert is_yolo(tmp_path) is True
    set_yolo(False, data_dir=tmp_path, source="test")
    assert is_yolo(tmp_path) is False


def test_set_orchestrate_roundtrip(tmp_path: Path, monkeypatch):
    monkeypatch.delenv("WRATH_ORCHESTRATE", raising=False)
    set_orchestrate(True, data_dir=tmp_path, source="test")
    assert is_orchestrate(tmp_path) is True
    set_orchestrate(False, data_dir=tmp_path, source="test")
    assert is_orchestrate(tmp_path) is False


def test_orchestrate_preserves_other_flags(tmp_path: Path, monkeypatch):
    monkeypatch.delenv("WRATH_ORCHESTRATE", raising=False)
    monkeypatch.delenv("WRATH_STRICT", raising=False)
    set_wrath_enabled(True, data_dir=tmp_path, source="test")
    set_strict(True, data_dir=tmp_path, source="test")
    set_orchestrate(True, data_dir=tmp_path, source="test")
    assert is_strict(tmp_path) is True
    assert is_wrath_enabled(tmp_path) is True
    set_wrath_enabled(False, data_dir=tmp_path, source="test")
    assert is_orchestrate(tmp_path) is True
    assert is_strict(tmp_path) is True


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
    assert "Wrath" in msg
    assert "ON" in msg
    assert "Ladder" in msg or "Drive:" in msg
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


def test_user_prompt_orchestrate_on(tmp_path: Path, monkeypatch):
    import subprocess
    import sys

    monkeypatch.delenv("WRATH_ORCHESTRATE", raising=False)
    env = {**os.environ, "GROK_PLUGIN_DATA": str(tmp_path)}
    hooks = Path(__file__).resolve().parents[1] / "hooks"
    set_orchestrate(False, data_dir=tmp_path)
    proc = subprocess.run(
        [sys.executable, str(hooks / "user_prompt_submit.py")],
        input=json.dumps({"prompt": "/wrath-orchestrate"}),
        capture_output=True,
        text=True,
        env=env,
        cwd=str(hooks),
        check=False,
    )
    assert proc.returncode == 0
    out = json.loads(proc.stdout)
    msg = out.get("systemMessage", "")
    assert "orchestrate=on" in msg
    assert "ORCHESTRATE" in msg or "LEAD" in msg
    assert is_orchestrate(tmp_path) is True


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
