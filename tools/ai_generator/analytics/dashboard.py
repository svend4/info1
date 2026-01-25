#!/usr/bin/env python3
"""
Analytics Dashboard

Генерация dashboard с метриками.
"""

from typing import Dict, Any
import json


class AnalyticsDashboard:
    """Analytics Dashboard Generator"""

    def __init__(self, usage_analytics, template_metrics, project_analyzer):
        """Инициализация"""
        self.usage = usage_analytics
        self.templates = template_metrics
        self.projects = project_analyzer

    def generate_overview(self) -> Dict[str, Any]:
        """Генерация overview"""
        return {
            'users': {
                'dau': self.usage.get_dau(),
                'mau': self.usage.get_mau(),
                'retention_7d': self.usage.get_retention_rate(7),
                'retention_30d': self.usage.get_retention_rate(30)
            },
            'templates': {
                'top_templates': self.templates.get_top_templates(5),
                'trending': self.templates.get_trending()
            },
            'projects': {
                'total': len(self.projects.projects),
                'success_rate': self.projects.get_success_rate(),
                'roi': self.projects.get_roi_metrics()
            }
        }

    def generate_html_dashboard(self) -> str:
        """Генерация HTML dashboard"""
        data = self.generate_overview()

        return f"""<!DOCTYPE html>
<html>
<head>
    <title>AI Generator Analytics</title>
    <style>
        body {{ font-family: Arial; margin: 0; padding: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .card {{ background: white; padding: 20px; margin: 10px 0; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .metric {{ display: inline-block; margin: 10px 20px; }}
        .metric-value {{ font-size: 32px; font-weight: bold; color: #0066cc; }}
        .metric-label {{ color: #666; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Analytics Dashboard</h1>

        <div class="card">
            <h2>User Metrics</h2>
            <div class="metric">
                <div class="metric-value">{data['users']['dau']}</div>
                <div class="metric-label">Daily Active Users</div>
            </div>
            <div class="metric">
                <div class="metric-value">{data['users']['mau']}</div>
                <div class="metric-label">Monthly Active Users</div>
            </div>
            <div class="metric">
                <div class="metric-value">{data['users']['retention_7d']:.1f}%</div>
                <div class="metric-label">7-Day Retention</div>
            </div>
        </div>

        <div class="card">
            <h2>Top Templates</h2>
            <table>
                <tr>
                    <th>Template</th>
                    <th>Downloads</th>
                    <th>Rating</th>
                    <th>Success Rate</th>
                </tr>
                {"".join(f'''
                <tr>
                    <td>{t["template_id"]}</td>
                    <td>{t["downloads"]}</td>
                    <td>{t["avg_rating"]:.1f}/5</td>
                    <td>{t["success_rate"]:.1f}%</td>
                </tr>
                ''' for t in data['templates']['top_templates'])}
            </table>
        </div>

        <div class="card">
            <h2>Project Success</h2>
            <div class="metric">
                <div class="metric-value">{data['projects']['total']}</div>
                <div class="metric-label">Total Projects</div>
            </div>
            <div class="metric">
                <div class="metric-value">{data['projects']['success_rate']:.1f}%</div>
                <div class="metric-label">Success Rate</div>
            </div>
        </div>
    </div>
</body>
</html>
"""

    def export_json(self, filename: str):
        """Экспорт в JSON"""
        data = self.generate_overview()
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
