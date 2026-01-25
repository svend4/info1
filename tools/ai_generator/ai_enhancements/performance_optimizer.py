#!/usr/bin/env python3
"""
Performance Optimizer

Автоматический анализ и оптимизация производительности кода.
"""

import ast
import re
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
from collections import defaultdict


class OptimizationType(Enum):
    """Тип оптимизации"""
    ALGORITHM = "algorithm"
    DATA_STRUCTURE = "data_structure"
    CACHING = "caching"
    LAZY_EVALUATION = "lazy_evaluation"
    VECTORIZATION = "vectorization"
    MEMORY = "memory"
    IO_OPTIMIZATION = "io_optimization"
    CONCURRENCY = "concurrency"


@dataclass
class PerformanceIssue:
    """Проблема производительности"""
    issue_type: OptimizationType
    severity: str  # 'low', 'medium', 'high', 'critical'
    description: str
    current_complexity: str
    optimized_complexity: str
    line_number: int
    original_code: str
    optimized_code: str
    expected_speedup: str
    explanation: str

    def to_dict(self) -> Dict:
        return {
            'type': self.issue_type.value,
            'severity': self.severity,
            'description': self.description,
            'current_complexity': self.current_complexity,
            'optimized_complexity': self.optimized_complexity,
            'line_number': self.line_number,
            'original_code': self.original_code,
            'optimized_code': self.optimized_code,
            'expected_speedup': self.expected_speedup,
            'explanation': self.explanation
        }


@dataclass
class OptimizationReport:
    """Отчет об оптимизации"""
    file_path: str
    issues: List[PerformanceIssue]
    total_issues: int
    potential_speedup: str
    metrics: Dict[str, Any]

    def to_dict(self) -> Dict:
        return {
            'file_path': self.file_path,
            'total_issues': self.total_issues,
            'potential_speedup': self.potential_speedup,
            'metrics': self.metrics,
            'issues': [issue.to_dict() for issue in self.issues]
        }


class PerformanceOptimizer:
    """
    Performance Optimizer

    Анализирует код и предлагает оптимизации:
    - Алгоритмическая сложность
    - Структуры данных
    - Кеширование
    - Векторизация
    - Управление памятью
    """

    # Паттерны неэффективных алгоритмов
    ANTIPATTERNS = {
        'nested_loops_with_membership': {
            'pattern': r'for\s+\w+\s+in\s+.*:\s*for\s+\w+\s+in\s+.*:\s*if\s+.*\s+in\s+',
            'complexity': 'O(n³)',
            'optimized': 'O(n²) or O(n)',
            'type': OptimizationType.ALGORITHM
        },
        'list_in_loop': {
            'pattern': r'for\s+.*\s+in\s+.*:\s*if\s+.*\s+in\s+\[',
            'complexity': 'O(n²)',
            'optimized': 'O(n)',
            'type': OptimizationType.DATA_STRUCTURE
        },
        'repeated_len_calls': {
            'pattern': r'for\s+.*\s+in\s+range\(len\(.*\)\):.*len\(',
            'complexity': 'O(n) with repeated calls',
            'optimized': 'O(n)',
            'type': OptimizationType.ALGORITHM
        }
    }

    def __init__(self):
        """Инициализация оптимизатора"""
        self.optimization_history: List[OptimizationReport] = []

    def analyze_file(self, file_path: str) -> OptimizationReport:
        """
        Анализ файла на проблемы производительности

        Args:
            file_path: Путь к файлу

        Returns:
            Отчет об оптимизации
        """
        with open(file_path, 'r') as f:
            code = f.read()

        return self.analyze_code(code, file_path)

    def analyze_code(self, code: str, file_path: str = "unknown") -> OptimizationReport:
        """
        Анализ кода на проблемы производительности

        Args:
            code: Исходный код
            file_path: Путь к файлу (для отчета)

        Returns:
            Отчет об оптимизации
        """
        issues: List[PerformanceIssue] = []

        # 1. AST анализ
        issues.extend(self._analyze_ast(code, file_path))

        # 2. Паттерн-матчинг
        issues.extend(self._pattern_analysis(code, file_path))

        # 3. Анализ структур данных
        issues.extend(self._data_structure_analysis(code, file_path))

        # 4. Анализ IO операций
        issues.extend(self._io_analysis(code, file_path))

        # Расчет метрик
        metrics = self._calculate_metrics(code, issues)

        # Оценка потенциального ускорения
        speedup = self._estimate_speedup(issues)

        report = OptimizationReport(
            file_path=file_path,
            issues=issues,
            total_issues=len(issues),
            potential_speedup=speedup,
            metrics=metrics
        )

        self.optimization_history.append(report)
        return report

    def _analyze_ast(self, code: str, file_path: str) -> List[PerformanceIssue]:
        """Анализ через AST"""
        issues = []

        try:
            tree = ast.parse(code)
        except SyntaxError:
            return issues

        for node in ast.walk(tree):
            # Поиск вложенных циклов
            if isinstance(node, ast.For):
                nested_loops = self._count_nested_loops(node)
                if nested_loops >= 3:
                    issues.append(PerformanceIssue(
                        issue_type=OptimizationType.ALGORITHM,
                        severity='high',
                        description=f'{nested_loops} nested loops detected',
                        current_complexity=f'O(n^{nested_loops})',
                        optimized_complexity='O(n log n) or O(n²)',
                        line_number=node.lineno,
                        original_code=self._get_code_snippet(code, node.lineno),
                        optimized_code='# Consider using vectorization, memoization, or better algorithm',
                        expected_speedup=f'{2**nested_loops}x-{10**nested_loops}x',
                        explanation='Multiple nested loops cause exponential time complexity. Consider algorithmic improvements.'
                    ))

            # Список в list comprehension внутри цикла
            if isinstance(node, ast.For):
                for child in ast.walk(node):
                    if isinstance(child, ast.ListComp):
                        issues.append(PerformanceIssue(
                            issue_type=OptimizationType.ALGORITHM,
                            severity='medium',
                            description='List comprehension inside loop',
                            current_complexity='O(n²)',
                            optimized_complexity='O(n)',
                            line_number=node.lineno,
                            original_code=self._get_code_snippet(code, node.lineno),
                            optimized_code='# Move comprehension outside loop or use generator',
                            expected_speedup='2x-10x',
                            explanation='Creating new lists in each iteration is inefficient. Consider generator expressions or restructuring.'
                        ))

            # Конкатенация строк в цикле
            if isinstance(node, ast.For):
                for child in ast.walk(node):
                    if isinstance(child, ast.AugAssign) and isinstance(child.op, ast.Add):
                        if isinstance(child.target, ast.Name):
                            # Проверка типа (примерная)
                            issues.append(PerformanceIssue(
                                issue_type=OptimizationType.MEMORY,
                                severity='medium',
                                description='String concatenation in loop',
                                current_complexity='O(n²)',
                                optimized_complexity='O(n)',
                                line_number=node.lineno,
                                original_code=self._get_code_snippet(code, node.lineno),
                                optimized_code="result = ''.join(items)",
                                expected_speedup='5x-50x for large strings',
                                explanation='String concatenation creates new objects. Use list and join() instead.'
                            ))

            # Множественные вызовы len() в цикле
            if isinstance(node, ast.For):
                len_calls = sum(1 for child in ast.walk(node)
                              if isinstance(child, ast.Call)
                              and isinstance(child.func, ast.Name)
                              and child.func.id == 'len')
                if len_calls > 2:
                    issues.append(PerformanceIssue(
                        issue_type=OptimizationType.CACHING,
                        severity='low',
                        description=f'Multiple len() calls ({len_calls}) in loop',
                        current_complexity='O(n) with overhead',
                        optimized_complexity='O(n)',
                        line_number=node.lineno,
                        original_code=self._get_code_snippet(code, node.lineno),
                        optimized_code='length = len(items)  # Calculate once before loop',
                        expected_speedup='1.5x-2x',
                        explanation='Cache length calculation before loop to avoid repeated calls.'
                    ))

        return issues

    def _pattern_analysis(self, code: str, file_path: str) -> List[PerformanceIssue]:
        """Анализ паттернов кода"""
        issues = []
        lines = code.split('\n')

        # Проверка на использование списка для membership testing
        for i, line in enumerate(lines, 1):
            if re.search(r'if\s+\w+\s+in\s+\[.*\]:', line):
                issues.append(PerformanceIssue(
                    issue_type=OptimizationType.DATA_STRUCTURE,
                    severity='medium',
                    description='List used for membership testing',
                    current_complexity='O(n)',
                    optimized_complexity='O(1)',
                    line_number=i,
                    original_code=line.strip(),
                    optimized_code=line.strip().replace('[', '{').replace(']', '}') + '  # Use set instead',
                    expected_speedup='10x-100x for large collections',
                    explanation='Sets provide O(1) membership testing vs O(n) for lists.'
                ))

            # Проверка глобальных переменных в циклах
            if 'global ' in line and any('for ' in l for l in lines[max(0, i-3):i+3]):
                issues.append(PerformanceIssue(
                    issue_type=OptimizationType.ALGORITHM,
                    severity='medium',
                    description='Global variable access in loop context',
                    current_complexity='O(n) with overhead',
                    optimized_complexity='O(n)',
                    line_number=i,
                    original_code=line.strip(),
                    optimized_code='# Use local variable instead of global',
                    expected_speedup='1.5x-3x',
                    explanation='Global lookups are slower than local. Cache in local variable.'
                ))

        return issues

    def _data_structure_analysis(self, code: str, file_path: str) -> List[PerformanceIssue]:
        """Анализ использования структур данных"""
        issues = []
        lines = code.split('\n')

        for i, line in enumerate(lines, 1):
            # Поиск по индексу вместо итератора
            if re.search(r'for\s+\w+\s+in\s+range\(len\((\w+)\)\):.*\[\1\]', line + lines[i] if i < len(lines) else ''):
                issues.append(PerformanceIssue(
                    issue_type=OptimizationType.ALGORITHM,
                    severity='low',
                    description='Index-based iteration instead of iterator',
                    current_complexity='O(n)',
                    optimized_complexity='O(n) (same, but cleaner)',
                    line_number=i,
                    original_code=line.strip(),
                    optimized_code='for item in items:  # Direct iteration',
                    expected_speedup='1.2x-1.5x (minor improvement)',
                    explanation='Direct iteration is more Pythonic and slightly faster.'
                ))

            # Множественные append в цикле
            if '.append(' in line and any('for ' in l for l in lines[max(0, i-2):i+1]):
                # Проверка, не лучше ли использовать list comprehension
                issues.append(PerformanceIssue(
                    issue_type=OptimizationType.ALGORITHM,
                    severity='low',
                    description='Multiple append() calls in loop',
                    current_complexity='O(n)',
                    optimized_complexity='O(n) (same, but faster)',
                    line_number=i,
                    original_code=line.strip(),
                    optimized_code='result = [process(x) for x in items]  # List comprehension',
                    expected_speedup='1.3x-2x',
                    explanation='List comprehensions are optimized in CPython and generally faster.'
                ))

        return issues

    def _io_analysis(self, code: str, file_path: str) -> List[PerformanceIssue]:
        """Анализ IO операций"""
        issues = []
        lines = code.split('\n')

        for i, line in enumerate(lines, 1):
            # Чтение файла построчно без генератора
            if 'readlines()' in line:
                issues.append(PerformanceIssue(
                    issue_type=OptimizationType.MEMORY,
                    severity='medium',
                    description='readlines() loads entire file into memory',
                    current_complexity='O(n) memory',
                    optimized_complexity='O(1) memory',
                    line_number=i,
                    original_code=line.strip(),
                    optimized_code='for line in file:  # Iterate directly',
                    expected_speedup='Memory usage: 100x-1000x improvement',
                    explanation='Direct iteration over file object is memory-efficient.'
                ))

            # Множественные открытия файла
            if 'open(' in line:
                # Проверка контекста
                context_lines = lines[max(0, i-5):min(len(lines), i+5)]
                open_count = sum(1 for l in context_lines if 'open(' in l)
                if open_count > 1:
                    issues.append(PerformanceIssue(
                        issue_type=OptimizationType.IO_OPTIMIZATION,
                        severity='medium',
                        description='Multiple file open operations',
                        current_complexity='O(k*n) where k=opens',
                        optimized_complexity='O(n)',
                        line_number=i,
                        original_code=line.strip(),
                        optimized_code='# Combine operations into single file open',
                        expected_speedup='2x-10x depending on file size',
                        explanation='File I/O is expensive. Minimize open/close cycles.'
                    ))

        return issues

    def _count_nested_loops(self, node: ast.For) -> int:
        """Подсчет уровней вложенности циклов"""
        count = 1
        for child in ast.walk(node):
            if child != node and isinstance(child, (ast.For, ast.While)):
                child_count = self._count_nested_loops(child) if isinstance(child, ast.For) else 1
                count = max(count, 1 + child_count)
        return count

    def _get_code_snippet(self, code: str, line_number: int, context: int = 0) -> str:
        """Получение фрагмента кода вокруг строки"""
        lines = code.split('\n')
        if line_number <= 0 or line_number > len(lines):
            return ""

        start = max(0, line_number - 1 - context)
        end = min(len(lines), line_number + context)

        snippet_lines = lines[start:end]
        return '\n'.join(snippet_lines)

    def _calculate_metrics(self, code: str, issues: List[PerformanceIssue]) -> Dict[str, Any]:
        """Расчет метрик производительности"""
        lines = code.split('\n')
        code_lines = [l for l in lines if l.strip() and not l.strip().startswith('#')]

        # Подсчет различных конструкций
        loop_count = sum(1 for line in code_lines if re.match(r'\s*(for|while)\s+', line))
        list_comp_count = sum(1 for line in code_lines if '[' in line and 'for' in line and 'in' in line)

        # Группировка проблем по типу
        issues_by_type = defaultdict(int)
        for issue in issues:
            issues_by_type[issue.issue_type.value] += 1

        return {
            'total_lines': len(lines),
            'code_lines': len(code_lines),
            'loop_count': loop_count,
            'list_comprehension_count': list_comp_count,
            'issues_by_type': dict(issues_by_type),
            'critical_issues': sum(1 for i in issues if i.severity == 'critical'),
            'high_issues': sum(1 for i in issues if i.severity == 'high'),
            'medium_issues': sum(1 for i in issues if i.severity == 'medium'),
            'low_issues': sum(1 for i in issues if i.severity == 'low')
        }

    def _estimate_speedup(self, issues: List[PerformanceIssue]) -> str:
        """Оценка потенциального ускорения"""
        if not issues:
            return "No optimization needed"

        critical_count = sum(1 for i in issues if i.severity == 'critical')
        high_count = sum(1 for i in issues if i.severity == 'high')
        medium_count = sum(1 for i in issues if i.severity == 'medium')

        if critical_count > 0:
            return "10x-100x (critical issues present)"
        elif high_count > 2:
            return "5x-50x (multiple high-priority issues)"
        elif high_count > 0 or medium_count > 3:
            return "2x-10x (several optimization opportunities)"
        else:
            return "1.5x-3x (minor improvements)"

    def apply_optimization(self, code: str, issue: PerformanceIssue) -> str:
        """
        Применение оптимизации к коду

        Args:
            code: Исходный код
            issue: Проблема для исправления

        Returns:
            Оптимизированный код
        """
        lines = code.split('\n')

        if issue.line_number > 0 and issue.line_number <= len(lines):
            # Замена строки на оптимизированную версию
            lines[issue.line_number - 1] = issue.optimized_code

        return '\n'.join(lines)

    def generate_optimization_suggestions(self, code: str) -> List[str]:
        """
        Генерация общих рекомендаций по оптимизации

        Args:
            code: Исходный код

        Returns:
            Список рекомендаций
        """
        suggestions = []

        # Проверка на отсутствие кеширования
        if '@lru_cache' not in code and 'cache' not in code.lower():
            suggestions.append("Consider using @lru_cache for expensive function calls")

        # Проверка на отсутствие генераторов
        if '[' in code and 'for' in code:
            list_comps = len(re.findall(r'\[.*for.*in.*\]', code))
            if list_comps > 3:
                suggestions.append(f"Found {list_comps} list comprehensions. Consider generators for memory efficiency")

        # Проверка импортов
        if 'import numpy' not in code and 'import pandas' not in code:
            if any(keyword in code for keyword in ['array', 'matrix', 'vector']):
                suggestions.append("Consider using NumPy for numerical operations (10x-100x faster)")

        # Проверка параллелизации
        if 'for ' in code and 'threading' not in code and 'multiprocessing' not in code:
            suggestions.append("Consider parallel processing for CPU-intensive loops")

        # Проверка профилирования
        suggestions.append("Use cProfile or line_profiler to identify actual bottlenecks")

        return suggestions

    def benchmark_code(self, code: str, iterations: int = 1000) -> Dict[str, float]:
        """
        Бенчмарк кода (симуляция)

        Args:
            code: Код для бенчмарка
            iterations: Количество итераций

        Returns:
            Результаты бенчмарка
        """
        # В реальности здесь был бы timeit или подобное
        # Для демонстрации возвращаем примерные значения

        lines = code.count('\n')
        complexity_estimate = len([l for l in code.split('\n') if 'for' in l]) * 10

        return {
            'avg_time_ms': complexity_estimate * 0.01,
            'min_time_ms': complexity_estimate * 0.008,
            'max_time_ms': complexity_estimate * 0.015,
            'std_dev_ms': complexity_estimate * 0.002,
            'iterations': iterations
        }
