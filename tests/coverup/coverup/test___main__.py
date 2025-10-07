# Generated tests for coverup.__main__.py

import sys
import types
from pathlib import Path
import importlib
import pytest


def _ensure_dummy_deps(monkeypatch):
    # Create dummy coverup.llm module
    mod_llm = types.ModuleType("coverup.llm")

    class DummyLLM:
        def __init__(self, model):
            self.model = model

    mod_llm.LLMCaller = object
    mod_llm.GptCaller = DummyLLM
    mod_llm.GeminiCaller = DummyLLM
    monkeypatch.setitem(sys.modules, "coverup.llm", mod_llm)

    # Create dummy coverup.utils module
    mod_utils = types.ModuleType("coverup.utils")

    def test_file_to_src_file(test_file, coverup_tests_dir):
        return Path("src/dummy.py")

    mod_utils.test_file_to_src_file = test_file_to_src_file
    monkeypatch.setitem(sys.modules, "coverup.utils", mod_utils)

    # Create dummy coverup.test_runner module
    mod_runner = types.ModuleType("coverup.test_runner")

    def run_tests(*args, **kwargs):
        class Cov:
            percent_covered = 100
            files = []
        class Rep:
            passed = True
            coverage_report = Cov()
            errors = {}
        return Rep()
    mod_runner.run_tests = run_tests
    monkeypatch.setitem(sys.modules, "coverup.test_runner", mod_runner)

    # Create dummy coverup.test_writer_agent module
    mod_writer = types.ModuleType("coverup.test_writer_agent")

    def generate_tests(**kwargs):
        return None

    def build_prompt(*args, **kwargs):
        return ""
    mod_writer.generate_tests = generate_tests
    mod_writer.build_prompt = build_prompt
    monkeypatch.setitem(sys.modules, "coverup.test_writer_agent", mod_writer)


def _get_main_module(monkeypatch):
    _ensure_dummy_deps(monkeypatch)
    return importlib.reload(importlib.import_module("coverup.__main__"))


def test_choose_llm_branches(monkeypatch):
    m = _get_main_module(monkeypatch)
    # Ensure our dummy classes are used
    class DummyLLM:
        def __init__(self, model):
            self.model = model
    monkeypatch.setattr(m, "GptCaller", DummyLLM)
    monkeypatch.setattr(m, "GeminiCaller", DummyLLM)
    assert m.choose_llm("gpt-4").model == "gpt-4"
    assert m.choose_llm("gemini-pro").model == "gemini-pro"
    with pytest.raises(ValueError):
        m.choose_llm("unknown-model")


def test_parse_args_defaults(monkeypatch, tmp_path):
    m = _get_main_module(monkeypatch)
    ns = m.parse_args([str(tmp_path), "run_tests.sh"])
    assert ns.target == str(tmp_path)
    assert ns.run_tests_script == "run_tests.sh"
    assert ns.max_iterations == 10
    assert ns.llm == "gpt-5"


def test_main_reaches_target_breaks(monkeypatch, tmp_path):
    m = _get_main_module(monkeypatch)

    # Stub choose_llm
    class DummyLLM:
        def __init__(self, model):
            self.model = model
    monkeypatch.setattr(m, "choose_llm", lambda name: DummyLLM(name))

    # Stub run_tests to report high coverage and passed=True
    class DummyCov:
        def __init__(self):
            self.percent_covered = 90
            self.files = []

    class DummyReport:
        def __init__(self):
            self.passed = True
            self.coverage_report = DummyCov()
            self.errors = {}

    monkeypatch.setattr(m.test_runner, "run_tests", lambda *args, **kwargs: DummyReport())

    # Track if generate_tests is called (should not be)
    called = {"flag": False}
    monkeypatch.setattr(m, "generate_tests", lambda **kwargs: called.update(flag=True))

    ret = m.main([str(tmp_path), "run_tests.sh", "--target_coverage", "80", "--max_iterations", "3"])
    assert ret == 0
    assert called["flag"] is False


def test_main_failing_tests_in_coverup_dir(monkeypatch, tmp_path):
    m = _get_main_module(monkeypatch)

    # Stub choose_llm
    monkeypatch.setattr(m, "choose_llm", lambda name: object())

    # Prepare a failing report with error in coverup tests dir
    coverup_test_file = Path("tests/coverup/test_broken.py")

    class DummyCov:
        def __init__(self):
            self.percent_covered = 50
            self.files = []

    class DummyReport:
        def __init__(self):
            self.passed = False
            self.coverage_report = DummyCov()
            self.errors = {coverup_test_file: [1, 2]}

    monkeypatch.setattr(m.test_runner, "run_tests", lambda *args, **kwargs: DummyReport())

    # Stub utils.test_file_to_src_file
    monkeypatch.setattr(m.utils, "test_file_to_src_file", lambda test_file, root: Path("src/from_test.py"))

    # Track generate_tests called
    called = {"flag": False, "src": None}
    def fake_generate_tests(**kwargs):
        called["flag"] = True
        called["src"] = kwargs.get("rel_src_file")
    monkeypatch.setattr(m, "generate_tests", fake_generate_tests)

    ret = m.main([str(tmp_path), "run_tests.sh", "--max_iterations", "1"])
    assert ret == 0
    assert called["flag"] is True
    assert called["src"] == Path("src/from_test.py")


def test_main_increase_coverage_branch(monkeypatch, tmp_path):
    m = _get_main_module(monkeypatch)

    # Stub choose_llm
    monkeypatch.setattr(m, "choose_llm", lambda name: object())

    class FileCov:
        def __init__(self, file, percent):
            self.file = file
            self.percent_covered = percent

    class DummyCov:
        def __init__(self):
            self.percent_covered = 40  # below target
            self.files = [FileCov("a.py", 70), FileCov("b.py", 10)]

    class DummyReport:
        def __init__(self):
            self.passed = True
            self.coverage_report = DummyCov()
            self.errors = {}

    monkeypatch.setattr(m.test_runner, "run_tests", lambda *args, **kwargs: DummyReport())

    called = {"src": None, "file_cov": None}
    def fake_generate_tests(**kwargs):
        called["src"] = kwargs.get("rel_src_file")
        called["file_cov"] = kwargs.get("file_coverage")
    monkeypatch.setattr(m, "generate_tests", fake_generate_tests)

    ret = m.main([str(tmp_path), "run_tests.sh", "--max_iterations", "1", "--target_coverage", "80"])
    assert ret == 0
    assert called["src"] == Path("b.py")
    assert called["file_cov"].percent_covered == 10