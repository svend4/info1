#!/usr/bin/env python3
"""
Скрипт инициализации демо-данных для карточной системы

Создает набор примеров карточек всех типов для демонстрации возможностей системы.
Полезно для новых пользователей и тестирования.

α-уровень: -4 (исполняемый код)
"""

import sys
import os
from datetime import datetime, timedelta
from pathlib import Path

# Добавляем путь к card_system в PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent))

from card_manager import CardManager
from card import Card


def create_demo_tasks(manager: CardManager):
    """Создать демонстрационные задачи"""
    print("📋 Создание демонстрационных задач...")

    tasks = [
        {
            "title": "Купить молоко",
            "description": "Купить 2 литра молока в магазине",
            "type": "task",
            "status": "active",
            "priority": "high",
            "tags": ["покупки", "срочно"],
            "due_date": (datetime.now() + timedelta(days=1)).isoformat()
        },
        {
            "title": "Оплатить коммунальные услуги",
            "description": "Оплатить электричество и воду до конца месяца",
            "type": "task",
            "status": "pending",
            "priority": "high",
            "tags": ["финансы", "ежемесячно"],
            "due_date": (datetime.now() + timedelta(days=7)).isoformat()
        },
        {
            "title": "Позвонить маме",
            "description": "Поздравить с днём рождения",
            "type": "task",
            "status": "active",
            "priority": "high",
            "tags": ["семья", "важно"],
            "due_date": (datetime.now() + timedelta(days=3)).isoformat()
        },
        {
            "title": "Записаться к стоматологу",
            "description": "Плановый осмотр раз в полгода",
            "type": "task",
            "status": "pending",
            "priority": "medium",
            "tags": ["здоровье"],
            "due_date": (datetime.now() + timedelta(days=14)).isoformat()
        },
        {
            "title": "Прочитать книгу 'Война и мир'",
            "description": "Закончить читать классику русской литературы",
            "type": "task",
            "status": "active",
            "priority": "low",
            "tags": ["досуг", "чтение"],
            "due_date": (datetime.now() + timedelta(days=60)).isoformat()
        }
    ]

    for task_data in tasks:
        card = Card.from_dict(task_data)
        manager.add_card(card)
        print(f"  ✓ {task_data['title']}")

    print(f"✅ Создано {len(tasks)} задач\n")


def create_demo_medicines(manager: CardManager):
    """Создать демонстрационные карточки лекарств"""
    print("💊 Создание карточек лекарств...")

    medicines = [
        {
            "title": "Эналаприл",
            "description": "От давления, принимать утром и вечером",
            "type": "medicine",
            "status": "active",
            "priority": "high",
            "tags": ["давление", "ежедневно"],
            "dosage": "10 мг",
            "schedule": "09:00, 21:00",
            "doctor": "Кардиолог Иванов И.И."
        },
        {
            "title": "Аспирин",
            "description": "Разжижение крови, по назначению врача",
            "type": "medicine",
            "status": "active",
            "priority": "high",
            "tags": ["сердце", "ежедневно"],
            "dosage": "75 мг",
            "schedule": "20:00",
            "doctor": "Кардиолог Иванов И.И."
        },
        {
            "title": "Витамин D3",
            "description": "Поддержка иммунитета зимой",
            "type": "medicine",
            "status": "active",
            "priority": "medium",
            "tags": ["витамины", "профилактика"],
            "dosage": "2000 МЕ",
            "schedule": "12:00",
            "doctor": "Терапевт Петрова А.В."
        },
        {
            "title": "Парацетамол",
            "description": "При головной боли или температуре",
            "type": "medicine",
            "status": "pending",
            "priority": "low",
            "tags": ["обезболивающее", "при необходимости"],
            "dosage": "500 мг",
            "schedule": "По необходимости",
            "doctor": "Без рецепта"
        }
    ]

    for med_data in medicines:
        card = Card.from_dict(med_data)
        manager.add_card(card)
        print(f"  ✓ {med_data['title']} ({med_data['dosage']})")

    print(f"✅ Создано {len(medicines)} карточек лекарств\n")


def create_demo_contacts(manager: CardManager):
    """Создать демонстрационные контакты"""
    print("👤 Создание контактов...")

    contacts = [
        {
            "title": "Кардиолог Иванов И.И.",
            "description": "Лечащий врач-кардиолог, клиника 'Здоровье'",
            "type": "contact",
            "status": "active",
            "priority": "high",
            "tags": ["врач", "кардиология"],
            "phone": "+7-495-123-45-67",
            "email": "ivanov@clinic-health.ru",
            "address": "Москва, ул. Медицинская, д. 10"
        },
        {
            "title": "Дочь Мария",
            "description": "Моя дочь, живёт в Санкт-Петербурге",
            "type": "contact",
            "status": "active",
            "priority": "high",
            "tags": ["семья", "дети"],
            "phone": "+7-812-987-65-43",
            "email": "maria@email.com",
            "address": "Санкт-Петербург, Невский пр-т, д. 50, кв. 25"
        },
        {
            "title": "Сантехник Петров",
            "description": "Мастер по ремонту сантехники, проверенный",
            "type": "contact",
            "status": "active",
            "priority": "medium",
            "tags": ["услуги", "дом"],
            "phone": "+7-903-111-22-33",
            "email": "",
            "address": ""
        },
        {
            "title": "Соседка Анна (3 этаж)",
            "description": "Добрая соседка, помогает с покупками",
            "type": "contact",
            "status": "active",
            "priority": "medium",
            "tags": ["соседи", "помощь"],
            "phone": "+7-916-555-66-77",
            "email": "",
            "address": "Тот же дом, 3 этаж"
        },
        {
            "title": "Аптека 'Здоровье'",
            "description": "Ближайшая аптека, доставка на дом",
            "type": "contact",
            "status": "active",
            "priority": "high",
            "tags": ["аптека", "доставка"],
            "phone": "+7-495-777-88-99",
            "email": "apteka@health.ru",
            "address": "Москва, ул. Садовая, д. 5"
        }
    ]

    for contact_data in contacts:
        card = Card.from_dict(contact_data)
        manager.add_card(card)
        print(f"  ✓ {contact_data['title']}")

    print(f"✅ Создано {len(contacts)} контактов\n")


def create_demo_meetings(manager: CardManager):
    """Создать демонстрационные встречи"""
    print("📅 Создание встреч...")

    meetings = [
        {
            "title": "Приём у кардиолога",
            "description": "Плановый осмотр, проверка давления",
            "type": "meeting",
            "status": "pending",
            "priority": "high",
            "tags": ["врач", "здоровье"],
            "location": "Клиника 'Здоровье', каб. 205",
            "participants": "Иванов И.И. (кардиолог)",
            "meeting_date": (datetime.now() + timedelta(days=5)).isoformat(),
            "duration": "30 минут"
        },
        {
            "title": "Визит дочери",
            "description": "Мария приезжает в гости на выходные",
            "type": "meeting",
            "status": "pending",
            "priority": "high",
            "tags": ["семья", "выходные"],
            "location": "Дома",
            "participants": "Дочь Мария",
            "meeting_date": (datetime.now() + timedelta(days=10)).isoformat(),
            "duration": "2 дня"
        },
        {
            "title": "Встреча с соседкой",
            "description": "Обсудить ремонт в подъезде",
            "type": "meeting",
            "status": "active",
            "priority": "medium",
            "tags": ["соседи", "дом"],
            "location": "Подъезд, 1 этаж",
            "participants": "Соседка Анна",
            "meeting_date": (datetime.now() + timedelta(days=2)).isoformat(),
            "duration": "15 минут"
        }
    ]

    for meeting_data in meetings:
        card = Card.from_dict(meeting_data)
        manager.add_card(card)
        print(f"  ✓ {meeting_data['title']}")

    print(f"✅ Создано {len(meetings)} встреч\n")


def create_demo_shopping(manager: CardManager):
    """Создать демонстрационные списки покупок"""
    print("🛒 Создание списков покупок...")

    shopping_lists = [
        {
            "title": "Продукты на неделю",
            "description": "Еженедельные покупки в супермаркете",
            "type": "shopping",
            "status": "active",
            "priority": "high",
            "tags": ["еда", "еженедельно"],
            "items": "Молоко 2л, Хлеб, Яйца 10шт, Курица, Овощи (помидоры, огурцы), Фрукты (яблоки, бананы)",
            "budget": "2500 руб",
            "store": "Магазин 'Пятёрочка'"
        },
        {
            "title": "Лекарства из аптеки",
            "description": "Пополнить запас лекарств",
            "type": "shopping",
            "status": "pending",
            "priority": "high",
            "tags": ["лекарства", "здоровье"],
            "items": "Эналаприл 10мг (2 упаковки), Аспирин 75мг (1 упаковка), Витамин D3",
            "budget": "1200 руб",
            "store": "Аптека 'Здоровье'"
        },
        {
            "title": "Хозтовары",
            "description": "Бытовая химия и расходники",
            "type": "shopping",
            "status": "pending",
            "priority": "medium",
            "tags": ["дом", "хозтовары"],
            "items": "Стиральный порошок, Мыло, Туалетная бумага, Мусорные пакеты",
            "budget": "800 руб",
            "store": "Хозяйственный магазин"
        }
    ]

    for shopping_data in shopping_lists:
        card = Card.from_dict(shopping_data)
        manager.add_card(card)
        print(f"  ✓ {shopping_data['title']}")

    print(f"✅ Создано {len(shopping_lists)} списков покупок\n")


def create_demo_notes(manager: CardManager):
    """Создать демонстрационные заметки"""
    print("📝 Создание заметок...")

    notes = [
        {
            "title": "Рецепт бабушкиных пирожков",
            "description": """
Ингредиенты:
- Мука 500г
- Молоко 250мл
- Яйца 2шт
- Дрожжи 10г
- Сахар 2 ст.л.
- Соль 1 ч.л.
- Масло растительное

Приготовление:
1. Развести дрожжи в тёплом молоке
2. Добавить яйца, сахар, соль
3. Постепенно добавить муку
4. Замесить тесто, дать подойти 1 час
5. Сформировать пирожки с начинкой
6. Выпекать при 180°C 25-30 минут
            """,
            "type": "note",
            "status": "active",
            "priority": "low",
            "tags": ["рецепты", "выпечка", "семья"]
        },
        {
            "title": "Полезные телефоны",
            "description": """
Служба 112 — Единый номер экстренных служб
Скорая помощь — 103
Полиция — 102
Пожарная — 101
Газовая служба — 104

ЖКХ: +7-495-000-11-22
Управляющая компания: +7-495-000-33-44
            """,
            "type": "note",
            "status": "active",
            "priority": "high",
            "tags": ["важное", "телефоны", "экстренные"]
        },
        {
            "title": "Идеи для подарков",
            "description": """
Для дочери на день рождения:
- Теплый плед
- Набор хорошего чая
- Фоторамка с семейным фото
- Книга любимого автора

Для внуков:
- Настольные игры
- Конструктор
- Книги с картинками
            """,
            "type": "note",
            "status": "active",
            "priority": "medium",
            "tags": ["подарки", "семья", "идеи"]
        }
    ]

    for note_data in notes:
        card = Card.from_dict(note_data)
        manager.add_card(card)
        print(f"  ✓ {note_data['title']}")

    print(f"✅ Создано {len(notes)} заметок\n")


def main():
    """Главная функция инициализации демо-данных"""
    print("=" * 70)
    print("🎬 ИНИЦИАЛИЗАЦИЯ ДЕМО-ДАННЫХ")
    print("=" * 70)
    print()

    # Путь к директории с данными
    data_dir = Path.home() / '.card_system' / 'cards'

    # Проверка, есть ли уже данные
    if data_dir.exists() and any(data_dir.iterdir()):
        print(f"⚠️  Внимание! Директория {data_dir} уже содержит данные.")
        response = input("Продолжить и добавить демо-данные? (y/n): ")
        if response.lower() != 'y':
            print("Отменено.")
            return
        print()

    # Создать менеджер карточек
    manager = CardManager(str(data_dir))

    # Создать демо-данные всех типов
    create_demo_tasks(manager)
    create_demo_medicines(manager)
    create_demo_contacts(manager)
    create_demo_meetings(manager)
    create_demo_shopping(manager)
    create_demo_notes(manager)

    # Итоговая статистика
    stats = manager.get_stats()
    print("=" * 70)
    print("📊 ИТОГОВАЯ СТАТИСТИКА")
    print("=" * 70)
    print(f"Всего карточек создано: {stats['total']}")
    print(f"Директория с данными: {data_dir}")
    print()

    print("По типам:")
    for card_type, count in stats.get('by_type', {}).items():
        type_icons = {
            'task': '📋',
            'medicine': '💊',
            'contact': '👤',
            'meeting': '📅',
            'shopping': '🛒',
            'note': '📝'
        }
        icon = type_icons.get(card_type, '📄')
        print(f"  {icon} {card_type}: {count}")
    print()

    print("✅ Демо-данные успешно загружены!")
    print()
    print("📝 Следующие шаги:")
    print("  1. Запустите CLI: card-cli list")
    print("  2. Или запустите веб-интерфейс: python3 examples/flask_api_example.py")
    print("  3. Или попробуйте демо: card-demo")
    print()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Прервано пользователем")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
