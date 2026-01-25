#!/usr/bin/env python3
"""
Documentation Generator

Автоматическая генерация documentation (JSDoc, Sphinx, Google style) из code.
"""

import ast
import json
import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any


class DocStyle(Enum):
    """Documentation Style"""
    GOOGLE = "google"
    NUMPY = "numpy"
    SPHINX = "sphinx"
    JSDOC = "jsdoc"
    TYPEDOC = "typedoc"
    JAVADOC = "javadoc"
    GODOC = "godoc"


class DocFormat(Enum):
    """Documentation Format"""
    MARKDOWN = "markdown"
    HTML = "html"
    RESTRUCTUREDTEXT = "rst"
    PDF = "pdf"


@dataclass
class FunctionDoc:
    """Function Documentation"""
    name: str
    description: str
    parameters: List[Dict[str, str]] = field(default_factory=list)
    returns: Optional[Dict[str, str]] = None
    raises: List[Dict[str, str]] = field(default_factory=list)
    examples: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)


@dataclass
class ClassDoc:
    """Class Documentation"""
    name: str
    description: str
    attributes: List[Dict[str, str]] = field(default_factory=list)
    methods: List[FunctionDoc] = field(default_factory=list)
    examples: List[str] = field(default_factory=list)


@dataclass
class ModuleDoc:
    """Module Documentation"""
    name: str
    description: str
    classes: List[ClassDoc] = field(default_factory=list)
    functions: List[FunctionDoc] = field(default_factory=list)
    constants: List[Dict[str, str]] = field(default_factory=list)


class DocumentationGenerator:
    """Documentation Generator"""

    def __init__(self, style: DocStyle = DocStyle.GOOGLE):
        """
        Инициализация documentation generator

        Args:
            style: Documentation style to generate
        """
        self.style = style
        self.modules: Dict[str, ModuleDoc] = {}

    def generate_from_code(self, code: str, module_name: str = "module") -> ModuleDoc:
        """
        Generate documentation from code

        Args:
            code: Source code
            module_name: Module name

        Returns:
            Module documentation
        """
        print(f"📖 Generating {self.style.value} documentation...")

        # Parse code
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            print(f"Error parsing code: {e}")
            return ModuleDoc(name=module_name, description="")

        # Extract module docstring
        module_docstring = ast.get_docstring(tree) or ""

        module_doc = ModuleDoc(
            name=module_name,
            description=module_docstring
        )

        # Parse classes and functions
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.ClassDef):
                class_doc = self._parse_class(node)
                module_doc.classes.append(class_doc)

            elif isinstance(node, ast.FunctionDef):
                func_doc = self._parse_function(node)
                module_doc.functions.append(func_doc)

            elif isinstance(node, ast.Assign):
                # Constants (module-level assignments)
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id.isupper():
                        constant = {
                            'name': target.id,
                            'type': self._infer_type(node.value),
                            'description': ''
                        }
                        module_doc.constants.append(constant)

        self.modules[module_name] = module_doc

        print(f"✅ Generated docs: {len(module_doc.classes)} classes, {len(module_doc.functions)} functions")
        return module_doc

    def export_docs(self,
                   module_doc: ModuleDoc,
                   output_path: Path,
                   format: DocFormat = DocFormat.MARKDOWN):
        """
        Export documentation to file

        Args:
            module_doc: Module documentation
            output_path: Output file path
            format: Output format
        """
        if format == DocFormat.MARKDOWN:
            content = self._generate_markdown(module_doc)
        elif format == DocFormat.HTML:
            content = self._generate_html(module_doc)
        elif format == DocFormat.RESTRUCTUREDTEXT:
            content = self._generate_rst(module_doc)
        else:
            content = self._generate_markdown(module_doc)

        with open(output_path, 'w') as f:
            f.write(content)

        print(f"✅ Exported documentation to {output_path}")

    def generate_api_reference(self, modules: List[ModuleDoc], output_dir: Path):
        """
        Generate complete API reference documentation

        Args:
            modules: List of module documentations
            output_dir: Output directory
        """
        output_dir.mkdir(parents=True, exist_ok=True)

        # Generate index
        index_md = self._generate_index(modules)
        with open(output_dir / "index.md", 'w') as f:
            f.write(index_md)

        # Generate individual module docs
        for module_doc in modules:
            module_file = output_dir / f"{module_doc.name}.md"
            self.export_docs(module_doc, module_file)

        print(f"✅ Generated API reference with {len(modules)} modules")

    def add_docstrings_to_code(self, code: str) -> str:
        """
        Add missing docstrings to code

        Args:
            code: Source code

        Returns:
            Code with added docstrings
        """
        print("📝 Adding missing docstrings...")

        try:
            tree = ast.parse(code)
        except:
            return code

        # Track modifications
        lines = code.split('\n')
        insertions = []  # (line_number, docstring)

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                if not ast.get_docstring(node):
                    # Generate docstring
                    docstring = self._generate_docstring(node)

                    # Find insertion point (after def/class line)
                    insert_line = node.lineno
                    indent = self._get_indent(lines[insert_line - 1])

                    insertions.append((insert_line, indent, docstring))

        # Insert docstrings (reverse order to maintain line numbers)
        for line_num, indent, docstring in reversed(insertions):
            docstring_lines = [f'{indent}    """', f'{indent}    {docstring}', f'{indent}    """']
            lines[line_num:line_num] = docstring_lines

        enhanced_code = '\n'.join(lines)
        print(f"✅ Added {len(insertions)} docstrings")

        return enhanced_code

    def _parse_class(self, node: ast.ClassDef) -> ClassDoc:
        """Parse class documentation"""
        docstring = ast.get_docstring(node) or ""

        class_doc = ClassDoc(
            name=node.name,
            description=docstring
        )

        # Parse class attributes (from __init__)
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == '__init__':
                for stmt in item.body:
                    if isinstance(stmt, ast.Assign):
                        for target in stmt.targets:
                            if isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name) and target.value.id == 'self':
                                class_doc.attributes.append({
                                    'name': target.attr,
                                    'type': self._infer_type(stmt.value),
                                    'description': ''
                                })

        # Parse methods
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                method_doc = self._parse_function(item)
                class_doc.methods.append(method_doc)

        return class_doc

    def _parse_function(self, node: ast.FunctionDef) -> FunctionDoc:
        """Parse function documentation"""
        docstring = ast.get_docstring(node) or ""

        func_doc = FunctionDoc(
            name=node.name,
            description=docstring
        )

        # Parse parameters
        for arg in node.args.args:
            param = {
                'name': arg.arg,
                'type': self._get_type_annotation(arg),
                'description': ''
            }
            func_doc.parameters.append(param)

        # Parse return type
        if node.returns:
            func_doc.returns = {
                'type': ast.unparse(node.returns),
                'description': ''
            }

        # Extract from docstring if exists
        if docstring:
            parsed_doc = self._parse_docstring(docstring)
            func_doc.description = parsed_doc.get('description', docstring)
            func_doc.parameters = parsed_doc.get('parameters', func_doc.parameters)
            func_doc.returns = parsed_doc.get('returns', func_doc.returns)
            func_doc.raises = parsed_doc.get('raises', [])

        return func_doc

    def _parse_docstring(self, docstring: str) -> Dict[str, Any]:
        """Parse existing docstring"""
        parsed = {
            'description': '',
            'parameters': [],
            'returns': None,
            'raises': []
        }

        lines = docstring.split('\n')
        current_section = 'description'
        description_lines = []

        for line in lines:
            line = line.strip()

            if line.startswith('Args:') or line.startswith('Parameters:'):
                current_section = 'parameters'
            elif line.startswith('Returns:'):
                current_section = 'returns'
            elif line.startswith('Raises:'):
                current_section = 'raises'
            elif current_section == 'description':
                description_lines.append(line)

        parsed['description'] = ' '.join(description_lines).strip()
        return parsed

    def _generate_markdown(self, module_doc: ModuleDoc) -> str:
        """Generate Markdown documentation"""
        md = f"# {module_doc.name}\n\n"

        if module_doc.description:
            md += f"{module_doc.description}\n\n"

        # Table of contents
        md += "## Table of Contents\n\n"
        if module_doc.classes:
            md += "- [Classes](#classes)\n"
        if module_doc.functions:
            md += "- [Functions](#functions)\n"
        if module_doc.constants:
            md += "- [Constants](#constants)\n"
        md += "\n"

        # Classes
        if module_doc.classes:
            md += "## Classes\n\n"
            for class_doc in module_doc.classes:
                md += f"### `{class_doc.name}`\n\n"
                md += f"{class_doc.description}\n\n"

                if class_doc.attributes:
                    md += "**Attributes:**\n\n"
                    for attr in class_doc.attributes:
                        md += f"- `{attr['name']}` ({attr['type']}): {attr['description']}\n"
                    md += "\n"

                if class_doc.methods:
                    md += "**Methods:**\n\n"
                    for method in class_doc.methods:
                        md += self._format_function_markdown(method)

        # Functions
        if module_doc.functions:
            md += "## Functions\n\n"
            for func_doc in module_doc.functions:
                md += self._format_function_markdown(func_doc)

        # Constants
        if module_doc.constants:
            md += "## Constants\n\n"
            for const in module_doc.constants:
                md += f"- `{const['name']}` ({const['type']}): {const['description']}\n"

        return md

    def _format_function_markdown(self, func_doc: FunctionDoc) -> str:
        """Format function as Markdown"""
        md = f"#### `{func_doc.name}()`\n\n"
        md += f"{func_doc.description}\n\n"

        if func_doc.parameters:
            md += "**Parameters:**\n\n"
            for param in func_doc.parameters:
                md += f"- `{param['name']}` ({param.get('type', 'Any')}): {param.get('description', '')}\n"
            md += "\n"

        if func_doc.returns:
            md += f"**Returns:** {func_doc.returns.get('type', '')} - {func_doc.returns.get('description', '')}\n\n"

        if func_doc.raises:
            md += "**Raises:**\n\n"
            for raises in func_doc.raises:
                md += f"- `{raises['type']}`: {raises['description']}\n"
            md += "\n"

        return md

    def _generate_html(self, module_doc: ModuleDoc) -> str:
        """Generate HTML documentation"""
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{module_doc.name} - Documentation</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; margin: 40px; line-height: 1.6; }}
        h1 {{ border-bottom: 2px solid #333; }}
        h2 {{ border-bottom: 1px solid #666; margin-top: 30px; }}
        code {{ background: #f4f4f4; padding: 2px 6px; border-radius: 3px; }}
        pre {{ background: #f4f4f4; padding: 15px; border-radius: 5px; overflow-x: auto; }}
    </style>
</head>
<body>
    <h1>{module_doc.name}</h1>
    <p>{module_doc.description}</p>
"""

        if module_doc.classes:
            html += "<h2>Classes</h2>\n"
            for class_doc in module_doc.classes:
                html += f"<h3>{class_doc.name}</h3>\n"
                html += f"<p>{class_doc.description}</p>\n"

        if module_doc.functions:
            html += "<h2>Functions</h2>\n"
            for func_doc in module_doc.functions:
                html += f"<h3>{func_doc.name}()</h3>\n"
                html += f"<p>{func_doc.description}</p>\n"

        html += "</body>\n</html>"
        return html

    def _generate_rst(self, module_doc: ModuleDoc) -> str:
        """Generate reStructuredText documentation"""
        rst = f"{module_doc.name}\n{'=' * len(module_doc.name)}\n\n"
        rst += f"{module_doc.description}\n\n"

        if module_doc.classes:
            rst += "Classes\n-------\n\n"
            for class_doc in module_doc.classes:
                rst += f".. class:: {class_doc.name}\n\n"
                rst += f"   {class_doc.description}\n\n"

        if module_doc.functions:
            rst += "Functions\n---------\n\n"
            for func_doc in module_doc.functions:
                rst += f".. function:: {func_doc.name}()\n\n"
                rst += f"   {func_doc.description}\n\n"

        return rst

    def _generate_index(self, modules: List[ModuleDoc]) -> str:
        """Generate index page"""
        md = "# API Reference\n\n"
        md += "## Modules\n\n"

        for module in modules:
            md += f"- [{module.name}]({module.name}.md) - {module.description[:100]}\n"

        return md

    def _generate_docstring(self, node: ast.AST) -> str:
        """Generate docstring for node"""
        if isinstance(node, ast.FunctionDef):
            desc = f"Function {node.name}"

            if node.args.args:
                param_names = ', '.join(arg.arg for arg in node.args.args)
                desc = f"{desc} with parameters: {param_names}"

            return desc

        elif isinstance(node, ast.ClassDef):
            return f"Class {node.name}"

        return "TODO: Add description"

    def _get_type_annotation(self, arg: ast.arg) -> str:
        """Get type annotation from argument"""
        if arg.annotation:
            return ast.unparse(arg.annotation)
        return "Any"

    def _infer_type(self, node: ast.AST) -> str:
        """Infer type from AST node"""
        if isinstance(node, ast.Constant):
            return type(node.value).__name__
        elif isinstance(node, ast.List):
            return "List"
        elif isinstance(node, ast.Dict):
            return "Dict"
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                return node.func.id
        return "Any"

    def _get_indent(self, line: str) -> str:
        """Get indentation from line"""
        return line[:len(line) - len(line.lstrip())]
