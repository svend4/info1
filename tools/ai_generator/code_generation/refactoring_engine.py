#!/usr/bin/env python3
"""
Advanced Refactoring Engine

Автоматический рефакторинг code для улучшения quality, performance, и maintainability.
"""

import ast
import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Set, Tuple


class RefactoringType(Enum):
    """Refactoring Types"""
    EXTRACT_METHOD = "extract_method"
    EXTRACT_VARIABLE = "extract_variable"
    INLINE_VARIABLE = "inline_variable"
    RENAME = "rename"
    MOVE_METHOD = "move_method"
    REMOVE_DEAD_CODE = "remove_dead_code"
    SIMPLIFY_CONDITIONAL = "simplify_conditional"
    REPLACE_MAGIC_NUMBER = "replace_magic_number"
    INTRODUCE_PARAMETER = "introduce_parameter"
    REMOVE_PARAMETER = "remove_parameter"


class CodeIssueType(Enum):
    """Code Issue Types"""
    COMPLEXITY = "complexity"
    DUPLICATION = "duplication"
    NAMING = "naming"
    PERFORMANCE = "performance"
    STYLE = "style"
    SECURITY = "security"


@dataclass
class CodeIssue:
    """Code Issue/Smell"""
    issue_type: CodeIssueType
    severity: str  # "low", "medium", "high", "critical"
    message: str
    file_path: Path
    line_number: int
    suggested_refactoring: RefactoringType
    original_code: str
    refactored_code: str


@dataclass
class RefactoringResult:
    """Refactoring Result"""
    refactoring_type: RefactoringType
    original_code: str
    refactored_code: str
    issues_fixed: List[CodeIssue]
    improvements: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)


class AdvancedRefactoringEngine:
    """Advanced Code Refactoring Engine"""

    def __init__(self):
        """Инициализация refactoring engine"""
        self.refactoring_history: List[RefactoringResult] = []
        self.max_method_lines = 50
        self.max_complexity = 10
        self.max_parameters = 5

    def analyze_code(self, code: str, file_path: Optional[Path] = None) -> List[CodeIssue]:
        """
        Analyze code for issues and refactoring opportunities

        Args:
            code: Source code to analyze
            file_path: Path to source file

        Returns:
            List of code issues
        """
        issues = []

        # Parse Python code
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return issues

        # Analyze different aspects
        issues.extend(self._check_complexity(tree, code, file_path))
        issues.extend(self._check_duplication(code, file_path))
        issues.extend(self._check_naming(tree, file_path))
        issues.extend(self._check_magic_numbers(tree, code, file_path))
        issues.extend(self._check_dead_code(tree, code, file_path))

        return issues

    def refactor_code(self,
                     code: str,
                     refactoring_type: RefactoringType,
                     **kwargs) -> RefactoringResult:
        """
        Refactor code

        Args:
            code: Source code
            refactoring_type: Type of refactoring
            **kwargs: Additional refactoring parameters

        Returns:
            Refactoring result
        """
        if refactoring_type == RefactoringType.EXTRACT_METHOD:
            return self._extract_method(code, **kwargs)
        elif refactoring_type == RefactoringType.EXTRACT_VARIABLE:
            return self._extract_variable(code, **kwargs)
        elif refactoring_type == RefactoringType.RENAME:
            return self._rename(code, **kwargs)
        elif refactoring_type == RefactoringType.REMOVE_DEAD_CODE:
            return self._remove_dead_code(code)
        elif refactoring_type == RefactoringType.SIMPLIFY_CONDITIONAL:
            return self._simplify_conditional(code, **kwargs)
        elif refactoring_type == RefactoringType.REPLACE_MAGIC_NUMBER:
            return self._replace_magic_numbers(code)
        else:
            return RefactoringResult(
                refactoring_type=refactoring_type,
                original_code=code,
                refactored_code=code,
                issues_fixed=[]
            )

    def auto_refactor(self, code: str) -> RefactoringResult:
        """
        Automatically refactor code based on detected issues

        Args:
            code: Source code

        Returns:
            Combined refactoring result
        """
        print("🔧 Auto-refactoring code...")

        issues = self.analyze_code(code)
        print(f"  Found {len(issues)} issues")

        refactored = code
        all_fixes = []

        # Apply refactorings in priority order
        priority_order = [
            RefactoringType.REMOVE_DEAD_CODE,
            RefactoringType.REPLACE_MAGIC_NUMBER,
            RefactoringType.SIMPLIFY_CONDITIONAL,
            RefactoringType.EXTRACT_METHOD
        ]

        for refactoring_type in priority_order:
            relevant_issues = [i for i in issues if i.suggested_refactoring == refactoring_type]

            if relevant_issues:
                result = self.refactor_code(refactored, refactoring_type)
                refactored = result.refactored_code
                all_fixes.extend(relevant_issues)
                print(f"  Applied {refactoring_type.value}")

        # Calculate improvements
        improvements = self._calculate_improvements(code, refactored)

        return RefactoringResult(
            refactoring_type=RefactoringType.EXTRACT_METHOD,  # Combined
            original_code=code,
            refactored_code=refactored,
            issues_fixed=all_fixes,
            improvements=improvements
        )

    def _check_complexity(self,
                         tree: ast.AST,
                         code: str,
                         file_path: Optional[Path]) -> List[CodeIssue]:
        """Check cyclomatic complexity"""
        issues = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                complexity = self._calculate_complexity(node)

                if complexity > self.max_complexity:
                    issues.append(CodeIssue(
                        issue_type=CodeIssueType.COMPLEXITY,
                        severity="high",
                        message=f"Function '{node.name}' has complexity {complexity} (max: {self.max_complexity})",
                        file_path=file_path or Path("unknown"),
                        line_number=node.lineno,
                        suggested_refactoring=RefactoringType.EXTRACT_METHOD,
                        original_code=ast.unparse(node),
                        refactored_code=""
                    ))

                # Check method length
                func_lines = len(ast.unparse(node).split('\n'))
                if func_lines > self.max_method_lines:
                    issues.append(CodeIssue(
                        issue_type=CodeIssueType.COMPLEXITY,
                        severity="medium",
                        message=f"Function '{node.name}' has {func_lines} lines (max: {self.max_method_lines})",
                        file_path=file_path or Path("unknown"),
                        line_number=node.lineno,
                        suggested_refactoring=RefactoringType.EXTRACT_METHOD,
                        original_code=ast.unparse(node),
                        refactored_code=""
                    ))

                # Check parameter count
                param_count = len(node.args.args)
                if param_count > self.max_parameters:
                    issues.append(CodeIssue(
                        issue_type=CodeIssueType.COMPLEXITY,
                        severity="medium",
                        message=f"Function '{node.name}' has {param_count} parameters (max: {self.max_parameters})",
                        file_path=file_path or Path("unknown"),
                        line_number=node.lineno,
                        suggested_refactoring=RefactoringType.INTRODUCE_PARAMETER,
                        original_code=ast.unparse(node),
                        refactored_code=""
                    ))

        return issues

    def _check_duplication(self, code: str, file_path: Optional[Path]) -> List[CodeIssue]:
        """Check for code duplication"""
        issues = []
        lines = code.split('\n')

        # Simple duplication detection: find repeated blocks of 5+ lines
        for i in range(len(lines) - 5):
            block = '\n'.join(lines[i:i+5])

            # Search for duplicates
            rest_of_code = '\n'.join(lines[i+5:])
            if block in rest_of_code:
                issues.append(CodeIssue(
                    issue_type=CodeIssueType.DUPLICATION,
                    severity="medium",
                    message=f"Duplicate code block found at line {i+1}",
                    file_path=file_path or Path("unknown"),
                    line_number=i+1,
                    suggested_refactoring=RefactoringType.EXTRACT_METHOD,
                    original_code=block,
                    refactored_code=""
                ))
                break  # Avoid reporting same duplication multiple times

        return issues

    def _check_naming(self, tree: ast.AST, file_path: Optional[Path]) -> List[CodeIssue]:
        """Check naming conventions"""
        issues = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Check for non-descriptive names
                if len(node.name) < 3 or node.name in ['foo', 'bar', 'baz', 'temp', 'tmp']:
                    issues.append(CodeIssue(
                        issue_type=CodeIssueType.NAMING,
                        severity="low",
                        message=f"Function '{node.name}' has non-descriptive name",
                        file_path=file_path or Path("unknown"),
                        line_number=node.lineno,
                        suggested_refactoring=RefactoringType.RENAME,
                        original_code=node.name,
                        refactored_code=""
                    ))

            elif isinstance(node, ast.ClassDef):
                # Check PascalCase for classes
                if not node.name[0].isupper():
                    issues.append(CodeIssue(
                        issue_type=CodeIssueType.NAMING,
                        severity="low",
                        message=f"Class '{node.name}' should use PascalCase",
                        file_path=file_path or Path("unknown"),
                        line_number=node.lineno,
                        suggested_refactoring=RefactoringType.RENAME,
                        original_code=node.name,
                        refactored_code=""
                    ))

        return issues

    def _check_magic_numbers(self,
                            tree: ast.AST,
                            code: str,
                            file_path: Optional[Path]) -> List[CodeIssue]:
        """Check for magic numbers"""
        issues = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Constant):
                # Check for numeric literals (excluding 0, 1, -1)
                if isinstance(node.value, (int, float)) and node.value not in [0, 1, -1]:
                    issues.append(CodeIssue(
                        issue_type=CodeIssueType.STYLE,
                        severity="low",
                        message=f"Magic number {node.value} should be a named constant",
                        file_path=file_path or Path("unknown"),
                        line_number=node.lineno,
                        suggested_refactoring=RefactoringType.REPLACE_MAGIC_NUMBER,
                        original_code=str(node.value),
                        refactored_code=""
                    ))

        return issues

    def _check_dead_code(self,
                        tree: ast.AST,
                        code: str,
                        file_path: Optional[Path]) -> List[CodeIssue]:
        """Check for dead/unreachable code"""
        issues = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Check for functions that are never called
                func_name = node.name

                # Simple check: if function starts with underscore and is never referenced
                if func_name.startswith('_') and func_name not in code.replace(f'def {func_name}', ''):
                    issues.append(CodeIssue(
                        issue_type=CodeIssueType.COMPLEXITY,
                        severity="low",
                        message=f"Function '{func_name}' appears to be unused",
                        file_path=file_path or Path("unknown"),
                        line_number=node.lineno,
                        suggested_refactoring=RefactoringType.REMOVE_DEAD_CODE,
                        original_code=ast.unparse(node),
                        refactored_code=""
                    ))

        return issues

    def _extract_method(self, code: str, **kwargs) -> RefactoringResult:
        """Extract method refactoring"""
        start_line = kwargs.get('start_line', 0)
        end_line = kwargs.get('end_line', 0)
        method_name = kwargs.get('method_name', 'extracted_method')

        lines = code.split('\n')

        if start_line and end_line:
            # Extract specific lines
            extracted_lines = lines[start_line:end_line+1]
            extracted_code = '\n'.join(extracted_lines)

            # Create new method
            new_method = f'''
def {method_name}():
    """
    Extracted method
    """
{extracted_code}
'''

            # Replace original code with method call
            lines[start_line:end_line+1] = [f'    {method_name}()']

            refactored = '\n'.join(lines)
            refactored = new_method + '\n' + refactored

        else:
            # Auto-extract longest method
            refactored = code  # Simplified

        return RefactoringResult(
            refactoring_type=RefactoringType.EXTRACT_METHOD,
            original_code=code,
            refactored_code=refactored,
            issues_fixed=[]
        )

    def _extract_variable(self, code: str, **kwargs) -> RefactoringResult:
        """Extract variable refactoring"""
        expression = kwargs.get('expression', '')
        variable_name = kwargs.get('variable_name', 'extracted_var')

        if expression:
            refactored = code.replace(
                expression,
                f"{variable_name} = {expression}\n    {variable_name}"
            )
        else:
            refactored = code

        return RefactoringResult(
            refactoring_type=RefactoringType.EXTRACT_VARIABLE,
            original_code=code,
            refactored_code=refactored,
            issues_fixed=[]
        )

    def _rename(self, code: str, **kwargs) -> RefactoringResult:
        """Rename refactoring"""
        old_name = kwargs.get('old_name', '')
        new_name = kwargs.get('new_name', '')

        if old_name and new_name:
            # Simple text replacement (in production: use AST for accurate renaming)
            refactored = re.sub(r'\b' + old_name + r'\b', new_name, code)
        else:
            refactored = code

        return RefactoringResult(
            refactoring_type=RefactoringType.RENAME,
            original_code=code,
            refactored_code=refactored,
            issues_fixed=[]
        )

    def _remove_dead_code(self, code: str) -> RefactoringResult:
        """Remove dead code"""
        # Simplified: remove empty functions and comments
        lines = code.split('\n')
        cleaned_lines = [line for line in lines if line.strip() and not line.strip().startswith('#')]

        refactored = '\n'.join(cleaned_lines)

        return RefactoringResult(
            refactoring_type=RefactoringType.REMOVE_DEAD_CODE,
            original_code=code,
            refactored_code=refactored,
            issues_fixed=[]
        )

    def _simplify_conditional(self, code: str, **kwargs) -> RefactoringResult:
        """Simplify conditional expressions"""
        # Simplify: if x == True -> if x
        refactored = code.replace('== True', '')
        refactored = refactored.replace('== False', '== False')  # Keep for clarity

        # Simplify: if not (x == y) -> if x != y
        refactored = re.sub(r'if not \((.+?) == (.+?)\)', r'if \1 != \2', refactored)

        return RefactoringResult(
            refactoring_type=RefactoringType.SIMPLIFY_CONDITIONAL,
            original_code=code,
            refactored_code=refactored,
            issues_fixed=[]
        )

    def _replace_magic_numbers(self, code: str) -> RefactoringResult:
        """Replace magic numbers with named constants"""
        # Find magic numbers
        magic_numbers = set()

        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.Constant):
                    if isinstance(node.value, (int, float)) and node.value not in [0, 1, -1]:
                        magic_numbers.add(node.value)
        except:
            pass

        # Generate constants at top
        constants = '\n'.join([
            f"{self._generate_constant_name(num)} = {num}"
            for num in sorted(magic_numbers)
        ])

        if constants:
            refactored = f"# Constants\n{constants}\n\n{code}"

            # Replace numbers with constants (simplified)
            for num in magic_numbers:
                const_name = self._generate_constant_name(num)
                refactored = refactored.replace(f" {num}", f" {const_name}")
        else:
            refactored = code

        return RefactoringResult(
            refactoring_type=RefactoringType.REPLACE_MAGIC_NUMBER,
            original_code=code,
            refactored_code=refactored,
            issues_fixed=[]
        )

    def _calculate_complexity(self, node: ast.FunctionDef) -> int:
        """Calculate cyclomatic complexity"""
        complexity = 1  # Base complexity

        for child in ast.walk(node):
            # Count decision points
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                # Each boolean operator adds complexity
                complexity += len(child.values) - 1

        return complexity

    def _calculate_improvements(self, original: str, refactored: str) -> Dict[str, Any]:
        """Calculate code improvements"""
        return {
            'lines_removed': len(original.split('\n')) - len(refactored.split('\n')),
            'characters_saved': len(original) - len(refactored),
            'complexity_reduced': self._estimate_complexity_reduction(original, refactored)
        }

    def _estimate_complexity_reduction(self, original: str, refactored: str) -> int:
        """Estimate complexity reduction"""
        # Simplified: count control flow statements
        original_complexity = original.count('if ') + original.count('for ') + original.count('while ')
        refactored_complexity = refactored.count('if ') + refactored.count('for ') + refactored.count('while ')

        return original_complexity - refactored_complexity

    def _generate_constant_name(self, number: Any) -> str:
        """Generate constant name for magic number"""
        # Simple heuristic naming
        if number == 100:
            return "PERCENTAGE_MAX"
        elif number == 60:
            return "SECONDS_PER_MINUTE"
        elif number == 24:
            return "HOURS_PER_DAY"
        else:
            return f"CONSTANT_{str(number).replace('.', '_')}"
