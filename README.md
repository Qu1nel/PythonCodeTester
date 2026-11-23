# PythonCodeTester

Run JSON test scenarios against Python code. A scenario describes the actions to perform and the results to expect, such as a return value, an exception, or printed output. Checks can call functions and methods, save objects for later steps, and inspect their attributes.

For coursework, [PythonCodeValidator](https://github.com/Qu1nel/PythonCodeValidator) checks source structure. PythonCodeTester runs the code and checks its behavior.

## Quick start

Use Python 3.11 or later. Clone the repository and create a virtual environment.

```bash
git clone https://github.com/Qu1nel/PythonCodeTester.git
cd PythonCodeTester
python -m venv .venv
```

Activate it with `source .venv/bin/activate` on macOS or Linux, or `.\.venv\Scripts\Activate.ps1` in PowerShell. Install from the checkout and run the calculator scenario from the repository root.

```bash
python -m pip install .
python -m code_tester run tests/fixtures/solutions/py_general/calculator.py tests/fixtures/test_cases/py_general/calculator_test.json
```

You can also use `code-tester run` with the same two paths. The first path is the [Python solution](tests/fixtures/solutions/py_general/calculator.py) and the second is the [JSON scenario](tests/fixtures/test_cases/py_general/calculator_test.json).

The scenario creates a `Calculator`, reuses the saved instance to check that `add(5, 3)` returns `8`, and checks that `divide(10, 0)` raises `ValueError`. A successful run prints `All tests passed!` and exits with status `0`.

Run only trusted solutions locally. The tester imports and executes the submitted Python file in its own process. Isolate execution before accepting untrusted submissions.

## Arcade direction

The first development target is checking the behavior of small [Arcade](https://api.arcade.academy/) games. A first scenario could send a left-arrow input and verify that a paddle moves left. The current Arcade examples are fixtures for future integration work. Automated game input and screenshot comparison are pending.

## License

[MIT](LICENSE)
