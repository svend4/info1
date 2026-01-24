# API Reference — Карточная система

**Уровень абстракции:** α=-2 (шаблоны и API)
**Дата создания:** 2026-01-23
**Версия:** 1.0

---

## Введение

Этот документ содержит полную справку по API карточной системы. Предназначен для разработчиков, которые хотят интегрировать карточную систему в свои приложения или расширить её функциональность.

**Связи:**
- ⇑ ТЕХНИЧЕСКИЕ-СПЕЦИФИКАЦИИ.md — детализация технических спецификаций
- ⇑ ЗАКОНЫ-В-КОДЕ.md — показывает как API реализует законы
- ⇓ EXAMPLES.md — примеры использования API
- ↔ card.py, card_manager.py — реализация API

---

## Содержание

1. [Модель данных](#модель-данных)
2. [Card — базовый класс](#card--базовый-класс)
3. [Специализированные карточки](#специализированные-карточки)
4. [CardManager — управление карточками](#cardmanager--управление-карточками)
5. [CardIndex — индексирование](#cardindex--индексирование)
6. [Экспорт и импорт](#экспорт-и-импорт)
7. [Автоматизация](#автоматизация)
8. [CLI](#cli)

---

## Модель данных

### CardType (Enum)

Типы карточек в системе.

```python
class CardType(Enum):
    TASK = "task"             # Задача
    MEDICINE = "medicine"     # Лекарство
    RECIPE = "recipe"         # Рецепт
    SHOPPING = "shopping"     # Покупки
    CONTACT = "contact"       # Контакт
    APPOINTMENT = "appointment"  # Встреча
    NOTE = "note"             # Заметка
```

### CardStatus (Enum)

Статусы карточек.

```python
class CardStatus(Enum):
    PENDING = "pending"           # Ожидает выполнения
    IN_PROGRESS = "in_progress"   # В процессе
    COMPLETED = "completed"        # Завершена
    CANCELLED = "cancelled"        # Отменена
    ARCHIVED = "archived"          # Заархивирована
```

### Priority (Enum)

Приоритеты задач.

```python
class Priority(Enum):
    LOW = "low"           # Низкий
    MEDIUM = "medium"     # Средний
    HIGH = "high"         # Высокий
    URGENT = "urgent"     # Срочный
```

---

## Card — базовый класс

Базовый класс для всех карточек.

### Поля

```python
@dataclass
class Card:
    id: str                          # Уникальный ID (card_YYYYMMDD_HHMMSS_RAND)
    type: CardType                   # Тип карточки
    title: str                       # Заголовок
    description: str = ""            # Описание
    tags: List[str] = field(default_factory=list)  # Теги
    status: CardStatus = CardStatus.PENDING  # Статус
    priority: Priority = Priority.MEDIUM     # Приоритет
    linked_cards: List[str] = field(default_factory=list)  # ID связанных карточек
    created_at: datetime = field(default_factory=datetime.now)  # Дата создания
    updated_at: datetime = field(default_factory=datetime.now)  # Дата обновления
```

### Методы

#### `generate_id() -> str` (статический)

Генерирует уникальный ID для карточки.

**Возвращает:**
- `str`: ID в формате `card_YYYYMMDD_HHMMSS_RANDOM`

**Пример:**
```python
card_id = Card.generate_id()
# "card_20260123_143022_a1b2c3"
```

#### `to_yaml_frontmatter() -> str`

Преобразует карточку в YAML frontmatter.

**Возвращает:**
- `str`: YAML представление метаданных карточки

**Пример:**
```python
card = TaskCard(title="Купить молоко")
yaml = card.to_yaml_frontmatter()
# ---
# id: card_20260123_143022_a1b2c3
# type: task
# title: Купить молоко
# ...
# ---
```

#### `to_markdown() -> str`

Преобразует карточку в полный Markdown документ.

**Возвращает:**
- `str`: Markdown документ с YAML frontmatter + описанием

**Пример:**
```python
card = TaskCard(title="Купить молоко", description="2 литра 3.2%")
md = card.to_markdown()
# ---
# [YAML frontmatter]
# ---
#
# 2 литра 3.2%
```

#### `from_markdown(file_path: Path) -> Card` (статический)

Загружает карточку из Markdown файла.

**Параметры:**
- `file_path` (Path): Путь к файлу

**Возвращает:**
- `Card`: Карточка соответствующего типа

**Исключения:**
- `ValueError`: Если файл имеет неверный формат

**Пример:**
```python
card = Card.from_markdown(Path("cards/task_123.md"))
```

---

## Специализированные карточки

### TaskCard

Карточка задачи.

**Дополнительные поля:**
```python
@dataclass
class TaskCard(Card):
    due_date: Optional[datetime] = None     # Срок выполнения
    estimated_time: Optional[int] = None    # Оценка времени (минуты)
    actual_time: Optional[int] = None       # Фактическое время
    subtasks: List[Dict] = field(default_factory=list)  # Подзадачи
    assigned_robot: Optional[str] = None    # Назначенный робот
```

**Методы:**

```python
def add_subtask(self, title: str, completed: bool = False):
    """Добавить подзадачу"""

def complete_subtask(self, index: int):
    """Отметить подзадачу как выполненную"""

def get_progress(self) -> float:
    """Получить прогресс выполнения (0.0 - 1.0)"""
```

---

### MedicineCard

Карточка лекарства.

**Дополнительные поля:**
```python
@dataclass
class MedicineCard(Card):
    dosage: str = ""                # Дозировка (например, "10 мг")
    administration: str = ""         # Способ приёма
    frequency: str = ""              # Частота приёма
    schedule: List[str] = field(default_factory=list)  # Расписание ["08:00", "20:00"]
    side_effects: str = ""           # Побочные эффекты
    prescribing_doctor: str = ""     # Назначивший врач
```

---

### RecipeCard

Карточка рецепта.

**Дополнительные поля:**
```python
@dataclass
class RecipeCard(Card):
    ingredients: List[Dict] = field(default_factory=list)  # Ингредиенты
    instructions: str = ""           # Инструкции приготовления
    cooking_time: Optional[int] = None  # Время приготовления (мин)
    servings: Optional[int] = None   # Количество порций
    difficulty: str = "medium"       # Сложность: easy/medium/hard
```

**Методы:**

```python
def add_ingredient(self, name: str, quantity: float, unit: str):
    """Добавить ингредиент"""
```

---

### ShoppingCard

Карточка покупок.

**Дополнительные поля:**
```python
@dataclass
class ShoppingCard(Card):
    items: List[Dict] = field(default_factory=list)  # Товары
    store: str = ""                  # Магазин
    estimated_cost: float = 0.0      # Примерная стоимость
```

**Методы:**

```python
def add_item(self, name: str, quantity: float = 1, unit: str = "", checked: bool = False):
    """Добавить товар в список"""

def check_item(self, index: int):
    """Отметить товар как купленный"""

def get_total_items(self) -> int:
    """Получить общее количество товаров"""

def get_checked_items(self) -> int:
    """Получить количество купленных товаров"""
```

---

### ContactCard

Карточка контакта.

**Дополнительные поля:**
```python
@dataclass
class ContactCard(Card):
    phone: str = ""                  # Телефон
    email: str = ""                  # Email
    address: str = ""                # Адрес
    relationship: str = ""           # Отношения (врач, родственник, мастер)
    emergency_contact: bool = False  # Контакт для экстренных случаев
```

---

### AppointmentCard

Карточка встречи.

**Дополнительные поля:**
```python
@dataclass
class AppointmentCard(Card):
    appointment_date: Optional[datetime] = None  # Дата и время встречи
    location: str = ""               # Место встречи
    duration_minutes: int = 60       # Длительность (минуты)
    participants: List[str] = field(default_factory=list)  # Участники
    reminder_minutes: int = 60       # Напомнить за X минут
```

---

### NoteCard

Карточка заметки.

**Дополнительные поля:**
```python
@dataclass
class NoteCard(Card):
    category: str = "general"        # Категория
    attachments: List[str] = field(default_factory=list)  # Вложения (пути к файлам)
```

---

## CardManager — управление карточками

Основной класс для работы с карточками (CRUD + поиск + граф связей).

### Инициализация

```python
manager = CardManager(cards_dir: Path)
```

**Параметры:**
- `cards_dir` (Path): Директория для хранения карточек

---

### CRUD операции

#### `create(card: Card) -> Card`

Создать новую карточку.

**Параметры:**
- `card` (Card): Карточка для создания

**Возвращает:**
- `Card`: Созданная карточка

**Исключения:**
- `ValueError`: Если карточка с таким ID уже существует

**Пример:**
```python
task = TaskCard(title="Купить молоко")
created = manager.create(task)
```

---

#### `read(card_id: str) -> Optional[Card]`

Прочитать карточку по ID.

**Параметры:**
- `card_id` (str): ID карточки

**Возвращает:**
- `Card | None`: Карточка или None, если не найдена

**Пример:**
```python
card = manager.read("card_20260123_143022_a1b2c3")
if card:
    print(card.title)
```

---

#### `update(card: Card) -> Card`

Обновить существующую карточку.

**Параметры:**
- `card` (Card): Карточка с обновлёнными данными

**Возвращает:**
- `Card`: Обновлённая карточка

**Исключения:**
- `ValueError`: Если карточка не найдена

**Пример:**
```python
card = manager.read(card_id)
card.title = "Новый заголовок"
updated = manager.update(card)
```

---

#### `delete(card_id: str) -> bool`

Удалить (заархивировать) карточку.

**Параметры:**
- `card_id` (str): ID карточки

**Возвращает:**
- `bool`: True если успешно

**Примечание:** По умолчанию выполняется "мягкое удаление" (soft delete) — карточка архивируется, а не удаляется физически.

**Пример:**
```python
success = manager.delete(card_id)
```

---

### Поиск

#### `search(**filters) -> List[Card]`

Поиск карточек по различным критериям.

**Параметры:**
- `query` (str, optional): Текстовый поиск по title и description
- `tags` (List[str], optional): Поиск по тегам (AND логика)
- `card_type` (CardType, optional): Фильтр по типу
- `status` (CardStatus, optional): Фильтр по статусу
- `limit` (int, optional): Максимальное количество результатов (default: 100)

**Возвращает:**
- `List[Card]`: Список найденных карточек

**Примеры:**
```python
# Поиск по тексту
cards = manager.search(query="молоко")

# Поиск по тегам
health_cards = manager.search(tags=["здоровье"])

# Поиск по типу и статусу
active_tasks = manager.search(
    card_type=CardType.TASK,
    status=CardStatus.PENDING
)

# Комбинированный поиск
urgent_health = manager.search(
    tags=["здоровье"],
    query="лекарство",
    limit=10
)
```

---

### Граф связей

#### `link_cards(card_id_1: str, card_id_2: str) -> bool`

Создать двунаправленную связь между карточками.

**Параметры:**
- `card_id_1` (str): ID первой карточки
- `card_id_2` (str): ID второй карточки

**Возвращает:**
- `bool`: True если успешно

**Пример:**
```python
# Связать задачу с лекарством
manager.link_cards(task.id, medicine.id)
```

---

#### `unlink_cards(card_id_1: str, card_id_2: str) -> bool`

Удалить связь между карточками.

**Параметры:**
- `card_id_1` (str): ID первой карточки
- `card_id_2` (str): ID второй карточки

**Возвращает:**
- `bool`: True если успешно

**Пример:**
```python
manager.unlink_cards(task.id, medicine.id)
```

---

#### `get_linked_cards(card_id: str) -> List[Card]`

Получить все карточки, связанные с данной.

**Параметры:**
- `card_id` (str): ID карточки

**Возвращает:**
- `List[Card]`: Список связанных карточек

**Пример:**
```python
linked = manager.get_linked_cards(medicine.id)
for card in linked:
    print(f"Связанная карточка: {card.title}")
```

---

### Статистика

#### `get_stats() -> Dict`

Получить статистику по карточкам.

**Возвращает:**
- `Dict`: Словарь со статистикой

**Пример:**
```python
stats = manager.get_stats()
# {
#   "total": 42,
#   "by_type": {"task": 15, "medicine": 5, ...},
#   "by_status": {"pending": 10, "completed": 20, ...},
#   "by_priority": {"high": 5, "medium": 8, ...}
# }
```

---

### Индексирование

#### `rebuild_index()`

Перестроить индексы с нуля.

**Использование:**
Вызывайте эту функцию если вы вручную изменили файлы карточек и хотите обновить индексы.

**Пример:**
```python
manager.rebuild_index()
```

---

## Экспорт и импорт

### CardExporter

Класс для экспорта карточек в различные форматы.

#### Инициализация

```python
from export_import import CardExporter

exporter = CardExporter(card_manager: CardManager)
```

#### `export_to_json(output_file: Path) -> int`

Экспортировать карточки в JSON.

**Параметры:**
- `output_file` (Path): Путь к выходному файлу

**Возвращает:**
- `int`: Количество экспортированных карточек

**Пример:**
```python
count = exporter.export_to_json(Path("backup.json"))
print(f"Экспортировано: {count} карточек")
```

---

#### `export_to_csv(output_file: Path) -> int`

Экспортировать карточки в CSV (для анализа в Excel).

**Параметры:**
- `output_file` (Path): Путь к выходному файлу

**Возвращает:**
- `int`: Количество экспортированных карточек

**Пример:**
```python
count = exporter.export_to_csv(Path("cards_export.csv"))
```

---

#### `export_to_archive(output_file: Path) -> int`

Создать ZIP-архив со всеми карточками.

**Параметры:**
- `output_file` (Path): Путь к ZIP файлу

**Возвращает:**
- `int`: Количество экспортированных карточек

**Пример:**
```python
count = exporter.export_to_archive(Path("backup.zip"))
```

---

### CardImporter

Класс для импорта карточек.

#### Инициализация

```python
from export_import import CardImporter

importer = CardImporter(card_manager: CardManager)
```

#### `import_from_json(input_file: Path, overwrite: bool = False) -> Dict`

Импортировать карточки из JSON.

**Параметры:**
- `input_file` (Path): Путь к JSON файлу
- `overwrite` (bool): Перезаписать существующие карточки

**Возвращает:**
- `Dict`: Статистика импорта
  - `imported`: Количество импортированных карточек
  - `skipped`: Количество пропущенных (уже существуют)
  - `errors`: Количество ошибок

**Пример:**
```python
stats = importer.import_from_json(Path("backup.json"))
print(f"Импортировано: {stats['imported']}")
print(f"Пропущено: {stats['skipped']}")
print(f"Ошибок: {stats['errors']}")
```

---

## Автоматизация

### CardAutomation

Менеджер автоматизации для выполнения рутинных задач.

#### Инициализация

```python
from automation import CardAutomation

automation = CardAutomation(
    card_dir: Path,
    backup_dir: Optional[Path] = None
)
```

**Параметры:**
- `card_dir` (Path): Директория с карточками
- `backup_dir` (Path, optional): Директория для резервных копий

---

#### `check_overdue_tasks() -> List[Reminder]`

Проверить просроченные задачи.

**Возвращает:**
- `List[Reminder]`: Список напоминаний о просроченных задачах

**Пример:**
```python
reminders = automation.check_overdue_tasks()
for reminder in reminders:
    print(reminder)  # 🔥 [TASK_OVERDUE] Купить молоко: Задача просрочена на 2 дн.
```

---

#### `check_medicine_reminders() -> List[Reminder]`

Проверить напоминания о приёме лекарств.

**Возвращает:**
- `List[Reminder]`: Список напоминаний о лекарствах

**Пример:**
```python
reminders = automation.check_medicine_reminders()
for reminder in reminders:
    print(reminder)  # 🔥 [MEDICINE] Эналаприл 10 мг: Время приёма: 08:00
```

---

#### `archive_old_completed_cards(days_old: int = 30) -> int`

Архивировать старые завершённые карточки.

**Параметры:**
- `days_old` (int): Возраст карточки в днях для архивирования

**Возвращает:**
- `int`: Количество заархивированных карточек

**Пример:**
```python
count = automation.archive_old_completed_cards(days_old=60)
print(f"Заархивировано: {count} карточек")
```

---

#### `create_backup(prefix: str = "auto") -> Optional[Path]`

Создать резервную копию.

**Параметры:**
- `prefix` (str): Префикс имени файла

**Возвращает:**
- `Path | None`: Путь к созданному backup файлу или None при ошибке

**Пример:**
```python
backup_file = automation.create_backup(prefix="weekly")
print(f"Backup создан: {backup_file}")
```

---

#### `generate_weekly_report() -> Dict`

Сгенерировать еженедельный отчёт.

**Возвращает:**
- `Dict`: Статистика за неделю

**Пример:**
```python
report = automation.generate_weekly_report()
print(f"Создано карточек: {report['total_created']}")
print(f"Завершено задач: {report['completed_tasks']}")
```

---

#### `run_automation_cycle() -> Dict`

Запустить полный цикл автоматизации.

**Возвращает:**
- `Dict`: Результаты выполнения всех автоматических задач

**Пример:**
```python
results = automation.run_automation_cycle()
print(f"Выполнено задач: {len(results['tasks_run'])}")
print(f"Напоминания: {len(results['reminders'])}")
```

---

## CLI

### Основные команды

```bash
# Создать карточку
python cli.py create -t task --title "Купить молоко" --tags еда,покупки

# Показать список карточек
python cli.py list

# Показать карточку
python cli.py show <card_id>

# Обновить карточку
python cli.py update <card_id> --title "Новое название"

# Удалить карточку
python cli.py delete <card_id>

# Поиск
python cli.py search --tags здоровье --query лекарство

# Связать карточки
python cli.py link <card_id_1> <card_id_2>

# Статистика
python cli.py stats
```

См. `python cli.py --help` для полного списка команд.

---

## Реализованные законы

API реализует все 12 универсальных законов:

1. **Закон сохранения информации**: Soft delete (архивирование вместо удаления)
2. **Закон SSOT**: Уникальные ID, ссылки по ID
3. **Закон минимизации связности**: CardManager не зависит от Card напрямую
4. **Закон максимизации когезии**: Каждый класс имеет одну ответственность
5. **Закон обратимости**: Export ↔ Import
6. **Закон предсказуемости**: Детерминированное API
7. **Закон градуального усложнения**: Простой базовый Card → сложные специализации
8. **Закон композиционности**: Карточки можно связывать
9. **Закон локальности изменений**: Изменения в Card не влияют на CardManager
10. **Закон явности**: Explicit > Implicit во всём API
11. **Закон устойчивости к ошибкам**: Проверка всех входных данных
12. **Закон измеримости**: get_stats(), тесты

См. ЗАКОНЫ-В-КОДЕ.md для деталей реализации каждого закона.

---

## Тестирование

### Юнит-тесты

```bash
python -m pytest test_card_system.py -v
```

21 юнит-тест, покрывает:
- Создание всех 7 типов карточек
- CRUD операции
- Поиск и фильтрацию
- Граф связей
- Граничные случаи

### Интеграционные тесты

```bash
python -m pytest test_integration.py -v
```

4 интеграционных теста, проверяет:
- Полный жизненный цикл карточки
- Export/import roundtrip
- Навигацию по графу
- Производительность на 500 карточках

---

## Производительность

**Характеристики:**
- Создание карточки: < 10ms
- Поиск среди 1000 карточек: < 100ms
- Rebuild index для 1000 карточек: < 500ms

**Рекомендации:**
- Используйте `limit` в search() для больших наборов
- Избегайте частых rebuild_index()
- Кэширование встроено (LRU cache для частых запросов)

---

## Лицензия

Карточная система — часть проекта "Информационно-операционная система для домашнего использования".

---

## См. также

**Практические руководства:**
- ⇓ [EXAMPLES.md](EXAMPLES.md) (α=-3) — практические примеры использования API
- ⇓ [USER-GUIDE.md](../02-Информационная-система/USER-GUIDE.md) (α=-3) — руководство пользователя
- ⇓ [QUICK-START.md](../QUICK-START.md) (α=-1) — быстрый старт за 5 минут

**Архитектура и спецификации:**
- ⇑ [АРХИТЕКТУРА-СИСТЕМЫ.md](../АРХИТЕКТУРА-СИСТЕМЫ.md) (α=0) — общая архитектура
- ↔ [README.md](README.md) (α=-4) — программная реализация

**Инструменты и тестирование:**
- ↔ [tools/EXAMPLES.md](../tools/EXAMPLES.md) — примеры использования CLI
- ↔ [TROUBLESHOOTING.md](../TROUBLESHOOTING.md) (α=-1) — решение проблем

**Методология:**
- ⇑ [ДОКУМЕНТАЦИЯ.md](../ДОКУМЕНТАЦИЯ.md) — полная методология ⇑⇓↔
- ↔ [BEST-PRACTICES.md](../BEST-PRACTICES.md) (α=-1) — лучшие практики разработки

---

**Дата:** 2026-01-23
**Версия:** 1.0
**Статус:** Актуальная документация
