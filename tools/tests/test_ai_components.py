#!/usr/bin/env python3
"""
Tests for AI components (NLP Parser and Classifier)

Тесты для ЭТАПА 9: AI-assisted Project Generation
"""

import unittest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai_generator'))

from nlp_parser import NLPParser, ParsedProject
from classifier import ProjectClassifier, ProjectSpec


class TestNLPParser(unittest.TestCase):
    """Тесты для NLP Parser"""

    def setUp(self):
        """Инициализация парсера"""
        self.parser = NLPParser()

    def test_basic_parsing(self):
        """Тест базового парсинга"""
        description = "Хочу создать веб-приложение"
        result = self.parser.parse(description)

        self.assertIsInstance(result, ParsedProject)
        self.assertEqual(result.raw_description, description)
        self.assertIsInstance(result.keywords, list)
        self.assertIsInstance(result.detected_types, list)

    def test_software_detection(self):
        """Тест определения software проектов"""
        descriptions = [
            "Создать веб-приложение с React",
            "Мобильное приложение на Python",
            "API для управления данными"
        ]

        for desc in descriptions:
            result = self.parser.parse(desc)
            self.assertIn('software', result.detected_types,
                         f"Failed to detect software in: {desc}")

    def test_research_detection(self):
        """Тест определения research проектов"""
        descriptions = [
            "Научное исследование микропластика",
            "Эксперимент по изучению данных",
            "Диссертация на тему анализа"
        ]

        for desc in descriptions:
            result = self.parser.parse(desc)
            self.assertIn('research', result.detected_types,
                         f"Failed to detect research in: {desc}")

    def test_budget_extraction(self):
        """Тест извлечения бюджета"""
        test_cases = [
            ("грант 4.5 млн ₽", "4.5 млн ₽"),
            ("бюджет 100 тыс рублей", "100 тыс"),
            ("проект без бюджета", None)
        ]

        for description, expected_budget in test_cases:
            result = self.parser.parse(description)
            if expected_budget:
                self.assertIsNotNone(result.budget,
                                   f"Failed to extract budget from: {description}")
            else:
                self.assertIsNone(result.budget)

    def test_timeline_extraction(self):
        """Тест извлечения временных рамок"""
        test_cases = [
            ("проект на 24 месяца", "24 месяц"),
            ("исследование длительностью 2 года", "2 год"),
            ("без указания срока", None)
        ]

        for description, expected_timeline in test_cases:
            result = self.parser.parse(description)
            if expected_timeline:
                self.assertIsNotNone(result.timeline,
                                   f"Failed to extract timeline from: {description}")

    def test_team_size_extraction(self):
        """Тест извлечения размера команды"""
        test_cases = [
            ("команда из 5 человек", 5),
            ("50 сотрудников", 50),
            ("один разработчик", None)  # Не определится автоматически
        ]

        for description, expected_size in test_cases:
            result = self.parser.parse(description)
            if expected_size:
                self.assertEqual(result.team_size, expected_size,
                               f"Failed to extract team size from: {description}")

    def test_technology_extraction(self):
        """Тест извлечения технологий"""
        description = "Веб-приложение с React, Node.js и PostgreSQL"
        result = self.parser.parse(description)

        expected_techs = ['react', 'node', 'postgresql']
        for tech in expected_techs:
            self.assertIn(tech, result.extracted_features['technologies'],
                         f"Failed to detect technology: {tech}")


class TestProjectClassifier(unittest.TestCase):
    """Тесты для Project Classifier"""

    def setUp(self):
        """Инициализация классификатора"""
        self.classifier = ProjectClassifier()

    def test_basic_classification(self):
        """Тест базовой классификации"""
        description = "Хочу создать веб-приложение"
        spec = self.classifier.classify(description)

        self.assertIsInstance(spec, ProjectSpec)
        self.assertIn(spec.primary_type, [
            'software', 'research', 'business', 'education', 'legal',
            'healthcare', 'arts', 'finance', 'government', 'nonprofit',
            'manufacturing', 'agriculture', 'sports', 'hospitality',
            'retail', 'hobby'
        ])

    def test_project_name_generation(self):
        """Тест генерации имени проекта"""
        test_cases = [
            ("Веб-приложение для задач", None),  # Автогенерация
            ("Научное исследование", "my-research"),  # Заданное имя
        ]

        for description, provided_name in test_cases:
            spec = self.classifier.classify(description, provided_name)

            if provided_name:
                self.assertEqual(spec.name, provided_name)
            else:
                self.assertIsNotNone(spec.name)
                self.assertGreater(len(spec.name), 0)

    def test_confidence_scores(self):
        """Тест confidence scores"""
        description = "Хочу создать мобильное приложение"
        spec = self.classifier.classify(description)

        self.assertGreater(spec.confidence, 0.0)
        self.assertLessEqual(spec.confidence, 1.0)

    def test_multi_domain_detection(self):
        """Тест определения multi-domain проектов"""
        description = "Открываю клинику с бизнес-планом и медицинскими протоколами"
        spec = self.classifier.classify(description)

        # Должен определить healthcare или business как primary
        self.assertIn(spec.primary_type, ['healthcare', 'business'])

        # Один из типов должен быть в secondary
        all_types = [spec.primary_type] + spec.secondary_types
        self.assertTrue(
            'healthcare' in all_types or 'business' in all_types,
            "Failed to detect multi-domain project"
        )

    def test_recommendations(self):
        """Тест генерации рекомендаций"""
        description = "Большой проект с React, Docker и командой 50 человек"
        spec = self.classifier.classify(description)

        recommendations = self.classifier.recommend_structure(spec)

        self.assertIsInstance(recommendations, dict)
        self.assertIn('suggestions', recommendations)
        self.assertIsInstance(recommendations['suggestions'], list)

        # Должны быть рекомендации для Docker
        suggestions_text = ' '.join(recommendations['suggestions'])
        self.assertTrue(
            'docker' in suggestions_text.lower(),
            "Failed to generate Docker recommendations"
        )

    def test_transliteration(self):
        """Тест транслитерации"""
        test_cases = [
            ("веб", "veb"),
            ("приложение", "prilozhenie"),
            ("научное", "nauchnoe"),
        ]

        for russian, expected_latin in test_cases:
            result = self.classifier._transliterate(russian)
            self.assertEqual(result, expected_latin,
                           f"Transliteration failed for: {russian}")


class TestIntegration(unittest.TestCase):
    """Интеграционные тесты"""

    def setUp(self):
        """Инициализация"""
        self.classifier = ProjectClassifier()

    def test_full_pipeline(self):
        """Тест полного pipeline: описание → спецификация"""
        descriptions = [
            "Веб-приложение для управления задачами",
            "Научное исследование микропластика, 24 месяца, грант 4.5 млн",
            "Открываю клинику на 50 сотрудников",
            "Мобильное приложение для учёта финансов",
            "Интернет-магазин одежды с доставкой"
        ]

        for desc in descriptions:
            spec = self.classifier.classify(desc)

            # Проверки спецификации
            self.assertIsNotNone(spec.name, f"No name generated for: {desc}")
            self.assertIsNotNone(spec.primary_type, f"No type detected for: {desc}")
            self.assertGreater(spec.confidence, 0.0, f"Zero confidence for: {desc}")
            self.assertIsInstance(spec.parameters, dict)

    def test_accuracy_on_test_set(self):
        """Тест точности на тестовом наборе"""
        test_cases = [
            ("Создать веб-приложение с React", "software"),
            ("Научное исследование по биологии", "research"),
            ("Бизнес-план для стартапа", "business"),
            ("Онлайн-курс по программированию", "education"),
            ("Юридическая консультация", "legal"),
            ("Система управления клиникой", "healthcare"),
            ("Выставка современного искусства", "arts"),
            ("Инвестиционный портфель", "finance"),
            ("Госуслуги онлайн", "government"),
            ("Благотворительный фонд", "nonprofit"),
            ("Завод по производству упаковки", "manufacturing"),
            ("Управление фермой", "agriculture"),
            ("Спортивная академия", "sports"),
            ("Гостиница в центре города", "hospitality"),
            ("Магазин одежды", "retail"),
            ("Блог о путешествиях", "hobby"),
        ]

        correct = 0
        total = len(test_cases)

        for description, expected_type in test_cases:
            spec = self.classifier.classify(description)

            if spec.primary_type == expected_type:
                correct += 1
            else:
                print(f"\nMisclassification:")
                print(f"  Description: {description}")
                print(f"  Expected: {expected_type}")
                print(f"  Got: {spec.primary_type}")
                print(f"  Confidence: {spec.confidence:.2%}")

        accuracy = correct / total
        print(f"\nAccuracy: {correct}/{total} = {accuracy:.1%}")

        # Ожидаем минимум 70% точности для rule-based подхода
        self.assertGreaterEqual(accuracy, 0.70,
                              f"Accuracy too low: {accuracy:.1%}")


def run_tests():
    """Запуск всех тестов"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Добавление тестов
    suite.addTests(loader.loadTestsFromTestCase(TestNLPParser))
    suite.addTests(loader.loadTestsFromTestCase(TestProjectClassifier))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))

    # Запуск
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Итоговая статистика
    print("\n" + "="*70)
    print("AI COMPONENTS TEST SUMMARY")
    print("="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("="*70)

    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
