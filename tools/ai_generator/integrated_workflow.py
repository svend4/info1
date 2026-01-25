#!/usr/bin/env python3
"""
Integrated Workflow - End-to-End Demo

Демонстрация полного workflow с использованием всех 6 вариантов ЭТАПА 10:
1. Web Integration - AI analysis
2. Production API - authentication
3. Model Enhancement - improved predictions
4. GitHub Integration - auto repo creation
5. Community Templates - template reuse
6. Advanced Features - health monitoring

Полный цикл: Описание → AI анализ → Генерация → GitHub → Marketplace → Monitoring
"""

import sys
import os
from pathlib import Path
import json
import tempfile
from typing import Optional

# Добавляем пути
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Импорты всех компонентов
from tools.ai_generator.multi_label_classifier import MultiLabelClassifier
from tools.ai_generator.enhanced_parameter_extractor import EnhancedParameterExtractor
from tools.ai_generator.template_composer import TemplateComposer
from tools.ai_generator.context_aware_adapter import ContextAwareAdapter
from tools.ai_generator.llm_content_generator import LLMContentGenerator

# Variant 3: Model Enhancement
from tools.ai_generator.confidence_calibration import ConfidenceCalibrator

# Variant 4: GitHub Integration
from tools.ai_generator.github_integration import GitHubConfig, get_github_token
from tools.ai_generator.github_project_creator import GitHubProjectCreator

# Variant 5: Community Templates
from tools.ai_generator.template_marketplace import TemplateMarketplace

# Variant 6: Advanced Features
from tools.ai_generator.project_evolution_tracker import ProjectEvolutionTracker


class IntegratedWorkflow:
    """
    Интегрированный workflow всех компонентов

    Демонстрирует как все варианты работают вместе.
    """

    def __init__(self, enable_github: bool = False, github_token: Optional[str] = None):
        """
        Args:
            enable_github: Включить GitHub integration
            github_token: GitHub token (optional)
        """
        print("="*70)
        print("🚀 INTEGRATED WORKFLOW - AI-POWERED PROJECT GENERATION")
        print("="*70)

        # Variant 1 & 2: AI Components
        print("\n📦 Initializing AI components...")
        self.classifier = MultiLabelClassifier()
        self.extractor = EnhancedParameterExtractor()
        self.composer = TemplateComposer()
        self.adapter = ContextAwareAdapter()
        self.generator = LLMContentGenerator()
        print("✅ AI components ready")

        # Variant 3: Model Enhancement (optional calibrator)
        self.calibrator = None

        # Variant 4: GitHub Integration
        self.enable_github = enable_github
        self.github_creator = None

        if enable_github:
            if not github_token:
                github_token = get_github_token()

            if github_token:
                username = os.environ.get('GITHUB_USERNAME', 'demo-user')
                config = GitHubConfig(token=github_token, username=username)
                self.github_creator = GitHubProjectCreator(config)
                print("✅ GitHub integration enabled")
            else:
                print("⚠️  GitHub token not found, skipping GitHub integration")
                self.enable_github = False

        # Variant 5: Community Templates
        marketplace_path = Path.home() / '.ai_generator' / 'marketplace'
        self.marketplace = TemplateMarketplace(marketplace_path)
        print("✅ Marketplace ready")

        # Variant 6: Advanced Features (будет инициализирован для каждого проекта)
        self.tracker = None

    def run_complete_workflow(
        self,
        description: str,
        project_name: Optional[str] = None,
        output_dir: Optional[Path] = None,
        publish_to_marketplace: bool = False,
        create_github_repo: bool = False
    ) -> dict:
        """
        Полный end-to-end workflow

        Args:
            description: Описание проекта
            project_name: Название (auto-generate если None)
            output_dir: Директория для проекта
            publish_to_marketplace: Опубликовать в marketplace
            create_github_repo: Создать GitHub repo

        Returns:
            Dict с результатами всех этапов
        """
        print("\n" + "="*70)
        print("STARTING INTEGRATED WORKFLOW")
        print("="*70)

        results = {}

        # ===== ЭТАП 1: AI ANALYSIS =====
        print("\n📊 STEP 1: AI Analysis")
        print("-" * 70)

        ml_result = self.classifier.classify(description)
        params = self.extractor.extract(description)

        print(f"✅ Classification: {ml_result.primary_type}")
        print(f"   Confidence: {ml_result.primary_confidence:.2%}")

        if ml_result.is_hybrid:
            print(f"   Hybrid: {', '.join(ml_result.secondary_types[:2])}")

        print(f"\n✅ Parameters extracted:")
        print(f"   Budget: {params.budget}")
        print(f"   Timeline: {params.timeline}")
        print(f"   Team size: {params.team_size}")
        print(f"   Technologies: {', '.join(params.technologies[:3])}")

        results['analysis'] = {
            'classification': ml_result,
            'parameters': params
        }

        # ===== ЭТАП 2: STRUCTURE GENERATION =====
        print("\n🏗️  STEP 2: Structure Generation")
        print("-" * 70)

        base_structure = self.composer.compose(ml_result)
        adapted = self.adapter.adapt(base_structure, params)

        print(f"✅ Base structure: {len(base_structure.directories)} dirs, {len(base_structure.files)} files")
        print(f"✅ Adapted structure: {len(adapted.directories)} dirs, {len(adapted.files)} files")
        print(f"   Adaptations: {len(adapted.adaptations)}")

        results['structure'] = {
            'base': base_structure,
            'adapted': adapted
        }

        # ===== ЭТАП 3: CONTENT GENERATION =====
        print("\n📝 STEP 3: Content Generation (LLM)")
        print("-" * 70)

        # Генерация имени если не указано
        if not project_name:
            from tools.ai_generator.classifier import ProjectClassifier
            temp_classifier = ProjectClassifier()
            temp_spec = temp_classifier.classify(description)
            project_name = temp_spec.name

        print(f"Project name: {project_name}")

        content = self.generator.generate_all(
            ml_result, params, adapted, project_name, description
        )

        print(f"✅ Generated content:")
        print(f"   README: {len(content.readme)} chars")
        if content.architecture:
            print(f"   ARCHITECTURE: {len(content.architecture)} chars")
        if content.contributing:
            print(f"   CONTRIBUTING: {len(content.contributing)} chars")
        if content.code_examples:
            print(f"   Code examples: {len(content.code_examples)} files")

        results['content'] = content
        results['project_name'] = project_name

        # ===== ЭТАП 4: PROJECT CREATION =====
        print("\n📦 STEP 4: Project Creation")
        print("-" * 70)

        if output_dir is None:
            output_dir = Path(tempfile.mkdtemp())

        project_path = output_dir / project_name

        # Используем project_template_generator.py
        import subprocess
        generator_path = Path(__file__).parent.parent / 'project_template_generator.py'

        cmd = [
            sys.executable,
            str(generator_path),
            '--name', project_name,
            '--type', ml_result.primary_type,
            '--output', str(output_dir)
        ]

        subprocess.run(cmd, capture_output=True, text=True, check=True)

        # Сохранение документации
        (project_path / "README.md").write_text(content.readme, encoding='utf-8')

        if content.architecture:
            (project_path / "ARCHITECTURE.md").write_text(content.architecture, encoding='utf-8')

        if content.contributing:
            (project_path / "CONTRIBUTING.md").write_text(content.contributing, encoding='utf-8')

        if content.checklist:
            (project_path / "CHECKLIST.md").write_text(content.checklist, encoding='utf-8')

        if content.code_examples:
            examples_dir = project_path / "examples"
            examples_dir.mkdir(exist_ok=True)
            for filename, code in content.code_examples.items():
                (examples_dir / filename).write_text(code, encoding='utf-8')

        print(f"✅ Project created: {project_path}")

        results['project_path'] = project_path

        # ===== ЭТАП 5: GITHUB INTEGRATION (optional) =====
        if create_github_repo and self.enable_github and self.github_creator:
            print("\n🐙 STEP 5: GitHub Integration")
            print("-" * 70)

            try:
                github_result = self.github_creator.create_complete_project(
                    description=description,
                    project_name=project_name,
                    private=False,
                    output_dir=output_dir,
                    push_to_github=True,
                    setup_project_board=True
                )

                print(f"✅ GitHub repo created: {github_result['repo_info'].html_url}")
                results['github'] = github_result['repo_info']

            except Exception as e:
                print(f"⚠️  GitHub creation failed: {str(e)}")
                results['github'] = None
        else:
            print("\n⏭️  STEP 5: GitHub Integration (skipped)")
            results['github'] = None

        # ===== ЭТАП 6: MARKETPLACE (optional) =====
        if publish_to_marketplace:
            print("\n🌐 STEP 6: Marketplace Publication")
            print("-" * 70)

            try:
                metadata = {
                    'name': project_name,
                    'description': description,
                    'author': 'AI Generator',
                    'category': ml_result.primary_type,
                    'language': params.technologies[0] if params.technologies else 'python',
                    'tags': params.technologies[:5],
                    'license': 'MIT'
                }

                template_id = self.marketplace.publish_template(
                    source_path=project_path,
                    metadata=metadata
                )

                print(f"✅ Published to marketplace: {template_id}")
                results['marketplace_id'] = template_id

            except Exception as e:
                print(f"⚠️  Marketplace publication failed: {str(e)}")
                results['marketplace_id'] = None
        else:
            print("\n⏭️  STEP 6: Marketplace Publication (skipped)")
            results['marketplace_id'] = None

        # ===== ЭТАП 7: HEALTH MONITORING =====
        print("\n💚 STEP 7: Initial Health Check")
        print("-" * 70)

        try:
            tracker = ProjectEvolutionTracker(project_path)

            # Initial snapshot
            snapshot = tracker.take_snapshot()
            print(f"✅ Snapshot: {snapshot.files_count} files, {snapshot.lines_of_code} LOC")

            # Metrics
            metrics = tracker.calculate_metrics()
            print(f"✅ Metrics: {metrics.code_lines} code lines, {metrics.functions_count} functions")

            # Health score
            health = tracker.calculate_health_score()
            print(f"✅ Health score: {health.overall_score}/100")

            print(f"\n   Component scores:")
            print(f"   - Structure: {health.structure_score}/100")
            print(f"   - Code Quality: {health.code_quality_score}/100")
            print(f"   - Tests: {health.test_coverage_score}/100")
            print(f"   - Docs: {health.documentation_score}/100")
            print(f"   - Maintainability: {health.maintainability_score}/100")

            results['health'] = health

        except Exception as e:
            print(f"⚠️  Health check failed: {str(e)}")
            results['health'] = None

        # ===== SUMMARY =====
        print("\n" + "="*70)
        print("✅ WORKFLOW COMPLETED SUCCESSFULLY!")
        print("="*70)

        print(f"\n📊 Summary:")
        print(f"   Project: {project_name}")
        print(f"   Type: {ml_result.primary_type}")
        print(f"   Location: {project_path}")

        if results.get('github'):
            print(f"   GitHub: {results['github'].html_url}")

        if results.get('marketplace_id'):
            print(f"   Marketplace ID: {results['marketplace_id']}")

        if results.get('health'):
            print(f"   Health: {results['health'].overall_score}/100")

        print(f"\n💡 Next steps:")
        print(f"   cd {project_path}")
        print(f"   # Review the generated structure")
        print(f"   # Start implementing your features!")

        return results


def demo_workflow():
    """
    Демонстрация integrated workflow
    """
    # Example project descriptions
    examples = [
        {
            'description': 'AI-powered финтех платформа для автоматического кредитного скоринга с ML моделями и интеграцией банковских API',
            'name': 'credit-scoring-ai'
        },
        {
            'description': 'Мобильное приложение для медитации с guided sessions, progress tracking и social features',
            'name': 'meditation-app'
        },
        {
            'description': 'Blockchain-based supply chain tracking система с IoT integration и real-time analytics',
            'name': 'supply-chain-tracker'
        }
    ]

    print("\n🎯 INTEGRATED WORKFLOW DEMO")
    print("="*70)
    print("\nAvailable examples:")

    for i, ex in enumerate(examples, 1):
        print(f"\n{i}. {ex['name']}")
        print(f"   {ex['description'][:80]}...")

    print(f"\n{len(examples) + 1}. Custom project (enter your own description)")

    # Для demo используем первый пример
    print("\n" + "="*70)
    print("Running demo with Example 1...")
    print("="*70)

    workflow = IntegratedWorkflow(
        enable_github=False  # Set to True if you have GitHub token
    )

    results = workflow.run_complete_workflow(
        description=examples[0]['description'],
        project_name=examples[0]['name'],
        output_dir=Path('./demo_projects'),
        publish_to_marketplace=False,  # Set to True to publish
        create_github_repo=False  # Set to True with GitHub token
    )

    # Сохранение отчёта
    report_path = Path('./demo_projects') / examples[0]['name'] / 'WORKFLOW_REPORT.json'
    report_data = {
        'project_name': results['project_name'],
        'classification': {
            'primary_type': results['analysis']['classification'].primary_type,
            'confidence': results['analysis']['classification'].primary_confidence,
            'is_hybrid': results['analysis']['classification'].is_hybrid
        },
        'parameters': {
            'budget': results['analysis']['parameters'].budget,
            'timeline': results['analysis']['parameters'].timeline,
            'team_size': results['analysis']['parameters'].team_size,
            'technologies': results['analysis']['parameters'].technologies
        },
        'structure': {
            'directories': len(results['structure']['adapted'].directories),
            'files': len(results['structure']['adapted'].files),
            'adaptations': len(results['structure']['adapted'].adaptations)
        },
        'health': {
            'overall_score': results['health'].overall_score if results['health'] else None,
            'structure_score': results['health'].structure_score if results['health'] else None
        } if results['health'] else None
    }

    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report_data, f, ensure_ascii=False, indent=2)

    print(f"\n📄 Workflow report saved to: {report_path}")


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        description="Integrated Workflow - End-to-End Demo"
    )

    parser.add_argument(
        '--demo',
        action='store_true',
        help='Run demo with example projects'
    )

    parser.add_argument(
        '--description',
        help='Project description'
    )

    parser.add_argument(
        '--name',
        help='Project name'
    )

    parser.add_argument(
        '--output',
        type=Path,
        default=Path('./generated_projects'),
        help='Output directory'
    )

    parser.add_argument(
        '--github',
        action='store_true',
        help='Create GitHub repository'
    )

    parser.add_argument(
        '--marketplace',
        action='store_true',
        help='Publish to marketplace'
    )

    args = parser.parse_args()

    if args.demo:
        demo_workflow()
    elif args.description:
        workflow = IntegratedWorkflow(enable_github=args.github)

        workflow.run_complete_workflow(
            description=args.description,
            project_name=args.name,
            output_dir=args.output,
            publish_to_marketplace=args.marketplace,
            create_github_repo=args.github
        )
    else:
        parser.print_help()
        print("\n\nExample usage:")
        print("  # Run demo")
        print("  python integrated_workflow.py --demo")
        print("\n  # Custom project")
        print("  python integrated_workflow.py \\")
        print("    --description 'AI платформа для анализа данных' \\")
        print("    --name 'data-analytics-platform' \\")
        print("    --output ./projects")
