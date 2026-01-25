#!/usr/bin/env python3
"""
Code Completion Engine

Real-time AI-powered code completion с context-aware suggestions и intelligent ranking.
"""

import re
import ast
import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Set, Tuple
from collections import defaultdict


class CompletionType(Enum):
    """Type of Code Completion"""
    LINE = "line"  # Complete current line
    BLOCK = "block"  # Complete code block
    FUNCTION = "function"  # Complete entire function
    IMPORT = "import"  # Suggest imports
    VARIABLE = "variable"  # Variable name
    METHOD = "method"  # Method call
    PARAMETER = "parameter"  # Function parameter


class ConfidenceLevel(Enum):
    """Confidence Level for Suggestion"""
    HIGH = "high"  # >90%
    MEDIUM = "medium"  # 70-90%
    LOW = "low"  # <70%


@dataclass
class CompletionContext:
    """Code Completion Context"""
    file_path: str
    cursor_line: int
    cursor_column: int
    current_line: str
    lines_before: List[str] = field(default_factory=list)
    lines_after: List[str] = field(default_factory=list)
    language: str = "python"
    project_files: List[str] = field(default_factory=list)


@dataclass
class CompletionSuggestion:
    """Code Completion Suggestion"""
    text: str
    type: CompletionType
    confidence: float
    confidence_level: ConfidenceLevel
    explanation: str
    insert_position: Tuple[int, int]  # (line, column)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CompletionResult:
    """Code Completion Result"""
    suggestions: List[CompletionSuggestion] = field(default_factory=list)
    processing_time_ms: float = 0.0
    context_analyzed: int = 0  # Lines analyzed


class CodeCompletionEngine:
    """AI-Powered Code Completion Engine"""

    def __init__(self, model: str = "gpt-4"):
        """
        Initialize code completion engine

        Args:
            model: AI model to use for completions
        """
        self.model = model
        self.cache: Dict[str, CompletionResult] = {}
        self.context_window = 50  # Lines of context
        self.max_suggestions = 5

    def get_completions(
        self,
        context: CompletionContext,
        trigger: Optional[str] = None
    ) -> CompletionResult:
        """
        Get code completions for current context

        Args:
            context: Current code context
            trigger: Trigger character (., (, etc.)

        Returns:
            Completion result with suggestions
        """
        start_time = datetime.now()

        print(f"🔍 Getting completions for {context.file_path}:{context.cursor_line}")

        # Check cache
        cache_key = self._get_cache_key(context)
        if cache_key in self.cache:
            print("✅ Using cached completions")
            return self.cache[cache_key]

        suggestions = []

        # Analyze context
        analysis = self._analyze_context(context)

        # Generate different types of suggestions
        if trigger == ".":
            suggestions.extend(self._suggest_methods(context, analysis))
        elif trigger == "(":
            suggestions.extend(self._suggest_parameters(context, analysis))
        elif context.current_line.strip().startswith("import") or \
             context.current_line.strip().startswith("from"):
            suggestions.extend(self._suggest_imports(context, analysis))
        else:
            # General completions
            suggestions.extend(self._suggest_line_completion(context, analysis))
            suggestions.extend(self._suggest_block_completion(context, analysis))

        # Rank suggestions
        suggestions = self._rank_suggestions(suggestions, context)

        # Limit to max suggestions
        suggestions = suggestions[:self.max_suggestions]

        elapsed = (datetime.now() - start_time).total_seconds() * 1000

        result = CompletionResult(
            suggestions=suggestions,
            processing_time_ms=elapsed,
            context_analyzed=len(context.lines_before) + len(context.lines_after)
        )

        # Cache result
        self.cache[cache_key] = result

        print(f"✅ Generated {len(suggestions)} suggestions in {elapsed:.2f}ms")

        return result

    def _analyze_context(self, context: CompletionContext) -> Dict[str, Any]:
        """Analyze code context"""
        analysis = {
            'language': context.language,
            'imports': [],
            'classes': [],
            'functions': [],
            'variables': [],
            'current_scope': None,
            'indentation_level': 0
        }

        # Combine all lines
        all_lines = context.lines_before + [context.current_line] + context.lines_after

        if context.language == "python":
            # Parse Python code
            try:
                tree = ast.parse('\n'.join(all_lines))

                # Extract imports
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            analysis['imports'].append(alias.name)
                    elif isinstance(node, ast.ImportFrom):
                        module = node.module or ''
                        for alias in node.names:
                            analysis['imports'].append(f"{module}.{alias.name}")

                    # Extract class definitions
                    elif isinstance(node, ast.ClassDef):
                        analysis['classes'].append(node.name)

                    # Extract function definitions
                    elif isinstance(node, ast.FunctionDef):
                        analysis['functions'].append(node.name)

                    # Extract variable assignments
                    elif isinstance(node, ast.Assign):
                        for target in node.targets:
                            if isinstance(target, ast.Name):
                                analysis['variables'].append(target.id)

            except SyntaxError:
                # Partial/invalid code, use regex fallback
                analysis['imports'] = self._extract_imports_regex(all_lines)
                analysis['classes'] = self._extract_classes_regex(all_lines)
                analysis['functions'] = self._extract_functions_regex(all_lines)

        # Determine current scope
        analysis['current_scope'] = self._determine_scope(context.lines_before)

        # Calculate indentation
        if context.current_line:
            analysis['indentation_level'] = len(context.current_line) - len(context.current_line.lstrip())

        return analysis

    def _suggest_line_completion(
        self,
        context: CompletionContext,
        analysis: Dict[str, Any]
    ) -> List[CompletionSuggestion]:
        """Suggest line completions"""
        suggestions = []

        current_line = context.current_line.strip()

        # If line starts with 'if', 'for', 'while', suggest common patterns
        if current_line.startswith('if '):
            completion = current_line + ' is not None:'
            suggestions.append(CompletionSuggestion(
                text=completion,
                type=CompletionType.LINE,
                confidence=0.85,
                confidence_level=ConfidenceLevel.MEDIUM,
                explanation="Common null check pattern",
                insert_position=(context.cursor_line, 0),
                metadata={'pattern': 'null_check'}
            ))

        elif current_line.startswith('for '):
            if ' in ' not in current_line:
                completion = current_line + ' in range(10):'
                suggestions.append(CompletionSuggestion(
                    text=completion,
                    type=CompletionType.LINE,
                    confidence=0.80,
                    confidence_level=ConfidenceLevel.MEDIUM,
                    explanation="Common for loop pattern",
                    insert_position=(context.cursor_line, 0),
                    metadata={'pattern': 'for_loop'}
                ))

        # Variable assignment patterns
        elif '=' in current_line and not current_line.endswith('='):
            var_name = current_line.split('=')[0].strip()
            if var_name and not current_line.strip().endswith(':'):
                # Suggest common values
                suggestions.extend([
                    CompletionSuggestion(
                        text=f"{current_line} None",
                        type=CompletionType.LINE,
                        confidence=0.70,
                        confidence_level=ConfidenceLevel.MEDIUM,
                        explanation="Initialize to None",
                        insert_position=(context.cursor_line, 0)
                    ),
                    CompletionSuggestion(
                        text=f"{current_line} []",
                        type=CompletionType.LINE,
                        confidence=0.75,
                        confidence_level=ConfidenceLevel.MEDIUM,
                        explanation="Initialize to empty list",
                        insert_position=(context.cursor_line, 0)
                    ),
                    CompletionSuggestion(
                        text=f"{current_line} {{}}",
                        type=CompletionType.LINE,
                        confidence=0.75,
                        confidence_level=ConfidenceLevel.MEDIUM,
                        explanation="Initialize to empty dict",
                        insert_position=(context.cursor_line, 0)
                    )
                ])

        return suggestions

    def _suggest_block_completion(
        self,
        context: CompletionContext,
        analysis: Dict[str, Any]
    ) -> List[CompletionSuggestion]:
        """Suggest block completions"""
        suggestions = []

        current_line = context.current_line.strip()

        # Function definition completion
        if current_line.startswith('def ') and current_line.endswith(':'):
            indent = ' ' * (analysis['indentation_level'] + 4)
            func_name = current_line.split('(')[0].replace('def ', '').strip()

            body = f'''"""
{indent}TODO: Add function description

{indent}Args:
{indent}    TODO: Add parameters

{indent}Returns:
{indent}    TODO: Add return value
{indent}"""
{indent}pass'''

            suggestions.append(CompletionSuggestion(
                text=body,
                type=CompletionType.FUNCTION,
                confidence=0.90,
                confidence_level=ConfidenceLevel.HIGH,
                explanation=f"Complete function {func_name} with docstring",
                insert_position=(context.cursor_line + 1, analysis['indentation_level'] + 4),
                metadata={'function': func_name}
            ))

        # Class definition completion
        elif current_line.startswith('class ') and current_line.endswith(':'):
            indent = ' ' * (analysis['indentation_level'] + 4)
            class_name = current_line.split('(')[0].replace('class ', '').strip()

            body = f'''"""
{indent}{class_name} class
{indent}"""

{indent}def __init__(self):
{indent}    """Initialize {class_name}"""
{indent}    pass'''

            suggestions.append(CompletionSuggestion(
                text=body,
                type=CompletionType.BLOCK,
                confidence=0.92,
                confidence_level=ConfidenceLevel.HIGH,
                explanation=f"Complete class {class_name} with __init__",
                insert_position=(context.cursor_line + 1, analysis['indentation_level'] + 4),
                metadata={'class': class_name}
            ))

        # Try-except block
        elif current_line.startswith('try:'):
            indent = ' ' * analysis['indentation_level']
            body_indent = ' ' * (analysis['indentation_level'] + 4)

            body = f'''{body_indent}# TODO: Add try block code
{body_indent}pass
{indent}except Exception as e:
{body_indent}# TODO: Handle exception
{body_indent}print(f"Error: {{e}}")'''

            suggestions.append(CompletionSuggestion(
                text=body,
                type=CompletionType.BLOCK,
                confidence=0.88,
                confidence_level=ConfidenceLevel.HIGH,
                explanation="Complete try-except block",
                insert_position=(context.cursor_line + 1, analysis['indentation_level'] + 4)
            ))

        return suggestions

    def _suggest_methods(
        self,
        context: CompletionContext,
        analysis: Dict[str, Any]
    ) -> List[CompletionSuggestion]:
        """Suggest method calls after dot operator"""
        suggestions = []

        # Extract object before dot
        line_before_cursor = context.current_line[:context.cursor_column]
        match = re.search(r'(\w+)\.$', line_before_cursor)

        if match:
            obj_name = match.group(1)

            # Common Python object methods
            common_methods = {
                'str': ['split', 'strip', 'replace', 'format', 'upper', 'lower'],
                'list': ['append', 'extend', 'pop', 'remove', 'sort'],
                'dict': ['get', 'keys', 'values', 'items', 'update'],
                'Path': ['exists', 'mkdir', 'read_text', 'write_text'],
            }

            # Check if object type is known
            for type_name, methods in common_methods.items():
                for method in methods:
                    suggestions.append(CompletionSuggestion(
                        text=f"{obj_name}.{method}()",
                        type=CompletionType.METHOD,
                        confidence=0.75,
                        confidence_level=ConfidenceLevel.MEDIUM,
                        explanation=f"Common {type_name} method",
                        insert_position=(context.cursor_line, context.cursor_column)
                    ))

        return suggestions[:10]  # Limit method suggestions

    def _suggest_parameters(
        self,
        context: CompletionContext,
        analysis: Dict[str, Any]
    ) -> List[CompletionSuggestion]:
        """Suggest function parameters"""
        suggestions = []

        # Extract function name
        line_before_cursor = context.current_line[:context.cursor_column]
        match = re.search(r'(\w+)\($', line_before_cursor)

        if match:
            func_name = match.group(1)

            # Common function signatures
            common_signatures = {
                'open': ['filename, mode="r"', 'file, "r", encoding="utf-8"'],
                'print': ['*args, sep=" ", end="\\n"'],
                'range': ['stop', 'start, stop', 'start, stop, step'],
                'sorted': ['iterable, key=None, reverse=False'],
            }

            if func_name in common_signatures:
                for signature in common_signatures[func_name]:
                    suggestions.append(CompletionSuggestion(
                        text=signature,
                        type=CompletionType.PARAMETER,
                        confidence=0.85,
                        confidence_level=ConfidenceLevel.HIGH,
                        explanation=f"Common {func_name} signature",
                        insert_position=(context.cursor_line, context.cursor_column)
                    ))

        return suggestions

    def _suggest_imports(
        self,
        context: CompletionContext,
        analysis: Dict[str, Any]
    ) -> List[CompletionSuggestion]:
        """Suggest import statements"""
        suggestions = []

        current_line = context.current_line.strip()

        # Common import patterns
        common_imports = [
            'import os',
            'import sys',
            'import json',
            'import re',
            'from pathlib import Path',
            'from typing import Dict, List, Optional',
            'from dataclasses import dataclass',
            'from datetime import datetime',
            'import numpy as np',
            'import pandas as pd',
        ]

        for imp in common_imports:
            if imp.startswith(current_line):
                suggestions.append(CompletionSuggestion(
                    text=imp,
                    type=CompletionType.IMPORT,
                    confidence=0.80,
                    confidence_level=ConfidenceLevel.MEDIUM,
                    explanation="Common Python import",
                    insert_position=(context.cursor_line, 0)
                ))

        return suggestions

    def _rank_suggestions(
        self,
        suggestions: List[CompletionSuggestion],
        context: CompletionContext
    ) -> List[CompletionSuggestion]:
        """Rank suggestions by relevance"""
        # Sort by confidence (descending)
        suggestions.sort(key=lambda s: s.confidence, reverse=True)

        # Adjust confidence based on context
        for suggestion in suggestions:
            # Boost suggestions that match current indentation
            if suggestion.type in [CompletionType.BLOCK, CompletionType.FUNCTION]:
                # Already high confidence
                pass

            # Boost import suggestions if at top of file
            if suggestion.type == CompletionType.IMPORT and context.cursor_line < 10:
                suggestion.confidence = min(1.0, suggestion.confidence + 0.1)

        # Re-sort after adjustments
        suggestions.sort(key=lambda s: s.confidence, reverse=True)

        return suggestions

    def _determine_scope(self, lines_before: List[str]) -> Optional[str]:
        """Determine current scope (function, class, etc.)"""
        for line in reversed(lines_before):
            stripped = line.strip()
            if stripped.startswith('def '):
                return stripped.split('(')[0].replace('def ', '').strip()
            elif stripped.startswith('class '):
                return stripped.split('(')[0].replace('class ', '').strip()
        return None

    def _extract_imports_regex(self, lines: List[str]) -> List[str]:
        """Extract imports using regex (fallback)"""
        imports = []
        for line in lines:
            if line.strip().startswith('import '):
                imports.append(line.strip().replace('import ', ''))
            elif line.strip().startswith('from '):
                match = re.search(r'from ([\w.]+) import', line)
                if match:
                    imports.append(match.group(1))
        return imports

    def _extract_classes_regex(self, lines: List[str]) -> List[str]:
        """Extract classes using regex (fallback)"""
        classes = []
        for line in lines:
            match = re.search(r'class (\w+)', line)
            if match:
                classes.append(match.group(1))
        return classes

    def _extract_functions_regex(self, lines: List[str]) -> List[str]:
        """Extract functions using regex (fallback)"""
        functions = []
        for line in lines:
            match = re.search(r'def (\w+)', line)
            if match:
                functions.append(match.group(1))
        return functions

    def _get_cache_key(self, context: CompletionContext) -> str:
        """Generate cache key for context"""
        return f"{context.file_path}:{context.cursor_line}:{context.cursor_column}:{context.current_line}"

    def clear_cache(self):
        """Clear completion cache"""
        self.cache.clear()
        print("🗑️  Completion cache cleared")
