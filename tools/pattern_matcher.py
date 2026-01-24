#!/usr/bin/env python3
"""
Pattern Matcher (ЭТАП 7: Коллективный интеллект)

ML-анализатор паттернов для обнаружения универсальных закономерностей
в коллективных данных методологии ⇑⇓↔.

Ключевые функции:
1. Кластеризация проектов по метрикам
2. Обнаружение корреляций между метриками
3. Выявление успешных паттернов
4. Предсказание оптимальных порогов
5. Анализ трендов в сети

Уровень абстракции: α=-4 (исполняемый код)
Статус: ⇑ ВВЕРХ (ML для ЭТАПА 7)

Вертикальные связи (⇑ к философии и концепциям):
    ⇑ ЭТАП-7-КОЛЛЕКТИВНЫЙ-ИНТЕЛЛЕКТ.md (α=+2) — ML как часть коллективного разума
    ⇑ БАЗА-ЗНАНИЙ-ПАТТЕРНОВ.md (α=+2) — паттерны для обнаружения
    ⇑ ФИЛОСОФИЯ-ПРОЕКТА.md (α=+3) — обучение на коллективном опыте

Горизонтальные связи (↔ другие инструменты α=-4):
    ↔ collective_intelligence.py — источник коллективных данных
    ↔ adaptive_metrics.py — адаптация порогов на основе паттернов
"""

import json
import math
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict


class PatternMatcher:
    """ML-анализатор паттернов в коллективных данных"""

    def __init__(self, network_dir: str = "collective_network"):
        self.network_dir = Path(network_dir)
        self.projects = []
        self.patterns = []

    def load_network_data(self) -> bool:
        """Загрузка данных из коллективной сети"""
        if not self.network_dir.exists():
            print(f"⚠️  Директория сети не найдена: {self.network_dir}")
            return False

        self.projects = []
        for export_file in self.network_dir.glob("export_*.json"):
            with open(export_file, 'r', encoding='utf-8') as f:
                project = json.load(f)
                # Фильтруем проекты с полными метриками
                if 'metrics' in project and all(m in project['metrics'] for m in ['cd', 'vt', 'cr', 'db']):
                    self.projects.append(project)

        print(f"✅ Загружено проектов: {len(self.projects)}")
        return len(self.projects) > 0

    def calculate_correlation(self, metric1: str, metric2: str) -> float:
        """
        Вычисляет корреляцию Пирсона между двумя метриками

        Returns: correlation coefficient (-1 to 1)
        """
        values1 = [p['metrics'][metric1] for p in self.projects if metric1 in p['metrics']]
        values2 = [p['metrics'][metric2] for p in self.projects if metric2 in p['metrics']]

        if len(values1) < 2 or len(values2) < 2:
            return 0.0

        n = min(len(values1), len(values2))
        values1 = values1[:n]
        values2 = values2[:n]

        # Средние значения
        mean1 = sum(values1) / n
        mean2 = sum(values2) / n

        # Ковариация
        cov = sum((values1[i] - mean1) * (values2[i] - mean2) for i in range(n)) / n

        # Стандартные отклонения
        std1 = math.sqrt(sum((v - mean1) ** 2 for v in values1) / n)
        std2 = math.sqrt(sum((v - mean2) ** 2 for v in values2) / n)

        if std1 == 0 or std2 == 0:
            return 0.0

        # Корреляция
        correlation = cov / (std1 * std2)
        return round(correlation, 3)

    def find_correlations(self) -> List[Dict]:
        """Находит значимые корреляции между метриками"""
        print("\n🔍 Поиск корреляций между метриками...")

        metrics = ['cd', 'vt', 'cr', 'db']
        correlations = []

        for i, m1 in enumerate(metrics):
            for m2 in metrics[i+1:]:
                corr = self.calculate_correlation(m1, m2)

                if abs(corr) > 0.3:  # Значимая корреляция
                    correlations.append({
                        'metric1': m1.upper(),
                        'metric2': m2.upper(),
                        'correlation': corr,
                        'strength': 'strong' if abs(corr) > 0.7 else 'moderate' if abs(corr) > 0.5 else 'weak',
                        'direction': 'positive' if corr > 0 else 'negative'
                    })

        # Сортировка по силе корреляции
        correlations.sort(key=lambda x: abs(x['correlation']), reverse=True)

        print(f"  ✓ Найдено значимых корреляций: {len(correlations)}")
        return correlations

    def cluster_by_success(self) -> Dict[str, List]:
        """
        Кластеризация проектов на "успешные" и "проблемные"

        Success criteria: VT > 40%, CD < 30%, DB < 50%
        """
        print("\n📊 Кластеризация проектов по успешности...")

        successful = []
        problematic = []

        for project in self.projects:
            metrics = project['metrics']
            score = 0

            # Критерии успеха
            if metrics.get('vt', 0) > 40:
                score += 1
            if 10 <= metrics.get('cd', 0) <= 30:
                score += 1
            if metrics.get('db', 100) < 50:
                score += 1
            if 0.7 <= metrics.get('cr', 0) <= 1.5:
                score += 1

            if score >= 3:
                successful.append(project)
            else:
                problematic.append(project)

        print(f"  ✓ Успешных проектов: {len(successful)}")
        print(f"  ✓ Проблемных проектов: {len(problematic)}")

        return {
            'successful': successful,
            'problematic': problematic
        }

    def find_success_patterns(self, clusters: Dict) -> List[Dict]:
        """Находит паттерны успешных проектов"""
        print("\n🎯 Поиск паттернов успешных проектов...")

        successful = clusters['successful']
        if not successful:
            print("  ⚠️  Нет успешных проектов для анализа")
            return []

        patterns = []

        # Паттерн 1: Средние метрики успешных проектов
        avg_metrics = {}
        for metric in ['cd', 'vt', 'cr', 'db']:
            values = [p['metrics'][metric] for p in successful if metric in p['metrics']]
            if values:
                avg_metrics[metric] = round(sum(values) / len(values), 2)

        if avg_metrics:
            patterns.append({
                'name': 'successful_metrics_avg',
                'type': 'statistical',
                'description': 'Средние метрики успешных проектов',
                'data': avg_metrics,
                'sample_size': len(successful),
                'confidence': 0.8 if len(successful) >= 3 else 0.6
            })

        # Паттерн 2: Распределение по типам
        type_distribution = defaultdict(int)
        for project in successful:
            type_distribution[project['project_type']] += 1

        if type_distribution:
            # Самый успешный тип
            most_successful_type = max(type_distribution.items(), key=lambda x: x[1])
            patterns.append({
                'name': 'successful_project_type',
                'type': 'categorical',
                'description': f'Самый успешный тип проектов',
                'data': {
                    'type': most_successful_type[0],
                    'count': most_successful_type[1],
                    'distribution': dict(type_distribution)
                },
                'confidence': 0.7
            })

        # Паттерн 3: Уроки из успешных проектов
        successful_lessons = []
        for project in successful:
            if 'lessons' in project:
                for lesson in project['lessons']:
                    if lesson.get('confidence', 0) > 0.8:
                        successful_lessons.append(lesson)

        if successful_lessons:
            patterns.append({
                'name': 'high_confidence_lessons',
                'type': 'knowledge',
                'description': 'Уроки с высокой уверенностью из успешных проектов',
                'data': successful_lessons,
                'confidence': 0.85
            })

        print(f"  ✓ Найдено паттернов: {len(patterns)}")
        return patterns

    def predict_optimal_thresholds(self, project_type: str) -> Dict:
        """
        Предсказывает оптимальные пороги для типа проекта
        на основе успешных проектов
        """
        print(f"\n🔮 Предсказание оптимальных порогов для '{project_type}'...")

        # Фильтрация проектов по типу
        type_projects = [p for p in self.projects if p['project_type'] == project_type]

        if not type_projects:
            print(f"  ⚠️  Нет данных для типа '{project_type}'")
            return {}

        # Кластеризация
        clusters = {'successful': [], 'problematic': []}
        for project in type_projects:
            metrics = project['metrics']
            score = 0
            if metrics.get('vt', 0) > 40:
                score += 1
            if 10 <= metrics.get('cd', 0) <= 30:
                score += 1
            if metrics.get('db', 100) < 50:
                score += 1

            if score >= 2:
                clusters['successful'].append(project)
            else:
                clusters['problematic'].append(project)

        successful = clusters['successful']
        if not successful:
            print(f"  ⚠️  Нет успешных проектов типа '{project_type}'")
            return {}

        # Вычисление оптимальных диапазонов
        thresholds = {}
        for metric in ['cd', 'vt', 'cr', 'db']:
            values = [p['metrics'][metric] for p in successful if metric in p['metrics']]
            if values:
                min_val = min(values)
                max_val = max(values)
                avg_val = sum(values) / len(values)

                # Расширение диапазона на 20% для толерантности
                range_size = max_val - min_val
                margin = range_size * 0.2

                thresholds[metric] = {
                    'min': round(max(0, min_val - margin), 1),
                    'max': round(max_val + margin, 1),
                    'optimal': round(avg_val, 1),
                    'sample_size': len(values)
                }

        print(f"  ✓ Предсказано порогов для {len(thresholds)} метрик")
        return thresholds

    def generate_report(self) -> Dict:
        """Генерирует полный отчет анализа паттернов"""
        print("\n" + "="*70)
        print("АНАЛИЗ ПАТТЕРНОВ В КОЛЛЕКТИВНЫХ ДАННЫХ")
        print("ML-система выявления универсальных закономерностей")
        print("="*70)

        if not self.load_network_data():
            return {}

        report = {
            'total_projects': len(self.projects),
            'correlations': self.find_correlations(),
            'clusters': self.cluster_by_success(),
            'patterns': [],
            'predicted_thresholds': {}
        }

        # Паттерны успеха
        report['patterns'] = self.find_success_patterns(report['clusters'])

        # Предсказание порогов для каждого типа
        project_types = set(p['project_type'] for p in self.projects)
        for proj_type in project_types:
            thresholds = self.predict_optimal_thresholds(proj_type)
            if thresholds:
                report['predicted_thresholds'][proj_type] = thresholds

        # Вывод отчета
        self.display_report(report)

        # Сохранение
        output_file = self.network_dir / "pattern_analysis.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"\n📄 Отчет сохранен: {output_file}")
        return report

    def display_report(self, report: Dict):
        """Отображает отчет в человекочитаемом виде"""
        print(f"\n📊 СТАТИСТИКА")
        print(f"  Проектов в сети: {report['total_projects']}")
        print(f"  Успешных: {len(report['clusters']['successful'])}")
        print(f"  Проблемных: {len(report['clusters']['problematic'])}")

        # Корреляции
        if report['correlations']:
            print(f"\n🔗 КОРРЕЛЯЦИИ МЕТРИК")
            for corr in report['correlations'][:5]:  # Топ-5
                emoji = "📈" if corr['direction'] == 'positive' else "📉"
                print(f"  {emoji} {corr['metric1']} ↔ {corr['metric2']}: {corr['correlation']:+.3f} ({corr['strength']})")

        # Паттерны
        if report['patterns']:
            print(f"\n🎯 ОБНАРУЖЕННЫЕ ПАТТЕРНЫ ({len(report['patterns'])})")
            for i, pattern in enumerate(report['patterns'], 1):
                print(f"\n  {i}. {pattern['description']}")
                print(f"     Тип: {pattern['type']}")
                print(f"     Уверенность: {pattern['confidence']*100:.0f}%")

                if pattern['name'] == 'successful_metrics_avg':
                    print(f"     Средние метрики успешных:")
                    for metric, value in pattern['data'].items():
                        print(f"       • {metric.upper()}: {value}")

        # Предсказанные пороги
        if report['predicted_thresholds']:
            print(f"\n🔮 ПРЕДСКАЗАННЫЕ ОПТИМАЛЬНЫЕ ПОРОГИ")
            for proj_type, thresholds in report['predicted_thresholds'].items():
                print(f"\n  📁 {proj_type}:")
                for metric, bounds in thresholds.items():
                    print(f"     {metric.upper()}: {bounds['min']}-{bounds['max']} (оптимум: {bounds['optimal']})")

        print("\n" + "="*70)
        print("✅ Анализ завершен")
        print("="*70)


def main():
    """Главная функция"""
    matcher = PatternMatcher()
    matcher.generate_report()
    return 0


if __name__ == "__main__":
    exit(main())
