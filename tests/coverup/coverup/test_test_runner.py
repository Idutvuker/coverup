# Generated tests for coverup.test_runner

import sys
import types
import importlib
from pathlib import Path


def _ensure_test_report_module():
    try:
        importlib.import_module("coverup.test_report")
    except Exception:
        m = types.ModuleType("coverup.test_report")
        def parse_test_report(*args, **kwargs):
            return {"dummy": True}
        m.parse_test_report = parse_test_report
        sys.modules["coverup.test_report"] = m


def test_init_test_dir_creates_dir_and_init_file(tmp_path):
    _ensure_test_report_module()
    test_runner = importlib.import_module("coverup.test_runner")

    target_dir = tmp_path / "pkg" / "tests"
    test_runner.init_test_dir(target_dir)

    assert target_dir.is_dir()
    assert (target_dir / "__init__.py").exists()


def test_run_tests_uses_subprocess_and_returns_parse_result(tmp_path, monkeypatch):
    _ensure_test_report_module()
    test_runner = importlib.import_module("coverup.test_runner")

    project_root = tmp_path / "project"
    project_root.mkdir()

    root_test_dir = Path("testdir")
    rel_run_tests_script = Path("run.sh")
    rel_cov = Path("coverage.xml")
    rel_report = Path("report.json")

    subprocess_calls = []

    def fake_run(cmd, capture_output, text, cwd):
        subprocess_calls.append(
            {"cmd": cmd, "capture_output": capture_output, "text": text, "cwd": cwd}
        )
        return types.SimpleNamespace(returncode=0, stdout="ok", stderr="")

    monkeypatch.setattr(test_runner.subprocess, "run", fake_run)

    parse_calls = []

    def fake_parse(test_report_path, coverage_report_path):
        parse_calls.append((test_report_path, coverage_report_path))
        return {"parsed": True}

    monkeypatch.setattr(test_runner, "parse_test_report", fake_parse)

    result = test_runner.run_tests(
        project_root, root_test_dir, rel_run_tests_script, rel_cov, rel_report
    )

    # subprocess.run called with expected command and cwd
    assert subprocess_calls[0]["cmd"] == [f"./{rel_run_tests_script}"]
    assert subprocess_calls[0]["cwd"] == project_root
    assert subprocess_calls[0]["capture_output"] is True
    assert subprocess_calls[0]["text"] is True

    # parse_test_report called with full paths derived from project_root
    assert parse_calls[0][0] == project_root / rel_report
    assert parse_calls[0][1] == project_root / rel_cov

    # run_tests returns the value from parse_test_report
    assert result == {"parsed": True}

    # init_test_dir created the test directory and __init__.py
    created_test_dir = project_root / root_test_dir
    assert created_test_dir.is_dir()
    assert (created_test_dir / "__init__.py").exists()