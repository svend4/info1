"""
Analytics & Insights Package

Аналитика использования, метрики templates и project success.
"""

from .usage_analytics import UsageAnalytics, UsageEvent
from .template_metrics import TemplateMetrics
from .project_success import ProjectSuccessAnalyzer, ProjectMetrics
from .dashboard import AnalyticsDashboard

__all__ = [
    'UsageAnalytics',
    'UsageEvent',
    'TemplateMetrics',
    'ProjectSuccessAnalyzer',
    'ProjectMetrics',
    'AnalyticsDashboard'
]

__version__ = '1.0.0'
