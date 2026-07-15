from pathlib import Path

from project_config import load_project_config


def test_defaults_when_missing(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    cfg = load_project_config(tmp_path)
    assert cfg.path is None
    assert cfg.budget_tools == 80
    assert cfg.reread_warn == 3
    assert cfg.deny == ()


def test_json_config(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".wrath.json").write_text(
        '{"strict": true, "budget_tools": 40, "reread_warn": 2, "deny": ["\\\\bnuke\\\\b"]}',
        encoding="utf-8",
    )
    cfg = load_project_config(tmp_path)
    assert cfg.strict is True
    assert cfg.budget_tools == 40
    assert cfg.reread_warn == 2
    assert len(cfg.deny) == 1
    assert cfg.path is not None


def test_bad_regex_dropped(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".wrath.json").write_text(
        '{"deny": ["(unclosed", "okword"]}',
        encoding="utf-8",
    )
    cfg = load_project_config(tmp_path)
    assert cfg.deny == ("okword",)
