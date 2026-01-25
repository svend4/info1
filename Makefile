.PHONY: help install install-dev test test-coverage lint format clean docker-build docker-up docker-down benchmark docs

# Default target
.DEFAULT_GOAL := help

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[1;33m
NC := \033[0m # No Color

help: ## Show this help message
	@echo "$(BLUE)AI Generator Toolkit - Available Commands$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "$(GREEN)%-20s$(NC) %s\n", $$1, $$2}'

install: ## Install the package
	@echo "$(BLUE)Installing AI Generator Toolkit...$(NC)"
	pip install -e .
	@echo "$(GREEN)✅ Installation complete$(NC)"

install-dev: ## Install development dependencies
	@echo "$(BLUE)Installing development dependencies...$(NC)"
	pip install -r requirements.txt
	pip install -r requirements-dev.txt
	pip install -e .
	@echo "$(GREEN)✅ Development setup complete$(NC)"

test: ## Run tests
	@echo "$(BLUE)Running tests...$(NC)"
	pytest -v

test-coverage: ## Run tests with coverage
	@echo "$(BLUE)Running tests with coverage...$(NC)"
	pytest -v --cov=tools/ai_generator --cov-report=html --cov-report=term-missing
	@echo "$(GREEN)✅ Coverage report generated at htmlcov/index.html$(NC)"

test-integration: ## Run integration tests only
	@echo "$(BLUE)Running integration tests...$(NC)"
	pytest -v -m integration

test-fast: ## Run fast tests (skip slow ones)
	@echo "$(BLUE)Running fast tests...$(NC)"
	pytest -v -m "not slow" -n auto

test-parallel: ## Run tests in parallel
	@echo "$(BLUE)Running tests in parallel...$(NC)"
	pytest -v -n auto

lint: ## Run linters
	@echo "$(BLUE)Running linters...$(NC)"
	@echo "$(YELLOW)Checking with black...$(NC)"
	black --check tools/ai_generator/
	@echo "$(YELLOW)Checking with isort...$(NC)"
	isort --check-only tools/ai_generator/
	@echo "$(YELLOW)Checking with flake8...$(NC)"
	flake8 tools/ai_generator/ --max-line-length=120
	@echo "$(YELLOW)Checking with bandit...$(NC)"
	bandit -r tools/ai_generator/
	@echo "$(GREEN)✅ All linting checks passed$(NC)"

format: ## Format code with black and isort
	@echo "$(BLUE)Formatting code...$(NC)"
	black tools/ai_generator/
	isort tools/ai_generator/
	@echo "$(GREEN)✅ Code formatted$(NC)"

clean: ## Clean up generated files
	@echo "$(BLUE)Cleaning up...$(NC)"
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf build/ dist/ .pytest_cache/ .coverage htmlcov/ reports/
	@echo "$(GREEN)✅ Cleanup complete$(NC)"

benchmark: ## Run performance benchmarks
	@echo "$(BLUE)Running benchmarks...$(NC)"
	python benchmarks/run_all_benchmarks.py
	@echo "$(GREEN)✅ Benchmarks complete - check reports/benchmarks/$(NC)"

docker-build: ## Build Docker images
	@echo "$(BLUE)Building Docker images...$(NC)"
	docker-compose build
	@echo "$(GREEN)✅ Docker images built$(NC)"

docker-up: ## Start Docker services
	@echo "$(BLUE)Starting Docker services...$(NC)"
	docker-compose up -d
	@echo "$(GREEN)✅ Services started$(NC)"

docker-down: ## Stop Docker services
	@echo "$(BLUE)Stopping Docker services...$(NC)"
	docker-compose down
	@echo "$(GREEN)✅ Services stopped$(NC)"

docker-logs: ## View Docker logs
	docker-compose logs -f

docker-test: ## Run tests in Docker
	@echo "$(BLUE)Running tests in Docker...$(NC)"
	docker-compose run --rm test
	@echo "$(GREEN)✅ Tests complete$(NC)"

docker-benchmark: ## Run benchmarks in Docker
	@echo "$(BLUE)Running benchmarks in Docker...$(NC)"
	docker-compose run --rm benchmark
	@echo "$(GREEN)✅ Benchmarks complete$(NC)"

security-check: ## Run security checks
	@echo "$(BLUE)Running security checks...$(NC)"
	safety check --file requirements.txt
	bandit -r tools/ai_generator/ -f json -o reports/security-report.json
	@echo "$(GREEN)✅ Security check complete$(NC)"

type-check: ## Run type checking with mypy
	@echo "$(BLUE)Running type checks...$(NC)"
	mypy tools/ai_generator/ --ignore-missing-imports
	@echo "$(GREEN)✅ Type checking complete$(NC)"

all-checks: format lint type-check test-coverage security-check ## Run all checks
	@echo "$(GREEN)✅ All checks passed!$(NC)"

setup-hooks: ## Setup git hooks
	@echo "$(BLUE)Setting up git hooks...$(NC)"
	chmod +x run_tests.sh benchmarks/run_benchmarks.sh
	@echo "$(GREEN)✅ Git hooks setup complete$(NC)"

examples: ## Run example scripts
	@echo "$(BLUE)Running examples...$(NC)"
	@echo "Security examples:"
	python tools/ai_generator/examples/security/01_sso_integration.py
	@echo ""
	@echo "MLOps examples:"
	python tools/ai_generator/examples/mlops/01_model_registry.py
	@echo "$(GREEN)✅ Examples complete$(NC)"

stats: ## Show project statistics
	@echo "$(BLUE)Project Statistics:$(NC)"
	@echo ""
	@echo "$(YELLOW)Lines of Code:$(NC)"
	@find tools/ai_generator -name "*.py" -not -path "*/tests/*" | xargs wc -l | tail -1
	@echo ""
	@echo "$(YELLOW)Module Files:$(NC)"
	@find tools/ai_generator -name "*.py" -not -path "*/tests/*" -not -name "__init__.py" | wc -l
	@echo ""
	@echo "$(YELLOW)Test Files:$(NC)"
	@find tests -name "*.py" | wc -l
	@echo ""
	@echo "$(YELLOW)Documentation Files:$(NC)"
	@find . -name "*.md" | wc -l

watch-tests: ## Watch and run tests on file changes
	@echo "$(BLUE)Watching for changes...$(NC)"
	pytest-watch -- -v

ci: install-dev lint test-coverage ## Run CI pipeline locally
	@echo "$(GREEN)✅ CI pipeline complete$(NC)"

release: all-checks ## Prepare for release
	@echo "$(BLUE)Preparing release...$(NC)"
	@echo "$(GREEN)✅ Ready for release$(NC)"
