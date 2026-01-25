#!/usr/bin/env python3
"""
Figma to Code Converter

Конвертация Figma designs в React/Vue/Angular/HTML code.
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple


class FrameworkType(Enum):
    """UI Framework Types"""
    REACT = "react"
    REACT_NATIVE = "react-native"
    VUE = "vue"
    ANGULAR = "angular"
    SVELTE = "svelte"
    HTML_CSS = "html-css"
    TAILWIND = "tailwind"


class ComponentType(Enum):
    """Figma Component Types"""
    FRAME = "FRAME"
    TEXT = "TEXT"
    RECTANGLE = "RECTANGLE"
    ELLIPSE = "ELLIPSE"
    GROUP = "GROUP"
    VECTOR = "VECTOR"
    INSTANCE = "INSTANCE"
    COMPONENT = "COMPONENT"
    BOOLEAN_OPERATION = "BOOLEAN_OPERATION"


@dataclass
class FigmaNode:
    """Figma Design Node"""
    id: str
    name: str
    type: ComponentType
    children: List['FigmaNode'] = field(default_factory=list)
    properties: Dict[str, Any] = field(default_factory=dict)
    styles: Dict[str, Any] = field(default_factory=dict)
    constraints: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GeneratedComponent:
    """Generated UI Component"""
    name: str
    framework: FrameworkType
    code: str
    styles: str
    imports: List[str] = field(default_factory=list)
    props: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ConversionResult:
    """Figma to Code Conversion Result"""
    figma_file_id: str
    framework: FrameworkType
    components: List[GeneratedComponent]
    assets: Dict[str, str] = field(default_factory=dict)  # image_id -> url
    design_tokens: Dict[str, Any] = field(default_factory=dict)
    generated_at: datetime = field(default_factory=datetime.utcnow)


class FigmaToCodeConverter:
    """Figma to Code Converter"""

    def __init__(self, figma_api_token: Optional[str] = None):
        """
        Инициализация Figma converter

        Args:
            figma_api_token: Figma API token
        """
        self.api_token = figma_api_token
        self.conversion_history: List[ConversionResult] = []

    def convert_file(self,
                    figma_file_id: str,
                    framework: FrameworkType,
                    page_name: Optional[str] = None) -> ConversionResult:
        """
        Convert Figma file to code

        Args:
            figma_file_id: Figma file ID
            framework: Target framework
            page_name: Specific page to convert (all if None)

        Returns:
            Conversion result
        """
        print(f"🎨 Converting Figma file to {framework.value}...")

        # 1. Fetch Figma file data
        figma_data = self._fetch_figma_file(figma_file_id)

        # 2. Extract design tokens
        design_tokens = self._extract_design_tokens(figma_data)

        # 3. Parse component tree
        root_nodes = self._parse_figma_nodes(figma_data, page_name)

        # 4. Generate code for each component
        components = []
        for node in root_nodes:
            component = self._generate_component(node, framework, design_tokens)
            components.append(component)

        # 5. Extract assets (images)
        assets = self._extract_assets(figma_data)

        result = ConversionResult(
            figma_file_id=figma_file_id,
            framework=framework,
            components=components,
            assets=assets,
            design_tokens=design_tokens
        )

        self.conversion_history.append(result)

        print(f"✅ Converted {len(components)} components")
        return result

    def export_project(self, result: ConversionResult, output_dir: Path):
        """
        Export converted code to project structure

        Args:
            result: Conversion result
            output_dir: Output directory
        """
        output_dir.mkdir(parents=True, exist_ok=True)

        # Create directory structure
        if result.framework in [FrameworkType.REACT, FrameworkType.REACT_NATIVE]:
            components_dir = output_dir / "src" / "components"
            styles_dir = output_dir / "src" / "styles"
        elif result.framework == FrameworkType.VUE:
            components_dir = output_dir / "src" / "components"
            styles_dir = output_dir / "src" / "assets" / "styles"
        elif result.framework == FrameworkType.ANGULAR:
            components_dir = output_dir / "src" / "app" / "components"
            styles_dir = output_dir / "src" / "styles"
        else:
            components_dir = output_dir / "components"
            styles_dir = output_dir / "styles"

        components_dir.mkdir(parents=True, exist_ok=True)
        styles_dir.mkdir(parents=True, exist_ok=True)

        # Write components
        for component in result.components:
            self._write_component(component, components_dir, styles_dir)

        # Write design tokens
        tokens_file = styles_dir / "tokens.json"
        with open(tokens_file, 'w') as f:
            json.dump(result.design_tokens, f, indent=2)

        # Write package.json or config files
        self._write_config_files(result.framework, output_dir)

        print(f"✅ Exported to {output_dir}")

    def _fetch_figma_file(self, file_id: str) -> Dict[str, Any]:
        """Fetch Figma file data from API"""
        # In production: use requests to call Figma API
        # GET https://api.figma.com/v1/files/{file_id}

        # Simulated Figma data
        return {
            'name': 'Design System',
            'document': {
                'id': '0:0',
                'name': 'Document',
                'type': 'DOCUMENT',
                'children': [
                    {
                        'id': '1:0',
                        'name': 'Page 1',
                        'type': 'CANVAS',
                        'children': [
                            {
                                'id': '1:1',
                                'name': 'Button',
                                'type': 'COMPONENT',
                                'children': [
                                    {
                                        'id': '1:2',
                                        'name': 'Label',
                                        'type': 'TEXT',
                                        'characters': 'Click Me',
                                        'style': {
                                            'fontFamily': 'Inter',
                                            'fontSize': 16,
                                            'fontWeight': 500,
                                            'textAlignHorizontal': 'CENTER'
                                        }
                                    }
                                ],
                                'backgroundColor': {'r': 0.2, 'g': 0.4, 'b': 0.8, 'a': 1},
                                'cornerRadius': 8,
                                'paddingLeft': 24,
                                'paddingRight': 24,
                                'paddingTop': 12,
                                'paddingBottom': 12,
                                'absoluteBoundingBox': {
                                    'x': 0,
                                    'y': 0,
                                    'width': 120,
                                    'height': 44
                                }
                            }
                        ]
                    }
                ]
            }
        }

    def _extract_design_tokens(self, figma_data: Dict) -> Dict[str, Any]:
        """Extract design tokens (colors, typography, spacing)"""
        tokens = {
            'colors': {
                'primary': '#3366CC',
                'secondary': '#6C757D',
                'success': '#28A745',
                'danger': '#DC3545',
                'warning': '#FFC107',
                'info': '#17A2B8'
            },
            'typography': {
                'fontFamily': {
                    'primary': 'Inter, sans-serif',
                    'secondary': 'Roboto, sans-serif'
                },
                'fontSize': {
                    'xs': '12px',
                    'sm': '14px',
                    'base': '16px',
                    'lg': '18px',
                    'xl': '20px',
                    '2xl': '24px'
                },
                'fontWeight': {
                    'normal': 400,
                    'medium': 500,
                    'semibold': 600,
                    'bold': 700
                }
            },
            'spacing': {
                'xs': '4px',
                'sm': '8px',
                'md': '16px',
                'lg': '24px',
                'xl': '32px'
            },
            'borderRadius': {
                'sm': '4px',
                'md': '8px',
                'lg': '12px',
                'full': '9999px'
            }
        }

        return tokens

    def _parse_figma_nodes(self, figma_data: Dict, page_name: Optional[str] = None) -> List[FigmaNode]:
        """Parse Figma nodes into internal structure"""
        document = figma_data.get('document', {})
        pages = document.get('children', [])

        # Filter by page name if specified
        if page_name:
            pages = [p for p in pages if p.get('name') == page_name]

        nodes = []
        for page in pages:
            for child in page.get('children', []):
                node = self._parse_node(child)
                if node:
                    nodes.append(node)

        return nodes

    def _parse_node(self, data: Dict) -> Optional[FigmaNode]:
        """Parse individual Figma node"""
        try:
            node_type = ComponentType(data['type'])
        except ValueError:
            return None

        node = FigmaNode(
            id=data['id'],
            name=data['name'],
            type=node_type,
            properties=data,
            styles=self._extract_styles(data)
        )

        # Parse children recursively
        if 'children' in data:
            for child_data in data['children']:
                child_node = self._parse_node(child_data)
                if child_node:
                    node.children.append(child_node)

        return node

    def _extract_styles(self, node_data: Dict) -> Dict[str, Any]:
        """Extract CSS-compatible styles from Figma node"""
        styles = {}

        # Background color
        if 'backgroundColor' in node_data:
            bg = node_data['backgroundColor']
            styles['backgroundColor'] = f"rgba({int(bg['r']*255)}, {int(bg['g']*255)}, {int(bg['b']*255)}, {bg['a']})"

        # Border radius
        if 'cornerRadius' in node_data:
            styles['borderRadius'] = f"{node_data['cornerRadius']}px"

        # Padding
        for side in ['paddingLeft', 'paddingRight', 'paddingTop', 'paddingBottom']:
            if side in node_data:
                styles[side] = f"{node_data[side]}px"

        # Size
        if 'absoluteBoundingBox' in node_data:
            box = node_data['absoluteBoundingBox']
            styles['width'] = f"{box['width']}px"
            styles['height'] = f"{box['height']}px"

        # Text styles
        if 'style' in node_data:
            text_style = node_data['style']
            if 'fontFamily' in text_style:
                styles['fontFamily'] = text_style['fontFamily']
            if 'fontSize' in text_style:
                styles['fontSize'] = f"{text_style['fontSize']}px"
            if 'fontWeight' in text_style:
                styles['fontWeight'] = text_style['fontWeight']
            if 'textAlignHorizontal' in text_style:
                styles['textAlign'] = text_style['textAlignHorizontal'].lower()

        return styles

    def _generate_component(self,
                           node: FigmaNode,
                           framework: FrameworkType,
                           design_tokens: Dict) -> GeneratedComponent:
        """Generate code for component"""
        if framework == FrameworkType.REACT:
            return self._generate_react(node, design_tokens)
        elif framework == FrameworkType.VUE:
            return self._generate_vue(node, design_tokens)
        elif framework == FrameworkType.ANGULAR:
            return self._generate_angular(node, design_tokens)
        elif framework == FrameworkType.HTML_CSS:
            return self._generate_html(node, design_tokens)
        else:
            return self._generate_react(node, design_tokens)

    def _generate_react(self, node: FigmaNode, tokens: Dict) -> GeneratedComponent:
        """Generate React component"""
        component_name = self._sanitize_name(node.name)

        # Generate JSX
        jsx = self._node_to_jsx(node, tokens)

        # Generate styles
        styles = self._generate_css_module(node, tokens)

        code = f'''import React from 'react';
import styles from './{component_name}.module.css';

interface {component_name}Props {{
  // Add props here
}}

export const {component_name}: React.FC<{component_name}Props> = (props) => {{
  return (
    {jsx}
  );
}};
'''

        return GeneratedComponent(
            name=component_name,
            framework=FrameworkType.REACT,
            code=code,
            styles=styles,
            imports=['react'],
            props=[]
        )

    def _generate_vue(self, node: FigmaNode, tokens: Dict) -> GeneratedComponent:
        """Generate Vue component"""
        component_name = self._sanitize_name(node.name)

        template = self._node_to_vue_template(node, tokens)
        styles = self._generate_scoped_css(node, tokens)

        code = f'''<template>
  {template}
</template>

<script setup lang="ts">
// Component logic here
</script>

<style scoped>
{styles}
</style>
'''

        return GeneratedComponent(
            name=component_name,
            framework=FrameworkType.VUE,
            code=code,
            styles=styles
        )

    def _generate_angular(self, node: FigmaNode, tokens: Dict) -> GeneratedComponent:
        """Generate Angular component"""
        component_name = self._sanitize_name(node.name)

        template = self._node_to_angular_template(node, tokens)
        styles = self._generate_component_css(node, tokens)

        code = f'''import {{ Component }} from '@angular/core';

@Component({{
  selector: 'app-{component_name.lower()}',
  templateUrl: './{component_name.lower()}.component.html',
  styleUrls: ['./{component_name.lower()}.component.css']
}})
export class {component_name}Component {{
  // Component logic
}}
'''

        return GeneratedComponent(
            name=component_name,
            framework=FrameworkType.ANGULAR,
            code=code,
            styles=styles
        )

    def _generate_html(self, node: FigmaNode, tokens: Dict) -> GeneratedComponent:
        """Generate HTML + CSS"""
        component_name = self._sanitize_name(node.name)

        html = self._node_to_html(node, tokens)
        css = self._generate_component_css(node, tokens)

        code = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{component_name}</title>
  <link rel="stylesheet" href="{component_name.lower()}.css">
</head>
<body>
  {html}
</body>
</html>
'''

        return GeneratedComponent(
            name=component_name,
            framework=FrameworkType.HTML_CSS,
            code=code,
            styles=css
        )

    def _node_to_jsx(self, node: FigmaNode, tokens: Dict) -> str:
        """Convert Figma node to JSX"""
        if node.type == ComponentType.TEXT:
            text = node.properties.get('characters', '')
            return f'<div className={{styles.text}}>{text}</div>'

        elif node.type in [ComponentType.FRAME, ComponentType.COMPONENT]:
            children_jsx = '\n      '.join(
                self._node_to_jsx(child, tokens) for child in node.children
            )
            return f'''<div className={{styles.container}}>
      {children_jsx}
    </div>'''

        elif node.type == ComponentType.RECTANGLE:
            return f'<div className={{styles.rectangle}}></div>'

        else:
            return f'<div className={{styles.element}}></div>'

    def _node_to_vue_template(self, node: FigmaNode, tokens: Dict) -> str:
        """Convert node to Vue template"""
        return self._node_to_html(node, tokens)

    def _node_to_angular_template(self, node: FigmaNode, tokens: Dict) -> str:
        """Convert node to Angular template"""
        return self._node_to_html(node, tokens)

    def _node_to_html(self, node: FigmaNode, tokens: Dict) -> str:
        """Convert node to HTML"""
        if node.type == ComponentType.TEXT:
            text = node.properties.get('characters', '')
            return f'<span class="text">{text}</span>'

        children_html = '\n    '.join(
            self._node_to_html(child, tokens) for child in node.children
        )

        return f'''<div class="container">
    {children_html}
  </div>'''

    def _generate_css_module(self, node: FigmaNode, tokens: Dict) -> str:
        """Generate CSS module"""
        css = ""

        # Container styles
        css += ".container {\n"
        for prop, value in node.styles.items():
            css += f"  {self._camel_to_kebab(prop)}: {value};\n"
        css += "}\n\n"

        # Text styles
        for child in node.children:
            if child.type == ComponentType.TEXT:
                css += ".text {\n"
                for prop, value in child.styles.items():
                    css += f"  {self._camel_to_kebab(prop)}: {value};\n"
                css += "}\n"

        return css

    def _generate_scoped_css(self, node: FigmaNode, tokens: Dict) -> str:
        """Generate scoped CSS for Vue"""
        return self._generate_component_css(node, tokens)

    def _generate_component_css(self, node: FigmaNode, tokens: Dict) -> str:
        """Generate component CSS"""
        return self._generate_css_module(node, tokens)

    def _extract_assets(self, figma_data: Dict) -> Dict[str, str]:
        """Extract image assets"""
        # In production: call Figma API to get image URLs
        # GET https://api.figma.com/v1/images/{file_id}
        return {}

    def _write_component(self, component: GeneratedComponent, components_dir: Path, styles_dir: Path):
        """Write component files to disk"""
        if component.framework == FrameworkType.REACT:
            # Write component file
            comp_file = components_dir / f"{component.name}.tsx"
            with open(comp_file, 'w') as f:
                f.write(component.code)

            # Write CSS module
            css_file = components_dir / f"{component.name}.module.css"
            with open(css_file, 'w') as f:
                f.write(component.styles)

        elif component.framework == FrameworkType.VUE:
            comp_file = components_dir / f"{component.name}.vue"
            with open(comp_file, 'w') as f:
                f.write(component.code)

        elif component.framework == FrameworkType.ANGULAR:
            name_lower = component.name.lower()

            # TypeScript
            ts_file = components_dir / f"{name_lower}.component.ts"
            with open(ts_file, 'w') as f:
                f.write(component.code)

            # Template
            html_file = components_dir / f"{name_lower}.component.html"
            with open(html_file, 'w') as f:
                f.write("<div>Template here</div>")

            # Styles
            css_file = components_dir / f"{name_lower}.component.css"
            with open(css_file, 'w') as f:
                f.write(component.styles)

    def _write_config_files(self, framework: FrameworkType, output_dir: Path):
        """Write framework config files"""
        if framework == FrameworkType.REACT:
            package_json = {
                "name": "figma-export",
                "version": "1.0.0",
                "dependencies": {
                    "react": "^18.2.0",
                    "react-dom": "^18.2.0"
                },
                "devDependencies": {
                    "@types/react": "^18.2.0",
                    "typescript": "^5.0.0"
                }
            }

            with open(output_dir / "package.json", 'w') as f:
                json.dump(package_json, f, indent=2)

    def _sanitize_name(self, name: str) -> str:
        """Sanitize component name"""
        # Remove special characters, convert to PascalCase
        name = ''.join(c for c in name if c.isalnum() or c == ' ')
        words = name.split()
        return ''.join(word.capitalize() for word in words)

    def _camel_to_kebab(self, name: str) -> str:
        """Convert camelCase to kebab-case"""
        result = []
        for i, char in enumerate(name):
            if char.isupper() and i > 0:
                result.append('-')
            result.append(char.lower())
        return ''.join(result)
