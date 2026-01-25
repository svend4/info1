#!/usr/bin/env python3
"""
AI Code Review Assistant

Automated code review с intelligent suggestions, best practices, и security analysis.
"""

import ast
import re
import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Set, Tuple


class ReviewSeverity(Enum):
    """Review Issue Severity"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ReviewCategory(Enum):
    """Review Category"""
    SECURITY = "security"
    PERFORMANCE = "performance"
    MAINTAINABILITY = "maintainability"
    STYLE = "style"
    BUGS = "bugs"
    BEST_PRACTICES = "best_practices"
    DOCUMENTATION = "documentation"


@dataclass
class ReviewIssue:
    """Code Review Issue"""
    severity: ReviewSeverity
    category: ReviewCategory
    title: str
    description: str
    file_path: str
    line: int
    column: int = 0
    code_snippet: str = ""
    suggestion: Optional[str] = None
    auto_fixable: bool = False
    references: List[str] = field(default_factory=list)


@dataclass
class ReviewSuggestion:
    """Code Improvement Suggestion"""
    title: str
    description: str
    before: str
    after: str
    impact: str  # High, Medium, Low
    category: ReviewCategory


@dataclass
class CodeReviewResult:
    """Code Review Result"""
    file_path: str
    issues: List[ReviewIssue] = field(default_factory=list)
    suggestions: List[ReviewSuggestion] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)
    score: float = 0.0  # 0-100
    reviewed_at: datetime = field(default_factory=datetime.now)


class CodeReviewAssistant:
    """AI-Powered Code Review Assistant"""

    def __init__(self, model: str = "gpt-4"):
        """
        Initialize code review assistant

        Args:
            model: AI model to use
        """
        self.model = model
        self.rules: Dict[ReviewCategory, List[Callable]] = {}
        self._setup_rules()

    def _setup_rules(self):
        """Setup review rules"""
        self.rules = {
            ReviewCategory.SECURITY: [
                self._check_sql_injection,
                self._check_command_injection,
                self._check_hardcoded_secrets,
                self._check_unsafe_deserialization,
            ],
            ReviewCategory.PERFORMANCE: [
                self._check_inefficient_loops,
                self._check_unnecessary_copies,
                self._check_string_concatenation,
            ],
            ReviewCategory.MAINTAINABILITY: [
                self._check_function_complexity,
                self._check_duplicate_code,
                self._check_long_functions,
            ],
            ReviewCategory.STYLE: [
                self._check_naming_conventions,
                self._check_line_length,
                self._check_imports_order,
            ],
            ReviewCategory.BUGS: [
                self._check_exception_handling,
                self._check_resource_leaks,
                self._check_null_pointer,
            ],
            ReviewCategory.BEST_PRACTICES: [
                self._check_type_hints,
                self._check_docstrings,
                self._check_test_coverage,
            ],
        }

    def review_file(self, file_path: Path) -> CodeReviewResult:
        """
        Review single file

        Args:
            file_path: Path to file

        Returns:
            Review result
        """
        print(f"🔍 Reviewing file: {file_path}")

        result = CodeReviewResult(file_path=str(file_path))

        # Read file
        try:
            code = file_path.read_text()
        except Exception as e:
            result.issues.append(ReviewIssue(
                severity=ReviewSeverity.ERROR,
                category=ReviewCategory.BUGS,
                title="File Read Error",
                description=f"Cannot read file: {e}",
                file_path=str(file_path),
                line=0
            ))
            return result

        # Parse code
        lines = code.split('\n')

        # Run all review rules
        for category, rules in self.rules.items():
            for rule in rules:
                issues = rule(file_path, code, lines)
                result.issues.extend(issues)

        # Calculate metrics
        result.metrics = self._calculate_metrics(code, lines)

        # Calculate score
        result.score = self._calculate_score(result)

        # Generate suggestions
        result.suggestions = self._generate_suggestions(result)

        print(f"✅ Review complete: {len(result.issues)} issues, score: {result.score:.1f}/100")

        return result

    def review_diff(self, diff_text: str) -> CodeReviewResult:
        """
        Review git diff

        Args:
            diff_text: Git diff text

        Returns:
            Review result
        """
        print("🔍 Reviewing diff...")

        result = CodeReviewResult(file_path="diff")

        # Parse diff
        added_lines = []
        removed_lines = []
        current_line = 0

        for line in diff_text.split('\n'):
            if line.startswith('@@'):
                # Extract line number
                match = re.search(r'\+(\d+)', line)
                if match:
                    current_line = int(match.group(1))

            elif line.startswith('+') and not line.startswith('+++'):
                added_lines.append((current_line, line[1:]))
                current_line += 1

            elif line.startswith('-') and not line.startswith('---'):
                removed_lines.append((current_line, line[1:]))

        # Review added lines
        for line_num, line_text in added_lines:
            # Check for common issues
            if 'password' in line_text.lower() and '=' in line_text:
                result.issues.append(ReviewIssue(
                    severity=ReviewSeverity.CRITICAL,
                    category=ReviewCategory.SECURITY,
                    title="Potential Hardcoded Password",
                    description="Password appears to be hardcoded",
                    file_path="diff",
                    line=line_num,
                    code_snippet=line_text,
                    suggestion="Use environment variables or secure vault"
                ))

            if 'TODO' in line_text or 'FIXME' in line_text:
                result.issues.append(ReviewIssue(
                    severity=ReviewSeverity.WARNING,
                    category=ReviewCategory.MAINTAINABILITY,
                    title="TODO Comment",
                    description="Code contains TODO/FIXME comment",
                    file_path="diff",
                    line=line_num,
                    code_snippet=line_text
                ))

        result.score = self._calculate_score(result)

        print(f"✅ Diff review complete: {len(result.issues)} issues")

        return result

    # Security checks
    def _check_sql_injection(
        self,
        file_path: Path,
        code: str,
        lines: List[str]
    ) -> List[ReviewIssue]:
        """Check for SQL injection vulnerabilities"""
        issues = []

        # Look for string concatenation with SQL queries
        sql_keywords = ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'DROP']

        for i, line in enumerate(lines):
            for keyword in sql_keywords:
                if keyword in line.upper():
                    # Check for string formatting
                    if '%s' in line or '.format(' in line or 'f"' in line or "f'" in line:
                        issues.append(ReviewIssue(
                            severity=ReviewSeverity.CRITICAL,
                            category=ReviewCategory.SECURITY,
                            title="Potential SQL Injection",
                            description="SQL query uses string formatting, vulnerable to injection",
                            file_path=str(file_path),
                            line=i + 1,
                            code_snippet=line.strip(),
                            suggestion="Use parameterized queries with placeholders",
                            references=[
                                "https://owasp.org/www-community/attacks/SQL_Injection"
                            ]
                        ))

        return issues

    def _check_command_injection(
        self,
        file_path: Path,
        code: str,
        lines: List[str]
    ) -> List[ReviewIssue]:
        """Check for command injection vulnerabilities"""
        issues = []

        dangerous_functions = ['os.system', 'subprocess.call', 'eval', 'exec']

        for i, line in enumerate(lines):
            for func in dangerous_functions:
                if func in line:
                    issues.append(ReviewIssue(
                        severity=ReviewSeverity.CRITICAL,
                        category=ReviewCategory.SECURITY,
                        title="Dangerous Function Usage",
                        description=f"Use of {func} can lead to command injection",
                        file_path=str(file_path),
                        line=i + 1,
                        code_snippet=line.strip(),
                        suggestion="Use safer alternatives with input validation",
                        references=[
                            "https://owasp.org/www-community/attacks/Command_Injection"
                        ]
                    ))

        return issues

    def _check_hardcoded_secrets(
        self,
        file_path: Path,
        code: str,
        lines: List[str]
    ) -> List[ReviewIssue]:
        """Check for hardcoded secrets"""
        issues = []

        secret_patterns = [
            (r'password\s*=\s*["\'][\w@#$%^&*]+["\']', 'Password'),
            (r'api_key\s*=\s*["\'][\w-]+["\']', 'API Key'),
            (r'secret\s*=\s*["\'][\w-]+["\']', 'Secret'),
            (r'token\s*=\s*["\'][\w.-]+["\']', 'Token'),
        ]

        for i, line in enumerate(lines):
            for pattern, secret_type in secret_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    issues.append(ReviewIssue(
                        severity=ReviewSeverity.CRITICAL,
                        category=ReviewCategory.SECURITY,
                        title=f"Hardcoded {secret_type}",
                        description=f"{secret_type} appears to be hardcoded",
                        file_path=str(file_path),
                        line=i + 1,
                        code_snippet=line.strip(),
                        suggestion="Use environment variables or secret management service",
                        auto_fixable=False
                    ))

        return issues

    def _check_unsafe_deserialization(
        self,
        file_path: Path,
        code: str,
        lines: List[str]
    ) -> List[ReviewIssue]:
        """Check for unsafe deserialization"""
        issues = []

        for i, line in enumerate(lines):
            if 'pickle.loads' in line or 'yaml.load(' in line:
                issues.append(ReviewIssue(
                    severity=ReviewSeverity.CRITICAL,
                    category=ReviewCategory.SECURITY,
                    title="Unsafe Deserialization",
                    description="Deserialization can execute arbitrary code",
                    file_path=str(file_path),
                    line=i + 1,
                    code_snippet=line.strip(),
                    suggestion="Use yaml.safe_load() or validate input"
                ))

        return issues

    # Performance checks
    def _check_inefficient_loops(
        self,
        file_path: Path,
        code: str,
        lines: List[str]
    ) -> List[ReviewIssue]:
        """Check for inefficient loops"""
        issues = []

        for i, line in enumerate(lines):
            # Nested loops
            if 'for ' in line:
                # Check next lines for nested for
                for j in range(i + 1, min(i + 10, len(lines))):
                    if 'for ' in lines[j]:
                        indent_current = len(line) - len(line.lstrip())
                        indent_next = len(lines[j]) - len(lines[j].lstrip())

                        if indent_next > indent_current:
                            issues.append(ReviewIssue(
                                severity=ReviewSeverity.WARNING,
                                category=ReviewCategory.PERFORMANCE,
                                title="Nested Loops",
                                description="Nested loops can be inefficient for large datasets",
                                file_path=str(file_path),
                                line=i + 1,
                                code_snippet=line.strip(),
                                suggestion="Consider using list comprehensions or vectorization"
                            ))
                            break

        return issues

    def _check_unnecessary_copies(
        self,
        file_path: Path,
        code: str,
        lines: List[str]
    ) -> List[ReviewIssue]:
        """Check for unnecessary copies"""
        issues = []

        for i, line in enumerate(lines):
            if '.copy()' in line and 'return' not in line:
                issues.append(ReviewIssue(
                    severity=ReviewSeverity.INFO,
                    category=ReviewCategory.PERFORMANCE,
                    title="Unnecessary Copy",
                    description="Creating copy may not be necessary",
                    file_path=str(file_path),
                    line=i + 1,
                    code_snippet=line.strip(),
                    suggestion="Review if copy is needed"
                ))

        return issues

    def _check_string_concatenation(
        self,
        file_path: Path,
        code: str,
        lines: List[str]
    ) -> List[ReviewIssue]:
        """Check for inefficient string concatenation"""
        issues = []

        for i, line in enumerate(lines):
            # String concatenation in loop
            if 'for ' in line:
                for j in range(i + 1, min(i + 10, len(lines))):
                    if '+=' in lines[j] and ('str' in lines[j] or '"' in lines[j] or "'" in lines[j]):
                        issues.append(ReviewIssue(
                            severity=ReviewSeverity.WARNING,
                            category=ReviewCategory.PERFORMANCE,
                            title="Inefficient String Concatenation",
                            description="String concatenation in loop is inefficient",
                            file_path=str(file_path),
                            line=j + 1,
                            code_snippet=lines[j].strip(),
                            suggestion="Use list.append() and ''.join() instead"
                        ))
                        break

        return issues

    # Maintainability checks
    def _check_function_complexity(
        self,
        file_path: Path,
        code: str,
        lines: List[str]
    ) -> List[ReviewIssue]:
        """Check function complexity"""
        issues = []

        try:
            tree = ast.parse(code)

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Count branches (if, for, while, etc.)
                    branches = sum(1 for _ in ast.walk(node) if isinstance(_, (ast.If, ast.For, ast.While)))

                    if branches > 10:
                        issues.append(ReviewIssue(
                            severity=ReviewSeverity.WARNING,
                            category=ReviewCategory.MAINTAINABILITY,
                            title="High Complexity",
                            description=f"Function '{node.name}' has high cyclomatic complexity ({branches} branches)",
                            file_path=str(file_path),
                            line=node.lineno,
                            suggestion="Consider breaking function into smaller functions"
                        ))

        except SyntaxError:
            pass

        return issues

    def _check_duplicate_code(
        self,
        file_path: Path,
        code: str,
        lines: List[str]
    ) -> List[ReviewIssue]:
        """Check for duplicate code blocks"""
        issues = []

        # Simple duplicate detection (3+ identical lines)
        line_counts: Dict[str, List[int]] = {}

        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped and not stripped.startswith('#'):
                if stripped not in line_counts:
                    line_counts[stripped] = []
                line_counts[stripped].append(i + 1)

        for line_text, line_nums in line_counts.items():
            if len(line_nums) >= 3:
                issues.append(ReviewIssue(
                    severity=ReviewSeverity.INFO,
                    category=ReviewCategory.MAINTAINABILITY,
                    title="Duplicate Code",
                    description=f"Identical line appears {len(line_nums)} times",
                    file_path=str(file_path),
                    line=line_nums[0],
                    code_snippet=line_text,
                    suggestion="Consider extracting to a variable or function"
                ))

        return issues

    def _check_long_functions(
        self,
        file_path: Path,
        code: str,
        lines: List[str]
    ) -> List[ReviewIssue]:
        """Check for overly long functions"""
        issues = []

        try:
            tree = ast.parse(code)

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Find end line
                    end_line = node.lineno
                    for child in ast.walk(node):
                        if hasattr(child, 'lineno'):
                            end_line = max(end_line, child.lineno)

                    length = end_line - node.lineno

                    if length > 50:
                        issues.append(ReviewIssue(
                            severity=ReviewSeverity.WARNING,
                            category=ReviewCategory.MAINTAINABILITY,
                            title="Long Function",
                            description=f"Function '{node.name}' is {length} lines long",
                            file_path=str(file_path),
                            line=node.lineno,
                            suggestion="Consider breaking into smaller functions"
                        ))

        except SyntaxError:
            pass

        return issues

    # Style checks
    def _check_naming_conventions(
        self,
        file_path: Path,
        code: str,
        lines: List[str]
    ) -> List[ReviewIssue]:
        """Check naming conventions"""
        issues = []

        try:
            tree = ast.parse(code)

            for node in ast.walk(tree):
                # Class names should be CamelCase
                if isinstance(node, ast.ClassDef):
                    if not node.name[0].isupper():
                        issues.append(ReviewIssue(
                            severity=ReviewSeverity.INFO,
                            category=ReviewCategory.STYLE,
                            title="Naming Convention",
                            description=f"Class '{node.name}' should use CamelCase",
                            file_path=str(file_path),
                            line=node.lineno,
                            auto_fixable=True
                        ))

                # Function names should be snake_case
                elif isinstance(node, ast.FunctionDef):
                    if any(c.isupper() for c in node.name):
                        issues.append(ReviewIssue(
                            severity=ReviewSeverity.INFO,
                            category=ReviewCategory.STYLE,
                            title="Naming Convention",
                            description=f"Function '{node.name}' should use snake_case",
                            file_path=str(file_path),
                            line=node.lineno,
                            auto_fixable=True
                        ))

        except SyntaxError:
            pass

        return issues

    def _check_line_length(
        self,
        file_path: Path,
        code: str,
        lines: List[str]
    ) -> List[ReviewIssue]:
        """Check line length"""
        issues = []

        max_length = 100

        for i, line in enumerate(lines):
            if len(line) > max_length:
                issues.append(ReviewIssue(
                    severity=ReviewSeverity.INFO,
                    category=ReviewCategory.STYLE,
                    title="Line Too Long",
                    description=f"Line exceeds {max_length} characters ({len(line)} chars)",
                    file_path=str(file_path),
                    line=i + 1,
                    auto_fixable=True
                ))

        return issues

    def _check_imports_order(
        self,
        file_path: Path,
        code: str,
        lines: List[str]
    ) -> List[ReviewIssue]:
        """Check import order"""
        issues = []

        # Imports should be: stdlib, third-party, local
        # For simplicity, just check if imports are at top

        import_lines = []
        code_started = False

        for i, line in enumerate(lines):
            stripped = line.strip()

            if stripped and not stripped.startswith('#'):
                if stripped.startswith('import ') or stripped.startswith('from '):
                    if code_started:
                        issues.append(ReviewIssue(
                            severity=ReviewSeverity.INFO,
                            category=ReviewCategory.STYLE,
                            title="Import Not at Top",
                            description="Imports should be at the top of the file",
                            file_path=str(file_path),
                            line=i + 1,
                            code_snippet=stripped,
                            auto_fixable=True
                        ))
                    import_lines.append(i)
                else:
                    code_started = True

        return issues

    # Bug checks
    def _check_exception_handling(
        self,
        file_path: Path,
        code: str,
        lines: List[str]
    ) -> List[ReviewIssue]:
        """Check exception handling"""
        issues = []

        for i, line in enumerate(lines):
            # Bare except
            if line.strip() == 'except:':
                issues.append(ReviewIssue(
                    severity=ReviewSeverity.WARNING,
                    category=ReviewCategory.BUGS,
                    title="Bare Except Clause",
                    description="Bare except catches all exceptions including system exit",
                    file_path=str(file_path),
                    line=i + 1,
                    code_snippet=line.strip(),
                    suggestion="Specify exception type or use 'except Exception:'",
                    auto_fixable=True
                ))

            # Empty except
            if 'except' in line and i + 1 < len(lines):
                next_line = lines[i + 1].strip()
                if next_line == 'pass':
                    issues.append(ReviewIssue(
                        severity=ReviewSeverity.WARNING,
                        category=ReviewCategory.BUGS,
                        title="Silent Exception",
                        description="Exception is silently ignored",
                        file_path=str(file_path),
                        line=i + 1,
                        suggestion="Log the exception or handle it properly"
                    ))

        return issues

    def _check_resource_leaks(
        self,
        file_path: Path,
        code: str,
        lines: List[str]
    ) -> List[ReviewIssue]:
        """Check for resource leaks"""
        issues = []

        for i, line in enumerate(lines):
            # File opened without context manager
            if 'open(' in line and 'with ' not in line:
                issues.append(ReviewIssue(
                    severity=ReviewSeverity.WARNING,
                    category=ReviewCategory.BUGS,
                    title="Potential Resource Leak",
                    description="File opened without context manager may not be closed",
                    file_path=str(file_path),
                    line=i + 1,
                    code_snippet=line.strip(),
                    suggestion="Use 'with open() as f:' to ensure file is closed",
                    auto_fixable=True
                ))

        return issues

    def _check_null_pointer(
        self,
        file_path: Path,
        code: str,
        lines: List[str]
    ) -> List[ReviewIssue]:
        """Check for potential null pointer issues"""
        issues = []

        for i, line in enumerate(lines):
            # Accessing attribute without None check
            if '.get(' not in line and ' is not None' not in line:
                # Look for potential None access
                if re.search(r'\w+\.\w+', line) and '=' in line:
                    # Check if there's a None check before
                    has_check = False
                    for j in range(max(0, i - 5), i):
                        if 'if ' in lines[j] and ' is not None' in lines[j]:
                            has_check = True
                            break

                    if not has_check:
                        # Potential issue (simplified check)
                        pass  # Too many false positives, skip for now

        return issues

    # Best practices checks
    def _check_type_hints(
        self,
        file_path: Path,
        code: str,
        lines: List[str]
    ) -> List[ReviewIssue]:
        """Check for type hints"""
        issues = []

        try:
            tree = ast.parse(code)

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Check if function has type hints
                    has_return_type = node.returns is not None
                    has_param_types = all(arg.annotation is not None for arg in node.args.args)

                    if not has_return_type or not has_param_types:
                        issues.append(ReviewIssue(
                            severity=ReviewSeverity.INFO,
                            category=ReviewCategory.BEST_PRACTICES,
                            title="Missing Type Hints",
                            description=f"Function '{node.name}' missing type hints",
                            file_path=str(file_path),
                            line=node.lineno,
                            suggestion="Add type hints for better code documentation"
                        ))

        except SyntaxError:
            pass

        return issues

    def _check_docstrings(
        self,
        file_path: Path,
        code: str,
        lines: List[str]
    ) -> List[ReviewIssue]:
        """Check for docstrings"""
        issues = []

        try:
            tree = ast.parse(code)

            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                    if not ast.get_docstring(node):
                        issues.append(ReviewIssue(
                            severity=ReviewSeverity.INFO,
                            category=ReviewCategory.DOCUMENTATION,
                            title="Missing Docstring",
                            description=f"{node.__class__.__name__} '{node.name}' has no docstring",
                            file_path=str(file_path),
                            line=node.lineno,
                            suggestion="Add docstring describing purpose and parameters"
                        ))

        except SyntaxError:
            pass

        return issues

    def _check_test_coverage(
        self,
        file_path: Path,
        code: str,
        lines: List[str]
    ) -> List[ReviewIssue]:
        """Check if file has tests"""
        issues = []

        # Simple check: look for test file
        test_file = file_path.parent / f"test_{file_path.name}"

        if not test_file.exists() and not str(file_path).startswith('test_'):
            issues.append(ReviewIssue(
                severity=ReviewSeverity.INFO,
                category=ReviewCategory.BEST_PRACTICES,
                title="No Test File",
                description="No corresponding test file found",
                file_path=str(file_path),
                line=0,
                suggestion=f"Create {test_file.name} with tests"
            ))

        return issues

    def _calculate_metrics(self, code: str, lines: List[str]) -> Dict[str, Any]:
        """Calculate code metrics"""
        metrics = {
            'total_lines': len(lines),
            'code_lines': sum(1 for line in lines if line.strip() and not line.strip().startswith('#')),
            'comment_lines': sum(1 for line in lines if line.strip().startswith('#')),
            'blank_lines': sum(1 for line in lines if not line.strip()),
            'functions': 0,
            'classes': 0,
        }

        try:
            tree = ast.parse(code)
            metrics['functions'] = sum(1 for _ in ast.walk(tree) if isinstance(_, ast.FunctionDef))
            metrics['classes'] = sum(1 for _ in ast.walk(tree) if isinstance(_, ast.ClassDef))
        except SyntaxError:
            pass

        return metrics

    def _calculate_score(self, result: CodeReviewResult) -> float:
        """Calculate review score (0-100)"""
        # Start with 100
        score = 100.0

        # Deduct points for issues
        for issue in result.issues:
            if issue.severity == ReviewSeverity.CRITICAL:
                score -= 10
            elif issue.severity == ReviewSeverity.ERROR:
                score -= 5
            elif issue.severity == ReviewSeverity.WARNING:
                score -= 2
            elif issue.severity == ReviewSeverity.INFO:
                score -= 0.5

        return max(0.0, score)

    def _generate_suggestions(self, result: CodeReviewResult) -> List[ReviewSuggestion]:
        """Generate improvement suggestions"""
        suggestions = []

        # Group issues by category
        category_counts = {}
        for issue in result.issues:
            category = issue.category
            category_counts[category] = category_counts.get(category, 0) + 1

        # Generate suggestions based on common issues
        if category_counts.get(ReviewCategory.SECURITY, 0) > 0:
            suggestions.append(ReviewSuggestion(
                title="Improve Security",
                description="Address security vulnerabilities found in code",
                before="Use of dangerous functions or hardcoded secrets",
                after="Use safe alternatives and environment variables",
                impact="High",
                category=ReviewCategory.SECURITY
            ))

        if category_counts.get(ReviewCategory.PERFORMANCE, 0) > 0:
            suggestions.append(ReviewSuggestion(
                title="Optimize Performance",
                description="Improve code efficiency",
                before="Nested loops and string concatenation",
                after="Use comprehensions and join()",
                impact="Medium",
                category=ReviewCategory.PERFORMANCE
            ))

        return suggestions
