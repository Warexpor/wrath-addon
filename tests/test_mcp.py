import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SERVER = ROOT / "mcp" / "run.py"


def _rpc(proc_in: list[dict], data_dir: Path) -> list[dict]:
    payload = "\n".join(json.dumps(m) for m in proc_in) + "\n"
    env = {
        **os.environ,
        "GROK_PLUGIN_DATA": str(data_dir),
        "GROK_PLUGIN_ROOT": str(ROOT),
    }
    proc = subprocess.run(
        [sys.executable, str(SERVER)],
        input=payload,
        capture_output=True,
        text=True,
        env=env,
        cwd=str(Path.home()),  # prove cwd-independence
        check=False,
    )
    assert proc.returncode == 0, proc.stderr
    outs = []
    for line in (proc.stdout or "").splitlines():
        line = line.strip()
        if line:
            outs.append(json.loads(line))
    return outs


def test_mcp_initialize_and_tools(tmp_path: Path):
    outs = _rpc(
        [
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "test", "version": "0"},
                },
            },
            {"jsonrpc": "2.0", "method": "notifications/initialized"},
            {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
        ],
        tmp_path,
    )
    assert outs[0]["result"]["serverInfo"]["name"] == "wrath-mcp"
    assert outs[0]["result"]["serverInfo"]["version"]
    names = {t["name"] for t in outs[1]["result"]["tools"]}
    assert "wrath_doctor" in names
    assert "wrath_policy_check" in names
    assert "wrath_session_stats" in names
    assert "wrath_config" in names
    assert "wrath_set_il" in names


def test_mcp_policy_check(tmp_path: Path):
    outs = _rpc(
        [
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "test", "version": "0"},
                },
            },
            {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {
                    "name": "wrath_policy_check",
                    "arguments": {"command": "rm -rf /"},
                },
            },
        ],
        tmp_path,
    )
    text = outs[1]["result"]["content"][0]["text"]
    body = json.loads(text)
    assert body["allow"] is False
