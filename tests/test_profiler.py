import pytest
from core.profiler import classify


def test_classify_email():
    assert classify("foo@bar.com") == ["email", "breach"]


def test_classify_ip():
    assert classify("8.8.8.8") == ["ip"]


def test_classify_domain():
    assert classify("example.com") == ["domain"]


def test_classify_phone():
    assert classify("+15551234567") == ["phone"]


def test_classify_username():
    assert classify("johndoe") == ["username", "name"]


def test_classify_ip_edge_cases():
    assert classify("192.168.1.1") == ["ip"]
    assert classify("256.256.256.256") == ["username", "name"]  # invalid IP → username


def test_classify_domain_with_subdomain():
    assert classify("sub.example.com") == ["domain"]


def test_classify_email_also_runs_breach():
    result = classify("admin@example.com")
    assert "email" in result
    assert "breach" in result


from unittest.mock import patch, MagicMock
import json
import os


def fake_lookup(query, on_line=None, on_tool_start=None):
    return [{"tool": "faketool", "query": query, "returncode": 0, "output": "found"}]


def test_run_profile_returns_combined_results():
    fake_mod = MagicMock()
    fake_mod.lookup = fake_lookup
    with patch.dict(
        "core.profiler.MODULE_MAP",
        {
            "email": fake_mod,
            "breach": fake_mod,
        },
        clear=True,
    ):
        from core.profiler import run_profile

        results = run_profile(
            {"email": "foo@bar.com", "breach": "foo@bar.com"},
            on_line=None,
            on_tool_start=None,
        )
    assert isinstance(results, list)
    assert len(results) == 2
    assert all("lookup_type" in r for r in results)
    assert all("identifier" in r for r in results)
    assert all("tools" in r for r in results)


def test_save_profile_writes_json(tmp_path):
    from core.profiler import save_profile

    targets = [
        {
            "identifier": "foo@bar.com",
            "lookup_type": "email",
            "tools": [{"name": "holehe", "returncode": 0, "output": "found"}],
        },
    ]
    json_path = save_profile(targets, results_dir=str(tmp_path))
    assert os.path.exists(json_path)
    data = json.loads(open(json_path).read())
    assert data["type"] == "profile"
    assert len(data["targets"]) == 1
    assert data["targets"][0]["lookup_type"] == "email"
