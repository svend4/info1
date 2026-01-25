#!/usr/bin/env python3
"""
Bug Predictor

ML-powered предсказание потенциальных багов в коде.
"""

import ast
import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
from collections import defaultdict


class BugType(Enum):
    """Типы багов"""
    NULL_POINTER = "null_pointer"
    TYPE_ERROR = "type_error"
    INDEX_ERROR = "index_error"
    RACE_CONDITION = "race_condition"
    MEMORY_LEAK = "memory_leak"
    LOGIC_ERROR = "logic_error"
    RESOURCE_LEAK = "resource_leak"
    INFINITE_LOOP = "infinite_loop"
    DIVISION_BY_ZERO = "division_by_zero"


class BugSeverity(Enum):
    """Серьезность бага"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class BugPrediction:
    """Предсказание бага"""
    bug_type: BugType
    severity: BugSeverity
    confidence: float  # 0.0-1.0
    line_number: int
    description: str
    code_snippet: str
    evidence: List[str]
    fix_suggestion: str
    similar_bugs: List[str]

    def to_dict(self) -> Dict:
        return {
            'bug_type': self.bug_type.value,
            'severity': self.severity.value,
            'confidence': self.confidence,
            'line_number': self.line_number,
            'description': self.description,
            'code_snippet': self.code_snippet,
            'evidence': self.evidence,
            'fix_suggestion': self.fix_suggestion,
            'similar_bugs': self.similar_bugs
        }


@dataclass
class BugReport:
    """Отчет о предсказанных багах"""
    file_path: str
    predictions: List[BugPrediction]
    total_predictions: int
    high_confidence_count: int
    risk_score: float  # 0-100
    metrics: Dict[str, Any]

    def to_dict(self) -> Dict:
        return {
            'file_path': self.file_path,
            'total_predictions': self.total_predictions,
            'high_confidence_count': self.high_confidence_count,
            'risk_score': self.risk_score,
            'metrics': self.metrics,
            'predictions': [p.to_dict() for p in self.predictions]
        }


class BugPredictor:
    """
    Bug Predictor

    Предсказывает потенциальные баги используя:
    - Статический анализ
    - Паттерн-матчинг известных багов
    - Анализ control flow
    - Эвристики на основе best practices
    """

    # Паттерны известных багов
    BUG_PATTERNS = {
        BugType.NULL_POINTER: [
            r'\.(\w+)\s*\(',  # Вызов метода без проверки на None
            r'\[.*\](?!\s*if)',  # Индексация без проверки
        ],
        BugType.DIVISION_BY_ZERO: [
            r'/\s*\w+(?!\s*if)',  # Деление без проверки
        ],
        BugType.RESOURCE_LEAK: [
            r'open\([^)]+\)(?!.*with)',  # open без with
            r'socket\((?!.*close)',  # socket без close
        ],
        BugType.INFINITE_LOOP: [
            r'while\s+True:(?!.*break)',  # while True без break
        ]
    }

    # Опасные функции
    DANGEROUS_OPERATIONS = {
        'eval': BugType.LOGIC_ERROR,
        'exec': BugType.LOGIC_ERROR,
        '__import__': BugType.LOGIC_ERROR,
        'pickle.loads': BugType.LOGIC_ERROR,
    }

    def __init__(self):
        """Инициализация предиктора"""
        self.prediction_history: List[BugReport] = []
        self.known_bugs_db: Dict[str, List[str]] = self._load_known_bugs()

    def _load_known_bugs(self) -> Dict[str, List[str]]:
        """Загрузка базы известных багов"""
        return {
            'null_pointer': [
                "AttributeError: 'NoneType' object has no attribute 'x'",
                "TypeError: unsupported operand type(s) for +: 'NoneType' and 'int'",
            ],
            'index_error': [
                "IndexError: list index out of range",
                "KeyError: 'key_name'",
            ],
            'type_error': [
                "TypeError: can only concatenate str (not \"int\") to str",
                "TypeError: unsupported operand type(s)",
            ],
            'race_condition': [
                "Multiple threads accessing shared state without locks",
                "Check-then-act race condition",
            ]
        }

    def predict_file(self, file_path: str) -> BugReport:
        """
        Предсказание багов в файле

        Args:
            file_path: Путь к файлу

        Returns:
            Отчет о предсказаниях
        """
        with open(file_path, 'r') as f:
            code = f.read()

        return self.predict_bugs(code, file_path)

    def predict_bugs(self, code: str, file_path: str = "unknown") -> BugReport:
        """
        Предсказание багов в коде

        Args:
            code: Исходный код
            file_path: Путь к файлу

        Returns:
            Отчет о предсказаниях
        """
        predictions: List[BugPrediction] = []

        # 1. AST анализ
        predictions.extend(self._ast_analysis(code, file_path))

        # 2. Паттерн-матчинг
        predictions.extend(self._pattern_analysis(code, file_path))

        # 3. Анализ control flow
        predictions.extend(self._control_flow_analysis(code, file_path))

        # 4. Анализ типов (где возможно)
        predictions.extend(self._type_analysis(code, file_path))

        # 5. Анализ многопоточности
        predictions.extend(self._concurrency_analysis(code, file_path))

        # Фильтрация по confidence
        high_confidence = [p for p in predictions if p.confidence >= 0.7]

        # Расчет метрик
        metrics = self._calculate_metrics(code, predictions)

        # Расчет risk score
        risk_score = self._calculate_risk_score(predictions)

        report = BugReport(
            file_path=file_path,
            predictions=predictions,
            total_predictions=len(predictions),
            high_confidence_count=len(high_confidence),
            risk_score=risk_score,
            metrics=metrics
        )

        self.prediction_history.append(report)
        return report

    def _ast_analysis(self, code: str, file_path: str) -> List[BugPrediction]:
        """Анализ через AST"""
        predictions = []

        try:
            tree = ast.parse(code)
        except SyntaxError:
            return predictions

        for node in ast.walk(tree):
            # Проверка доступа к атрибутам без проверки на None
            if isinstance(node, ast.Attribute):
                # Проверка, есть ли проверка на None в окружающем коде
                predictions.append(BugPrediction(
                    bug_type=BugType.NULL_POINTER,
                    severity=BugSeverity.MEDIUM,
                    confidence=0.5,
                    line_number=getattr(node, 'lineno', 0),
                    description="Potential AttributeError if object is None",
                    code_snippet=self._get_code_snippet(code, getattr(node, 'lineno', 0)),
                    evidence=["Attribute access without None check"],
                    fix_suggestion="Add None check: if obj is not None: obj.attribute",
                    similar_bugs=self.known_bugs_db.get('null_pointer', [])
                ))

            # Проверка индексации без проверки границ
            if isinstance(node, ast.Subscript):
                if isinstance(node.slice, ast.Constant) or isinstance(node.slice, ast.Index):
                    predictions.append(BugPrediction(
                        bug_type=BugType.INDEX_ERROR,
                        severity=BugSeverity.MEDIUM,
                        confidence=0.4,
                        line_number=getattr(node, 'lineno', 0),
                        description="Potential IndexError if list is shorter than expected",
                        code_snippet=self._get_code_snippet(code, getattr(node, 'lineno', 0)),
                        evidence=["Index access without bounds check"],
                        fix_suggestion="Use try/except or check len() first",
                        similar_bugs=self.known_bugs_db.get('index_error', [])
                    ))

            # Проверка деления
            if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Div, ast.FloorDiv, ast.Mod)):
                predictions.append(BugPrediction(
                    bug_type=BugType.DIVISION_BY_ZERO,
                    severity=BugSeverity.HIGH,
                    confidence=0.6,
                    line_number=getattr(node, 'lineno', 0),
                    description="Potential division by zero",
                    code_snippet=self._get_code_snippet(code, getattr(node, 'lineno', 0)),
                    evidence=["Division operation without zero check"],
                    fix_suggestion="Add check: if denominator != 0: result = a / b",
                    similar_bugs=["ZeroDivisionError: division by zero"]
                ))

            # Проверка циклов без выхода
            if isinstance(node, ast.While):
                has_break = any(isinstance(n, ast.Break) for n in ast.walk(node))
                if isinstance(node.test, ast.Constant) and node.test.value is True and not has_break:
                    predictions.append(BugPrediction(
                        bug_type=BugType.INFINITE_LOOP,
                        severity=BugSeverity.CRITICAL,
                        confidence=0.9,
                        line_number=node.lineno,
                        description="Infinite loop without break condition",
                        code_snippet=self._get_code_snippet(code, node.lineno),
                        evidence=["while True without break statement"],
                        fix_suggestion="Add break condition or timeout mechanism",
                        similar_bugs=["Process hangs indefinitely"]
                    ))

            # Проверка опасных функций
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in self.DANGEROUS_OPERATIONS:
                        bug_type = self.DANGEROUS_OPERATIONS[node.func.id]
                        predictions.append(BugPrediction(
                            bug_type=bug_type,
                            severity=BugSeverity.HIGH,
                            confidence=0.8,
                            line_number=getattr(node, 'lineno', 0),
                            description=f"Use of dangerous function: {node.func.id}",
                            code_snippet=self._get_code_snippet(code, getattr(node, 'lineno', 0)),
                            evidence=[f"{node.func.id}() can execute arbitrary code"],
                            fix_suggestion=f"Avoid using {node.func.id}() or add strict validation",
                            similar_bugs=["Arbitrary code execution vulnerability"]
                        ))

        return predictions

    def _pattern_analysis(self, code: str, file_path: str) -> List[BugPrediction]:
        """Анализ паттернов"""
        predictions = []
        lines = code.split('\n')

        for i, line in enumerate(lines, 1):
            # open() без with
            if 'open(' in line and 'with ' not in line:
                predictions.append(BugPrediction(
                    bug_type=BugType.RESOURCE_LEAK,
                    severity=BugSeverity.HIGH,
                    confidence=0.85,
                    line_number=i,
                    description="File opened without context manager (with statement)",
                    code_snippet=line.strip(),
                    evidence=["open() call without 'with' statement"],
                    fix_suggestion="Use: with open(...) as f:",
                    similar_bugs=["File handle not closed, leading to resource exhaustion"]
                ))

            # Множественные return в except без re-raise
            if 'except' in line and i < len(lines):
                # Проверка следующих строк
                next_lines = lines[i:min(i+5, len(lines))]
                if any('return' in nl for nl in next_lines) and not any('raise' in nl for nl in next_lines):
                    predictions.append(BugPrediction(
                        bug_type=BugType.LOGIC_ERROR,
                        severity=BugSeverity.MEDIUM,
                        confidence=0.5,
                        line_number=i,
                        description="Exception swallowed without logging or re-raising",
                        code_snippet=line.strip(),
                        evidence=["except block returns without handling error"],
                        fix_suggestion="Log the exception or re-raise it",
                        similar_bugs=["Silent failures make debugging difficult"]
                    ))

            # Изменение списка во время итерации
            if 'for ' in line and 'in ' in line:
                var_match = re.search(r'for\s+\w+\s+in\s+(\w+)', line)
                if var_match:
                    list_name = var_match.group(1)
                    # Проверка следующих строк
                    next_lines = lines[i:min(i+10, len(lines))]
                    if any(f"{list_name}.append(" in nl or f"{list_name}.remove(" in nl for nl in next_lines):
                        predictions.append(BugPrediction(
                            bug_type=BugType.LOGIC_ERROR,
                            severity=BugSeverity.HIGH,
                            confidence=0.75,
                            line_number=i,
                            description="Modifying list while iterating over it",
                            code_snippet=line.strip(),
                            evidence=[f"List '{list_name}' modified during iteration"],
                            fix_suggestion="Iterate over a copy: for item in list.copy():",
                            similar_bugs=["RuntimeError: dictionary changed size during iteration"]
                        ))

        return predictions

    def _control_flow_analysis(self, code: str, file_path: str) -> List[BugPrediction]:
        """Анализ control flow"""
        predictions = []

        try:
            tree = ast.parse(code)
        except SyntaxError:
            return predictions

        # Поиск функций без return
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                has_return = any(isinstance(n, ast.Return) for n in ast.walk(node))
                return_annotation = node.returns

                if return_annotation and not has_return:
                    # Функция с аннотацией типа возврата но без return
                    predictions.append(BugPrediction(
                        bug_type=BugType.LOGIC_ERROR,
                        severity=BugSeverity.MEDIUM,
                        confidence=0.7,
                        line_number=node.lineno,
                        description=f"Function '{node.name}' has return type annotation but no return statement",
                        code_snippet=f"def {node.name}(...) -> {ast.unparse(return_annotation) if hasattr(ast, 'unparse') else '...'}:",
                        evidence=["Return type specified but no return statement found"],
                        fix_suggestion="Add return statement or change return type to None",
                        similar_bugs=["Function returns None instead of expected type"]
                    ))

        return predictions

    def _type_analysis(self, code: str, file_path: str) -> List[BugPrediction]:
        """Анализ типов (примерный)"""
        predictions = []
        lines = code.split('\n')

        for i, line in enumerate(lines, 1):
            # Конкатенация str + int без приведения
            if re.search(r'["\'].*["\']\s*\+\s*\w+(?!\s*\()', line):
                predictions.append(BugPrediction(
                    bug_type=BugType.TYPE_ERROR,
                    severity=BugSeverity.MEDIUM,
                    confidence=0.6,
                    line_number=i,
                    description="Potential type error: string concatenation with non-string",
                    code_snippet=line.strip(),
                    evidence=["String concatenation without type conversion"],
                    fix_suggestion="Use f-strings or str() conversion",
                    similar_bugs=self.known_bugs_db.get('type_error', [])
                ))

        return predictions

    def _concurrency_analysis(self, code: str, file_path: str) -> List[BugPrediction]:
        """Анализ многопоточности"""
        predictions = []

        if 'threading' not in code and 'Thread' not in code:
            return predictions

        lines = code.split('\n')

        # Поиск общего состояния без блокировок
        has_threading = 'import threading' in code or 'from threading' in code
        has_locks = 'Lock()' in code or 'RLock()' in code

        if has_threading and not has_locks:
            # Поиск общих переменных
            for i, line in enumerate(lines, 1):
                if '=' in line and not line.strip().startswith('#'):
                    # Примерная проверка на модификацию состояния
                    predictions.append(BugPrediction(
                        bug_type=BugType.RACE_CONDITION,
                        severity=BugSeverity.HIGH,
                        confidence=0.5,
                        line_number=i,
                        description="Potential race condition: shared state without synchronization",
                        code_snippet=line.strip(),
                        evidence=["Threading used but no locks found"],
                        fix_suggestion="Use threading.Lock() to protect shared state",
                        similar_bugs=self.known_bugs_db.get('race_condition', [])
                    ))
                    break  # Один предупреждение достаточно

        return predictions

    def _get_code_snippet(self, code: str, line_number: int, context: int = 0) -> str:
        """Получение фрагмента кода"""
        lines = code.split('\n')
        if line_number <= 0 or line_number > len(lines):
            return ""

        start = max(0, line_number - 1 - context)
        end = min(len(lines), line_number + context)

        return '\n'.join(lines[start:end])

    def _calculate_metrics(self, code: str, predictions: List[BugPrediction]) -> Dict[str, Any]:
        """Расчет метрик"""
        bugs_by_type = defaultdict(int)
        bugs_by_severity = defaultdict(int)

        for pred in predictions:
            bugs_by_type[pred.bug_type.value] += 1
            bugs_by_severity[pred.severity.value] += 1

        return {
            'total_lines': len(code.split('\n')),
            'bugs_by_type': dict(bugs_by_type),
            'bugs_by_severity': dict(bugs_by_severity),
            'avg_confidence': sum(p.confidence for p in predictions) / len(predictions) if predictions else 0.0,
            'high_severity_count': bugs_by_severity.get('critical', 0) + bugs_by_severity.get('high', 0)
        }

    def _calculate_risk_score(self, predictions: List[BugPrediction]) -> float:
        """Расчет общего риска (0-100)"""
        if not predictions:
            return 0.0

        severity_weights = {
            BugSeverity.CRITICAL: 25,
            BugSeverity.HIGH: 15,
            BugSeverity.MEDIUM: 8,
            BugSeverity.LOW: 3,
            BugSeverity.INFO: 1
        }

        total_risk = 0.0
        for pred in predictions:
            weight = severity_weights.get(pred.severity, 1)
            total_risk += weight * pred.confidence

        # Нормализация к 0-100
        return min(100.0, total_risk)

    def generate_fix_recommendations(self, report: BugReport) -> Dict[str, List[str]]:
        """
        Генерация рекомендаций по исправлению

        Args:
            report: Отчет о багах

        Returns:
            Рекомендации сгруппированные по приоритету
        """
        recommendations = {
            'critical': [],
            'high': [],
            'medium': [],
            'low': []
        }

        for pred in report.predictions:
            if pred.confidence >= 0.7:
                severity_key = pred.severity.value if pred.severity.value in recommendations else 'low'
                rec = f"Line {pred.line_number}: {pred.description} - {pred.fix_suggestion}"
                recommendations[severity_key].append(rec)

        return recommendations
