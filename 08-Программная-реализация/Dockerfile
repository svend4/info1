# Dockerfile для карточной системы
FROM python:3.10-slim

LABEL maintainer="info1-project"
LABEL description="Card system for home automation"

# Рабочая директория
WORKDIR /app

# Копируем файлы проекта
COPY card_system/ ./card_system/
COPY requirements.txt setup.py ./
COPY examples/ ./examples/

# Устанавливаем зависимости
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -e .

# Создаём директорию для хранения карточек
RUN mkdir -p /data/cards

# Volume для persistent storage
VOLUME ["/data/cards"]

# Переменные окружения
ENV CARDS_DIR=/data/cards
ENV PYTHONUNBUFFERED=1

# Порт для Flask API (если используется)
EXPOSE 5000

# Default command: запуск демо
CMD ["card-demo"]
