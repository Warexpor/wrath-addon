from common import prompt_text, split_shell_segments, looks_like_secret_path


def test_prompt_text_string_keys():
    assert prompt_text({"userPrompt": "turn wrath on"}) == "turn wrath on"


def test_prompt_text_nested_content():
    event = {
        "content": [{"text": "turn wrath off"}, {"content": "more context"}]
    }
    assert prompt_text(event) == "turn wrath off\nmore context"


def test_prompt_text_empty():
    assert prompt_text({}) == ""


def test_split_shell_segments():
    segs = split_shell_segments("echo a; rm -rf / && true")
    assert len(segs) >= 2
    assert any("rm" in s for s in segs)


def test_looks_like_secret_path():
    assert looks_like_secret_path("/home/u/.env")
    assert looks_like_secret_path("C:\\Users\\x\\.ssh\\id_rsa")
    assert not looks_like_secret_path("src/main.py")
