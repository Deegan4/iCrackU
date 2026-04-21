import pytest
from unittest.mock import patch, MagicMock
from core.runner import check_tool, run_tool

def test_check_tool_found():
    with patch("shutil.which", return_value="/usr/bin/echo"):
        assert check_tool("echo") is True

def test_check_tool_missing():
    with patch("shutil.which", return_value=None):
        assert check_tool("notarealthing") is False

def test_run_tool_missing_returns_error_dict():
    with patch("shutil.which", return_value=None):
        result = run_tool("notarealthing", ["arg"], "testquery", on_line=None)
    assert result["tool"] == "notarealthing"
    assert result["returncode"] == -1
    assert "not found" in result["output"].lower()

def test_run_tool_runs_command():
    lines_seen = []
    with patch("shutil.which", return_value="/usr/bin/echo"):
        result = run_tool("echo", ["hello"], "hello", on_line=lambda l: lines_seen.append(l))
    assert result["returncode"] == 0
    assert "hello" in result["output"]
    assert any("hello" in l for l in lines_seen)
