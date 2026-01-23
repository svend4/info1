"""
Модуль Card - базовая реализация карточной системы [α=-4]

Этот модуль реализует основную функциональность карточной системы
согласно техническим спецификациям (α=-1).

Связи:
- Вверх: ТЕХНИЧЕСКИЕ-СПЕЦИФИКАЦИИ.md (α=-1)
- Вниз: Конкретный исполняемый код (α=-4)
"""

import yaml
import datetime
import hashlib
import random
import string
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from enum import Enum


class CardType(Enum):
    """Типы карточек согласно спецификации"""
    TASK = "task"
    MEDICINE = "medicine"
    RECIPE = "recipe"
    SHOPPING = "shopping"
    CONTACT = "contact"
    APPOINTMENT = "appointment"
    NOTE = "note"


class CardStatus(Enum):
    """Статусы карточек"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class Priority(Enum):
    """Приоритеты карточек"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


@dataclass
class Card:
    """
    Базовый класс карточки

    Реализует спецификацию из ТЕХНИЧЕСКИЕ-СПЕЦИФИКАЦИИ.md
    с обязательными и опциональными полями.
    """

    # Обязательные поля
    id: str
    type: CardType
    title: str
    created: datetime.datetime
    modified: datetime.datetime

    # Опциональные поля
    status: Optional[CardStatus] = CardStatus.PENDING
    priority: Optional[Priority] = Priority.MEDIUM
    tags: List[str] = field(default_factory=list)
    linked_cards: List[str] = field(default_factory=list)
    assigned_robot: Optional[str] = None
    location: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Markdown содержимое
    content: str = ""

    @staticmethod
    def generate_id() -> str:
        """
        Генерация уникального ID карточки

        Формат: card_YYYYMMDD_HHMMSS_RAND
        Где RAND - 4 случайных символа [a-z0-9]

        Returns:
            str: Уникальный идентификатор
        """
        now = datetime.datetime.now()
        timestamp = now.strftime("%Y%m%d_%H%M%S")
        rand_suffix = ''.join(random.choices(
            string.ascii_lowercase + string.digits,
            k=4
        ))
        return f"card_{timestamp}_{rand_suffix}"

    @classmethod
    def create(
        cls,
        card_type: CardType,
        title: str,
        content: str = "",
        **kwargs
    ) -> 'Card':
        """
        Создать новую карточку

        Args:
            card_type: Тип карточки
            title: Заголовок
            content: Markdown содержимое
            **kwargs: Дополнительные поля

        Returns:
            Card: Новая карточка
        """
        now = datetime.datetime.now()
        card_id = cls.generate_id()

        return cls(
            id=card_id,
            type=card_type,
            title=title,
            created=now,
            modified=now,
            content=content,
            **kwargs
        )

    def to_dict(self) -> Dict:
        """
        Конвертация карточки в словарь

        Returns:
            Dict: Данные карточки
        """
        data = asdict(self)

        # Конвертация Enum в строки
        data['type'] = self.type.value
        if self.status:
            data['status'] = self.status.value
        if self.priority:
            data['priority'] = self.priority.value

        # Конвертация datetime в ISO формат
        data['created'] = self.created.isoformat()
        data['modified'] = self.modified.isoformat()

        return data

    def to_yaml_frontmatter(self) -> str:
        """
        Генерация YAML frontmatter для markdown файла

        Returns:
            str: YAML frontmatter
        """
        data = self.to_dict()
        # Удаляем content, он идёт после frontmatter
        content = data.pop('content', '')

        yaml_str = yaml.dump(
            data,
            allow_unicode=True,
            default_flow_style=False,
            sort_keys=False
        )

        return f"---\n{yaml_str}---\n"

    def to_markdown(self) -> str:
        """
        Полная конвертация в Markdown файл

        Returns:
            str: Полный Markdown с YAML frontmatter
        """
        frontmatter = self.to_yaml_frontmatter()
        return f"{frontmatter}\n{self.content}"

    @classmethod
    def from_markdown(cls, markdown_text: str) -> 'Card':
        """
        Парсинг карточки из Markdown файла

        Args:
            markdown_text: Текст markdown файла

        Returns:
            Card: Распарсенная карточка
        """
        # Разделить frontmatter и content
        parts = markdown_text.split('---\n', 2)
        if len(parts) < 3:
            raise ValueError("Invalid markdown format: missing frontmatter")

        # Парсинг YAML
        yaml_data = yaml.safe_load(parts[1])
        content = parts[2].strip()

        # Конвертация строк обратно в Enum
        yaml_data['type'] = CardType(yaml_data['type'])
        if 'status' in yaml_data and yaml_data['status']:
            yaml_data['status'] = CardStatus(yaml_data['status'])
        if 'priority' in yaml_data and yaml_data['priority']:
            yaml_data['priority'] = Priority(yaml_data['priority'])

        # Конвертация строк обратно в datetime
        yaml_data['created'] = datetime.datetime.fromisoformat(
            yaml_data['created']
        )
        yaml_data['modified'] = datetime.datetime.fromisoformat(
            yaml_data['modified']
        )

        yaml_data['content'] = content

        return cls(**yaml_data)

    def save(self, directory: Path) -> Path:
        """
        Сохранить карточку в файл

        Args:
            directory: Директория для сохранения

        Returns:
            Path: Путь к сохранённому файлу
        """
        directory = Path(directory)
        directory.mkdir(parents=True, exist_ok=True)

        # Генерация имени файла
        date_str = self.created.strftime("%Y%m%d")
        safe_title = "".join(
            c if c.isalnum() or c in ('-', '_') else '_'
            for c in self.title
        )[:50]
        filename = f"{date_str}_{self.type.value}_{safe_title}.card.md"

        filepath = directory / filename

        # Сохранение
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(self.to_markdown())

        return filepath

    @classmethod
    def load(cls, filepath: Path) -> 'Card':
        """
        Загрузить карточку из файла

        Args:
            filepath: Путь к файлу

        Returns:
            Card: Загруженная карточка
        """
        filepath = Path(filepath)

        with open(filepath, 'r', encoding='utf-8') as f:
            markdown_text = f.read()

        return cls.from_markdown(markdown_text)

    def update(self, **kwargs) -> None:
        """
        Обновить поля карточки

        Args:
            **kwargs: Поля для обновления
        """
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

        self.modified = datetime.datetime.now()

    def add_tag(self, tag: str) -> None:
        """Добавить тег"""
        if tag not in self.tags:
            self.tags.append(tag)
            self.modified = datetime.datetime.now()

    def remove_tag(self, tag: str) -> None:
        """Удалить тег"""
        if tag in self.tags:
            self.tags.remove(tag)
            self.modified = datetime.datetime.now()

    def link_to(self, card_id: str) -> None:
        """Создать связь с другой карточкой"""
        if card_id not in self.linked_cards:
            self.linked_cards.append(card_id)
            self.modified = datetime.datetime.now()

    def unlink_from(self, card_id: str) -> None:
        """Удалить связь с карточкой"""
        if card_id in self.linked_cards:
            self.linked_cards.remove(card_id)
            self.modified = datetime.datetime.now()

    def __repr__(self) -> str:
        return f"Card(id='{self.id}', type={self.type.value}, title='{self.title}')"


# Специализированные классы карточек

@dataclass
class TaskCard(Card):
    """Карточка-задача с дополнительными полями"""

    due_date: Optional[datetime.datetime] = None
    reminder: Optional[datetime.datetime] = None
    estimated_duration: Optional[int] = None  # минуты
    completion_criteria: List[str] = field(default_factory=list)

    def __post_init__(self):
        self.type = CardType.TASK

    @classmethod
    def create_task(
        cls,
        title: str,
        content: str = "",
        due_date: Optional[datetime.datetime] = None,
        **kwargs
    ) -> 'TaskCard':
        """Создать карточку-задачу"""
        now = datetime.datetime.now()
        card_id = cls.generate_id()

        return cls(
            id=card_id,
            type=CardType.TASK,
            title=title,
            created=now,
            modified=now,
            content=content,
            due_date=due_date,
            **kwargs
        )

    def is_overdue(self) -> bool:
        """Проверить, просрочена ли задача"""
        if not self.due_date:
            return False
        return datetime.datetime.now() > self.due_date

    def complete(self) -> None:
        """Отметить задачу как выполненную"""
        self.status = CardStatus.COMPLETED
        self.modified = datetime.datetime.now()


@dataclass
class MedicineCard(Card):
    """Карточка-лекарство"""

    medication_name: str = ""
    dosage: str = ""
    frequency: str = ""
    administration_time: List[str] = field(default_factory=list)

    def __post_init__(self):
        self.type = CardType.MEDICINE

    @classmethod
    def create_medicine(
        cls,
        title: str,
        medication_name: str,
        dosage: str,
        frequency: str,
        **kwargs
    ) -> 'MedicineCard':
        """Создать карточку лекарства"""
        now = datetime.datetime.now()
        card_id = cls.generate_id()

        return cls(
            id=card_id,
            type=CardType.MEDICINE,
            title=title,
            created=now,
            modified=now,
            medication_name=medication_name,
            dosage=dosage,
            frequency=frequency,
            **kwargs
        )


@dataclass
class RecipeCard(Card):
    """Карточка-рецепт"""

    servings: int = 1
    prep_time: int = 0  # минуты
    cook_time: int = 0  # минуты
    difficulty: str = "medium"
    ingredients: List[Dict] = field(default_factory=list)

    def __post_init__(self):
        self.type = CardType.RECIPE

    @classmethod
    def create_recipe(
        cls,
        title: str,
        content: str = "",
        servings: int = 1,
        ingredients: List[Dict] = None,
        **kwargs
    ) -> 'RecipeCard':
        """Создать карточку рецепта"""
        now = datetime.datetime.now()
        card_id = cls.generate_id()

        return cls(
            id=card_id,
            type=CardType.RECIPE,
            title=title,
            created=now,
            modified=now,
            content=content,
            servings=servings,
            ingredients=ingredients or [],
            **kwargs
        )

    def get_total_time(self) -> int:
        """Общее время приготовления"""
        return self.prep_time + self.cook_time


@dataclass
class ShoppingCard(Card):
    """Карточка-покупка"""

    items: List[Dict] = field(default_factory=list)  # [{"name": "Молоко", "quantity": 1, "unit": "л", "checked": False}]
    store: str = ""
    estimated_cost: float = 0.0

    def __post_init__(self):
        self.type = CardType.SHOPPING

    @classmethod
    def create_shopping(
        cls,
        title: str,
        items: List[Dict] = None,
        store: str = "",
        **kwargs
    ) -> 'ShoppingCard':
        """Создать карточку покупки"""
        now = datetime.datetime.now()
        card_id = cls.generate_id()

        return cls(
            id=card_id,
            type=CardType.SHOPPING,
            title=title,
            created=now,
            modified=now,
            items=items or [],
            store=store,
            **kwargs
        )

    def add_item(self, name: str, quantity: float = 1, unit: str = "", checked: bool = False):
        """Добавить товар в список"""
        self.items.append({
            "name": name,
            "quantity": quantity,
            "unit": unit,
            "checked": checked
        })
        self.modified = datetime.datetime.now()

    def check_item(self, index: int):
        """Отметить товар как купленный"""
        if 0 <= index < len(self.items):
            self.items[index]["checked"] = True
            self.modified = datetime.datetime.now()

    def get_unchecked_items(self) -> List[Dict]:
        """Получить некупленные товары"""
        return [item for item in self.items if not item.get("checked", False)]


@dataclass
class ContactCard(Card):
    """Карточка-контакт"""

    person_name: str = ""
    phone: str = ""
    email: str = ""
    address: str = ""
    relationship: str = ""  # родственник, друг, врач, сосед и т.д.
    notes: str = ""

    def __post_init__(self):
        self.type = CardType.CONTACT

    @classmethod
    def create_contact(
        cls,
        title: str,
        person_name: str = "",
        phone: str = "",
        email: str = "",
        relationship: str = "",
        **kwargs
    ) -> 'ContactCard':
        """Создать карточку контакта"""
        now = datetime.datetime.now()
        card_id = cls.generate_id()

        return cls(
            id=card_id,
            type=CardType.CONTACT,
            title=title,
            created=now,
            modified=now,
            person_name=person_name or title,
            phone=phone,
            email=email,
            relationship=relationship,
            **kwargs
        )


@dataclass
class AppointmentCard(Card):
    """Карточка-встреча"""

    appointment_date: Optional[datetime.datetime] = None
    duration: int = 60  # минуты
    location: str = ""
    participants: List[str] = field(default_factory=list)
    reminder_time: Optional[datetime.datetime] = None

    def __post_init__(self):
        self.type = CardType.APPOINTMENT

    @classmethod
    def create_appointment(
        cls,
        title: str,
        appointment_date: datetime.datetime = None,
        location: str = "",
        duration: int = 60,
        **kwargs
    ) -> 'AppointmentCard':
        """Создать карточку встречи"""
        now = datetime.datetime.now()
        card_id = cls.generate_id()

        return cls(
            id=card_id,
            type=CardType.APPOINTMENT,
            title=title,
            created=now,
            modified=now,
            appointment_date=appointment_date or now,
            location=location,
            duration=duration,
            **kwargs
        )

    def is_upcoming(self) -> bool:
        """Проверить, предстоит ли встреча"""
        if not self.appointment_date:
            return False
        return self.appointment_date > datetime.datetime.now()

    def time_until(self) -> Optional[datetime.timedelta]:
        """Время до встречи"""
        if not self.appointment_date:
            return None
        return self.appointment_date - datetime.datetime.now()


@dataclass
class NoteCard(Card):
    """Карточка-заметка"""

    category: str = ""
    subcategory: str = ""

    def __post_init__(self):
        self.type = CardType.NOTE

    @classmethod
    def create_note(
        cls,
        title: str,
        content: str = "",
        category: str = "",
        tags: List[str] = None,
        **kwargs
    ) -> 'NoteCard':
        """Создать карточку заметки"""
        now = datetime.datetime.now()
        card_id = cls.generate_id()

        return cls(
            id=card_id,
            type=CardType.NOTE,
            title=title,
            created=now,
            modified=now,
            content=content,
            category=category,
            tags=tags or [],
            **kwargs
        )


# Демонстрация использования
if __name__ == "__main__":
    print("=== Демонстрация карточной системы [α=-4] ===\n")

    # 1. Создание простой карточки-задачи
    print("1. Создание карточки-задачи:")
    task = TaskCard.create_task(
        title="Утренняя зарядка",
        content="## Описание\n\nЕжедневная лёгкая зарядка для поддержания здоровья.",
        priority=Priority.MEDIUM,
        tags=["здоровье", "утро", "ежедневно"],
        estimated_duration=15,
        completion_criteria=[
            "Выполнить все 7 упражнений",
            "Общее время 15 минут"
        ]
    )
    print(f"   Создана: {task}")
    print(f"   ID: {task.id}")
    print(f"   Теги: {task.tags}\n")

    # 2. Создание карточки лекарства
    print("2. Создание карточки лекарства:")
    medicine = MedicineCard.create_medicine(
        title="Эналаприл 10мг",
        medication_name="Эналаприл",
        dosage="10 мг",
        frequency="1 раз в день",
        administration_time=["19:00"],
        tags=["здоровье", "лекарства", "гипертония"]
    )
    print(f"   Создана: {medicine}")
    print(f"   Лекарство: {medicine.medication_name} {medicine.dosage}\n")

    # 3. Создание карточки рецепта
    print("3. Создание карточки рецепта:")
    recipe = RecipeCard.create_recipe(
        title="Овсяная каша",
        content="## Ингредиенты\n- Овсянка 50г\n- Вода 200мл",
        servings=1,
        prep_time=2,
        cook_time=10,
        difficulty="легкая",
        ingredients=[
            {"name": "Овсяные хлопья", "quantity": 50, "unit": "г"},
            {"name": "Вода", "quantity": 200, "unit": "мл"}
        ],
        tags=["завтрак", "здоровое-питание"]
    )
    print(f"   Создана: {recipe}")
    print(f"   Общее время: {recipe.get_total_time()} минут\n")

    # 4. Связывание карточек
    print("4. Связывание карточек:")
    task.link_to(medicine.id)
    print(f"   Задача '{task.title}' связана с '{medicine.title}'")
    print(f"   Связи задачи: {task.linked_cards}\n")

    # 5. Сохранение в файл
    print("5. Сохранение карточек:")
    from pathlib import Path
    test_dir = Path("/tmp/test_cards")

    task_file = task.save(test_dir)
    print(f"   Задача сохранена: {task_file}")

    medicine_file = medicine.save(test_dir)
    print(f"   Лекарство сохранено: {medicine_file}")

    recipe_file = recipe.save(test_dir)
    print(f"   Рецепт сохранён: {recipe_file}\n")

    # 6. Загрузка из файла
    print("6. Загрузка карточки из файла:")
    loaded_task = TaskCard.load(task_file)
    print(f"   Загружена: {loaded_task}")
    print(f"   Содержимое совпадает: {loaded_task.title == task.title}\n")

    # 7. Обновление карточки
    print("7. Обновление карточки:")
    loaded_task.complete()
    loaded_task.add_tag("выполнено")
    print(f"   Статус: {loaded_task.status.value}")
    print(f"   Новые теги: {loaded_task.tags}\n")

    # 8. Проверка просроченности
    print("8. Проверка просроченности задачи:")
    overdue_task = TaskCard.create_task(
        title="Позвонить врачу",
        due_date=datetime.datetime.now() - datetime.timedelta(days=1)
    )
    print(f"   Задача просрочена: {overdue_task.is_overdue()}\n")

    print("=== Демонстрация завершена ===")
    print(f"\nСвязи с другими документами:")
    print(f"  ⇑ α=-1: ТЕХНИЧЕСКИЕ-СПЕЦИФИКАЦИИ.md")
    print(f"  ⇑ α=0:  02-Информационная-система/README.md")
    print(f"  ⇑ α=+1: ПРИНЦИПЫ-И-ПАТТЕРНЫ.md")
    print(f"  ⇑ α=+2: УНИВЕРСАЛЬНЫЕ-ЗАКОНЫ.md")
    print(f"  ⇑ α=+3: ФИЛОСОФИЯ-ПРОЕКТА.md")
