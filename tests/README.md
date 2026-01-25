# AI Generator Toolkit - Test Suite

Comprehensive test suite for all 38 modules across 8 categories.

## Test Structure

```
tests/
├── conftest.py                              # Shared fixtures
├── integration/                             # Integration tests
│   ├── test_security_integration.py         # Security modules (6 modules)
│   ├── test_mlops_integration.py            # MLOps modules (4 modules)
│   └── test_remaining_modules_integration.py # Other modules (28 modules)
└── README.md                                # This file
```

## Running Tests

### Quick Start

```bash
# Install dependencies
pip install -r requirements-dev.txt

# Run all tests
./run_tests.sh all

# Run specific category
./run_tests.sh security
./run_tests.sh mlops
./run_tests.sh codegen
```

### Test Categories

**By Module Type:**
```bash
./run_tests.sh security      # Security & Compliance (6 modules)
./run_tests.sh mlops          # MLOps & Model Management (4 modules)
./run_tests.sh codegen        # Code Generation (3 modules)
./run_tests.sh distributed    # Distributed Systems (5 modules)
./run_tests.sh mobile         # Mobile Development (5 modules)
./run_tests.sh ai_pair        # AI Pair Programming (4 modules)
./run_tests.sh testing        # Testing & Quality (4 modules)
./run_tests.sh devops         # DevOps Excellence (4 modules)
```

**By Test Type:**
```bash
./run_tests.sh integration    # Integration tests only
./run_tests.sh unit           # Unit tests only
./run_tests.sh fast           # Exclude slow tests
```

**Parallel Execution:**
```bash
./run_tests.sh all true       # Run all tests in parallel
./run_tests.sh integration true
```

### Using pytest directly

```bash
# Run all tests
pytest

# Run specific markers
pytest -m integration
pytest -m "security and integration"
pytest -m "not slow"

# Run with coverage
pytest --cov=tools/ai_generator --cov-report=html

# Parallel execution
pytest -n auto

# Verbose output
pytest -v -s
```

## Test Coverage

### Current Coverage

The test suite covers:
- ✅ **38 modules** across 8 categories
- ✅ **Integration tests** for all major workflows
- ✅ **End-to-end scenarios** for each module
- ✅ **Edge cases** and error handling

### Coverage Reports

After running tests, view coverage reports:

```bash
# Open HTML coverage report
open reports/coverage/all/index.html

# View terminal summary
pytest --cov=tools/ai_generator --cov-report=term-missing
```

### Target Coverage

- **Overall:** > 80%
- **Critical modules:** > 90%
- **Integration workflows:** 100%

## Test Markers

All tests are marked with pytest markers for selective execution:

### Category Markers
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.slow` - Slow-running tests

### Module Markers
- `@pytest.mark.security` - Security modules
- `@pytest.mark.mlops` - MLOps modules
- `@pytest.mark.codegen` - Code generation
- `@pytest.mark.distributed` - Distributed systems
- `@pytest.mark.mobile` - Mobile development
- `@pytest.mark.ai_pair` - AI pair programming
- `@pytest.mark.testing` - Testing modules
- `@pytest.mark.devops` - DevOps modules

## Test Fixtures

### Available Fixtures (conftest.py)

```python
temp_dir              # Temporary directory for test outputs
test_output_dir       # Session-scoped output directory
sample_code           # Sample Python code for testing
sample_openapi_spec   # Sample OpenAPI specification
mock_ml_metrics       # Mock ML model metrics
mock_user_features    # Mock user features for testing
```

## Writing New Tests

### Integration Test Template

```python
import pytest
from pathlib import Path
from tools.ai_generator.your_module import YourClass

@pytest.mark.integration
@pytest.mark.your_category
class TestYourModuleIntegration:
    """Integration tests for Your Module"""

    def test_basic_functionality(self, temp_dir):
        """Test basic module functionality"""
        instance = YourClass()
        result = instance.do_something(temp_dir)

        assert result is not None
        assert len(result) > 0

    def test_error_handling(self):
        """Test error handling"""
        instance = YourClass()

        with pytest.raises(ValueError):
            instance.do_invalid_operation()
```

## CI/CD Integration

Tests run automatically on:
- ✅ Every push to main/develop branches
- ✅ All pull requests
- ✅ Nightly scheduled runs

See `.github/workflows/tests.yml` for CI configuration.

## Troubleshooting

### Common Issues

**Import errors:**
```bash
# Ensure package is installed in development mode
pip install -e .
```

**Missing dependencies:**
```bash
# Reinstall dev dependencies
pip install -r requirements-dev.txt
```

**Slow tests:**
```bash
# Skip slow tests
pytest -m "not slow"

# Run in parallel
pytest -n auto
```

**Coverage not generated:**
```bash
# Install coverage plugin
pip install pytest-cov

# Run with explicit coverage
pytest --cov=tools/ai_generator --cov-report=html
```

## Best Practices

### Writing Tests

1. **Use descriptive names:** `test_security_sso_okta_integration` > `test_1`
2. **Test one thing:** Each test should verify a single behavior
3. **Use fixtures:** Reuse setup code via fixtures
4. **Mark appropriately:** Add relevant pytest markers
5. **Clean up:** Use temp directories, clean up resources

### Test Organization

1. **Group by category:** Keep related tests together
2. **Integration vs Unit:** Separate integration and unit tests
3. **Mark slow tests:** Use `@pytest.mark.slow` for tests > 1s
4. **Document complex tests:** Add docstrings explaining what's tested

### Performance

1. **Use fixtures efficiently:** Scope fixtures appropriately (function/class/module/session)
2. **Mock external services:** Don't make real API calls in tests
3. **Parallel execution:** Use `pytest -n auto` for faster runs
4. **Skip slow tests during development:** `pytest -m "not slow"`

## Performance Metrics

Expected test execution times:

```
Fast tests only:     < 30 seconds
Integration tests:   1-3 minutes
All tests:           3-5 minutes
All tests parallel:  1-2 minutes
```

## Continuous Improvement

### Adding Tests

When adding new modules:
1. Create integration tests in `tests/integration/`
2. Add appropriate pytest markers
3. Update this README
4. Ensure > 80% coverage

### Maintaining Tests

- Review failing tests immediately
- Update tests when modules change
- Keep fixtures DRY (Don't Repeat Yourself)
- Regularly check coverage reports

## Resources

- [pytest documentation](https://docs.pytest.org/)
- [pytest-cov plugin](https://pytest-cov.readthedocs.io/)
- [pytest markers](https://docs.pytest.org/en/stable/example/markers.html)
- [GitHub Actions pytest](https://docs.github.com/en/actions/automating-builds-and-tests/building-and-testing-python)

---

**Test Suite Version:** 1.0.0
**Last Updated:** 2026-01-25
**Coverage Target:** 80%+
