#!/usr/bin/env python3
"""
Automated Code Reviewer

Автоматическое ревью кода с использованием статического анализа и AI.
"""

import ast
import re
from typing import Dict, List, Optional, Set, Any
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import json


class IssueSeverity(Enum):
    """Уровень серьезности проблемы"""
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class IssueCategory(Enum):
    """Категория проблемы"""
    SECURITY = "security"
    PERFORMANCE = "performance"
    CODE_QUALITY = "code_quality"
    BEST_PRACTICES = "best_practices"
    BUG_RISK = "bug_risk"
    MAINTAINABILITY = "maintainability"
    DOCUMENTATION = "documentation"


@dataclass
class CodeIssue:
    """Обнаруженная проблема в коде"""
    severity: IssueSeverity
    category: IssueCategory
    message: str
    file_path: str
    line_number: int
    code_snippet: str
    suggestion: str
    auto_fixable: bool = False
    fix_code: Optional[str] = None

    def to_dict(self) -> Dict:
        return {
            'severity': self.severity.value,
            'category': self.category.value,
            'message': self.message,
            'file_path': self.file_path,
            'line_number': self.line_number,
            'code_snippet': self.code_snippet,
            'suggestion': self.suggestion,
            'auto_fixable': self.auto_fixable,
            'fix_code': self.fix_code
        }


@dataclass
class ReviewResult:
    """Результат ревью кода"""
    file_path: str
    total_issues: int
    issues_by_severity: Dict[str, int]
    issues_by_category: Dict[str, int]
    issues: List[CodeIssue]
    quality_score: float  # 0-100
    metrics: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return {
            'file_path': self.file_path,
            'total_issues': self.total_issues,
            'issues_by_severity': self.issues_by_severity,
            'issues_by_category': self.issues_by_category,
            'quality_score': self.quality_score,
            'metrics': self.metrics,
            'issues': [issue.to_dict() for issue in self.issues]
        }


class CodeReviewer:
    """
    Automated Code Reviewer

    Выполняет автоматическое ревью Python кода с использованием:
    - Статического анализа (AST)
    - Паттерн-матчинга
    - Метрик сложности
    - Best practices проверок
    """

    # Опасные функции
    DANGEROUS_FUNCTIONS = {
        'eval', 'exec', 'compile', '__import__',
        'input', 'open'  # Потенциально опасны без валидации
    }

    # Паттерны небезопасного кода
    SECURITY_PATTERNS = {
        'sql_injection': [
            r'execute\s*\(\s*["\'].*%s',
            r'execute\s*\(\s*f["\']',
            r'execute\s*\(\s*.*\+\s*.*\)',
        ],
        'command_injection': [
            r'os\.system\s*\(',
            r'subprocess\..*shell\s*=\s*True',
        ],
        'hardcoded_secrets': [
            r'password\s*=\s*["\'][^"\']+["\']',
            r'api_key\s*=\s*["\'][^"\']+["\']',
            r'secret\s*=\s*["\'][^"\']+["\']',
            r'token\s*=\s*["\'][^"\']+["\']',
        ],
        'weak_crypto': [
            r'hashlib\.md5',
            r'hashlib\.sha1',
        ]
    }

    # Антипаттерны производительности
    PERFORMANCE_ANTIPATTERNS = {
        'list_comprehension_in_loop': r'for\s+\w+\s+in\s+.*:\s*\[.*for.*in',
        'repeated_calculation': r'for\s+.*:\s*.*len\(',
        'string_concatenation_in_loop': r'for\s+.*:\s*\w+\s*\+=\s*["\']',
    }

    def __init__(self, strict_mode: bool = False):
        """
        Инициализация ревьюера

        Args:
            strict_mode: Если True, более строгие проверки
        """
        self.strict_mode = strict_mode
        self.custom_rules: List[Dict] = []

    def review_file(self, file_path: str) -> ReviewResult:
        """
        Ревью одного файла

        Args:
            file_path: Путь к файлу

        Returns:
            Результат ревью
        """
        file_path_obj = Path(file_path)
        if not file_path_obj.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()

        return self.review_code(code, str(file_path))

    def review_code(self, code: str, file_path: str = "unknown") -> ReviewResult:
        """
        Ревью кода

        Args:
            code: Код для анализа
            file_path: Путь к файлу (для отчета)

        Returns:
            Результат ревью
        """
        issues: List[CodeIssue] = []

        # 1. Статический анализ через AST
        issues.extend(self._ast_analysis(code, file_path))

        # 2. Проверка безопасности
        issues.extend(self._security_check(code, file_path))

        # 3. Проверка производительности
        issues.extend(self._performance_check(code, file_path))

        # 4. Проверка качества кода
        issues.extend(self._quality_check(code, file_path))

        # 5. Проверка документации
        issues.extend(self._documentation_check(code, file_path))

        # 6. Кастомные правила
        issues.extend(self._custom_rules_check(code, file_path))

        # Подсчет метрик
        metrics = self._calculate_metrics(code)

        # Группировка по серьезности и категории
        issues_by_severity = {}
        issues_by_category = {}

        for issue in issues:
            severity = issue.severity.value
            category = issue.category.value
            issues_by_severity[severity] = issues_by_severity.get(severity, 0) + 1
            issues_by_category[category] = issues_by_category.get(category, 0) + 1

        # Расчет общей оценки качества
        quality_score = self._calculate_quality_score(issues, metrics)

        return ReviewResult(
            file_path=file_path,
            total_issues=len(issues),
            issues_by_severity=issues_by_severity,
            issues_by_category=issues_by_category,
            issues=issues,
            quality_score=quality_score,
            metrics=metrics
        )

    def _ast_analysis(self, code: str, file_path: str) -> List[CodeIssue]:
        """Анализ через Abstract Syntax Tree"""
        issues = []

        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            return [CodeIssue(
                severity=IssueSeverity.CRITICAL,
                category=IssueCategory.BUG_RISK,
                message=f"Syntax error: {e.msg}",
                file_path=file_path,
                line_number=e.lineno or 0,
                code_snippet="",
                suggestion="Fix syntax error"
            )]

        for node in ast.walk(tree):
            # Проверка опасных функций
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in self.DANGEROUS_FUNCTIONS:
                        issues.append(CodeIssue(
                            severity=IssueSeverity.HIGH,
                            category=IssueCategory.SECURITY,
                            message=f"Use of dangerous function: {node.func.id}()",
                            file_path=file_path,
                            line_number=getattr(node, 'lineno', 0),
                            code_snippet=f"{node.func.id}(...)",
                            suggestion=f"Avoid using {node.func.id}() or add proper validation"
                        ))

            # Проверка слишком сложных функций
            if isinstance(node, ast.FunctionDef):
                complexity = self._calculate_complexity(node)
                if complexity > 10:
                    issues.append(CodeIssue(
                        severity=IssueSeverity.MEDIUM,
                        category=IssueCategory.MAINTAINABILITY,
                        message=f"Function '{node.name}' is too complex (complexity: {complexity})",
                        file_path=file_path,
                        line_number=node.lineno,
                        code_snippet=f"def {node.name}(...)",
                        suggestion="Consider breaking down into smaller functions"
                    ))

                # Проверка отсутствия docstring
                if not ast.get_docstring(node):
                    severity = IssueSeverity.MEDIUM if self.strict_mode else IssueSeverity.LOW
                    issues.append(CodeIssue(
                        severity=severity,
                        category=IssueCategory.DOCUMENTATION,
                        message=f"Function '{node.name}' missing docstring",
                        file_path=file_path,
                        line_number=node.lineno,
                        code_snippet=f"def {node.name}(...)",
                        suggestion="Add docstring explaining purpose, args, and return value"
                    ))

            # Проверка слишком длинных классов
            if isinstance(node, ast.ClassDef):
                method_count = sum(1 for n in node.body if isinstance(n, ast.FunctionDef))
                if method_count > 20:
                    issues.append(CodeIssue(
                        severity=IssueSeverity.MEDIUM,
                        category=IssueCategory.MAINTAINABILITY,
                        message=f"Class '{node.name}' has too many methods ({method_count})",
                        file_path=file_path,
                        line_number=node.lineno,
                        code_snippet=f"class {node.name}:",
                        suggestion="Consider splitting into multiple classes"
                    ))

            # Проверка bare except
            if isinstance(node, ast.ExceptHandler):
                if node.type is None:
                    issues.append(CodeIssue(
                        severity=IssueSeverity.MEDIUM,
                        category=IssueCategory.BEST_PRACTICES,
                        message="Bare 'except:' clause",
                        file_path=file_path,
                        line_number=node.lineno,
                        code_snippet="except:",
                        suggestion="Catch specific exceptions instead of bare except"
                    ))

        return issues

    def _security_check(self, code: str, file_path: str) -> List[CodeIssue]:
        """Проверка безопасности"""
        issues = []
        lines = code.split('\n')

        for pattern_type, patterns in self.SECURITY_PATTERNS.items():
            for pattern in patterns:
                for line_num, line in enumerate(lines, 1):
                    if re.search(pattern, line):
                        issues.append(CodeIssue(
                            severity=IssueSeverity.HIGH,
                            category=IssueCategory.SECURITY,
                            message=f"Potential {pattern_type.replace('_', ' ')} vulnerability",
                            file_path=file_path,
                            line_number=line_num,
                            code_snippet=line.strip(),
                            suggestion=self._get_security_suggestion(pattern_type)
                        ))

        return issues

    def _performance_check(self, code: str, file_path: str) -> List[CodeIssue]:
        """Проверка производительности"""
        issues = []
        lines = code.split('\n')

        for antipattern, pattern in self.PERFORMANCE_ANTIPATTERNS.items():
            for line_num, line in enumerate(lines, 1):
                if re.search(pattern, line):
                    issues.append(CodeIssue(
                        severity=IssueSeverity.MEDIUM,
                        category=IssueCategory.PERFORMANCE,
                        message=f"Performance antipattern: {antipattern.replace('_', ' ')}",
                        file_path=file_path,
                        line_number=line_num,
                        code_snippet=line.strip(),
                        suggestion=self._get_performance_suggestion(antipattern)
                    ))

        return issues

    def _quality_check(self, code: str, file_path: str) -> List[CodeIssue]:
        """Проверка качества кода"""
        issues = []
        lines = code.split('\n')

        for line_num, line in enumerate(lines, 1):
            # Проверка длины строки
            if len(line) > 120:
                issues.append(CodeIssue(
                    severity=IssueSeverity.LOW,
                    category=IssueCategory.CODE_QUALITY,
                    message=f"Line too long ({len(line)} > 120 characters)",
                    file_path=file_path,
                    line_number=line_num,
                    code_snippet=line[:50] + "...",
                    suggestion="Break into multiple lines"
                ))

            # Проверка множественных пробелов
            if '  ' in line and not line.strip().startswith('#'):
                issues.append(CodeIssue(
                    severity=IssueSeverity.LOW,
                    category=IssueCategory.CODE_QUALITY,
                    message="Multiple consecutive spaces",
                    file_path=file_path,
                    line_number=line_num,
                    code_snippet=line.strip(),
                    suggestion="Use single spaces"
                ))

        return issues

    def _documentation_check(self, code: str, file_path: str) -> List[CodeIssue]:
        """Проверка документации"""
        issues = []

        try:
            tree = ast.parse(code)
        except:
            return issues

        # Проверка module docstring
        module_docstring = ast.get_docstring(tree)
        if not module_docstring and self.strict_mode:
            issues.append(CodeIssue(
                severity=IssueSeverity.LOW,
                category=IssueCategory.DOCUMENTATION,
                message="Module missing docstring",
                file_path=file_path,
                line_number=1,
                code_snippet="",
                suggestion="Add module-level docstring"
            ))

        return issues

    def _custom_rules_check(self, code: str, file_path: str) -> List[CodeIssue]:
        """Проверка кастомных правил"""
        issues = []

        for rule in self.custom_rules:
            pattern = rule.get('pattern')
            if not pattern:
                continue

            lines = code.split('\n')
            for line_num, line in enumerate(lines, 1):
                if re.search(pattern, line):
                    issues.append(CodeIssue(
                        severity=IssueSeverity(rule.get('severity', 'low')),
                        category=IssueCategory(rule.get('category', 'code_quality')),
                        message=rule.get('message', 'Custom rule violation'),
                        file_path=file_path,
                        line_number=line_num,
                        code_snippet=line.strip(),
                        suggestion=rule.get('suggestion', 'Fix the issue')
                    ))

        return issues

    def _calculate_complexity(self, node: ast.FunctionDef) -> int:
        """Расчет цикломатической сложности функции"""
        complexity = 1

        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1

        return complexity

    def _calculate_metrics(self, code: str) -> Dict[str, Any]:
        """Расчет метрик кода"""
        lines = code.split('\n')
        loc = len(lines)
        blank_lines = sum(1 for line in lines if not line.strip())
        comment_lines = sum(1 for line in lines if line.strip().startswith('#'))
        code_lines = loc - blank_lines - comment_lines

        try:
            tree = ast.parse(code)
            functions = sum(1 for _ in ast.walk(tree) if isinstance(_, ast.FunctionDef))
            classes = sum(1 for _ in ast.walk(tree) if isinstance(_, ast.ClassDef))
        except:
            functions = 0
            classes = 0

        return {
            'total_lines': loc,
            'code_lines': code_lines,
            'blank_lines': blank_lines,
            'comment_lines': comment_lines,
            'functions': functions,
            'classes': classes,
            'avg_line_length': sum(len(line) for line in lines) / loc if loc > 0 else 0
        }

    def _calculate_quality_score(self, issues: List[CodeIssue], metrics: Dict) -> float:
        """Расчет общей оценки качества (0-100)"""
        base_score = 100.0

        # Штрафы за проблемы
        severity_penalties = {
            IssueSeverity.CRITICAL: 20,
            IssueSeverity.HIGH: 10,
            IssueSeverity.MEDIUM: 5,
            IssueSeverity.LOW: 2,
            IssueSeverity.INFO: 1
        }

        for issue in issues:
            penalty = severity_penalties.get(issue.severity, 1)
            base_score -= penalty

        # Бонусы за хорошие метрики
        code_lines = metrics.get('code_lines', 0)
        comment_lines = metrics.get('comment_lines', 0)

        if code_lines > 0:
            comment_ratio = comment_lines / code_lines
            if comment_ratio > 0.1:  # > 10% комментариев
                base_score += 5

        return max(0.0, min(100.0, base_score))

    def _get_security_suggestion(self, pattern_type: str) -> str:
        """Получение рекомендации по безопасности"""
        suggestions = {
            'sql_injection': "Use parameterized queries with placeholders instead of string formatting",
            'command_injection': "Avoid shell=True, use subprocess with list arguments",
            'hardcoded_secrets': "Use environment variables or secret management system",
            'weak_crypto': "Use SHA-256 or stronger hashing algorithms"
        }
        return suggestions.get(pattern_type, "Review security implications")

    def _get_performance_suggestion(self, antipattern: str) -> str:
        """Получение рекомендации по производительности"""
        suggestions = {
            'list_comprehension_in_loop': "Move comprehension outside loop or use generator",
            'repeated_calculation': "Calculate length once before loop",
            'string_concatenation_in_loop': "Use list and ''.join() instead"
        }
        return suggestions.get(antipattern, "Optimize this code pattern")

    def add_custom_rule(self, pattern: str, severity: str, category: str,
                       message: str, suggestion: str):
        """
        Добавление кастомного правила

        Args:
            pattern: Regex паттерн
            severity: Уровень серьезности
            category: Категория
            message: Сообщение об ошибке
            suggestion: Рекомендация по исправлению
        """
        self.custom_rules.append({
            'pattern': pattern,
            'severity': severity,
            'category': category,
            'message': message,
            'suggestion': suggestion
        })

    def review_project(self, project_path: str, extensions: List[str] = None) -> Dict[str, ReviewResult]:
        """
        Ревью всего проекта

        Args:
            project_path: Путь к проекту
            extensions: Расширения файлов для проверки (по умолчанию ['.py'])

        Returns:
            Словарь результатов по файлам
        """
        if extensions is None:
            extensions = ['.py']

        results = {}
        project_path_obj = Path(project_path)

        for ext in extensions:
            for file_path in project_path_obj.rglob(f'*{ext}'):
                if '__pycache__' in str(file_path) or '.venv' in str(file_path):
                    continue

                try:
                    result = self.review_file(str(file_path))
                    results[str(file_path)] = result
                except Exception as e:
                    print(f"Error reviewing {file_path}: {e}")

        return results

    def generate_report(self, results: Dict[str, ReviewResult], output_format: str = 'text') -> str:
        """
        Генерация отчета

        Args:
            results: Результаты ревью (может быть один ReviewResult или словарь)
            output_format: Формат ('text', 'json', 'markdown')

        Returns:
            Отчет в выбранном формате
        """
        if isinstance(results, ReviewResult):
            results = {results.file_path: results}

        if output_format == 'json':
            return json.dumps(
                {path: result.to_dict() for path, result in results.items()},
                indent=2
            )
        elif output_format == 'markdown':
            return self._generate_markdown_report(results)
        else:
            return self._generate_text_report(results)

    def _generate_text_report(self, results: Dict[str, ReviewResult]) -> str:
        """Генерация текстового отчета"""
        report_lines = ["=" * 70, "CODE REVIEW REPORT", "=" * 70, ""]

        total_issues = sum(r.total_issues for r in results.values())
        avg_quality = sum(r.quality_score for r in results.values()) / len(results) if results else 0

        report_lines.append(f"Files reviewed: {len(results)}")
        report_lines.append(f"Total issues: {total_issues}")
        report_lines.append(f"Average quality score: {avg_quality:.1f}/100")
        report_lines.append("")

        for file_path, result in results.items():
            report_lines.append(f"\n{'=' * 70}")
            report_lines.append(f"File: {file_path}")
            report_lines.append(f"Quality Score: {result.quality_score:.1f}/100")
            report_lines.append(f"Issues: {result.total_issues}")
            report_lines.append("")

            for issue in result.issues:
                severity_icon = {
                    IssueSeverity.CRITICAL: "🔴",
                    IssueSeverity.HIGH: "🟠",
                    IssueSeverity.MEDIUM: "🟡",
                    IssueSeverity.LOW: "🔵",
                    IssueSeverity.INFO: "⚪"
                }.get(issue.severity, "")

                report_lines.append(f"{severity_icon} Line {issue.line_number}: {issue.message}")
                report_lines.append(f"   Category: {issue.category.value}")
                report_lines.append(f"   Code: {issue.code_snippet}")
                report_lines.append(f"   💡 {issue.suggestion}")
                report_lines.append("")

        return "\n".join(report_lines)

    def _generate_markdown_report(self, results: Dict[str, ReviewResult]) -> str:
        """Генерация Markdown отчета"""
        lines = ["# Code Review Report\n"]

        total_issues = sum(r.total_issues for r in results.values())
        avg_quality = sum(r.quality_score for r in results.values()) / len(results) if results else 0

        lines.append("## Summary\n")
        lines.append(f"- **Files reviewed:** {len(results)}")
        lines.append(f"- **Total issues:** {total_issues}")
        lines.append(f"- **Average quality score:** {avg_quality:.1f}/100\n")

        for file_path, result in results.items():
            lines.append(f"\n## {file_path}\n")
            lines.append(f"**Quality Score:** {result.quality_score:.1f}/100\n")
            lines.append(f"**Issues:** {result.total_issues}\n")

            if result.issues:
                lines.append("### Issues\n")
                for issue in result.issues:
                    lines.append(f"#### Line {issue.line_number}: {issue.message}\n")
                    lines.append(f"- **Severity:** {issue.severity.value}")
                    lines.append(f"- **Category:** {issue.category.value}")
                    lines.append(f"- **Code:** `{issue.code_snippet}`")
                    lines.append(f"- **Suggestion:** {issue.suggestion}\n")

        return "\n".join(lines)
