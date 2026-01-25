# Contributing to AI Generator Toolkit

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Getting Started

### Prerequisites
- Python 3.8 or higher
- Git
- Docker (optional, for containerized development)

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/yourusername/info1.git
cd info1

# Install dependencies
make install-dev

# Or manually:
pip install -r requirements.txt
pip install -r requirements-dev.txt
pip install -e .
```

## Development Workflow

### 1. Create a Branch
```bash
git checkout -b feature/your-feature-name
```

### 2. Make Changes
- Write clean, documented code
- Follow existing code style
- Add tests for new features
- Update documentation

### 3. Run Tests
```bash
# Run all tests
make test

# Run with coverage
make test-coverage

# Run specific category
pytest -m security
```

### 4. Format Code
```bash
# Format code
make format

# Check code quality
make lint
```

### 5. Commit Changes
```bash
git add .
git commit -m "feat: add new feature"
```

### 6. Push and Create PR
```bash
git push origin feature/your-feature-name
```

## Code Style

### Python
- Follow PEP 8
- Use type hints
- Write docstrings for all public functions
- Maximum line length: 120 characters

### Formatting
```bash
# Auto-format with black
black tools/ai_generator/

# Sort imports with isort
isort tools/ai_generator/

# Check with flake8
flake8 tools/ai_generator/ --max-line-length=120
```

## Testing

### Writing Tests
```python
import pytest
from pathlib import Path

@pytest.mark.integration
@pytest.mark.security
class TestNewFeature:
    """Integration tests for new feature"""

    def test_basic_functionality(self, temp_dir):
        """Test basic feature functionality"""
        # Arrange
        input_data = {...}

        # Act
        result = your_function(input_data)

        # Assert
        assert result is not None
        assert len(result) > 0
```

### Running Tests
```bash
# All tests
pytest

# Specific marker
pytest -m integration

# Specific file
pytest tests/integration/test_security_integration.py

# With coverage
pytest --cov=tools/ai_generator --cov-report=html
```

## Documentation

### Module Documentation
Each new module should include:
- Module-level docstring
- Function/class docstrings
- Type hints
- Usage examples in `tools/ai_generator/examples/`

### Example Format
```python
"""
Module for XYZ functionality.

This module provides...
"""

from typing import Dict, List
from pathlib import Path

def example_function(param: str) -> Dict[str, any]:
    """
    Brief description of function.

    Args:
        param: Description of parameter

    Returns:
        Dictionary containing...

    Example:
        >>> result = example_function("test")
        >>> print(result)
        {...}
    """
    pass
```

## Commit Messages

Follow conventional commits:

```
feat: add new feature
fix: bug fix
docs: documentation update
test: add tests
refactor: code refactoring
perf: performance improvement
chore: maintenance tasks
```

Examples:
```
feat(security): add new encryption algorithm
fix(mlops): resolve drift detection bug
docs(readme): update installation instructions
test(distributed): add microservice tests
```

## Pull Request Process

1. **Update Documentation**: Ensure README and relevant docs are updated
2. **Add Tests**: New features must have tests
3. **Pass CI Checks**: All CI/CD checks must pass
4. **Request Review**: Tag maintainers for review
5. **Address Feedback**: Respond to review comments
6. **Squash Commits**: Clean up commit history before merge

## Code Review

Reviewers will check:
- Code quality and style
- Test coverage
- Documentation completeness
- Performance implications
- Security considerations

## Adding New Modules

### Structure
```
tools/ai_generator/your_category/
├── __init__.py
├── your_module.py
└── tests/
    └── test_your_module.py
```

### Checklist
- [ ] Module implementation with type hints
- [ ] Unit tests (>80% coverage)
- [ ] Integration tests
- [ ] Documentation and examples
- [ ] Benchmark implementation
- [ ] Update category README
- [ ] Update main README

## Performance Guidelines

- Profile code for performance bottlenecks
- Add benchmarks for new features
- Target execution times:
  - Simple operations: < 10ms
  - Complex operations: < 100ms
- Memory efficient implementations

## Security Guidelines

- Never commit secrets or credentials
- Use parameterized queries for databases
- Validate all user inputs
- Follow OWASP Top 10 guidelines
- Run security scans: `make security-check`

## Questions?

- Check existing documentation
- Search existing issues
- Ask in discussions
- Contact maintainers

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

Thank you for contributing! 🎉
