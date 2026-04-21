import pytest
from unittest.mock import patch, MagicMock

FAKE_RESULT = {"tool": "faketool", "query": "test", "returncode": 0, "output": "found something"}

def fake_run_tool(name, args, query, on_line):
    if on_line:
        on_line("fake output line")
    return {**FAKE_RESULT, "tool": name}

def test_email_lookup_returns_list():
    with patch("core.runner.run_tool", side_effect=fake_run_tool):
        from modules.email import lookup
        results = lookup("foo@bar.com", on_line=None)
    assert isinstance(results, list)
    assert all("tool" in r for r in results)

def test_username_lookup_returns_list():
    with patch("core.runner.run_tool", side_effect=fake_run_tool):
        from modules.username import lookup
        results = lookup("johndoe", on_line=None)
    assert isinstance(results, list)
    assert all("tool" in r for r in results)

def test_phone_lookup_returns_list():
    with patch("core.runner.run_tool", side_effect=fake_run_tool):
        from modules.phone import lookup
        results = lookup("+15551234567", on_line=None)
    assert isinstance(results, list)

def test_name_lookup_returns_list():
    with patch("core.runner.run_tool", side_effect=fake_run_tool):
        from modules.name import lookup
        results = lookup("John Doe", on_line=None)
    assert isinstance(results, list)
