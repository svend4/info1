# Quick Start — Быстрый старт за 5 минут

Добро пожаловать в систему организации информации! Это руководство поможет вам начать работу за 5 минут.

**α-уровень:** -1 (практическое руководство)

---

## Что это такое?

Система карточек для организации повседневной жизни:
- 📝 Задачи и списки дел
- 💊 Медицинские записи и напоминания
- 📅 Встречи и контакты
- 🛒 Списки покупок
- 📓 Заметки

**Для кого:** Особенно полезно для пожилых людей и тех, кто хочет структурировать свою жизнь.

---

## Шаг 1: Установка (2 минуты)

### Вариант A: Простая установка

```bash
# Клонируйте репозиторий
git clone https://github.com/svend4/info1.git
cd info1/08-Программная-реализация

# Установите систему
pip install -e .
```

### Вариант B: Установка с дополнениями

```bash
# Для веб-интерфейса
pip install -e ".[web]"

# Для Telegram-бота
pip install -e ".[bot]"

# Всё сразу
pip install -e ".[all]"
```

### Проверка установки

```bash
# Запустите демо
card-demo

# Или проверьте CLI
card-cli --help
```

---

## Шаг 2: Первые карточки (2 минуты)

### Создание задачи

```bash
card-cli create task "Купить молоко"
```

### Создание напоминания о лекарстве

```bash
card-cli create medicine "Эналаприл" --dosage "10 мг" --schedule "09:00,21:00"
```

### Создание контакта

```bash
card-cli create contact "Доктор Иванов" --phone "+7-900-123-4567"
```

### Просмотр всех карточек

```bash
card-cli list
```

---

## Шаг 3: Работа с карточками (1 минута)

### Поиск

```bash
# Поиск по тексту
card-cli search "молоко"

# Фильтр по типу
card-cli list --type task
```

### Просмотр деталей

```bash
# Посмотреть карточку по ID
card-cli show <ID>
```

### Обновление

```bash
# Пометить задачу выполненной
card-cli update <ID> --status completed
```

### Удаление

```bash
card-cli delete <ID>
```

---

## Шаг 4: Программное использование (опционально)

### Python API

```python
from pathlib import Path
from card import TaskCard, MedicineCard
from card_manager import CardManager

# Создание менеджера
manager = CardManager(Path("./my_cards"))

# Создание задачи
task = TaskCard(
    title="Купить молоко",
    description="2 литра обезжиренного",
    priority="high"
)
created_task = manager.create(task)

# Создание напоминания о лекарстве
medicine = MedicineCard(
    title="Эналаприл",
    dosage="10 мг",
    schedule=["09:00", "21:00"],
    doctor="Доктор Иванов"
)
created_medicine = manager.create(medicine)

# Поиск
tasks = manager.search(card_type="task", status="pending")

# Статистика
stats = manager.get_stats()
print(f"Всего карточек: {stats['total']}")
```

---

## Типичные сценарии

### Сценарий 1: Утренняя рутина

```python
# Создать карточки для утренних задач
morning_tasks = [
    TaskCard(title="Принять лекарства", priority="high"),
    TaskCard(title="Измерить давление"),
    TaskCard(title="Сделать зарядку"),
    TaskCard(title="Позавтракать")
]

for task in morning_tasks:
    manager.create(task)

# Просмотр всех задач
pending = manager.search(card_type="task", status="pending")
for task in pending:
    print(f"- {task.title}")
```

### Сценарий 2: Медицинские записи

```python
# Лекарства с расписанием
medicines = [
    MedicineCard(
        title="Эналаприл",
        dosage="10 мг",
        schedule=["09:00", "21:00"]
    ),
    MedicineCard(
        title="Аспирин",
        dosage="100 мг",
        schedule=["20:00"]
    )
]

for med in medicines:
    manager.create(med)

# Врачи
doctor = ContactCard(
    title="Доктор Иванов",
    phone="+7-900-123-4567",
    category="doctor"
)
manager.create(doctor)

# Связать лекарство с врачом
manager.link(medicines[0].id, doctor.id, "prescribed_by")
```

### Сценарий 3: Список покупок

```python
shopping_list = ShoppingCard(
    title="Продукты на неделю",
    items=[
        {"name": "Молоко", "quantity": "2 л", "bought": False},
        {"name": "Хлеб", "quantity": "1 шт", "bought": False},
        {"name": "Яйца", "quantity": "10 шт", "bought": False}
    ]
)
manager.create(shopping_list)

# В магазине: отметить купленное
shopping_list.items[0]["bought"] = True
manager.update(shopping_list)
```

---

## Автоматизация

### Настройка автоматических напоминаний

```python
from automation import CardAutomation

# Создать систему автоматизации
automation = CardAutomation(manager)

# Проверить просроченные задачи
overdue = automation.check_overdue_tasks()
for task in overdue:
    print(f"Просрочено: {task.title}")

# Проверить напоминания о лекарствах
reminders = automation.check_medicine_reminders()
for reminder in reminders:
    print(f"Напоминание: {reminder.title} в {reminder.time}")

# Создать backup
automation.create_backup()

# Сгенерировать еженедельный отчёт
report = automation.generate_report(period="week")
print(report)
```

### Запуск автоматизации в фоне

```bash
# Через CLI
card-automation --daemon

# Или через cron (Linux/Mac)
# Добавьте в crontab:
# 0 * * * * cd /path/to/info1 && card-automation --run
```

---

## Экспорт и импорт

### Экспорт данных

```bash
# Экспорт в JSON
card-cli export --format json --output my_cards.json

# Экспорт в CSV
card-cli export --format csv --output my_cards.csv

# Backup в ZIP
card-cli export --format zip --output backup.zip
```

### Импорт данных

```bash
card-cli import my_cards.json
```

---

## Что дальше?

### Для пользователей

1. **Руководство пользователя** → [USER-GUIDE.md](08-Программная-реализация/USER-GUIDE.md)
   - Подробное описание всех возможностей
   - Советы и лучшие практики
   - FAQ

2. **Примеры использования** → [EXAMPLES.md](08-Программная-реализация/EXAMPLES.md)
   - 8 разделов с практическими примерами
   - Интеграция с веб-приложениями
   - Создание Telegram-бота

### Для разработчиков

1. **API Reference** → [API-REFERENCE.md](08-Программная-реализация/API-REFERENCE.md)
   - Полная документация всех классов и методов
   - Примеры кода для каждого метода

2. **Contributing** → [CONTRIBUTING.md](CONTRIBUTING.md)
   - Как внести вклад в проект
   - Стандарты кода
   - Процесс разработки

3. **Архитектура** → [ARCHITECTURE.md](ARCHITECTURE.md)
   - Визуальная схема системы
   - Уровни абстракции
   - Паттерны проектирования

### Для философов

1. **Методология** → [МЕТОДОЛОГИЯ-ПАРАЛЛЕЛЬНОГО-РАЗВИТИЯ.md](01-Концепция/МЕТОДОЛОГИЯ-ПАРАЛЛЕЛЬНОГО-РАЗВИТИЯ.md)
   - Методология параллельного двунаправленного развития
   - Операторы ⇑⇓↔
   - Опыт 9 циклов разработки

2. **Философия** → [ФИЛОСОФИЯ-ПРОЕКТА.md](01-Концепция/ФИЛОСОФИЯ-ПРОЕКТА.md)
   - Философские основания проекта
   - Человеко-центричность
   - Достоинство и гуманность

---

## Помощь и поддержка

**Проблемы?**
- Проверьте [FAQ в USER-GUIDE.md](08-Программная-реализация/USER-GUIDE.md#faq)
- Создайте issue на GitHub
- Задайте вопрос в Discussions

**Хотите помочь?**
- См. [CONTRIBUTING.md](CONTRIBUTING.md)
- Поделитесь своим опытом использования
- Предложите улучшения

---

## Основные команды — шпаргалка

```bash
# Создание
card-cli create task "Описание задачи"
card-cli create medicine "Название" --dosage "10 мг"
card-cli create contact "Имя" --phone "+7-xxx"

# Просмотр
card-cli list                    # Все карточки
card-cli list --type task        # Только задачи
card-cli show <ID>               # Детали карточки

# Поиск
card-cli search "текст"          # Поиск по тексту

# Обновление
card-cli update <ID> --status completed
card-cli delete <ID>

# Экспорт
card-cli export --format json --output backup.json

# Автоматизация
card-demo                        # Демонстрация
card-automation --run            # Запуск автоматизации
```

---

**Время прочтения:** 5 минут
**Дата создания:** 2026-01-23
**Версия:** 1.0

**Следующий шаг:** [USER-GUIDE.md](08-Программная-реализация/USER-GUIDE.md) для подробного изучения системы
