from journal import session_id_from_env


def test_session_id_from_event(monkeypatch):
    monkeypatch.delenv("GROK_SESSION_ID", raising=False)
    monkeypatch.delenv("CLAUDE_SESSION_ID", raising=False)
    assert session_id_from_env({"sessionId": "abc-123"}) == "abc-123"


def test_session_id_env_fallback(monkeypatch):
    monkeypatch.setenv("GROK_SESSION_ID", "env-id")
    assert session_id_from_env({}) == "env-id"
