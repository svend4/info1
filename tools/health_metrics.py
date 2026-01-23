#!/usr/bin/env python3
"""
Health Metrics Calculator for ⇑⇓↔ Projects

Automatically calculates project health metrics:
- CD (Connectivity Density): 10-20% optimal
- VT (Vertical Traceability): 50-70% optimal
- CR (Convergence Rate): 0.7-1.5 optimal
- DB (Directional Balance): <30% optimal

Part of the Parallel Bidirectional Development Methodology.

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

        # Thresholds
        self.thresholds = {
            'cd': {'min': 10.0, 'max': 20.0, 'unit': '%'},
            'vt': {'min': 50.0, 'max': 70.0, 'unit': '%'},
            'cr': {'min': 0.7, 'max': 1.5, 'unit': ''},
            'db': {'min': 0.0, 'max': 30.0, 'unit': '%'}
        }

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
                direction = self._extract_direction(content)
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

    def _extract_direction(self, content: str) -> Optional[str]:
        """Extract development direction (⇑, ⇓, ↔)"""
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

    def format_report(self, format: str = 'text') -> str:
        """Format metrics report"""
        metrics = self.get_all_metrics()

        if format == 'json':
            return json.dumps(metrics, indent=2, ensure_ascii=False)

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
        print(calculator.format_report(args.format))
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
