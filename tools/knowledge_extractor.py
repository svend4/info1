#!/usr/bin/env python3
"""
Knowledge Extractor (ЭТАП 7: Коллективный интеллект)

Извлекает инсайты и паттерны из истории метрик проекта для передачи
другим проектам.

Ключевые функции:
1. Анализ трендов метрик
2. Обнаружение паттернов улучшений
3. Извлечение lessons learned
4. Экспорт знаний в standardized format

Уровень абстракции: α=-4 (исполняемый код)
Статус: ⇑ ВВЕРХ (инструмент для ЭТАПА 7)

Вертикальные связи (⇑ к философии и концепциям):
    ⇑ ЭТАП-7-КОЛЛЕКТИВНЫЙ-ИНТЕЛЛЕКТ.md (α=+2) — концепция коллективного обучения
    ⇑ БАЗА-ЗНАНИЙ-ПАТТЕРНОВ.md (α=+2) — structured knowledge base
    ⇑ ФИЛОСОФИЯ-ПРОЕКТА.md (α=+3) — принцип обмена знаниями
    ⇑ ЭТАП-6-САМОСОВЕРШЕНСТВОВАНИЕ.md (α=+2) — история как основа для обучения

Горизонтальные связи (↔ другие инструменты α=-4):
    ↔ save_metrics.py — источник истории метрик
    ↔ self_improvement.py — генератор рекомендаций
    ↔ predictive_warnings.py — предсказание на основе истории
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from pathlib import Path
import statistics


class KnowledgeExtractor:
    """Извлекатель знаний из истории проекта"""

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.history_file = self.project_root / "tools" / "metrics_history.json"
        self.knowledge_base = self.project_root / "БАЗА-ЗНАНИЙ-ПАТТЕРНОВ.md"
        self.history: List[Dict] = []

    def load_history(self) -> bool:
        """Загрузка истории метрик"""
        if not self.history_file.exists():
            print(f"⚠️  История метрик не найдена: {self.history_file}")
            return False

        with open(self.history_file, 'r', encoding='utf-8') as f:
            self.history = json.load(f)

        print(f"✅ Загружено {len(self.history)} записей истории")
        return True

    def analyze_trends(self) -> Dict[str, Dict]:
        """Анализ трендов метрик"""
        trends = {}

        # Фильтруем записи с полными метриками
        complete_records = [r for r in self.history if 'cd' in r and 'vt' in r]

        if len(complete_records) < 2:
            return {}

        for metric in ['cd', 'vt', 'cr', 'db']:
            values = [r[metric] for r in complete_records if metric in r]

            if len(values) < 2:
                continue

            # Тренд
            first_half = values[:len(values)//2] if len(values) > 2 else [values[0]]
            second_half = values[len(values)//2:]

            avg_first = statistics.mean(first_half)
            avg_second = statistics.mean(second_half)

            change = avg_second - avg_first
            change_pct = (change / avg_first * 100) if avg_first != 0 else 0

            # Направление тренда
            if abs(change_pct) < 5:
                direction = "стабильный"
                emoji = "→"
            elif change_pct > 0:
                direction = "растущий"
                emoji = "📈"
            else:
                direction = "падающий"
                emoji = "📉"

            trends[metric] = {
                'values': values,
                'first_avg': round(avg_first, 2),
                'second_avg': round(avg_second, 2),
                'change': round(change, 2),
                'change_pct': round(change_pct, 2),
                'direction': direction,
                'emoji': emoji,
                'current': values[-1] if values else None
            }

        return trends

    def detect_improvements(self) -> List[Dict]:
        """Обнаружение значимых улучшений"""
        improvements = []

        complete_records = [r for r in self.history if 'cd' in r and 'vt' in r]

        if len(complete_records) < 2:
            return []

        for i in range(1, len(complete_records)):
            prev = complete_records[i-1]
            curr = complete_records[i]

            for metric in ['cd', 'vt', 'cr', 'db']:
                if metric not in prev or metric not in curr:
                    continue

                change = curr[metric] - prev[metric]
                change_pct = (change / prev[metric] * 100) if prev[metric] != 0 else 0

                # Значимое изменение: >5% для CD/VT/DB, >10% для CR
                threshold = 10 if metric == 'cr' else 5

                if abs(change_pct) > threshold:
                    improvements.append({
                        'metric': metric.upper(),
                        'timestamp': curr.get('timestamp', 'unknown'),
                        'prev_value': round(prev[metric], 2),
                        'curr_value': round(curr[metric], 2),
                        'change': round(change, 2),
                        'change_pct': round(change_pct, 2),
                        'improvement': change < 0 if metric in ['cd', 'db'] else change > 0
                    })

        return improvements

    def extract_lessons(self) -> List[Dict]:
        """Извлечение уроков из истории"""
        lessons = []
        trends = self.analyze_trends()

        # Урок 1: DB улучшился
        if 'db' in trends:
            db_trend = trends['db']
            if db_trend['change'] < -30:  # Значительное улучшение
                lessons.append({
                    'id': 'lesson_db_improvement',
                    'title': 'Исправление логики определения направлений',
                    'category': 'metrics',
                    'severity': 'critical',
                    'evidence': {
                        'before': db_trend['first_avg'],
                        'after': db_trend['current'],
                        'change': db_trend['change']
                    },
                    'principle': 'Семантический анализ надежнее текстового поиска',
                    'confidence': 0.95
                })

        # Урок 2: CD растет
        if 'cd' in trends:
            cd_trend = trends['cd']
            if cd_trend['change_pct'] > 10:  # Рост >10%
                lessons.append({
                    'id': 'lesson_cd_growth',
                    'title': 'Качество связей важнее количества',
                    'category': 'architecture',
                    'severity': 'medium',
                    'evidence': {
                        'before': cd_trend['first_avg'],
                        'after': cd_trend['current'],
                        'change_pct': cd_trend['change_pct']
                    },
                    'principle': 'Лучше 10 качественных связей, чем 30 случайных',
                    'confidence': 0.85
                })

        # Урок 3: История улучшений
        improvements = self.detect_improvements()
        if len(improvements) >= 3:
            lessons.append({
                'id': 'lesson_iterative_improvement',
                'title': 'Итеративное улучшение работает',
                'category': 'process',
                'severity': 'high',
                'evidence': {
                    'improvements_count': len(improvements),
                    'history_length': len(self.history)
                },
                'principle': 'Маленькие улучшения каждый день лучше одного большого',
                'confidence': 0.90
            })

        return lessons

    def export_knowledge(self, output_file: str = "knowledge_export.json"):
        """Экспорт знаний в standardized format"""
        trends = self.analyze_trends()
        improvements = self.detect_improvements()
        lessons = self.extract_lessons()

        # Метаданные проекта
        project_metadata = {
            'project_name': 'info1',
            'project_type': 'methodology',
            'history_length': len(self.history),
            'export_date': datetime.now().isoformat(),
            'methodology_version': 'v1.0 (ЭТАП 6-7)'
        }

        # Текущее состояние
        current_state = {}
        if self.history and len(self.history) > 0:
            latest = self.history[-1]
            current_state = {
                'cd': latest.get('cd'),
                'vt': latest.get('vt'),
                'cr': latest.get('cr'),
                'db': latest.get('db'),
                'total_docs': latest.get('total_docs'),
                'total_connections': latest.get('total_connections'),
                'cycle': latest.get('cycle')
            }

        export = {
            'metadata': project_metadata,
            'current_state': current_state,
            'trends': trends,
            'improvements': improvements,
            'lessons': lessons
        }

        output_path = self.project_root / output_file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export, f, indent=2, ensure_ascii=False)

        print(f"\n📦 Знания экспортированы: {output_path}")
        print(f"   • Трендов: {len(trends)}")
        print(f"   • Улучшений: {len(improvements)}")
        print(f"   • Уроков: {len(lessons)}")

        return export

    def generate_report(self):
        """Генерация человекочитаемого отчета"""
        print("\n" + "="*70)
        print("ИЗВЛЕЧЕНИЕ ЗНАНИЙ ИЗ ИСТОРИИ ПРОЕКТА")
        print("ЭТАП 7: Коллективный интеллект")
        print("="*70)

        if not self.load_history():
            return

        # Анализ трендов
        print("\n📈 АНАЛИЗ ТРЕНДОВ МЕТРИК")
        print("-" * 70)

        trends = self.analyze_trends()
        for metric, data in trends.items():
            print(f"\n{metric.upper()}:")
            print(f"  {data['emoji']} Направление: {data['direction']}")
            print(f"  📊 Первая половина: {data['first_avg']}")
            print(f"  📊 Вторая половина: {data['second_avg']}")
            print(f"  📊 Изменение: {data['change']:+.2f} ({data['change_pct']:+.1f}%)")
            print(f"  📊 Текущее значение: {data['current']}")

        # Значимые улучшения
        print("\n\n🎯 ОБНАРУЖЕННЫЕ УЛУЧШЕНИЯ")
        print("-" * 70)

        improvements = self.detect_improvements()
        if improvements:
            for imp in improvements:
                emoji = "✅" if imp['improvement'] else "⚠️"
                print(f"\n{emoji} {imp['metric']}:")
                print(f"  📅 Время: {imp['timestamp']}")
                print(f"  📊 Было: {imp['prev_value']}")
                print(f"  📊 Стало: {imp['curr_value']}")
                print(f"  📊 Изменение: {imp['change']:+.2f} ({imp['change_pct']:+.1f}%)")
        else:
            print("\nПока не обнаружено значимых улучшений (требуется больше истории)")

        # Извлеченные уроки
        print("\n\n🎓 ИЗВЛЕЧЁННЫЕ УРОКИ")
        print("-" * 70)

        lessons = self.extract_lessons()
        if lessons:
            for lesson in lessons:
                print(f"\n📚 {lesson['title']}")
                print(f"  Категория: {lesson['category']}")
                print(f"  Серьезность: {lesson['severity']}")
                print(f"  Принцип: {lesson['principle']}")
                print(f"  Уверенность: {lesson['confidence']*100:.0f}%")
                if 'evidence' in lesson:
                    print(f"  Доказательства: {lesson['evidence']}")
        else:
            print("\nУроки будут извлечены после накопления большей истории")

        # Экспорт
        print("\n\n📦 ЭКСПОРТ ЗНАНИЙ")
        print("-" * 70)
        export = self.export_knowledge()

        print("\n" + "="*70)
        print("✅ Анализ завершён")
        print("="*70)
        print("\nЗнания готовы к обмену с другими проектами!")
        print("Формат: knowledge_export.json (JSON)")
        print("Совместим с: ЭТАП 7 (Коллективный интеллект)")
        print("\n")


def main():
    """Главная функция"""
    extractor = KnowledgeExtractor('.')
    extractor.generate_report()
    return 0


if __name__ == "__main__":
    exit(main())
