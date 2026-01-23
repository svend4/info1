#!/usr/bin/env python3
"""
Visualization tool for project connections

Analyzes markdown files to extract connections and generate visualizations
in multiple formats (DOT, HTML/D3.js, ASCII, JSON).

Part of the ⇑⇓↔ Parallel Bidirectional Development Methodology.

Usage:
    python3 visualize_connections.py --format dot --output graph.dot
    python3 visualize_connections.py --format html --output graph.html
    python3 visualize_connections.py --format ascii
    python3 visualize_connections.py --format json --output graph.json
"""

import os
import re
import json
import argparse
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from collections import defaultdict


class ProjectAnalyzer:
    """Analyzes project structure and extracts connections"""

    def __init__(self, root_path: str = "."):
        self.root = Path(root_path)
        self.documents: Dict[str, Dict] = {}
        self.connections: List[Tuple[str, str, str]] = []

        # Abstraction level patterns
        self.alpha_patterns = {
            r'α=\+4': '+4',
            r'α=\+3': '+3',
            r'α=\+2': '+2',
            r'α=\+1': '+1',
            r'α=0': '0',
            r'α=-1': '-1',
            r'α=-2': '-2',
            r'α=-3': '-3',
            r'α=-4': '-4',
        }

    def scan_project(self):
        """Scan all markdown files in the project"""
        md_files = list(self.root.glob("**/*.md"))

        for md_file in md_files:
            # Skip hidden directories and node_modules
            if any(part.startswith('.') for part in md_file.parts):
                continue
            if 'node_modules' in md_file.parts:
                continue

            self._analyze_file(md_file)

        self._extract_connections()

    def _analyze_file(self, file_path: Path):
        """Analyze a single markdown file"""
        try:
            content = file_path.read_text(encoding='utf-8')
            rel_path = str(file_path.relative_to(self.root))

            # Extract metadata
            alpha_level = self._extract_alpha_level(content)
            cycle = self._extract_cycle(content)
            doc_type = self._infer_type(rel_path, content)

            # Count lines
            lines = len(content.split('\n'))

            # Extract links
            links = self._extract_links(content)

            self.documents[rel_path] = {
                'path': rel_path,
                'alpha': alpha_level,
                'cycle': cycle,
                'type': doc_type,
                'lines': lines,
                'links': links,
                'title': self._extract_title(content)
            }

        except Exception as e:
            print(f"Warning: Could not analyze {file_path}: {e}")

    def _extract_alpha_level(self, content: str) -> Optional[str]:
        """Extract abstraction level from content"""
        for pattern, level in self.alpha_patterns.items():
            if re.search(pattern, content):
                return level
        return None

    def _extract_cycle(self, content: str) -> Optional[int]:
        """Extract CYCLE number from content"""
        match = re.search(r'CYCLE\s+(\d+)', content)
        if match:
            return int(match.group(1))
        return None

    def _infer_type(self, path: str, content: str) -> str:
        """Infer document type from path and content"""
        path_lower = path.lower()
        content_lower = content.lower()

        if 'философия' in path_lower or 'philosophy' in path_lower:
            return 'philosophy'
        elif 'методология' in path_lower or 'methodology' in path_lower:
            return 'methodology'
        elif 'api' in path_lower or 'справка' in path_lower:
            return 'api'
        elif 'example' in path_lower or 'пример' in path_lower:
            return 'examples'
        elif path.endswith('.py'):
            return 'code'
        elif 'readme' in path_lower:
            return 'readme'
        elif 'changelog' in path_lower:
            return 'changelog'
        elif 'резюме' in path_lower or 'summary' in path_lower:
            return 'summary'
        elif 'карта' in path_lower or 'map' in path_lower:
            return 'map'
        elif 'метрик' in path_lower or 'metric' in path_lower:
            return 'metrics'
        elif 'применение' in path_lower or 'application' in path_lower:
            return 'application'
        else:
            return 'document'

    def _extract_title(self, content: str) -> str:
        """Extract document title"""
        match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if match:
            return match.group(1).strip()
        return "Untitled"

    def _extract_links(self, content: str) -> List[str]:
        """Extract markdown links from content"""
        # Pattern: [text](path)
        links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
        return [link[1] for link in links if not link[1].startswith('http')]

    def _extract_connections(self):
        """Extract connections between documents"""
        for doc_path, doc_info in self.documents.items():
            for link in doc_info['links']:
                # Resolve relative link
                target = self._resolve_link(doc_path, link)
                if target and target in self.documents:
                    # Determine connection type
                    conn_type = self._connection_type(doc_info, self.documents[target])
                    self.connections.append((doc_path, target, conn_type))

    def _resolve_link(self, source_path: str, link: str) -> Optional[str]:
        """Resolve relative link to absolute path"""
        try:
            source_dir = Path(source_path).parent
            target_path = (source_dir / link).resolve()
            rel_target = target_path.relative_to(self.root)
            return str(rel_target)
        except:
            return None

    def _connection_type(self, source: Dict, target: Dict) -> str:
        """Determine connection type based on alpha levels"""
        source_alpha = source.get('alpha')
        target_alpha = target.get('alpha')

        if source_alpha and target_alpha:
            try:
                s_level = int(source_alpha)
                t_level = int(target_alpha)

                if abs(s_level - t_level) >= 2:
                    if s_level < t_level:
                        return 'vertical_up'  # ⇑
                    else:
                        return 'vertical_down'  # ⇓
                else:
                    return 'horizontal'  # ↔
            except:
                pass

        return 'unknown'


class VisualizationGenerator:
    """Generate visualizations in multiple formats"""

    def __init__(self, analyzer: ProjectAnalyzer):
        self.analyzer = analyzer

    def generate_dot(self) -> str:
        """Generate GraphViz DOT format"""
        lines = [
            'digraph ProjectConnections {',
            '    rankdir=TB;',
            '    node [shape=box, style=filled];',
            ''
        ]

        # Color scheme by type
        colors = {
            'philosophy': '#FFE6E6',
            'methodology': '#E6F3FF',
            'api': '#E6FFE6',
            'examples': '#FFF9E6',
            'code': '#F0F0F0',
            'readme': '#FFE6F0',
            'summary': '#E6E6FF',
            'map': '#FFFFE6',
            'metrics': '#E6FFFF',
            'document': '#FFFFFF'
        }

        # Add nodes
        for path, info in self.analyzer.documents.items():
            label = info['title']
            color = colors.get(info['type'], '#FFFFFF')
            alpha = f"α={info['alpha']}" if info['alpha'] else ""
            cycle = f"C{info['cycle']}" if info['cycle'] else ""
            meta = f"{alpha} {cycle}".strip()

            if meta:
                label = f"{label}\\n{meta}"

            node_id = self._sanitize_id(path)
            lines.append(f'    {node_id} [label="{label}", fillcolor="{color}"];')

        lines.append('')

        # Add edges
        for source, target, conn_type in self.analyzer.connections:
            source_id = self._sanitize_id(source)
            target_id = self._sanitize_id(target)

            if conn_type == 'vertical_up':
                style = 'color=blue, label="⇑"'
            elif conn_type == 'vertical_down':
                style = 'color=red, label="⇓"'
            elif conn_type == 'horizontal':
                style = 'color=green, label="↔"'
            else:
                style = 'color=gray'

            lines.append(f'    {source_id} -> {target_id} [{style}];')

        lines.append('}')
        return '\n'.join(lines)

    def generate_html(self) -> str:
        """Generate HTML with D3.js visualization"""
        # Prepare data for D3
        nodes = []
        node_ids = {}

        for idx, (path, info) in enumerate(self.analyzer.documents.items()):
            node_ids[path] = idx
            nodes.append({
                'id': idx,
                'name': info['title'],
                'type': info['type'],
                'alpha': info['alpha'],
                'cycle': info['cycle'],
                'path': path
            })

        links = []
        for source, target, conn_type in self.analyzer.connections:
            if source in node_ids and target in node_ids:
                links.append({
                    'source': node_ids[source],
                    'target': node_ids[target],
                    'type': conn_type
                })

        data_json = json.dumps({'nodes': nodes, 'links': links}, ensure_ascii=False)

        html = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Project Connections Visualization</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        body {{
            margin: 0;
            font-family: Arial, sans-serif;
        }}
        #graph {{
            width: 100vw;
            height: 100vh;
        }}
        .node {{
            stroke: #fff;
            stroke-width: 2px;
            cursor: pointer;
        }}
        .link {{
            stroke-opacity: 0.6;
        }}
        .link-vertical_up {{ stroke: blue; }}
        .link-vertical_down {{ stroke: red; }}
        .link-horizontal {{ stroke: green; }}
        .link-unknown {{ stroke: gray; }}
        .tooltip {{
            position: absolute;
            padding: 8px;
            background: rgba(0, 0, 0, 0.8);
            color: white;
            border-radius: 4px;
            pointer-events: none;
            opacity: 0;
            transition: opacity 0.3s;
        }}
    </style>
</head>
<body>
    <div id="graph"></div>
    <div class="tooltip"></div>

    <script>
        const data = {data_json};

        const width = window.innerWidth;
        const height = window.innerHeight;

        const svg = d3.select("#graph")
            .append("svg")
            .attr("width", width)
            .attr("height", height);

        const tooltip = d3.select(".tooltip");

        // Color scheme
        const colorScale = d3.scaleOrdinal()
            .domain(['philosophy', 'methodology', 'api', 'examples', 'code', 'readme', 'summary', 'map', 'metrics', 'document'])
            .range(['#FFE6E6', '#E6F3FF', '#E6FFE6', '#FFF9E6', '#F0F0F0', '#FFE6F0', '#E6E6FF', '#FFFFE6', '#E6FFFF', '#FFFFFF']);

        // Force simulation
        const simulation = d3.forceSimulation(data.nodes)
            .force("link", d3.forceLink(data.links).id(d => d.id).distance(100))
            .force("charge", d3.forceManyBody().strength(-300))
            .force("center", d3.forceCenter(width / 2, height / 2))
            .force("collision", d3.forceCollide().radius(30));

        // Links
        const link = svg.append("g")
            .selectAll("line")
            .data(data.links)
            .enter().append("line")
            .attr("class", d => `link link-${{d.type}}`)
            .attr("stroke-width", 2);

        // Nodes
        const node = svg.append("g")
            .selectAll("circle")
            .data(data.nodes)
            .enter().append("circle")
            .attr("class", "node")
            .attr("r", 10)
            .attr("fill", d => colorScale(d.type))
            .call(d3.drag()
                .on("start", dragstarted)
                .on("drag", dragged)
                .on("end", dragended))
            .on("mouseover", function(event, d) {{
                tooltip
                    .style("opacity", 1)
                    .html(`<strong>${{d.name}}</strong><br>Type: ${{d.type}}<br>α=${{d.alpha || 'N/A'}}<br>Cycle: ${{d.cycle || 'N/A'}}<br>${{d.path}}`);
            }})
            .on("mousemove", function(event) {{
                tooltip
                    .style("left", (event.pageX + 10) + "px")
                    .style("top", (event.pageY - 10) + "px");
            }})
            .on("mouseout", function() {{
                tooltip.style("opacity", 0);
            }});

        // Labels
        const label = svg.append("g")
            .selectAll("text")
            .data(data.nodes)
            .enter().append("text")
            .attr("text-anchor", "middle")
            .attr("dy", -15)
            .style("font-size", "10px")
            .text(d => d.name.substring(0, 20));

        simulation.on("tick", () => {{
            link
                .attr("x1", d => d.source.x)
                .attr("y1", d => d.source.y)
                .attr("x2", d => d.target.x)
                .attr("y2", d => d.target.y);

            node
                .attr("cx", d => d.x)
                .attr("cy", d => d.y);

            label
                .attr("x", d => d.x)
                .attr("y", d => d.y);
        }});

        function dragstarted(event) {{
            if (!event.active) simulation.alphaTarget(0.3).restart();
            event.subject.fx = event.subject.x;
            event.subject.fy = event.subject.y;
        }}

        function dragged(event) {{
            event.subject.fx = event.x;
            event.subject.fy = event.y;
        }}

        function dragended(event) {{
            if (!event.active) simulation.alphaTarget(0);
            event.subject.fx = null;
            event.subject.fy = null;
        }}
    </script>
</body>
</html>'''
        return html

    def generate_ascii(self) -> str:
        """Generate ASCII tree visualization"""
        lines = [
            "Project Structure (⇑⇓↔ Connections)",
            "=" * 50,
            ""
        ]

        # Group by type
        by_type = defaultdict(list)
        for path, info in self.analyzer.documents.items():
            by_type[info['type']].append((path, info))

        for doc_type, docs in sorted(by_type.items()):
            lines.append(f"\n📁 {doc_type.upper()}")
            lines.append("─" * 50)

            for path, info in sorted(docs, key=lambda x: x[1].get('alpha') or '0'):
                alpha = f"[α={info['alpha']}]" if info['alpha'] else ""
                cycle = f"[C{info['cycle']}]" if info['cycle'] else ""
                lines.append(f"  📄 {info['title']}")
                lines.append(f"     {alpha} {cycle} {path}".strip())

                # Show outgoing connections
                outgoing = [t for s, t, _ in self.analyzer.connections if s == path]
                if outgoing:
                    lines.append(f"     → {len(outgoing)} connections")

        # Statistics
        lines.append("\n" + "=" * 50)
        lines.append("STATISTICS")
        lines.append("=" * 50)
        lines.append(f"Total documents: {len(self.analyzer.documents)}")
        lines.append(f"Total connections: {len(self.analyzer.connections)}")

        # Connection types
        conn_types = defaultdict(int)
        for _, _, ctype in self.analyzer.connections:
            conn_types[ctype] += 1

        for ctype, count in sorted(conn_types.items()):
            symbol = {'vertical_up': '⇑', 'vertical_down': '⇓', 'horizontal': '↔'}.get(ctype, '?')
            lines.append(f"  {symbol} {ctype}: {count}")

        return '\n'.join(lines)

    def generate_json(self) -> str:
        """Generate JSON representation"""
        data = {
            'documents': self.analyzer.documents,
            'connections': [
                {
                    'source': s,
                    'target': t,
                    'type': ctype
                }
                for s, t, ctype in self.analyzer.connections
            ],
            'statistics': {
                'total_documents': len(self.analyzer.documents),
                'total_connections': len(self.analyzer.connections),
                'connection_types': dict(
                    (ctype, sum(1 for _, _, c in self.analyzer.connections if c == ctype))
                    for ctype in set(c for _, _, c in self.analyzer.connections)
                )
            }
        }
        return json.dumps(data, indent=2, ensure_ascii=False)

    def _sanitize_id(self, path: str) -> str:
        """Sanitize path for use as node ID"""
        return path.replace('/', '_').replace('.', '_').replace('-', '_')


def main():
    parser = argparse.ArgumentParser(
        description='Visualize project connections following ⇑⇓↔ methodology'
    )
    parser.add_argument(
        '--format',
        choices=['dot', 'html', 'ascii', 'json'],
        default='ascii',
        help='Output format (default: ascii)'
    )
    parser.add_argument(
        '--output',
        type=str,
        help='Output file (default: stdout)'
    )
    parser.add_argument(
        '--root',
        type=str,
        default='.',
        help='Project root directory (default: current directory)'
    )

    args = parser.parse_args()

    # Analyze project
    print("Scanning project...", flush=True)
    analyzer = ProjectAnalyzer(args.root)
    analyzer.scan_project()

    print(f"Found {len(analyzer.documents)} documents and {len(analyzer.connections)} connections")

    # Generate visualization
    generator = VisualizationGenerator(analyzer)

    if args.format == 'dot':
        output = generator.generate_dot()
    elif args.format == 'html':
        output = generator.generate_html()
    elif args.format == 'ascii':
        output = generator.generate_ascii()
    elif args.format == 'json':
        output = generator.generate_json()
    else:
        print(f"Unknown format: {args.format}")
        return 1

    # Write output
    if args.output:
        Path(args.output).write_text(output, encoding='utf-8')
        print(f"Output written to: {args.output}")
    else:
        print(output)

    return 0


if __name__ == '__main__':
    exit(main())
