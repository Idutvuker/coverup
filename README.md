
# coverup — automated test-generator helper

Small helper tool to generate test coverage for project. The tool runs iteratively: run the project's tests to produce coverage, ask the model to add focused tests for missing statements, run the tests again, and repeat until a target coverage is reached.

### Running on the sample project

1. Clone repo

```bash
git clone --recurse-submodules https://github.com/Idutvuker/coverup.git coverup
cd coverup
```

2. Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

3. Configure your LLM API key  
Set `OPENAI_API_KEY` or `GOOGLE_API_KEY`. The tool uses `gpt-5` model by default, you can change it via CLI argument (see `python3 -m coverup -h`).
```bash
export OPENAI_API_KEY=<your API key>
```

4. Run the tool (example):

```bash
# run coverup against a sample project directory
python3 -m coverup samples/myproj run_tests.sh
```

The tests will be generated in `samples/myproj/tests/coverup`

### Other sample - `things-cli` repo

```bash
cp run_tests_things_cli.sh samples/things-cli/
python3 -m coverup samples/things-cli run_tests.sh
```


### Running on your own project

You should provide a test runner script, that runs whole project test suite and produces JSON pytest report and JSON coverage report. You can use `run_tests.sh` as an example (in most cases you can just copy it to your project with minor changes).

Note: add `pytest-json-report` and `pytest-cov` to your virtual environment to generate reports.
