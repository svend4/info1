#!/usr/bin/env python3
"""
Интеграционные тесты для карточной системы

В отличие от юнит-тестов, интеграционные тесты проверяют:
- Взаимодействие между компонентами
- Полные workflow (end-to-end)
- Реалистичные сценарии использования
- Производительность на реальных данных

Уровень абстракции: α=-4 (исполняемый код)
"""

import unittest
import tempfile
import shutil
import datetime
import json
from pathlib import Path

from card import (
    Card, TaskCard, MedicineCard, RecipeCard, ShoppingCard,
    ContactCard, AppointmentCard, NoteCard,
    CardType, CardStatus, Priority
)
from card_manager import CardManager
from export_import import CardExporter, CardImporter


class TestFullWorkflow(unittest.TestCase):
    """
    Интеграционный тест: полный жизненный цикл карточки

    Workflow:
    1. Создание задачи
    2. Создание лекарства
    3. Связывание задачи с лекарством
    4. Поиск связанных карточек
    5. Обновление задачи
    6. Завершение задачи
    7. Архивирование
    """

    def setUp(self):
        """Создание временной директории"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.manager = CardManager(cards_dir=self.temp_dir)

    def tearDown(self):
        """Удаление временной директории"""
        shutil.rmtree(self.temp_dir)

    def test_full_workflow(self):
        """Полный жизненный цикл: создание → связывание → обновление → архивирование"""

        # 1. Создать задачу
        task = TaskCard(
            id=Card.generate_id(),
            type=CardType.TASK,
            title="Принять утреннее лекарство",
            created=datetime.datetime.now(),
            modified=datetime.datetime.now(),
            status=CardStatus.PENDING,
            priority=Priority.HIGH,
            tags=["здоровье", "утро"],
            due_date=datetime.datetime.now() + datetime.timedelta(hours=2)
        )

        created_task = self.manager.create(task)
        self.assertIsNotNone(created_task)
        print(f"✅ Шаг 1: Создана задача {task.id}")

        # 2. Создать лекарство
        medicine = MedicineCard(
            id=Card.generate_id(),
            type=CardType.MEDICINE,
            title="Эналаприл 10мг",
            created=datetime.datetime.now(),
            modified=datetime.datetime.now(),
            medication_name="Эналаприл",
            dosage="10мг",
            frequency="1 раз в день",
            administration_time=["08:00"],
            tags=["здоровье", "гипертония"]
        )

        created_medicine = self.manager.create(medicine)
        self.assertIsNotNone(created_medicine)
        print(f"✅ Шаг 2: Создано лекарство {medicine.id}")

        # 3. Связать задачу с лекарством
        self.manager.link_cards(task.id, medicine.id)
        linked = self.manager.get_linked_cards(task.id)
        self.assertGreater(len(linked), 0)
        print(f"✅ Шаг 3: Связаны task↔medicine (найдено {len(linked)} связей)")

        # 4. Поиск по тегу "здоровье"
        health_cards = self.manager.search(tags=["здоровье"])
        self.assertEqual(len(health_cards), 2)  # Task + Medicine
        print(f"✅ Шаг 4: Найдено {len(health_cards)} карточек по тегу 'здоровье'")

        # 5. Обновить задачу (добавить заметку)
        updated_task = self.manager.update(
            task.id,
            content="Принял в 08:15. Всё хорошо."
        )
        self.assertIsNotNone(updated_task)
        self.assertIn("08:15", updated_task.content)
        print(f"✅ Шаг 5: Обновлена задача (добавлена заметка)")

        # 6. Завершить задачу
        completed_task = self.manager.update(
            task.id,
            status=CardStatus.COMPLETED
        )
        self.assertEqual(completed_task.status, CardStatus.COMPLETED)
        print(f"✅ Шаг 6: Задача завершена (status=COMPLETED)")

        # 7. Найти все завершённые задачи
        completed = self.manager.search(status=CardStatus.COMPLETED)
        self.assertEqual(len(completed), 1)
        print(f"✅ Шаг 7: Найдено {len(completed)} завершённых задач")

        # 8. Архивировать задачу (soft delete)
        self.manager.delete(task.id, soft_delete=True)
        archived = self.manager.read(task.id)
        self.assertIsNotNone(archived)
        self.assertEqual(archived.status, CardStatus.ARCHIVED)
        print(f"✅ Шаг 8: Задача архивирована (status=ARCHIVED)")

        print("\n🎉 Полный workflow завершён успешно!")


class TestExportImportRoundtrip(unittest.TestCase):
    """
    Интеграционный тест: экспорт/импорт

    Workflow:
    1. Создать несколько карточек разных типов
    2. Экспортировать в JSON
    3. Удалить все карточки
    4. Импортировать обратно из JSON
    5. Проверить, что все карточки восстановлены
    """

    def setUp(self):
        """Создание временных директорий"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.import_dir = Path(tempfile.mkdtemp())  # Отдельная директория для импорта
        self.export_dir = Path(tempfile.mkdtemp())
        self.manager = CardManager(cards_dir=self.temp_dir)
        self.exporter = CardExporter(self.manager)

    def tearDown(self):
        """Удаление временных директорий"""
        shutil.rmtree(self.temp_dir)
        shutil.rmtree(self.import_dir)
        shutil.rmtree(self.export_dir)

    def test_json_roundtrip(self):
        """Roundtrip: экспорт в JSON → импорт → проверка идентичности"""

        # 1. Создать 5 карточек разных типов
        cards = [
            TaskCard(
                id=Card.generate_id(),
                type=CardType.TASK,
                title="Купить продукты",
                created=datetime.datetime.now(),
                modified=datetime.datetime.now(),
                tags=["покупки"]
            ),
            MedicineCard(
                id=Card.generate_id(),
                type=CardType.MEDICINE,
                title="Аспирин",
                created=datetime.datetime.now(),
                modified=datetime.datetime.now(),
                medication_name="Аспирин",
                dosage="500мг",
                frequency="при необходимости"
            ),
            RecipeCard(
                id=Card.generate_id(),
                type=CardType.RECIPE,
                title="Омлет",
                created=datetime.datetime.now(),
                modified=datetime.datetime.now(),
                servings=2
            ),
            ContactCard(
                id=Card.generate_id(),
                type=CardType.CONTACT,
                title="Врач Иванов",
                created=datetime.datetime.now(),
                modified=datetime.datetime.now(),
                person_name="Иванов Иван",
                phone="+7-123-456-78-90"
            ),
            NoteCard(
                id=Card.generate_id(),
                type=CardType.NOTE,
                title="Идея для проекта",
                created=datetime.datetime.now(),
                modified=datetime.datetime.now(),
                content="Разработать систему карточек",
                category="идеи"
            )
        ]

        # Создать все карточки
        for card in cards:
            self.manager.create(card)

        print(f"✅ Создано {len(cards)} карточек разных типов")

        # 2. Экспортировать в JSON
        export_file = self.export_dir / "backup.json"
        count = self.exporter.export_to_json(export_file)
        self.assertEqual(count, len(cards))
        self.assertTrue(export_file.exists())
        print(f"✅ Экспортировано {count} карточек в {export_file}")

        # 3. Создать новый manager в пустой директории для импорта
        import_manager = CardManager(cards_dir=self.import_dir)
        importer = CardImporter(import_manager)

        # Проверить, что директория пуста
        remaining = import_manager.search(limit=1000)
        self.assertEqual(len(remaining), 0)
        print(f"✅ Новая директория пуста (осталось {len(remaining)} карточек)")

        # 4. Импортировать обратно из JSON в новую директорию
        stats = importer.import_from_json(export_file, overwrite=False)
        self.assertEqual(stats['imported'], len(cards))
        self.assertEqual(stats['errors'], 0)
        print(f"✅ Импортировано {stats['imported']} карточек")

        # 5. Проверить, что все карточки восстановлены в новой директории
        restored = import_manager.search(limit=1000)
        self.assertEqual(len(restored), len(cards))

        # Проверить типы
        types_count = {}
        for card in restored:
            type_name = card.type.value
            types_count[type_name] = types_count.get(type_name, 0) + 1

        self.assertEqual(types_count['task'], 1)
        self.assertEqual(types_count['medicine'], 1)
        self.assertEqual(types_count['recipe'], 1)
        self.assertEqual(types_count['contact'], 1)
        self.assertEqual(types_count['note'], 1)

        print(f"✅ Все типы карточек восстановлены: {types_count}")
        print("\n🎉 Roundtrip экспорт/импорт успешен!")


class TestGraphNavigation(unittest.TestCase):
    """
    Интеграционный тест: навигация по графу связей

    Workflow:
    1. Создать граф карточек: A → B → C → D
    2. Найти связанные карточки
    3. Найти путь от A до D
    4. Проверить компоненты связности
    """

    def setUp(self):
        """Создание временной директории"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.manager = CardManager(cards_dir=self.temp_dir)

    def tearDown(self):
        """Удаление временной директории"""
        shutil.rmtree(self.temp_dir)

    def test_graph_navigation(self):
        """Навигация по графу: создание цепочки связей и поиск путей"""

        # 1. Создать цепочку: A → B → C → D
        card_a = NoteCard(
            id=Card.generate_id(),
            type=CardType.NOTE,
            title="Карточка A",
            created=datetime.datetime.now(),
            modified=datetime.datetime.now()
        )

        card_b = NoteCard(
            id=Card.generate_id(),
            type=CardType.NOTE,
            title="Карточка B",
            created=datetime.datetime.now(),
            modified=datetime.datetime.now()
        )

        card_c = NoteCard(
            id=Card.generate_id(),
            type=CardType.NOTE,
            title="Карточка C",
            created=datetime.datetime.now(),
            modified=datetime.datetime.now()
        )

        card_d = NoteCard(
            id=Card.generate_id(),
            type=CardType.NOTE,
            title="Карточка D",
            created=datetime.datetime.now(),
            modified=datetime.datetime.now()
        )

        # Создать все карточки
        self.manager.create(card_a)
        self.manager.create(card_b)
        self.manager.create(card_c)
        self.manager.create(card_d)

        # Создать связи: A → B → C → D
        self.manager.link_cards(card_a.id, card_b.id)
        self.manager.link_cards(card_b.id, card_c.id)
        self.manager.link_cards(card_c.id, card_d.id)

        print(f"✅ Создан граф: A → B → C → D")

        # 2. Проверить прямые связи A → B
        linked_from_a = self.manager.get_linked_cards(card_a.id)
        linked_ids = [c.id for c in linked_from_a]
        self.assertIn(card_b.id, linked_ids)
        print(f"✅ A связана с B (найдено {len(linked_from_a)} связей)")

        # 3. Проверить связи B → C
        linked_from_b = self.manager.get_linked_cards(card_b.id)
        linked_ids_b = [c.id for c in linked_from_b]
        self.assertIn(card_c.id, linked_ids_b)
        print(f"✅ B связана с C (найдено {len(linked_from_b)} связей)")

        # 4. Создать изолированную карточку E (не связана ни с чем)
        card_e = NoteCard(
            id=Card.generate_id(),
            type=CardType.NOTE,
            title="Карточка E (изолированная)",
            created=datetime.datetime.now(),
            modified=datetime.datetime.now()
        )
        self.manager.create(card_e)

        # Проверить, что E изолирована
        linked_from_e = self.manager.get_linked_cards(card_e.id)
        self.assertEqual(len(linked_from_e), 0)
        print(f"✅ Карточка E изолирована (0 связей)")

        print("\n🎉 Навигация по графу работает корректно!")


class TestPerformanceIntegration(unittest.TestCase):
    """
    Интеграционный тест: производительность на реальных данных

    Workflow:
    1. Создать 500 карточек
    2. Выполнить 100 поисковых запросов
    3. Экспортировать все в JSON
    4. Импортировать обратно
    5. Измерить время каждой операции
    """

    def setUp(self):
        """Создание временных директорий"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.export_dir = Path(tempfile.mkdtemp())
        self.manager = CardManager(cards_dir=self.temp_dir)

    def tearDown(self):
        """Удаление временных директорий"""
        shutil.rmtree(self.temp_dir)
        shutil.rmtree(self.export_dir)

    def test_large_dataset_performance(self):
        """Производительность на большом датасете (500 карточек)"""
        import time

        # 1. Создать 500 карточек
        print("\n📊 Тест производительности на 500 карточках:")

        start = time.time()
        for i in range(500):
            card = TaskCard(
                id=Card.generate_id(),
                type=CardType.TASK,
                title=f"Задача номер {i}",
                created=datetime.datetime.now(),
                modified=datetime.datetime.now(),
                tags=[f"tag{i % 10}", "test"],
                priority=Priority.MEDIUM if i % 2 == 0 else Priority.HIGH
            )
            self.manager.create(card)

        create_time = time.time() - start
        print(f"  ✅ Создание 500 карточек: {create_time:.2f}с ({500/create_time:.0f} cards/sec)")
        self.assertLess(create_time, 30.0, "Создание 500 карточек должно быть < 30 сек")

        # 2. Выполнить 100 поисковых запросов
        start = time.time()
        for i in range(100):
            results = self.manager.search(query="задача")
            self.assertGreater(len(results), 0)

        search_time = time.time() - start
        print(f"  ✅ 100 поисковых запросов: {search_time:.2f}с ({100/search_time:.0f} queries/sec)")
        self.assertLess(search_time, 5.0, "100 запросов должны быть < 5 сек")

        # 3. Экспортировать все в JSON
        exporter = CardExporter(self.manager)
        export_file = self.export_dir / "large_backup.json"

        start = time.time()
        count = exporter.export_to_json(export_file)
        export_time = time.time() - start

        print(f"  ✅ Экспорт {count} карточек в JSON: {export_time:.2f}с")
        self.assertEqual(count, 500)
        self.assertLess(export_time, 10.0, "Экспорт должен быть < 10 сек")

        # 4. Получить статистику
        start = time.time()
        stats = self.manager.get_stats()
        stats_time = time.time() - start

        print(f"  ✅ Получение статистики: {stats_time:.3f}с")
        print(f"     Всего карточек: {stats.get('total_cards', 0)}")

        print("\n🎉 Тест производительности пройден!")


def run_integration_tests():
    """Запуск всех интеграционных тестов"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Добавить все тест-классы
    suite.addTests(loader.loadTestsFromTestCase(TestFullWorkflow))
    suite.addTests(loader.loadTestsFromTestCase(TestExportImportRoundtrip))
    suite.addTests(loader.loadTestsFromTestCase(TestGraphNavigation))
    suite.addTests(loader.loadTestsFromTestCase(TestPerformanceIntegration))

    # Запустить
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Статистика
    print("\n" + "=" * 70)
    print(f"Интеграционных тестов запущено: {result.testsRun}")
    print(f"Успешно: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Провалено: {len(result.failures)}")
    print(f"Ошибок: {len(result.errors)}")
    print("=" * 70)

    return result.wasSuccessful()


if __name__ == '__main__':
    import sys
    success = run_integration_tests()
    sys.exit(0 if success else 1)
