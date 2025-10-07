
from pathlib import Path
from typing import Optional, List
import argparse
import logging

from coverup import utils
from coverup import test_runner
from coverup.test_writer_agent import build_prompt, generate_tests
from coverup.llm import GeminiCaller, GptCaller, LLMCaller


logging.basicConfig(
    filename="coverup.log",
    filemode="w",
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(name)s - %(message)s",
)


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Find functions with missing coverage lines")
    parser.add_argument(
        "target",
        help="Path to the target project directory",
    )
    parser.add_argument(
        "run_tests_script",
        help="Path inside the project to script for running all tests. "
        "It should generate coverage.json and test_report.json files. "
        "See README.md for details.",
    )
    parser.add_argument(
        "--max_iterations",
        dest="max_iterations",
        type=int,
        default=10,
        help="Maximum number of LLM iterations to run",
    )
    parser.add_argument(
        "--target_coverage",
        "-t",
        dest="target_coverage",
        type=int,
        default=80,
        help="Target code coverage percentage to reach",
    )
    parser.add_argument(
        "--coverage_report_file",
        default="coverage.json",
        help="Path to the coverage report file inside the project",
    )
    parser.add_argument(
        "--test_report_file",
        default="test_report.json",
        help="Path to the test report file in the project",
    )
    parser.add_argument(
        "--test_dir",
        default="tests/",
        help="Tests directory in the project",
    )
    parser.add_argument(
        "--llm",
        default="gpt-5",
        help="Tests directory in the project",
    )
    return parser.parse_args(argv)


def choose_llm(llm_name: str) -> LLMCaller:
    if llm_name.startswith("gpt"):
        return GptCaller(model=llm_name)
    elif llm_name.startswith("gemini"):
        return GeminiCaller(model=llm_name)
    else:
        raise ValueError(f"Unknown LLM model: {llm_name}")


def main(argv=None) -> int:
    args = parse_args(argv)
    project_root = Path(args.target)

    rel_coverage_report_file = Path(args.coverage_report_file)
    rel_test_report_file = Path(args.test_report_file)
    rel_run_script_file = Path(args.run_tests_script)
    root_test_dir = Path(args.test_dir)
    coverup_tests_dir = root_test_dir / "coverup"

    llm_caller = choose_llm(args.llm)

    for iteration in range(args.max_iterations):
        print(f"=== Iteration {iteration + 1} (max {args.max_iterations}) ===")

        test_report = test_runner.run_tests(
            project_root, root_test_dir, rel_run_script_file, rel_coverage_report_file, rel_test_report_file)
        print(
            f"Current all code coverage: {round(test_report.coverage_report.percent_covered)}%")

        if test_report.passed and test_report.coverage_report.percent_covered >= args.target_coverage:
            print(
                f"Target coverage {args.target_coverage}% reached: {round(test_report.coverage_report.percent_covered)}%")
            break

        if not test_report.passed:
            # Some tests are failing, prioritize fixing them first

            print("Failing generated tests:")
            for test_file, errors in test_report.errors.items():
                if test_file.is_relative_to(coverup_tests_dir):
                    print(f"- {test_file}: {len(errors)} errors")
                    target_test_file = test_file
                    target_errors = len(errors)

            if not target_test_file:
                print(
                    "Tests are failing, but none in coverup tests directory. Please fix them manually.")
                return 1

            print(f"Fixing tests in {target_test_file}")

            target_src_file = utils.test_file_to_src_file(
                target_test_file, coverup_tests_dir)
            target_file_coverage = None
            reason = f"{target_errors} test errors"

        else:
            # All tests are passing, focus on increasing coverage
            # Find the file with the lowest coverage

            target_file_coverage = sorted(
                test_report.coverage_report.files, key=lambda f: f.percent_covered)[0]
            target_src_file = Path(target_file_coverage.file)
            reason = f"{round(target_file_coverage.percent_covered)}% coverage"

        print(f"Generating tests for {target_src_file} ({reason})")

        # last_test_report = full_test_report

        generate_tests(
            project_root=project_root,
            rel_src_file=target_src_file,
            file_coverage=target_file_coverage,
            test_report=test_report,
            llm_caller=llm_caller)

        print("\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
