#!/usr/bin/env python3
"""
Project Success Metrics

Метрики успешности созданных проектов.
"""

from typing import Dict, List
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ProjectMetrics:
    """Метрики проекта"""
    project_id: str
    template_used: str
    created_at: str
    completion_rate: float  # %
    build_success: bool
    tests_passing: bool
    deployed: bool
    active_days: int

    def success_score(self) -> float:
        """Расчет success score"""
        score = 0.0
        score += self.completion_rate * 0.3
        score += 25 if self.build_success else 0
        score += 25 if self.tests_passing else 0
        score += 20 if self.deployed else 0
        return score


class ProjectSuccessAnalyzer:
    """Project Success Analyzer"""

    def __init__(self):
        """Инициализация"""
        self.projects: Dict[str, ProjectMetrics] = {}

    def track_project(self, metrics: ProjectMetrics):
        """Отслеживание проекта"""
        self.projects[metrics.project_id] = metrics

    def get_success_rate(self) -> float:
        """Общий success rate"""
        if not self.projects:
            return 0.0

        successful = sum(1 for p in self.projects.values() if p.success_score() >= 70)
        return (successful / len(self.projects)) * 100

    def get_template_success(self, template_id: str) -> Dict:
        """Success rate по template"""
        template_projects = [p for p in self.projects.values() if p.template_used == template_id]

        if not template_projects:
            return {'template_id': template_id, 'success_rate': 0, 'project_count': 0}

        successful = sum(1 for p in template_projects if p.success_score() >= 70)

        return {
            'template_id': template_id,
            'project_count': len(template_projects),
            'success_rate': (successful / len(template_projects)) * 100,
            'avg_completion': sum(p.completion_rate for p in template_projects) / len(template_projects),
            'build_success_rate': sum(1 for p in template_projects if p.build_success) / len(template_projects) * 100,
            'deploy_rate': sum(1 for p in template_projects if p.deployed) / len(template_projects) * 100
        }

    def get_roi_metrics(self) -> Dict:
        """ROI metrics"""
        total_projects = len(self.projects)
        successful_projects = sum(1 for p in self.projects.values() if p.success_score() >= 70)
        avg_active_days = sum(p.active_days for p in self.projects.values()) / total_projects if total_projects else 0

        return {
            'total_projects': total_projects,
            'successful_projects': successful_projects,
            'success_rate': (successful_projects / total_projects * 100) if total_projects else 0,
            'avg_active_days': round(avg_active_days, 1),
            'time_to_production': 7.5,  # days (example)
            'estimated_time_saved': total_projects * 40  # hours saved
        }
