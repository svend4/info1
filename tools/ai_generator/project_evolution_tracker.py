#!/usr/bin/env python3
"""
Project Evolution Tracker

Отслеживание эволюции проектов:
- Изменения в структуре
- Метрики кода (complexity, coverage, etc.)
- Technical debt tracking
- Refactoring suggestions
- Health score
"""

import os
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import hashlib


@dataclass
class StructureSnapshot:
    """Снимок структуры проекта"""
    timestamp: str
    directories_count: int
    files_count: int
    lines_of_code: int
    file_tree: Dict[str, any]
    file_hashes: Dict[str, str]


@dataclass
class CodeMetrics:
    """Метрики кода"""
    timestamp: str
    total_lines: int
    code_lines: int
    comment_lines: int
    blank_lines: int
    files_count: int
    average_complexity: float
    max_complexity: int
    functions_count: int
    classes_count: int
    test_coverage: Optional[float]
    duplicated_lines: int


@dataclass
class TechnicalDebt:
    """Technical debt item"""
    id: str
    category: str  # complexity, duplication, smell, security
    severity: str  # low, medium, high, critical
    file_path: str
    line_number: int
    description: str
    suggestion: str
    effort_minutes: int
    detected_at: str


@dataclass
class HealthScore:
    """Health score проекта"""
    timestamp: str
    overall_score: float  # 0-100
    structure_score: float
    code_quality_score: float
    test_coverage_score: float
    documentation_score: float
    maintainability_score: float
    issues: List[str]
    recommendations: List[str]


class ProjectEvolutionTracker:
    """
    Трекер эволюции проекта

    Tracks project changes, metrics, and health over time.
    """

    def __init__(self, project_path: Path):
        """
        Args:
            project_path: Путь к проекту
        """
        self.project_path = Path(project_path)
        self.tracker_dir = self.project_path / '.ai_tracker'
        self.tracker_dir.mkdir(parents=True, exist_ok=True)

        self.snapshots_file = self.tracker_dir / 'snapshots.json'
        self.metrics_file = self.tracker_dir / 'metrics.json'
        self.debt_file = self.tracker_dir / 'technical_debt.json'
        self.health_file = self.tracker_dir / 'health.json'

        self.snapshots = self._load_snapshots()
        self.metrics = self._load_metrics()
        self.debt_items = self._load_debt()
        self.health_history = self._load_health()

    def _load_snapshots(self) -> List[StructureSnapshot]:
        """Загрузка snapshots"""
        if self.snapshots_file.exists():
            with open(self.snapshots_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return [StructureSnapshot(**s) for s in data]
        return []

    def _save_snapshots(self):
        """Сохранение snapshots"""
        data = [asdict(s) for s in self.snapshots]
        with open(self.snapshots_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _load_metrics(self) -> List[CodeMetrics]:
        """Загрузка metrics"""
        if self.metrics_file.exists():
            with open(self.metrics_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return [CodeMetrics(**m) for m in data]
        return []

    def _save_metrics(self):
        """Сохранение metrics"""
        data = [asdict(m) for m in self.metrics]
        with open(self.metrics_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _load_debt(self) -> List[TechnicalDebt]:
        """Загрузка technical debt"""
        if self.debt_file.exists():
            with open(self.debt_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return [TechnicalDebt(**d) for d in data]
        return []

    def _save_debt(self):
        """Сохранение technical debt"""
        data = [asdict(d) for d in self.debt_items]
        with open(self.debt_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _load_health(self) -> List[HealthScore]:
        """Загрузка health history"""
        if self.health_file.exists():
            with open(self.health_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return [HealthScore(**h) for h in data]
        return []

    def _save_health(self):
        """Сохранение health history"""
        data = [asdict(h) for h in self.health_history]
        with open(self.health_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def take_snapshot(self) -> StructureSnapshot:
        """
        Создание snapshot структуры проекта

        Returns:
            StructureSnapshot
        """
        file_tree = {}
        file_hashes = {}
        total_files = 0
        total_dirs = 0
        total_lines = 0

        # Обход проекта
        for root, dirs, files in os.walk(self.project_path):
            # Пропускаем .git, .ai_tracker, __pycache__, node_modules
            dirs[:] = [d for d in dirs if d not in ['.git', '.ai_tracker', '__pycache__', 'node_modules', '.venv', 'venv']]

            rel_root = Path(root).relative_to(self.project_path)
            total_dirs += len(dirs)

            for file in files:
                file_path = Path(root) / file
                rel_path = file_path.relative_to(self.project_path)

                total_files += 1

                # Hash файла
                try:
                    with open(file_path, 'rb') as f:
                        file_hash = hashlib.md5(f.read()).hexdigest()
                        file_hashes[str(rel_path)] = file_hash

                    # Подсчёт строк для текстовых файлов
                    if file.endswith(('.py', '.js', '.java', '.c', '.cpp', '.h', '.md', '.txt', '.yml', '.yaml', '.json')):
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            lines = len(f.readlines())
                            total_lines += lines

                except Exception:
                    pass

        # Создаём file tree
        file_tree['directories'] = total_dirs
        file_tree['files'] = total_files

        snapshot = StructureSnapshot(
            timestamp=datetime.now().isoformat(),
            directories_count=total_dirs,
            files_count=total_files,
            lines_of_code=total_lines,
            file_tree=file_tree,
            file_hashes=file_hashes
        )

        self.snapshots.append(snapshot)
        self._save_snapshots()

        print(f"✅ Snapshot taken: {total_files} files, {total_lines} LOC")
        return snapshot

    def calculate_metrics(self) -> CodeMetrics:
        """
        Вычисление метрик кода

        Returns:
            CodeMetrics
        """
        total_lines = 0
        code_lines = 0
        comment_lines = 0
        blank_lines = 0
        files_count = 0
        functions_count = 0
        classes_count = 0

        # Проход по файлам
        for root, dirs, files in os.walk(self.project_path):
            dirs[:] = [d for d in dirs if d not in ['.git', '.ai_tracker', '__pycache__', 'node_modules', '.venv']]

            for file in files:
                if not file.endswith(('.py', '.js', '.java', '.c', '.cpp')):
                    continue

                file_path = Path(root) / file
                files_count += 1

                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = f.readlines()

                        for line in lines:
                            total_lines += 1
                            stripped = line.strip()

                            if not stripped:
                                blank_lines += 1
                            elif stripped.startswith('#') or stripped.startswith('//'):
                                comment_lines += 1
                            else:
                                code_lines += 1

                            # Подсчёт функций и классов (простой)
                            if file.endswith('.py'):
                                if stripped.startswith('def '):
                                    functions_count += 1
                                elif stripped.startswith('class '):
                                    classes_count += 1
                            elif file.endswith('.js'):
                                if 'function ' in stripped or '=>' in stripped:
                                    functions_count += 1
                                if 'class ' in stripped:
                                    classes_count += 1

                except Exception:
                    pass

        # Complexity (упрощённая версия)
        # В реальности использовать radon, mccabe, etc.
        avg_complexity = 1.0  # Placeholder
        max_complexity = 1  # Placeholder

        metrics = CodeMetrics(
            timestamp=datetime.now().isoformat(),
            total_lines=total_lines,
            code_lines=code_lines,
            comment_lines=comment_lines,
            blank_lines=blank_lines,
            files_count=files_count,
            average_complexity=avg_complexity,
            max_complexity=max_complexity,
            functions_count=functions_count,
            classes_count=classes_count,
            test_coverage=None,  # Requires pytest-cov
            duplicated_lines=0  # Requires duplication detection
        )

        self.metrics.append(metrics)
        self._save_metrics()

        print(f"✅ Metrics calculated: {code_lines} LOC, {functions_count} functions")
        return metrics

    def detect_technical_debt(self) -> List[TechnicalDebt]:
        """
        Обнаружение technical debt

        Returns:
            Список TechnicalDebt items
        """
        new_debt_items = []

        # 1. Большие функции (>50 lines)
        for root, dirs, files in os.walk(self.project_path):
            dirs[:] = [d for d in dirs if d not in ['.git', '.ai_tracker', '__pycache__', 'node_modules']]

            for file in files:
                if not file.endswith('.py'):
                    continue

                file_path = Path(root) / file
                rel_path = file_path.relative_to(self.project_path)

                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        in_function = False
                        function_start = 0
                        function_name = ""

                        for i, line in enumerate(lines, 1):
                            stripped = line.strip()

                            if stripped.startswith('def '):
                                if in_function and (i - function_start) > 50:
                                    # Большая функция
                                    debt_id = hashlib.md5(
                                        f"{rel_path}{function_start}".encode()
                                    ).hexdigest()[:12]

                                    debt = TechnicalDebt(
                                        id=debt_id,
                                        category='complexity',
                                        severity='medium',
                                        file_path=str(rel_path),
                                        line_number=function_start,
                                        description=f"Function '{function_name}' is too long ({i - function_start} lines)",
                                        suggestion="Consider breaking down into smaller functions",
                                        effort_minutes=30,
                                        detected_at=datetime.now().isoformat()
                                    )

                                    new_debt_items.append(debt)

                                in_function = True
                                function_start = i
                                function_name = stripped.split('(')[0].replace('def ', '')

                except Exception:
                    pass

        # 2. Missing docstrings
        for root, dirs, files in os.walk(self.project_path):
            dirs[:] = [d for d in dirs if d not in ['.git', '.ai_tracker', '__pycache__', 'node_modules']]

            for file in files:
                if not file.endswith('.py'):
                    continue

                file_path = Path(root) / file
                rel_path = file_path.relative_to(self.project_path)

                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                        # Простая проверка на отсутствие docstrings
                        if 'def ' in content and '"""' not in content and "'''" not in content:
                            debt_id = hashlib.md5(f"{rel_path}docstring".encode()).hexdigest()[:12]

                            debt = TechnicalDebt(
                                id=debt_id,
                                category='documentation',
                                severity='low',
                                file_path=str(rel_path),
                                line_number=1,
                                description="Missing docstrings",
                                suggestion="Add docstrings to functions and classes",
                                effort_minutes=15,
                                detected_at=datetime.now().isoformat()
                            )

                            new_debt_items.append(debt)

                except Exception:
                    pass

        # Добавляем новые debt items
        self.debt_items.extend(new_debt_items)
        self._save_debt()

        print(f"✅ Detected {len(new_debt_items)} technical debt items")
        return new_debt_items

    def calculate_health_score(self) -> HealthScore:
        """
        Вычисление health score проекта

        Returns:
            HealthScore
        """
        # Берём последний snapshot и metrics
        snapshot = self.snapshots[-1] if self.snapshots else None
        metrics = self.metrics[-1] if self.metrics else None

        structure_score = 70.0  # Placeholder
        code_quality_score = 75.0
        test_coverage_score = 60.0
        documentation_score = 65.0
        maintainability_score = 70.0

        if snapshot:
            # Проверка структуры
            if snapshot.files_count > 0:
                structure_score = min(100, 50 + (snapshot.directories_count / snapshot.files_count) * 100)

        if metrics:
            # Code quality на основе метрик
            if metrics.total_lines > 0:
                comment_ratio = metrics.comment_lines / metrics.total_lines
                code_quality_score = min(100, 50 + comment_ratio * 200)

        # Technical debt влияет на maintainability
        critical_debt = len([d for d in self.debt_items if d.severity == 'critical'])
        high_debt = len([d for d in self.debt_items if d.severity == 'high'])

        maintainability_score = max(0, 100 - critical_debt * 20 - high_debt * 10)

        # Overall score
        overall_score = (
            structure_score * 0.2 +
            code_quality_score * 0.25 +
            test_coverage_score * 0.2 +
            documentation_score * 0.15 +
            maintainability_score * 0.2
        )

        # Issues и recommendations
        issues = []
        recommendations = []

        if test_coverage_score < 70:
            issues.append("Low test coverage")
            recommendations.append("Increase test coverage to 70%+")

        if critical_debt > 0:
            issues.append(f"{critical_debt} critical technical debt items")
            recommendations.append("Address critical debt items first")

        if documentation_score < 70:
            issues.append("Insufficient documentation")
            recommendations.append("Add more docstrings and documentation")

        health = HealthScore(
            timestamp=datetime.now().isoformat(),
            overall_score=round(overall_score, 2),
            structure_score=round(structure_score, 2),
            code_quality_score=round(code_quality_score, 2),
            test_coverage_score=round(test_coverage_score, 2),
            documentation_score=round(documentation_score, 2),
            maintainability_score=round(maintainability_score, 2),
            issues=issues,
            recommendations=recommendations
        )

        self.health_history.append(health)
        self._save_health()

        print(f"✅ Health score: {health.overall_score}/100")
        return health

    def get_evolution_report(self) -> Dict:
        """
        Отчёт об эволюции проекта

        Returns:
            Dict с полным отчётом
        """
        if not self.snapshots or not self.metrics:
            return {
                'error': 'No tracking data available. Run take_snapshot() first.'
            }

        first_snapshot = self.snapshots[0]
        last_snapshot = self.snapshots[-1]

        first_metrics = self.metrics[0]
        last_metrics = self.metrics[-1]

        # Changes
        files_change = last_snapshot.files_count - first_snapshot.files_count
        lines_change = last_metrics.code_lines - first_metrics.code_lines

        # Debt
        total_debt = len(self.debt_items)
        critical_debt = len([d for d in self.debt_items if d.severity == 'critical'])
        debt_effort_hours = sum(d.effort_minutes for d in self.debt_items) / 60

        # Health
        current_health = self.health_history[-1] if self.health_history else None

        return {
            'project_path': str(self.project_path),
            'tracking_period': {
                'start': first_snapshot.timestamp,
                'end': last_snapshot.timestamp,
                'snapshots_count': len(self.snapshots)
            },
            'growth': {
                'files': {
                    'start': first_snapshot.files_count,
                    'current': last_snapshot.files_count,
                    'change': files_change,
                    'change_percent': round(files_change / first_snapshot.files_count * 100, 1) if first_snapshot.files_count > 0 else 0
                },
                'lines_of_code': {
                    'start': first_metrics.code_lines,
                    'current': last_metrics.code_lines,
                    'change': lines_change,
                    'change_percent': round(lines_change / first_metrics.code_lines * 100, 1) if first_metrics.code_lines > 0 else 0
                }
            },
            'technical_debt': {
                'total_items': total_debt,
                'critical': critical_debt,
                'high': len([d for d in self.debt_items if d.severity == 'high']),
                'medium': len([d for d in self.debt_items if d.severity == 'medium']),
                'low': len([d for d in self.debt_items if d.severity == 'low']),
                'estimated_effort_hours': round(debt_effort_hours, 1)
            },
            'current_health': asdict(current_health) if current_health else None,
            'recommendations': current_health.recommendations if current_health else []
        }


if __name__ == '__main__':
    print("="*70)
    print("PROJECT EVOLUTION TRACKER")
    print("="*70)
    print("\nTracks project changes, metrics, and health over time")
    print("\nUsage:")
    print("  from project_evolution_tracker import ProjectEvolutionTracker")
    print("  tracker = ProjectEvolutionTracker(Path('./my-project'))")
    print("  tracker.take_snapshot()")
    print("  tracker.calculate_metrics()")
    print("  health = tracker.calculate_health_score()")
