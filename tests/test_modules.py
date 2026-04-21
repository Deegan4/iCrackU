import pytest
from unittest.mock import patch, MagicMock

FAKE_RESULT = {
    "tool": "faketool",
    "query": "test",
    "returncode": 0,
    "output": "found something",
}


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


def test_ip_lookup_returns_list():
    mock_resp = MagicMock()
    mock_resp.json.return_value = {
        "ip": "8.8.8.8",
        "city": "Mountain View",
        "org": "AS15169 Google",
    }
    with (
        patch("modules.ip.requests.get", return_value=mock_resp),
        patch(
            "modules.ip.socket.gethostbyaddr",
            return_value=("dns.google", [], ["8.8.8.8"]),
        ),
        patch("core.runner.run_tool", side_effect=fake_run_tool),
        patch("modules.ip.require_key", return_value=None),
    ):
        from modules.ip import lookup

        results = lookup("8.8.8.8", on_line=None)
    assert isinstance(results, list)
    assert all("tool" in r for r in results)
    assert any(r["tool"] == "ipinfo" for r in results)


def test_domain_lookup_returns_list():
    mock_whois = MagicMock()
    mock_whois.registrar = "GoDaddy"
    mock_whois.creation_date = "2000-01-01"
    mock_whois.expiration_date = "2030-01-01"
    mock_whois.name_servers = ["ns1.example.com", "ns2.example.com"]

    mock_answer = MagicMock()
    mock_answer.__iter__ = MagicMock(
        return_value=iter([MagicMock(address="93.184.216.34")])
    )

    with (
        patch("modules.domain.whois.whois", return_value=mock_whois),
        patch("modules.domain.dns.resolver.resolve", return_value=mock_answer),
        patch("core.runner.run_tool", side_effect=fake_run_tool),
    ):
        from modules.domain import lookup

        results = lookup("example.com", on_line=None)
    assert isinstance(results, list)
    assert all("tool" in r for r in results)
    assert any(r["tool"] == "whois-py" for r in results)


def test_breach_lookup_returns_list():
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = [
        {"Name": "Adobe", "PwnCount": 153000000, "IsVerified": True},
        {"Name": "LinkedIn", "PwnCount": 164611595, "IsVerified": True},
    ]
    with (
        patch("modules.breach.requests.get", return_value=mock_resp),
        patch("modules.breach.require_key", return_value="testkey"),
    ):
        from modules.breach import lookup

        results = lookup("foo@bar.com", on_line=None)
    assert isinstance(results, list)
    assert any(r["tool"] == "hibp" for r in results)
    assert results[0]["returncode"] == 0


def test_hash_lookup_returns_list():
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "data": {
            "attributes": {
                "meaningful_name": "eicar.txt",
                "last_analysis_stats": {"malicious": 0, "harmless": 70},
                "type_description": "Text",
            }
        }
    }
    with (
        patch("core.runner.run_tool", side_effect=fake_run_tool),
        patch("modules.hash.requests.get", return_value=mock_resp),
        patch("modules.hash.require_key", return_value="vtkey"),
    ):
        from modules.hash import lookup

        results = lookup("d41d8cd98f00b204e9800998ecf8427e", on_line=None)
    assert isinstance(results, list)
    assert any(r["tool"] == "hashid" for r in results)
