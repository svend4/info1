#!/usr/bin/env python3
"""
Intelligent Refactoring Assistant

AI-powered code refactoring с automatic transformations, pattern detection, и safe rewrites.
"""

import ast
import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Set, Tuple


class RefactoringType(Enum):
    """Type of Refactoring"""
    EXTRACT_METHOD = "extract_method"
    EXTRACT_VARIABLE = "extract_variable"
    RENAME = "rename"
    INLINE = "inline"
    MOVE_METHOD = "move_method"
    SIMPLIFY_CONDITION = "simplify_condition"
    REMOVE_DEAD_CODE = "remove_dead_code"
    EXTRACT_CLASS = "extract_class"
    INTRODUCE_PARAMETER = "introduce_parameter"
    REPLACE_MAGIC_NUMBER = "replace_magic_number"


class RefactoringSafety(Enum):
    """Refactoring Safety Level"""
    SAFE = "safe"  # No side effects
    MOSTLY_SAFE = "mostly_safe"  # Minimal risk
    RISKY = "risky"  # Requires careful review
    DANGEROUS = "dangerous"  # High risk


@dataclass
class CodeRange:
    """Code Range Selection"""
    start_line: int
    start_column: int
    end_line: int
    end_column: int


@dataclass
class RefactoringAction:
    """Refactoring Action"""
    type: RefactoringType
    title: str
    description: str
    safety: RefactoringSafety
    file_path: str
    range: CodeRange
    before_code: str
    after_code: str
    affected_files: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RefactoringResult:
    """Refactoring Result"""
    success: bool
    actions: List[RefactoringAction] = field(default_factory=list)
    changes: Dict[str, str] = field(default_factory=dict)  # file -> new content
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


class IntelligentRefactoringAssistant:
    """AI-Powered Intelligent Refactoring Assistant"""

    def __init__(self, model: str = "gpt-4"):
        """
        Initialize refactoring assistant

        Args:
            model: AI model to use
        """
        self.model = model
        self.refactorings: Dict[RefactoringType, Callable] = {}
        self._setup_refactorings()

    def _setup_refactorings(self):
        """Setup refactoring handlers"""
        self.refactorings = {
            RefactoringType.EXTRACT_METHOD: self._extract_method,
            RefactoringType.EXTRACT_VARIABLE: self._extract_variable,
            RefactoringType.RENAME: self._rename_symbol,
            RefactoringType.INLINE: self._inline_variable,
            RefactoringType.SIMPLIFY_CONDITION: self._simplify_condition,
            RefactoringType.REMOVE_DEAD_CODE: self._remove_dead_code,
            RefactoringType.REPLACE_MAGIC_NUMBER: self._replace_magic_number,
        }

    def suggest_refactorings(
        self,
        file_path: Path,
        code_range: Optional[CodeRange] = None
    ) -> List[RefactoringAction]:
        """
        Suggest refactorings for code

        Args:
            file_path: File to analyze
            code_range: Optional specific code range

        Returns:
            List of refactoring suggestions
        """
        print(f"🔍 Analyzing {file_path} for refactoring opportunities...")

        suggestions = []

        # Read file
        code = file_path.read_text()
        lines = code.split('\n')

        # Analyze code
        try:
            tree = ast.parse(code)

            # Find long methods
            suggestions.extend(self._suggest_extract_method(file_path, tree, lines))

            # Find complex expressions
            suggestions.extend(self._suggest_extract_variable(file_path, tree, lines))

            # Find magic numbers
            suggestions.extend(self._suggest_replace_magic_numbers(file_path, tree, lines))

            # Find dead code
            suggestions.extend(self._suggest_remove_dead_code(file_path, tree, lines))

            # Find complex conditions
            suggestions.extend(self._suggest_simplify_conditions(file_path, tree, lines))

        except SyntaxError as e:
            print(f"⚠️  Syntax error in {file_path}: {e}")

        print(f"✅ Found {len(suggestions)} refactoring opportunities")

        return suggestions

    def apply_refactoring(
        self,
        action: RefactoringAction,
        auto_apply: bool = False
    ) -> RefactoringResult:
        """
        Apply refactoring action

        Args:
            action: Refactoring action to apply
            auto_apply: Automatically apply without confirmation

        Returns:
            Refactoring result
        """
        print(f"🔧 Applying refactoring: {action.title}")

        result = RefactoringResult(success=False)

        # Check safety
        if action.safety == RefactoringSafety.DANGEROUS and not auto_apply:
            result.errors.append("Dangerous refactoring requires manual confirmation")
            return result

        # Apply refactoring
        try:
            file_path = Path(action.file_path)
            original_code = file_path.read_text()

            # Perform transformation
            if action.type in self.refactorings:
                new_code = self.refactorings[action.type](
                    original_code,
                    action
                )

                result.changes[str(file_path)] = new_code
                result.success = True
                result.actions.append(action)

                print(f"✅ Refactoring applied successfully")

            else:
                result.errors.append(f"Unsupported refactoring type: {action.type}")

        except Exception as e:
            result.errors.append(f"Error applying refactoring: {e}")
            print(f"❌ Error: {e}")

        return result

    def _suggest_extract_method(
        self,
        file_path: Path,
        tree: ast.AST,
        lines: List[str]
    ) -> List[RefactoringAction]:
        """Suggest extract method refactorings"""
        suggestions = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Count statements
                statements = [n for n in ast.walk(node) if isinstance(n, ast.stmt)]

                if len(statements) > 20:
                    # Find logical blocks to extract
                    # Simplified: suggest extracting loops
                    for child in ast.walk(node):
                        if isinstance(child, (ast.For, ast.While)) and hasattr(child, 'lineno'):
                            # Calculate end line
                            end_line = child.lineno
                            for subchild in ast.walk(child):
                                if hasattr(subchild, 'lineno'):
                                    end_line = max(end_line, subchild.lineno)

                            loop_code = '\n'.join(lines[child.lineno - 1:end_line])

                            suggestions.append(RefactoringAction(
                                type=RefactoringType.EXTRACT_METHOD,
                                title=f"Extract loop to separate method",
                                description=f"Extract complex loop from {node.name} to improve readability",
                                safety=RefactoringSafety.SAFE,
                                file_path=str(file_path),
                                range=CodeRange(
                                    start_line=child.lineno,
                                    start_column=0,
                                    end_line=end_line,
                                    end_column=len(lines[end_line - 1]) if end_line <= len(lines) else 0
                                ),
                                before_code=loop_code,
                                after_code=f"self._process_items()  # Extracted method",
                                metadata={'function': node.name, 'extracted_name': '_process_items'}
                            ))

        return suggestions

    def _suggest_extract_variable(
        self,
        file_path: Path,
        tree: ast.AST,
        lines: List[str]
    ) -> List[RefactoringAction]:
        """Suggest extract variable refactorings"""
        suggestions = []

        for node in ast.walk(tree):
            # Find complex expressions
            if isinstance(node, ast.BinOp) and hasattr(node, 'lineno'):
                # Check if used multiple times (simplified check)
                line = lines[node.lineno - 1]

                # Complex boolean expression
                if isinstance(node.op, (ast.And, ast.Or)):
                    expr = ast.unparse(node) if hasattr(ast, 'unparse') else line.strip()

                    suggestions.append(RefactoringAction(
                        type=RefactoringType.EXTRACT_VARIABLE,
                        title="Extract complex condition to variable",
                        description="Extract complex boolean expression to named variable",
                        safety=RefactoringSafety.SAFE,
                        file_path=str(file_path),
                        range=CodeRange(
                            start_line=node.lineno,
                            start_column=node.col_offset,
                            end_line=node.lineno,
                            end_column=node.col_offset + len(expr)
                        ),
                        before_code=expr,
                        after_code=f"is_valid = {expr}\n    if is_valid:",
                        metadata={'variable_name': 'is_valid'}
                    ))

        return suggestions

    def _suggest_replace_magic_numbers(
        self,
        file_path: Path,
        tree: ast.AST,
        lines: List[str]
    ) -> List[RefactoringAction]:
        """Suggest replacing magic numbers with constants"""
        suggestions = []

        # Track numbers and their usage
        numbers_used: Dict[int, List[int]] = {}

        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
                # Skip 0, 1 (common values)
                if node.value not in [0, 1, -1] and hasattr(node, 'lineno'):
                    if node.value not in numbers_used:
                        numbers_used[node.value] = []
                    numbers_used[node.value].append(node.lineno)

        # Suggest replacement for numbers used multiple times
        for number, line_nums in numbers_used.items():
            if len(line_nums) >= 2:
                const_name = f"MAX_VALUE" if number > 100 else f"THRESHOLD"

                suggestions.append(RefactoringAction(
                    type=RefactoringType.REPLACE_MAGIC_NUMBER,
                    title=f"Replace magic number {number}",
                    description=f"Replace magic number {number} with named constant (used {len(line_nums)} times)",
                    safety=RefactoringSafety.SAFE,
                    file_path=str(file_path),
                    range=CodeRange(
                        start_line=line_nums[0],
                        start_column=0,
                        end_line=line_nums[0],
                        end_column=0
                    ),
                    before_code=f"value = {number}",
                    after_code=f"{const_name} = {number}\nvalue = {const_name}",
                    metadata={'number': number, 'occurrences': len(line_nums), 'constant_name': const_name}
                ))

        return suggestions

    def _suggest_remove_dead_code(
        self,
        file_path: Path,
        tree: ast.AST,
        lines: List[str]
    ) -> List[RefactoringAction]:
        """Suggest removing dead code"""
        suggestions = []

        # Find unreachable code after return
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                has_return = False
                for i, child in enumerate(node.body):
                    if isinstance(child, ast.Return):
                        has_return = True
                        # Check if there's code after return
                        if i < len(node.body) - 1:
                            next_node = node.body[i + 1]
                            if hasattr(next_node, 'lineno'):
                                dead_code = lines[next_node.lineno - 1]

                                suggestions.append(RefactoringAction(
                                    type=RefactoringType.REMOVE_DEAD_CODE,
                                    title="Remove unreachable code",
                                    description=f"Code after return in {node.name} is unreachable",
                                    safety=RefactoringSafety.SAFE,
                                    file_path=str(file_path),
                                    range=CodeRange(
                                        start_line=next_node.lineno,
                                        start_column=0,
                                        end_line=next_node.lineno,
                                        end_column=len(dead_code)
                                    ),
                                    before_code=dead_code,
                                    after_code="# Removed unreachable code",
                                    metadata={'function': node.name}
                                ))

        return suggestions

    def _suggest_simplify_conditions(
        self,
        file_path: Path,
        tree: ast.AST,
        lines: List[str]
    ) -> List[RefactoringAction]:
        """Suggest simplifying complex conditions"""
        suggestions = []

        for node in ast.walk(tree):
            if isinstance(node, ast.If) and hasattr(node, 'lineno'):
                # Count boolean operators
                bool_ops = sum(1 for _ in ast.walk(node.test) if isinstance(_, (ast.And, ast.Or)))

                if bool_ops > 2:
                    condition = lines[node.lineno - 1].strip()

                    suggestions.append(RefactoringAction(
                        type=RefactoringType.SIMPLIFY_CONDITION,
                        title="Simplify complex condition",
                        description=f"Condition has {bool_ops} boolean operators",
                        safety=RefactoringSafety.MOSTLY_SAFE,
                        file_path=str(file_path),
                        range=CodeRange(
                            start_line=node.lineno,
                            start_column=0,
                            end_line=node.lineno,
                            end_column=len(condition)
                        ),
                        before_code=condition,
                        after_code="# Extract to well-named functions",
                        metadata={'bool_operators': bool_ops}
                    ))

        return suggestions

    def _extract_method(
        self,
        code: str,
        action: RefactoringAction
    ) -> str:
        """Apply extract method refactoring"""
        lines = code.split('\n')

        # Extract the code block
        start = action.range.start_line - 1
        end = action.range.end_line

        extracted_code = lines[start:end]
        method_name = action.metadata.get('extracted_name', '_extracted_method')

        # Determine indentation
        indent = len(extracted_code[0]) - len(extracted_code[0].lstrip())
        base_indent = ' ' * indent

        # Create new method
        new_method = [
            '',
            f'{base_indent}def {method_name}(self):',
            f'{base_indent}    """Extracted method"""'
        ]

        # Add extracted code with adjusted indentation
        for line in extracted_code:
            if line.strip():
                new_method.append(f'{base_indent}    {line.lstrip()}')

        # Replace original code with method call
        lines[start:end] = [f'{base_indent}self.{method_name}()']

        # Insert new method (find appropriate location - end of class)
        # Simplified: insert before current function
        lines = lines[:start] + new_method + lines[start:]

        return '\n'.join(lines)

    def _extract_variable(
        self,
        code: str,
        action: RefactoringAction
    ) -> str:
        """Apply extract variable refactoring"""
        lines = code.split('\n')
        line_num = action.range.start_line - 1

        # Get variable name
        var_name = action.metadata.get('variable_name', 'temp_var')

        # Insert variable assignment
        line = lines[line_num]
        indent = len(line) - len(line.lstrip())

        # Replace expression with variable
        before = action.before_code
        after = var_name

        new_var_line = f"{' ' * indent}{var_name} = {before}"
        modified_line = line.replace(before, after)

        lines[line_num] = new_var_line + '\n' + modified_line

        return '\n'.join(lines)

    def _rename_symbol(
        self,
        code: str,
        action: RefactoringAction
    ) -> str:
        """Apply rename refactoring"""
        old_name = action.metadata.get('old_name', '')
        new_name = action.metadata.get('new_name', '')

        if not old_name or not new_name:
            return code

        # Simple replace (in production, use AST for accurate renaming)
        # Use word boundaries to avoid partial matches
        pattern = r'\b' + re.escape(old_name) + r'\b'
        new_code = re.sub(pattern, new_name, code)

        return new_code

    def _inline_variable(
        self,
        code: str,
        action: RefactoringAction
    ) -> str:
        """Apply inline variable refactoring"""
        # Simplified implementation
        return code

    def _simplify_condition(
        self,
        code: str,
        action: RefactoringAction
    ) -> str:
        """Apply simplify condition refactoring"""
        # This would use AI to suggest simplified condition
        # Simplified implementation
        return code

    def _remove_dead_code(
        self,
        code: str,
        action: RefactoringAction
    ) -> str:
        """Apply remove dead code refactoring"""
        lines = code.split('\n')

        # Remove the specified line
        start = action.range.start_line - 1
        end = action.range.end_line

        del lines[start:end]

        return '\n'.join(lines)

    def _replace_magic_number(
        self,
        code: str,
        action: RefactoringAction
    ) -> str:
        """Apply replace magic number refactoring"""
        number = action.metadata.get('number')
        const_name = action.metadata.get('constant_name', 'CONSTANT')

        if number is None:
            return code

        # Add constant at top of file (simplified)
        lines = code.split('\n')

        # Find first non-import, non-comment line
        insert_pos = 0
        for i, line in enumerate(lines):
            if line.strip() and not line.strip().startswith('#') and not line.strip().startswith('import'):
                insert_pos = i
                break

        # Insert constant
        lines.insert(insert_pos, f'{const_name} = {number}')
        lines.insert(insert_pos + 1, '')

        # Replace occurrences
        new_code = '\n'.join(lines)
        new_code = re.sub(r'\b' + str(number) + r'\b', const_name, new_code)

        return new_code

    def batch_refactor(
        self,
        actions: List[RefactoringAction],
        auto_apply: bool = False
    ) -> RefactoringResult:
        """
        Apply multiple refactorings in batch

        Args:
            actions: List of refactoring actions
            auto_apply: Automatically apply all

        Returns:
            Combined refactoring result
        """
        print(f"🔧 Applying {len(actions)} refactorings in batch...")

        combined_result = RefactoringResult(success=True)

        for action in actions:
            result = self.apply_refactoring(action, auto_apply)

            if result.success:
                combined_result.changes.update(result.changes)
                combined_result.actions.extend(result.actions)
            else:
                combined_result.errors.extend(result.errors)
                combined_result.warnings.extend(result.warnings)

        combined_result.success = len(combined_result.errors) == 0

        print(f"✅ Batch refactoring complete: {len(combined_result.actions)} applied, {len(combined_result.errors)} errors")

        return combined_result

    def preview_refactoring(
        self,
        action: RefactoringAction
    ) -> Tuple[str, str]:
        """
        Preview refactoring without applying

        Args:
            action: Refactoring action

        Returns:
            Tuple of (before, after) code
        """
        file_path = Path(action.file_path)
        original_code = file_path.read_text()

        # Apply refactoring to get preview
        if action.type in self.refactorings:
            new_code = self.refactorings[action.type](original_code, action)
            return original_code, new_code

        return original_code, original_code
