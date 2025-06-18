"""Enables running the dynamic tester as a package.

This file allows the package to be executed directly from the command line
using the ``-m`` flag with Python (e.g., ``python -m code_tester``). It
serves as the primary entry point that finds and invokes the command-line
interface logic defined in the `cli` module.

Example:
    You can run the tester package like this from the project root:

    .. code-block:: bash

        python -m code_tester path/to/solution.py path/to/test_case.json
"""

from .cli import run_from_cli

if __name__ == "__main__":
    run_from_cli()
