# Утилиты карточной системы

**α-уровень:** -2 (детальная документация)

---

## Обзор

Этот документ описывает вспомогательные утилиты для управления карточной системой:
- **seed_data.py** — инициализация демо-данных
- **backup_restore.py** — резервное копирование и восстановление

---

## 🎬 seed_data.py — Демонстрационные данные

### Назначение

Скрипт создает набор примеров карточек всех типов для демонстрации возможностей системы. Полезно для:
- Новых пользователей (быстрый старт)
- Тестирования функционала
- Разработки и отладки
- Демонстрации системы

### Что создается

**Типы карточек:**
- 📋 **Задачи (5 шт.)** — покупки, оплата, звонки, записи, досуг
- 💊 **Лекарства (4 шт.)** — Эналаприл, Аспирин, Витамин D3, Парацетамол
- 👤 **Контакты (5 шт.)** — врачи, семья, сантехник, соседи, аптека
- 📅 **Встречи (3 шт.)** — прием у врача, визиты, встречи с соседями
- 🛒 **Покупки (3 шт.)** — продукты, лекарства, хозтовары
- 📝 **Заметки (3 шт.)** — рецепты, телефоны, идеи

**Итого:** ~23 карточки с реалистичными данными

### Использование

#### Базовое использование

```bash
cd 08-Программная-реализация/card_system
python3 seed_data.py
```

Скрипт спросит подтверждение если директория уже содержит данные.

#### Программное использование

```python
from seed_data import (
    create_demo_tasks,
    create_demo_medicines,
    create_demo_contacts
)
from card_manager import CardManager

# Создать менеджер
manager = CardManager('path/to/cards')

# Создать только определенный тип данных
create_demo_tasks(manager)
create_demo_medicines(manager)
```

### Примеры созданных карточек

**Задача:**
```
Название: Купить молоко
Описание: Купить 2 литра молока в магазине
Приоритет: Высокий
Срок: Завтра
Теги: покупки, срочно
```

**Лекарство:**
```
Название: Эналаприл
Дозировка: 10 мг
Расписание: 09:00, 21:00
Врач: Кардиолог Иванов И.И.
Теги: давление, ежедневно
```

**Контакт:**
```
Название: Дочь Мария
Телефон: +7-812-987-65-43
Email: maria@email.com
Адрес: Санкт-Петербург, Невский пр-т, д. 50, кв. 25
Теги: семья, дети
```

### После запуска

```bash
# Просмотреть созданные карточки
card-cli list

# Или запустить веб-интерфейс
python3 ../examples/flask_api_example.py

# Или демо
card-demo
```

---

## 💾 backup_restore.py — Резервное копирование

### Назначение

Утилита для создания резервных копий всех карточек и восстановления данных. Критически важно для:
- Безопасности данных
- Миграции между устройствами
- Тестирования (создать копию, протестировать, восстановить)
- Архивирования

### Функции

- ✅ Создание резервных копий в JSON или ZIP
- ✅ Восстановление с заменой или объединением
- ✅ Dry-run режим (предпросмотр без изменений)
- ✅ Список доступных резервных копий
- ✅ Метаданные (дата, версия, количество карточек)

### Использование

#### 1. Создание резервной копии

```bash
# Базовое использование (создает backup_YYYYMMDD_HHMMSS.zip)
python3 backup_restore.py backup

# В определенный файл
python3 backup_restore.py backup --output my_backup.zip

# В JSON формате без сжатия
python3 backup_restore.py backup --format json --no-compress

# Указать директорию с данными
python3 backup_restore.py backup --data-dir /path/to/cards
```

**Вывод:**
```
📦 Создание резервной копии...
Источник: /home/user/.card_system/cards
Найдено карточек: 23
✅ Резервная копия создана: backup_20260124_150000.zip
Размер: 12,345 байт (12.1 KB)
```

#### 2. Восстановление из резервной копии

```bash
# Восстановить (ЗАМЕНИТ текущие данные!)
python3 backup_restore.py restore backup_20260124_150000.zip

# Объединить с текущими данными
python3 backup_restore.py restore backup.zip --merge

# Предпросмотр (без изменений)
python3 backup_restore.py restore backup.zip --dry-run
```

**Вывод (dry-run):**
```
📂 Восстановление из: backup_20260124_150000.zip

Информация о резервной копии:
  Создана: 2026-01-24T15:00:00
  Версия: 1.0
  Карточек: 23

🔍 Режим dry-run: показываю что будет восстановлено

Будет восстановлено:
  contact: 5 карточек
    - Кардиолог Иванов И.И.
    - Дочь Мария
    - Сантехник Петров
    ... и еще 2
  medicine: 4 карточек
  task: 5 карточек
  ...
```

#### 3. Список резервных копий

```bash
# В текущей директории
python3 backup_restore.py list

# В определенной директории
python3 backup_restore.py list --dir /path/to/backups
```

**Вывод:**
```
📂 Найдено резервных копий: 3

  • backup_20260124_150000.zip
    Размер: 12,345 байт (12.1 KB)
    Изменён: 2026-01-24 15:00:00

  • backup_20260123_120000.zip
    Размер: 11,234 байт (11.0 KB)
    Изменён: 2026-01-23 12:00:00
```

### Форматы резервных копий

#### JSON (несжатый)

```json
{
  "metadata": {
    "created_at": "2026-01-24T15:00:00",
    "version": "1.0",
    "total_cards": 23,
    "source_dir": "/home/user/.card_system/cards"
  },
  "cards": [
    {
      "id": "uuid-here",
      "title": "Купить молоко",
      "type": "task",
      ...
    }
  ]
}
```

**Преимущества:**
- Читаемый формат
- Легко редактировать вручную
- Можно версионировать в Git

**Недостатки:**
- Больший размер файла

#### ZIP (сжатый, по умолчанию)

Содержит JSON файл внутри ZIP архива.

**Преимущества:**
- Меньший размер (сжатие ~50-70%)
- Удобно для пересылки

**Недостатки:**
- Нужно распаковывать для редактирования

### Сценарии использования

#### Ежедневное резервное копирование

```bash
#!/bin/bash
# Скрипт ежедневного backup

cd /path/to/card_system
python3 backup_restore.py backup --output ~/backups/daily_backup.zip

# Или с автоматическим именем
python3 backup_restore.py backup --output ~/backups/backup_$(date +%Y%m%d).zip
```

#### Миграция на новое устройство

```bash
# На старом устройстве
python3 backup_restore.py backup --output transfer_backup.zip

# Копировать transfer_backup.zip на новое устройство

# На новом устройстве
python3 backup_restore.py restore transfer_backup.zip
```

#### Тестирование с откатом

```bash
# 1. Создать backup перед тестами
python3 backup_restore.py backup --output before_test.zip

# 2. Провести тесты, внести изменения
# ...

# 3. Если что-то пошло не так - откатиться
python3 backup_restore.py restore before_test.zip
```

#### Объединение данных

```bash
# Есть карточки на рабочем компьютере
python3 backup_restore.py backup --output work_cards.zip

# Перенести на домашний компьютер
# Объединить с домашними карточками
python3 backup_restore.py restore work_cards.zip --merge
```

### Программное использование

```python
from backup_restore import BackupManager

# Создать менеджер
manager = BackupManager('/path/to/cards')

# Создать резервную копию
backup_path = manager.create_backup('my_backup.zip', format='zip')

# Восстановить
manager.restore_backup('my_backup.zip', merge=False)

# Список резервных копий
backups = manager.list_backups('/path/to/backups')
```

---

## 🔗 Интеграция с другими инструментами

### Автоматизация с cron

```bash
# Ежедневный backup в 2:00
0 2 * * * cd /path/to/card_system && python3 backup_restore.py backup --output ~/backups/daily.zip

# Еженедельный backup в воскресенье в 3:00
0 3 * * 0 cd /path/to/card_system && python3 backup_restore.py backup --output ~/backups/weekly_$(date +%Y%m%d).zip
```

### Синхронизация с облаком

```bash
#!/bin/bash
# backup_to_cloud.sh

# Создать резервную копию
cd /path/to/card_system
python3 backup_restore.py backup --output /tmp/cards_backup.zip

# Загрузить в Dropbox/Google Drive
rclone copy /tmp/cards_backup.zip dropbox:backups/

# Или в облачное хранилище
aws s3 cp /tmp/cards_backup.zip s3://my-bucket/backups/

# Очистить временный файл
rm /tmp/cards_backup.zip
```

---

## 🛠️ Troubleshooting

### Проблема: "Нет карточек для резервного копирования"

**Причина:** Директория с данными пуста

**Решение:**
```bash
# Проверить директорию
ls -la ~/.card_system/cards/

# Создать демо-данные
python3 seed_data.py

# Или указать правильную директорию
python3 backup_restore.py backup --data-dir /correct/path
```

### Проблема: "Файл резервной копии не найден"

**Причина:** Неправильный путь к backup файлу

**Решение:**
```bash
# Проверить доступные резервные копии
python3 backup_restore.py list

# Указать полный путь
python3 backup_restore.py restore /full/path/to/backup.zip
```

### Проблема: Резервная копия повреждена

**Причина:** Файл поврежден или неполный

**Решение:**
```bash
# Проверить ZIP целостность
unzip -t backup.zip

# Для JSON проверить синтаксис
python3 -m json.tool backup.json > /dev/null

# Если backup поврежден, использовать более раннюю копию
python3 backup_restore.py list
python3 backup_restore.py restore backup_older.zip
```

---

## См. также

### ⇑ ВВЕРХ (документация и руководства)
- [README.md](README.md) — основная документация card_system
- [../README.md](../README.md) — общая документация программной реализации
- [../API-REFERENCE.md](../API-REFERENCE.md) — полный API reference

### ⇓ ВНИЗ (исполняемый код)
- [card_manager.py](card_manager.py) — менеджер карточек (используется утилитами)
- [card.py](card.py) — базовая модель карточки
- [export_import.py](export_import.py) — экспорт/импорт (альтернатива backup)

### ↔ СВЯЗИ (практические примеры)
- [demo.py](demo.py) — демонстрация работы системы
- [cli.py](cli.py) — CLI интерфейс для управления карточками
- [../EXAMPLES.md](../EXAMPLES.md) — практические примеры использования

---

**Дата создания:** 2026-01-24
**Версия:** 1.0
