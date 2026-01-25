#!/usr/bin/env python3
"""
Multi-label классификатор проектов (Фаза 3 ЭТАПА 9)

Поддерживает гибридные проекты с несколькими доменами.
Например: Healthcare + Business, Research + Software
"""

import json
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, asdict

# Импорт существующих классификаторов
try:
    from .ml_classifier import MLClassifier
    from .classifier import ProjectClassifier as RuleBasedClassifier
except ImportError:
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from ai_generator.ml_classifier import MLClassifier
    from ai_generator.classifier import ProjectClassifier as RuleBasedClassifier


@dataclass
class MultiLabelResult:
    """Результат multi-label классификации"""
    primary_type: str
    primary_confidence: float
    secondary_types: List[str]
    secondary_confidences: Dict[str, float]
    all_scores: Dict[str, float]
    is_hybrid: bool
    template_composition: List[str]
    recommendations: List[str]


class MultiLabelClassifier:
    """
    Multi-label классификатор для гибридных проектов

    Определяет проекты, принадлежащие нескольким доменам одновременно.
    Например:
    - Healthcare + Business → Медицинская клиника
    - Research + Software → Научное ПО
    - Education + Arts → Курс по творческим дисциплинам
    """

    # Пороги для определения вторичных типов
    SECONDARY_THRESHOLD = 0.07  # Минимальная уверенность для вторичного типа
    HYBRID_THRESHOLD = 0.10     # Порог для явно гибридного проекта
    MAX_SECONDARY_TYPES = 3     # Максимум вторичных типов

    # Рекомендации по композиции шаблонов
    COMPOSITION_RULES = {
        # Healthcare combinations
        ('healthcare', 'business'): {
            'strategy': 'merge_directories',
            'merge': ['business-plan/', 'medical-protocols/'],
            'recommendations': [
                'Добавить бизнес-план с финансовыми прогнозами',
                'Включить медицинские протоколы и лицензирование',
                'Создать структуру для HR (врачи + административный персонал)'
            ]
        },
        ('healthcare', 'software'): {
            'strategy': 'nested_structure',
            'merge': ['src/', 'medical-data/', 'compliance/'],
            'recommendations': [
                'Добавить медицинские стандарты (HIPAA, GDPR)',
                'Создать структуру для электронных медкарт',
                'Включить тестирование безопасности данных'
            ]
        },

        # Research combinations
        ('research', 'software'): {
            'strategy': 'parallel_structure',
            'merge': ['src/', 'experiments/', 'publications/'],
            'recommendations': [
                'Отдельные директории для кода и исследовательских материалов',
                'Добавить Jupyter notebooks для анализа данных',
                'Включить requirements.txt для воспроизводимости'
            ]
        },
        ('research', 'agriculture'): {
            'strategy': 'merge_directories',
            'merge': ['field-data/', 'lab-analysis/', 'publications/'],
            'recommendations': [
                'Создать структуру для полевых данных',
                'Добавить протоколы лабораторных экспериментов',
                'Включить статистический анализ результатов'
            ]
        },

        # Business combinations
        ('business', 'software'): {
            'strategy': 'nested_structure',
            'merge': ['src/', 'business-plan/', 'financials/'],
            'recommendations': [
                'Tech startup структура: код + бизнес-документы',
                'Добавить pitch deck и финансовые модели',
                'Включить roadmap продукта'
            ]
        },
        ('business', 'hospitality'): {
            'strategy': 'merge_directories',
            'merge': ['operations/', 'marketing/', 'financials/'],
            'recommendations': [
                'Бизнес-план для ресторана/отеля',
                'Добавить меню, прайс-листы, стандарты обслуживания',
                'Включить маркетинговую стратегию'
            ]
        },
        ('business', 'retail'): {
            'strategy': 'merge_directories',
            'merge': ['inventory/', 'sales/', 'financials/'],
            'recommendations': [
                'Структура для управления товарами',
                'Добавить систему учёта продаж',
                'Включить анализ рентабельности'
            ]
        },

        # Education combinations
        ('education', 'software'): {
            'strategy': 'nested_structure',
            'merge': ['src/', 'curriculum/', 'materials/'],
            'recommendations': [
                'Платформа для онлайн-обучения',
                'Добавить учебные материалы и задания',
                'Включить систему оценивания'
            ]
        },
        ('education', 'arts'): {
            'strategy': 'merge_directories',
            'merge': ['curriculum/', 'projects/', 'portfolio/'],
            'recommendations': [
                'Курс по творческим дисциплинам',
                'Добавить портфолио студентов',
                'Включить критерии оценки творческих работ'
            ]
        },
        ('education', 'sports'): {
            'strategy': 'merge_directories',
            'merge': ['training-programs/', 'schedule/', 'assessment/'],
            'recommendations': [
                'Спортивная академия или тренировочная программа',
                'Добавить расписание тренировок',
                'Включить систему отслеживания прогресса'
            ]
        },

        # Finance combinations
        ('finance', 'software'): {
            'strategy': 'nested_structure',
            'merge': ['src/', 'financial-models/', 'compliance/'],
            'recommendations': [
                'Fintech приложение или платформа',
                'Добавить финансовые модели и калькуляторы',
                'Включить соответствие регуляторным требованиям'
            ]
        },

        # Legal combinations
        ('legal', 'business'): {
            'strategy': 'merge_directories',
            'merge': ['contracts/', 'compliance/', 'business-docs/'],
            'recommendations': [
                'Юридическое сопровождение бизнеса',
                'Добавить шаблоны договоров',
                'Включить корпоративные документы'
            ]
        },

        # Software combinations
        ('software', 'retail'): {
            'strategy': 'nested_structure',
            'merge': ['src/', 'inventory/', 'api/'],
            'recommendations': [
                'E-commerce платформа',
                'Добавить управление каталогом товаров',
                'Включить интеграцию с платёжными системами'
            ]
        },
        ('software', 'government'): {
            'strategy': 'nested_structure',
            'merge': ['src/', 'security/', 'compliance/', 'docs/'],
            'recommendations': [
                'Государственная информационная система',
                'Добавить усиленные меры безопасности',
                'Включить соответствие ГОСТ и ФЗ-152'
            ]
        },

        # Nonprofit combinations
        ('nonprofit', 'software'): {
            'strategy': 'nested_structure',
            'merge': ['src/', 'campaigns/', 'donors/'],
            'recommendations': [
                'Платформа для благотворительной организации',
                'Добавить систему управления донорами',
                'Включить отчётность и прозрачность'
            ]
        },

        # Sports combinations
        ('sports', 'business'): {
            'strategy': 'merge_directories',
            'merge': ['training/', 'business-plan/', 'marketing/'],
            'recommendations': [
                'Спортивный клуб или академия',
                'Добавить бизнес-план и финансовые модели',
                'Включить маркетинг и набор участников'
            ]
        },

        # Manufacturing combinations
        ('manufacturing', 'software'): {
            'strategy': 'nested_structure',
            'merge': ['src/', 'production/', 'quality-control/'],
            'recommendations': [
                'Система управления производством',
                'Добавить контроль качества',
                'Включить учёт материалов и запасов'
            ]
        },
    }

    def __init__(self, ml_model_path: Optional[str] = None):
        """
        Инициализация multi-label классификатора

        Args:
            ml_model_path: Путь к обученной ML модели
        """
        # Загрузка ML классификатора
        self.ml_classifier = MLClassifier()

        if ml_model_path is None:
            ml_model_path = Path(__file__).parent / 'models' / 'project_classifier.pkl'

        if Path(ml_model_path).exists():
            self.ml_classifier.load_model(str(ml_model_path))
        else:
            print(f"⚠️  ML модель не найдена: {ml_model_path}")
            print("   Multi-label классификация будет ограничена")

    def classify(self, description: str) -> MultiLabelResult:
        """
        Multi-label классификация проекта

        Args:
            description: Описание проекта на естественном языке

        Returns:
            MultiLabelResult с primary/secondary типами и рекомендациями
        """
        # Получение scores от ML классификатора
        primary_type, primary_conf, all_scores = self.ml_classifier.predict(description)

        # Определение вторичных типов (confidence > threshold)
        secondary_types = []
        secondary_confidences = {}

        for proj_type, score in list(all_scores.items())[1:]:  # Пропускаем primary
            if score >= self.SECONDARY_THRESHOLD and len(secondary_types) < self.MAX_SECONDARY_TYPES:
                secondary_types.append(proj_type)
                secondary_confidences[proj_type] = score

        # Определение, является ли проект гибридным
        is_hybrid = (
            len(secondary_types) > 0 and
            secondary_confidences.get(secondary_types[0], 0) >= self.HYBRID_THRESHOLD
        )

        # Определение стратегии композиции шаблонов
        template_composition = self._get_template_composition(primary_type, secondary_types)

        # Генерация рекомендаций
        recommendations = self._generate_recommendations(
            primary_type, secondary_types, all_scores, description
        )

        return MultiLabelResult(
            primary_type=primary_type,
            primary_confidence=primary_conf,
            secondary_types=secondary_types,
            secondary_confidences=secondary_confidences,
            all_scores=all_scores,
            is_hybrid=is_hybrid,
            template_composition=template_composition,
            recommendations=recommendations
        )

    def _get_template_composition(self, primary: str, secondary: List[str]) -> List[str]:
        """Определение шаблонов для композиции"""
        composition = [primary]  # Всегда включаем primary

        for sec_type in secondary:
            key = (primary, sec_type)
            if key in self.COMPOSITION_RULES:
                composition.append(sec_type)

        return composition

    def _generate_recommendations(
        self,
        primary: str,
        secondary: List[str],
        all_scores: Dict[str, float],
        description: str
    ) -> List[str]:
        """Генерация рекомендаций по структуре проекта"""
        recommendations = []

        # Рекомендации для гибридных проектов
        for sec_type in secondary:
            key = (primary, sec_type)
            if key in self.COMPOSITION_RULES:
                rule = self.COMPOSITION_RULES[key]
                recommendations.extend(rule['recommendations'])

        # Общие рекомендации
        if not recommendations:
            recommendations.append(f"Использовать стандартную структуру для {primary}")

        # Рекомендации на основе confidence scores
        top_3_types = list(all_scores.keys())[:3]
        if len(top_3_types) >= 3:
            third_type = top_3_types[2]
            third_score = all_scores[third_type]
            if third_score >= 0.10:
                recommendations.append(
                    f"Рассмотреть добавление элементов из {third_type} "
                    f"(confidence: {third_score:.1%})"
                )

        return recommendations

    def get_composition_strategy(self, primary: str, secondary: str) -> Optional[Dict]:
        """
        Получить стратегию композиции для пары типов

        Args:
            primary: Основной тип
            secondary: Вторичный тип

        Returns:
            Dict с strategy, merge, recommendations или None
        """
        key = (primary, secondary)
        return self.COMPOSITION_RULES.get(key)

    def to_dict(self, result: MultiLabelResult) -> Dict:
        """Преобразование результата в dict"""
        return asdict(result)

    def to_json(self, result: MultiLabelResult) -> str:
        """Преобразование результата в JSON"""
        return json.dumps(self.to_dict(result), ensure_ascii=False, indent=2)


def main():
    """Тестирование multi-label классификатора"""
    import argparse

    parser = argparse.ArgumentParser(description='Multi-label классификатор проектов')
    parser.add_argument('description', nargs='?',
                       help='Описание проекта')
    parser.add_argument('--model', default=None,
                       help='Путь к ML модели')
    parser.add_argument('--test', action='store_true',
                       help='Запустить тестовые примеры')

    args = parser.parse_args()

    classifier = MultiLabelClassifier(ml_model_path=args.model)

    if args.test:
        # Тестовые примеры гибридных проектов
        test_cases = [
            "Открываем медицинский центр кардиологии, нужен бизнес-план",
            "Научное исследование с разработкой ПО для анализа данных",
            "Финтех-стартап для управления личными финансами",
            "Онлайн-курс по веб-дизайну и HTML/CSS",
            "Ресторан итальянской кухни в центре города",
            "E-commerce платформа для продажи товаров ручной работы",
            "Спортивная академия футбола для детей, коммерческий проект",
        ]

        print("="*70)
        print("MULTI-LABEL CLASSIFIER - TEST CASES")
        print("="*70)

        for i, desc in enumerate(test_cases, 1):
            print(f"\n{'='*70}")
            print(f"Тест {i}: {desc}")
            print('='*70)

            result = classifier.classify(desc)

            print(f"\n✓ Primary type: {result.primary_type} ({result.primary_confidence:.1%})")

            if result.secondary_types:
                print(f"✓ Secondary types:")
                for sec_type in result.secondary_types:
                    conf = result.secondary_confidences[sec_type]
                    print(f"  - {sec_type} ({conf:.1%})")

            print(f"\n✓ Hybrid project: {'Yes' if result.is_hybrid else 'No'}")
            print(f"✓ Template composition: {' + '.join(result.template_composition)}")

            print(f"\n📋 Recommendations:")
            for j, rec in enumerate(result.recommendations, 1):
                print(f"  {j}. {rec}")

            # Composition strategy
            if result.secondary_types:
                strategy = classifier.get_composition_strategy(
                    result.primary_type,
                    result.secondary_types[0]
                )
                if strategy:
                    print(f"\n🔧 Composition strategy: {strategy['strategy']}")
                    print(f"   Merge directories: {', '.join(strategy['merge'])}")

    elif args.description:
        # Классификация одного проекта
        result = classifier.classify(args.description)

        print("="*70)
        print("MULTI-LABEL CLASSIFICATION RESULT")
        print("="*70)
        print(classifier.to_json(result))

    else:
        parser.print_help()


if __name__ == '__main__':
    main()
