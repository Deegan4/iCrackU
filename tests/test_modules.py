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

def test_address_lookup_returns_list():
    mock_location = MagicMock()
    mock_location.address = "123 Main St, New York, USA"
    mock_location.latitude = 40.7128
    mock_location.longitude = -74.0060
    mock_location.raw = {"display_name": "123 Main St, New York, USA", "type": "house"}

    with patch("geopy.geocoders.Nominatim.geocode", return_value=mock_location):
        from modules.address import lookup
        results = lookup("123 Main St, New York", on_line=None)
    assert isinstance(results, list)
    assert len(results) == 1
    assert results[0]["tool"] == "nominatim"
    assert results[0]["returncode"] == 0
