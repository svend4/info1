#!/bin/bash
#
# AI Generator Toolkit - Test Runner
# Runs all integration and unit tests with coverage reporting
#

set -e

echo "====================================================================="
echo "  AI Generator Toolkit - Test Suite Runner"
echo "====================================================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Parse command line arguments
TEST_TYPE="${1:-all}"
PARALLEL="${2:-false}"

echo "📋 Configuration:"
echo "   Test type: $TEST_TYPE"
echo "   Parallel execution: $PARALLEL"
echo ""

# Install dependencies if needed
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    pip install -r requirements-dev.txt
else
    source venv/bin/activate
fi

# Create reports directory
mkdir -p reports/coverage
mkdir -p reports/junit

echo ""
echo "====================================================================="
echo "  Running Tests"
echo "====================================================================="
echo ""

# Function to run tests
run_tests() {
    local test_marker=$1
    local test_name=$2

    echo -e "${YELLOW}▶ Running ${test_name} tests...${NC}"

    if [ "$PARALLEL" = "true" ]; then
        pytest -v -m "$test_marker" \
            --cov=tools/ai_generator \
            --cov-report=html:reports/coverage/${test_name} \
            --cov-report=term-missing \
            --junit-xml=reports/junit/${test_name}.xml \
            -n auto
    else
        pytest -v -m "$test_marker" \
            --cov=tools/ai_generator \
            --cov-report=html:reports/coverage/${test_name} \
            --cov-report=term-missing \
            --junit-xml=reports/junit/${test_name}.xml
    fi

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ ${test_name} tests passed!${NC}"
    else
        echo -e "${RED}❌ ${test_name} tests failed!${NC}"
        exit 1
    fi
    echo ""
}

# Run tests based on test type
case $TEST_TYPE in
    "all")
        echo "Running all tests..."
        run_tests "integration or unit" "all"
        ;;
    "integration")
        echo "Running integration tests only..."
        run_tests "integration" "integration"
        ;;
    "unit")
        echo "Running unit tests only..."
        run_tests "unit" "unit"
        ;;
    "security")
        echo "Running security module tests..."
        run_tests "security" "security"
        ;;
    "mlops")
        echo "Running MLOps module tests..."
        run_tests "mlops" "mlops"
        ;;
    "codegen")
        echo "Running code generation module tests..."
        run_tests "codegen" "codegen"
        ;;
    "distributed")
        echo "Running distributed systems module tests..."
        run_tests "distributed" "distributed"
        ;;
    "mobile")
        echo "Running mobile development module tests..."
        run_tests "mobile" "mobile"
        ;;
    "ai_pair")
        echo "Running AI pair programming module tests..."
        run_tests "ai_pair" "ai_pair"
        ;;
    "testing")
        echo "Running testing module tests..."
        run_tests "testing" "testing"
        ;;
    "devops")
        echo "Running DevOps module tests..."
        run_tests "devops" "devops"
        ;;
    "fast")
        echo "Running fast tests only (excluding slow tests)..."
        pytest -v -m "not slow" \
            --cov=tools/ai_generator \
            --cov-report=html:reports/coverage/fast \
            --cov-report=term-missing \
            --junit-xml=reports/junit/fast.xml
        ;;
    *)
        echo -e "${RED}Unknown test type: $TEST_TYPE${NC}"
        echo "Usage: $0 [all|integration|unit|security|mlops|codegen|distributed|mobile|ai_pair|testing|devops|fast] [true|false]"
        exit 1
        ;;
esac

echo ""
echo "====================================================================="
echo "  Test Summary"
echo "====================================================================="
echo ""

# Show coverage summary
if [ -f "reports/coverage/${TEST_TYPE}/index.html" ]; then
    echo -e "${GREEN}📊 Coverage report generated:${NC}"
    echo "   reports/coverage/${TEST_TYPE}/index.html"
fi

# Show JUnit report
if [ -f "reports/junit/${TEST_TYPE}.xml" ]; then
    echo -e "${GREEN}📋 JUnit report generated:${NC}"
    echo "   reports/junit/${TEST_TYPE}.xml"
fi

echo ""
echo -e "${GREEN}✅ All tests completed successfully!${NC}"
echo ""

# Optional: Run code quality checks
if [ "$TEST_TYPE" = "all" ]; then
    echo "====================================================================="
    echo "  Code Quality Checks"
    echo "====================================================================="
    echo ""

    echo "🔍 Running black (code formatting)..."
    black --check tools/ai_generator/ || true

    echo "🔍 Running isort (import sorting)..."
    isort --check-only tools/ai_generator/ || true

    echo "🔍 Running flake8 (linting)..."
    flake8 tools/ai_generator/ --max-line-length=120 || true

    echo "🔍 Running bandit (security)..."
    bandit -r tools/ai_generator/ -f screen || true

    echo ""
fi

echo "====================================================================="
echo "  Done!"
echo "====================================================================="
