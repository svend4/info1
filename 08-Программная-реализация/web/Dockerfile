# Multi-stage Docker build для AI Generator API

# Stage 1: Builder
FROM python:3.11-slim as builder

WORKDIR /build

# Установка зависимостей для сборки
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Копируем requirements
COPY requirements-ai.txt .

# Устанавливаем зависимости в /install директорию
RUN pip install --prefix=/install --no-cache-dir -r requirements-ai.txt

# Stage 2: Runtime
FROM python:3.11-slim

WORKDIR /app

# Копируем установленные пакеты из builder stage
COPY --from=builder /install /usr/local

# Копируем AI Generator API
COPY ai_api.py .
COPY ai-generator.html .
COPY AI-GENERATOR-README.md .

# Копируем tools/ai_generator
COPY ../../tools /app/tools

# Создаём unprivileged пользователя
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

USER appuser

# Expose порт
EXPOSE 5001

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5001/api/ai/health')" || exit 1

# Запуск с production-ready конфигурацией
CMD ["python", "-u", "ai_api.py"]
