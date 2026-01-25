#!/usr/bin/env python3
"""
Template Composer (Фаза 3 ЭТАПА 9)

Система композиции шаблонов для гибридных проектов.
Объединяет структуры из нескольких доменов в единый проект.
"""

import json
from pathlib import Path
from typing import List, Dict, Optional, Set
from dataclasses import dataclass

try:
    from .multi_label_classifier import MultiLabelResult, MultiLabelClassifier
except ImportError:
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from ai_generator.multi_label_classifier import MultiLabelResult, MultiLabelClassifier


@dataclass
class ComposedStructure:
    """Структура скомпонованного проекта"""
    directories: List[str]
    files: List[str]
    strategy: str
    primary_type: str
    merged_types: List[str]
    description: str


class TemplateComposer:
    """
    Система композиции шаблонов для гибридных проектов

    Поддерживает 3 стратегии композиции:
    1. merge_directories - Объединение директорий из обоих типов
    2. nested_structure - Вложенная структура (src/ + domain-specific/)
    3. parallel_structure - Параллельные директории на верхнем уровне
    """

    # Базовые структуры для каждого типа проекта
    BASE_STRUCTURES = {
        'software': {
            'dirs': [
                'src/',
                'tests/',
                'docs/',
                'config/',
            ],
            'files': [
                'README.md',
                'requirements.txt',
                '.gitignore',
                'setup.py',
            ]
        },
        'research': {
            'dirs': [
                'data/',
                'experiments/',
                'publications/',
                'notebooks/',
            ],
            'files': [
                'README.md',
                'METHODOLOGY.md',
                'requirements.txt',
                'LICENSE',
            ]
        },
        'business': {
            'dirs': [
                'business-plan/',
                'financials/',
                'marketing/',
                'operations/',
            ],
            'files': [
                'README.md',
                'EXECUTIVE-SUMMARY.md',
                'PITCH-DECK.md',
            ]
        },
        'education': {
            'dirs': [
                'curriculum/',
                'materials/',
                'assessments/',
                'resources/',
            ],
            'files': [
                'README.md',
                'SYLLABUS.md',
                'SCHEDULE.md',
            ]
        },
        'healthcare': {
            'dirs': [
                'medical-protocols/',
                'patient-data/',
                'compliance/',
                'staff/',
            ],
            'files': [
                'README.md',
                'PROTOCOLS.md',
                'COMPLIANCE.md',
            ]
        },
        'legal': {
            'dirs': [
                'contracts/',
                'documents/',
                'compliance/',
                'research/',
            ],
            'files': [
                'README.md',
                'PROCEDURES.md',
            ]
        },
        'finance': {
            'dirs': [
                'models/',
                'reports/',
                'compliance/',
                'data/',
            ],
            'files': [
                'README.md',
                'MODELS.md',
                'RISK-ASSESSMENT.md',
            ]
        },
        'arts': {
            'dirs': [
                'projects/',
                'portfolio/',
                'resources/',
                'exhibitions/',
            ],
            'files': [
                'README.md',
                'ARTIST-STATEMENT.md',
                'PORTFOLIO.md',
            ]
        },
        'government': {
            'dirs': [
                'programs/',
                'compliance/',
                'reporting/',
                'docs/',
            ],
            'files': [
                'README.md',
                'COMPLIANCE.md',
                'PROCEDURES.md',
            ]
        },
        'nonprofit': {
            'dirs': [
                'campaigns/',
                'donors/',
                'reports/',
                'events/',
            ],
            'files': [
                'README.md',
                'MISSION.md',
                'IMPACT.md',
            ]
        },
        'manufacturing': {
            'dirs': [
                'production/',
                'quality-control/',
                'inventory/',
                'supply-chain/',
            ],
            'files': [
                'README.md',
                'PROCESSES.md',
                'QUALITY-STANDARDS.md',
            ]
        },
        'agriculture': {
            'dirs': [
                'operations/',
                'crops-livestock/',
                'equipment/',
                'financials/',
            ],
            'files': [
                'README.md',
                'OPERATIONS.md',
                'SUSTAINABILITY.md',
            ]
        },
        'sports': {
            'dirs': [
                'training-programs/',
                'schedule/',
                'athletes/',
                'equipment/',
            ],
            'files': [
                'README.md',
                'TRAINING-PLAN.md',
                'ASSESSMENT.md',
            ]
        },
        'hospitality': {
            'dirs': [
                'operations/',
                'menu-services/',
                'staff/',
                'marketing/',
            ],
            'files': [
                'README.md',
                'OPERATIONS.md',
                'STANDARDS.md',
            ]
        },
        'retail': {
            'dirs': [
                'inventory/',
                'sales/',
                'marketing/',
                'operations/',
            ],
            'files': [
                'README.md',
                'PRODUCTS.md',
                'OPERATIONS.md',
            ]
        },
        'hobby': {
            'dirs': [
                'projects/',
                'resources/',
                'notes/',
                'media/',
            ],
            'files': [
                'README.md',
                'GOALS.md',
            ]
        },
    }

    def __init__(self):
        """Инициализация композитора шаблонов"""
        pass

    def compose(self, result: MultiLabelResult) -> ComposedStructure:
        """
        Создание скомпонованной структуры проекта

        Args:
            result: Результат multi-label классификации

        Returns:
            ComposedStructure с объединёнными директориями и файлами
        """
        primary = result.primary_type
        secondary = result.secondary_types

        # Получаем базовую структуру primary типа
        base_dirs = set(self.BASE_STRUCTURES.get(primary, {}).get('dirs', []))
        base_files = set(self.BASE_STRUCTURES.get(primary, {}).get('files', []))

        # Определяем стратегию композиции
        if not secondary:
            # Простой проект - только primary тип
            strategy = 'single_type'
            merged_types = [primary]
        elif len(secondary) == 1:
            # Гибридный проект с одним вторичным типом
            strategy = self._get_composition_strategy(primary, secondary[0])
            merged_types = [primary, secondary[0]]

            # Применяем композицию
            base_dirs, base_files = self._apply_composition(
                base_dirs, base_files, primary, secondary[0], strategy
            )
        else:
            # Сложный гибридный проект (2+ вторичных типов)
            strategy = 'multi_domain'
            merged_types = [primary] + secondary

            # Применяем композицию для каждого вторичного типа
            for sec_type in secondary[:2]:  # Ограничиваем до 2 вторичных
                sec_strategy = self._get_composition_strategy(primary, sec_type)
                base_dirs, base_files = self._apply_composition(
                    base_dirs, base_files, primary, sec_type, sec_strategy
                )

        return ComposedStructure(
            directories=sorted(base_dirs),
            files=sorted(base_files),
            strategy=strategy,
            primary_type=primary,
            merged_types=merged_types,
            description=self._generate_description(primary, secondary, strategy)
        )

    def _get_composition_strategy(self, primary: str, secondary: str) -> str:
        """Определить стратегию композиции для пары типов"""
        # Используем правила из MultiLabelClassifier
        classifier = MultiLabelClassifier()
        rule = classifier.get_composition_strategy(primary, secondary)

        if rule:
            return rule['strategy']
        else:
            # Стратегия по умолчанию
            if primary == 'software' or secondary == 'software':
                return 'nested_structure'
            else:
                return 'merge_directories'

    def _apply_composition(
        self,
        base_dirs: Set[str],
        base_files: Set[str],
        primary: str,
        secondary: str,
        strategy: str
    ) -> tuple:
        """Применить стратегию композиции"""
        sec_structure = self.BASE_STRUCTURES.get(secondary, {})
        sec_dirs = set(sec_structure.get('dirs', []))
        sec_files = set(sec_structure.get('files', []))

        if strategy == 'merge_directories':
            # Просто объединяем все директории и файлы
            base_dirs.update(sec_dirs)
            # Файлы объединяем аккуратно (избегаем дубликатов README)
            for file in sec_files:
                if file != 'README.md':  # README остаётся один
                    base_files.add(file)

        elif strategy == 'nested_structure':
            # Создаём подструктуру для вторичного типа
            # Например: src/ (из software) + domain-specific/ (из другого типа)
            if primary == 'software':
                # Software - primary, добавляем domain директории
                for dir in sec_dirs:
                    if dir not in base_dirs:
                        base_dirs.add(dir)
            else:
                # Другой тип - primary, добавляем src/ для software
                base_dirs.update(sec_dirs)

            base_files.update(sec_files - {'README.md'})

        elif strategy == 'parallel_structure':
            # Параллельные структуры на верхнем уровне
            # Добавляем все директории из обоих типов
            base_dirs.update(sec_dirs)
            base_files.update(sec_files - {'README.md'})

        return base_dirs, base_files

    def _generate_description(self, primary: str, secondary: List[str], strategy: str) -> str:
        """Генерация описания композиции"""
        if strategy == 'single_type':
            return f"Стандартная структура для {primary} проекта"
        elif not secondary:
            return f"Стандартная структура для {primary} проекта"
        elif len(secondary) == 1:
            return (
                f"Гибридная структура: {primary} (основной) + {secondary[0]} (вторичный). "
                f"Стратегия: {strategy}"
            )
        else:
            sec_list = ", ".join(secondary[:2])
            return (
                f"Многодоменная структура: {primary} (основной) + [{sec_list}] (вторичные). "
                f"Стратегия: {strategy}"
            )

    def to_dict(self, structure: ComposedStructure) -> Dict:
        """Преобразование структуры в dict"""
        return {
            'directories': structure.directories,
            'files': structure.files,
            'strategy': structure.strategy,
            'primary_type': structure.primary_type,
            'merged_types': structure.merged_types,
            'description': structure.description
        }

    def to_json(self, structure: ComposedStructure) -> str:
        """Преобразование структуры в JSON"""
        return json.dumps(self.to_dict(structure), ensure_ascii=False, indent=2)

    def generate_directory_tree(self, structure: ComposedStructure) -> str:
        """Генерация текстового представления дерева директорий"""
        lines = [f"{structure.primary_type}-project/"]

        for directory in structure.directories:
            lines.append(f"├── {directory}")

        for i, file in enumerate(structure.files):
            prefix = "└──" if i == len(structure.files) - 1 else "├──"
            lines.append(f"{prefix} {file}")

        return "\n".join(lines)


def main():
    """Тестирование композитора шаблонов"""
    import argparse

    parser = argparse.ArgumentParser(description='Template Composer')
    parser.add_argument('description', nargs='?',
                       help='Описание проекта')
    parser.add_argument('--test', action='store_true',
                       help='Запустить тестовые примеры')

    args = parser.parse_args()

    classifier = MultiLabelClassifier()
    composer = TemplateComposer()

    if args.test:
        # Тестовые примеры
        test_cases = [
            "Медицинская клиника кардиологии, нужен бизнес-план",
            "Научное исследование с разработкой ПО для анализа",
            "Финтех-стартап для управления личными финансами",
            "E-commerce платформа для продажи товаров",
        ]

        print("="*70)
        print("TEMPLATE COMPOSER - TEST CASES")
        print("="*70)

        for i, desc in enumerate(test_cases, 1):
            print(f"\n{'='*70}")
            print(f"Тест {i}: {desc}")
            print('='*70)

            # Классификация
            result = classifier.classify(desc)

            print(f"\n✓ Primary: {result.primary_type}")
            if result.secondary_types:
                print(f"✓ Secondary: {', '.join(result.secondary_types)}")

            # Композиция
            structure = composer.compose(result)

            print(f"\n📁 Composed Structure:")
            print(f"   Strategy: {structure.strategy}")
            print(f"   Merged types: {' + '.join(structure.merged_types)}")
            print(f"\n{structure.description}")

            print(f"\n🌳 Directory Tree:")
            tree = composer.generate_directory_tree(structure)
            for line in tree.split('\n'):
                print(f"   {line}")

    elif args.description:
        # Композиция для одного проекта
        result = classifier.classify(args.description)
        structure = composer.compose(result)

        print("="*70)
        print("TEMPLATE COMPOSITION RESULT")
        print("="*70)
        print(composer.to_json(structure))
        print("\n" + "="*70)
        print("DIRECTORY TREE")
        print("="*70)
        print(composer.generate_directory_tree(structure))

    else:
        parser.print_help()


if __name__ == '__main__':
    main()
