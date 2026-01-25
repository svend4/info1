#!/usr/bin/env python3
"""
Демонстрационная программа карточной системы

Показывает практические примеры использования для пожилого человека,
живущего в частном доме с приусадебным участком.

Уровень абстракции: α=-4 (исполняемый код)
Связь с: α=-3 (конкретные примеры), α=-2 (шаблоны), α=-1 (технические спецификации)
"""

import datetime
from pathlib import Path
import shutil

from card import (
    CardType, CardStatus, CardPriority,
    TaskCard, MedicineCard, RecipeCard,
    ShoppingCard, ContactCard, AppointmentCard, NoteCard
)
from card_manager import CardManager


def demo_header(title: str) -> None:
    """Красивый заголовок для демо"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def demo_task_cards(manager: CardManager) -> dict:
    """Демонстрация карточек-задач"""
    demo_header("📋 ДЕМО 1: Карточки-задачи (TaskCard)")

    # Задача 1: Полить огород
    task1 = TaskCard(
        id="task_20260123_morning_water",
        type=CardType.TASK,
        title="Полить огород",
        created=datetime.datetime.now(),
        modified=datetime.datetime.now(),
        status=CardStatus.PENDING,
        priority=CardPriority.HIGH,
        tags=["огород", "ежедневно", "утро"],
        content="""# Утренний полив огорода

## Что поливать:
- Помидоры (грядки 1-3)
- Огурцы (грядка 4)
- Перец (грядка 5)
- Цветы у входа

## Важно:
- Поливать до 9:00 утра
- Проверить давление в системе полива
- Не забыть закрыть кран после полива
        """,
        due_date=datetime.datetime.now().replace(hour=9, minute=0),
        estimated_time=45,
        location="приусадебный участок"
    )

    # Задача 2: Принять лекарства
    task2 = TaskCard(
        id="task_20260123_medicine_morning",
        type=CardType.TASK,
        title="Принять утренние лекарства",
        created=datetime.datetime.now(),
        modified=datetime.datetime.now(),
        status=CardStatus.PENDING,
        priority=CardPriority.URGENT,
        tags=["здоровье", "лекарства", "утро"],
        linked_cards=["med_20260110_aspirin", "med_20260110_pressure"],
        content="См. связанные карточки с лекарствами",
        due_date=datetime.datetime.now().replace(hour=8, minute=0),
        reminder_time=datetime.datetime.now().replace(hour=7, minute=45)
    )

    # Задача 3: Позвонить дочери
    task3 = TaskCard(
        id="task_20260123_call_daughter",
        type=CardType.TASK,
        title="Позвонить Ольге (дочери)",
        created=datetime.datetime.now(),
        modified=datetime.datetime.now(),
        status=CardStatus.PENDING,
        priority=CardPriority.MEDIUM,
        tags=["семья", "звонок"],
        linked_cards=["contact_20260110_daughter"],
        content="""# Темы для разговора:
- Как дела у внуков
- Договориться о визите на выходные
- Спросить про рецепт варенья
        """
    )

    tasks = [task1, task2, task3]
    for task in tasks:
        manager.save(task)
        print(f"✅ Создана задача: {task.title}")
        print(f"   Приоритет: {task.priority.value}, Статус: {task.status.value}")
        if task.tags:
            print(f"   Теги: {', '.join(task.tags)}")

    return {task.id: task for task in tasks}


def demo_medicine_cards(manager: CardManager) -> dict:
    """Демонстрация карточек-лекарств"""
    demo_header("💊 ДЕМО 2: Карточки-лекарства (MedicineCard)")

    # Лекарство 1: Аспирин
    med1 = MedicineCard(
        id="med_20260110_aspirin",
        type=CardType.MEDICINE,
        title="Аспирин Кардио 100 мг",
        created=datetime.datetime.now(),
        modified=datetime.datetime.now(),
        status=CardStatus.IN_PROGRESS,
        priority=CardPriority.HIGH,
        tags=["сердце", "постоянно", "утро"],
        medication={
            "name": "Аспирин Кардио",
            "active_ingredient": "ацетилсалициловая кислота",
            "dosage": "100 мг",
            "form": "таблетки",
            "manufacturer": "Байер"
        },
        administration={
            "frequency": "1 раз в день",
            "time_of_day": ["утро"],
            "with_food": True,
            "instructions": "Принимать утром после завтрака, запивать водой"
        },
        prescription={
            "doctor": "Сидоров С.С. (кардиолог)",
            "prescribed_date": "2026-01-10",
            "refills_left": 2
        },
        inventory={
            "quantity_current": 25,
            "quantity_per_package": 30,
            "reorder_level": 10,
            "storage_location": "Аптечка в спальне, верхняя полка"
        },
        content="""# Важная информация

## Показания:
Профилактика сердечно-сосудистых заболеваний

## Побочные эффекты:
- Возможна изжога (принимать после еды!)
- При кровотечениях немедленно обратиться к врачу

## Взаимодействия:
Осторожно с другими разжижающими кровь препаратами
        """
    )

    # Лекарство 2: Препарат от давления
    med2 = MedicineCard(
        id="med_20260110_pressure",
        type=CardType.MEDICINE,
        title="Эналаприл 10 мг",
        created=datetime.datetime.now(),
        modified=datetime.datetime.now(),
        status=CardStatus.IN_PROGRESS,
        priority=CardPriority.URGENT,
        tags=["давление", "постоянно", "утро", "вечер"],
        medication={
            "name": "Эналаприл",
            "dosage": "10 мг",
            "form": "таблетки"
        },
        administration={
            "frequency": "2 раза в день",
            "time_of_day": ["утро", "вечер"],
            "instructions": "Утром и вечером в одно и то же время"
        },
        inventory={
            "quantity_current": 42,
            "quantity_per_package": 50,
            "reorder_level": 15,
            "storage_location": "Аптечка в спальне, верхняя полка"
        },
        monitoring={
            "measure_before": "давление",
            "target_range": "120-140 / 70-90"
        }
    )

    meds = [med1, med2]
    for med in meds:
        manager.save(med)
        print(f"✅ Создана карточка лекарства: {med.title}")
        print(f"   Приём: {med.administration['frequency']}")
        print(f"   Остаток: {med.inventory['quantity_current']} шт.")

    return {med.id: med for med in meds}


def demo_contact_cards(manager: CardManager) -> dict:
    """Демонстрация карточек-контактов"""
    demo_header("📞 ДЕМО 3: Карточки-контакты (ContactCard)")

    # Контакт 1: Дочь
    contact1 = ContactCard(
        id="contact_20260110_daughter",
        type=CardType.CONTACT,
        title="Ольга (дочь)",
        created=datetime.datetime.now(),
        modified=datetime.datetime.now(),
        status=CardStatus.IN_PROGRESS,
        priority=CardPriority.HIGH,
        tags=["семья", "близкие"],
        person={
            "full_name": "Петрова Ольга Ивановна",
            "relationship": "дочь",
            "birth_date": "1985-05-15"
        },
        contact_info={
            "phone_mobile": "+7 (912) 345-67-89",
            "phone_work": "+7 (343) 234-56-78",
            "email": "olga.petrova@example.com",
            "address": "г. Екатеринбург, ул. Ленина, д. 25, кв. 10"
        },
        emergency_contact=True,
        content="""# Семья:
- Муж: Андрей
- Дети: Маша (8 лет), Саша (5 лет)

# Важные даты:
- День рождения: 15 мая
- День рождения Маши: 10 сентября
- День рождения Саши: 3 марта

# Заметки:
- Звонить лучше после 19:00 (после работы)
- По выходным приезжают в гости
        """
    )

    # Контакт 2: Врач-кардиолог
    contact2 = ContactCard(
        id="contact_20260110_cardiologist",
        type=CardType.CONTACT,
        title="Доктор Сидоров (кардиолог)",
        created=datetime.datetime.now(),
        modified=datetime.datetime.now(),
        status=CardStatus.IN_PROGRESS,
        priority=CardPriority.HIGH,
        tags=["врачи", "здоровье", "кардиолог"],
        person={
            "full_name": "Сидоров Сергей Сергеевич",
            "relationship": "врач-кардиолог (лечащий)"
        },
        contact_info={
            "phone_mobile": "+7 (912) 456-78-90",
            "phone_work": "+7 (343) 345-67-89",
            "work_address": "Поликлиника №5, каб. 208"
        },
        emergency_contact=True,
        availability={
            "work_hours": "Пн-Пт 9:00-17:00",
            "appointment_required": True
        },
        content="""# Специализация:
Кардиолог, 20 лет опыта

# История лечения:
- 2025: Назначил Аспирин Кардио
- 2024: Корректировка дозы Эналаприла
- 2023: Первичный приём

# Запись на приём:
Через регистратуру: +7 (343) 345-67-89
        """
    )

    contacts = [contact1, contact2]
    for contact in contacts:
        manager.save(contact)
        print(f"✅ Создан контакт: {contact.title}")
        print(f"   Телефон: {contact.contact_info.get('phone_mobile', 'не указан')}")
        print(f"   Экстренный контакт: {'Да' if contact.emergency_contact else 'Нет'}")

    return {contact.id: contact for contact in contacts}


def demo_appointment_cards(manager: CardManager) -> dict:
    """Демонстрация карточек-встреч"""
    demo_header("📅 ДЕМО 4: Карточки-встречи (AppointmentCard)")

    # Встреча 1: Приём у кардиолога
    appt1 = AppointmentCard(
        id="appt_20260125_cardiologist",
        type=CardType.APPOINTMENT,
        title="Приём у кардиолога",
        created=datetime.datetime.now(),
        modified=datetime.datetime.now(),
        status=CardStatus.PENDING,
        priority=CardPriority.HIGH,
        tags=["врачи", "здоровье", "плановый-осмотр"],
        linked_cards=["contact_20260110_cardiologist"],
        event_datetime=datetime.datetime(2026, 1, 25, 10, 30),
        duration=30,
        location="Поликлиника №5, каб. 208",
        participants=["Доктор Сидоров С.С."],
        preparation=[
            "Взять медицинскую карту",
            "Взять результаты анализов",
            "Записать текущее давление за неделю",
            "Взять список принимаемых лекарств"
        ],
        reminder=60,
        content="""# Цель визита:
Плановый осмотр, проверка эффективности лечения

# Вопросы врачу:
- Нужно ли менять дозировку?
- Можно ли добавить витамины?
- Когда следующий визит?

# После приёма:
- Записать рекомендации
- Купить лекарства если назначили новые
- Записаться на следующий приём
        """
    )

    # Встреча 2: Визит внуков
    appt2 = AppointmentCard(
        id="appt_20260126_grandkids",
        type=CardType.APPOINTMENT,
        title="Внуки в гости",
        created=datetime.datetime.now(),
        modified=datetime.datetime.now(),
        status=CardStatus.PENDING,
        priority=CardPriority.MEDIUM,
        tags=["семья", "внуки", "выходные"],
        linked_cards=["contact_20260110_daughter"],
        event_datetime=datetime.datetime(2026, 1, 26, 14, 0),
        duration=240,
        location="дом",
        participants=["Ольга", "Маша", "Саша"],
        preparation=[
            "Купить сладости для детей",
            "Приготовить пирог",
            "Убрать в доме",
            "Подготовить настольные игры"
        ],
        content="""# План:
- 14:00 - Приезд
- 14:30 - Обед
- 15:30 - Прогулка по саду
- 17:00 - Чаепитие с пирогом
- 18:00 - Проводы

# Меню:
- Щи
- Котлеты с картошкой
- Салат из огурцов
- Пирог с яблоками
        """
    )

    appointments = [appt1, appt2]
    for appt in appointments:
        manager.save(appt)
        print(f"✅ Создана встреча: {appt.title}")
        print(f"   Дата: {appt.event_datetime.strftime('%d.%m.%Y %H:%M')}")
        print(f"   Место: {appt.location}")

    return {appt.id: appt for appt in appointments}


def demo_shopping_cards(manager: CardManager) -> dict:
    """Демонстрация карточек-покупок"""
    demo_header("🛒 ДЕМО 5: Карточки-покупки (ShoppingCard)")

    # Покупки 1: Еженедельные продукты
    shop1 = ShoppingCard(
        id="shop_20260123_weekly",
        type=CardType.SHOPPING,
        title="Продукты на неделю",
        created=datetime.datetime.now(),
        modified=datetime.datetime.now(),
        status=CardStatus.PENDING,
        priority=CardPriority.MEDIUM,
        tags=["продукты", "еженедельно"],
        items=[
            {"name": "Хлеб белый", "quantity": 2, "unit": "шт", "category": "хлеб"},
            {"name": "Хлеб черный", "quantity": 1, "unit": "шт", "category": "хлеб"},
            {"name": "Молоко", "quantity": 3, "unit": "л", "category": "молочное"},
            {"name": "Творог", "quantity": 500, "unit": "г", "category": "молочное"},
            {"name": "Яйца", "quantity": 10, "unit": "шт", "category": "молочное"},
            {"name": "Курица", "quantity": 1, "unit": "кг", "category": "мясо"},
            {"name": "Картофель", "quantity": 3, "unit": "кг", "category": "овощи"},
            {"name": "Морковь", "quantity": 0.5, "unit": "кг", "category": "овощи"},
            {"name": "Лук", "quantity": 0.5, "unit": "кг", "category": "овощи"},
            {"name": "Огурцы", "quantity": 1, "unit": "кг", "category": "овощи"},
            {"name": "Помидоры", "quantity": 1, "unit": "кг", "category": "овощи"}
        ],
        store="Магазин 'Пятёрочка'",
        budget=2000.0,
        content="""# Маршрут покупок:
1. Овощной отдел
2. Молочный отдел
3. Мясной отдел
4. Хлебный отдел

# Не забыть:
- Взять сумку-тележку
- Проверить срок годности
- Сохранить чек
        """
    )

    # Покупки 2: Лекарства
    shop2 = ShoppingCard(
        id="shop_20260123_pharmacy",
        type=CardType.SHOPPING,
        title="Покупка лекарств",
        created=datetime.datetime.now(),
        modified=datetime.datetime.now(),
        status=CardStatus.PENDING,
        priority=CardPriority.HIGH,
        tags=["лекарства", "аптека", "здоровье"],
        linked_cards=["med_20260110_aspirin"],
        items=[
            {"name": "Аспирин Кардио 100мг", "quantity": 1, "unit": "уп"},
            {"name": "Витамин D3", "quantity": 1, "unit": "уп"},
            {"name": "Пластырь", "quantity": 1, "unit": "уп"}
        ],
        store="Аптека 'Здоровье'",
        budget=800.0,
        content="Взять рецепт от доктора Сидорова"
    )

    shopping_lists = [shop1, shop2]
    for shop in shopping_lists:
        manager.save(shop)
        print(f"✅ Создан список покупок: {shop.title}")
        print(f"   Магазин: {shop.store}")
        print(f"   Позиций: {len(shop.items)}")
        print(f"   Бюджет: {shop.budget} руб.")

    return {shop.id: shop for shop in shopping_lists}


def demo_note_cards(manager: CardManager) -> dict:
    """Демонстрация карточек-заметок"""
    demo_header("📝 ДЕМО 6: Карточки-заметки (NoteCard)")

    # Заметка 1: Рецепт варенья
    note1 = NoteCard(
        id="note_20260115_jam_recipe",
        type=CardType.NOTE,
        title="Рецепт клубничного варенья",
        created=datetime.datetime.now(),
        modified=datetime.datetime.now(),
        status=CardStatus.ARCHIVED,
        priority=CardPriority.LOW,
        tags=["рецепты", "заготовки", "лето"],
        category="рецепты",
        content="""# Клубничное варенье

## Ингредиенты:
- Клубника - 1 кг
- Сахар - 1 кг
- Лимонная кислота - 1 ч.л.

## Приготовление:
1. Клубнику перебрать, помыть
2. Засыпать сахаром, оставить на 2 часа
3. Довести до кипения, варить 5 минут
4. Остудить, повторить 3 раза
5. На последнем кипячении добавить лимонную кислоту
6. Разлить по банкам

## Заметки:
- Лучше всего использовать некрупную клубнику
- Банки стерилизовать заранее
- Хранить в прохладном месте
        """
    )

    # Заметка 2: Показания давления
    note2 = NoteCard(
        id="note_20260123_pressure_log",
        type=CardType.NOTE,
        title="Дневник давления - январь 2026",
        created=datetime.datetime.now(),
        modified=datetime.datetime.now(),
        status=CardStatus.IN_PROGRESS,
        priority=CardPriority.MEDIUM,
        tags=["здоровье", "давление", "мониторинг"],
        linked_cards=["med_20260110_pressure", "contact_20260110_cardiologist"],
        category="здоровье",
        content="""# Измерения артериального давления

## Неделя 20-26 января:

**20.01 (Пн)**
- Утро: 135/85, пульс 72
- Вечер: 130/80, пульс 68

**21.01 (Вт)**
- Утро: 140/90, пульс 75 ⚠️ (выше нормы)
- Вечер: 132/82, пульс 70

**22.01 (Ср)**
- Утро: 128/78, пульс 68
- Вечер: 125/75, пульс 66

**23.01 (Чт)**
- Утро: 132/80, пульс 71
- Вечер: (будет измерено)

## Заметки:
- 21.01 - давление повышено, возможно из-за стресса (приезжала дочь)
- Самочувствие в целом хорошее
- Лекарства принимаю регулярно
- Показать доктору 25.01
        """
    )

    # Заметка 3: План огорода
    note3 = NoteCard(
        id="note_20260115_garden_plan",
        type=CardType.NOTE,
        title="План посадок огорода на 2026",
        created=datetime.datetime.now(),
        modified=datetime.datetime.now(),
        status=CardStatus.IN_PROGRESS,
        priority=CardPriority.LOW,
        tags=["огород", "планирование", "весна"],
        category="огород",
        content="""# План огорода 2026

## Грядка 1 (южная, солнечная):
- Помидоры (сорт 'Бычье сердце')
- Посадка: начало мая
- Рассада: с 15 марта

## Грядка 2-3:
- Огурцы (сорт 'Зозуля')
- Посадка: середина мая
- Требуют подвязки

## Грядка 4:
- Перец сладкий
- Баклажаны
- Посадка: конец мая (теплолюбивые!)

## Грядка 5:
- Морковь (посев в апреле)
- Свекла (посев в мае)

## Грядка 6:
- Лук на перо
- Чеснок (уже посажен осенью)

## Цветы:
- Петунии у крыльца
- Бархатцы вдоль дорожки
- Георгины у забора

## Семена купить:
- [ ] Помидоры
- [ ] Огурцы
- [ ] Перец
- [x] Морковь (куплено)
- [ ] Петунии
        """
    )

    notes = [note1, note2, note3]
    for note in notes:
        manager.save(note)
        print(f"✅ Создана заметка: {note.title}")
        print(f"   Категория: {note.category}")
        if note.tags:
            print(f"   Теги: {', '.join(note.tags)}")

    return {note.id: note for note in notes}


def demo_search_and_links(manager: CardManager, all_cards: dict) -> None:
    """Демонстрация поиска и связей"""
    demo_header("🔍 ДЕМО 7: Поиск и связи между карточками")

    # Поиск 1: Все карточки со здоровьем
    print("1. Поиск всех карточек по тегу 'здоровье':")
    health_cards = manager.search(tags=["здоровье"])
    print(f"   Найдено: {len(health_cards)} карточек")
    for card in health_cards[:3]:
        print(f"   • [{card.type.value}] {card.title}")

    # Поиск 2: Все задачи с высоким приоритетом
    print("\n2. Поиск всех задач с высоким приоритетом:")
    urgent_tasks = manager.search(
        card_type=CardType.TASK,
        priority=CardPriority.HIGH
    )
    print(f"   Найдено: {len(urgent_tasks)} задач")
    for task in urgent_tasks:
        print(f"   • {task.title} (срок: {task.due_date if hasattr(task, 'due_date') else 'не указан'})")

    # Поиск 3: Все карточки связанные с дочерью
    print("\n3. Карточки, связанные с контактом дочери:")
    daughter_id = "contact_20260110_daughter"
    related = manager.find_related(daughter_id)
    print(f"   Найдено связанных: {len(related)}")
    for card in related:
        print(f"   • [{card.type.value}] {card.title}")

    # Граф связей
    print("\n4. Анализ графа связей:")
    graph = manager.get_connection_graph()
    print(f"   Узлов в графе: {len(graph)}")
    connected = sum(1 for node in graph.values() if node['links'])
    print(f"   Карточек со связями: {connected}")

    # Пример цепочки связей
    print("\n5. Пример цепочки связей:")
    print("   Задача 'Принять лекарства'")
    print("     ├─→ Лекарство 'Аспирин Кардио'")
    print("     │     └─→ Список покупок 'Лекарства в аптеке'")
    print("     └─→ Лекарство 'Эналаприл'")
    print("           └─→ Заметка 'Дневник давления'")
    print("                 └─→ Встреча 'Приём у кардиолога'")
    print("                       └─→ Контакт 'Доктор Сидоров'")


def demo_statistics(manager: CardManager) -> None:
    """Демонстрация статистики"""
    demo_header("📊 ДЕМО 8: Статистика системы")

    all_cards = manager.search(limit=1000)

    print(f"Всего карточек в системе: {len(all_cards)}\n")

    # По типам
    by_type = {}
    for card in all_cards:
        by_type[card.type.value] = by_type.get(card.type.value, 0) + 1

    print("Распределение по типам:")
    for ctype, count in sorted(by_type.items(), key=lambda x: x[1], reverse=True):
        bar = "█" * count
        print(f"  {ctype:12} {bar} {count}")

    # По статусу
    print("\nРаспределение по статусу:")
    by_status = {}
    for card in all_cards:
        by_status[card.status.value] = by_status.get(card.status.value, 0) + 1

    for status, count in sorted(by_status.items(), key=lambda x: x[1], reverse=True):
        bar = "█" * count
        print(f"  {status:12} {bar} {count}")

    # По приоритету
    print("\nРаспределение по приоритету:")
    by_priority = {}
    for card in all_cards:
        by_priority[card.priority.value] = by_priority.get(card.priority.value, 0) + 1

    for priority, count in sorted(by_priority.items(), key=lambda x: x[1], reverse=True):
        bar = "█" * count
        print(f"  {priority:12} {bar} {count}")

    # Теги
    all_tags = set()
    for card in all_cards:
        all_tags.update(card.tags)

    print(f"\nВсего уникальных тегов: {len(all_tags)}")
    print(f"Примеры тегов: {', '.join(list(all_tags)[:10])}")

    # Связи
    total_links = sum(len(card.linked_cards) for card in all_cards)
    print(f"\nВсего связей между карточками: {total_links}")

    avg_links = total_links / len(all_cards) if all_cards else 0
    print(f"Среднее количество связей на карточку: {avg_links:.2f}")


def main():
    """Главная демо-функция"""
    print("\n" + "🌟" * 40)
    print("  ДЕМОНСТРАЦИЯ КАРТОЧНОЙ СИСТЕМЫ")
    print("  Информационно-операционная система для домашнего использования")
    print("  Уровень абстракции: α=-4 (исполняемый код)")
    print("🌟" * 40)

    # Создаем временную директорию для демо
    demo_dir = Path("./demo_cards")
    if demo_dir.exists():
        shutil.rmtree(demo_dir)
    demo_dir.mkdir()

    # Инициализация менеджера
    manager = CardManager(str(demo_dir))

    # Хранилище всех созданных карточек
    all_cards = {}

    # Запуск демо
    all_cards.update(demo_task_cards(manager))
    all_cards.update(demo_medicine_cards(manager))
    all_cards.update(demo_contact_cards(manager))
    all_cards.update(demo_appointment_cards(manager))
    all_cards.update(demo_shopping_cards(manager))
    all_cards.update(demo_note_cards(manager))

    # Демо поиска и связей
    demo_search_and_links(manager, all_cards)

    # Статистика
    demo_statistics(manager)

    # Финал
    demo_header("✅ ДЕМОНСТРАЦИЯ ЗАВЕРШЕНА")
    print(f"Создано {len(all_cards)} карточек разных типов")
    print(f"Карточки сохранены в директории: {demo_dir.absolute()}")
    print("\nВсе карточки успешно созданы, связаны и проиндексированы!")
    print("\nСистема готова к использованию. 🎉")

    print("\n" + "─" * 80)
    print("💡 Следующие шаги:")
    print("   1. Изучите созданные карточки в директории demo_cards/")
    print("   2. Попробуйте CLI: python cli.py list")
    print("   3. Создайте свои карточки: python cli.py create -t task --title 'Моя задача'")
    print("   4. Поищите карточки: python cli.py search 'здоровье'")
    print("─" * 80 + "\n")


if __name__ == "__main__":
    main()
