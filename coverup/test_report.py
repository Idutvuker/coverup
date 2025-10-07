import json

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional
from collections import defaultdict


@dataclass
class FileCoverage:
    file: Path
    missing_lines: List[int]
    percent_covered: float = 0.0


@dataclass
class CoveregeReport:
    files: List[FileCoverage] = field(default_factory=list)
    percent_covered: float = 0.0


@dataclass
class SignleTestData:
    name: str
    test_file: Path
    passed: bool
    error: Optional[str] = None


@dataclass
class TestReport:
    passed: bool = True
    tests: List[SignleTestData] = field(default_factory=list)
    coverage_report: CoveregeReport = None

    errors: Dict[Path, List[str]] = field(
        default_factory=lambda: defaultdict(list))

    def getFailedTests(self) -> List[SignleTestData]:
        return [t for t in self.tests if not t.passed]


def parse_coverage_report(coverage_report_file: Path) -> CoveregeReport:
    data = json.loads(coverage_report_file.read_text())

    coverage = CoveregeReport()

    files = data.get("files", {})
    for file_path, file_info in files.items():
        missing_lines = file_info.get("missing_lines", [])
        percent_covered = file_info.get(
            "summary", {}).get("percent_covered", 0.0)
        fc = FileCoverage(file=Path(
            file_path), missing_lines=missing_lines, percent_covered=percent_covered)
        coverage.files.append(fc)

    percent_covered = data.get("totals", {}).get("percent_covered", 0.0)
    coverage.percent_covered = percent_covered

    return coverage


def parse_test_report(test_report_file: Path, coverage_report_file: Path) -> TestReport:
    test_report = TestReport()
    test_report.coverage_report = parse_coverage_report(coverage_report_file)

    data = json.loads(test_report_file.read_text())

    tests = data.get("tests", [])
    for test in tests:
        passed = (test['outcome'] == 'passed')
        stages = ['setup', 'call', 'teardown']
        name = test['nodeid']
        test_file = Path(name.split("::")[0])

        if not passed:
            test_report.passed = False

            stage_error_list = []
            for stage in stages:
                if stage in test and 'longrepr' in test[stage]:
                    error_msg = test[stage]['longrepr']
                    stage_error_list.append(error_msg)

            full_error = '\n'.join(stage_error_list)
            test_report.errors[test_file].append(full_error)

            test_report.tests.append(SignleTestData(
                name=name, test_file=test_file, passed=passed, error=full_error))

    # If collector failed, the test setup is probably incorrect
    for col in data.get("collectors", []):
        if col.get("outcome") != "passed":
            test_report.passed = False

            test_file = Path(col["nodeid"].split("::")[0])
            error = col.get("longrepr", "")
            test_report.errors[test_file].append(error)

    return test_report
