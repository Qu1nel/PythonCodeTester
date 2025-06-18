# ==============================================================================
#  Makefile for Python Projects
#  - Author: Qu1nel
#  - Version: 2.0
# ==============================================================================


# --- Color Codes for Output (work in Linux, macOS, Git Bash, WSL) ---
RESET   = \033[0m
BOLD    = \033[1m
RED     = \033[31m
GREEN   = \033[32m
YELLOW  = \033[33m
CYAN    = \033[36m

# --- Variables ---
# Use uv to run commands inside the virtual environment
PYTHON_RUNNER   := uv run python
RUFF_RUNNER     := $(PYTHON_RUNNER) -m ruff
TEST_RUNNER     := $(PYTHON_RUNNER) -m unittest
COVERAGE_RUNNER := $(PYTHON_RUNNER) -m coverage
BUILD_RUNNER    := $(PYTHON_RUNNER) -m build
TWINE_RUNNER    := $(PYTHON_RUNNER) -m twine

.DEFAULT_GOAL := help
.SILENT:

# ==============================================================================
#  DEVELOPER COMMANDS
# ==============================================================================

.PHONY: setup
setup: ## Install all dependencies for development. Ex: make setup
	@echo "$(CYAN)› Setting up virtual environment and installing dependencies...$(RESET)"
	@uv venv -p 3.11 --seed
	@uv pip install -e ".[dev,docs]"
	@echo "$(GREEN)✅ Setup complete. Activate with 'source .venv/bin/activate' or '.venv\\Scripts\\activate'.$(RESET)"

.PHONY: sync
sync: ## Synchronize virtual environment with pyproject.toml. Ex: make sync
	@echo "$(CYAN)› Syncing dependencies...$(RESET)"
	@uv pip sync ./src/
	@echo "$(GREEN)✅ Dependencies are up to date.$(RESET)"

.PHONY: lint
lint: format check ## Run all formatters and linters. Ex: make lint
	@echo "$(GREEN)✅ All linting and formatting checks passed.$(RESET)"

.PHONY: format
format: ## Auto-format code with ruff. Ex: make format
	@echo "$(CYAN)› Formatting code with ruff...$(RESET)"
	@$(RUFF_RUNNER) format src/ tests/

.PHONY: check
check: ## Check for linting errors with ruff. Ex: make check
	@echo "$(CYAN)› Checking for linting errors with ruff...$(RESET)"
	@$(RUFF_RUNNER) check src/ tests/ --fix


# ==============================================================================
#  TESTING
# ==============================================================================

.PHONY: test
test: ## Run all unit tests. Ex: make test
	@echo "$(CYAN)› Running unit tests...$(RESET)"
	@$(TEST_RUNNER) discover tests

.PHONY: coverage
coverage: ## Run tests and show coverage report in the console. Ex: make coverage
	@echo "$(CYAN)› Running tests with coverage...$(RESET)"
	@$(COVERAGE_RUNNER) run -m unittest discover tests
	@echo "$(CYAN)› Coverage report:$(RESET)"
	@$(COVERAGE_RUNNER) report -m

.PHONY: coverage-html
coverage-html: ## Run tests and generate an HTML coverage report. Ex: make coverage-html
	@echo "$(CYAN)› Running tests with coverage...$(RESET)"
	@$(COVERAGE_RUNNER) run -m unittest discover tests
	@echo "$(CYAN)› Generating HTML report...$(RESET)"
	@$(COVERAGE_RUNNER) html
	@echo "$(GREEN)✅ HTML report generated in 'htmlcov/'. Open 'htmlcov/index.html' in your browser.$(RESET)"


# ==============================================================================
#  BUILD & PUBLISH
# ==============================================================================

.PHONY: build
build: ## Build the package into wheel and sdist artifacts
	@echo "$(BLUE)› Building package...$(RESET)"
	@$(BUILD_RUNNER)
	@echo "$(GREEN)✅ Package built in 'dist/'.$(RESET)"

.PHONY: publish-test
publish-test: build ## Publish package to the TestPyPI repository
	@echo "$(YELLOW)Uploading package to TestPyPI...$(RESET)"
	@$(TWINE_RUNNER) upload --repository testpypi dist/*

.PHONY: publish
publish: build ## Publish package to the official PyPI repository
	@echo "$(RED)$(BOLD)Uploading package to the REAL PyPI...$(RESET)"
	@$(TWINE_RUNNER) upload dist/*


# ==============================================================================
#  CLEANUP
# ==============================================================================

.PHONY: clean
clean: ## Remove cache files and build artifacts
	@echo "$(YELLOW)› Cleaning up...$(RESET)"
	@rm -rf .ruff_cache/ .pytest_cache/ .mypy_cache/ htmlcov/ .coverage
	@rm -rf dist/ build/ src/*.egg-info/
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@echo "$(GREEN)✅ Cleanup complete.$(RESET)"


# ==============================================================================
#  HELP
# ==============================================================================
.PHONY: help
help: ## Show this help message. Ex: make help
	@echo ""
	@echo "  $(BOLD)PythonCodeTester - Makefile Help$(RESET)"
	@echo "  -------------------------------------"
	@echo "  Usage: $(GREEN)make$(RESET) $(CYAN)<target>$(RESET)"
	@echo ""
	@echo "  $(YELLOW)Examples:$(RESET)"
	@echo "    $(GREEN)make setup$(RESET)          - First-time setup for the project."
	@echo "    $(GREEN)make lint$(RESET)           - Format and check the entire codebase."
	@echo "    $(GREEN)make test$(RESET)           - Run the test suite."
	@echo "    $(GREEN)make coverage-html$(RESET)  - Run tests and open the HTML coverage report."
	@echo ""
	@echo "  $(YELLOW)Available targets:$(RESET)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' Makefile | awk 'BEGIN {FS = ":.*?## "}; {printf "    $(GREEN)%-20s$(RESET) %s\n", $$1, $$2}'