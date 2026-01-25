#!/usr/bin/env python3
"""
Refactoring Engine

Автоматический рефакторинг кода с сохранением функциональности.
"""

import ast
import re
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class RefactoringType(Enum):
    """Типы рефакторинга"""
    EXTRACT_METHOD = "extract_method"
    RENAME_VARIABLE = "rename_variable"
    SIMPLIFY_CONDITIONAL = "simplify_conditional"
    REMOVE_DUPLICATE_CODE = "remove_duplicate_code"
    INLINE_VARIABLE = "inline_variable"
    EXTRACT_CONSTANT = "extract_constant"
    REPLACE_MAGIC_NUMBER = "replace_magic_number"
    DECOMPOSE_CONDITIONAL = "decompose_conditional"
    CONSOLIDATE_CONDITIONAL = "consolidate_conditional"
    REMOVE_DEAD_CODE = "remove_dead_code"


@dataclass
class RefactoringOperation:
    """Операция рефакторинга"""
    refactoring_type: RefactoringType
    description: str
    line_start: int
    line_end: int
    original_code: str
    refactored_code: str
    confidence: float
    impact: str  # 'low', 'medium', 'high'
    preserves_behavior: bool
    requires_review: bool

    def to_dict(self) -> Dict:
        return {
            'type': self.refactoring_type.value,
            'description': self.description,
            'line_start': self.line_start,
            'line_end': self.line_end,
            'original_code': self.original_code,
            'refactored_code': self.refactored_code,
            'confidence': self.confidence,
            'impact': self.impact,
            'preserves_behavior': self.preserves_behavior,
            'requires_review': self.requires_review
        }


@dataclass
class RefactoringPlan:
    """План рефакторинга"""
    file_path: str
    operations: List[RefactoringOperation]
    total_operations: int
    estimated_improvement: str
    risks: List[str]

    def to_dict(self) -> Dict:
        return {
            'file_path': self.file_path,
            'total_operations': self.total_operations,
            'estimated_improvement': self.estimated_improvement,
            'risks': self.risks,
            'operations': [op.to_dict() for op in self.operations]
        }


class RefactoringEngine:
    """
    Refactoring Engine

    Автоматически рефакторит код:
    - Извлечение методов
    - Упрощение условий
    - Удаление дублирования
    - Замена magic numbers
    - Удаление мертвого кода
    """

    # Magic numbers (исключения)
    COMMON_NUMBERS = {0, 1, -1, 2, 10, 100, 1000}

    def __init__(self, aggressive: bool = False):
        """
        Инициализация

        Args:
            aggressive: Если True, более агрессивный рефакторинг
        """
        self.aggressive = aggressive
        self.refactoring_history: List[RefactoringPlan] = []

    def analyze_file(self, file_path: str) -> RefactoringPlan:
        """
        Анализ файла и создание плана рефакторинга

        Args:
            file_path: Путь к файлу

        Returns:
            План рефакторинга
        """
        with open(file_path, 'r') as f:
            code = f.read()

        return self.create_refactoring_plan(code, file_path)

    def create_refactoring_plan(self, code: str, file_path: str = "unknown") -> RefactoringPlan:
        """
        Создание плана рефакторинга

        Args:
            code: Исходный код
            file_path: Путь к файлу

        Returns:
            План рефакторинга
        """
        operations: List[RefactoringOperation] = []

        # 1. Поиск длинных методов для извлечения
        operations.extend(self._find_long_methods(code))

        # 2. Поиск magic numbers
        operations.extend(self._find_magic_numbers(code))

        # 3. Поиск дублирования
        operations.extend(self._find_duplicates(code))

        # 4. Поиск сложных условий
        operations.extend(self._find_complex_conditionals(code))

        # 5. Поиск мертвого кода
        operations.extend(self._find_dead_code(code))

        # 6. Поиск переменных для переименования
        operations.extend(self._find_poor_names(code))

        # Оценка улучшения
        improvement = self._estimate_improvement(operations)

        # Определение рисков
        risks = self._identify_risks(operations)

        plan = RefactoringPlan(
            file_path=file_path,
            operations=operations,
            total_operations=len(operations),
            estimated_improvement=improvement,
            risks=risks
        )

        self.refactoring_history.append(plan)
        return plan

    def _find_long_methods(self, code: str) -> List[RefactoringOperation]:
        """Поиск длинных методов для извлечения"""
        operations = []

        try:
            tree = ast.parse(code)
        except SyntaxError:
            return operations

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Подсчет строк в функции
                body_lines = node.end_lineno - node.lineno if hasattr(node, 'end_lineno') else 0

                if body_lines > 50:
                    operations.append(RefactoringOperation(
                        refactoring_type=RefactoringType.EXTRACT_METHOD,
                        description=f"Function '{node.name}' is too long ({body_lines} lines)",
                        line_start=node.lineno,
                        line_end=node.end_lineno if hasattr(node, 'end_lineno') else node.lineno + 10,
                        original_code=self._get_code_snippet(code, node.lineno, 3),
                        refactored_code=f"# Extract logical blocks into separate methods",
                        confidence=0.8,
                        impact='high',
                        preserves_behavior=True,
                        requires_review=True
                    ))

                # Поиск блоков кода внутри функции для извлечения
                for child in node.body:
                    if isinstance(child, (ast.For, ast.While)):
                        # Сложный цикл можно извлечь
                        loop_complexity = self._calculate_complexity(child)
                        if loop_complexity > 5:
                            operations.append(RefactoringOperation(
                                refactoring_type=RefactoringType.EXTRACT_METHOD,
                                description=f"Extract complex loop into separate method",
                                line_start=child.lineno,
                                line_end=child.end_lineno if hasattr(child, 'end_lineno') else child.lineno,
                                original_code=self._get_code_snippet(code, child.lineno, 2),
                                refactored_code=f"# Extract: def _process_items(items): ...",
                                confidence=0.75,
                                impact='medium',
                                preserves_behavior=True,
                                requires_review=False
                            ))

        return operations

    def _find_magic_numbers(self, code: str) -> List[RefactoringOperation]:
        """Поиск magic numbers для замены константами"""
        operations = []
        lines = code.split('\n')

        try:
            tree = ast.parse(code)
        except SyntaxError:
            return operations

        found_numbers = {}

        for node in ast.walk(tree):
            if isinstance(node, ast.Constant):
                if isinstance(node.value, (int, float)):
                    # Пропускаем общие числа
                    if node.value in self.COMMON_NUMBERS:
                        continue

                    # Пропускаем числа в вызовах range()
                    if hasattr(node, 'lineno'):
                        line = lines[node.lineno - 1] if node.lineno <= len(lines) else ""
                        if 'range(' in line:
                            continue

                    number = node.value
                    line_num = getattr(node, 'lineno', 0)

                    if number not in found_numbers:
                        found_numbers[number] = []
                    found_numbers[number].append(line_num)

        # Создание операций для чисел, которые встречаются более одного раза
        for number, line_nums in found_numbers.items():
            if len(line_nums) > 1:
                const_name = f"CONSTANT_{abs(int(number))}"

                operations.append(RefactoringOperation(
                    refactoring_type=RefactoringType.REPLACE_MAGIC_NUMBER,
                    description=f"Replace magic number {number} with named constant (used {len(line_nums)} times)",
                    line_start=min(line_nums),
                    line_end=max(line_nums),
                    original_code=f"value = {number}",
                    refactored_code=f"{const_name} = {number}  # Add at module level\nvalue = {const_name}",
                    confidence=0.9,
                    impact='low',
                    preserves_behavior=True,
                    requires_review=False
                ))

        return operations

    def _find_duplicates(self, code: str) -> List[RefactoringOperation]:
        """Поиск дублирования кода"""
        operations = []
        lines = code.split('\n')

        # Поиск дублирующихся блоков (упрощенный алгоритм)
        min_block_size = 3
        blocks = {}

        for i in range(len(lines) - min_block_size + 1):
            block = '\n'.join(lines[i:i+min_block_size])
            block_normalized = re.sub(r'\s+', ' ', block).strip()

            if not block_normalized or block_normalized.startswith('#'):
                continue

            if block_normalized not in blocks:
                blocks[block_normalized] = []
            blocks[block_normalized].append(i + 1)

        # Операции для дублирующихся блоков
        for block_text, line_nums in blocks.items():
            if len(line_nums) > 1:
                operations.append(RefactoringOperation(
                    refactoring_type=RefactoringType.REMOVE_DUPLICATE_CODE,
                    description=f"Duplicate code block found ({len(line_nums)} occurrences)",
                    line_start=min(line_nums),
                    line_end=min(line_nums) + min_block_size,
                    original_code=block_text[:100] + "...",
                    refactored_code="# Extract into common function",
                    confidence=0.7,
                    impact='medium',
                    preserves_behavior=True,
                    requires_review=True
                ))

        return operations

    def _find_complex_conditionals(self, code: str) -> List[RefactoringOperation]:
        """Поиск сложных условий"""
        operations = []

        try:
            tree = ast.parse(code)
        except SyntaxError:
            return operations

        for node in ast.walk(tree):
            if isinstance(node, ast.If):
                # Подсчет сложности условия
                condition_complexity = self._count_boolean_operators(node.test)

                if condition_complexity > 3:
                    operations.append(RefactoringOperation(
                        refactoring_type=RefactoringType.SIMPLIFY_CONDITIONAL,
                        description=f"Complex conditional with {condition_complexity} boolean operators",
                        line_start=node.lineno,
                        line_end=node.lineno,
                        original_code=self._get_code_snippet(code, node.lineno, 0),
                        refactored_code="# Extract to descriptive method: if is_valid_user():",
                        confidence=0.8,
                        impact='medium',
                        preserves_behavior=True,
                        requires_review=False
                    ))

                # Множественные elif
                elif_count = len(node.orelse)
                if elif_count > 4:
                    operations.append(RefactoringOperation(
                        refactoring_type=RefactoringType.SIMPLIFY_CONDITIONAL,
                        description=f"Long if-elif chain ({elif_count} branches)",
                        line_start=node.lineno,
                        line_end=node.lineno + elif_count * 2,
                        original_code=self._get_code_snippet(code, node.lineno, 1),
                        refactored_code="# Consider using dictionary dispatch or match/case (Python 3.10+)",
                        confidence=0.7,
                        impact='medium',
                        preserves_behavior=True,
                        requires_review=True
                    ))

        return operations

    def _find_dead_code(self, code: str) -> List[RefactoringOperation]:
        """Поиск мертвого кода"""
        operations = []

        try:
            tree = ast.parse(code)
        except SyntaxError:
            return operations

        # Поиск функций/классов, которые не используются
        defined_names = set()
        used_names = set()

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                defined_names.add(node.name)
            elif isinstance(node, ast.ClassDef):
                defined_names.add(node.name)
            elif isinstance(node, ast.Name):
                used_names.add(node.id)

        unused = defined_names - used_names

        for name in unused:
            # Пропускаем специальные методы и приватные
            if name.startswith('__') or name == 'main':
                continue

            operations.append(RefactoringOperation(
                refactoring_type=RefactoringType.REMOVE_DEAD_CODE,
                description=f"Unused function/class: '{name}'",
                line_start=0,
                line_end=0,
                original_code=f"def {name}(...) / class {name}:",
                refactored_code="# Remove if truly unused",
                confidence=0.6,
                impact='low',
                preserves_behavior=True,
                requires_review=True
            ))

        return operations

    def _find_poor_names(self, code: str) -> List[RefactoringOperation]:
        """Поиск плохих имен переменных"""
        operations = []

        try:
            tree = ast.parse(code)
        except SyntaxError:
            return operations

        poor_names = {'a', 'b', 'c', 'x', 'y', 'z', 'tmp', 'temp', 'data', 'result'}

        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                if node.id in poor_names and len(node.id) <= 4:
                    operations.append(RefactoringOperation(
                        refactoring_type=RefactoringType.RENAME_VARIABLE,
                        description=f"Non-descriptive variable name: '{node.id}'",
                        line_start=getattr(node, 'lineno', 0),
                        line_end=getattr(node, 'lineno', 0),
                        original_code=f"{node.id} = ...",
                        refactored_code=f"descriptive_name = ...  # Rename '{node.id}' to something meaningful",
                        confidence=0.5,
                        impact='low',
                        preserves_behavior=True,
                        requires_review=True
                    ))

        return operations

    def _calculate_complexity(self, node: ast.AST) -> int:
        """Расчет сложности узла"""
        complexity = 1

        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1

        return complexity

    def _count_boolean_operators(self, node: ast.AST) -> int:
        """Подсчет булевых операторов"""
        count = 0
        for child in ast.walk(node):
            if isinstance(child, (ast.And, ast.Or, ast.Not, ast.BoolOp)):
                count += 1
        return count

    def _get_code_snippet(self, code: str, line_number: int, context: int = 1) -> str:
        """Получение фрагмента кода"""
        lines = code.split('\n')
        if line_number <= 0 or line_number > len(lines):
            return ""

        start = max(0, line_number - 1 - context)
        end = min(len(lines), line_number + context)

        return '\n'.join(lines[start:end])

    def _estimate_improvement(self, operations: List[RefactoringOperation]) -> str:
        """Оценка улучшения от рефакторинга"""
        if not operations:
            return "No refactoring needed"

        high_impact = sum(1 for op in operations if op.impact == 'high')
        medium_impact = sum(1 for op in operations if op.impact == 'medium')

        if high_impact >= 3:
            return "Significant improvement expected"
        elif high_impact > 0 or medium_impact >= 5:
            return "Moderate improvement expected"
        else:
            return "Minor improvement expected"

    def _identify_risks(self, operations: List[RefactoringOperation]) -> List[str]:
        """Определение рисков"""
        risks = []

        high_impact_ops = [op for op in operations if op.impact == 'high']
        if len(high_impact_ops) > 5:
            risks.append("Many high-impact changes - thorough testing required")

        low_confidence_ops = [op for op in operations if op.confidence < 0.7]
        if len(low_confidence_ops) > 3:
            risks.append("Several low-confidence refactorings - manual review needed")

        extract_method_ops = [op for op in operations
                             if op.refactoring_type == RefactoringType.EXTRACT_METHOD]
        if len(extract_method_ops) > 3:
            risks.append("Multiple method extractions may change code structure significantly")

        return risks if risks else ["Low risk - mostly safe refactorings"]

    def apply_refactoring(self, code: str, operation: RefactoringOperation) -> str:
        """
        Применение операции рефакторинга

        Args:
            code: Исходный код
            operation: Операция

        Returns:
            Рефакторенный код
        """
        # Для демонстрации - реальная реализация потребует AST трансформации
        lines = code.split('\n')

        if operation.refactoring_type == RefactoringType.REPLACE_MAGIC_NUMBER:
            # Простая замена magic number
            # В реальности нужен более сложный AST-based подход
            pass

        return code  # Заглушка

    def apply_all_safe_refactorings(self, code: str, plan: RefactoringPlan) -> str:
        """
        Применение всех безопасных рефакторингов

        Args:
            code: Исходный код
            plan: План рефакторинга

        Returns:
            Рефакторенный код
        """
        refactored = code

        # Применяем только безопасные операции (высокая уверенность, не требуют ревью)
        safe_ops = [
            op for op in plan.operations
            if op.confidence >= 0.8 and not op.requires_review
        ]

        for operation in safe_ops:
            refactored = self.apply_refactoring(refactored, operation)

        return refactored

    def generate_refactoring_report(self, plan: RefactoringPlan) -> str:
        """Генерация отчета о рефакторинге"""
        lines = []

        lines.append("=" * 70)
        lines.append("REFACTORING PLAN")
        lines.append("=" * 70)
        lines.append(f"\nFile: {plan.file_path}")
        lines.append(f"Total operations: {plan.total_operations}")
        lines.append(f"Estimated improvement: {plan.estimated_improvement}")
        lines.append(f"\nRisks:")
        for risk in plan.risks:
            lines.append(f"  - {risk}")

        lines.append("\n" + "=" * 70)
        lines.append("OPERATIONS")
        lines.append("=" * 70)

        # Группировка по типу
        by_type = {}
        for op in plan.operations:
            op_type = op.refactoring_type.value
            if op_type not in by_type:
                by_type[op_type] = []
            by_type[op_type].append(op)

        for op_type, ops in by_type.items():
            lines.append(f"\n{op_type.upper().replace('_', ' ')} ({len(ops)})")
            lines.append("-" * 50)

            for op in ops[:3]:  # Показываем первые 3
                lines.append(f"\nLine {op.line_start}: {op.description}")
                lines.append(f"Impact: {op.impact}, Confidence: {op.confidence:.0%}")
                lines.append(f"Original: {op.original_code[:60]}...")
                lines.append(f"Refactored: {op.refactored_code[:60]}...")

            if len(ops) > 3:
                lines.append(f"\n... and {len(ops) - 3} more")

        return "\n".join(lines)
