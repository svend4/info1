#!/usr/bin/env python3
"""
Юнит-тесты для карточной системы

Покрытие:
- card.py: создание карточек
- card_manager.py: CRUD, поиск
- Все 7 типов карточек

Использует unittest (стандартная библиотека, без внешних зависимостей)
"""

import unittest
import tempfile
import shutil
import datetime
from pathlib import Path

from card import (
    Card, TaskCard, MedicineCard, RecipeCard, ShoppingCard,
    ContactCard, AppointmentCard, NoteCard,
    CardType, CardStatus, Priority
)
from card_manager import CardManager


class TestCardCreation(unittest.TestCase):
    """Тесты создания карточек"""

    def test_generate_id_format(self):
        """Проверка формата генерируемого ID"""
        card_id = Card.generate_id()
        self.assertTrue(card_id.startswith('card_'))
        parts = card_id.split('_')
        self.assertEqual(len(parts), 4)  # card_YYYYMMDD_HHMMSS_xxxx

    def test_generate_id_uniqueness(self):
        """Проверка уникальности ID"""
        ids = [Card.generate_id() for _ in range(100)]
        self.assertEqual(len(ids), len(set(ids)), "IDs должны быть уникальными")

    def test_task_card_creation(self):
        """Создание карточки-задачи"""
        task = TaskCard(
            id=Card.generate_id(),
            type=CardType.TASK,
            title="Тестовая задача",
            created=datetime.datetime.now(),
            modified=datetime.datetime.now(),
            status=CardStatus.PENDING,
            priority=Priority.HIGH,
            tags=["тест"],
            due_date=datetime.datetime.now() + datetime.timedelta(days=1)
        )

        self.assertEqual(task.type, CardType.TASK)
        self.assertEqual(task.title, "Тестовая задача")
        self.assertEqual(task.status, CardStatus.PENDING)
        self.assertEqual(task.priority, Priority.HIGH)
        self.assertIn("тест", task.tags)
        self.assertIsNotNone(task.due_date)

    def test_medicine_card_creation(self):
        """Создание карточки-лекарства"""
        medicine = MedicineCard(
            id=Card.generate_id(),
            type=CardType.MEDICINE,
            title="Тестовое лекарство",
            created=datetime.datetime.now(),
            modified=datetime.datetime.now(),
            medication_name='Аспирин',
            dosage='500мг',
            frequency='2 раза в день'
        )

        self.assertEqual(medicine.type, CardType.MEDICINE)
        self.assertEqual(medicine.medication_name, 'Аспирин')
        self.assertEqual(medicine.dosage, '500мг')
        self.assertEqual(medicine.frequency, '2 раза в день')

    def test_all_card_types(self):
        """Проверка создания всех типов карточек"""
        now = datetime.datetime.now()

        cards = [
            TaskCard(id=Card.generate_id(), type=CardType.TASK, title="Task", created=now, modified=now),
            MedicineCard(id=Card.generate_id(), type=CardType.MEDICINE, title="Med", created=now, modified=now, medication_name="Med", dosage="10mg", frequency="1x"),
            RecipeCard(id=Card.generate_id(), type=CardType.RECIPE, title="Recipe", created=now, modified=now),
            ShoppingCard(id=Card.generate_id(), type=CardType.SHOPPING, title="Shop", created=now, modified=now),
            ContactCard(id=Card.generate_id(), type=CardType.CONTACT, title="Contact", created=now, modified=now),
            AppointmentCard(id=Card.generate_id(), type=CardType.APPOINTMENT, title="Appt", created=now, modified=now),
            NoteCard(id=Card.generate_id(), type=CardType.NOTE, title="Note", created=now, modified=now)
        ]

        self.assertEqual(len(cards), 7)
        for card in cards:
            self.assertIsInstance(card, Card)
            self.assertIsNotNone(card.id)
            self.assertIsNotNone(card.title)


class TestCardManager(unittest.TestCase):
    """Тесты CardManager"""

    def setUp(self):
        """Создание временной директории для тестов"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.manager = CardManager(cards_dir=self.temp_dir)

    def tearDown(self):
        """Удаление временной директории"""
        shutil.rmtree(self.temp_dir)

    def test_create_and_read(self):
        """Создание и чтение карточки"""
        card = TaskCard(
            id=Card.generate_id(),
            type=CardType.TASK,
            title="Тестовая задача",
            created=datetime.datetime.now(),
            modified=datetime.datetime.now()
        )

        # Создание
        created = self.manager.create(card)
        self.assertIsNotNone(created)
        self.assertEqual(card.id, created.id)

        # Чтение
        loaded = self.manager.read(card.id)
        self.assertIsNotNone(loaded)
        self.assertEqual(card.id, loaded.id)
        self.assertEqual(card.title, loaded.title)

    def test_update(self):
        """Обновление карточки"""
        card = TaskCard(
            id=Card.generate_id(),
            type=CardType.TASK,
            title="Оригинальное название",
            created=datetime.datetime.now(),
            modified=datetime.datetime.now()
        )

        self.manager.create(card)

        # Обновление
        updated = self.manager.update(card.id, title="Новое название")
        self.assertIsNotNone(updated)
        self.assertEqual(updated.title, "Новое название")

        # Проверка, что изменения сохранились
        loaded = self.manager.read(card.id)
        self.assertEqual(loaded.title, "Новое название")

    def test_delete(self):
        """Удаление карточки (soft delete - архивирование)"""
        card = TaskCard(
            id=Card.generate_id(),
            type=CardType.TASK,
            title="Задача для удаления",
            created=datetime.datetime.now(),
            modified=datetime.datetime.now()
        )

        self.manager.create(card)
        self.assertIsNotNone(self.manager.read(card.id))

        # Soft delete (по умолчанию)
        result = self.manager.delete(card.id)
        self.assertTrue(result)

        # Проверка, что карточка архивирована (а не удалена полностью)
        deleted = self.manager.read(card.id)
        self.assertIsNotNone(deleted)
        self.assertEqual(deleted.status, CardStatus.ARCHIVED)

    def test_search_by_query(self):
        """Поиск по тексту"""
        # Создать несколько карточек
        card1 = TaskCard(
            id=Card.generate_id(),
            type=CardType.TASK,
            title="Купить молоко",
            created=datetime.datetime.now(),
            modified=datetime.datetime.now()
        )
        card2 = TaskCard(
            id=Card.generate_id(),
            type=CardType.TASK,
            title="Купить хлеб",
            created=datetime.datetime.now(),
            modified=datetime.datetime.now()
        )
        card3 = TaskCard(
            id=Card.generate_id(),
            type=CardType.TASK,
            title="Позвонить врачу",
            created=datetime.datetime.now(),
            modified=datetime.datetime.now()
        )

        self.manager.create(card1)
        self.manager.create(card2)
        self.manager.create(card3)

        # Поиск по слову "купить"
        results = self.manager.search(query="купить")
        self.assertGreaterEqual(len(results), 2)

        titles = [c.title for c in results]
        self.assertIn("Купить молоко", titles)
        self.assertIn("Купить хлеб", titles)

    def test_search_by_type(self):
        """Поиск по типу карточки"""
        task = TaskCard(
            id=Card.generate_id(),
            type=CardType.TASK,
            title="Задача",
            created=datetime.datetime.now(),
            modified=datetime.datetime.now()
        )
        medicine = MedicineCard(
            id=Card.generate_id(),
            type=CardType.MEDICINE,
            title="Лекарство",
            created=datetime.datetime.now(),
            modified=datetime.datetime.now(),
            medication_name="Аспирин",
            dosage="500мг",
            frequency="1x"
        )

        self.manager.create(task)
        self.manager.create(medicine)

        # Поиск задач
        tasks = self.manager.search(card_type=CardType.TASK)
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0].type, CardType.TASK)

        # Поиск лекарств
        medicines = self.manager.search(card_type=CardType.MEDICINE)
        self.assertEqual(len(medicines), 1)
        self.assertEqual(medicines[0].type, CardType.MEDICINE)

    def test_search_by_tags(self):
        """Поиск по тегам"""
        card1 = TaskCard(
            id=Card.generate_id(),
            type=CardType.TASK,
            title="Задача 1",
            created=datetime.datetime.now(),
            modified=datetime.datetime.now(),
            tags=["работа", "срочно"]
        )
        card2 = TaskCard(
            id=Card.generate_id(),
            type=CardType.TASK,
            title="Задача 2",
            created=datetime.datetime.now(),
            modified=datetime.datetime.now(),
            tags=["дом", "срочно"]
        )
        card3 = TaskCard(
            id=Card.generate_id(),
            type=CardType.TASK,
            title="Задача 3",
            created=datetime.datetime.now(),
            modified=datetime.datetime.now(),
            tags=["работа"]
        )

        self.manager.create(card1)
        self.manager.create(card2)
        self.manager.create(card3)

        # Поиск по тегу "срочно"
        urgent = self.manager.search(tags=["срочно"])
        self.assertEqual(len(urgent), 2)

        # Поиск по тегу "работа"
        work = self.manager.search(tags=["работа"])
        self.assertEqual(len(work), 2)

    def test_search_by_status(self):
        """Поиск по статусу"""
        card1 = TaskCard(
            id=Card.generate_id(),
            type=CardType.TASK,
            title="PENDING задача",
            created=datetime.datetime.now(),
            modified=datetime.datetime.now(),
            status=CardStatus.PENDING
        )
        card2 = TaskCard(
            id=Card.generate_id(),
            type=CardType.TASK,
            title="В работе",
            created=datetime.datetime.now(),
            modified=datetime.datetime.now(),
            status=CardStatus.IN_PROGRESS
        )

        self.manager.create(card1)
        self.manager.create(card2)

        # Поиск PENDING
        pending = self.manager.search(status=CardStatus.PENDING)
        self.assertEqual(len(pending), 1)
        self.assertEqual(pending[0].status, CardStatus.PENDING)


class TestConnectionGraph(unittest.TestCase):
    """Тесты графа связей"""

    def setUp(self):
        """Создание временной директории для тестов"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.manager = CardManager(cards_dir=self.temp_dir)

    def tearDown(self):
        """Удаление временной директории"""
        shutil.rmtree(self.temp_dir)

    def test_link_cards(self):
        """Связывание карточек"""
        card1 = TaskCard(
            id=Card.generate_id(),
            type=CardType.TASK,
            title="Задача 1",
            created=datetime.datetime.now(),
            modified=datetime.datetime.now()
        )
        card2 = TaskCard(
            id=Card.generate_id(),
            type=CardType.TASK,
            title="Задача 2",
            created=datetime.datetime.now(),
            modified=datetime.datetime.now()
        )

        self.manager.create(card1)
        self.manager.create(card2)

        # Связать карточки
        self.manager.link_cards(card1.id, card2.id)

        # Загрузить и проверить связь
        loaded = self.manager.read(card1.id)
        self.assertIn(card2.id, loaded.linked_cards)

    def test_get_linked_cards(self):
        """Получение связанных карточек"""
        card_a = TaskCard(
            id=Card.generate_id(),
            type=CardType.TASK,
            title="A",
            created=datetime.datetime.now(),
            modified=datetime.datetime.now()
        )
        card_b = TaskCard(
            id=Card.generate_id(),
            type=CardType.TASK,
            title="B",
            created=datetime.datetime.now(),
            modified=datetime.datetime.now()
        )

        self.manager.create(card_a)
        self.manager.create(card_b)
        self.manager.link_cards(card_a.id, card_b.id)

        # Получить связанные карточки (link_cards создаёт двунаправленную связь)
        linked = self.manager.get_linked_cards(card_a.id)
        self.assertGreaterEqual(len(linked), 1)

        # Проверить, что card_b в списке связанных
        linked_ids = [c.id for c in linked]
        self.assertIn(card_b.id, linked_ids)


class TestEdgeCases(unittest.TestCase):
    """Тесты граничных случаев и обработки ошибок"""

    def setUp(self):
        """Создание временной директории для тестов"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.manager = CardManager(cards_dir=self.temp_dir)

    def tearDown(self):
        """Удаление временной директории"""
        shutil.rmtree(self.temp_dir)

    def test_read_nonexistent_card(self):
        """Чтение несуществующей карточки"""
        result = self.manager.read("nonexistent_id")
        self.assertIsNone(result)

    def test_delete_nonexistent_card(self):
        """Удаление несуществующей карточки"""
        result = self.manager.delete("nonexistent_id")
        self.assertFalse(result)

    def test_search_empty_database(self):
        """Поиск в пустой базе"""
        results = self.manager.search(query="что-то")
        self.assertEqual(len(results), 0)

    def test_empty_tags(self):
        """Карточка с пустым списком тегов"""
        card = TaskCard(
            id=Card.generate_id(),
            type=CardType.TASK,
            title="Без тегов",
            created=datetime.datetime.now(),
            modified=datetime.datetime.now(),
            tags=[]
        )

        self.manager.create(card)
        loaded = self.manager.read(card.id)

        self.assertEqual(loaded.tags, [])

    def test_unicode_in_title(self):
        """Unicode символы в заголовке"""
        card = TaskCard(
            id=Card.generate_id(),
            type=CardType.TASK,
            title="Тест с эмодзи и кириллицей",
            created=datetime.datetime.now(),
            modified=datetime.datetime.now()
        )

        self.manager.create(card)
        loaded = self.manager.read(card.id)

        self.assertIn("кириллицей", loaded.title)


class TestPerformance(unittest.TestCase):
    """Тесты производительности (базовые)"""

    def setUp(self):
        """Создание временной директории для тестов"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.manager = CardManager(cards_dir=self.temp_dir)

    def tearDown(self):
        """Удаление временной директории"""
        shutil.rmtree(self.temp_dir)

    def test_create_100_cards(self):
        """Создание 100 карточек"""
        import time

        start = time.time()

        for i in range(100):
            card = TaskCard(
                id=Card.generate_id(),
                type=CardType.TASK,
                title=f"Задача {i}",
                created=datetime.datetime.now(),
                modified=datetime.datetime.now()
            )
            self.manager.create(card)

        elapsed = time.time() - start

        # Должно быть быстрее 10 секунд
        self.assertLess(elapsed, 10.0, f"Создание 100 карточек заняло {elapsed:.2f}с")

    def test_search_100_cards(self):
        """Поиск по 100 карточкам"""
        import time

        # Создать 100 карточек
        for i in range(100):
            card = TaskCard(
                id=Card.generate_id(),
                type=CardType.TASK,
                title=f"Задача номер {i}",
                created=datetime.datetime.now(),
                modified=datetime.datetime.now(),
                tags=["тест", f"номер{i}"]
            )
            self.manager.create(card)

        # Поиск
        start = time.time()
        results = self.manager.search(query="задача")
        elapsed = time.time() - start

        self.assertGreater(len(results), 0)
        self.assertLess(elapsed, 2.0, f"Поиск занял {elapsed:.2f}с")


def run_tests():
    """Запуск всех тестов"""
    # Создать test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Добавить все тест-классы
    suite.addTests(loader.loadTestsFromTestCase(TestCardCreation))
    suite.addTests(loader.loadTestsFromTestCase(TestCardManager))
    suite.addTests(loader.loadTestsFromTestCase(TestConnectionGraph))
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeCases))
    suite.addTests(loader.loadTestsFromTestCase(TestPerformance))

    # Запустить
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Статистика
    print("\n" + "=" * 70)
    print(f"Тестов запущено: {result.testsRun}")
    print(f"Успешно: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Провалено: {len(result.failures)}")
    print(f"Ошибок: {len(result.errors)}")
    print("=" * 70)

    return result.wasSuccessful()


if __name__ == '__main__':
    import sys
    success = run_tests()
    sys.exit(0 if success else 1)
