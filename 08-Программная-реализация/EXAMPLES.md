# Примеры использования карточной системы
*Уровень абстракции: α=+1 (методология)*


**Дата создания:** 2026-01-23
**Версия:** 1.0

---

## Введение

Этот документ содержит практические примеры использования карточной системы в реальных сценариях. Каждый пример включает:
- 📋 Контекст и задачу
- 💻 Код на Python
- 📊 Ожидаемый результат
- 💡 Объяснение и советы

**Связи:**
- ⇑ USER-GUIDE.md — примеры дополняют руководство пользователя
- ⇑ ТЕХНИЧЕСКИЕ-СПЕЦИФИКАЦИИ.md — примеры иллюстрируют спецификации
- ⇑ ЗАКОНЫ-В-КОДЕ.md — примеры показывают законы в действии
- ↔ card.py, card_manager.py, automation.py — используемые модули

---

## Содержание

1. [Базовые операции](#1-базовые-операции)
2. [Работа с медицинскими карточками](#2-работа-с-медицинскими-карточками)
3. [Планирование задач](#3-планирование-задач)
4. [Поиск и фильтрация](#4-поиск-и-фильтрация)
5. [Граф связей между карточками](#5-граф-связей-между-карточками)
6. [Экспорт и импорт данных](#6-экспорт-и-импорт-данных)
7. [Автоматизация](#7-автоматизация)
8. [Интеграция в приложения](#8-интеграция-в-приложения)

---

## 1. Базовые операции

### Пример 1.1: Создание и сохранение задачи

**Задача:** Создать задачу "Купить продукты" с напоминанием на завтра

```python
from pathlib import Path
from datetime import datetime, timedelta
from card import TaskCard, Priority
from card_manager import CardManager

# Инициализация менеджера
cards_dir = Path("./my_cards")
cards_dir.mkdir(exist_ok=True)
manager = CardManager(cards_dir)

# Создание задачи
task = TaskCard(
    title="Купить продукты",
    description="Молоко, хлеб, яйца, масло",
    tags=["покупки", "еда"],
    priority=Priority.MEDIUM,
    due_date=datetime.now() + timedelta(days=1)
)

# Сохранение
created_task = manager.create(task)
print(f"✅ Создана задача: {created_task.title}")
print(f"   ID: {created_task.id}")
print(f"   Срок: {created_task.due_date.strftime('%d.%m.%Y %H:%M')}")
```

**Результат:**
```
✅ Создана задача: Купить продукты
   ID: task_20260123_143022_abc123
   Срок: 24.01.2026 14:30
```

**💡 Советы:**
- ID генерируется автоматически и уникален
- Используйте понятные теги для последующего поиска
- Приоритет помогает сортировать задачи по важности

---

### Пример 1.2: Чтение и обновление карточки

**Задача:** Прочитать карточку и обновить её статус

```python
from card import CardStatus

# Читаем карточку по ID
task_id = "task_20260123_143022_abc123"
task = manager.read(task_id)

if task:
    print(f"📋 Задача: {task.title}")
    print(f"   Статус: {task.status.value}")

    # Обновляем статус
    task.status = CardStatus.IN_PROGRESS
    updated = manager.update(task)

    print(f"✅ Статус обновлён: {updated.status.value}")
else:
    print(f"❌ Задача {task_id} не найдена")
```

**Результат:**
```
📋 Задача: Купить продукты
   Статус: pending
✅ Статус обновлён: in_progress
```

---

### Пример 1.3: Удаление (архивирование) карточки

**Задача:** Заархивировать выполненную задачу

```python
# Отметить задачу как выполненную
task.status = CardStatus.COMPLETED
manager.update(task)

# Архивировать (soft delete)
manager.delete(task.id)

# Проверить статус
archived_task = manager.read(task.id)
print(f"📦 Задача '{archived_task.title}' заархивирована")
print(f"   Статус: {archived_task.status.value}")
```

**Результат:**
```
📦 Задача 'Купить продукты' заархивирована
   Статус: archived
```

**💡 Советы:**
- Удаление - это "мягкое удаление" (архивирование)
- Архивированные карточки остаются доступными
- Для полного удаления файл нужно удалить вручную

---

## 2. Работа с медицинскими карточками

### Пример 2.1: Карточка лекарства с расписанием

**Задача:** Создать карточку для ежедневного лекарства с напоминаниями

```python
from card import MedicineCard

# Создание карточки лекарства
medicine = MedicineCard(
    title="Эналаприл 10 мг",
    description="Снижение артериального давления",
    tags=["здоровье", "сердце", "ежедневно"],
    dosage="10 мг",
    administration="перорально с водой",
    frequency="1 раз в день",
    schedule=["08:00"],  # Время приёма
    side_effects="Возможна сухость во рту, головокружение",
    prescribing_doctor="Кардиолог Иванова А.С."
)

created_medicine = manager.create(medicine)
print(f"💊 Создано лекарство: {created_medicine.title}")
print(f"   Приём: {created_medicine.frequency} в {', '.join(created_medicine.schedule)}")
print(f"   Врач: {created_medicine.prescribing_doctor}")
```

**Результат:**
```
💊 Создано лекарство: Эналаприл 10 мг
   Приём: 1 раз в день в 08:00
   Врач: Кардиолог Иванова А.С.
```

---

### Пример 2.2: Связывание лекарства с задачей

**Задача:** Создать задачу напоминания о приёме лекарства

```python
# Создать задачу-напоминание
reminder_task = TaskCard(
    title="Принять Эналаприл",
    description="Утренний приём лекарства от давления",
    tags=["здоровье", "лекарство", "утро"],
    priority=Priority.HIGH,
    due_date=datetime.now().replace(hour=8, minute=0, second=0)
)

created_reminder = manager.create(reminder_task)

# Связать задачу с лекарством
manager.link_cards(created_reminder.id, created_medicine.id)

print(f"🔗 Связаны карточки:")
print(f"   Задача: {created_reminder.title}")
print(f"   Лекарство: {created_medicine.title}")

# Проверить связи
linked = manager.get_linked_cards(created_reminder.id)
print(f"   Найдено связей: {len(linked)}")
```

**Результат:**
```
🔗 Связаны карточки:
   Задача: Принять Эналаприл
   Лекарство: Эналаприл 10 мг
   Найдено связей: 1
```

---

## 3. Планирование задач

### Пример 3.1: Еженедельный план покупок

**Задача:** Создать список покупок на неделю

```python
from card import ShoppingCard

# Создать карточку покупок
shopping = ShoppingCard(
    title="Покупки на неделю",
    description="Продукты на 23-29 января",
    tags=["покупки", "еда", "неделя"],
    store="Магнит на площади",
    estimated_cost=3500.0
)

# Добавить товары
items = [
    ("Молоко 3.2%", 2, "л", False),
    ("Хлеб Бородинский", 1, "шт", False),
    ("Яйца С1", 10, "шт", False),
    ("Масло сливочное", 200, "г", False),
    ("Картофель", 2, "кг", False),
    ("Морковь", 1, "кг", False),
    ("Лук репчатый", 1, "кг", False)
]

for name, quantity, unit, checked in items:
    shopping.add_item(name, quantity, unit, checked)

created_shopping = manager.create(shopping)
print(f"🛒 Создан список покупок: {created_shopping.title}")
print(f"   Магазин: {created_shopping.store}")
print(f"   Товаров: {len(created_shopping.items)}")
print(f"   Бюджет: {created_shopping.estimated_cost} руб")

# Вывести список
print("\n📝 Список покупок:")
for i, item in enumerate(created_shopping.items, 1):
    status = "✓" if item["checked"] else " "
    print(f"   [{status}] {i}. {item['name']} - {item['quantity']} {item['unit']}")
```

**Результат:**
```
🛒 Создан список покупок: Покупки на неделю
   Магазин: Магнит на площади
   Товаров: 7
   Бюджет: 3500.0 руб

📝 Список покупок:
   [ ] 1. Молоко 3.2% - 2.0 л
   [ ] 2. Хлеб Бородинский - 1.0 шт
   [ ] 3. Яйца С1 - 10.0 шт
   [ ] 4. Масло сливочное - 200.0 г
   [ ] 5. Картофель - 2.0 кг
   [ ] 6. Морковь - 1.0 кг
   [ ] 7. Лук репчатый - 1.0 кг
```

---

### Пример 3.2: Планирование встречи

**Задача:** Запланировать визит к врачу

```python
from card import AppointmentCard

# Создать встречу
appointment = AppointmentCard(
    title="Приём у кардиолога",
    description="Плановый осмотр, обсуждение результатов анализов",
    tags=["здоровье", "врач", "кардиолог"],
    appointment_date=datetime(2026, 1, 30, 10, 30),
    location="Поликлиника №5, каб. 208",
    duration_minutes=30,
    participants=["Кардиолог Иванова А.С."]
)

created_appointment = manager.create(appointment)
print(f"📅 Запланирована встреча: {created_appointment.title}")
print(f"   Дата: {created_appointment.appointment_date.strftime('%d.%m.%Y %H:%M')}")
print(f"   Место: {created_appointment.location}")
print(f"   Длительность: {created_appointment.duration_minutes} мин")
print(f"   Участники: {', '.join(created_appointment.participants)}")
```

**Результат:**
```
📅 Запланирована встреча: Приём у кардиолога
   Дата: 30.01.2026 10:30
   Место: Поликлиника №5, каб. 208
   Длительность: 30 мин
   Участники: Кардиолог Иванова А.С.
```

---

## 4. Поиск и фильтрация

### Пример 4.1: Поиск по тегам

**Задача:** Найти все карточки, связанные со здоровьем

```python
# Поиск по тегу
health_cards = manager.search(tags=["здоровье"])

print(f"🔍 Найдено карточек со здоровьем: {len(health_cards)}")
for card in health_cards:
    card_type = card.type.value if hasattr(card.type, 'value') else str(card.type)
    print(f"   [{card_type}] {card.title}")
```

**Результат:**
```
🔍 Найдено карточек со здоровьем: 3
   [medicine] Эналаприл 10 мг
   [task] Принять Эналаприл
   [appointment] Приём у кардиолога
```

---

### Пример 4.2: Поиск по типу и статусу

**Задача:** Найти все активные задачи

```python
from card import CardType

# Поиск активных задач
all_cards = manager.search()
active_tasks = [
    c for c in all_cards
    if c.type == CardType.TASK and c.status != CardStatus.ARCHIVED and c.status != CardStatus.COMPLETED
]

print(f"📋 Активные задачи: {len(active_tasks)}")
for task in active_tasks:
    priority_icon = {
        Priority.LOW: "📋",
        Priority.MEDIUM: "⚠️",
        Priority.HIGH: "🔥",
        Priority.URGENT: "🚨"
    }.get(task.priority, "📋")

    status = task.status.value if hasattr(task.status, 'value') else str(task.status)
    print(f"   {priority_icon} [{status}] {task.title}")
```

**Результат:**
```
📋 Активные задачи: 2
   ⚠️ [in_progress] Купить продукты
   🔥 [pending] Принять Эналаприл
```

---

### Пример 4.3: Поиск с множественными критериями

**Задача:** Найти высокоприоритетные задачи со здоровьем на эту неделю

```python
from datetime import datetime, timedelta

# Определить границы недели
now = datetime.now()
week_end = now + timedelta(days=7)

# Поиск
all_cards = manager.search(tags=["здоровье"])
filtered_tasks = [
    c for c in all_cards
    if (c.type == CardType.TASK and
        hasattr(c, 'priority') and c.priority in [Priority.HIGH, Priority.URGENT] and
        hasattr(c, 'due_date') and c.due_date and
        now <= c.due_date <= week_end)
]

print(f"🎯 Важные задачи по здоровью на неделю: {len(filtered_tasks)}")
for task in filtered_tasks:
    days_left = (task.due_date - now).days
    print(f"   🔥 {task.title}")
    print(f"      Срок: через {days_left} дн. ({task.due_date.strftime('%d.%m %H:%M')})")
```

**Результат:**
```
🎯 Важные задачи по здоровью на неделю: 1
   🔥 Принять Эналаприл
      Срок: через 0 дн. (23.01 08:00)
```

---

## 5. Граф связей между карточками

### Пример 5.1: Создание сети связанных карточек

**Задача:** Создать связанный кластер "Здоровье"

```python
from card import ContactCard

# 1. Создать контакт врача
doctor = ContactCard(
    title="Кардиолог Иванова А.С.",
    description="Лечащий врач",
    tags=["здоровье", "врачи", "кардиолог"],
    phone="+7 912 345-67-89",
    email="ivanova@clinic5.ru",
    address="Поликлиника №5, каб. 208"
)
created_doctor = manager.create(doctor)

# 2. Связать врача с лекарством и встречей
manager.link_cards(created_medicine.id, created_doctor.id)
manager.link_cards(created_appointment.id, created_doctor.id)

# 3. Визуализировать сеть связей
print(f"🕸️ Сеть связей карточки '{created_medicine.title}':")
linked_cards = manager.get_linked_cards(created_medicine.id)

for linked_card in linked_cards:
    card_type = linked_card.type.value if hasattr(linked_card.type, 'value') else str(linked_card.type)
    print(f"   → [{card_type}] {linked_card.title}")
```

**Результат:**
```
🕸️ Сеть связей карточки 'Эналаприл 10 мг':
   → [task] Принять Эналаприл
   → [contact] Кардиолог Иванова А.С.
```

---

### Пример 5.2: Навигация по графу связей

**Задача:** Найти все карточки, связанные с врачом (прямо и косвенно)

```python
def get_all_related_cards(manager, card_id, visited=None):
    """Рекурсивный обход графа связей (BFS)"""
    if visited is None:
        visited = set()

    if card_id in visited:
        return []

    visited.add(card_id)
    related = []

    # Получить прямые связи
    linked = manager.get_linked_cards(card_id)
    related.extend(linked)

    # Рекурсивно получить связи связанных карточек
    for linked_card in linked:
        related.extend(get_all_related_cards(manager, linked_card.id, visited))

    return related

# Получить всю сеть врача
all_related = get_all_related_cards(manager, created_doctor.id)

print(f"🌐 Вся сеть связей '{created_doctor.title}': {len(all_related)} карточек")
for card in all_related:
    card_type = card.type.value if hasattr(card.type, 'value') else str(card.type)
    print(f"   • [{card_type}] {card.title}")
```

**Результат:**
```
🌐 Вся сеть связей 'Кардиолог Иванова А.С.': 3 карточек
   • [medicine] Эналаприл 10 мг
   • [appointment] Приём у кардиолога
   • [task] Принять Эналаприл
```

---

## 6. Экспорт и импорт данных

### Пример 6.1: Экспорт в JSON

**Задача:** Создать резервную копию всех карточек в JSON

```python
from export_import import CardExporter

exporter = CardExporter(manager)

# Экспорт в JSON
backup_file = Path("./backup_cards.json")
count = exporter.export_to_json(backup_file)

print(f"💾 Экспортировано карточек: {count}")
print(f"   Файл: {backup_file}")
print(f"   Размер: {backup_file.stat().st_size / 1024:.1f} KB")
```

**Результат:**
```
💾 Экспортировано карточек: 6
   Файл: ./backup_cards.json
   Размер: 12.3 KB
```

---

### Пример 6.2: Экспорт в CSV для анализа

**Задача:** Экспортировать задачи в CSV для анализа в Excel

```python
# Экспорт в CSV
csv_file = Path("./tasks_report.csv")
count = exporter.export_to_csv(csv_file)

print(f"📊 Экспортировано в CSV: {count} карточек")
print(f"   Файл: {csv_file}")
print(f"   Формат: ID, Type, Title, Status, Tags, Created, Updated")
```

**Результат:**
```
📊 Экспортировано в CSV: 6 карточек
   Файл: ./tasks_report.csv
   Формат: ID, Type, Title, Status, Tags, Created, Updated
```

---

### Пример 6.3: Полный backup в ZIP

**Задача:** Создать полную резервную копию системы

```python
# Создать ZIP-архив
archive_file = Path("./full_backup.zip")
count = exporter.export_to_archive(archive_file)

print(f"📦 Создан архив: {archive_file}")
print(f"   Карточек: {count}")
print(f"   Размер: {archive_file.stat().st_size / 1024:.1f} KB")
```

**Результат:**
```
📦 Создан архив: full_backup.zip
   Карточек: 6
   Размер: 8.7 KB
```

---

## 7. Автоматизация

### Пример 7.1: Автоматическая проверка просроченных задач

**Задача:** Настроить ежедневную проверку просроченных задач

```python
from automation import CardAutomation

# Инициализация автоматизации
automation = CardAutomation(cards_dir)

# Запустить проверку просроченных задач
overdue_reminders = automation.check_overdue_tasks()

print(f"⏰ Проверка просроченных задач:")
print(f"   Найдено напоминаний: {len(overdue_reminders)}")

for reminder in overdue_reminders:
    print(f"   {reminder}")
```

**Результат:**
```
⏰ Проверка просроченных задач:
   Найдено напоминаний: 0
```

---

### Пример 7.2: Напоминания о лекарствах

**Задача:** Получить напоминания о приёме лекарств на текущее время

```python
# Проверить напоминания о лекарствах
medicine_reminders = automation.check_medicine_reminders()

print(f"💊 Напоминания о лекарствах:")
print(f"   Найдено: {len(medicine_reminders)}")

for reminder in medicine_reminders:
    print(f"   {reminder}")
```

**Результат:**
```
💊 Напоминания о лекарствах:
   Найдено: 1
   🔥 [MEDICINE] Эналаприл 10 мг: Время приёма: 08:00. Дозировка: 10 мг
```

---

### Пример 7.3: Автоматическое архивирование

**Задача:** Архивировать карточки, завершённые более 30 дней назад

```python
# Архивировать старые завершённые карточки
archived_count = automation.archive_old_completed_cards(days_old=30)

print(f"📦 Автоматическое архивирование:")
print(f"   Заархивировано: {archived_count} карточек")
```

**Результат:**
```
📦 Автоматическое архивирование:
   Заархивировано: 0 карточек
```

---

### Пример 7.4: Еженедельный отчёт

**Задача:** Сгенерировать статистику за неделю

```python
# Получить еженедельный отчёт
report = automation.generate_weekly_report()

print(f"📈 Еженедельный отчёт:")
print(f"   Период: {report['period']}")
print(f"   Создано карточек: {report['total_created']}")
print(f"   По типам:")
for card_type, count in report['by_type'].items():
    print(f"      • {card_type}: {count}")
print(f"   Завершено задач: {report['completed_tasks']}")
print(f"   Просроченных задач: {report['overdue_tasks']}")
print(f"   Активных лекарств: {report['active_medicines']}")
```

**Результат:**
```
📈 Еженедельный отчёт:
   Период: 2026-01-16 — 2026-01-23
   Создано карточек: 6
   По типам:
      • task: 2
      • medicine: 1
      • shopping: 1
      • appointment: 1
      • contact: 1
   Завершено задач: 1
   Просроченных задач: 0
   Активных лекарств: 1
```

---

## 8. Интеграция в приложения

### Пример 8.1: Простой веб-сервер

**Задача:** Создать REST API для карточной системы

```python
from flask import Flask, jsonify, request
from pathlib import Path

app = Flask(__name__)
manager = CardManager(Path("./my_cards"))

@app.route('/cards', methods=['GET'])
def get_cards():
    """Получить все карточки"""
    cards = manager.search()
    return jsonify([{
        'id': c.id,
        'type': c.type.value if hasattr(c.type, 'value') else str(c.type),
        'title': c.title,
        'status': c.status.value if hasattr(c.status, 'value') else str(c.status)
    } for c in cards])

@app.route('/cards/<card_id>', methods=['GET'])
def get_card(card_id):
    """Получить карточку по ID"""
    card = manager.read(card_id)
    if card:
        return jsonify({
            'id': card.id,
            'type': card.type.value if hasattr(card.type, 'value') else str(card.type),
            'title': card.title,
            'description': card.description,
            'status': card.status.value if hasattr(card.status, 'value') else str(card.status),
            'tags': card.tags
        })
    return jsonify({'error': 'Card not found'}), 404

@app.route('/search', methods=['GET'])
def search_cards():
    """Поиск карточек по тегам"""
    tags = request.args.get('tags', '').split(',')
    cards = manager.search(tags=tags if tags[0] else None)
    return jsonify([{
        'id': c.id,
        'title': c.title,
        'tags': c.tags
    } for c in cards])

if __name__ == '__main__':
    app.run(debug=True, port=5000)
```

**Использование:**
```bash
# Запустить сервер
python app.py

# Получить все карточки
curl http://localhost:5000/cards

# Поиск по тегам
curl http://localhost:5000/search?tags=здоровье,лекарство
```

---

### Пример 8.2: Telegram-бот

**Задача:** Создать Telegram-бота для управления карточками

```python
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

manager = CardManager(Path("./my_cards"))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /start"""
    await update.message.reply_text(
        "👋 Привет! Я бот для управления карточками.\n"
        "Команды:\n"
        "/list - Показать все карточки\n"
        "/search <тег> - Поиск по тегу\n"
        "/create - Создать новую карточку"
    )

async def list_cards(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /list - показать все карточки"""
    cards = manager.search()

    if not cards:
        await update.message.reply_text("📭 Карточек нет")
        return

    message = f"📋 Всего карточек: {len(cards)}\n\n"
    for card in cards[:10]:  # Первые 10
        card_type = card.type.value if hasattr(card.type, 'value') else str(card.type)
        message += f"• [{card_type}] {card.title}\n"

    await update.message.reply_text(message)

async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /search <тег> - поиск по тегу"""
    if not context.args:
        await update.message.reply_text("❌ Укажите тег: /search здоровье")
        return

    tag = context.args[0]
    cards = manager.search(tags=[tag])

    if not cards:
        await update.message.reply_text(f"🔍 Карточек с тегом '{tag}' не найдено")
        return

    message = f"🔍 Найдено: {len(cards)}\n\n"
    for card in cards:
        card_type = card.type.value if hasattr(card.type, 'value') else str(card.type)
        message += f"• [{card_type}] {card.title}\n"

    await update.message.reply_text(message)

def main():
    """Запуск бота"""
    # Замените YOUR_BOT_TOKEN на токен вашего бота
    app = Application.builder().token("YOUR_BOT_TOKEN").build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("list", list_cards))
    app.add_handler(CommandHandler("search", search))

    print("🤖 Бот запущен...")
    app.run_polling()

if __name__ == '__main__':
    main()
```

---

## Заключение

Эти примеры демонстрируют основные возможности карточной системы:

✅ **Создание и управление** всеми 7 типами карточек
✅ **Поиск и фильтрация** с множественными критериями
✅ **Граф связей** для организации информации
✅ **Экспорт/импорт** для backup и миграции
✅ **Автоматизация** рутинных задач
✅ **Интеграция** в другие приложения

**Дальнейшее развитие:**
- Интеграция с календарём (Google Calendar, iCal)
- Синхронизация между устройствами
- Мобильное приложение
- Голосовые команды через умных ассистентов
- Машинное обучение для автоматической категоризации

---

## См. также

**Документация и руководства:**
- ⇑ [USER-GUIDE.md](../02-Информационная-система/USER-GUIDE.md) (α=-3) — полное руководство пользователя
- ⇑ [API-REFERENCE.md](API-REFERENCE.md) (α=-2) — полная API документация
- ⇑ [QUICK-START.md](../QUICK-START.md) (α=-1) — быстрый старт за 5 минут

**Программная реализация:**
- ↔ [README.md](README.md) (α=-4) — обзор программной реализации
- ↔ automation.py — система автоматизации
- ↔ cli.py — интерфейс командной строки

**Инструменты и примеры:**
- ↔ [tools/EXAMPLES.md](../tools/EXAMPLES.md) — примеры работы с инструментами
- ↔ [TROUBLESHOOTING.md](../TROUBLESHOOTING.md) (α=-1) — решение проблем

**Методология и практики:**
- ⇑ [ДОКУМЕНТАЦИЯ.md](../ДОКУМЕНТАЦИЯ.md) — методология ⇑⇓↔
- ↔ [BEST-PRACTICES.md](../BEST-PRACTICES.md) (α=-1) — лучшие практики

---

**Версия:** 1.0
**Дата:** 2026-01-23
**Статус:** Активный документ (обновляется при добавлении новых примеров)
