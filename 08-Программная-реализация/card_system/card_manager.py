"""
Модуль CardManager - управление коллекцией карточек [α=-4]

Этот модуль реализует операции CRUD, поиск, фильтрацию
и управление связями между карточками.

Уровень абстракции: α=-4 (исполняемый код)

Вертикальные связи (⇑ к принципам):
    ⇑ ../02-Информационная-система/Карточки/ТЕХНИЧЕСКИЕ-СПЕЦИФИКАЦИИ.md (α=-1) — API спецификация
    ⇑ ../01-Концепция/ПРИНЦИПЫ-И-ПАТТЕРНЫ.md (α=+2) — принципы координации и композиции
    ⇑ ../01-Концепция/ФИЛОСОФИЯ-ПРОЕКТА.md (α=+3) — философия системного мышления

Горизонтальные связи (↔ на том же уровне):
    ↔ card.py (α=-4) — базовые классы карточек
"""

import json
from pathlib import Path
from typing import List, Optional, Dict, Callable
from datetime import datetime
import re

from card import Card, CardType, CardStatus, Priority, TaskCard, MedicineCard, RecipeCard


class CardIndex:
    """
    Индексы для быстрого поиска карточек

    Реализует индексы из спецификации:
    - По ID (хэш-таблица)
    - По типу
    - По тегам (инвертированный индекс)
    - По дате
    """

    def __init__(self):
        self.by_id: Dict[str, Path] = {}
        self.by_type: Dict[str, List[str]] = {t.value: [] for t in CardType}
        self.by_tag: Dict[str, List[str]] = {}
        self.by_date: Dict[str, List[str]] = {}
        self.graph: Dict[str, Dict] = {}  # Граф связей

    def add(self, card: Card, filepath: Path):
        """Добавить карточку в индексы"""
        card_id = card.id

        # Индекс по ID
        self.by_id[card_id] = filepath

        # Индекс по типу
        self.by_type[card.type.value].append(card_id)

        # Индекс по тегам
        for tag in card.tags:
            if tag not in self.by_tag:
                self.by_tag[tag] = []
            self.by_tag[tag].append(card_id)

        # Индекс по дате
        date_key = card.created.strftime("%Y-%m-%d")
        if date_key not in self.by_date:
            self.by_date[date_key] = []
        self.by_date[date_key].append(card_id)

        # Граф связей
        self.graph[card_id] = {
            "links_to": card.linked_cards,
            "linked_from": []
        }

        # Обновить обратные связи
        for linked_id in card.linked_cards:
            if linked_id in self.graph:
                self.graph[linked_id]["linked_from"].append(card_id)

    def remove(self, card_id: str):
        """Удалить карточку из индексов"""
        if card_id not in self.by_id:
            return

        # Удалить из всех индексов
        del self.by_id[card_id]

        for cards in self.by_type.values():
            if card_id in cards:
                cards.remove(card_id)

        for cards in self.by_tag.values():
            if card_id in cards:
                cards.remove(card_id)

        for cards in self.by_date.values():
            if card_id in cards:
                cards.remove(card_id)

        # Удалить из графа
        if card_id in self.graph:
            # Удалить обратные связи
            for linked_id in self.graph[card_id]["links_to"]:
                if linked_id in self.graph:
                    if card_id in self.graph[linked_id]["linked_from"]:
                        self.graph[linked_id]["linked_from"].remove(card_id)

            del self.graph[card_id]

    def save(self, filepath: Path):
        """Сохранить индексы"""
        data = {
            "by_id": {k: str(v) for k, v in self.by_id.items()},
            "by_type": self.by_type,
            "by_tag": self.by_tag,
            "by_date": self.by_date,
            "graph": self.graph
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    @classmethod
    def load(cls, filepath: Path) -> 'CardIndex':
        """Загрузить индексы"""
        index = cls()

        if not filepath.exists():
            return index

        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        index.by_id = {k: Path(v) for k, v in data.get("by_id", {}).items()}
        index.by_type = data.get("by_type", {t.value: [] for t in CardType})
        index.by_tag = data.get("by_tag", {})
        index.by_date = data.get("by_date", {})
        index.graph = data.get("graph", {})

        return index


class CardManager:
    """
    Менеджер карточек - CRUD и поиск

    Реализует API из технической спецификации.
    """

    def __init__(self, cards_dir: Path):
        """
        Инициализация менеджера

        Args:
            cards_dir: Директория с карточками
        """
        self.cards_dir = Path(cards_dir)
        self.cards_dir.mkdir(parents=True, exist_ok=True)

        # Индексы
        self.index_file = self.cards_dir / ".index.json"
        self.index = CardIndex.load(self.index_file)

        # Кэш (LRU)
        self.cache: Dict[str, Card] = {}
        self.cache_max_size = 1000
        self.cache_access_order: List[str] = []

    def _add_to_cache(self, card: Card):
        """Добавить в кэш"""
        if card.id in self.cache:
            # Переместить в конец (недавно использованные)
            self.cache_access_order.remove(card.id)
            self.cache_access_order.append(card.id)
            return

        # Проверить размер кэша
        if len(self.cache) >= self.cache_max_size:
            # Удалить LRU
            lru_id = self.cache_access_order.pop(0)
            del self.cache[lru_id]

        self.cache[card.id] = card
        self.cache_access_order.append(card.id)

    def _get_from_cache(self, card_id: str) -> Optional[Card]:
        """Получить из кэша"""
        if card_id in self.cache:
            # Переместить в конец
            self.cache_access_order.remove(card_id)
            self.cache_access_order.append(card_id)
            return self.cache[card_id]
        return None

    # CRUD операции

    def create(self, card: Card) -> Card:
        """
        Создать новую карточку

        Args:
            card: Карточка для создания

        Returns:
            Card: Созданная карточка
        """
        # Сохранить в файл
        filepath = card.save(self.cards_dir)

        # Добавить в индекс
        self.index.add(card, filepath)
        self.index.save(self.index_file)

        # Добавить в кэш
        self._add_to_cache(card)

        return card

    def read(self, card_id: str) -> Optional[Card]:
        """
        Прочитать карточку

        Args:
            card_id: ID карточки

        Returns:
            Card или None
        """
        # Проверить кэш
        cached = self._get_from_cache(card_id)
        if cached:
            return cached

        # Проверить индекс
        if card_id not in self.index.by_id:
            return None

        filepath = self.index.by_id[card_id]

        # Загрузить из файла
        card = Card.load(filepath)

        # Добавить в кэш
        self._add_to_cache(card)

        return card

    def update(self, card_id: str, **updates) -> Optional[Card]:
        """
        Обновить карточку

        Args:
            card_id: ID карточки
            **updates: Поля для обновления

        Returns:
            Card или None
        """
        card = self.read(card_id)
        if not card:
            return None

        # Обновить поля
        card.update(**updates)

        # Сохранить
        filepath = self.index.by_id[card_id]
        card.save(self.cards_dir)

        # Обновить кэш
        self._add_to_cache(card)

        return card

    def delete(self, card_id: str, soft_delete: bool = True) -> bool:
        """
        Удалить карточку

        Args:
            card_id: ID карточки
            soft_delete: Если True, архивировать, иначе удалить

        Returns:
            bool: Успешность операции
        """
        card = self.read(card_id)
        if not card:
            return False

        if soft_delete:
            # Архивировать
            card.status = CardStatus.ARCHIVED
            filepath = self.index.by_id[card_id]
            card.save(self.cards_dir)
        else:
            # Физическое удаление
            filepath = self.index.by_id[card_id]
            filepath.unlink(missing_ok=True)

            # Удалить из индекса
            self.index.remove(card_id)
            self.index.save(self.index_file)

            # Удалить из кэша
            if card_id in self.cache:
                del self.cache[card_id]
                self.cache_access_order.remove(card_id)

        return True

    # Поиск и фильтрация

    def search(
        self,
        query: Optional[str] = None,
        card_type: Optional[CardType] = None,
        tags: Optional[List[str]] = None,
        status: Optional[CardStatus] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        sort_by: str = "modified",
        limit: int = 100
    ) -> List[Card]:
        """
        Поиск карточек по критериям

        Args:
            query: Текстовый поиск
            card_type: Фильтр по типу
            tags: Список тегов (ИЛИ)
            status: Фильтр по статусу
            date_from: Начальная дата
            date_to: Конечная дата
            sort_by: Поле сортировки
            limit: Максимум результатов

        Returns:
            List[Card]: Найденные карточки
        """
        # Начальный набор
        if card_type:
            candidate_ids = set(self.index.by_type[card_type.value])
        else:
            candidate_ids = set(self.index.by_id.keys())

        # Фильтр по тегам (ИЛИ)
        if tags:
            tag_ids = set()
            for tag in tags:
                if tag in self.index.by_tag:
                    tag_ids.update(self.index.by_tag[tag])
            candidate_ids &= tag_ids

        # Фильтр по датам
        if date_from or date_to:
            date_ids = set()
            for date_key, ids in self.index.by_date.items():
                date = datetime.strptime(date_key, "%Y-%m-%d")
                if date_from and date < date_from:
                    continue
                if date_to and date > date_to:
                    continue
                date_ids.update(ids)
            candidate_ids &= date_ids

        # Загрузить карточки
        cards = []
        for card_id in candidate_ids:
            card = self.read(card_id)
            if not card:
                continue

            # Фильтр по статусу
            if status and card.status != status:
                continue

            # Текстовый поиск
            if query:
                query_lower = query.lower()
                if (query_lower not in card.title.lower() and
                    query_lower not in card.content.lower()):
                    continue

            cards.append(card)

        # Сортировка
        if sort_by == "created":
            cards.sort(key=lambda c: c.created, reverse=True)
        elif sort_by == "modified":
            cards.sort(key=lambda c: c.modified, reverse=True)
        elif sort_by == "title":
            cards.sort(key=lambda c: c.title)

        # Лимит
        return cards[:limit]

    def find_by_tag(self, tag: str) -> List[Card]:
        """Найти все карточки с тегом"""
        if tag not in self.index.by_tag:
            return []

        return [self.read(card_id) for card_id in self.index.by_tag[tag]]

    def find_by_type(self, card_type: CardType) -> List[Card]:
        """Найти все карточки типа"""
        return [
            self.read(card_id)
            for card_id in self.index.by_type[card_type.value]
        ]

    # Работа со связями

    def link_cards(
        self,
        card_id_from: str,
        card_id_to: str,
        link_type: str = "related"
    ) -> bool:
        """
        Создать связь между карточками

        Args:
            card_id_from: ID исходной карточки
            card_id_to: ID целевой карточки
            link_type: Тип связи

        Returns:
            bool: Успешность
        """
        card_from = self.read(card_id_from)
        if not card_from:
            return False

        card_from.link_to(card_id_to)

        # Сохранить
        filepath = self.index.by_id[card_id_from]
        card_from.save(self.cards_dir)

        # Обновить граф в индексе
        if card_id_from in self.index.graph:
            self.index.graph[card_id_from]["links_to"].append(card_id_to)
        if card_id_to in self.index.graph:
            self.index.graph[card_id_to]["linked_from"].append(card_id_from)

        self.index.save(self.index_file)

        return True

    def get_linked_cards(
        self,
        card_id: str,
        direction: str = "to"
    ) -> List[Card]:
        """
        Получить связанные карточки

        Args:
            card_id: ID карточки
            direction: Направление ("to" или "from")

        Returns:
            List[Card]: Связанные карточки
        """
        if card_id not in self.index.graph:
            return []

        if direction == "to":
            linked_ids = self.index.graph[card_id]["links_to"]
        else:
            linked_ids = self.index.graph[card_id]["linked_from"]

        return [self.read(lid) for lid in linked_ids if self.read(lid)]

    # Статистика

    def get_stats(self) -> Dict:
        """Получить статистику по карточкам"""
        total = len(self.index.by_id)

        by_type = {
            t: len(ids)
            for t, ids in self.index.by_type.items()
        }

        # Популярные теги
        popular_tags = sorted(
            self.index.by_tag.items(),
            key=lambda x: len(x[1]),
            reverse=True
        )[:10]

        return {
            "total_cards": total,
            "by_type": by_type,
            "popular_tags": [(tag, len(ids)) for tag, ids in popular_tags],
            "total_tags": len(self.index.by_tag),
            "cache_size": len(self.cache),
            "graph_nodes": len(self.index.graph)
        }


# Демонстрация
if __name__ == "__main__":
    from pathlib import Path

    print("=== Демонстрация CardManager [α=-4] ===\n")

    # Создать менеджер
    manager = CardManager(Path("/tmp/cards_demo"))

    # 1. Создать несколько карточек
    print("1. Создание карточек:\n")

    task1 = TaskCard.create_task(
        title="Утренняя зарядка",
        content="Ежедневная зарядка 15 минут",
        tags=["здоровье", "утро"],
        priority=Priority.MEDIUM
    )
    manager.create(task1)
    print(f"   ✓ Создана задача: {task1.title}")

    task2 = TaskCard.create_task(
        title="Позвонить внукам",
        content="Воскресный видеозвонок",
        tags=["семья", "воскресенье"],
        priority=Priority.HIGH
    )
    manager.create(task2)
    print(f"   ✓ Создана задача: {task2.title}")

    medicine = MedicineCard.create_medicine(
        title="Эналаприл 10мг",
        medication_name="Эналаприл",
        dosage="10 мг",
        frequency="1 раз в день",
        tags=["здоровье", "лекарства"]
    )
    manager.create(medicine)
    print(f"   ✓ Создано лекарство: {medicine.title}")

    recipe = RecipeCard.create_recipe(
        title="Овсяная каша",
        content="Полезный завтрак",
        servings=1,
        tags=["завтрак", "здоровое-питание"]
    )
    manager.create(recipe)
    print(f"   ✓ Создан рецепт: {recipe.title}\n")

    # 2. Поиск
    print("2. Поиск по тегу 'здоровье':")
    health_cards = manager.find_by_tag("здоровье")
    for card in health_cards:
        print(f"   - {card.title} ({card.type.value})")
    print()

    # 3. Поиск по типу
    print("3. Все задачи:")
    tasks = manager.find_by_type(CardType.TASK)
    for task in tasks:
        print(f"   - {task.title}")
    print()

    # 4. Связывание
    print("4. Связывание карточек:")
    manager.link_cards(task1.id, medicine.id)
    print(f"   '{task1.title}' → '{medicine.title}'")

    linked = manager.get_linked_cards(task1.id)
    print(f"   Связанные карточки: {[c.title for c in linked]}\n")

    # 5. Обновление
    print("5. Обновление карточки:")
    manager.update(task1.id, status=CardStatus.COMPLETED)
    updated = manager.read(task1.id)
    print(f"   Новый статус '{task1.title}': {updated.status.value}\n")

    # 6. Статистика
    print("6. Статистика:")
    stats = manager.get_stats()
    print(f"   Всего карточек: {stats['total_cards']}")
    print(f"   По типам: {stats['by_type']}")
    print(f"   Популярные теги: {stats['popular_tags'][:5]}")
    print(f"   Размер кэша: {stats['cache_size']}\n")

    # 7. Текстовый поиск
    print("7. Текстовый поиск 'зарядка':")
    results = manager.search(query="зарядка")
    for card in results:
        print(f"   - {card.title}\n")

    print("=== Демонстрация завершена ===")
