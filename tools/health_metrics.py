#!/usr/bin/env python3
"""
Health Metrics Calculator for ⇑⇓↔ Projects

Automatically calculates project health metrics:
- CD (Connectivity Density): 10-20% optimal
- VT (Vertical Traceability): 50-70% optimal
- CR (Convergence Rate): 0.7-1.5 optimal
- DB (Directional Balance): <30% optimal

Part of the Parallel Bidirectional Development Methodology.

Уровень абстракции: α=-4 (исполняемый код)

Вертикальные связи (⇑ к философии и концепциям):
    ⇑ ../МЕТРИКИ-ЗДОРОВЬЯ.md (α=+2) — полное описание метрик и их значение
    ⇑ ../МЕТА-АНАЛИЗ-МЕТОДОЛОГИИ.md (α=+3) — рефлексивный анализ методологии через метрики
    ⇑ ../01-Концепция/МЕТОДОЛОГИЯ-ПАРАЛЛЕЛЬНОГО-РАЗВИТИЯ.md (α=+1) — методология ⇑⇓↔
    ⇑ ../ЭВОЛЮЦИЯ-МЕТОДОЛОГИИ.md (α=+2) — как метрики эволюционировали
    ⇑ ../01-Концепция/ФИЛОСОФИЯ-ПРОЕКТА.md (α=+3) — принцип измеримости и адаптации
    ⇑ ../ЭТАП-6-САМОСОВЕРШЕНСТВОВАНИЕ.md (α=+2) — концептуальная основа автоматического улучшения

Горизонтальные связи (↔ другие инструменты α=-4):
    ↔ self_improvement.py — использует метрики для диагностики
    ↔ predictive_warnings.py — использует метрики для прогнозов
    ↔ adaptive_metrics.py — адаптирует пороги метрик
    ↔ save_metrics.py — сохраняет историю метрик
    ↔ visualize_connections.py — визуализирует связи для расчёта метрик

Usage:
    python3 health_metrics.py                    # Show all metrics
    python3 health_metrics.py --metric cd        # Show only CD
    python3 health_metrics.py --json             # JSON output
    python3 health_metrics.py --check-thresholds # Exit 1 if out of range
"""

import os
import re
import json
import math
import argparse
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from collections import defaultdict
from datetime import datetime


class HealthMetricsCalculator:
    """Calculate project health metrics"""

    def __init__(self, root_path: str = "."):
        self.root = Path(root_path)
        self.documents: Dict[str, Dict] = {}
        self.connections: List[Tuple[str, str, str, int]] = []
        self.cycles: List[Tuple[int, int]] = []  # (cycle_num, new_docs)

        # Thresholds (default, will be replaced by adaptive if available)
        self.thresholds = {
            'cd': {'min': 10.0, 'max': 20.0, 'unit': '%'},
            'vt': {'min': 50.0, 'max': 70.0, 'unit': '%'},
            'cr': {'min': 0.7, 'max': 1.5, 'unit': ''},
            'db': {'min': 0.0, 'max': 30.0, 'unit': '%'}
        }

        # Load adaptive thresholds if available
        self._load_adaptive_thresholds()

    def _load_adaptive_thresholds(self):
        """Load adaptive thresholds from adaptive_metrics.py if available"""
        try:
            from adaptive_metrics import AdaptiveThresholdOptimizer

            optimizer = AdaptiveThresholdOptimizer(str(self.root))
            characteristics = optimizer.analyze_project_characteristics()
            project_type = characteristics.get('type', 'info_system')

            # Get recommendations for project type
            recommendations = optimizer.recommend_thresholds_for_project_type(project_type)

            # Apply size and maturity adjustments
            size = characteristics.get('size', 'medium')
            maturity = characteristics.get('maturity', 'mature')

            size_multipliers = {'small': 0.9, 'medium': 1.0, 'large': 1.1}
            maturity_multipliers = {'early': 1.2, 'developing': 1.1, 'mature': 1.0}

            size_mult = size_multipliers.get(size, 1.0)
            maturity_mult = maturity_multipliers.get(maturity, 1.0)

            # Update thresholds
            for metric in ['cd', 'vt', 'cr', 'db']:
                if metric in recommendations:
                    rec = recommendations[metric]
                    self.thresholds[metric]['min'] = round(rec['min'] * size_mult * maturity_mult, 1)
                    self.thresholds[metric]['max'] = round(rec['max'] * size_mult * maturity_mult, 1)

        except Exception:
            # If adaptive metrics not available, use default thresholds
            pass

    def analyze(self):
        """Analyze project and calculate all metrics"""
        self._scan_documents()
        self._extract_connections()
        self._extract_cycle_data()

    def _scan_documents(self):
        """Scan all markdown files"""
        md_files = list(self.root.glob("**/*.md"))

        for md_file in md_files:
            # Skip hidden directories
            if any(part.startswith('.') for part in md_file.parts):
                continue
            if 'node_modules' in md_file.parts:
                continue

            try:
                content = md_file.read_text(encoding='utf-8')
                rel_path = str(md_file.relative_to(self.root))

                alpha = self._extract_alpha(content)
                cycle = self._extract_cycle(content)
                direction = self._extract_direction(content, alpha)
                lines = len(content.split('\n'))

                self.documents[rel_path] = {
                    'alpha': alpha,
                    'cycle': cycle,
                    'direction': direction,
                    'lines': lines,
                    'links': self._extract_links(content)
                }

            except Exception as e:
                pass  # Skip problematic files

    def _extract_alpha(self, content: str) -> Optional[int]:
        """Extract alpha level (abstraction level)"""
        patterns = [
            (r'α=\+4|α=4', 4),
            (r'α=\+3|α=3', 3),
            (r'α=\+2|α=2', 2),
            (r'α=\+1|α=1', 1),
            (r'α=0', 0),
            (r'α=-1', -1),
            (r'α=-2', -2),
            (r'α=-3', -3),
            (r'α=-4', -4),
        ]

        for pattern, level in patterns:
            if re.search(pattern, content):
                return level
        return None

    def _extract_cycle(self, content: str) -> Optional[int]:
        """Extract CYCLE number"""
        match = re.search(r'CYCLE\s+(\d+)', content)
        if match:
            return int(match.group(1))
        return None

    def _extract_direction(self, content: str, alpha: Optional[int] = None) -> Optional[str]:
        """
        Extract development direction (⇑, ⇓, ↔) based on abstraction level

        Правильная логика определения направления:
        - ⇑ UP: обобщающие документы (α > 0) - философия, теория, методология
        - ⇓ DOWN: детализирующие документы (α < 0) - спецификации, код, примеры
        - ↔ HORIZONTAL: связующие документы (α = 0) - архитектура, индексы
        """
        if alpha is not None:
            if alpha > 0:
                return 'up'
            elif alpha < 0:
                return 'down'
            else:  # alpha == 0
                return 'horizontal'

        # Fallback: старая логика (только если α не определен)
        if '⇑' in content or 'ВВЕРХ' in content or 'UP' in content.upper():
            return 'up'
        elif '⇓' in content or 'ВНИЗ' in content or 'DOWN' in content.upper():
            return 'down'
        elif '↔' in content or 'СВЯЗИ' in content or 'HORIZONTAL' in content.upper():
            return 'horizontal'
        return None

    def _extract_links(self, content: str) -> List[str]:
        """Extract markdown links"""
        links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
        # Filter out HTTP links and anchors-only
        result = []
        for link in links:
            path = link[1]
            # Skip HTTP/HTTPS links
            if path.startswith('http://') or path.startswith('https://'):
                continue
            # Skip anchor-only links
            if path.startswith('#'):
                continue
            result.append(path)
        return result

    def _extract_connections(self):
        """Extract connections between documents"""
        for doc_path, doc_info in self.documents.items():
            for link in doc_info['links']:
                target = self._resolve_link(doc_path, link)
                if target and target in self.documents:
                    source_alpha = doc_info.get('alpha')
                    target_alpha = self.documents[target].get('alpha')

                    # Calculate alpha delta
                    if source_alpha is not None and target_alpha is not None:
                        delta = abs(source_alpha - target_alpha)
                    else:
                        delta = 0

                    # Determine connection type
                    if delta >= 2:
                        conn_type = 'vertical'
                    else:
                        conn_type = 'horizontal'

                    self.connections.append((doc_path, target, conn_type, delta))

    def _resolve_link(self, source_path: str, link: str) -> Optional[str]:
        """Resolve relative link"""
        try:
            # Remove anchor if present (path.md#anchor -> path.md)
            clean_link = link.split('#')[0]
            if not clean_link:
                return None

            source_dir = Path(source_path).parent

            # Try to resolve the link
            if clean_link.startswith('/'):
                # Absolute path from root
                target_path = (self.root / clean_link.lstrip('/')).resolve()
            else:
                # Relative path from source directory
                target_path = (source_dir / clean_link).resolve()

            # Check if path is within project root
            try:
                rel_target = target_path.relative_to(self.root.resolve())
            except ValueError:
                # Path is outside project root
                return None

            # Normalize to string with forward slashes
            rel_target_str = str(rel_target).replace('\\', '/')

            return rel_target_str
        except Exception:
            return None

    def _extract_cycle_data(self):
        """Extract data about cycles"""
        docs_by_cycle = defaultdict(int)

        for doc_info in self.documents.values():
            cycle = doc_info.get('cycle')
            if cycle:
                docs_by_cycle[cycle] += 1

        self.cycles = sorted(docs_by_cycle.items())

    def calculate_cd(self) -> float:
        """
        Calculate CD (Connectivity Density)

        Formula: CD = (actual_connections / max_possible_connections) × 100%
        where max_possible_connections = N × (N - 1) / 2

        Optimal range: 10-20%
        """
        n = len(self.documents)
        if n <= 1:
            return 0.0

        actual_connections = len(self.connections)
        max_connections = n * (n - 1) / 2

        cd = (actual_connections / max_connections) * 100
        return round(cd, 2)

    def calculate_vt(self) -> float:
        """
        Calculate VT (Vertical Traceability)

        Formula: VT = (vertical_connections / total_connections) × 100%
        where vertical_connection = connection with |Δα| ≥ 2

        Optimal range: 50-70%
        """
        if not self.connections:
            return 0.0

        vertical_connections = sum(1 for _, _, ctype, _ in self.connections if ctype == 'vertical')
        total_connections = len(self.connections)

        vt = (vertical_connections / total_connections) * 100
        return round(vt, 2)

    def calculate_cr(self) -> float:
        """
        Calculate CR (Convergence Rate)

        Formula: CR = average(new_docs_in_cycle_N / new_docs_in_cycle_N-1)

        Optimal range: 0.7-1.5
        - CR < 0.7: Project declining too fast
        - CR 0.7-1.0: Healthy stabilization
        - CR 1.0-1.5: Healthy growth
        - CR > 1.5: Explosive growth (may indicate lack of focus)
        """
        if len(self.cycles) < 2:
            return 1.0

        ratios = []
        for i in range(1, len(self.cycles)):
            prev_cycle, prev_docs = self.cycles[i - 1]
            curr_cycle, curr_docs = self.cycles[i]

            if prev_docs > 0:
                ratio = curr_docs / prev_docs
                ratios.append(ratio)

        if not ratios:
            return 1.0

        cr = sum(ratios) / len(ratios)
        return round(cr, 2)

    def calculate_db(self) -> float:
        """
        Calculate DB (Directional Balance)

        Formula: DB = (std_dev(⇑, ⇓, ↔) / mean(⇑, ⇓, ↔)) × 100%

        Optimal range: < 30%
        - DB < 20%: Excellent balance
        - DB 20-30%: Good balance
        - DB 30-50%: Moderate imbalance
        - DB > 50%: Significant imbalance (one direction dominates)
        """
        # Count documents by direction
        up_count = sum(1 for d in self.documents.values() if d.get('direction') == 'up')
        down_count = sum(1 for d in self.documents.values() if d.get('direction') == 'down')
        horiz_count = sum(1 for d in self.documents.values() if d.get('direction') == 'horizontal')

        values = [up_count, down_count, horiz_count]

        # Calculate mean
        mean = sum(values) / len(values)
        if mean == 0:
            return 0.0

        # Calculate standard deviation
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        std_dev = math.sqrt(variance)

        # Calculate DB
        db = (std_dev / mean) * 100
        return round(db, 2)

    def get_all_metrics(self) -> Dict:
        """Get all metrics with evaluations"""
        metrics = {
            'cd': self.calculate_cd(),
            'vt': self.calculate_vt(),
            'cr': self.calculate_cr(),
            'db': self.calculate_db()
        }

        # Add evaluations
        result = {}
        for metric, value in metrics.items():
            threshold = self.thresholds[metric]
            result[metric] = {
                'value': value,
                'unit': threshold['unit'],
                'threshold': {
                    'min': threshold['min'],
                    'max': threshold['max']
                },
                'status': self._evaluate_metric(metric, value)
            }

        # Add metadata
        result['metadata'] = {
            'total_documents': len(self.documents),
            'total_connections': len(self.connections),
            'total_cycles': len(self.cycles),
            'analysis_date': datetime.now().isoformat()
        }

        return result

    def _evaluate_metric(self, metric: str, value: float) -> str:
        """Evaluate metric status"""
        threshold = self.thresholds[metric]

        if metric in ['cd', 'vt', 'cr']:
            # These have min-max optimal range
            if threshold['min'] <= value <= threshold['max']:
                return 'optimal'
            elif value < threshold['min']:
                return 'below'
            else:
                return 'above'
        elif metric == 'db':
            # DB should be below max
            if value < 20.0:
                return 'excellent'
            elif value <= threshold['max']:
                return 'good'
            elif value <= 50.0:
                return 'moderate'
            else:
                return 'poor'

        return 'unknown'

    def detect_antipatterns(self) -> Dict:
        """Detect anti-patterns in project structure"""
        antipatterns = {
            'orphan_documents': [],
            'dead_ends': [],
            'hub_documents': [],
            'missing_alpha': [],
            'unbalanced_directions': {},
            'empty_cycles': [],
            'isolated_clusters': []
        }

        # Build connection graph
        outgoing = defaultdict(list)
        incoming = defaultdict(list)

        for source, target, conn_type, delta in self.connections:
            outgoing[source].append(target)
            incoming[target].append(source)

        # 1. Orphan Documents (no connections at all)
        for doc_path in self.documents:
            if doc_path not in outgoing and doc_path not in incoming:
                antipatterns['orphan_documents'].append({
                    'path': doc_path,
                    'title': self.documents[doc_path].get('title', 'Untitled'),
                    'severity': 'high'
                })

        # 2. Dead Ends (no outgoing connections)
        for doc_path in self.documents:
            if doc_path not in outgoing and doc_path in incoming:
                antipatterns['dead_ends'].append({
                    'path': doc_path,
                    'title': self.documents[doc_path].get('title', 'Untitled'),
                    'incoming_count': len(incoming[doc_path]),
                    'severity': 'medium'
                })

        # 3. Hub Documents (too many connections)
        HUB_THRESHOLD = 20
        for doc_path in outgoing:
            connection_count = len(outgoing[doc_path]) + len(incoming.get(doc_path, []))
            if connection_count > HUB_THRESHOLD:
                antipatterns['hub_documents'].append({
                    'path': doc_path,
                    'title': self.documents[doc_path].get('title', 'Untitled'),
                    'connection_count': connection_count,
                    'severity': 'medium'
                })

        # 4. Missing Alpha (documents without α-level)
        for doc_path, doc_info in self.documents.items():
            if doc_info.get('alpha') is None:
                antipatterns['missing_alpha'].append({
                    'path': doc_path,
                    'title': doc_info.get('title', 'Untitled'),
                    'severity': 'low'
                })

        # 5. Unbalanced Directions (check if one direction dominates)
        up_count = sum(1 for d in self.documents.values() if d.get('direction') == 'up')
        down_count = sum(1 for d in self.documents.values() if d.get('direction') == 'down')
        horiz_count = sum(1 for d in self.documents.values() if d.get('direction') == 'horizontal')

        total_directional = up_count + down_count + horiz_count
        if total_directional > 0:
            up_pct = (up_count / total_directional) * 100
            down_pct = (down_count / total_directional) * 100
            horiz_pct = (horiz_count / total_directional) * 100

            antipatterns['unbalanced_directions'] = {
                'up': {'count': up_count, 'percentage': round(up_pct, 1)},
                'down': {'count': down_count, 'percentage': round(down_pct, 1)},
                'horizontal': {'count': horiz_count, 'percentage': round(horiz_pct, 1)},
                'severity': 'high' if max(up_pct, down_pct, horiz_pct) > 70 else 'medium'
            }

        # 6. Empty Cycles (cycles without documents)
        if self.cycles:
            all_cycle_nums = set(range(1, self.cycles[-1][0] + 1))
            existing_cycle_nums = set(c[0] for c in self.cycles)
            missing_cycles = all_cycle_nums - existing_cycle_nums

            for cycle_num in missing_cycles:
                antipatterns['empty_cycles'].append({
                    'cycle': cycle_num,
                    'severity': 'medium'
                })

        # 7. Isolated Clusters (documents that only link within a small group)
        # Simple heuristic: if a document has no path to high-level docs (α≥+2)
        high_level_docs = [p for p, d in self.documents.items()
                          if d.get('alpha') and int(d['alpha']) >= 2]

        if high_level_docs:
            for doc_path in self.documents:
                # Check if doc can reach any high-level doc
                can_reach_high = False
                visited = set()
                queue = [doc_path]

                while queue and not can_reach_high:
                    current = queue.pop(0)
                    if current in visited:
                        continue
                    visited.add(current)

                    if current in high_level_docs:
                        can_reach_high = True
                        break

                    # Add connected documents to queue
                    queue.extend(outgoing.get(current, []))

                if not can_reach_high and doc_path not in high_level_docs:
                    alpha = self.documents[doc_path].get('alpha')
                    if alpha and int(alpha) < 2:  # Only flag low-level isolated docs
                        antipatterns['isolated_clusters'].append({
                            'path': doc_path,
                            'title': self.documents[doc_path].get('title', 'Untitled'),
                            'alpha': alpha,
                            'severity': 'medium'
                        })

        return antipatterns

    def check_thresholds(self) -> bool:
        """Check if all metrics are within optimal ranges"""
        metrics = self.get_all_metrics()

        all_ok = True
        for metric_name, metric_data in metrics.items():
            if metric_name == 'metadata':
                continue

            status = metric_data['status']
            if status not in ['optimal', 'excellent', 'good']:
                all_ok = False

        return all_ok

    def format_report(self, format: str = 'text', include_antipatterns: bool = False) -> str:
        """Format metrics report"""
        metrics = self.get_all_metrics()

        if format == 'json':
            result = metrics
            if include_antipatterns:
                result['antipatterns'] = self.detect_antipatterns()
            return json.dumps(result, indent=2, ensure_ascii=False)

        # Text format
        lines = [
            "=" * 70,
            "PROJECT HEALTH METRICS (⇑⇓↔ Methodology)",
            "=" * 70,
            ""
        ]

        # Individual metrics
        for metric_name in ['cd', 'vt', 'cr', 'db']:
            metric = metrics[metric_name]
            value = metric['value']
            unit = metric['unit']
            status = metric['status']
            threshold = metric['threshold']

            status_symbol = {
                'optimal': '✅',
                'excellent': '✅',
                'good': '✅',
                'below': '⚠️',
                'above': '⚠️',
                'moderate': '⚠️',
                'poor': '❌'
            }.get(status, '❓')

            metric_full_name = {
                'cd': 'CD (Connectivity Density)',
                'vt': 'VT (Vertical Traceability)',
                'cr': 'CR (Convergence Rate)',
                'db': 'DB (Directional Balance)'
            }[metric_name]

            lines.append(f"{metric_full_name}")
            lines.append(f"  Value: {value}{unit} {status_symbol} ({status})")

            if metric_name in ['cd', 'vt', 'cr']:
                lines.append(f"  Target: {threshold['min']}-{threshold['max']}{unit}")
            else:
                lines.append(f"  Target: <{threshold['max']}{unit}")

            lines.append("")

        # Metadata
        meta = metrics['metadata']
        lines.append("-" * 70)
        lines.append("METADATA")
        lines.append("-" * 70)
        lines.append(f"Total documents: {meta['total_documents']}")
        lines.append(f"Total connections: {meta['total_connections']}")
        lines.append(f"Total cycles: {meta['total_cycles']}")
        lines.append(f"Analysis date: {meta['analysis_date']}")
        lines.append("")

        # Anti-patterns (if requested)
        if include_antipatterns:
            antipatterns = self.detect_antipatterns()

            lines.append("=" * 70)
            lines.append("ANTI-PATTERNS DETECTED")
            lines.append("=" * 70)
            lines.append("")

            total_issues = sum(len(v) if isinstance(v, list) else (1 if v else 0)
                             for v in antipatterns.values())

            if total_issues == 0:
                lines.append("✅ No anti-patterns detected!")
                lines.append("")
            else:
                lines.append(f"⚠️  Found {total_issues} potential issues\n")

                # 1. Orphan Documents
                if antipatterns['orphan_documents']:
                    lines.append(f"🔴 Orphan Documents ({len(antipatterns['orphan_documents'])}):")
                    lines.append("   Documents with no connections at all")
                    for item in antipatterns['orphan_documents'][:5]:  # Show first 5
                        lines.append(f"   - {item['path']}")
                    if len(antipatterns['orphan_documents']) > 5:
                        lines.append(f"   ... and {len(antipatterns['orphan_documents']) - 5} more")
                    lines.append("")

                # 2. Dead Ends
                if antipatterns['dead_ends']:
                    lines.append(f"🟡 Dead Ends ({len(antipatterns['dead_ends'])}):")
                    lines.append("   Documents with no outgoing links")
                    for item in antipatterns['dead_ends'][:5]:
                        lines.append(f"   - {item['path']} ({item['incoming_count']} incoming)")
                    if len(antipatterns['dead_ends']) > 5:
                        lines.append(f"   ... and {len(antipatterns['dead_ends']) - 5} more")
                    lines.append("")

                # 3. Hub Documents
                if antipatterns['hub_documents']:
                    lines.append(f"🟡 Hub Documents ({len(antipatterns['hub_documents'])}):")
                    lines.append("   Documents with too many connections (>20)")
                    for item in antipatterns['hub_documents']:
                        lines.append(f"   - {item['path']} ({item['connection_count']} connections)")
                    lines.append("")

                # 4. Missing Alpha
                if antipatterns['missing_alpha']:
                    lines.append(f"🟢 Missing α-level ({len(antipatterns['missing_alpha'])}):")
                    lines.append("   Documents without abstraction level")
                    for item in antipatterns['missing_alpha'][:5]:
                        lines.append(f"   - {item['path']}")
                    if len(antipatterns['missing_alpha']) > 5:
                        lines.append(f"   ... and {len(antipatterns['missing_alpha']) - 5} more")
                    lines.append("")

                # 5. Unbalanced Directions
                if antipatterns['unbalanced_directions']:
                    ub = antipatterns['unbalanced_directions']
                    severity_symbol = '🔴' if ub['severity'] == 'high' else '🟡'
                    lines.append(f"{severity_symbol} Unbalanced Directions:")
                    lines.append(f"   ⇑ UP: {ub['up']['count']} ({ub['up']['percentage']}%)")
                    lines.append(f"   ⇓ DOWN: {ub['down']['count']} ({ub['down']['percentage']}%)")
                    lines.append(f"   ↔ HORIZONTAL: {ub['horizontal']['count']} ({ub['horizontal']['percentage']}%)")
                    lines.append("")

                # 6. Empty Cycles
                if antipatterns['empty_cycles']:
                    lines.append(f"🟡 Empty Cycles ({len(antipatterns['empty_cycles'])}):")
                    cycles_str = ', '.join(str(c['cycle']) for c in antipatterns['empty_cycles'])
                    lines.append(f"   Missing: {cycles_str}")
                    lines.append("")

                # 7. Isolated Clusters
                if antipatterns['isolated_clusters']:
                    lines.append(f"🟡 Isolated Clusters ({len(antipatterns['isolated_clusters'])}):")
                    lines.append("   Low-level docs not connected to high-level architecture")
                    for item in antipatterns['isolated_clusters'][:5]:
                        lines.append(f"   - {item['path']} (α={item['alpha']})")
                    if len(antipatterns['isolated_clusters']) > 5:
                        lines.append(f"   ... and {len(antipatterns['isolated_clusters']) - 5} more")
                    lines.append("")

        # Overall assessment
        lines.append("=" * 70)
        all_ok = self.check_thresholds()
        if all_ok:
            lines.append("✅ PROJECT HEALTH: EXCELLENT")
        else:
            lines.append("⚠️  PROJECT HEALTH: NEEDS ATTENTION")
        lines.append("=" * 70)

        return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(
        description='Calculate health metrics for ⇑⇓↔ projects'
    )
    parser.add_argument(
        '--metric',
        choices=['cd', 'vt', 'cr', 'db', 'all'],
        default='all',
        help='Metric to calculate (default: all)'
    )
    parser.add_argument(
        '--format',
        choices=['text', 'json'],
        default='text',
        help='Output format (default: text)'
    )
    parser.add_argument(
        '--check-thresholds',
        action='store_true',
        help='Exit with code 1 if metrics are out of optimal range'
    )
    parser.add_argument(
        '--detect-antipatterns',
        action='store_true',
        help='Include anti-pattern detection in report'
    )
    parser.add_argument(
        '--root',
        type=str,
        default='.',
        help='Project root directory (default: current directory)'
    )

    args = parser.parse_args()

    # Calculate metrics
    calculator = HealthMetricsCalculator(args.root)
    calculator.analyze()

    # Output
    if args.metric == 'all':
        print(calculator.format_report(args.format, include_antipatterns=args.detect_antipatterns))
    else:
        # Single metric
        metrics = calculator.get_all_metrics()
        if args.format == 'json':
            print(json.dumps({args.metric: metrics[args.metric]}, indent=2))
        else:
            metric = metrics[args.metric]
            print(f"{args.metric.upper()}: {metric['value']}{metric['unit']} ({metric['status']})")

    # Check thresholds
    if args.check_thresholds:
        if not calculator.check_thresholds():
            return 1

    return 0


if __name__ == '__main__':
    exit(main())
