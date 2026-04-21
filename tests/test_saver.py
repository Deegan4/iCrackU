import json
import os
import pytest
from core.saver import save_results

SAMPLE_RESULTS = [
    {"tool": "holehe", "query": "foo@bar.com", "returncode": 0, "output": "twitter: found"},
    {"tool": "ghunt", "query": "foo@bar.com", "returncode": 0, "output": "profile: public"},
]

def test_save_results_creates_txt_and_json(tmp_path):
    txt_path, json_path = save_results(
        lookup_type="email",
        query="foo@bar.com",
        tool_results=SAMPLE_RESULTS,
        results_dir=str(tmp_path),
    )
    assert os.path.exists(txt_path)
    assert os.path.exists(json_path)
    assert txt_path.endswith(".txt")
    assert json_path.endswith(".json")

def test_save_results_json_structure(tmp_path):
    _, json_path = save_results(
        lookup_type="email",
        query="foo@bar.com",
        tool_results=SAMPLE_RESULTS,
        results_dir=str(tmp_path),
    )
    with open(json_path) as f:
        data = json.load(f)
    assert data["type"] == "email"
    assert data["query"] == "foo@bar.com"
    assert "timestamp" in data
    assert len(data["tools"]) == 2
    assert data["tools"][0]["name"] == "holehe"

def test_save_results_txt_contains_output(tmp_path):
    txt_path, _ = save_results(
        lookup_type="email",
        query="foo@bar.com",
        tool_results=SAMPLE_RESULTS,
        results_dir=str(tmp_path),
    )
    content = open(txt_path).read()
    assert "twitter: found" in content
    assert "profile: public" in content

def test_save_results_creates_dir_if_missing(tmp_path):
    subdir = str(tmp_path / "deep" / "results")
    save_results("email", "foo@bar.com", SAMPLE_RESULTS, results_dir=subdir)
    assert os.path.isdir(subdir)
