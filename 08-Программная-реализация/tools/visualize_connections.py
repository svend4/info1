#!/usr/bin/env python3
"""
Инструмент визуализации связей между документами проекта

Уровень абстракции: α=-3 (инструменты)
Назначение: Анализ и визуализация графа зависимостей документов

Возможности:
- Парсинг всех .md файлов проекта
- Извлечение ссылок между документами
- Построение графа связей
- Генерация визуализации (GraphViz DOT, HTML, ASCII)
- Расчет метрик (CD, VT и др.)
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict
import json


class DocumentGraph:
    """Граф связей между документами проекта"""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.documents: Dict[str, Dict] = {}  # путь -> метаданные
        self.connections: List[Tuple[str, str, str]] = []  # (from, to, type)
        self.abstraction_levels: Dict[str, int] = {}  # путь -> уровень α

    def scan_project(self):
        """Сканирование проекта для поиска документов"""
        print(f"🔍 Сканирование проекта: {self.project_root}")

        for md_file in self.project_root.rglob("*.md"):
            if ".git" in str(md_file) or "node_modules" in str(md_file):
                continue

            rel_path = md_file.relative_to(self.project_root)
            self.documents[str(rel_path)] = {
                "path": str(rel_path),
                "name": md_file.stem,
                "size": md_file.stat().st_size,
                "lines": 0,
                "alpha": None,
            }

        print(f"✅ Найдено документов: {len(self.documents)}")

    def extract_connections(self):
        """Извлечение связей между документами"""
        print("🔗 Извлечение связей...")

        link_pattern = re.compile(r'\[([^\]]+)\]\(([^\)]+)\)')
        reference_pattern = re.compile(r'См\.\s+также:\s*([^\n]+)', re.IGNORECASE)
        alpha_pattern = re.compile(r'α\s*=\s*([+-]?\d+)')

        for doc_path, doc_info in self.documents.items():
            full_path = self.project_root / doc_path

            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')
                    doc_info['lines'] = len(lines)

                    # Извлечь уровень абстракции
                    alpha_match = alpha_pattern.search(content)
                    if alpha_match:
                        doc_info['alpha'] = int(alpha_match.group(1))
                        self.abstraction_levels[doc_path] = doc_info['alpha']

                    # Извлечь markdown ссылки
                    for match in link_pattern.finditer(content):
                        link_text = match.group(1)
                        link_target = match.group(2)

                        # Игнорировать внешние ссылки
                        if link_target.startswith(('http://', 'https://', '#')):
                            continue

                        # Нормализовать путь
                        target_path = self._normalize_path(doc_path, link_target)
                        if target_path in self.documents:
                            self.connections.append((
                                doc_path,
                                target_path,
                                "markdown_link"
                            ))

                    # Извлечь упоминания из "См. также:"
                    for match in reference_pattern.finditer(content):
                        references = match.group(1)
                        for ref_doc in self.documents.keys():
                            doc_name = Path(ref_doc).stem
                            if doc_name in references or doc_name.replace('-', ' ') in references:
                                self.connections.append((
                                    doc_path,
                                    ref_doc,
                                    "reference"
                                ))

            except Exception as e:
                print(f"⚠️  Ошибка чтения {doc_path}: {e}")

        print(f"✅ Найдено связей: {len(self.connections)}")

    def _normalize_path(self, from_path: str, link: str) -> str:
        """Нормализация пути ссылки"""
        # Убрать якоря
        link = link.split('#')[0]

        # Если абсолютный путь от корня проекта
        if link.startswith('/'):
            return link[1:]

        # Относительный путь
        from_dir = Path(from_path).parent
        target = (from_dir / link).resolve()

        try:
            rel = target.relative_to(self.project_root)
            return str(rel)
        except ValueError:
            return link

    def calculate_metrics(self) -> Dict[str, float]:
        """Расчет метрик графа"""
        print("📊 Расчет метрик...")

        n = len(self.documents)
        m = len(self.connections)

        # Connectivity Density (CD)
        max_connections = n * (n - 1) / 2
        cd = (m / max_connections * 100) if max_connections > 0 else 0

        # Средняя степень вершины
        in_degree = defaultdict(int)
        out_degree = defaultdict(int)
        for from_doc, to_doc, _ in self.connections:
            out_degree[from_doc] += 1
            in_degree[to_doc] += 1

        avg_degree = sum(out_degree.values()) / n if n > 0 else 0

        # Уровни абстракции
        alpha_distribution = defaultdict(int)
        for alpha in self.abstraction_levels.values():
            alpha_distribution[alpha] += 1

        # Вертикальная трассируемость (VT)
        # Количество документов, связанных с документами других уровней
        vertical_connections = 0
        for from_doc, to_doc, _ in self.connections:
            alpha_from = self.abstraction_levels.get(from_doc)
            alpha_to = self.abstraction_levels.get(to_doc)
            if alpha_from is not None and alpha_to is not None:
                if abs(alpha_from - alpha_to) >= 2:
                    vertical_connections += 1

        vt = (vertical_connections / m * 100) if m > 0 else 0

        metrics = {
            "documents": n,
            "connections": m,
            "connectivity_density": cd,
            "avg_degree": avg_degree,
            "vertical_traceability": vt,
            "alpha_distribution": dict(alpha_distribution),
        }

        print(f"✅ Метрики рассчитаны:")
        print(f"   📄 Документов: {n}")
        print(f"   🔗 Связей: {m}")
        print(f"   📊 CD (Connectivity Density): {cd:.1f}%")
        print(f"   📈 Средняя степень: {avg_degree:.1f}")
        print(f"   ⬍ VT (Vertical Traceability): {vt:.1f}%")

        return metrics

    def generate_dot(self, output_file: str):
        """Генерация GraphViz DOT файла"""
        print(f"🎨 Генерация GraphViz DOT: {output_file}")

        # Цвета для уровней абстракции
        alpha_colors = {
            4: "#8B0000",    # темно-красный (философия)
            3: "#CD5C5C",    # красный
            2: "#F08080",    # светло-красный
            1: "#FFA500",    # оранжевый
            0: "#FFD700",    # золотой (дизайн)
            -1: "#90EE90",   # светло-зеленый
            -2: "#32CD32",   # зеленый
            -3: "#008000",   # темно-зеленый
            -4: "#006400",   # очень темно-зеленый (код)
        }

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("digraph DocumentGraph {\n")
            f.write("  rankdir=TB;\n")
            f.write("  node [shape=box, style=filled];\n")
            f.write("  edge [color=gray50];\n\n")

            # Узлы (документы)
            for doc_path, doc_info in self.documents.items():
                alpha = doc_info.get('alpha')
                color = alpha_colors.get(alpha, "#D3D3D3")
                label = doc_info['name']

                # Сократить длинные имена
                if len(label) > 30:
                    label = label[:27] + "..."

                alpha_label = f"α={alpha}" if alpha is not None else ""
                full_label = f"{label}\\n{alpha_label}" if alpha_label else label

                node_id = self._sanitize_id(doc_path)
                f.write(f'  "{node_id}" [label="{full_label}", fillcolor="{color}"];\n')

            f.write("\n")

            # Ребра (связи)
            for from_doc, to_doc, conn_type in self.connections:
                from_id = self._sanitize_id(from_doc)
                to_id = self._sanitize_id(to_doc)
                style = "solid" if conn_type == "markdown_link" else "dashed"
                f.write(f'  "{from_id}" -> "{to_id}" [style={style}];\n')

            # Легенда
            f.write("\n  // Легенда\n")
            f.write('  subgraph cluster_legend {\n')
            f.write('    label="Уровни абстракции α";\n')
            for alpha in sorted(alpha_colors.keys(), reverse=True):
                color = alpha_colors[alpha]
                label = self._alpha_label(alpha)
                f.write(f'    "legend_{alpha}" [label="α={alpha:+d}\\n{label}", fillcolor="{color}"];\n')
            f.write('  }\n')

            f.write("}\n")

        print(f"✅ DOT файл создан: {output_file}")
        print(f"   Чтобы визуализировать: dot -Tpng {output_file} -o graph.png")
        print(f"   Или: dot -Tsvg {output_file} -o graph.svg")

    def _sanitize_id(self, path: str) -> str:
        """Санитизация ID для DOT"""
        return path.replace('/', '_').replace('-', '_').replace('.', '_')

    def _alpha_label(self, alpha: int) -> str:
        """Метка для уровня абстракции"""
        labels = {
            4: "Философия",
            3: "Онтология",
            2: "Модель",
            1: "Архитектура",
            0: "Дизайн",
            -1: "Модули",
            -2: "Компоненты",
            -3: "Примеры",
            -4: "Код",
        }
        return labels.get(alpha, "?")

    def generate_ascii(self) -> str:
        """Генерация ASCII представления графа"""
        print("🎨 Генерация ASCII графа...")

        output = []
        output.append("=" * 70)
        output.append("ГРАФ СВЯЗЕЙ ДОКУМЕНТОВ ПРОЕКТА")
        output.append("=" * 70)
        output.append("")

        # Группировка по уровням абстракции
        by_alpha = defaultdict(list)
        no_alpha = []
        for doc_path, doc_info in self.documents.items():
            alpha = doc_info.get('alpha')
            if alpha is not None:
                by_alpha[alpha].append(doc_path)
            else:
                no_alpha.append(doc_path)

        # Вывод по уровням (от высоких к низким)
        for alpha in sorted(by_alpha.keys(), reverse=True):
            docs = by_alpha[alpha]
            alpha_label = self._alpha_label(alpha)
            output.append(f"[α={alpha:+d}] {alpha_label}")
            output.append("-" * 70)

            for doc in docs:
                doc_info = self.documents[doc]
                name = doc_info['name']

                # Найти связи от этого документа
                outgoing = [to for fr, to, _ in self.connections if fr == doc]
                incoming = [fr for fr, to, _ in self.connections if to == doc]

                output.append(f"  📄 {name}")
                if outgoing:
                    output.append(f"     ↳ Ссылается на: {len(outgoing)} документ(ов)")
                if incoming:
                    output.append(f"     ↰ Ссылаются сюда: {len(incoming)} документ(ов)")

            output.append("")

        # Документы без указанного уровня абстракции
        if no_alpha:
            output.append("[α=?] Без указанного уровня")
            output.append("-" * 70)
            for doc in no_alpha:
                doc_info = self.documents[doc]
                name = doc_info['name']
                outgoing = [to for fr, to, _ in self.connections if fr == doc]
                incoming = [fr for fr, to, _ in self.connections if to == doc]

                output.append(f"  📄 {name}")
                if outgoing:
                    output.append(f"     ↳ Ссылается на: {len(outgoing)} документ(ов)")
                if incoming:
                    output.append(f"     ↰ Ссылаются сюда: {len(incoming)} документ(ов)")
            output.append("")

        result = "\n".join(output)
        print("✅ ASCII граф сгенерирован")
        return result

    def generate_html(self, output_file: str):
        """Генерация интерактивной HTML визуализации (D3.js)"""
        print(f"🎨 Генерация HTML визуализации: {output_file}")

        # Подготовка данных для D3.js
        nodes = []
        for idx, (doc_path, doc_info) in enumerate(self.documents.items()):
            nodes.append({
                "id": idx,
                "name": doc_info['name'],
                "path": doc_path,
                "alpha": doc_info.get('alpha'),
                "lines": doc_info.get('lines', 0),
            })

        # Создать индекс путь -> ID
        path_to_id = {doc_path: idx for idx, doc_path in enumerate(self.documents.keys())}

        links = []
        for from_doc, to_doc, conn_type in self.connections:
            if from_doc in path_to_id and to_doc in path_to_id:
                links.append({
                    "source": path_to_id[from_doc],
                    "target": path_to_id[to_doc],
                    "type": conn_type,
                })

        graph_data = {
            "nodes": nodes,
            "links": links,
        }

        html_template = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Граф связей документов</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        body {
            margin: 0;
            padding: 20px;
            font-family: Arial, sans-serif;
            background: #f5f5f5;
        }

        #graph {
            width: 100%;
            height: 800px;
            border: 1px solid #ccc;
            background: white;
        }

        .node circle {
            stroke: #fff;
            stroke-width: 2px;
        }

        .node text {
            font-size: 10px;
            pointer-events: none;
        }

        .link {
            stroke: #999;
            stroke-opacity: 0.6;
        }

        .link.reference {
            stroke-dasharray: 5,5;
        }

        #info {
            margin-top: 20px;
            padding: 15px;
            background: white;
            border: 1px solid #ccc;
        }

        .legend {
            margin-top: 10px;
        }

        .legend-item {
            display: inline-block;
            margin-right: 15px;
        }

        .legend-color {
            display: inline-block;
            width: 20px;
            height: 20px;
            margin-right: 5px;
            vertical-align: middle;
        }
    </style>
</head>
<body>
    <h1>📊 Граф связей документов проекта</h1>

    <div class="legend">
        <strong>Уровни абстракции α:</strong>
        <div class="legend-item"><span class="legend-color" style="background: #8B0000;"></span>α=+4 (Философия)</div>
        <div class="legend-item"><span class="legend-color" style="background: #CD5C5C;"></span>α=+3 (Онтология)</div>
        <div class="legend-item"><span class="legend-color" style="background: #F08080;"></span>α=+2 (Модель)</div>
        <div class="legend-item"><span class="legend-color" style="background: #FFA500;"></span>α=+1 (Архитектура)</div>
        <div class="legend-item"><span class="legend-color" style="background: #FFD700;"></span>α=0 (Дизайн)</div>
        <div class="legend-item"><span class="legend-color" style="background: #90EE90;"></span>α=-1 (Модули)</div>
        <div class="legend-item"><span class="legend-color" style="background: #32CD32;"></span>α=-2 (Компоненты)</div>
        <div class="legend-item"><span class="legend-color" style="background: #008000;"></span>α=-3 (Примеры)</div>
        <div class="legend-item"><span class="legend-color" style="background: #006400;"></span>α=-4 (Код)</div>
    </div>

    <svg id="graph"></svg>

    <div id="info">
        <p>💡 <strong>Инструкция:</strong></p>
        <ul>
            <li>Кликните на узел для просмотра информации</li>
            <li>Перетаскивайте узлы для перестановки</li>
            <li>Сплошные линии — прямые ссылки, пунктирные — упоминания</li>
        </ul>
        <div id="node-info"></div>
    </div>

    <script>
        const data = """ + json.dumps(graph_data, ensure_ascii=False) + """;

        const width = document.getElementById('graph').clientWidth;
        const height = 800;

        const svg = d3.select("#graph")
            .attr("viewBox", [0, 0, width, height]);

        const alphaColors = {
            4: "#8B0000", 3: "#CD5C5C", 2: "#F08080", 1: "#FFA500",
            0: "#FFD700", "-1": "#90EE90", "-2": "#32CD32", "-3": "#008000", "-4": "#006400"
        };

        const simulation = d3.forceSimulation(data.nodes)
            .force("link", d3.forceLink(data.links).id(d => d.id).distance(100))
            .force("charge", d3.forceManyBody().strength(-300))
            .force("center", d3.forceCenter(width / 2, height / 2))
            .force("collision", d3.forceCollide().radius(30));

        const link = svg.append("g")
            .selectAll("line")
            .data(data.links)
            .join("line")
            .attr("class", d => "link " + d.type)
            .attr("stroke-width", 1);

        const node = svg.append("g")
            .selectAll("g")
            .data(data.nodes)
            .join("g")
            .attr("class", "node")
            .call(drag(simulation))
            .on("click", showNodeInfo);

        node.append("circle")
            .attr("r", d => Math.sqrt(d.lines / 10) + 5)
            .attr("fill", d => alphaColors[d.alpha] || "#D3D3D3");

        node.append("text")
            .text(d => d.name.substring(0, 20))
            .attr("x", 0)
            .attr("y", -10)
            .attr("text-anchor", "middle");

        simulation.on("tick", () => {
            link
                .attr("x1", d => d.source.x)
                .attr("y1", d => d.source.y)
                .attr("x2", d => d.target.x)
                .attr("y2", d => d.target.y);

            node
                .attr("transform", d => `translate(${d.x},${d.y})`);
        });

        function drag(simulation) {
            function dragstarted(event) {
                if (!event.active) simulation.alphaTarget(0.3).restart();
                event.subject.fx = event.subject.x;
                event.subject.fy = event.subject.y;
            }

            function dragged(event) {
                event.subject.fx = event.x;
                event.subject.fy = event.y;
            }

            function dragended(event) {
                if (!event.active) simulation.alphaTarget(0);
                event.subject.fx = null;
                event.subject.fy = null;
            }

            return d3.drag()
                .on("start", dragstarted)
                .on("drag", dragged)
                .on("end", dragended);
        }

        function showNodeInfo(event, d) {
            const inLinks = data.links.filter(l => l.target.id === d.id).length;
            const outLinks = data.links.filter(l => l.source.id === d.id).length;

            document.getElementById("node-info").innerHTML = `
                <h3>📄 ${d.name}</h3>
                <p><strong>Путь:</strong> ${d.path}</p>
                <p><strong>Уровень абстракции:</strong> α=${d.alpha !== null ? d.alpha : 'не указан'}</p>
                <p><strong>Строк:</strong> ${d.lines}</p>
                <p><strong>Входящих связей:</strong> ${inLinks}</p>
                <p><strong>Исходящих связей:</strong> ${outLinks}</p>
            `;
        }
    </script>
</body>
</html>
"""

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_template)

        print(f"✅ HTML визуализация создана: {output_file}")
        print(f"   Откройте в браузере для интерактивного просмотра")

    def save_metrics(self, output_file: str):
        """Сохранение метрик в JSON"""
        metrics = self.calculate_metrics()

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(metrics, f, indent=2, ensure_ascii=False)

        print(f"✅ Метрики сохранены: {output_file}")


def main():
    """Главная функция"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Визуализация связей между документами проекта"
    )
    parser.add_argument(
        "--project-root",
        default=".",
        help="Корневая директория проекта (по умолчанию: текущая)"
    )
    parser.add_argument(
        "--output-dir",
        default="./visualizations",
        help="Директория для сохранения результатов"
    )
    parser.add_argument(
        "--format",
        choices=["all", "dot", "html", "ascii", "json"],
        default="all",
        help="Формат вывода"
    )

    args = parser.parse_args()

    # Создать граф
    graph = DocumentGraph(args.project_root)

    # Сканировать проект
    graph.scan_project()
    graph.extract_connections()

    # Рассчитать метрики
    metrics = graph.calculate_metrics()

    # Создать директорию для результатов
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Генерация визуализаций
    if args.format in ("all", "dot"):
        graph.generate_dot(str(output_dir / "document_graph.dot"))

    if args.format in ("all", "html"):
        graph.generate_html(str(output_dir / "document_graph.html"))

    if args.format in ("all", "ascii"):
        ascii_output = graph.generate_ascii()
        with open(output_dir / "document_graph.txt", 'w', encoding='utf-8') as f:
            f.write(ascii_output)
        print(f"✅ ASCII граф сохранен: {output_dir / 'document_graph.txt'}")

    if args.format in ("all", "json"):
        graph.save_metrics(str(output_dir / "metrics.json"))

    print("\n" + "=" * 70)
    print("✅ ВИЗУАЛИЗАЦИЯ ЗАВЕРШЕНА")
    print("=" * 70)
    print(f"📁 Результаты в директории: {output_dir}")
    print("\n💡 Рекомендации:")
    print("   1. Откройте document_graph.html в браузере")
    print("   2. Если есть GraphViz: dot -Tpng document_graph.dot -o graph.png")
    print("   3. Изучите метрики в metrics.json")


if __name__ == "__main__":
    main()
