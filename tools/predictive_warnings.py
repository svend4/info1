#!/usr/bin/env python3
"""
Predictive Warnings System (ЭТАП 6: Самосовершенствование)

Предсказывает будущие проблемы проекта на основе анализа трендов метрик.

Ключевые функции:
1. Анализ исторических данных метрик
2. Построение трендов (линейная регрессия)
3. Прогнозирование значений на N циклов вперёд
4. Генерация упреждающих предупреждений
5. Рекомендации по предотвращению проблем

Уровень абстракции: α=-4 (исполняемый код)
Статус: ⇑ ВВЕРХ (инструмент для улучшения методологии)

Вертикальные связи (⇑ к философии и концепциям):
    ⇑ ЭТАП-6-САМОСОВЕРШЕНСТВОВАНИЕ.md (α=+2) — переход от реактивного к проактивному управлению
    ⇑ ФИЛОСОФИЯ-ПРОЕКТА.md (α=+3) — принципы адаптации и предвидения
    ⇑ МЕТРИКИ-ЗДОРОВЬЯ.md (α=+1) — определения метрик CD, VT, CR, DB
    ⇑ БУДУЩЕЕ-МЕТОДОЛОГИИ.md (α=+3) — видение предиктивной аналитики в ЭТАПЕ 6

Горизонтальные связи (↔ другие инструменты α=-4):
    ↔ health_metrics.py — источник текущих метрик
    ↔ save_metrics.py — источник исторических данных
    ↔ self_improvement.py — дополняет упреждающие рекомендации
"""

import json
import os
import re
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from pathlib import Path
import subprocess


class MetricTrendAnalyzer:
    """Анализатор трендов метрик для предсказания проблем"""

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.history = []
        self.predictions = {}
        self.warnings = []

    def load_metrics_history(self) -> List[Dict]:
        """
        Загружает историю метрик из различных источников.

        В идеале метрики должны сохраняться в JSON файл при каждом запуске.
        Пока используем текущие метрики как единственную точку данных.
        """
        # Запускаем health_metrics.py для получения текущих метрик
        try:
            result = subprocess.run(
                ["python3", str(self.project_root / "tools" / "health_metrics.py")],
                capture_output=True,
                text=True,
                timeout=30
            )

            output = result.stdout

            # Парсим текущие метрики
            current_metrics = self._parse_metrics_output(output)

            # В реальной системе здесь был бы загрузка истории из файла
            # Пока создаём минимальную историю для демонстрации
            self.history = [current_metrics]

            return self.history

        except Exception as e:
            print(f"⚠️  Ошибка при загрузке истории метрик: {e}")
            return []

    def _parse_metrics_output(self, output: str) -> Dict:
        """Парсинг вывода health_metrics.py"""
        metrics = {'cycle': 1}  # По умолчанию цикл 1

        # CD
        cd_match = re.search(r'CD.*?Value:\s+([\d.]+)%', output)
        if cd_match:
            metrics['cd'] = float(cd_match.group(1))

        # VT
        vt_match = re.search(r'VT.*?Value:\s+([\d.]+)%', output)
        if vt_match:
            metrics['vt'] = float(vt_match.group(1))

        # CR
        cr_match = re.search(r'CR.*?Value:\s+([\d.]+)', output)
        if cr_match:
            metrics['cr'] = float(cr_match.group(1))

        # DB
        db_match = re.search(r'DB.*?Value:\s+([\d.]+)%', output)
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
            metrics['cycle'] = int(cycles_match.group(1))

        return metrics

    def predict_linear_trend(self, values: List[float], cycles_ahead: int = 3) -> List[float]:
        """
        Предсказывает тренд метрики используя линейную регрессию.

        Простая реализация без NumPy/SciPy для минимизации зависимостей.
        """
        if len(values) < 2:
            # Недостаточно данных для предсказания
            return [values[-1]] * cycles_ahead if values else [0] * cycles_ahead

        n = len(values)
        x = list(range(n))
        y = values

        # Вычисление коэффициентов линейной регрессии: y = a + b*x
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(x[i] * y[i] for i in range(n))
        sum_xx = sum(x[i] * x[i] for i in range(n))

        # Избегаем деления на ноль
        denominator = n * sum_xx - sum_x * sum_x
        if abs(denominator) < 0.0001:
            # Данные практически постоянны
            return [values[-1]] * cycles_ahead

        b = (n * sum_xy - sum_x * sum_y) / denominator
        a = (sum_y - b * sum_x) / n

        # Предсказание
        predictions = []
        for i in range(cycles_ahead):
            future_x = n + i
            predicted_y = a + b * future_x
            predictions.append(predicted_y)

        return predictions

    def analyze_metric_trend(
        self,
        metric_name: str,
        current_value: float,
        target_min: float,
        target_max: float,
        history_values: List[float],
        cycles_ahead: int = 3
    ) -> Dict:
        """
        Анализирует тренд конкретной метрики и генерирует предупреждения.
        """
        # Предсказание будущих значений
        if len(history_values) >= 2:
            predictions = self.predict_linear_trend(history_values, cycles_ahead)
        else:
            # Если истории нет, предполагаем постоянное значение
            predictions = [current_value] * cycles_ahead

        # Проверка, выйдет ли метрика за целевые диапазоны
        warnings = []
        for i, predicted in enumerate(predictions):
            cycle_num = len(history_values) + i + 1

            if predicted < target_min:
                warnings.append({
                    'cycle': cycle_num,
                    'predicted_value': predicted,
                    'problem': f'Метрика упадёт ниже {target_min}',
                    'severity': 'MEDIUM' if i >= 2 else 'HIGH'
                })
            elif predicted > target_max:
                warnings.append({
                    'cycle': cycle_num,
                    'predicted_value': predicted,
                    'problem': f'Метрика превысит {target_max}',
                    'severity': 'MEDIUM' if i >= 2 else 'HIGH'
                })

        trend_direction = self._determine_trend(history_values + predictions[:1])

        return {
            'metric': metric_name,
            'current_value': current_value,
            'predictions': predictions,
            'trend': trend_direction,
            'warnings': warnings,
            'action_required': len(warnings) > 0
        }

    def _determine_trend(self, values: List[float]) -> str:
        """Определяет направление тренда"""
        if len(values) < 2:
            return 'STABLE'

        # Сравниваем последние 2 значения
        diff = values[-1] - values[-2]

        if abs(diff) < 0.5:
            return 'STABLE'
        elif diff > 0:
            return 'INCREASING'
        else:
            return 'DECREASING'

    def generate_warnings(self) -> List[Dict]:
        """Генерирует все предупреждения на основе трендов метрик"""
        if not self.history:
            self.load_metrics_history()

        if not self.history:
            return []

        current = self.history[-1]
        all_warnings = []

        # Анализ CD (Connectivity Density)
        cd_history = [m.get('cd', 0) for m in self.history]
        cd_analysis = self.analyze_metric_trend(
            'CD (Connectivity Density)',
            current.get('cd', 0),
            target_min=10.0,
            target_max=20.0,
            history_values=cd_history,
            cycles_ahead=3
        )
        if cd_analysis['action_required']:
            all_warnings.extend(self._format_warnings(cd_analysis))

        # Анализ VT (Vertical Traceability)
        vt_history = [m.get('vt', 0) for m in self.history]
        vt_analysis = self.analyze_metric_trend(
            'VT (Vertical Traceability)',
            current.get('vt', 0),
            target_min=50.0,
            target_max=70.0,
            history_values=vt_history,
            cycles_ahead=3
        )
        if vt_analysis['action_required']:
            all_warnings.extend(self._format_warnings(vt_analysis))

        # Анализ CR (Convergence Rate)
        cr_history = [m.get('cr', 0) for m in self.history]
        cr_analysis = self.analyze_metric_trend(
            'CR (Convergence Rate)',
            current.get('cr', 0),
            target_min=0.7,
            target_max=1.5,
            history_values=cr_history,
            cycles_ahead=3
        )
        if cr_analysis['action_required']:
            all_warnings.extend(self._format_warnings(cr_analysis))

        # Анализ DB (Directional Balance)
        db_history = [m.get('db', 0) for m in self.history]
        db_analysis = self.analyze_metric_trend(
            'DB (Directional Balance)',
            current.get('db', 0),
            target_min=0.0,
            target_max=30.0,
            history_values=db_history,
            cycles_ahead=3
        )
        if db_analysis['action_required']:
            all_warnings.extend(self._format_warnings(db_analysis))

        self.warnings = all_warnings
        return all_warnings

    def _format_warnings(self, analysis: Dict) -> List[Dict]:
        """Форматирует предупреждения из анализа"""
        formatted = []
        metric = analysis['metric']

        for warning in analysis['warnings']:
            formatted.append({
                'metric': metric,
                'severity': warning['severity'],
                'cycle': warning['cycle'],
                'predicted_value': warning['predicted_value'],
                'problem': warning['problem'],
                'trend': analysis['trend'],
                'current_value': analysis['current_value']
            })

        return formatted

    def generate_preventive_recommendations(self) -> List[Dict]:
        """Генерирует рекомендации по предотвращению предсказанных проблем"""
        recommendations = []

        for warning in self.warnings:
            metric = warning['metric']
            severity = warning['severity']
            cycle = warning['cycle']
            problem = warning['problem']

            if 'CD' in metric:
                if 'упадёт ниже' in problem:
                    recommendations.append({
                        'priority': severity,
                        'metric': metric,
                        'action': 'Начать добавлять связи между документами СЕЙЧАС',
                        'reason': f'В CYCLE {cycle} CD упадёт слишком низко',
                        'steps': [
                            'Найти документы с малым количеством связей',
                            'Добавить секции "См. также"',
                            'Фокус на горизонтальных (↔) связях',
                            f'Цель: предотвратить падение в CYCLE {cycle}'
                        ]
                    })
                else:  # превысит
                    recommendations.append({
                        'priority': severity,
                        'metric': metric,
                        'action': 'Начать удаление избыточных связей СЕЙЧАС',
                        'reason': f'В CYCLE {cycle} CD станет слишком высоким',
                        'steps': [
                            'Проверить документы с большим количеством связей',
                            'Удалить дублирующие связи',
                            'Оставить только самые важные (5-10 на документ)',
                            f'Цель: предотвратить перегрузку в CYCLE {cycle}'
                        ]
                    })

            elif 'VT' in metric:
                if 'упадёт ниже' in problem:
                    recommendations.append({
                        'priority': severity,
                        'metric': metric,
                        'action': 'Усилить вертикальные связи (⇑⇓) СЕЙЧАС',
                        'reason': f'В CYCLE {cycle} VT упадёт слишком низко',
                        'steps': [
                            'Добавить связи между уровнями абстракции α',
                            'Связать философию (α=+3,+4) с кодом (α=-3,-4)',
                            'Создать промежуточные документы (α=-1, α=-2)',
                            f'Цель: предотвратить разрыв трассируемости в CYCLE {cycle}'
                        ]
                    })

            elif 'DB' in metric:
                if 'превысит' in problem:
                    recommendations.append({
                        'priority': 'HIGH',  # DB критичен
                        'metric': metric,
                        'action': 'СРОЧНО: Сбалансировать направления ⇑⇓↔',
                        'reason': f'В CYCLE {cycle} DB станет критически высоким',
                        'steps': [
                            'НЕМЕДЛЕННО определить недостающее направление',
                            'Провести цикл балансировки',
                            'Добавить документы недостающего типа',
                            'Проверять DB после каждого добавления',
                            f'Цель: предотвратить критический дисбаланс в CYCLE {cycle}'
                        ]
                    })

        # Сортировка по приоритету
        priority_order = {'HIGH': 0, 'MEDIUM': 1, 'LOW': 2}
        recommendations.sort(key=lambda x: priority_order.get(x['priority'], 3))

        return recommendations

    def generate_report(self) -> str:
        """Генерирует детальный отчёт о предсказаниях"""
        report = []
        report.append("=" * 70)
        report.append("ПРЕДИКТИВНЫЙ АНАЛИЗ — ПРОГНОЗ ПРОБЛЕМ")
        report.append("ЭТАП 6: Система упреждающих предупреждений")
        report.append("=" * 70)
        report.append("")
        report.append(f"Дата анализа: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Глубина прогноза: 3 цикла вперёд")
        report.append("")

        if not self.warnings:
            report.append("✅ ОТЛИЧНЫЕ НОВОСТИ!")
            report.append("")
            report.append("Предиктивный анализ не обнаружил потенциальных проблем")
            report.append("в ближайших 3 циклах развития проекта.")
            report.append("")
            report.append("Все метрики находятся в стабильном состоянии.")
            report.append("Продолжайте текущий курс развития.")
            report.append("")
        else:
            report.append("⚠️  ОБНАРУЖЕНЫ ПОТЕНЦИАЛЬНЫЕ ПРОБЛЕМЫ!")
            report.append("")
            report.append(f"Предсказано проблем: {len(self.warnings)}")
            report.append("")

            # Группировка по метрикам
            by_metric = {}
            for w in self.warnings:
                metric = w['metric']
                if metric not in by_metric:
                    by_metric[metric] = []
                by_metric[metric].append(w)

            for metric, warnings in by_metric.items():
                report.append("-" * 70)
                report.append(f"📊 {metric}")
                report.append("-" * 70)

                for w in warnings:
                    report.append("")
                    report.append(f"⚠️  [{w['severity']}] CYCLE {w['cycle']}")
                    report.append(f"   Текущее значение: {w['current_value']:.2f}")
                    report.append(f"   Прогноз: {w['predicted_value']:.2f}")
                    report.append(f"   Проблема: {w['problem']}")
                    report.append(f"   Тренд: {w['trend']}")

                report.append("")

        # Рекомендации по предотвращению
        recommendations = self.generate_preventive_recommendations()

        if recommendations:
            report.append("")
            report.append("=" * 70)
            report.append("УПРЕЖДАЮЩИЕ РЕКОМЕНДАЦИИ")
            report.append("=" * 70)
            report.append("")
            report.append("Действуйте СЕЙЧАС, чтобы предотвратить будущие проблемы:")
            report.append("")

            for i, rec in enumerate(recommendations, 1):
                report.append(f"{i}. [{rec['priority']}] {rec['action']}")
                report.append(f"   Метрика: {rec['metric']}")
                report.append(f"   Причина: {rec['reason']}")
                report.append(f"   Действия:")
                for step in rec['steps']:
                    report.append(f"     • {step}")
                report.append("")

        report.append("=" * 70)
        report.append("ФИЛОСОФИЯ ПРЕДИКТИВНОГО АНАЛИЗА")
        report.append("=" * 70)
        report.append("")
        report.append("Предсказание проблем — это не гадание на кофейной гуще.")
        report.append("Это научный анализ трендов, основанный на истории проекта.")
        report.append("")
        report.append("Действуя упреждающе, мы:")
        report.append("  • Предотвращаем проблемы ДО их возникновения")
        report.append("  • Экономим время на исправление кризисов")
        report.append("  • Поддерживаем здоровье проекта стабильным")
        report.append("")
        report.append("Это переход от РЕАКТИВНОГО к ПРОАКТИВНОМУ управлению.")
        report.append("")
        report.append("=" * 70)
        report.append("Конец отчёта. Методология предвидит будущее. ⇑⇓↔")
        report.append("=" * 70)

        return "\n".join(report)

    def save_report(self, filename: str = "predictive_warnings_report.txt"):
        """Сохранение отчёта в файл"""
        report = self.generate_report()
        output_path = self.project_root / filename

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)

        print(f"📄 Отчёт сохранён: {output_path}")
        return output_path

    def run_analysis(self):
        """Запуск полного предиктивного анализа"""
        print("🔮 Запуск предиктивного анализа...")
        print()

        # Загрузка истории
        print("📊 Загрузка истории метрик...")
        self.load_metrics_history()
        print(f"   ✓ Загружено: {len(self.history)} точек данных")
        print()

        # Генерация предупреждений
        print("⚠️  Генерация предупреждений...")
        warnings = self.generate_warnings()
        print(f"   ✓ Обнаружено потенциальных проблем: {len(warnings)}")
        print()

        # Генерация рекомендаций
        print("💡 Генерация упреждающих рекомендаций...")
        recommendations = self.generate_preventive_recommendations()
        print(f"   ✓ Создано рекомендаций: {len(recommendations)}")
        print()

        # Генерация отчёта
        print("📝 Генерация отчёта...")
        report = self.generate_report()
        print()
        print(report)
        print()

        # Сохранение отчёта
        self.save_report()

        return warnings, recommendations


def main():
    """Главная функция"""
    analyzer = MetricTrendAnalyzer()
    warnings, recommendations = analyzer.run_analysis()

    # Код возврата:
    # 0 = нет предупреждений
    # 1 = есть предупреждения MEDIUM
    # 2 = есть предупреждения HIGH
    if not warnings:
        return 0

    has_high = any(w['severity'] == 'HIGH' for w in warnings)
    return 2 if has_high else 1


if __name__ == "__main__":
    exit(main())
