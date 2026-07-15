from pathlib import Path

from journal import append_event, counts, session_stats, tail


def test_journal_roundtrip(tmp_path: Path):
    append_event(tmp_path, {"kind": "tool", "tool": "read_file", "session_id": "s1"})
    append_event(tmp_path, {"kind": "deny", "reason": "x", "session_id": "s1"})
    append_event(tmp_path, {"kind": "stop", "session_id": "s1"})
    rows = tail(tmp_path, n=10)
    assert len(rows) == 3
    c = counts(tmp_path)
    assert c["tools"] == 1
    assert c["denies"] == 1
    assert c["stops"] == 1


def test_tail_filter_kind(tmp_path: Path):
    append_event(tmp_path, {"kind": "tool", "tool": "a"})
    append_event(tmp_path, {"kind": "deny", "reason": "nope"})
    append_event(tmp_path, {"kind": "tool", "tool": "b"})
    rows = tail(tmp_path, n=10, kind="deny")
    assert len(rows) == 1
    assert rows[0]["kind"] == "deny"


def test_session_stats(tmp_path: Path):
    append_event(tmp_path, {"kind": "tool", "tool": "read_file", "session_id": "abc"})
    append_event(tmp_path, {"kind": "tool", "tool": "read_file", "session_id": "abc"})
    append_event(tmp_path, {"kind": "tool", "tool": "grep", "session_id": "abc"})
    append_event(tmp_path, {"kind": "deny", "tool": "bash", "reason": "x", "session_id": "abc"})
    append_event(tmp_path, {"kind": "tool", "tool": "other", "session_id": "zzz"})
    stats = session_stats(tmp_path, "abc")
    assert stats["events"] == 4
    assert stats["tool_histogram"]["read_file"] == 2
    assert stats["deny_count"] == 1


def test_count_tool_path(tmp_path: Path):
    from journal import count_tool_path

    append_event(
        tmp_path,
        {"kind": "tool", "tool": "read_file", "path": "src/a.py", "session_id": "s1"},
    )
    append_event(
        tmp_path,
        {"kind": "tool", "tool": "read_file", "path": "src/a.py", "session_id": "s1"},
    )
    append_event(
        tmp_path,
        {"kind": "tool", "tool": "read_file", "path": "src/b.py", "session_id": "s1"},
    )
    assert count_tool_path(tmp_path, "s1", "src/a.py") == 2
    assert count_tool_path(tmp_path, "s1", "src/b.py") == 1
