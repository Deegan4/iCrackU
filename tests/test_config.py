import json
import pytest
from unittest.mock import patch
import core.config


def test_get_key_returns_none_when_missing(tmp_path):
    with patch.object(core.config, "KEYS_FILE", str(tmp_path / "keys.json")):
        assert core.config.get_key("shodan") is None


def test_get_key_returns_value_when_present(tmp_path):
    keys_file = tmp_path / "keys.json"
    keys_file.write_text(json.dumps({"shodan": "abc123"}))
    with patch.object(core.config, "KEYS_FILE", str(keys_file)):
        assert core.config.get_key("shodan") == "abc123"


def test_prompt_and_save_key_writes_file(tmp_path):
    keys_file = tmp_path / "keys.json"
    with (
        patch.object(core.config, "KEYS_FILE", str(keys_file)),
        patch.object(core.config, "CONFIG_DIR", str(tmp_path)),
        patch.object(core.config, "console") as mock_console,
    ):
        mock_console.input.return_value = "mykey"
        result = core.config.prompt_and_save_key("shodan", "Enter key: ")
    assert result == "mykey"
    assert json.loads(keys_file.read_text())["shodan"] == "mykey"


def test_prompt_and_save_key_returns_none_on_empty(tmp_path):
    keys_file = tmp_path / "keys.json"
    with (
        patch.object(core.config, "KEYS_FILE", str(keys_file)),
        patch.object(core.config, "CONFIG_DIR", str(tmp_path)),
        patch.object(core.config, "console") as mock_console,
    ):
        mock_console.input.return_value = ""
        result = core.config.prompt_and_save_key("shodan", "Enter key: ")
    assert result is None
    assert json.loads(keys_file.read_text()).get("shodan") == "__skip__"


def test_require_key_returns_cached_key(tmp_path):
    keys_file = tmp_path / "keys.json"
    keys_file.write_text(json.dumps({"hibp": "xyz"}))
    with (
        patch.object(core.config, "KEYS_FILE", str(keys_file)),
        patch.object(core.config, "console") as mock_console,
    ):
        result = core.config.require_key("hibp", "Enter key: ")
    assert result == "xyz"
    mock_console.input.assert_not_called()


def test_require_key_prompts_when_missing(tmp_path):
    keys_file = tmp_path / "keys.json"
    with (
        patch.object(core.config, "KEYS_FILE", str(keys_file)),
        patch.object(core.config, "CONFIG_DIR", str(tmp_path)),
        patch.object(core.config, "console") as mock_console,
    ):
        mock_console.input.return_value = "newkey"
        result = core.config.require_key("hibp", "Enter key: ")
    assert result == "newkey"


def test_require_key_skip_sentinel_prevents_reprompt(tmp_path):
    keys_file = tmp_path / "keys.json"
    keys_file.write_text(json.dumps({"shodan": "__skip__"}))
    with (
        patch.object(core.config, "KEYS_FILE", str(keys_file)),
        patch.object(core.config, "console") as mock_console,
    ):
        result = core.config.require_key("shodan", "Enter key: ")
    assert result is None
    mock_console.input.assert_not_called()
