import jinja2
import logging
import time

from typing import List, Optional
from pathlib import Path

from coverup import utils
from .test_report import TestReport, FileCoverage
from .llm.LLMCaller import LLMCaller


logger = logging.getLogger(__name__)


def build_prompt(rel_src_file: Path, rel_test_file: Path, src_file: Path, test_file: Path, file_coverage: FileCoverage, test_report: TestReport) -> str:
    src_text = ""
    if src_file.exists():
        src_text = src_file.read_text(encoding="utf-8")
    enumerated_lines = utils.enumerate_lines(src_text)
    enumerated_src = '\n'.join(enumerated_lines)

    existing_tests = None
    if test_file.exists():
        existing_tests = test_file.read_text(encoding="utf-8")

    template_path = Path("coverup/prompts/create_tests.md.j2")
    template_text = template_path.read_text(encoding="utf-8")
    template = jinja2.Template(template_text)

    missing_lines = None
    if file_coverage:
        missing_lines = '\n'.join(
            enumerated_lines[i - 1] for i in file_coverage.missing_lines)

    failed_tests = test_report.getFailedTests()
    previous_failed_tests = [test.name for test in failed_tests if test.name.startswith(
        str(rel_test_file))] if failed_tests else None
    previous_errors = [
        test.error for test in failed_tests if test.error] if failed_tests else None

    context = {
        "source_filepath": rel_src_file,
        "enumerated_source": enumerated_src,
        "existing_tests": existing_tests,
        "missing_lines": missing_lines,
        "previous_failed_tests": previous_failed_tests,
        "previous_errors": previous_errors,
    }

    return template.render(**context)


def generate_tests(project_root: Path, rel_src_file: Path, file_coverage: Optional[FileCoverage], test_report: TestReport, llm_caller: LLMCaller) -> Path:
    test_dir = Path("tests/coverup")

    rel_test_file = utils.create_test_file(
        rel_src_file, test_dir, project_root)
    test_file = project_root / rel_test_file

    prompt = build_prompt(
        rel_src_file=rel_src_file,
        rel_test_file=rel_test_file,
        src_file=project_root / rel_src_file,
        test_file=test_file,
        file_coverage=file_coverage,
        test_report=test_report
    )

    logger.info("Rendered prompt for %s:\n%s", rel_src_file, prompt)

    print(f"Prompting LLM ({llm_caller.model})...")

    start = time.monotonic()
    response = llm_caller.call(prompt)
    elapsed = time.monotonic() - start

    test_file.write_text(response, encoding="utf-8")

    logger.info("LLM response \n%s", response)
    logger.info("Wrote generated tests to %s", test_file)
    logger.info("LLM response took: %.1f seconds", elapsed)

    print(f"LLM response took {elapsed:.1f} seconds")

    return test_file
