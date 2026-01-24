#!/usr/bin/env python3
"""
Context-Aware Project Structure Adapter (Фаза 3 ЭТАПА 9)

Адаптация структуры проекта на основе извлечённых параметров.
Добавляет контекстно-зависимые директории и файлы.
"""

from typing import List, Dict, Set
from dataclasses import dataclass

try:
    from .enhanced_parameter_extractor import ExtractedParameters, EnhancedParameterExtractor
    from .template_composer import ComposedStructure, TemplateComposer
    from .multi_label_classifier import MultiLabelResult, MultiLabelClassifier
except ImportError:
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from ai_generator.enhanced_parameter_extractor import ExtractedParameters, EnhancedParameterExtractor
    from ai_generator.template_composer import ComposedStructure, TemplateComposer
    from ai_generator.multi_label_classifier import MultiLabelResult, MultiLabelClassifier


@dataclass
class AdaptedStructure:
    """Адаптированная структура проекта"""
    directories: List[str]
    files: List[str]
    adaptations: List[str]  # Список применённых адаптаций
    recommendations: List[str]


class ContextAwareAdapter:
    """
    Контекстно-зависимый адаптер структуры проекта

    Адаптирует базовую структуру на основе:
    - Бюджета и финансирования
    - Размера команды
    - Фазы проекта
    - Технологий
    - Уровня риска
    - И других параметров
    """

    def __init__(self):
        """Инициализация адаптера"""
        pass

    def adapt(
        self,
        base_structure: ComposedStructure,
        parameters: ExtractedParameters
    ) -> AdaptedStructure:
        """
        Адаптация структуры на основе параметров

        Args:
            base_structure: Базовая скомпонованная структура
            parameters: Извлечённые параметры проекта

        Returns:
            AdaptedStructure с дополнительными директориями и файлами
        """
        # Начинаем с базовой структуры
        adapted_dirs = set(base_structure.directories)
        adapted_files = set(base_structure.files)
        adaptations = []
        recommendations = []

        # Адаптация по бюджету
        if parameters.budget:
            self._adapt_budget(
                adapted_dirs, adapted_files, adaptations,
                parameters.budget, parameters.is_funded
            )

        # Адаптация по размеру команды
        if parameters.team_size:
            self._adapt_team(
                adapted_dirs, adapted_files, adaptations, recommendations,
                parameters.team_size
            )

        # Адаптация по фазе
        if parameters.phase:
            self._adapt_phase(
                adapted_dirs, adapted_files, adaptations,
                parameters.phase
            )

        # Адаптация по технологиям
        if parameters.technologies:
            self._adapt_technologies(
                adapted_dirs, adapted_files, adaptations,
                parameters.technologies
            )

        # Адаптация по уровню риска
        if parameters.risk_level:
            self._adapt_risk(
                adapted_dirs, adapted_files, adaptations,
                parameters.risk_level
            )

        # Адаптация по приоритету
        if parameters.priority == 'critical' or parameters.priority == 'high':
            self._adapt_priority(
                adapted_dirs, adapted_files, adaptations,
                parameters.priority
            )

        # Адаптация по дедлайну
        if parameters.has_deadline and parameters.timeline:
            self._adapt_deadline(
                adapted_dirs, adapted_files, adaptations,
                parameters.timeline
            )

        # Адаптация для некоммерческих проектов
        if parameters.is_nonprofit:
            self._adapt_nonprofit(
                adapted_dirs, adapted_files, adaptations
            )

        # Адаптация для коммерческих проектов
        if parameters.is_commercial:
            self._adapt_commercial(
                adapted_dirs, adapted_files, adaptations
            )

        # Адаптация по масштабу
        if parameters.scale == 'large':
            self._adapt_large_scale(
                adapted_dirs, adapted_files, adaptations, recommendations
            )

        return AdaptedStructure(
            directories=sorted(adapted_dirs),
            files=sorted(adapted_files),
            adaptations=adaptations,
            recommendations=recommendations
        )

    def _adapt_budget(
        self,
        dirs: Set[str],
        files: Set[str],
        adaptations: List[str],
        budget: Dict,
        is_funded: bool
    ):
        """Адаптация для проектов с бюджетом"""
        if budget['amount'] >= 1_000_000:  # ≥1M
            dirs.add('financials/')
            files.add('BUDGET-PLAN.md')
            files.add('EXPENSES-TRACKING.md')
            adaptations.append(f"Added financial tracking for {budget['formatted']} budget")

        if is_funded:
            dirs.add('reporting/')
            files.add('GRANT-REPORTING.md')
            adaptations.append("Added grant reporting structure")

    def _adapt_team(
        self,
        dirs: Set[str],
        files: Set[str],
        adaptations: List[str],
        recommendations: List[str],
        team_size: int
    ):
        """Адаптация для проектов с командой"""
        if team_size >= 5:
            # Большая команда - добавляем коллаборацию
            files.add('CONTRIBUTING.md')
            files.add('CODE-OF-CONDUCT.md')
            dirs.add('team/')
            adaptations.append(f"Added collaboration docs for team of {team_size}")

        if team_size >= 10:
            # Очень большая команда - добавляем документацию процессов
            dirs.add('team/onboarding/')
            files.add('TEAM-STRUCTURE.md')
            files.add('ONBOARDING.md')
            adaptations.append("Added team management structure for large team")
            recommendations.append("Consider implementing CI/CD for coordination")
            recommendations.append("Set up code review process")

        if team_size >= 20:
            # Enterprise-level
            dirs.add('team/departments/')
            files.add('ROLES-AND-RESPONSIBILITIES.md')
            adaptations.append("Added enterprise team structure")
            recommendations.append("Implement project management tools (Jira, etc.)")

    def _adapt_phase(
        self,
        dirs: Set[str],
        files: Set[str],
        adaptations: List[str],
        phase: str
    ):
        """Адаптация по фазе проекта"""
        if phase == 'mvp':
            dirs.add('mvp/')
            files.add('MVP-PLAN.md')
            files.add('FEATURE-PRIORITIZATION.md')
            adaptations.append("Added MVP-specific structure")

        elif phase == 'alpha' or phase == 'beta':
            dirs.add('testing/')
            dirs.add('feedback/')
            files.add('TESTING-PLAN.md')
            files.add('FEEDBACK-COLLECTION.md')
            files.add('KNOWN-ISSUES.md')
            adaptations.append(f"Added {phase} testing structure")

        elif phase == 'production':
            dirs.add('deployment/')
            dirs.add('monitoring/')
            files.add('DEPLOYMENT-GUIDE.md')
            files.add('MONITORING.md')
            files.add('INCIDENT-RESPONSE.md')
            adaptations.append("Added production infrastructure")

        elif phase == 'scaling':
            dirs.add('scalability/')
            dirs.add('performance/')
            files.add('SCALING-STRATEGY.md')
            files.add('PERFORMANCE-OPTIMIZATION.md')
            adaptations.append("Added scaling infrastructure")

    def _adapt_technologies(
        self,
        dirs: Set[str],
        files: Set[str],
        adaptations: List[str],
        technologies: List[str]
    ):
        """Адаптация по технологиям"""
        tech_lower = [t.lower() for t in technologies]

        # Frontend frameworks
        if any(t in tech_lower for t in ['react', 'vue', 'angular']):
            dirs.add('src/components/')
            dirs.add('src/hooks/' if 'react' in tech_lower else 'src/composables/')
            files.add('package.json')
            files.add('.eslintrc.json')
            adaptations.append("Added frontend framework structure")

        # Backend frameworks
        if any(t in tech_lower for t in ['django', 'flask', 'fastapi', 'express']):
            dirs.add('src/api/')
            dirs.add('src/models/')
            if 'django' in tech_lower:
                files.add('manage.py')
                files.add('requirements.txt')
            adaptations.append("Added backend framework structure")

        # Python projects
        if 'python' in tech_lower:
            files.add('requirements.txt')
            files.add('setup.py')
            files.add('.python-version')
            dirs.add('tests/')
            adaptations.append("Added Python project structure")

        # Node.js projects
        if 'node' in tech_lower or any(t in tech_lower for t in ['express', 'next.js']):
            files.add('package.json')
            files.add('.nvmrc')
            adaptations.append("Added Node.js project structure")

        # Docker
        if 'docker' in tech_lower:
            files.add('Dockerfile')
            files.add('docker-compose.yml')
            files.add('.dockerignore')
            adaptations.append("Added Docker configuration")

        # Kubernetes
        if 'kubernetes' in tech_lower:
            dirs.add('k8s/')
            files.add('k8s/deployment.yaml')
            files.add('k8s/service.yaml')
            adaptations.append("Added Kubernetes manifests")

        # Databases
        if any(db in tech_lower for db in ['postgresql', 'mysql', 'mongodb']):
            dirs.add('database/')
            dirs.add('database/migrations/')
            files.add('database/schema.sql' if 'mongodb' not in tech_lower else 'database/schema.json')
            adaptations.append("Added database structure")

        # AI/ML
        if any(t in tech_lower for t in ['ai', 'ml', 'machine learning', 'deep learning']):
            dirs.add('models/')
            dirs.add('training/')
            dirs.add('data/')
            files.add('requirements.txt')
            adaptations.append("Added AI/ML project structure")

    def _adapt_risk(
        self,
        dirs: Set[str],
        files: Set[str],
        adaptations: List[str],
        risk_level: str
    ):
        """Адаптация по уровню риска"""
        if risk_level == 'high':
            dirs.add('risk-management/')
            files.add('RISK-ASSESSMENT.md')
            files.add('CONTINGENCY-PLAN.md')
            files.add('RISK-MITIGATION.md')
            adaptations.append("Added risk management structure")

        if risk_level == 'high' or risk_level == 'medium':
            files.add('RISK-REGISTER.md')
            adaptations.append(f"Added risk tracking for {risk_level} risk project")

    def _adapt_priority(
        self,
        dirs: Set[str],
        files: Set[str],
        adaptations: List[str],
        priority: str
    ):
        """Адаптация по приоритету"""
        if priority == 'critical':
            files.add('CRITICAL-PATH.md')
            files.add('ESCALATION-PROCEDURES.md')
            adaptations.append("Added critical priority tracking")

        if priority in ['critical', 'high']:
            files.add('SPRINT-PLANNING.md')
            files.add('DAILY-STANDUPS.md')
            adaptations.append(f"Added {priority} priority management")

    def _adapt_deadline(
        self,
        dirs: Set[str],
        files: Set[str],
        adaptations: List[str],
        timeline: Dict
    ):
        """Адаптация для проектов с дедлайном"""
        files.add('TIMELINE.md')
        files.add('MILESTONES.md')

        if timeline['months'] <= 3:
            # Короткий дедлайн
            files.add('SPRINT-SCHEDULE.md')
            adaptations.append(f"Added tight deadline tracking ({timeline['formatted']})")
        else:
            adaptations.append(f"Added timeline tracking ({timeline['formatted']})")

    def _adapt_nonprofit(
        self,
        dirs: Set[str],
        files: Set[str],
        adaptations: List[str]
    ):
        """Адаптация для некоммерческих проектов"""
        dirs.add('impact-reporting/')
        files.add('MISSION-STATEMENT.md')
        files.add('IMPACT-METRICS.md')
        files.add('DONOR-RELATIONS.md')
        adaptations.append("Added nonprofit/charity structure")

    def _adapt_commercial(
        self,
        dirs: Set[str],
        files: Set[str],
        adaptations: List[str]
    ):
        """Адаптация для коммерческих проектов"""
        dirs.add('business/')
        files.add('BUSINESS-MODEL.md')
        files.add('REVENUE-PROJECTIONS.md')
        files.add('MARKET-ANALYSIS.md')
        adaptations.append("Added commercial business structure")

    def _adapt_large_scale(
        self,
        dirs: Set[str],
        files: Set[str],
        adaptations: List[str],
        recommendations: List[str]
    ):
        """Адаптация для крупномасштабных проектов"""
        dirs.add('architecture/')
        dirs.add('infrastructure/')
        files.add('ARCHITECTURE.md')
        files.add('SCALING-PLAN.md')
        files.add('INFRASTRUCTURE.md')
        adaptations.append("Added large-scale infrastructure")
        recommendations.append("Consider microservices architecture")
        recommendations.append("Implement monitoring and observability")


def main():
    """Тестирование context-aware адаптера"""
    # Инициализация всех компонентов
    classifier = MultiLabelClassifier()
    composer = TemplateComposer()
    extractor = EnhancedParameterExtractor()
    adapter = ContextAwareAdapter()

    test_cases = [
        "Создать MVP финтех-приложения на React для студентов, бюджет 2.5 млн ₽, команда 12 человек, срок 6 месяцев",
        "Научное исследование высокого риска, грант РНФ 10 млн ₽, команда из 25 исследователей, критический приоритет",
        "E-commerce платформа на Django + PostgreSQL, коммерческий проект, срочный launch в продакшн",
        "Благотворительный фонд с мобильным приложением на React Native, бюджет 1.5 млн ₽",
    ]

    print("="*70)
    print("CONTEXT-AWARE ADAPTER - TESTING")
    print("="*70)

    for i, desc in enumerate(test_cases, 1):
        print(f"\n{'='*70}")
        print(f"Тест {i}: {desc}")
        print('='*70)

        # 1. Классификация
        ml_result = classifier.classify(desc)
        print(f"\n✓ Primary type: {ml_result.primary_type}")
        if ml_result.secondary_types:
            print(f"✓ Secondary: {', '.join(ml_result.secondary_types)}")

        # 2. Композиция базовой структуры
        base_structure = composer.compose(ml_result)
        print(f"✓ Base strategy: {base_structure.strategy}")

        # 3. Извлечение параметров
        params = extractor.extract(desc)
        print(f"\n📊 Extracted parameters:")
        print(f"   Budget: {params.budget.get('formatted') if params.budget else 'N/A'}")
        print(f"   Timeline: {params.timeline.get('formatted') if params.timeline else 'N/A'}")
        print(f"   Team: {params.team_size or 'N/A'}")
        print(f"   Phase: {params.phase or 'N/A'}")
        print(f"   Technologies: {params.technologies or 'N/A'}")
        print(f"   Risk: {params.risk_level or 'N/A'}")
        print(f"   Priority: {params.priority or 'N/A'}")

        # 4. Адаптация структуры
        adapted = adapter.adapt(base_structure, params)

        print(f"\n🔧 Applied adaptations ({len(adapted.adaptations)}):")
        for adaptation in adapted.adaptations:
            print(f"   • {adaptation}")

        if adapted.recommendations:
            print(f"\n💡 Recommendations ({len(adapted.recommendations)}):")
            for rec in adapted.recommendations:
                print(f"   • {rec}")

        print(f"\n📁 Total structure:")
        print(f"   Directories: {len(adapted.directories)}")
        print(f"   Files: {len(adapted.files)}")
        print(f"   Base → Adapted: {len(base_structure.directories)} → {len(adapted.directories)} dirs")


if __name__ == '__main__':
    main()
