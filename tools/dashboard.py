#!/usr/bin/env python3
"""
Project Health Dashboard for ⇑⇓↔ Projects

Unified interface for all project health metrics, visualizations, and recommendations.
Integrates health_metrics.py, visualize_connections.py, and anti-pattern detection.

Usage:
    python3 dashboard.py                    # Full dashboard
    python3 dashboard.py --quick            # Quick summary
    python3 dashboard.py --recommendations  # Show recommendations only
    python3 dashboard.py --export report.md # Export as markdown report

Part of the Parallel Bidirectional Development Methodology.
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List

# Import from sibling modules
sys.path.insert(0, str(Path(__file__).parent))
from health_metrics import HealthMetricsCalculator
from visualize_connections import ProjectAnalyzer


class ProjectDashboard:
    """Unified dashboard for project health"""

    def __init__(self, root_path: str = "."):
        self.root = Path(root_path)
        self.metrics_calc = HealthMetricsCalculator(root_path)
        self.project_analyzer = ProjectAnalyzer(root_path)

    def analyze(self):
        """Run full analysis"""
        self.metrics_calc.analyze()
        self.project_analyzer.scan_project()

    def generate_quick_summary(self) -> str:
        """Generate quick summary (< 10 lines)"""
        metrics = self.metrics_calc.get_all_metrics()
        antipatterns = self.metrics_calc.detect_antipatterns()

        lines = [
            "=" * 60,
            "📊 PROJECT HEALTH SUMMARY (⇑⇓↔)",
            "=" * 60,
            "",
            f"Documents: {metrics['metadata']['total_documents']} | "
            f"Connections: {metrics['metadata']['total_connections']} | "
            f"Cycles: {metrics['metadata']['total_cycles']}",
            "",
            f"CD: {metrics['cd']['value']}{metrics['cd']['unit']} {self._status_emoji(metrics['cd']['status'])} | "
            f"VT: {metrics['vt']['value']}{metrics['vt']['unit']} {self._status_emoji(metrics['vt']['status'])} | "
            f"CR: {metrics['cr']['value']} {self._status_emoji(metrics['cr']['status'])} | "
            f"DB: {metrics['db']['value']}{metrics['db']['unit']} {self._status_emoji(metrics['db']['status'])}",
            "",
            f"Anti-patterns: {self._count_antipatterns(antipatterns)} issues found",
            "",
            f"Overall: {'✅ HEALTHY' if self.metrics_calc.check_thresholds() else '⚠️  NEEDS ATTENTION'}",
            "=" * 60,
        ]

        return '\n'.join(lines)

    def generate_full_dashboard(self) -> str:
        """Generate comprehensive dashboard"""
        metrics = self.metrics_calc.get_all_metrics()
        antipatterns = self.metrics_calc.detect_antipatterns()

        lines = [
            "=" * 70,
            "📊 PROJECT HEALTH DASHBOARD (⇑⇓↔ Methodology)",
            "=" * 70,
            "",
            f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Project Root: {self.root.absolute()}",
            "",
        ]

        # Section 1: Core Metrics
        lines.extend([
            "─" * 70,
            "1. CORE METRICS",
            "─" * 70,
            "",
        ])

        metric_details = [
            ('CD', 'Connectivity Density', 'cd'),
            ('VT', 'Vertical Traceability', 'vt'),
            ('CR', 'Convergence Rate', 'cr'),
            ('DB', 'Directional Balance', 'db'),
        ]

        for short, full, key in metric_details:
            m = metrics[key]
            status_emoji = self._status_emoji(m['status'])
            lines.append(f"  {short} ({full})")
            lines.append(f"    Value: {m['value']}{m['unit']} {status_emoji} ({m['status']})")

            if key in ['cd', 'vt', 'cr']:
                lines.append(f"    Target: {m['threshold']['min']}-{m['threshold']['max']}{m['unit']}")
            else:
                lines.append(f"    Target: <{m['threshold']['max']}{m['unit']}")
            lines.append("")

        # Section 2: Project Statistics
        lines.extend([
            "─" * 70,
            "2. PROJECT STATISTICS",
            "─" * 70,
            "",
            f"  Total Documents: {metrics['metadata']['total_documents']}",
            f"  Total Connections: {metrics['metadata']['total_connections']}",
            f"  Total Cycles: {metrics['metadata']['total_cycles']}",
            "",
        ])

        # Section 3: Document Distribution by Type
        doc_types = {}
        for doc_info in self.project_analyzer.documents.values():
            dtype = doc_info.get('type', 'unknown')
            doc_types[dtype] = doc_types.get(dtype, 0) + 1

        lines.extend([
            "  Document Types:",
        ])
        for dtype, count in sorted(doc_types.items(), key=lambda x: x[1], reverse=True):
            lines.append(f"    - {dtype}: {count}")
        lines.append("")

        # Section 4: Anti-Patterns Summary
        total_issues = self._count_antipatterns(antipatterns)

        lines.extend([
            "─" * 70,
            f"3. ANTI-PATTERNS ({total_issues} issues)",
            "─" * 70,
            "",
        ])

        if total_issues == 0:
            lines.append("  ✅ No anti-patterns detected!")
        else:
            antipattern_summary = [
                ('🔴 Orphan Documents', len(antipatterns['orphan_documents']), 'high'),
                ('🟡 Dead Ends', len(antipatterns['dead_ends']), 'medium'),
                ('🟡 Hub Documents', len(antipatterns['hub_documents']), 'medium'),
                ('🟢 Missing α-level', len(antipatterns['missing_alpha']), 'low'),
                ('🟡 Empty Cycles', len(antipatterns['empty_cycles']), 'medium'),
                ('🟡 Isolated Clusters', len(antipatterns['isolated_clusters']), 'medium'),
            ]

            for name, count, severity in antipattern_summary:
                if count > 0:
                    lines.append(f"  {name}: {count}")

            # Unbalanced Directions
            if antipatterns['unbalanced_directions']:
                ub = antipatterns['unbalanced_directions']
                severity_emoji = '🔴' if ub['severity'] == 'high' else '🟡'
                lines.append(f"  {severity_emoji} Unbalanced Directions:")
                lines.append(f"      ⇑ UP: {ub['up']['count']} ({ub['up']['percentage']}%)")
                lines.append(f"      ⇓ DOWN: {ub['down']['count']} ({ub['down']['percentage']}%)")
                lines.append(f"      ↔ HORIZONTAL: {ub['horizontal']['count']} ({ub['horizontal']['percentage']}%)")

        lines.append("")

        # Section 5: Top Recommendations
        recommendations = self.generate_recommendations(metrics, antipatterns)

        lines.extend([
            "─" * 70,
            f"4. TOP RECOMMENDATIONS ({len(recommendations)})",
            "─" * 70,
            "",
        ])

        for i, rec in enumerate(recommendations[:5], 1):  # Show top 5
            lines.append(f"  {i}. {rec['priority']} {rec['title']}")
            lines.append(f"     {rec['description']}")
            lines.append(f"     → {rec['action']}")
            lines.append("")

        if len(recommendations) > 5:
            lines.append(f"  ... and {len(recommendations) - 5} more recommendations")
            lines.append("")

        # Section 6: Overall Health
        lines.extend([
            "=" * 70,
            f"OVERALL HEALTH: {'✅ EXCELLENT' if self.metrics_calc.check_thresholds() else '⚠️  NEEDS ATTENTION'}",
            "=" * 70,
        ])

        return '\n'.join(lines)

    def generate_recommendations(self, metrics: Dict, antipatterns: Dict) -> List[Dict]:
        """Generate prioritized recommendations"""
        recommendations = []

        # 1. Check DB (Directional Balance)
        db = metrics['db']
        if db['value'] > 50:
            recommendations.append({
                'priority': '🔴 CRITICAL',
                'title': 'Severe Directional Imbalance',
                'description': f"DB is {db['value']}% (target: <30%). One direction dominates.",
                'action': 'Balance next cycles: create documents in ⇓ DOWN and ↔ HORIZONTAL'
            })
        elif db['value'] > 30:
            recommendations.append({
                'priority': '⚠️  HIGH',
                'title': 'Moderate Directional Imbalance',
                'description': f"DB is {db['value']}% (target: <30%).",
                'action': 'Focus on balancing directions in next 2-3 cycles'
            })

        # 2. Check Unbalanced Directions
        if antipatterns['unbalanced_directions']:
            ub = antipatterns['unbalanced_directions']
            if ub['severity'] == 'high':
                dominant = max(
                    [('⇑ UP', ub['up']['percentage']),
                     ('⇓ DOWN', ub['down']['percentage']),
                     ('↔ HORIZONTAL', ub['horizontal']['percentage'])],
                    key=lambda x: x[1]
                )
                recommendations.append({
                    'priority': '🔴 CRITICAL',
                    'title': f'{dominant[0]} dominates ({dominant[1]}%)',
                    'description': 'Extreme imbalance in development directions',
                    'action': f'Next 3-5 cycles: minimize {dominant[0]}, focus on other directions'
                })

        # 3. Check VT (Vertical Traceability)
        vt = metrics['vt']
        if vt['value'] < 40:
            recommendations.append({
                'priority': '⚠️  HIGH',
                'title': 'Low Vertical Traceability',
                'description': f"VT is {vt['value']}% (target: 50-70%). Weak links between abstraction levels.",
                'action': 'Add vertical links (|Δα| ≥ 2): architecture → implementation, philosophy → code'
            })

        # 4. Check CD (Connectivity Density)
        cd = metrics['cd']
        if cd['value'] < 5:
            recommendations.append({
                'priority': '⚠️  HIGH',
                'title': 'Very Low Connectivity',
                'description': f"CD is {cd['value']}% (target: 10-20%). Documents are poorly connected.",
                'action': 'Add more cross-references between related documents'
            })
        elif cd['value'] > 30:
            recommendations.append({
                'priority': '🟡 MEDIUM',
                'title': 'Excessive Connectivity',
                'description': f"CD is {cd['value']}% (target: 10-20%). Too many connections.",
                'action': 'Review and remove redundant links'
            })

        # 5. Orphan Documents
        if antipatterns['orphan_documents']:
            recommendations.append({
                'priority': '🔴 CRITICAL',
                'title': f'{len(antipatterns["orphan_documents"])} Orphan Document(s)',
                'description': 'Documents with no connections at all',
                'action': 'Add links to/from orphan documents or remove them if obsolete'
            })

        # 6. Hub Documents
        if antipatterns['hub_documents']:
            top_hub = max(antipatterns['hub_documents'], key=lambda x: x['connection_count'])
            recommendations.append({
                'priority': '🟡 MEDIUM',
                'title': f'Hub Document: {Path(top_hub["path"]).name}',
                'description': f"{top_hub['connection_count']} connections (target: <20)",
                'action': 'Split hub document into smaller, focused documents'
            })

        # 7. Dead Ends
        if len(antipatterns['dead_ends']) > 10:
            recommendations.append({
                'priority': '🟡 MEDIUM',
                'title': f'{len(antipatterns["dead_ends"])} Dead-End Documents',
                'description': 'Documents without outgoing links',
                'action': 'Add "See also" sections with links to related documents'
            })

        # 8. Missing Alpha
        if len(antipatterns['missing_alpha']) > 5:
            recommendations.append({
                'priority': '🟢 LOW',
                'title': f'{len(antipatterns["missing_alpha"])} Documents Missing α-level',
                'description': 'Documents without abstraction level metadata',
                'action': 'Add "α-уровень: X" to document headers'
            })

        # 9. Isolated Clusters
        if antipatterns['isolated_clusters']:
            recommendations.append({
                'priority': '🟡 MEDIUM',
                'title': f'{len(antipatterns["isolated_clusters"])} Isolated Document(s)',
                'description': 'Low-level docs not connected to high-level architecture',
                'action': 'Add upward links (⇑) from implementation to architecture'
            })

        # Sort by priority
        priority_order = {'🔴 CRITICAL': 0, '⚠️  HIGH': 1, '🟡 MEDIUM': 2, '🟢 LOW': 3}
        recommendations.sort(key=lambda x: priority_order.get(x['priority'], 4))

        return recommendations

    def export_markdown_report(self, output_path: str):
        """Export dashboard as markdown report"""
        metrics = self.metrics_calc.get_all_metrics()
        antipatterns = self.metrics_calc.detect_antipatterns()
        recommendations = self.generate_recommendations(metrics, antipatterns)

        lines = [
            f"# Project Health Report",
            "",
            f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Project:** {self.root.absolute()}",
            "",
            "---",
            "",
            "## Core Metrics",
            "",
            "| Metric | Value | Status | Target |",
            "|--------|-------|--------|--------|",
        ]

        for key in ['cd', 'vt', 'cr', 'db']:
            m = metrics[key]
            status = self._status_emoji(m['status'])
            target = f"{m['threshold']['min']}-{m['threshold']['max']}{m['unit']}" if key != 'db' else f"<{m['threshold']['max']}{m['unit']}"
            lines.append(f"| {key.upper()} | {m['value']}{m['unit']} | {status} {m['status']} | {target} |")

        lines.extend([
            "",
            "## Project Statistics",
            "",
            f"- **Documents:** {metrics['metadata']['total_documents']}",
            f"- **Connections:** {metrics['metadata']['total_connections']}",
            f"- **Cycles:** {metrics['metadata']['total_cycles']}",
            "",
            "## Anti-Patterns",
            "",
        ])

        total_issues = self._count_antipatterns(antipatterns)

        if total_issues == 0:
            lines.append("✅ No anti-patterns detected!")
        else:
            lines.append(f"⚠️  Found **{total_issues}** potential issues:")
            lines.append("")

            if antipatterns['orphan_documents']:
                lines.append(f"- 🔴 **Orphan Documents:** {len(antipatterns['orphan_documents'])}")
            if antipatterns['dead_ends']:
                lines.append(f"- 🟡 **Dead Ends:** {len(antipatterns['dead_ends'])}")
            if antipatterns['hub_documents']:
                lines.append(f"- 🟡 **Hub Documents:** {len(antipatterns['hub_documents'])}")
            if antipatterns['missing_alpha']:
                lines.append(f"- 🟢 **Missing α-level:** {len(antipatterns['missing_alpha'])}")
            if antipatterns['empty_cycles']:
                lines.append(f"- 🟡 **Empty Cycles:** {len(antipatterns['empty_cycles'])}")
            if antipatterns['isolated_clusters']:
                lines.append(f"- 🟡 **Isolated Clusters:** {len(antipatterns['isolated_clusters'])}")

            if antipatterns['unbalanced_directions']:
                ub = antipatterns['unbalanced_directions']
                lines.append(f"- {'' if ub['severity'] == 'medium' else '🔴'} **Unbalanced Directions:** ⇑{ub['up']['percentage']}% / ⇓{ub['down']['percentage']}% / ↔{ub['horizontal']['percentage']}%")

        lines.extend([
            "",
            "## Recommendations",
            "",
        ])

        for i, rec in enumerate(recommendations, 1):
            lines.append(f"### {i}. {rec['priority']} {rec['title']}")
            lines.append("")
            lines.append(f"**Issue:** {rec['description']}")
            lines.append("")
            lines.append(f"**Action:** {rec['action']}")
            lines.append("")

        lines.extend([
            "---",
            "",
            f"**Overall Health:** {'✅ EXCELLENT' if self.metrics_calc.check_thresholds() else '⚠️  NEEDS ATTENTION'}",
        ])

        # Write to file
        Path(output_path).write_text('\n'.join(lines), encoding='utf-8')

    def _status_emoji(self, status: str) -> str:
        """Get emoji for status"""
        return {
            'optimal': '✅',
            'excellent': '✅',
            'good': '✅',
            'below': '⚠️',
            'above': '⚠️',
            'moderate': '⚠️',
            'poor': '❌',
        }.get(status, '❓')

    def _count_antipatterns(self, antipatterns: Dict) -> int:
        """Count total anti-pattern issues"""
        total = 0
        for key, value in antipatterns.items():
            if isinstance(value, list):
                total += len(value)
            elif isinstance(value, dict) and value:  # unbalanced_directions
                total += 1
        return total


def main():
    parser = argparse.ArgumentParser(
        description='Unified dashboard for ⇑⇓↔ project health'
    )
    parser.add_argument(
        '--quick',
        action='store_true',
        help='Show quick summary only'
    )
    parser.add_argument(
        '--recommendations',
        action='store_true',
        help='Show recommendations only'
    )
    parser.add_argument(
        '--export',
        type=str,
        metavar='FILE',
        help='Export full report to markdown file'
    )
    parser.add_argument(
        '--root',
        type=str,
        default='.',
        help='Project root directory (default: current directory)'
    )

    args = parser.parse_args()

    # Create dashboard
    dashboard = ProjectDashboard(args.root)
    dashboard.analyze()

    # Output based on options
    if args.export:
        dashboard.export_markdown_report(args.export)
        print(f"✅ Report exported to: {args.export}")
    elif args.quick:
        print(dashboard.generate_quick_summary())
    elif args.recommendations:
        metrics = dashboard.metrics_calc.get_all_metrics()
        antipatterns = dashboard.metrics_calc.detect_antipatterns()
        recommendations = dashboard.generate_recommendations(metrics, antipatterns)

        print("=" * 70)
        print(f"📋 RECOMMENDATIONS ({len(recommendations)})")
        print("=" * 70)
        print("")

        for i, rec in enumerate(recommendations, 1):
            print(f"{i}. {rec['priority']} {rec['title']}")
            print(f"   {rec['description']}")
            print(f"   → {rec['action']}")
            print("")
    else:
        print(dashboard.generate_full_dashboard())

    return 0


if __name__ == '__main__':
    exit(main())
