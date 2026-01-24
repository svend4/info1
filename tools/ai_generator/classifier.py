#!/usr/bin/env python3
"""
Project Type Classifier

Классификация типов проектов на основе естественно-языковых описаний.

Уровень абстракции: α=-4 (исполняемый код)
Связи:
  ⇑ ../ЭТАП-9-ПЛАН.md (α=+1) — архитектура классификатора
  ↔ nlp_parser.py (α=-4) — парсинг описаний
  ↔ ../project_template_generator.py (α=-4) — генерация проектов
"""

from typing import Dict, List, Optional
from dataclasses import dataclass

# Относительный импорт для использования как модуль
try:
    from .nlp_parser import NLPParser, ParsedProject
except ImportError:
    # Абсолютный импорт для прямого запуска
    from nlp_parser import NLPParser, ParsedProject


@dataclass
class ProjectSpec:
    """Спецификация проекта для генерации"""

    name: str
    primary_type: str
    secondary_types: List[str]
    confidence: float
    parameters: Dict[str, any]
    raw_description: str


class ProjectClassifier:
    """
    Классификатор типов проектов

    Использует NLPParser для анализа описания и определения параметров
    для генерации проекта.
    """

    def __init__(self):
        """Инициализация классификатора"""
        self.parser = NLPParser()

    def classify(self, description: str, project_name: Optional[str] = None) -> ProjectSpec:
        """
        Классификация проекта на основе описания

        Args:
            description: Описание проекта на естественном языке
            project_name: Опциональное имя проекта (если None, генерируется автоматически)

        Returns:
            ProjectSpec с параметрами для генерации
        """
        # Парсинг описания
        parsed = self.parser.parse(description)

        # Определение основного типа
        primary_type = parsed.detected_types[0] if parsed.detected_types else 'software'

        # Дополнительные типы (для будущей multi-domain поддержки)
        secondary_types = parsed.detected_types[1:] if len(parsed.detected_types) > 1 else []

        # Confidence score
        confidence = parsed.confidence_scores.get(primary_type, 0.5)

        # Генерация имени проекта (если не указано)
        if project_name is None:
            project_name = self._generate_project_name(parsed, primary_type)

        # Сборка параметров
        parameters = {
            'budget': parsed.budget,
            'timeline': parsed.timeline,
            'team_size': parsed.team_size,
            'scale': parsed.scale,
            'technologies': parsed.extracted_features.get('technologies', []),
            'keywords': parsed.keywords,
        }

        return ProjectSpec(
            name=project_name,
            primary_type=primary_type,
            secondary_types=secondary_types,
            confidence=confidence,
            parameters=parameters,
            raw_description=description
        )

    def _generate_project_name(self, parsed: ParsedProject, project_type: str) -> str:
        """
        Генерация имени проекта на основе ключевых слов

        Args:
            parsed: Результат парсинга
            project_type: Тип проекта

        Returns:
            Сгенерированное имя проекта
        """
        # Берём первые 1-2 значимых ключевых слова
        keywords = parsed.keywords[:2]

        if keywords:
            # Транслитерация и нормализация
            name_parts = [self._transliterate(kw) for kw in keywords]
            name = '-'.join(name_parts)
        else:
            # Fallback: тип проекта
            name = f"{project_type}-project"

        return name

    def _transliterate(self, text: str) -> str:
        """
        Простая транслитерация русского текста в латиницу

        Args:
            text: Текст на русском

        Returns:
            Транслитерированный текст
        """
        translit_map = {
            'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd',
            'е': 'e', 'ё': 'yo', 'ж': 'zh', 'з': 'z', 'и': 'i',
            'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n',
            'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't',
            'у': 'u', 'ф': 'f', 'х': 'h', 'ц': 'ts', 'ч': 'ch',
            'ш': 'sh', 'щ': 'sch', 'ъ': '', 'ы': 'y', 'ь': '',
            'э': 'e', 'ю': 'yu', 'я': 'ya'
        }

        result = []
        for char in text.lower():
            result.append(translit_map.get(char, char))

        return ''.join(result)

    def recommend_structure(self, spec: ProjectSpec) -> Dict[str, List[str]]:
        """
        Рекомендации по структуре проекта на основе спецификации

        Args:
            spec: Спецификация проекта

        Returns:
            Словарь с рекомендованными директориями и файлами
        """
        recommendations = {
            'additional_dirs': [],
            'additional_files': [],
            'suggestions': []
        }

        # Рекомендации на основе технологий
        techs = spec.parameters.get('technologies', [])

        if 'react' in techs or 'vue' in techs or 'angular' in techs:
            recommendations['suggestions'].append('Добавить frontend/ директорию для SPA')

        if 'docker' in techs:
            recommendations['suggestions'].append('Добавить Dockerfile и docker-compose.yml')

        if 'kubernetes' in techs:
            recommendations['additional_dirs'].append('k8s')
            recommendations['suggestions'].append('Добавить Kubernetes манифесты в k8s/')

        # Рекомендации на основе масштаба
        scale = spec.parameters.get('scale', 'medium')

        if scale == 'large':
            recommendations['suggestions'].append('Рассмотреть микросервисную архитектуру')
            recommendations['additional_dirs'].extend(['services', 'api-gateway'])

        # Рекомендации на основе размера команды
        team_size = spec.parameters.get('team_size')

        if team_size and team_size > 10:
            recommendations['suggestions'].append('Добавить CONTRIBUTING.md для больших команд')
            recommendations['suggestions'].append('Настроить CI/CD для автоматизации')

        return recommendations


def main():
    """Тестирование классификатора"""
    classifier = ProjectClassifier()

    test_cases = [
        {
            'description': 'Хочу создать веб-приложение для управления задачами с React frontend',
            'name': None
        },
        {
            'description': 'Научное исследование микропластика в океане, грант РНФ 4.5 млн ₽, 24 месяца, 3 исследователя',
            'name': 'microplastic-research'
        },
        {
            'description': 'Планирую открыть клинику на 50 сотрудников. Нужен бизнес-план и медицинские протоколы',
            'name': None
        },
        {
            'description': 'Стартап в области fintech для учёта личных финансов. Команда 5 человек, budget $100K',
            'name': None
        },
    ]

    print("=" * 70)
    print("PROJECT CLASSIFIER TESTING")
    print("=" * 70)

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'='*70}")
        print(f"Test Case {i}")
        print(f"{'='*70}")
        print(f"Описание: {test_case['description']}\n")

        spec = classifier.classify(
            description=test_case['description'],
            project_name=test_case['name']
        )

        print(f"Project Name: {spec.name}")
        print(f"Primary Type: {spec.primary_type}")
        print(f"Secondary Types: {spec.secondary_types}")
        print(f"Confidence: {spec.confidence:.2f}")
        print(f"\nParameters:")
        for key, value in spec.parameters.items():
            if value:
                print(f"  - {key}: {value}")

        recommendations = classifier.recommend_structure(spec)
        if recommendations['suggestions']:
            print(f"\nRecommendations:")
            for suggestion in recommendations['suggestions']:
                print(f"  • {suggestion}")


if __name__ == '__main__':
    main()
