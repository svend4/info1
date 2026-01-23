# Docker — Запуск в контейнере

Руководство по запуску карточной системы в Docker контейнере.

---

## Быстрый старт

### 1. Сборка образа

\`\`\`bash
cd 08-Программная-реализация
docker build -t card-system:latest .
\`\`\`

### 2. Запуск CLI

\`\`\`bash
docker run -it --rm \
  -v $(pwd)/cards:/data/cards \
  card-system:latest \
  card-cli list
\`\`\`

### 3. Запуск Flask API

\`\`\`bash
docker run -d \
  --name card-api \
  -p 5000:5000 \
  -v $(pwd)/cards:/data/cards \
  card-system:latest \
  python examples/flask_api_example.py
\`\`\`

API будет доступен на http://localhost:5000

---

## Docker Compose

Для запуска всех сервисов одновременно используйте Docker Compose.

### Запуск всех сервисов

\`\`\`bash
# API + Automation
docker-compose up -d api automation

# Только API
docker-compose up api

# С Telegram ботом (требуется BOT_TOKEN в .env)
docker-compose --profile bot up
\`\`\`

### Проверка статуса

\`\`\`bash
docker-compose ps
\`\`\`

### Логи

\`\`\`bash
# Все сервисы
docker-compose logs -f

# Конкретный сервис
docker-compose logs -f api
\`\`\`

### Остановка

\`\`\`bash
docker-compose down
\`\`\`

---

## Сервисы

### api (Flask REST API)
- **Порт:** 5000
- **Health check:** http://localhost:5000/api/health
- **Документация:** см. examples/flask_api_example.py

### automation
- Автоматические задачи (проверка напоминаний, backup, отчёты)
- Работает в фоне

### bot (Telegram)
- Требует BOT_TOKEN в .env файле
- Запускается только с флагом --profile bot

---

## Volumes

Данные карточек хранятся в Docker volume \`cards-data\`:

\`\`\`bash
# Список volumes
docker volume ls

# Инспекция volume
docker volume inspect card-system_cards-data

# Backup
docker run --rm \
  -v card-system_cards-data:/data \
  -v $(pwd):/backup \
  alpine tar czf /backup/cards-backup.tar.gz -C /data .

# Restore
docker run --rm \
  -v card-system_cards-data:/data \
  -v $(pwd):/backup \
  alpine tar xzf /backup/cards-backup.tar.gz -C /data
\`\`\`

---

## Environment variables

Переменные окружения можно задать в файле \`.env\`:

\`\`\`bash
# .env file
CARDS_DIR=/data/cards
BOT_TOKEN=your-telegram-bot-token-here
\`\`\`

---

## Production deployment

Для production используйте:

1. **Bind volumes** вместо named volumes для легкого доступа к данным
2. **Environment variables** через .env файл или secrets
3. **Health checks** для всех сервисов
4. **Restart policies** (restart: unless-stopped)
5. **Nginx** reverse proxy перед Flask API
6. **SSL/TLS** сертификаты

### Пример production docker-compose:

\`\`\`yaml
version: '3.8'

services:
  api:
    image: card-system:latest
    restart: always
    volumes:
      - /opt/cards/data:/data/cards:rw
      - /opt/cards/backups:/backups:rw
    environment:
      - CARDS_DIR=/data/cards
    ports:
      - "127.0.0.1:5000:5000"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  nginx:
    image: nginx:alpine
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - /etc/letsencrypt:/etc/letsencrypt:ro
    depends_on:
      - api
\`\`\`

---

## Troubleshooting

### Контейнер не запускается

\`\`\`bash
# Проверить логи
docker logs card-system-api

# Запустить интерактивно
docker run -it --rm card-system:latest bash
\`\`\`

### Permission denied для volume

\`\`\`bash
# Изменить владельца
sudo chown -R $USER:$USER ./cards
\`\`\`

### API недоступен

\`\`\`bash
# Проверить порты
docker ps
netstat -tulpn | grep 5000

# Проверить health
curl http://localhost:5000/api/health
\`\`\`

---

## Размер образа

Текущий образ базируется на \`python:3.10-slim\` (~150 MB).

Для уменьшения размера:
- Используйте \`python:3.10-alpine\` (~50 MB)
- Multi-stage build для production

---

**См. также:**
- [Dockerfile](Dockerfile) — конфигурация образа
- [docker-compose.yml](docker-compose.yml) — оркестрация сервисов
- [README.md](README.md) — основная документация
