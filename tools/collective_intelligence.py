#!/usr/bin/env python3
"""
Collective Intelligence System (ЭТАП 7: Коллективный интеллект)

Система подключения проекта к коллективной сети для обмена метриками,
паттернами и извлеченными уроками.

Ключевые функции:
1. Экспорт метрик в стандартизированный формат (MEP - Methodology Exchange Protocol)
2. Симуляция обмена знаниями между проектами (локально)
3. Анализ коллективного опыта
4. Генерация рекомендаций на основе опыта других проектов
5. Конфиденциальность (анонимизация, opt-in)

Уровень абстракции: α=-4 (исполняемый код)
Статус: ⇑ ВВЕРХ (инструмент ЭТАПА 7)

Вертикальные связи (⇑ к философии и концепциям):
    ⇑ ЭТАП-7-КОЛЛЕКТИВНЫЙ-ИНТЕЛЛЕКТ.md (α=+2) — концепция коллективного обучения
    ⇑ БАЗА-ЗНАНИЙ-ПАТТЕРНОВ.md (α=+2) — structured knowledge для обмена
    ⇑ ФИЛОСОФИЯ-ПРОЕКТА.md (α=+3) — принцип открытости и обмена знаниями

Горизонтальные связи (↔ другие инструменты α=-4):
    ↔ knowledge_extractor.py — источник извлеченных уроков
    ↔ save_metrics.py — история метрик для экспорта
    ↔ adaptive_metrics.py — адаптивные пороги из коллективного опыта
"""

import json
import hashlib
import os
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path


class CollectiveIntelligence:
    """Система коллективного интеллекта для обмена опытом между проектами"""

    def __init__(self, project_root: str = ".", opt_in: bool = True):
        self.project_root = Path(project_root)
        self.opt_in = opt_in
        self.project_id = self._generate_anonymous_id()

        # Локальное хранилище для симуляции
        self.network_dir = self.project_root / "collective_network"
        self.network_dir.mkdir(exist_ok=True)

        # Файлы
        self.export_file = self.network_dir / f"export_{self.project_id}.json"
        self.recommendations_file = self.network_dir / "collective_recommendations.json"

    def _generate_anonymous_id(self) -> str:
        """Генерация анонимного ID проекта на основе пути"""
        project_path = str(self.project_root.resolve())
        hash_obj = hashlib.sha256(project_path.encode())
        return hash_obj.hexdigest()[:12]  # Первые 12 символов

    def export_to_network(self) -> Dict:
        """
        Экспортирует знания проекта в сеть (симуляция)

        Формат: MEP (Methodology Exchange Protocol) v7.0
        """
        print("🌐 Экспорт знаний в коллективную сеть...")

        # Загрузка knowledge_export.json
        knowledge_file = self.project_root / "knowledge_export.json"
        if not knowledge_file.exists():
            print("⚠️  knowledge_export.json не найден. Запустите knowledge_extractor.py")
            return {}

        with open(knowledge_file, 'r', encoding='utf-8') as f:
            knowledge = json.load(f)

        # Формирование MEP-совместимого экспорта
        mep_export = {
            "protocol_version": "7.0",
            "project_id": self.project_id,
            "timestamp": datetime.now().isoformat(),
            "project_type": knowledge['metadata']['project_type'],
            "project_size": knowledge['metadata'].get('project_size', 'large'),
            "project_maturity": knowledge['metadata'].get('project_maturity', 'mature'),
            "metrics": knowledge['current_state'],
            "trends": knowledge.get('trends', {}),
            "improvements": knowledge.get('improvements', []),
            "lessons": knowledge.get('lessons', []),
            "privacy": {
                "anonymized": True,
                "opt_in": self.opt_in,
                "data_retention_days": 365
            }
        }

        # Сохранение в сеть (локально)
        with open(self.export_file, 'w', encoding='utf-8') as f:
            json.dump(mep_export, f, indent=2, ensure_ascii=False)

        print(f"✅ Экспорт завершён: {self.export_file}")
        print(f"   Project ID: {self.project_id}")
        print(f"   Opt-in: {self.opt_in}")
        print(f"   Lessons: {len(mep_export.get('lessons', []))}")
        print(f"   Improvements: {len(mep_export.get('improvements', []))}")

        return mep_export

    def simulate_network(self, num_projects: int = 3):
        """
        Симулирует сеть из нескольких проектов для демонстрации

        Создает несколько виртуальных проектов с разными характеристиками
        """
        print(f"\n🔬 Симуляция коллективной сети ({num_projects} проектов)...")

        # Шаблоны для разных типов проектов
        project_templates = [
            {
                "name": "library-project",
                "type": "library",
                "size": "medium",
                "maturity": "mature",
                "metrics": {"cd": 12.3, "vt": 65.0, "cr": 0.7, "db": 18.5,
                           "total_docs": 45, "total_connections": 250},
                "lessons": [
                    {
                        "id": "lesson_high_vt",
                        "title": "Высокая VT критична для библиотек",
                        "principle": "API должен явно прослеживаться до реализации",
                        "confidence": 0.92
                    }
                ]
            },
            {
                "name": "webapp-project",
                "type": "webapp",
                "size": "large",
                "maturity": "developing",
                "metrics": {"cd": 18.9, "vt": 42.0, "cr": 1.8, "db": 25.0,
                           "total_docs": 89, "total_connections": 890},
                "lessons": [
                    {
                        "id": "lesson_fast_cr",
                        "title": "Высокий CR в молодых проектах нормален",
                        "principle": "Активное развитие = высокая скорость изменений",
                        "confidence": 0.88
                    }
                ]
            },
            {
                "name": "datascience-project",
                "type": "datascience",
                "size": "small",
                "maturity": "early",
                "metrics": {"cd": 7.5, "vt": 35.0, "cr": 2.1, "db": 38.0,
                           "total_docs": 28, "total_connections": 95},
                "lessons": [
                    {
                        "id": "lesson_low_cd_ok",
                        "title": "Низкая CD допустима для экспериментов",
                        "principle": "Notebooks часто изолированы - это нормально",
                        "confidence": 0.85
                    }
                ]
            }
        ]

        # Создание симулированных проектов
        for i, template in enumerate(project_templates[:num_projects]):
            project_id = hashlib.sha256(template['name'].encode()).hexdigest()[:12]

            simulated_export = {
                "protocol_version": "7.0",
                "project_id": project_id,
                "timestamp": datetime.now().isoformat(),
                "project_type": template['type'],
                "project_size": template['size'],
                "project_maturity": template['maturity'],
                "metrics": template['metrics'],
                "lessons": template['lessons'],
                "privacy": {
                    "anonymized": True,
                    "opt_in": True,
                    "simulated": True
                }
            }

            # Сохранение
            sim_file = self.network_dir / f"export_{project_id}.json"
            with open(sim_file, 'w', encoding='utf-8') as f:
                json.dump(simulated_export, f, indent=2, ensure_ascii=False)

            print(f"  📦 Создан: {template['name']} ({template['type']})")

        print(f"\n✅ Сеть из {num_projects} проектов создана")

    def analyze_collective_knowledge(self) -> Dict:
        """
        Анализирует коллективные знания из сети

        Returns: Агрегированная статистика и паттерны
        """
        print("\n📊 Анализ коллективных знаний...")

        # Загрузка всех экспортов из сети
        exports = []
        for export_file in self.network_dir.glob("export_*.json"):
            with open(export_file, 'r', encoding='utf-8') as f:
                exports.append(json.load(f))

        if not exports:
            print("⚠️  Нет данных в сети")
            return {}

        # Агрегация по типам проектов
        by_type = {}
        for exp in exports:
            proj_type = exp['project_type']
            if proj_type not in by_type:
                by_type[proj_type] = []
            by_type[proj_type].append(exp)

        # Статистика
        collective_stats = {
            "total_projects": len(exports),
            "project_types": list(by_type.keys()),
            "aggregated_metrics": {},
            "collective_lessons": [],
            "recommendations": []
        }

        # Агрегация метрик по типам
        for proj_type, projects in by_type.items():
            metrics_list = [p['metrics'] for p in projects if 'metrics' in p]

            if metrics_list:
                avg_metrics = {}
                for metric in ['cd', 'vt', 'cr', 'db']:
                    values = [m[metric] for m in metrics_list if metric in m]
                    if values:
                        avg_metrics[metric] = round(sum(values) / len(values), 2)

                collective_stats['aggregated_metrics'][proj_type] = avg_metrics

        # Сбор всех уроков
        all_lessons = []
        for exp in exports:
            if 'lessons' in exp:
                for lesson in exp['lessons']:
                    lesson_with_source = lesson.copy()
                    lesson_with_source['source_project_type'] = exp['project_type']
                    all_lessons.append(lesson_with_source)

        collective_stats['collective_lessons'] = all_lessons

        print(f"  ✓ Проанализировано проектов: {len(exports)}")
        print(f"  ✓ Типов проектов: {len(by_type)}")
        print(f"  ✓ Извлечено уроков: {len(all_lessons)}")

        return collective_stats

    def generate_recommendations(self) -> List[Dict]:
        """
        Генерирует рекомендации для текущего проекта на основе
        коллективного опыта
        """
        print("\n💡 Генерация рекомендаций на основе коллективного опыта...")

        collective = self.analyze_collective_knowledge()

        if not collective:
            return []

        # Загрузка своих метрик
        knowledge_file = self.project_root / "knowledge_export.json"
        if not knowledge_file.exists():
            return []

        with open(knowledge_file, 'r', encoding='utf-8') as f:
            my_knowledge = json.load(f)

        my_type = my_knowledge['metadata']['project_type']
        my_metrics = my_knowledge['current_state']

        recommendations = []

        # Рекомендация 1: Сравнение с проектами того же типа
        if my_type in collective['aggregated_metrics']:
            avg_metrics = collective['aggregated_metrics'][my_type]

            for metric, avg_value in avg_metrics.items():
                my_value = my_metrics.get(metric)
                if my_value is not None:
                    diff = my_value - avg_value
                    diff_pct = (diff / avg_value * 100) if avg_value != 0 else 0

                    if abs(diff_pct) > 20:  # Значимое отличие
                        recommendations.append({
                            "type": "comparison",
                            "metric": metric.upper(),
                            "my_value": my_value,
                            "collective_avg": avg_value,
                            "difference": round(diff, 2),
                            "difference_pct": round(diff_pct, 1),
                            "severity": "high" if abs(diff_pct) > 50 else "medium",
                            "message": f"Ваш {metric.upper()} ({my_value}) отличается от среднего {my_type} проектов ({avg_value}) на {diff_pct:+.1f}%"
                        })

        # Рекомендация 2: Релевантные уроки из других проектов
        relevant_lessons = []
        for lesson in collective.get('collective_lessons', []):
            # Уроки с высокой уверенностью (>85%)
            if lesson.get('confidence', 0) > 0.85:
                relevant_lessons.append({
                    "type": "collective_lesson",
                    "title": lesson.get('title'),
                    "principle": lesson.get('principle'),
                    "confidence": lesson.get('confidence'),
                    "source_type": lesson.get('source_project_type'),
                    "message": f"Урок от {lesson.get('source_project_type')} проектов: {lesson.get('principle')}"
                })

        recommendations.extend(relevant_lessons[:3])  # Топ-3 урока

        # Сохранение рекомендаций
        with open(self.recommendations_file, 'w', encoding='utf-8') as f:
            json.dump({
                "generated_at": datetime.now().isoformat(),
                "total_recommendations": len(recommendations),
                "recommendations": recommendations
            }, f, indent=2, ensure_ascii=False)

        print(f"  ✓ Сгенерировано рекомендаций: {len(recommendations)}")
        print(f"  ✓ Сохранено в: {self.recommendations_file}")

        return recommendations

    def display_recommendations(self, recommendations: List[Dict]):
        """Отображает рекомендации в человекочитаемом формате"""
        if not recommendations:
            print("\n✅ Нет рекомендаций — проект в отличном состоянии!")
            return

        print("\n" + "="*70)
        print("РЕКОМЕНДАЦИИ ИЗ КОЛЛЕКТИВНОГО ОПЫТА")
        print("="*70)

        for i, rec in enumerate(recommendations, 1):
            print(f"\n{i}. ", end="")

            if rec['type'] == 'comparison':
                severity_emoji = "🔴" if rec['severity'] == 'high' else "🟡"
                print(f"{severity_emoji} СРАВНЕНИЕ С КОЛЛЕКТИВОМ ({rec['metric']})")
                print(f"   Ваше значение: {rec['my_value']}")
                print(f"   Среднее по сети: {rec['collective_avg']}")
                print(f"   Отличие: {rec['difference']:+.2f} ({rec['difference_pct']:+.1f}%)")
                print(f"   💬 {rec['message']}")

            elif rec['type'] == 'collective_lesson':
                print(f"📚 УРОК ОТ СООБЩЕСТВА ({rec['source_type']})")
                print(f"   Тема: {rec['title']}")
                print(f"   Принцип: {rec['principle']}")
                print(f"   Уверенность: {rec['confidence']*100:.0f}%")

        print("\n" + "="*70)
        print(f"Всего рекомендаций: {len(recommendations)}")
        print("="*70 + "\n")

    def run_full_cycle(self):
        """Запускает полный цикл работы с коллективным интеллектом"""
        print("="*70)
        print("КОЛЛЕКТИВНЫЙ ИНТЕЛЛЕКТ — ПОЛНЫЙ ЦИКЛ")
        print("ЭТАП 7: Обмен знаниями между проектами")
        print("="*70)

        # 1. Экспорт своих знаний
        self.export_to_network()

        # 2. Симуляция сети (если еще нет)
        existing_exports = list(self.network_dir.glob("export_*.json"))
        if len(existing_exports) < 3:
            self.simulate_network(3)

        # 3. Анализ коллективных знаний
        collective = self.analyze_collective_knowledge()

        # 4. Генерация рекомендаций
        recommendations = self.generate_recommendations()

        # 5. Отображение
        self.display_recommendations(recommendations)

        print("\n✅ Полный цикл завершён")
        print(f"📁 Данные сети: {self.network_dir}")
        print(f"📄 Рекомендации: {self.recommendations_file}")
        print("\nМетодология ⇑⇓↔ учится коллективно! 🌐")


def main():
    """Главная функция"""
    ci = CollectiveIntelligence('.', opt_in=True)
    ci.run_full_cycle()
    return 0


if __name__ == "__main__":
    exit(main())
