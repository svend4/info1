# Architecture — Архитектура системы

Визуальное представление архитектуры информационно-операционной системы для домашнего использования.

---

## Оглавление

1. [Обзор архитектуры](#обзор-архитектуры)
2. [Уровни абстракции](#уровни-абстракции)
3. [Компоненты системы](#компоненты-системы)
4. [Потоки данных](#потоки-данных)
5. [Технологический стек](#технологический-стек)
6. [Паттерны проектирования](#паттерны-проектирования)

---

## Обзор архитектуры

### Вертикальная структура (9 уровней абстракции)

```
┌─────────────────────────────────────────────────────────────┐
│                     α = +4: ОНТОЛОГИЯ                        │
│                  (метаметапринципы)                         │
│        ОНТОЛОГИЯ-СИСТЕМ.md: 6 метаметапринципов            │
│                                                             │
│  ⇅ Обобщение ↑ / Практика ↓                                │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                     α = +3: ФИЛОСОФИЯ                        │
│               (философские основания)                        │
│   ФИЛОСОФИЯ-ПРОЕКТА.md + ФИЛОСОФИЯ-ПРИМЕНИМОСТИ.md          │
│                                                             │
│  ⇅ Философское обоснование ↑ / Философские выводы ↓         │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                  α = +2: УНИВЕРСАЛЬНЫЕ ЗАКОНЫ                │
│                    (12 законов)                             │
│              УНИВЕРСАЛЬНЫЕ-ЗАКОНЫ.md                        │
│                                                             │
│  ⇅ Законы организации ↑ / Обобщение паттернов ↓            │
└─────────────────────────────────────────────────────────────┘
           ↓                                       ↓
      ┌────────┐                           ┌──────────────┐
      │  МОСТ  │←──────────────────────────│ ЗАКОНЫ-В-    │
      │ α=+2 ↔│                            │  КОДЕ.md     │
      │  α=-4  │                            └──────────────┘
      └────────┘
           ↓
┌─────────────────────────────────────────────────────────────┐
│                  α = +1: ПРИНЦИПЫ + МЕТОДОЛОГИЯ              │
│                (принципы и методология)                      │
│ ПРИНЦИПЫ-И-ПАТТЕРНЫ.md + МЕТОДОЛОГИЯ-...-РАЗВИТИЯ.md ⭐     │
│                                                             │
│  ⇅ Принципы проектирования ↑ / Извлечение принципов ↓       │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│             α = 0: КОНЦЕПЦИИ (точка опоры)                   │
│                                                             │
│    README.md + Папки 02-07/ (концептуальные документы)     │
│                                                             │
│  ⇅ Детализация ↓ / Обобщение ↑                              │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│          α = -1: ТЕХНИЧЕСКИЕ СПЕЦИФИКАЦИИ                    │
│                  (спецификации)                             │
│           ТЕХНИЧЕСКИЕ-СПЕЦИФИКАЦИИ.md                       │
│                                                             │
│  ⇅ Технические детали ↓ / Обобщение спецификаций ↑          │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│               α = -2: API + ШАБЛОНЫ                          │
│                                                             │
│    API-REFERENCE.md + ШАБЛОНЫ-КАРТОЧЕК.md                   │
│                                                             │
│  ⇅ Готовые шаблоны ↓ / Обобщение шаблонов ↑                 │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│             α = -3: ПРИМЕРЫ + РУКОВОДСТВА                    │
│                                                             │
│   EXAMPLES.md + USER-GUIDE.md + Примеры/ (7 файлов)        │
│                                                             │
│  ⇅ Конкретные примеры ↓ / Обобщение из примеров ↑           │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│              α = -4: ИСПОЛНЯЕМЫЙ КОД                         │
│                 (~4100 строк кода)                          │
│                                                             │
│  card.py + card_manager.py + automation.py +                │
│  export_import.py + cli.py + demo.py +                     │
│  visualize_graph.py + test_*.py                            │
└─────────────────────────────────────────────────────────────┘
```

---

## Компоненты системы

### Архитектура карточной системы (α=-4)

```
┌───────────────────────────────────────────────────────────────┐
│                        CLI LAYER                              │
│                                                               │
│   ┌─────────────┐  ┌──────────────┐  ┌──────────────┐       │
│   │   cli.py    │  │   demo.py    │  │ automation.py│       │
│   │ (Commands)  │  │ (Examples)   │  │  (Schedule)  │       │
│   └──────┬──────┘  └──────┬───────┘  └──────┬───────┘       │
│          │                 │                 │               │
└──────────┼─────────────────┼─────────────────┼───────────────┘
           │                 │                 │
           ↓                 ↓                 ↓
┌───────────────────────────────────────────────────────────────┐
│                      MANAGER LAYER                            │
│                                                               │
│   ┌─────────────────────────────────────────────────┐        │
│   │              CardManager                         │        │
│   │                                                  │        │
│   │  • create(card) → Card                          │        │
│   │  • read(id) → Card                              │        │
│   │  • update(card) → Card                          │        │
│   │  • delete(id) → bool                            │        │
│   │  • search(**filters) → List[Card]               │        │
│   │  • link(id1, id2, rel) → Link                   │        │
│   │  • get_related(id) → List[Card]                 │        │
│   │  • get_stats() → Dict                           │        │
│   └──────────────────┬──────────────────────────────┘        │
│                      │                                        │
│         ┌────────────┼────────────┐                          │
│         ↓            ↓            ↓                          │
│   ┌──────────┐ ┌──────────┐ ┌──────────┐                    │
│   │CardIndex │ │  Storage │ │  Graph   │                    │
│   │(BFS/DFS) │ │  (YAML)  │ │ (Links)  │                    │
│   └──────────┘ └──────────┘ └──────────┘                    │
└───────────────────────────────────────────────────────────────┘
           │                 │                 │
           ↓                 ↓                 ↓
┌───────────────────────────────────────────────────────────────┐
│                        DATA LAYER                             │
│                                                               │
│   ┌─────────────────────────────────────────────────────┐    │
│   │                     Card (Base)                      │    │
│   │                                                      │    │
│   │  id: UUID                                           │    │
│   │  type: CardType                                     │    │
│   │  title: str                                         │    │
│   │  created_at: datetime                               │    │
│   │  updated_at: datetime                               │    │
│   │  tags: List[str]                                    │    │
│   │  links: List[Link]                                  │    │
│   └──────────────────┬──────────────────────────────────┘    │
│                      │                                        │
│       ┌──────────────┼──────────────┐                        │
│       ↓              ↓              ↓                        │
│  ┌─────────┐   ┌──────────┐   ┌──────────┐                  │
│  │  Task   │   │ Medicine │   │ Contact  │                  │
│  │  Card   │   │   Card   │   │   Card   │                  │
│  └─────────┘   └──────────┘   └──────────┘                  │
│       ↓              ↓              ↓                        │
│  ┌─────────┐   ┌──────────┐   ┌──────────┐                  │
│  │Shopping │   │Appointment│   │   Note   │                  │
│  │  Card   │   │   Card   │   │   Card   │                  │
│  └─────────┘   └──────────┘   └──────────┘                  │
│                      ↓                                        │
│                ┌──────────┐                                   │
│                │ Project  │                                   │
│                │   Card   │                                   │
│                └──────────┘                                   │
└───────────────────────────────────────────────────────────────┘
           │                 │                 │
           ↓                 ↓                 ↓
┌───────────────────────────────────────────────────────────────┐
│                    PERSISTENCE LAYER                          │
│                                                               │
│   ┌─────────────┐  ┌──────────────┐  ┌──────────────┐       │
│   │    YAML     │  │     JSON     │  │     CSV      │       │
│   │   Storage   │  │    Export    │  │    Export    │       │
│   └─────────────┘  └──────────────┘  └──────────────┘       │
└───────────────────────────────────────────────────────────────┘
```

### Система автоматизации

```
┌───────────────────────────────────────────────────────────────┐
│                    CardAutomation                             │
│                                                               │
│  ┌───────────────────────────────────────────────────────┐   │
│  │              Scheduled Tasks                          │   │
│  │                                                        │   │
│  │  • check_overdue_tasks() → List[Task]               │   │
│  │    ↳ Проверка просроченных задач                    │   │
│  │                                                        │   │
│  │  • check_medicine_reminders() → List[Reminder]       │   │
│  │    ↳ Напоминания о приёме лекарств                   │   │
│  │                                                        │   │
│  │  • archive_old_cards(days=30)                        │   │
│  │    ↳ Архивирование старых карточек                   │   │
│  │                                                        │   │
│  │  • create_backup() → Path                            │   │
│  │    ↳ Создание резервной копии в ZIP                  │   │
│  │                                                        │   │
│  │  • generate_report(period) → str                     │   │
│  │    ↳ Генерация отчётов (week/month)                  │   │
│  └────────────────────────────────────────────────────────┘   │
│                                                               │
│  Cron Schedule:                                              │
│  • Every hour: check reminders                              │
│  • Daily: check overdue tasks                               │
│  • Weekly: archive old cards, generate report                │
│  • Monthly: create backup, generate monthly report           │
└───────────────────────────────────────────────────────────────┘
```

---

## Потоки данных

### Создание карточки (Create Flow)

```
User Input
    ↓
CLI Command: card-cli create task "Купить молоко"
    ↓
┌──────────────────────┐
│  CLI Parser          │  Парсинг аргументов командной строки
│  (cli.py)            │
└──────┬───────────────┘
       ↓
┌──────────────────────┐
│  Validation          │  Валидация данных
│  (card.py)           │
└──────┬───────────────┘
       ↓
┌──────────────────────┐
│  CardManager         │  Создание UUID, timestamps
│  .create()           │
└──────┬───────────────┘
       ↓
┌──────────────────────┐
│  Persistence         │  Сохранение в YAML файл
│  (storage)           │  cards/<UUID>.yaml
└──────┬───────────────┘
       ↓
┌──────────────────────┐
│  Index Update        │  Обновление индекса
│  (CardIndex)         │  для быстрого поиска
└──────┬───────────────┘
       ↓
Return Created Card with ID
```

### Поиск карточек (Search Flow)

```
User Query: card-cli search "молоко" --type task
    ↓
┌──────────────────────┐
│  CLI Parser          │  Парсинг query + filters
└──────┬───────────────┘
       ↓
┌──────────────────────┐
│  CardManager         │  Применение фильтров:
│  .search()           │  • type filter
│                      │  • text search (in title/description)
│                      │  • tag filter
│                      │  • date range filter
└──────┬───────────────┘
       ↓
┌──────────────────────┐
│  CardIndex           │  Быстрый поиск по индексу
│  (LRU Cache)         │  O(1) для частых запросов
└──────┬───────────────┘
       ↓
┌──────────────────────┐
│  Results             │  Сортировка по relevance
│  Sorting             │  или created_at
└──────┬───────────────┘
       ↓
Return List[Card]
```

### Граф связей (Link Traversal)

```
Get Related Cards: manager.get_related(card_id)
    ↓
┌──────────────────────┐
│  Load Card           │  Загрузка начальной карточки
│  (card_id)           │
└──────┬───────────────┘
       ↓
┌──────────────────────┐
│  Extract Links       │  Извлечение всех связей из card.links
│  (from card)         │
└──────┬───────────────┘
       ↓
┌──────────────────────┐
│  BFS Traversal       │  Обход графа в ширину:
│  (or DFS)            │  • Очередь связанных ID
│                      │  • Visited set (избежание циклов)
│                      │  • Max depth limit
└──────┬───────────────┘
       ↓
┌──────────────────────┐
│  Load Related        │  Загрузка всех связанных карточек
│  Cards               │
└──────┬───────────────┘
       ↓
Return Dict[str, List[Card]]  # Группировка по типу связи
```

---

## Технологический стек

### Базовая система (без внешних зависимостей)

```
Python 3.8+
├── dataclasses         (Card models)
├── enum                (CardType, Status)
├── pathlib             (File operations)
├── datetime            (Timestamps)
├── uuid                (Unique IDs)
├── typing              (Type hints)
├── json                (Export/Import)
├── csv                 (Export)
├── zipfile             (Backup)
└── unittest            (Testing)
```

### Опциональные расширения

```
Web Integration
├── flask>=2.0.0        (REST API)
└── requests            (HTTP client)

Bot Integration
├── python-telegram-bot>=13.0  (Telegram bot)
└── aiogram             (Alternative bot framework)

Development Tools
├── black>=22.0.0       (Code formatting)
├── flake8>=4.0.0       (Linting)
├── mypy>=0.950         (Type checking)
└── pytest>=7.0.0       (Advanced testing)
```

---

## Паттерны проектирования

### 1. Repository Pattern (CardManager)

```python
# CardManager инкапсулирует всю логику работы с данными
manager = CardManager(Path("./cards"))

# CRUD операции через единый интерфейс
card = manager.create(TaskCard(title="Task"))
card = manager.read(card_id)
card = manager.update(modified_card)
manager.delete(card_id)

# Поиск и навигация
cards = manager.search(type="task", status="pending")
related = manager.get_related(card_id)
```

**Преимущества:**
- Единая точка доступа к данным (SSOT)
- Легко тестировать (мокаем только manager)
- Можно менять хранилище без изменения клиентского кода

### 2. Strategy Pattern (Card Types)

```python
# Базовый класс определяет интерфейс
@dataclass
class Card:
    def to_dict(self) -> dict: ...
    @classmethod
    def from_dict(cls, data: dict) -> 'Card': ...

# Специализированные карточки реализуют разное поведение
class TaskCard(Card):
    status: str = "pending"
    priority: str = "medium"

class MedicineCard(Card):
    dosage: str
    schedule: List[str]
```

**Преимущества:**
- Расширяемость (легко добавить новый тип)
- Полиморфизм (обработка разных типов единообразно)
- Инкапсуляция (специфичная логика в своём классе)

### 3. Factory Pattern (Card Creation)

```python
def create_card_from_type(card_type: str, **kwargs) -> Card:
    """Фабрика для создания карточек по типу"""
    card_classes = {
        "task": TaskCard,
        "medicine": MedicineCard,
        "contact": ContactCard,
        # ...
    }
    card_class = card_classes.get(card_type)
    if not card_class:
        raise ValueError(f"Unknown card type: {card_type}")
    return card_class(**kwargs)
```

**Преимущества:**
- Централизованное создание объектов
- Легко добавить новые типы
- Валидация при создании

### 4. Observer Pattern (Automation)

```python
class CardAutomation:
    def __init__(self, manager: CardManager):
        self.manager = manager
        self.observers = []  # Подписчики на события

    def check_medicine_reminders(self):
        reminders = self._find_due_reminders()
        for reminder in reminders:
            # Уведомить всех подписчиков
            self._notify(reminder)
```

**Преимущества:**
- Слабая связанность (automation не знает о конкретных подписчиках)
- Расширяемость (легко добавить новые обработчики событий)

### 5. Template Method (Export/Import)

```python
class CardExporter:
    def export(self, cards: List[Card], path: Path):
        """Шаблонный метод"""
        data = self._prepare_data(cards)      # Шаг 1
        formatted = self._format_data(data)    # Шаг 2
        self._write_to_file(formatted, path)   # Шаг 3

class JSONExporter(CardExporter):
    def _format_data(self, data):
        return json.dumps(data, indent=2)

class CSVExporter(CardExporter):
    def _format_data(self, data):
        # CSV formatting
        ...
```

**Преимущества:**
- Переиспользование общей логики
- Гибкость в специфичных шагах
- Соблюдение DRY

---

## Принципы проектирования

### SOLID Principles

**Single Responsibility**
- `Card` — только данные
- `CardManager` — только управление карточками
- `CardAutomation` — только автоматизация

**Open/Closed**
- Легко добавить новый тип карточки (наследование от `Card`)
- Легко добавить новый формат экспорта (наследование от `CardExporter`)

**Liskov Substitution**
- Все специализированные карточки могут использоваться вместо базового `Card`

**Interface Segregation**
- Узкие, специфичные интерфейсы вместо монолитных

**Dependency Inversion**
- `CardManager` зависит от абстракции `Card`, а не от конкретных типов

### Дополнительные принципы

**SSOT (Single Source of Truth)**
- Одна карточка = один YAML файл
- CardManager — единственный способ работы с данными

**DRY (Don't Repeat Yourself)**
- Общая логика в базовом `Card`
- Переиспользование через наследование

**YAGNI (You Aren't Gonna Need It)**
- Никаких внешних зависимостей для базовой функциональности
- Только то, что реально нужно

---

## Масштабируемость и производительность

### Производительность

```
Операция                    Время        Сложность
────────────────────────────────────────────────────
Создание карточки          < 10ms       O(1)
Чтение карточки            < 5ms        O(1)
Обновление карточки        < 10ms       O(1)
Удаление карточки          < 5ms        O(1)
Поиск среди 1000 карточек  < 100ms      O(n)
Экспорт 1000 карточек      < 1s         O(n)
BFS traversal (depth=3)    < 50ms       O(b^d)
```

### Кэширование

```python
from functools import lru_cache

class CardIndex:
    @lru_cache(maxsize=128)
    def search(self, query: str) -> List[Card]:
        # Результаты часто используемых запросов кэшируются
        ...
```

### Масштабируемость

**Текущие ограничения:**
- ~10,000 карточек на одного пользователя (комфортно)
- ~100,000 карточек (максимум, с деградацией производительности)

**Для масштабирования:**
- Индексация в SQLite или PostgreSQL
- Полнотекстовый поиск (Elasticsearch)
- Кэш в Redis

---

## Безопасность

### Data Security

```
Storage: YAML files on disk
├── Permissions: 0600 (read/write только для владельца)
├── Backup: ZIP archives с опциональным шифрованием
└── Export: JSON/CSV с контролируемым доступом
```

### Code Security

```python
# Валидация входных данных
def create(self, card: Card) -> Card:
    if not isinstance(card, Card):
        raise TypeError("Must be a Card instance")
    if card.id:
        raise ValueError("Card must not have an ID")
    # ...

# Санитизация путей
def _get_card_path(self, card_id: str) -> Path:
    # Защита от path traversal
    if ".." in card_id or "/" in card_id:
        raise ValueError("Invalid card ID")
    return self.cards_dir / f"{card_id}.yaml"
```

---

## Тестирование

### Test Pyramid

```
         ┌────────────┐
         │     E2E    │  Integration Tests (4)
         │   Tests    │  • Full workflow tests
         ├────────────┤
         │            │
         │   Unit     │  Unit Tests (21)
         │   Tests    │  • Card creation
         │            │  • CRUD operations
         │            │  • Search & filter
         │            │  • Graph traversal
         └────────────┘
```

### Coverage

```
Component            Coverage
─────────────────────────────
card.py              100%
card_manager.py      100%
export_import.py     95%
automation.py        90%
cli.py               85%
─────────────────────────────
Total                ~95%
```

---

## Развитие архитектуры

### Roadmap

**v1.0 (текущая версия)**
- ✅ Базовая карточная система
- ✅ 7 типов карточек
- ✅ Граф связей
- ✅ Автоматизация
- ✅ CLI интерфейс
- ✅ Экспорт/импорт

**v1.1 (планируется)**
- 🔄 Web UI (Flask/FastAPI)
- 🔄 Telegram bot
- 🔄 REST API
- 🔄 Мобильное приложение

**v2.0 (будущее)**
- 📋 Multi-user support
- 📋 Cloud sync
- 📋 Collaborative cards
- 📋 AI-powered suggestions

---

**Дата создания:** 2026-01-23
**Версия:** 1.0
**Статус:** Актуальная документация

**См. также:**
- [API-REFERENCE.md](08-Программная-реализация/API-REFERENCE.md) — подробная документация API
- [МЕТОДОЛОГИЯ-ПАРАЛЛЕЛЬНОГО-РАЗВИТИЯ.md](01-Концепция/МЕТОДОЛОГИЯ-ПАРАЛЛЕЛЬНОГО-РАЗВИТИЯ.md) — методология создания архитектуры
- [ПРИНЦИПЫ-И-ПАТТЕРНЫ.md](01-Концепция/ПРИНЦИПЫ-И-ПАТТЕРНЫ.md) — принципы проектирования
