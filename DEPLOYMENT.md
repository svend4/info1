# Руководство по развертыванию системы
*Уровень абстракции: α=+1 (методология)*

**Версия:** 1.0
**Дата:** 2026-01-23
**Уровень абстракции:** α=-2 (развертывание и конфигурация)
**Статус:** ✅ Production Ready

---

## Содержание

1. [Введение](#введение)
2. [Требования к системе](#требования-к-системе)
3. [Вариант 1: Локальная установка](#вариант-1-локальная-установка)
4. [Вариант 2: Docker (рекомендуется)](#вариант-2-docker-рекомендуется)
5. [Вариант 3: Production сервер](#вариант-3-production-сервер)
6. [Конфигурация](#конфигурация)
7. [Мониторинг и логирование](#мониторинг-и-логирование)
8. [Backup и восстановление](#backup-и-восстановление)
9. [Безопасность](#безопасность)
10. [Обновление системы](#обновление-системы)
11. [Устранение неполадок](#устранение-неполадок)

---

## Введение

Данное руководство описывает все возможные способы развертывания домашней информационной системы управления карточками.

**Целевая аудитория:**
- Системные администраторы
- DevOps инженеры
- Продвинутые пользователи
- Разработчики

**Время развертывания:**
- Локальная установка: 10-15 минут
- Docker: 5-10 минут
- Production сервер: 30-60 минут

---

## Требования к системе

### Минимальные требования

| Компонент | Минимум | Рекомендуется |
|-----------|---------|---------------|
| **ОС** | Linux, macOS, Windows | Ubuntu 22.04 LTS |
| **CPU** | 1 ядро | 2+ ядра |
| **RAM** | 512 MB | 2 GB |
| **Диск** | 100 MB | 1 GB |
| **Python** | 3.8+ | 3.10+ |

### Поддерживаемые ОС

- ✅ **Ubuntu** 20.04, 22.04, 24.04
- ✅ **Debian** 10, 11, 12
- ✅ **CentOS** / RHEL 8, 9
- ✅ **macOS** 11+
- ✅ **Windows** 10, 11 (WSL2 или native)
- ✅ **Docker** (любая ОС с Docker 20.10+)

### Зависимости

**Обязательные:**
- Python 3.8+
- pip

**Опциональные (для веб-интерфейса):**
- Flask (для API сервера)
- flask-cors (для CORS support)

**Опциональные (для разработки):**
- pytest (для тестов)
- flake8 (для линтинга)
- mypy (для проверки типов)

---

## Вариант 1: Локальная установка

### Шаг 1: Клонирование репозитория

```bash
# Клонировать проект
git clone https://github.com/svend4/info1.git
cd info1
```

### Шаг 2: Установка базовой системы

```bash
# Перейти в директорию программной реализации
cd 08-Программная-реализация

# Установить систему
pip install -e .

# Проверить установку
card-cli --version
```

**Что произошло:**
- Установлен пакет `card_system` в editable режиме
- Добавлены CLI команды: `card-cli`, `card-demo`, `card-automation`
- Создана директория данных: `~/.card_system/cards/`

### Шаг 3: Запуск демонстрации

```bash
# Запустить демо (создаст 20+ примеров карточек)
card-demo

# Посмотреть список карточек
card-cli list

# Создать свою карточку
card-cli create task "Моя первая задача"
```

### Шаг 4: Установка веб-интерфейса (опционально)

```bash
# Установить зависимости для веб
pip install -e .[web]

# Запустить API сервер
python3 examples/flask_api_example.py

# В другом терминале: открыть веб-интерфейс
cd web
python3 -m http.server 8080

# Открыть в браузере: http://localhost:8080
```

### Шаг 5: Настройка автоматизации (опционально)

```bash
# Запустить систему автоматизации в фоне
card-automation --daemon

# Проверить статус
ps aux | grep card-automation

# Остановить
pkill -f card-automation
```

---

## Вариант 2: Docker (рекомендуется)

### Шаг 1: Установка Docker

**Ubuntu / Debian:**
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

**macOS:**
```bash
brew install --cask docker
```

**Windows:**
- Скачать [Docker Desktop](https://www.docker.com/products/docker-desktop)

### Шаг 2: Клонирование и запуск

```bash
# Клонировать проект
git clone https://github.com/svend4/info1.git
cd info1/08-Программная-реализация

# Запустить все сервисы
docker-compose up -d

# Проверить статус
docker-compose ps

# Просмотр логов
docker-compose logs -f
```

**Что запустилось:**
- `api` — Flask API сервер (порт 5000)
- `automation` — система автоматизации
- `bot` — Telegram бот (если настроен)

### Шаг 3: Доступ к интерфейсам

- **Веб-интерфейс:** http://localhost:5000
- **API:** http://localhost:5000/api/cards
- **Данные:** Docker volume `cards-data`

### Шаг 4: Управление контейнерами

```bash
# Остановить
docker-compose stop

# Перезапустить
docker-compose restart

# Удалить (с сохранением данных)
docker-compose down

# Удалить (с удалением данных)
docker-compose down -v

# Обновить образы
docker-compose pull
docker-compose up -d
```

---

## Вариант 3: Production сервер

### Архитектура production развертывания

```
┌─────────────────────────────────────────────┐
│              Internet                       │
└───────────────┬─────────────────────────────┘
                │
                ↓
┌───────────────────────────────────────────────┐
│         Nginx (reverse proxy)                 │
│   - SSL/TLS termination                       │
│   - Static files serving                      │
│   - Rate limiting                             │
└───────────────┬───────────────────────────────┘
                │
                ↓
┌───────────────────────────────────────────────┐
│       Gunicorn (WSGI server)                  │
│   - Flask application                         │
│   - 4 worker processes                        │
└───────────────┬───────────────────────────────┘
                │
                ↓
┌───────────────────────────────────────────────┐
│          Card System                          │
│   - CardManager                               │
│   - YAML files storage                        │
└───────────────────────────────────────────────┘
```

### Шаг 1: Подготовка сервера

```bash
# Обновить систему
sudo apt update && sudo apt upgrade -y

# Установить необходимые пакеты
sudo apt install -y python3 python3-pip python3-venv nginx certbot python3-certbot-nginx

# Создать пользователя для приложения
sudo useradd -m -s /bin/bash cardapp
sudo su - cardapp
```

### Шаг 2: Установка приложения

```bash
# От имени cardapp

# Клонировать проект
git clone https://github.com/svend4/info1.git
cd info1/08-Программная-реализация

# Создать виртуальное окружение
python3 -m venv venv
source venv/bin/activate

# Установить приложение с production зависимостями
pip install -e .[web,prod]

# Создать директории
mkdir -p /home/cardapp/logs
mkdir -p /home/cardapp/data/cards
```

### Шаг 3: Настройка Gunicorn

```bash
# Создать конфигурацию Gunicorn
cat > gunicorn_config.py <<'EOF'
import multiprocessing

bind = "127.0.0.1:8000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

# Логирование
accesslog = "/home/cardapp/logs/gunicorn-access.log"
errorlog = "/home/cardapp/logs/gunicorn-error.log"
loglevel = "info"

# Security
limit_request_line = 4096
limit_request_fields = 100
limit_request_field_size = 8190
EOF

# Создать WSGI entry point
cat > wsgi.py <<'EOF'
import sys
sys.path.insert(0, '/home/cardapp/info1/08-Программная-реализация')

from examples.flask_api_example import app

if __name__ == "__main__":
    app.run()
EOF
```

### Шаг 4: Создание systemd service

```bash
# От имени root
sudo cat > /etc/systemd/system/cardapp.service <<'EOF'
[Unit]
Description=Card System API Server
After=network.target

[Service]
Type=notify
User=cardapp
Group=cardapp
WorkingDirectory=/home/cardapp/info1/08-Программная-реализация
Environment="PATH=/home/cardapp/info1/08-Программная-реализация/venv/bin"
Environment="CARDS_DIR=/home/cardapp/data/cards"
ExecStart=/home/cardapp/info1/08-Программная-реализация/venv/bin/gunicorn --config gunicorn_config.py wsgi:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Включить и запустить сервис
sudo systemctl daemon-reload
sudo systemctl enable cardapp
sudo systemctl start cardapp
sudo systemctl status cardapp
```

### Шаг 5: Настройка Nginx

```bash
# Создать конфигурацию Nginx
sudo cat > /etc/nginx/sites-available/cardapp <<'EOF'
upstream cardapp {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name your-domain.com;  # ИЗМЕНИТЬ НА СВОЙ ДОМЕН

    # Логи
    access_log /var/log/nginx/cardapp-access.log;
    error_log /var/log/nginx/cardapp-error.log;

    # Статические файлы (веб-интерфейс)
    location / {
        root /home/cardapp/info1/08-Программная-реализация/web;
        try_files $uri $uri/ /index.html;
    }

    # API endpoint
    location /api {
        proxy_pass http://cardapp;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Таймауты
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
    limit_req zone=api_limit burst=20 nodelay;

    # Безопасность
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
}
EOF

# Активировать конфигурацию
sudo ln -s /etc/nginx/sites-available/cardapp /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### Шаг 6: Настройка SSL/TLS (Let's Encrypt)

```bash
# Получить SSL сертификат
sudo certbot --nginx -d your-domain.com

# Автопродление (cron уже настроен certbot)
sudo certbot renew --dry-run
```

### Шаг 7: Настройка автоматизации

```bash
# Создать systemd service для автоматизации
sudo cat > /etc/systemd/system/cardapp-automation.service <<'EOF'
[Unit]
Description=Card System Automation
After=network.target

[Service]
Type=simple
User=cardapp
Group=cardapp
WorkingDirectory=/home/cardapp/info1/08-Программная-реализация
Environment="PATH=/home/cardapp/info1/08-Программная-реализация/venv/bin"
Environment="CARDS_DIR=/home/cardapp/data/cards"
ExecStart=/home/cardapp/info1/08-Программная-реализация/venv/bin/card-automation --daemon
Restart=always
RestartSec=60

[Install]
WantedBy=multi-user.target
EOF

# Включить и запустить
sudo systemctl daemon-reload
sudo systemctl enable cardapp-automation
sudo systemctl start cardapp-automation
```

---

## Конфигурация

### Переменные окружения

```bash
# Основные настройки
export CARDS_DIR="/path/to/cards"  # Директория данных (default: ~/.card_system/cards)
export FLASK_ENV="production"       # Режим Flask (development/production)
export LOG_LEVEL="INFO"             # Уровень логирования (DEBUG/INFO/WARNING/ERROR)

# Telegram бот (опционально)
export BOT_TOKEN="your-telegram-bot-token"

# Backup
export BACKUP_DIR="/path/to/backups"  # Директория backup (default: ~/.card_system/backups)
export BACKUP_INTERVAL="86400"        # Интервал backup в секундах (default: 24 часа)
```

### Файл конфигурации

```bash
# Создать файл конфигурации
cat > ~/.card_system/config.yaml <<'EOF'
# Card System Configuration

# Директории
cards_dir: "~/.card_system/cards"
backups_dir: "~/.card_system/backups"
logs_dir: "~/.card_system/logs"

# Логирование
log_level: "INFO"
log_format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Автоматизация
automation:
  enabled: true
  check_overdue_interval: 3600      # Проверка просроченных (секунды)
  medicine_reminder_advance: 300    # Напоминание о лекарствах заранее (секунды)
  archive_after_days: 30            # Архивация старых карточек (дни)
  backup_interval: 86400            # Backup интервал (секунды)

# Веб-интерфейс
web:
  host: "0.0.0.0"
  port: 5000
  debug: false
  cors_origins: ["*"]

# Безопасность
security:
  max_file_size: 1048576             # Максимальный размер файла (байты)
  allowed_extensions: [".md", ".yaml"]
EOF
```

---

## Мониторинг и логирование

### Логи приложения

```bash
# Просмотр логов Gunicorn
tail -f /home/cardapp/logs/gunicorn-access.log
tail -f /home/cardapp/logs/gunicorn-error.log

# Просмотр логов systemd
sudo journalctl -u cardapp -f
sudo journalctl -u cardapp-automation -f

# Логи приложения
tail -f ~/.card_system/logs/card_system.log
```

### Мониторинг системы

```bash
# CPU и память
top -p $(pgrep -f gunicorn)

# Диск
df -h ~/.card_system

# Сетевые соединения
sudo netstat -tlnp | grep 8000

# Статус сервисов
sudo systemctl status cardapp
sudo systemctl status cardapp-automation
sudo systemctl status nginx
```

### Алерты (опционально)

Настройка alertmanager или простой скрипт проверки:

```bash
#!/bin/bash
# /usr/local/bin/check-cardapp.sh

if ! systemctl is-active --quiet cardapp; then
    echo "Card System API is down!" | mail -s "Alert: Card System" admin@example.com
fi

if ! systemctl is-active --quiet cardapp-automation; then
    echo "Card System Automation is down!" | mail -s "Alert: Card System" admin@example.com
fi
```

Добавить в crontab:
```bash
# Проверка каждые 5 минут
*/5 * * * * /usr/local/bin/check-cardapp.sh
```

---

## Backup и восстановление

### Автоматический backup

Система имеет встроенную автоматизацию backup:

```bash
# Автоматический backup (через automation.py)
card-automation --daemon
# Создает backup каждые 24 часа в ~/.card_system/backups/
```

### Ручной backup

```bash
# Создать backup вручную
cd ~/.card_system
tar -czf backups/cards-backup-$(date +%Y%m%d-%H%M%S).tar.gz cards/

# Или использовать встроенный экспорт
cd 08-Программная-реализация
python3 -c "
from card_system.export_import import CardExporter
exporter = CardExporter('~/.card_system/cards')
exporter.export_all_to_zip('backup.zip')
"
```

### Восстановление из backup

```bash
# Из tar.gz архива
cd ~/.card_system
tar -xzf backups/cards-backup-20260123-120000.tar.gz

# Из ZIP экспорта
python3 -c "
from card_system.export_import import CardImporter
importer = CardImporter('~/.card_system/cards')
importer.import_from_zip('backup.zip')
"
```

### Стратегия backup для production

**3-2-1 правило:**
- **3** копии данных
- **2** разных носителя
- **1** копия offsite (удаленная)

```bash
# Скрипт backup с rotацией
#!/bin/bash
# /usr/local/bin/backup-cardapp.sh

BACKUP_DIR="/home/cardapp/backups"
CARDS_DIR="/home/cardapp/data/cards"
DATE=$(date +%Y%m%d-%H%M%S)
BACKUP_FILE="$BACKUP_DIR/cards-$DATE.tar.gz"

# Создать backup
tar -czf "$BACKUP_FILE" "$CARDS_DIR"

# Удалить старые backup (оставить последние 30)
ls -t $BACKUP_DIR/cards-*.tar.gz | tail -n +31 | xargs rm -f

# Отправить на удаленный сервер (опционально)
# rsync -avz "$BACKUP_FILE" backup@remote-server:/backups/
```

Добавить в crontab:
```bash
# Backup каждый день в 2:00
0 2 * * * /usr/local/bin/backup-cardapp.sh
```

---

## Безопасность

### Чеклист безопасности

- [ ] **HTTPS включен** (SSL/TLS сертификаты установлены)
- [ ] **Firewall настроен** (открыты только 80, 443, 22)
- [ ] **Пароли сложные** (для пользователей системы)
- [ ] **Обновления установлены** (OS и пакеты актуальны)
- [ ] **Backup работает** (автоматический backup настроен)
- [ ] **Логи ротируются** (logrotate настроен)
- [ ] **Rate limiting** (защита от DDoS)
- [ ] **CORS настроен** (только разрешенные origins)

### Настройка firewall (ufw)

```bash
# Установить ufw
sudo apt install ufw

# Базовые правила
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Разрешить SSH (ВАЖНО: сделать до enable!)
sudo ufw allow 22/tcp

# Разрешить HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Включить firewall
sudo ufw enable

# Проверить статус
sudo ufw status verbose
```

### Ограничение SSH доступа

```bash
# Редактировать конфигурацию SSH
sudo nano /etc/ssh/sshd_config

# Рекомендуемые настройки:
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes
X11Forwarding no

# Перезапустить SSH
sudo systemctl restart sshd
```

### Регулярные обновления

```bash
# Создать скрипт обновления
sudo cat > /usr/local/bin/update-system.sh <<'EOF'
#!/bin/bash
apt update
apt upgrade -y
apt autoremove -y
EOF

sudo chmod +x /usr/local/bin/update-system.sh

# Добавить в crontab
# Обновления каждое воскресенье в 3:00
0 3 * * 0 /usr/local/bin/update-system.sh
```

---

## Обновление системы

### Обновление приложения

```bash
# Остановить сервисы
sudo systemctl stop cardapp cardapp-automation

# От имени cardapp
cd /home/cardapp/info1
git pull origin main

cd 08-Программная-реализация
source venv/bin/activate
pip install --upgrade -e .[web,prod]

# Запустить сервисы
sudo systemctl start cardapp cardapp-automation

# Проверить статус
sudo systemctl status cardapp
```

### Миграция данных (если требуется)

```bash
# Backup перед миграцией
cd ~/.card_system
tar -czf pre-migration-backup-$(date +%Y%m%d).tar.gz cards/

# Выполнить миграцию (если есть скрипт)
python3 migrate.py

# Проверить целостность
card-cli list
```

---

## Устранение неполадок

### Проблема: API сервер не запускается

**Симптомы:**
```bash
sudo systemctl status cardapp
# показывает "failed"
```

**Решение:**
```bash
# Просмотр логов
sudo journalctl -u cardapp -n 50

# Проверка порта
sudo netstat -tlnp | grep 8000

# Проверка конфигурации
/home/cardapp/info1/08-Программная-реализация/venv/bin/gunicorn --check-config gunicorn_config.py wsgi:app
```

### Проблема: Веб-интерфейс не подключается к API

**Симптомы:**
- Веб-интерфейс открывается, но карточки не загружаются
- В консоли браузера: "Failed to load cards"

**Решение:**
```bash
# Проверить, что API работает
curl http://localhost:5000/api/cards

# Проверить CORS настройки
# В flask_api_example.py должно быть:
from flask_cors import CORS
CORS(app)

# Проверить, что веб-интерфейс настроен на правильный URL
# В web/app.js проверить:
const API_BASE_URL = 'http://localhost:5000/api';
```

### Проблема: Nginx 502 Bad Gateway

**Симптомы:**
```
502 Bad Gateway
```

**Решение:**
```bash
# Проверить, что Gunicorn работает
sudo systemctl status cardapp

# Проверить, что upstream доступен
curl http://127.0.0.1:8000/api/cards

# Проверить логи Nginx
sudo tail -f /var/log/nginx/error.log

# Проверить конфигурацию Nginx
sudo nginx -t
```

### Проблема: Медленная работа

**Симптомы:**
- API отвечает медленно (>1 секунда)
- Веб-интерфейс тормозит

**Решение:**
```bash
# Увеличить количество workers Gunicorn
# В gunicorn_config.py:
workers = 8  # или больше

# Проверить использование ресурсов
top
free -h
df -h

# Оптимизировать YAML загрузку (кеширование)
# Добавить в CardManager кеш
```

---

## Поддержка

**Документация:**
- [README.md](../README.md) — общий обзор
- [QUICKSTART.md](../QUICKSTART.md) — быстрый старт
- [08-Программная-реализация/README.md](../08-Программная-реализация/README.md) — руководство разработчика

**Вопросы и баги:**
- GitHub Issues: https://github.com/svend4/info1/issues

**Лицензия:**
- MIT License — см. [LICENSE](../LICENSE)

---

## См. также

**Методология:**
- [ДОКУМЕНТАЦИЯ.md](ДОКУМЕНТАЦИЯ.md) — полное описание методологии ⇑⇓↔
- [ПРИМЕНЕНИЕ-МЕТОДОЛОГИИ.md](ПРИМЕНЕНИЕ-МЕТОДОЛОГИИ.md) — паттерны применения

**Инструменты и автоматизация:**
- [tools/README.md](tools/README.md) — документация инструментов
- [SETUP-CI-CD.md](SETUP-CI-CD.md) — настройка автоматизации
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) — решение проблем

**Навигация:**
- [КАРТА-РЕПОЗИТОРИЯ.md](КАРТА-РЕПОЗИТОРИЯ.md) — полная карта проекта
- [QUICK-START.md](QUICK-START.md) — быстрый старт

**Архитектура:**
- [ARCHITECTURE.md](ARCHITECTURE.md) — техническая архитектура

---

**Версия документа:** 1.0
**Дата последнего обновления:** 2026-01-23
**Статус:** ✅ Готов к использованию
