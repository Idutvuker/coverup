import subprocess
import logging

from pathlib import Path

from .test_report import parse_test_report

logger = logging.getLogger(__name__)


def init_test_dir(test_dir: Path) -> None:
    test_dir.mkdir(parents=True, exist_ok=True)
    (test_dir / "__init__.py").touch(exist_ok=True)


def run_tests(project_root: Path, root_test_dir: Path, rel_run_tests_script: Path, rel_coverage_report_file: Path, rel_test_report_file: Path) -> None:
    init_test_dir(project_root / root_test_dir)

    result = subprocess.run(
        [f"./{rel_run_tests_script}"], capture_output=True, text=True, cwd=project_root)

    logger.debug(f"Test run exit code: {result.returncode}")
    logger.debug(f"Test stdout: {result.stdout}")
    logger.debug(f"Test stderr: {result.stderr}")

    test_report = parse_test_report(
        project_root / rel_test_report_file, project_root / rel_coverage_report_file)

    return test_report
