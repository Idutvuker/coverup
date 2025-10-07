#!/bin/bash

set -euo pipefail
# set -x

python3 -m venv .venv
source .venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt

pytest --cov=src --cov-report=json --json-report --json-report-file=test_report.json --color=no tests/
