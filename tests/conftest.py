"""
Pytest configuration and shared fixtures for AI Generator Toolkit tests
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime


@pytest.fixture(scope="session")
def test_output_dir():
    """Create temporary directory for test outputs"""
    temp_dir = Path(tempfile.mkdtemp(prefix="ai_generator_test_"))
    yield temp_dir
    # Cleanup after all tests
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture(scope="function")
def temp_dir():
    """Create temporary directory for individual test"""
    temp_dir = Path(tempfile.mkdtemp())
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def sample_code():
    """Sample code for testing"""
    return """
def calculate_fibonacci(n: int) -> int:
    if n <= 1:
        return n
    return calculate_fibonacci(n - 1) + calculate_fibonacci(n - 2)

def factorial(n: int) -> int:
    if n <= 1:
        return 1
    return n * factorial(n - 1)
"""


@pytest.fixture
def sample_openapi_spec():
    """Sample OpenAPI specification"""
    return {
        "openapi": "3.0.0",
        "info": {
            "title": "Test API",
            "version": "1.0.0"
        },
        "paths": {
            "/users": {
                "get": {
                    "summary": "List users",
                    "responses": {
                        "200": {
                            "description": "Success"
                        }
                    }
                }
            }
        }
    }


@pytest.fixture
def mock_ml_metrics():
    """Mock ML model metrics"""
    return {
        "accuracy": 0.92,
        "precision": 0.89,
        "recall": 0.91,
        "f1_score": 0.90,
        "auc_roc": 0.94
    }


@pytest.fixture
def mock_user_features():
    """Mock user features for testing"""
    return {
        "user_id": "test_user_001",
        "age": 32,
        "total_purchases": 45,
        "avg_purchase_value": 89.50,
        "days_since_last_purchase": 7,
        "is_premium": True
    }


@pytest.fixture(autouse=True)
def reset_test_environment():
    """Reset environment before each test"""
    yield
    # Cleanup code here if needed


def pytest_configure(config):
    """Pytest configuration hook"""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection"""
    for item in items:
        # Add integration marker to tests in integration directory
        if "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
