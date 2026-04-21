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
