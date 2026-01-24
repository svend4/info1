#!/usr/bin/env python3
"""
Self-Improvement System (ЭТАП 6: Самосовершенствование)

Анализирует текущее состояние проекта и автоматически предлагает
конкретные улучшения на основе метрик здоровья.

Ключевые функции:
1. Диагностика проблем метрик (CD, VT, CR, DB)
2. Генерация конкретных рекомендаций
3. Приоритизация действий
4. Автоматическое создание плана улучшений

Уровень абстракции: α=-4 (исполняемый код)
Статус: ⇑ ВВЕРХ (инструмент для улучшения методологии)

Вертикальные связи (⇑ к философии и концепциям):
    ⇑ ЭТАП-6-САМОСОВЕРШЕНСТВОВАНИЕ.md (α=+2) — концептуальное обоснование самосовершенствования
    ⇑ ЭВОЛЮЦИЯ-МЕТОДОЛОГИИ.md (α=+2) — контекст эволюции методологии до ЭТАПА 6
    ⇑ МЕТОДОЛОГИЯ-ПАРАЛЛЕЛЬНОГО-РАЗВИТИЯ.md (α=+1) — методология ⇑⇓↔, которую реализует этот инструмент
    ⇑ ФИЛОСОФИЯ-ПРОЕКТА.md (α=+3) — философские принципы (адаптация, телеология)
    ⇑ МЕТРИКИ-ЗДОРОВЬЯ.md (α=+1) — определения метрик CD, VT, CR, DB

Горизонтальные связи (↔ другие инструменты α=-4):
    ↔ health_metrics.py — источник метрик для анализа
    ↔ predictive_warnings.py — дополняет диагностику предсказанием
    ↔ adaptive_metrics.py — адаптирует пороги метрик под проект
"""

import json
import os
import re
from datetime import datetime
from typing import Dict, List, Tuple
from pathlib import Path


class SelfImprovementAnalyzer:
    """Анализатор для автоматического улучшения проекта"""

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.metrics = {}
        self.recommendations = []
        self.priority_actions = []

    def load_current_metrics(self) -> Dict:
        """Загрузка текущих метрик из health_metrics.py"""
        # Запускаем health_metrics.py и парсим вывод
        import subprocess

        try:
            result = subprocess.run(
                ["python3", str(self.project_root / "tools" / "health_metrics.py")],
                capture_output=True,
                text=True,
                timeout=30
            )

            output = result.stdout

            # Парсим метрики из вывода (с учетом переносов строк)
            metrics = {}

            # CD
            cd_match = re.search(r'CD.*?Value:\s+([\d.]+)%', output, re.DOTALL)
            if cd_match:
                metrics['cd'] = float(cd_match.group(1))

            # VT
            vt_match = re.search(r'VT.*?Value:\s+([\d.]+)%', output, re.DOTALL)
            if vt_match:
                metrics['vt'] = float(vt_match.group(1))

            # CR
            cr_match = re.search(r'CR.*?Value:\s+([\d.]+)', output, re.DOTALL)
            if cr_match:
                metrics['cr'] = float(cr_match.group(1))

            # DB
            db_match = re.search(r'DB.*?Value:\s+([\d.]+)%', output, re.DOTALL)
            if db_match:
                metrics['db'] = float(db_match.group(1))

            # Метаданные
            docs_match = re.search(r'Total documents:\s+(\d+)', output)
            if docs_match:
                metrics['total_docs'] = int(docs_match.group(1))

            conn_match = re.search(r'Total connections:\s+(\d+)', output)
            if conn_match:
                metrics['total_connections'] = int(conn_match.group(1))

            cycles_match = re.search(r'Total cycles:\s+(\d+)', output)
            if cycles_match:
                metrics['total_cycles'] = int(cycles_match.group(1))

            self.metrics = metrics
            return metrics

        except Exception as e:
            print(f"⚠️  Ошибка при загрузке метрик: {e}")
            return {}

    def diagnose_cd_problem(self):
        """Диагностика проблемы Connectivity Density"""
        cd = self.metrics.get('cd', 0)
        target_min, target_max = 10.0, 20.0

        if cd < target_min:
            severity = "⚠️  НИЗКАЯ"
            problem = f"CD = {cd:.1f}% (ниже целевого {target_min}%)"
            explanation = """
Проблема: Недостаточная связность документов.

Причины:
- Документы изолированы друг от друга
- Секции "См. также" отсутствуют или неполные
- Горизонтальные (↔) связи слабые

Последствия:
- Сложно навигироваться по проекту
- Теряется контекст между документами
- Снижается понимание целостности системы
"""
            recommendations = [
                {
                    'priority': 'HIGH',
                    'action': 'Добавить секции "См. также" к документам без них',
                    'estimated_impact': f'+{target_min - cd:.1f}% к CD',
                    'steps': [
                        'Найти документы без секций "См. также"',
                        'Добавить минимум 5-10 связей к каждому документу',
                        'Сфокусироваться на горизонтальных (↔) связях'
                    ]
                },
                {
                    'priority': 'MEDIUM',
                    'action': 'Создать индексные документы',
                    'estimated_impact': f'+{(target_min - cd) * 0.3:.1f}% к CD',
                    'steps': [
                        'Создать ИНДЕКС-ДОКУМЕНТОВ.md',
                        'Создать тематические индексы (по функциональности)',
                        'Связать индексы с конкретными документами'
                    ]
                }
            ]

        elif cd > target_max:
            severity = "⚠️  ВЫСОКАЯ"
            problem = f"CD = {cd:.1f}% (выше целевого {target_max}%)"
            explanation = """
Проблема: Избыточная связность документов.

Причины:
- Слишком много связей в секциях "См. также"
- Дублирующие связи
- Связи к нерелевантным документам
- Автоматически добавленные связи не прошли ревью

Последствия:
- Информационная перегрузка
- Сложно определить действительно важные связи
- Снижается полезность навигации
- Увеличивается когнитивная нагрузка
"""
            excess = cd - target_max
            total_connections = self.metrics.get('total_connections', 0)
            total_docs = self.metrics.get('total_docs', 1)

            # Рассчитываем, сколько связей нужно удалить
            max_possible = total_docs * (total_docs - 1)
            current_connections = int((cd / 100) * max_possible)
            target_connections = int((target_max / 100) * max_possible)
            connections_to_remove = current_connections - target_connections

            recommendations = [
                {
                    'priority': 'HIGH',
                    'action': f'Удалить ~{connections_to_remove} избыточных связей',
                    'estimated_impact': f'-{excess:.1f}% к CD (цель: {target_max}%)',
                    'steps': [
                        'Проверить все секции "См. также" на релевантность',
                        'Удалить дублирующие связи',
                        'Удалить связи к слабо связанным документам',
                        'Оставить только 5-10 наиболее важных связей на документ',
                        'Приоритет: оставить вертикальные (⇑⇓) связи, сократить горизонтальные (↔)'
                    ]
                },
                {
                    'priority': 'MEDIUM',
                    'action': 'Ввести правило максимального количества связей',
                    'estimated_impact': 'Предотвращение будущих проблем',
                    'steps': [
                        'Установить лимит: максимум 15 связей на документ',
                        'Обновить ПРИМЕНЕНИЕ-МЕТОДОЛОГИИ.md с этим правилом',
                        'Добавить проверку в health_metrics.py'
                    ]
                },
                {
                    'priority': 'LOW',
                    'action': 'Создать иерархию связей',
                    'estimated_impact': 'Улучшение качества связей',
                    'steps': [
                        'Разделить связи на "Основные" и "Дополнительные"',
                        'Показывать только основные связи по умолчанию',
                        'Дополнительные связи — в раскрывающейся секции'
                    ]
                }
            ]
        else:
            severity = "✅ НОРМА"
            problem = f"CD = {cd:.1f}% (в целевом диапазоне {target_min}-{target_max}%)"
            explanation = "Связность документов в оптимальном диапазоне."
            recommendations = []

        self.recommendations.append({
            'metric': 'CD (Connectivity Density)',
            'severity': severity,
            'problem': problem,
            'explanation': explanation,
            'recommendations': recommendations
        })

    def diagnose_vt_problem(self):
        """Диагностика проблемы Vertical Traceability"""
        vt = self.metrics.get('vt', 0)
        target_min, target_max = 50.0, 70.0

        if vt < target_min:
            severity = "⚠️  НИЗКАЯ"
            problem = f"VT = {vt:.1f}% (ниже целевого {target_min}%)"
            explanation = """
Проблема: Недостаточная вертикальная трассируемость.

Причины:
- Слабые связи между уровнями абстракции (α)
- Концептуальные документы (α=+2,+3,+4) не связаны с кодом (α=-3,-4)
- Отсутствуют промежуточные уровни (спецификации α=-1, шаблоны α=-2)

Последствия:
- Непонятно, как философия реализована в коде
- Сложно проследить путь от требований до реализации
- Разрывы между "что делаем" и "как делаем"
"""
            gap = target_min - vt

            recommendations = [
                {
                    'priority': 'HIGH',
                    'action': 'Усилить вертикальные (⇑⇓) связи',
                    'estimated_impact': f'+{gap * 0.6:.1f}% к VT',
                    'steps': [
                        'Найти документы высокого уровня (α=+2,+3,+4)',
                        'Добавить явные ссылки вниз (⇓) к реализации',
                        'Найти код (α=-3,-4) и добавить ссылки вверх (⇑) к концепциям',
                        'Создать документы промежуточных уровней (α=-1, α=-2)',
                        'Цель: каждый уровень α должен ссылаться на α±1'
                    ]
                },
                {
                    'priority': 'MEDIUM',
                    'action': 'Создать КАРТУ ВЕРТИКАЛЬНОЙ ТРАССИРУЕМОСТИ',
                    'estimated_impact': f'+{gap * 0.3:.1f}% к VT',
                    'steps': [
                        'Создать ВЕРТИКАЛЬНАЯ-ТРАССИРУЕМОСТЬ.md',
                        'Визуализировать путь от ОНТОЛОГИЯ (α=+4) до КОД (α=-4)',
                        'Для каждой ключевой концепции показать реализацию',
                        'Пример: ФИЛОСОФИЯ-ПРОЕКТА.md → МЕТОДОЛОГИЯ.md → QUICKSTART.md → seed_data.py'
                    ]
                },
                {
                    'priority': 'LOW',
                    'action': 'Добавить маркеры уровня абстракции в код',
                    'estimated_impact': f'+{gap * 0.1:.1f}% к VT',
                    'steps': [
                        'В комментариях к коду указать уровень α',
                        'Пример: # α=-4: Реализация концепции "достоинство" из ФИЛОСОФИЯ-ПРОЕКТА.md',
                        'Добавить ссылки на концептуальные документы'
                    ]
                }
            ]

        elif vt > target_max:
            severity = "⚠️  ВЫСОКАЯ"
            problem = f"VT = {vt:.1f}% (выше целевого {target_max}%)"
            explanation = """
Проблема: Избыточная вертикальная трассируемость.

Причины:
- Слишком много уровней абстракции
- Дублирующие документы на разных уровнях
- Избыточные связи между уровнями

Последствия:
- Перегрузка навигации
- Сложность в различении уровней
"""
            recommendations = [
                {
                    'priority': 'MEDIUM',
                    'action': 'Упростить иерархию уровней',
                    'estimated_impact': f'-{vt - target_max:.1f}% к VT',
                    'steps': [
                        'Объединить похожие документы на разных уровнях',
                        'Удалить избыточные промежуточные уровни'
                    ]
                }
            ]
        else:
            severity = "✅ НОРМА"
            problem = f"VT = {vt:.1f}% (в целевом диапазоне {target_min}-{target_max}%)"
            explanation = "Вертикальная трассируемость в оптимальном диапазоне."
            recommendations = []

        self.recommendations.append({
            'metric': 'VT (Vertical Traceability)',
            'severity': severity,
            'problem': problem,
            'explanation': explanation,
            'recommendations': recommendations
        })

    def diagnose_cr_problem(self):
        """Диагностика проблемы Convergence Rate"""
        cr = self.metrics.get('cr', 0)
        target_min, target_max = 0.7, 1.5

        if target_min <= cr <= target_max:
            severity = "✅ НОРМА"
            problem = f"CR = {cr:.2f} (в целевом диапазоне {target_min}-{target_max})"
            explanation = "Скорость развития проекта оптимальна."
            recommendations = []
        elif cr < target_min:
            severity = "⚠️  НИЗКАЯ"
            problem = f"CR = {cr:.2f} (ниже {target_min})"
            explanation = """
Проблема: Проект развивается слишком медленно.

Причины:
- Мало новых документов создается
- Мало новых связей добавляется
- Проект стагнирует

Рекомендация: Возможно, проект достиг зрелости и это нормально.
"""
            recommendations = [
                {
                    'priority': 'LOW',
                    'action': 'Оценить необходимость дальнейшего развития',
                    'estimated_impact': 'Стратегическое решение',
                    'steps': [
                        'Проверить, все ли функции реализованы',
                        'Если проект завершен — это нормально',
                        'Если нет — добавить новые фичи'
                    ]
                }
            ]
        else:  # cr > target_max
            severity = "⚠️  ВЫСОКАЯ"
            problem = f"CR = {cr:.2f} (выше {target_max})"
            explanation = """
Проблема: Проект развивается слишком быстро.

Причины:
- Много новых документов, но недостаточно связей
- Качество может страдать из-за скорости
- Отсутствие консолидации

Рекомендация: Замедлиться и улучшить качество существующего.
"""
            recommendations = [
                {
                    'priority': 'MEDIUM',
                    'action': 'Консолидировать существующую документацию',
                    'estimated_impact': f'Снижение CR до {target_max}',
                    'steps': [
                        'Не создавать новые документы 1-2 цикла',
                        'Улучшить существующие документы',
                        'Добавить связи между документами',
                        'Провести рефакторинг документации'
                    ]
                }
            ]

        self.recommendations.append({
            'metric': 'CR (Convergence Rate)',
            'severity': severity,
            'problem': problem,
            'explanation': explanation,
            'recommendations': recommendations
        })

    def diagnose_db_problem(self):
        """Диагностика проблемы Directional Balance"""
        db = self.metrics.get('db', 0)
        target_max = 30.0

        if db > target_max:
            severity = "❌ КРИТИЧНО" if db > 100 else "⚠️  ВЫСОКАЯ"
            problem = f"DB = {db:.1f}% (намного выше целевого <{target_max}%)"
            explanation = """
Проблема: КРИТИЧЕСКИЙ дисбаланс направлений развития.

Причины:
- Неравномерное использование операторов ⇑⇓↔
- Один оператор доминирует (обычно ⇑ или ↔)
- Отсутствует баланс между обобщением, детализацией и связыванием

Последствия:
- Проект становится однобоким
- Теряется преимущество трёхмерного развития
- Снижается общее качество архитектуры
- ВЫСОКИЙ ПРИОРИТЕТ ИСПРАВЛЕНИЯ!
"""

            # Оценка, какого направления не хватает
            if db > 100:
                missing_direction = """
КРИТИЧЕСКАЯ СИТУАЦИЯ: DB > 100%

Вероятная причина: Один из операторов практически не используется.

Наиболее вероятные сценарии:
1. Мало горизонтальных (↔) связей — документы изолированы по уровням
2. Мало вертикальных вниз (⇓) связей — нет детализации от концепций к коду
3. Мало вертикальных вверх (⇑) связей — нет обобщения от кода к концепциям
"""
            else:
                missing_direction = "Требуется балансировка всех трёх направлений."

            recommendations = [
                {
                    'priority': 'CRITICAL',
                    'action': 'СРОЧНО: Сбалансировать направления ⇑⇓↔',
                    'estimated_impact': f'-{db - target_max:.1f}% к DB (цель: <{target_max}%)',
                    'steps': [
                        'НЕМЕДЛЕННО провести анализ использования операторов',
                        'Определить недостающее направление (⇑, ⇓ или ↔)',
                        'Провести ЦИКЛ БАЛАНСИРОВКИ:',
                        '  - Если не хватает ⇑: добавить обобщающие документы',
                        '  - Если не хватает ⇓: добавить детализирующие документы',
                        '  - Если не хватает ↔: добавить горизонтальные связи',
                        'Цель: каждый оператор должен использоваться ~33% времени',
                        'Проверить метрики после каждого добавления'
                    ]
                },
                {
                    'priority': 'HIGH',
                    'action': 'Создать ПЛАН БАЛАНСИРОВКИ',
                    'estimated_impact': 'Системный подход к решению',
                    'steps': [
                        'Создать ПЛАН-БАЛАНСИРОВКИ-НАПРАВЛЕНИЙ.md',
                        'Расписать конкретные действия на 3-5 циклов',
                        'Определить метрики успеха (DB < 30%)',
                        'Назначить ответственного за мониторинг'
                    ]
                },
                {
                    'priority': 'MEDIUM',
                    'action': 'Установить автоматические предупреждения',
                    'estimated_impact': 'Предотвращение будущих проблем',
                    'steps': [
                        'Обновить health_metrics.py',
                        'Добавить критическое предупреждение при DB > 50%',
                        'Добавить блокировку коммитов при DB > 100%',
                        'Интегрировать в CI/CD'
                    ]
                }
            ]

            recommendations[0]['additional_context'] = missing_direction

        else:
            severity = "✅ НОРМА"
            problem = f"DB = {db:.1f}% (ниже целевого <{target_max}%)"
            explanation = "Баланс направлений развития в допустимом диапазоне."
            recommendations = []

        self.recommendations.append({
            'metric': 'DB (Directional Balance)',
            'severity': severity,
            'problem': problem,
            'explanation': explanation,
            'recommendations': recommendations
        })

    def prioritize_actions(self):
        """Приоритизация всех рекомендаций"""
        all_actions = []

        for rec_group in self.recommendations:
            metric = rec_group['metric']
            for rec in rec_group.get('recommendations', []):
                all_actions.append({
                    'metric': metric,
                    'priority': rec['priority'],
                    'action': rec['action'],
                    'estimated_impact': rec['estimated_impact'],
                    'steps': rec['steps']
                })

        # Сортировка по приоритету
        priority_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
        all_actions.sort(key=lambda x: priority_order.get(x['priority'], 4))

        self.priority_actions = all_actions
        return all_actions

    def generate_report(self) -> str:
        """Генерация детального отчёта"""
        report = []
        report.append("=" * 70)
        report.append("ОТЧЁТ СИСТЕМЫ САМОСОВЕРШЕНСТВОВАНИЯ")
        report.append("ЭТАП 6: Автоматический анализ и рекомендации")
        report.append("=" * 70)
        report.append("")
        report.append(f"Дата анализа: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")

        # Текущие метрики
        report.append("ТЕКУЩИЕ МЕТРИКИ:")
        report.append("-" * 70)
        report.append(f"  Документов: {self.metrics.get('total_docs', 'N/A')}")
        report.append(f"  Связей: {self.metrics.get('total_connections', 'N/A')}")
        report.append(f"  Циклов: {self.metrics.get('total_cycles', 'N/A')}")
        report.append(f"  CD: {self.metrics.get('cd', 'N/A')}%")
        report.append(f"  VT: {self.metrics.get('vt', 'N/A')}%")
        report.append(f"  CR: {self.metrics.get('cr', 'N/A')}")
        report.append(f"  DB: {self.metrics.get('db', 'N/A')}%")
        report.append("")

        # Диагностика
        report.append("ДИАГНОСТИКА ПРОБЛЕМ:")
        report.append("=" * 70)

        for i, rec_group in enumerate(self.recommendations, 1):
            report.append("")
            report.append(f"{i}. {rec_group['metric']}")
            report.append(f"   Статус: {rec_group['severity']}")
            report.append(f"   {rec_group['problem']}")
            report.append("")
            report.append("   Объяснение:")
            for line in rec_group['explanation'].strip().split('\n'):
                report.append(f"   {line}")

            if rec_group.get('recommendations'):
                report.append("")
                report.append("   Рекомендации:")
                for j, rec in enumerate(rec_group['recommendations'], 1):
                    report.append(f"   {i}.{j} [{rec['priority']}] {rec['action']}")
                    report.append(f"       Ожидаемый эффект: {rec['estimated_impact']}")
                    report.append(f"       Шаги:")
                    for step in rec['steps']:
                        report.append(f"         • {step}")

                    if 'additional_context' in rec:
                        report.append(f"       Дополнительный контекст:")
                        for line in rec['additional_context'].strip().split('\n'):
                            report.append(f"         {line}")
                    report.append("")

        # План действий
        report.append("")
        report.append("=" * 70)
        report.append("ПРИОРИТИЗИРОВАННЫЙ ПЛАН ДЕЙСТВИЙ")
        report.append("=" * 70)

        for i, action in enumerate(self.priority_actions, 1):
            report.append("")
            report.append(f"{i}. [{action['priority']}] {action['action']}")
            report.append(f"   Метрика: {action['metric']}")
            report.append(f"   Эффект: {action['estimated_impact']}")
            report.append(f"   Действия:")
            for step in action['steps']:
                report.append(f"     • {step}")

        report.append("")
        report.append("=" * 70)
        report.append("СЛЕДУЮЩИЕ ШАГИ:")
        report.append("=" * 70)
        report.append("")

        if self.priority_actions:
            report.append(f"1. Начните с действия с приоритетом CRITICAL или HIGH")
            report.append(f"2. Выполните рекомендованные шаги")
            report.append(f"3. Запустите health_metrics.py для проверки прогресса")
            report.append(f"4. Повторите анализ с помощью self_improvement.py")
            report.append(f"5. Продолжайте до достижения целевых значений метрик")
        else:
            report.append("✅ Все метрики в норме! Проект находится в здоровом состоянии.")
            report.append("   Продолжайте поддерживать текущий уровень качества.")

        report.append("")
        report.append("=" * 70)
        report.append("Конец отчёта. Методология продолжает самосовершенствоваться. ⇑⇓↔")
        report.append("=" * 70)

        return "\n".join(report)

    def save_report(self, filename: str = "self_improvement_report.txt"):
        """Сохранение отчёта в файл"""
        report = self.generate_report()
        output_path = self.project_root / filename

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)

        print(f"📄 Отчёт сохранён: {output_path}")
        return output_path

    def run_analysis(self):
        """Запуск полного анализа"""
        print("🔍 Запуск системы самосовершенствования...")
        print()

        # Загрузка метрик
        print("📊 Загрузка текущих метрик...")
        self.load_current_metrics()
        print(f"   ✓ Загружено: {len(self.metrics)} метрик")
        print()

        # Диагностика
        print("🔬 Диагностика проблем...")
        self.diagnose_cd_problem()
        self.diagnose_vt_problem()
        self.diagnose_cr_problem()
        self.diagnose_db_problem()
        print(f"   ✓ Проанализировано: 4 метрики")
        print()

        # Приоритизация
        print("📋 Приоритизация рекомендаций...")
        self.prioritize_actions()
        print(f"   ✓ Создано действий: {len(self.priority_actions)}")
        print()

        # Генерация отчёта
        print("📝 Генерация отчёта...")
        report = self.generate_report()
        print()
        print(report)
        print()

        # Сохранение отчёта
        self.save_report()

        return self.recommendations, self.priority_actions


def main():
    """Главная функция"""
    analyzer = SelfImprovementAnalyzer()
    recommendations, actions = analyzer.run_analysis()

    return 0 if not actions else 1  # 0 = все ОК, 1 = есть проблемы


if __name__ == "__main__":
    exit(main())
