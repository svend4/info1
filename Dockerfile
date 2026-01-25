# AI Generator Toolkit - Production Docker Image
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY tools/ ./tools/
COPY setup.py .
COPY README.md .

# Install the package
RUN pip install -e .

# Create non-root user
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

USER appuser

# Expose port (if running as a service)
EXPOSE 8000

# Default command
CMD ["python", "-m", "tools.ai_generator"]

# ============================================================================
# Development Image
# ============================================================================
FROM base as development

USER root

# Install development dependencies
COPY requirements-dev.txt .
RUN pip install --no-cache-dir -r requirements-dev.txt

# Install additional dev tools
RUN pip install ipython jupyter

USER appuser

CMD ["bash"]

# ============================================================================
# Test Image
# ============================================================================
FROM development as test

USER root

# Copy test files
COPY tests/ ./tests/
COPY pytest.ini .
COPY run_tests.sh .

USER appuser

# Run tests
CMD ["pytest", "-v", "--cov=tools/ai_generator"]

# ============================================================================
# Benchmark Image
# ============================================================================
FROM base as benchmark

USER root

# Copy benchmark files
COPY benchmarks/ ./benchmarks/

USER appuser

# Run benchmarks
CMD ["python", "benchmarks/run_all_benchmarks.py"]
