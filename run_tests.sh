#!/bin/bash

set -euo pipefail
# set -x

# Replace with your source directory if copied elsewhere
SRC_DIR="coverup"

python3 -m venv .venv
source .venv/bin/activate

pip install --upgrade pip
pip install pytest pytest-cov pytest-json-report
pip install -r requirements.txt

pytest --cov=$SRC_DIR --cov-report=json --json-report --json-report-file=test_report.json --color=no tests/
