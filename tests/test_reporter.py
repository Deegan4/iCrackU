import pytest
from core.reporter import generate_markdown, generate_html

SAMPLE_DATA = {
    "timestamp": "2026-04-21_063340",
    "type": "email",
    "query": "foo@bar.com",
    "tools": [
        {
            "name": "holehe",
            "returncode": 0,
            "output": "twitter: found\nfacebook: not found",
        },
        {"name": "ghunt", "returncode": -1, "output": "ghunt not found — skipping"},
    ],
}

SAMPLE_PROFILE = {
    "timestamp": "2026-04-21_070000",
    "type": "profile",
    "targets": [
        {
            "identifier": "foo@bar.com",
            "lookup_type": "email",
            "tools": [{"name": "holehe", "returncode": 0, "output": "twitter: found"}],
        },
        {
            "identifier": "foo@bar.com",
            "lookup_type": "breach",
            "tools": [
                {"name": "hibp", "returncode": 0, "output": "Found in 2 breach(es)"}
            ],
        },
    ],
}


def test_generate_markdown_contains_query():
    md = generate_markdown(SAMPLE_DATA)
    assert "foo@bar.com" in md


def test_generate_markdown_contains_summary_table():
    md = generate_markdown(SAMPLE_DATA)
    assert "| Tool |" in md


def test_generate_markdown_contains_tool_section():
    md = generate_markdown(SAMPLE_DATA)
    assert "## holehe" in md


def test_generate_markdown_contains_output():
    md = generate_markdown(SAMPLE_DATA)
    assert "twitter: found" in md


def test_generate_markdown_handles_profile():
    md = generate_markdown(SAMPLE_PROFILE)
    assert "foo@bar.com" in md
    assert "holehe" in md
    assert "hibp" in md


def test_generate_html_contains_query():
    html = generate_html(SAMPLE_DATA)
    assert "foo@bar.com" in html


def test_generate_html_contains_tool_name():
    html = generate_html(SAMPLE_DATA)
    assert "holehe" in html


def test_generate_html_is_valid_structure():
    html = generate_html(SAMPLE_DATA)
    assert "<html" in html
    assert "<body" in html
    assert "<details" in html


def test_generate_html_handles_profile():
    html = generate_html(SAMPLE_PROFILE)
    assert "hibp" in html
    assert "holehe" in html


def test_generate_html_dark_theme():
    html = generate_html(SAMPLE_DATA)
    assert "0d0d0d" in html
