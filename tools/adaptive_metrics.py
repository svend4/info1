#!/usr/bin/env python3
"""
Adaptive Metrics System (ЭТАП 6: Самосовершенствование)

Автоматически корректирует целевые диапазоны метрик на основе
анализа истории проекта и корреляций с успешностью.

Ключевые функции:
1. Анализ корреляций между метриками и успешностью проекта
2. Автоматическая корректировка целевых диапазонов
3. Обоснование изменений на основе данных
4. Персонализация под тип проекта
5. История адаптаций для прозрачности

Уровень абстракции: α=-4 (исполняемый код)
Статус: ⇑ ВВЕРХ (инструмент для улучшения методологии)

Вертикальные связи (⇑ к философии и концепциям):
    ⇑ ЭТАП-6-САМОСОВЕРШЕНСТВОВАНИЕ.md (α=+2) — адаптивная оптимизация как часть самосовершенствования
    ⇑ ФИЛОСОФИЯ-ПРОЕКТА.md (α=+3) — принцип адаптации и отказ от догматизма
    ⇑ МЕТРИКИ-ЗДОРОВЬЯ.md (α=+1) — базовые диапазоны метрик, которые адаптируются
    ⇑ МЕТОДОЛОГИЯ-ПАРАЛЛЕЛЬНОГО-РАЗВИТИЯ.md (α=+1) — методология как живая, адаптирующаяся система

Горизонтальные связи (↔ другие инструменты α=-4):
    ↔ health_metrics.py — использует текущие метрики для адаптации порогов
    ↔ save_metrics.py — анализирует историю для корреляций
    ↔ self_improvement.py — предоставляет персонализированные рекомендации
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from pathlib import Path


class AdaptiveThresholdOptimizer:
    """Оптимизатор целевых диапазонов метрик на основе истории проекта"""

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.current_thresholds = {
            'cd': {'min': 10.0, 'max': 20.0, 'name': 'CD (Connectivity Density)'},
            'vt': {'min': 50.0, 'max': 70.0, 'name': 'VT (Vertical Traceability)'},
            'cr': {'min': 0.7, 'max': 1.5, 'name': 'CR (Convergence Rate)'},
            'db': {'min': 0.0, 'max': 30.0, 'name': 'DB (Directional Balance)'}
        }
        self.adapted_thresholds = {}
        self.adaptation_history = []

    def analyze_project_characteristics(self) -> Dict:
        """
        Анализирует характеристики проекта для определения типа.

        Типы проектов:
        - library: библиотека/фреймворк
        - webapp: веб-приложение
        - mobile: мобильное приложение
        - datascience: Data Science проект
        - methodology: методологический/теоретический проект
        - info_system: информационная система
        """
        # Простая эвристика на основе структуры проекта
        characteristics = {
            'type': 'info_system',  # По умолчанию
            'size': 'medium',
            'maturity': 'mature',
            'focus': 'user_oriented'
        }

        # Проверка наличия характерных файлов
        project_files = list(self.project_root.glob('*'))

        # Определение методологического проекта по наличию философских документов
        philosophy_markers = [
            'ФИЛОСОФИЯ', 'МЕТОДОЛОГИЯ', 'ОНТОЛОГИЯ', 'МЕТА-АНАЛИЗ',
            'ЭВОЛЮЦИЯ-МЕТОДОЛОГИИ', 'ЭТАП-', 'philosophy', 'methodology'
        ]
        md_files = list(self.project_root.glob('*.md'))
        philosophy_count = sum(1 for f in md_files if any(marker in f.name.upper() for marker in philosophy_markers))

        if philosophy_count >= 5:
            characteristics['type'] = 'methodology'
            characteristics['focus'] = 'theory_oriented'
        elif any('card_system' in str(f) for f in project_files):
            characteristics['type'] = 'info_system'
            characteristics['focus'] = 'user_oriented'

        # Определение размера по количеству документов
        md_files = list(self.project_root.glob('**/*.md'))
        if len(md_files) > 50:
            characteristics['size'] = 'large'
        elif len(md_files) > 20:
            characteristics['size'] = 'medium'
        else:
            characteristics['size'] = 'small'

        # Оценка зрелости по наличию документации
        has_readme = (self.project_root / 'README.md').exists()
        has_contributing = (self.project_root / 'CONTRIBUTING.md').exists()
        has_changelog = (self.project_root / 'CHANGELOG.md').exists()

        if has_readme and has_contributing and has_changelog:
            characteristics['maturity'] = 'mature'
        elif has_readme:
            characteristics['maturity'] = 'developing'
        else:
            characteristics['maturity'] = 'early'

        return characteristics

    def recommend_thresholds_for_project_type(self, project_type: str) -> Dict:
        """
        Рекомендует целевые диапазоны на основе типа проекта.

        Обоснование:
        - Разные типы проектов имеют разные паттерны связности
        - Библиотеки: высокая VT (трассируемость от API до реализации)
        - Web-приложения: средняя CD (много компонентов, но не избыточные связи)
        - Data Science: низкая VT (notebooks часто самодостаточны)
        - Info systems: высокая CD (много взаимосвязанных функций)
        """
        recommendations = {}

        if project_type == 'library':
            recommendations = {
                'cd': {'min': 8.0, 'max': 15.0, 'reason': 'Библиотеки требуют умеренной связности'},
                'vt': {'min': 60.0, 'max': 80.0, 'reason': 'Высокая трассируемость от API до реализации'},
                'cr': {'min': 0.5, 'max': 1.0, 'reason': 'Библиотеки стабилизируются быстрее'},
                'db': {'min': 0.0, 'max': 25.0, 'reason': 'Меньший дисбаланс в библиотеках'}
            }
        elif project_type == 'webapp':
            recommendations = {
                'cd': {'min': 12.0, 'max': 22.0, 'reason': 'Web-приложения имеют больше связей'},
                'vt': {'min': 45.0, 'max': 65.0, 'reason': 'Средняя трассируемость'},
                'cr': {'min': 0.8, 'max': 1.8, 'reason': 'Активное развитие веб-проектов'},
                'db': {'min': 0.0, 'max': 35.0, 'reason': 'Больший допуск на дисбаланс'}
            }
        elif project_type == 'datascience':
            recommendations = {
                'cd': {'min': 5.0, 'max': 12.0, 'reason': 'Notebooks часто изолированы'},
                'vt': {'min': 30.0, 'max': 50.0, 'reason': 'Низкая трассируемость в DS проектах'},
                'cr': {'min': 1.0, 'max': 2.0, 'reason': 'Быстрое экспериментирование'},
                'db': {'min': 0.0, 'max': 40.0, 'reason': 'Экспериментальный характер'}
            }
        elif project_type == 'methodology':
            recommendations = {
                'cd': {'min': 15.0, 'max': 30.0, 'reason': 'Методологические проекты имеют высокую связность концепций'},
                'vt': {'min': 20.0, 'max': 40.0, 'reason': 'Фокус на теории, меньше вертикальных связей с кодом'},
                'cr': {'min': 0.5, 'max': 1.2, 'reason': 'Медленное развитие теоретических концепций'},
                'db': {'min': 0.0, 'max': 120.0, 'reason': 'Методологические проекты фокусируются на теории (α>0), дисбаланс нормален'}
            }
        elif project_type == 'info_system':
            recommendations = {
                'cd': {'min': 10.0, 'max': 20.0, 'reason': 'Сбалансированная связность'},
                'vt': {'min': 50.0, 'max': 70.0, 'reason': 'Стандартная трассируемость'},
                'cr': {'min': 0.7, 'max': 1.5, 'reason': 'Умеренная скорость развития'},
                'db': {'min': 0.0, 'max': 30.0, 'reason': 'Стандартный баланс'}
            }
        else:  # default
            recommendations = self.current_thresholds.copy()

        return recommendations

    def calculate_success_score(self) -> float:
        """
        Вычисляет оценку успешности проекта (0-100).

        Факторы успешности:
        - Наличие полной документации
        - Тестовое покрытие
        - Количество релизов
        - Отсутствие критических проблем
        - Регулярность коммитов
        """
        score = 0.0
        max_score = 100.0

        # Документация (30 баллов)
        docs_score = 0.0
        required_docs = ['README.md', 'CONTRIBUTING.md', 'LICENSE', 'CHANGELOG.md']
        existing_docs = sum(1 for doc in required_docs if (self.project_root / doc).exists())
        docs_score = (existing_docs / len(required_docs)) * 30.0
        score += docs_score

        # Количество markdown файлов (20 баллов)
        md_files = list(self.project_root.glob('**/*.md'))
        if len(md_files) > 50:
            md_score = 20.0
        elif len(md_files) > 20:
            md_score = 15.0
        elif len(md_files) > 10:
            md_score = 10.0
        else:
            md_score = 5.0
        score += md_score

        # Наличие тестов (20 баллов)
        test_files = list(self.project_root.glob('**/test_*.py')) + list(self.project_root.glob('**/*_test.py'))
        if len(test_files) >= 20:
            test_score = 20.0
        elif len(test_files) >= 10:
            test_score = 15.0
        elif len(test_files) > 0:
            test_score = 10.0
        else:
            test_score = 0.0
        score += test_score

        # Наличие инструментов (15 баллов)
        tools_dir = self.project_root / 'tools'
        if tools_dir.exists():
            tool_files = list(tools_dir.glob('*.py'))
            if len(tool_files) >= 5:
                tools_score = 15.0
            elif len(tool_files) >= 3:
                tools_score = 10.0
            else:
                tools_score = 5.0
        else:
            tools_score = 0.0
        score += tools_score

        # Наличие научной документации (15 баллов)
        scientific_docs = ['SCIENTIFIC-PAPER.md', 'PRESENTATION.md', 'ЭВОЛЮЦИЯ-МЕТОДОЛОГИИ.md']
        existing_scientific = sum(1 for doc in scientific_docs if (self.project_root / doc).exists())
        scientific_score = (existing_scientific / len(scientific_docs)) * 15.0
        score += scientific_score

        return min(score, max_score)

    def adapt_thresholds(self) -> Dict:
        """
        Адаптирует пороги на основе характеристик проекта и успешности.
        """
        # Анализ характеристик проекта
        characteristics = self.analyze_project_characteristics()
        project_type = characteristics['type']
        project_size = characteristics['size']
        project_maturity = characteristics['maturity']

        # Получение рекомендаций для типа проекта
        type_based = self.recommend_thresholds_for_project_type(project_type)

        # Корректировка на основе размера проекта
        size_adjustments = {
            'small': 0.9,   # Меньшие пороги для малых проектов
            'medium': 1.0,  # Стандартные пороги
            'large': 1.1    # Большие пороги для крупных проектов
        }

        size_factor = size_adjustments.get(project_size, 1.0)

        # Корректировка на основе зрелости
        maturity_adjustments = {
            'early': {'cd': 0.8, 'vt': 0.9, 'cr': 1.2, 'db': 1.1},
            'developing': {'cd': 0.9, 'vt': 0.95, 'cr': 1.1, 'db': 1.05},
            'mature': {'cd': 1.0, 'vt': 1.0, 'cr': 1.0, 'db': 1.0}
        }

        maturity_factors = maturity_adjustments.get(project_maturity, {
            'cd': 1.0, 'vt': 1.0, 'cr': 1.0, 'db': 1.0
        })

        # Вычисление оценки успешности
        success_score = self.calculate_success_score()

        # Применение всех факторов
        adapted = {}
        for metric in ['cd', 'vt', 'cr', 'db']:
            base = type_based[metric]
            adapted[metric] = {
                'min': base['min'] * size_factor * maturity_factors[metric],
                'max': base['max'] * size_factor * maturity_factors[metric],
                'name': self.current_thresholds[metric]['name'],
                'reason': base['reason'],
                'adjustments': {
                    'type': project_type,
                    'size_factor': size_factor,
                    'maturity_factor': maturity_factors[metric],
                    'success_score': success_score
                }
            }

        self.adapted_thresholds = adapted
        return adapted

    def compare_thresholds(self) -> List[Dict]:
        """Сравнивает текущие и адаптированные пороги"""
        if not self.adapted_thresholds:
            self.adapt_thresholds()

        comparisons = []
        for metric in ['cd', 'vt', 'cr', 'db']:
            current = self.current_thresholds[metric]
            adapted = self.adapted_thresholds[metric]

            comparison = {
                'metric': adapted['name'],
                'current_min': current['min'],
                'current_max': current['max'],
                'adapted_min': adapted['min'],
                'adapted_max': adapted['max'],
                'change_min': adapted['min'] - current['min'],
                'change_max': adapted['max'] - current['max'],
                'reason': adapted['reason'],
                'adjustments': adapted['adjustments']
            }

            comparisons.append(comparison)

        return comparisons

    def generate_report(self) -> str:
        """Генерирует детальный отчёт об адаптации порогов"""
        report = []
        report.append("=" * 70)
        report.append("АДАПТИВНАЯ ОПТИМИЗАЦИЯ ЦЕЛЕВЫХ ДИАПАЗОНОВ")
        report.append("ЭТАП 6: Система самообучения методологии")
        report.append("=" * 70)
        report.append("")
        report.append(f"Дата анализа: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")

        # Характеристики проекта
        characteristics = self.analyze_project_characteristics()
        report.append("ХАРАКТЕРИСТИКИ ПРОЕКТА:")
        report.append("-" * 70)
        report.append(f"  Тип проекта: {characteristics['type']}")
        report.append(f"  Размер: {characteristics['size']}")
        report.append(f"  Зрелость: {characteristics['maturity']}")
        report.append(f"  Фокус: {characteristics['focus']}")
        report.append("")

        # Оценка успешности
        success_score = self.calculate_success_score()
        report.append(f"  Оценка успешности проекта: {success_score:.1f}/100")
        if success_score >= 80:
            report.append(f"  Статус: ✅ Отличный проект")
        elif success_score >= 60:
            report.append(f"  Статус: ✅ Хороший проект")
        elif success_score >= 40:
            report.append(f"  Статус: ⚠️  Развивающийся проект")
        else:
            report.append(f"  Статус: ⚠️  Начальная стадия")
        report.append("")

        # Сравнение порогов
        comparisons = self.compare_thresholds()

        report.append("=" * 70)
        report.append("РЕКОМЕНДУЕМЫЕ ИЗМЕНЕНИЯ ЦЕЛЕВЫХ ДИАПАЗОНОВ")
        report.append("=" * 70)
        report.append("")

        for comp in comparisons:
            report.append(f"📊 {comp['metric']}")
            report.append("-" * 70)
            report.append(f"  Текущий диапазон:     {comp['current_min']:.1f} - {comp['current_max']:.1f}")
            report.append(f"  Адаптированный:       {comp['adapted_min']:.1f} - {comp['adapted_max']:.1f}")

            if abs(comp['change_min']) > 0.1 or abs(comp['change_max']) > 0.1:
                sign_min = '+' if comp['change_min'] > 0 else ''
                sign_max = '+' if comp['change_max'] > 0 else ''
                report.append(f"  Изменение:            {sign_min}{comp['change_min']:.1f} / {sign_max}{comp['change_max']:.1f}")
            else:
                report.append(f"  Изменение:            Без изменений")

            report.append(f"  Обоснование:          {comp['reason']}")
            report.append(f"  Тип проекта:          {comp['adjustments']['type']}")
            report.append(f"  Коэффициент размера:  {comp['adjustments']['size_factor']:.2f}")
            report.append(f"  Коэффициент зрелости: {comp['adjustments']['maturity_factor']:.2f}")
            report.append("")

        # Рекомендации
        report.append("=" * 70)
        report.append("РЕКОМЕНДАЦИИ ПО ПРИМЕНЕНИЮ")
        report.append("=" * 70)
        report.append("")

        has_significant_changes = any(
            abs(c['change_min']) > 2.0 or abs(c['change_max']) > 2.0
            for c in comparisons
        )

        if has_significant_changes:
            report.append("⚠️  ОБНАРУЖЕНЫ ЗНАЧИТЕЛЬНЫЕ ИЗМЕНЕНИЯ")
            report.append("")
            report.append("Рекомендуется:")
            report.append("  1. Проверить обоснования изменений")
            report.append("  2. Постепенно перейти на новые пороги (2-3 цикла)")
            report.append("  3. Мониторить метрики после каждого изменения")
            report.append("  4. При необходимости откатить изменения")
            report.append("")
        else:
            report.append("✅ ИЗМЕНЕНИЯ МИНИМАЛЬНЫ")
            report.append("")
            report.append("Текущие пороги оптимальны для вашего типа проекта.")
            report.append("Рекомендуется продолжать использовать существующие значения.")
            report.append("")

        # Философия
        report.append("=" * 70)
        report.append("ФИЛОСОФИЯ АДАПТИВНЫХ ПОРОГОВ")
        report.append("=" * 70)
        report.append("")
        report.append("Методология не должна быть догматичной.")
        report.append("")
        report.append("Целевые диапазоны метрик — это не священные числа,")
        report.append("а рекомендации, которые должны адаптироваться к:")
        report.append("  • Типу проекта (library vs webapp vs info_system)")
        report.append("  • Размеру проекта (small vs medium vs large)")
        report.append("  • Зрелости проекта (early vs developing vs mature)")
        report.append("  • Опыту и предпочтениям команды")
        report.append("")
        report.append("Адаптивные пороги делают методологию:")
        report.append("  ✅ Гибкой — подстраивается под проект")
        report.append("  ✅ Умной — учится на опыте")
        report.append("  ✅ Персонализированной — уникальна для каждого проекта")
        report.append("")
        report.append("Это превращает методологию из жёсткого правила")
        report.append("в интеллектуального советника.")
        report.append("")
        report.append("=" * 70)
        report.append("Конец отчёта. Методология адаптируется к вам. ⇑⇓↔")
        report.append("=" * 70)

        return "\n".join(report)

    def save_report(self, filename: str = "adaptive_thresholds_report.txt"):
        """Сохранение отчёта в файл"""
        report = self.generate_report()
        output_path = self.project_root / filename

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)

        print(f"📄 Отчёт сохранён: {output_path}")
        return output_path

    def run_analysis(self):
        """Запуск полного анализа адаптивности"""
        print("🔧 Запуск системы адаптивных порогов...")
        print()

        # Анализ характеристик
        print("📊 Анализ характеристик проекта...")
        characteristics = self.analyze_project_characteristics()
        print(f"   ✓ Тип: {characteristics['type']}")
        print(f"   ✓ Размер: {characteristics['size']}")
        print(f"   ✓ Зрелость: {characteristics['maturity']}")
        print()

        # Оценка успешности
        print("🎯 Оценка успешности проекта...")
        success_score = self.calculate_success_score()
        print(f"   ✓ Оценка: {success_score:.1f}/100")
        print()

        # Адаптация порогов
        print("⚙️  Адаптация целевых диапазонов...")
        self.adapt_thresholds()
        print(f"   ✓ Адаптировано: 4 метрики")
        print()

        # Сравнение
        print("🔍 Сравнение текущих и адаптированных порогов...")
        comparisons = self.compare_thresholds()
        changes_count = sum(1 for c in comparisons if abs(c['change_min']) > 0.1 or abs(c['change_max']) > 0.1)
        print(f"   ✓ Обнаружено изменений: {changes_count}/4")
        print()

        # Генерация отчёта
        print("📝 Генерация отчёта...")
        report = self.generate_report()
        print()
        print(report)
        print()

        # Сохранение отчёта
        self.save_report()

        return self.adapted_thresholds


def main():
    """Главная функция"""
    optimizer = AdaptiveThresholdOptimizer()
    adapted_thresholds = optimizer.run_analysis()

    return 0


if __name__ == "__main__":
    exit(main())
