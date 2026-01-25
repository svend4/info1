#!/usr/bin/env python3
"""
AI-powered CLI для генерации проектов (V2 - Full Integration)

Интегрирует все компоненты из ЭТАП 9 Фаз 1-4:
- Phase 1: Rule-based classification
- Phase 2: ML classification
- Phase 3: Multi-domain + Context-aware adaptation
- Phase 4: LLM content generation

Уровень абстракции: α=-3 (пользовательский интерфейс)
"""

import sys
import os
import argparse
import subprocess
from pathlib import Path

# Добавление ai_generator в путь
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ai_generator'))

try:
    from ai_generator.multi_label_classifier import MultiLabelClassifier
    from ai_generator.template_composer import TemplateComposer
    from ai_generator.enhanced_parameter_extractor import EnhancedParameterExtractor
    from ai_generator.context_aware_adapter import ContextAwareAdapter
    from ai_generator.llm_content_generator import LLMContentGenerator
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Ensure ai_generator package is accessible")
    sys.exit(1)


def print_header(text: str):
    """Красивый заголовок"""
    print("\n" + "=" * 70)
    print(text)
    print("=" * 70 + "\n")


def print_section(title: str):
    """Секция вывода"""
    print(f"\n{title}")
    print("-" * 70)


def generate_from_description_v2(
    description: str,
    output_dir: str = ".",
    project_name: str = None,
    interactive: bool = False,
    dry_run: bool = False,
    generate_content: bool = True
):
    """
    Генерация проекта с полной AI-powered pipeline (Phases 1-4)

    Args:
        description: Описание проекта
        output_dir: Директория для создания проекта
        project_name: Имя проекта (опционально)
        interactive: Интерактивный режим
        dry_run: Только показать параметры
        generate_content: Генерировать README и контент (Phase 4)
    """
    print_header("🤖 AI-POWERED PROJECT GENERATOR V2 (Phases 1-4)")

    print(f"📝 Ваше описание:")
    print(f"   {description}\n")

    # Initialize all components
    print("🔧 Инициализация AI компонентов...")
    classifier = MultiLabelClassifier()
    composer = TemplateComposer()
    extractor = EnhancedParameterExtractor()
    adapter = ContextAwareAdapter()
    generator = LLMContentGenerator() if generate_content else None

    # Phase 1-2: Multi-label Classification
    print_section("🔍 Phase 1-2: Классификация проекта (ML)")
    ml_result = classifier.classify(description)

    print(f"✓ Primary type: {ml_result.primary_type}")
    print(f"✓ Confidence: {ml_result.primary_confidence:.1%}")

    if ml_result.secondary_types:
        print(f"✓ Secondary types:")
        for sec_type in ml_result.secondary_types:
            conf = ml_result.secondary_confidences[sec_type]
            print(f"  - {sec_type} ({conf:.1%})")

    if ml_result.is_hybrid:
        print(f"✓ Hybrid project: YES")

    # Phase 3: Enhanced Parameter Extraction
    print_section("⚙️  Phase 3: Извлечение параметров")
    params = extractor.extract(description)

    # Show extracted parameters
    if params.budget:
        print(f"✓ Budget: {params.budget['formatted']}")
    if params.timeline:
        print(f"✓ Timeline: {params.timeline['formatted']}")
    if params.team_size:
        print(f"✓ Team size: {params.team_size} members")
    if params.phase:
        print(f"✓ Phase: {params.phase.upper()}")
    if params.technologies:
        print(f"✓ Technologies: {', '.join(params.technologies)}")
    if params.priority:
        print(f"✓ Priority: {params.priority.upper()}")
    if params.risk_level:
        print(f"✓ Risk level: {params.risk_level}")
    if params.industry:
        print(f"✓ Industry: {params.industry}")

    # Flags
    flags = []
    if params.is_funded:
        flags.append("Funded")
    if params.is_commercial:
        flags.append("Commercial")
    if params.is_nonprofit:
        flags.append("Nonprofit")
    if params.has_deadline:
        flags.append("Has deadline")

    if flags:
        print(f"✓ Flags: {', '.join(flags)}")

    # Phase 3: Template Composition
    print_section("📦 Phase 3: Композиция шаблонов")
    base_structure = composer.compose(ml_result)

    print(f"✓ Strategy: {base_structure.strategy}")
    print(f"✓ Merged types: {' + '.join(base_structure.merged_types)}")
    print(f"✓ Base structure: {len(base_structure.directories)} dirs, {len(base_structure.files)} files")

    # Phase 3: Context-Aware Adaptation
    print_section("🔧 Phase 3: Контекстная адаптация")
    adapted = adapter.adapt(base_structure, params)

    print(f"✓ Adaptations applied: {len(adapted.adaptations)}")
    for adaptation in adapted.adaptations:
        print(f"  • {adaptation}")

    if adapted.recommendations:
        print(f"\n💡 Recommendations:")
        for rec in adapted.recommendations:
            print(f"  • {rec}")

    print(f"\n✓ Final structure: {len(adapted.directories)} dirs, {len(adapted.files)} files")
    print(f"✓ Growth: {len(base_structure.directories)} → {len(adapted.directories)} dirs "
          f"({((len(adapted.directories) - len(base_structure.directories)) / len(base_structure.directories) * 100):.0f}% increase)")

    # Phase 4: LLM Content Generation
    if generate_content:
        print_section("📄 Phase 4: Генерация контента (LLM)")

        # Generate project name if not provided
        if not project_name:
            # Simple transliteration
            from ai_generator.classifier import ProjectClassifier
            temp_classifier = ProjectClassifier()
            temp_spec = temp_classifier.classify(description)
            project_name = temp_spec.name

        content = generator.generate_all(
            ml_result, params, adapted, project_name, description
        )

        print(f"✓ README.md generated ({len(content.readme)} chars)")

        if content.architecture:
            print(f"✓ ARCHITECTURE.md generated ({len(content.architecture)} chars)")

        if content.contributing:
            print(f"✓ CONTRIBUTING.md generated ({len(content.contributing)} chars)")

        if content.checklist:
            print(f"✓ CHECKLIST.md generated ({len(content.checklist)} chars)")

        if content.code_examples:
            print(f"✓ Code examples: {len(content.code_examples)} files")
            for filename in content.code_examples.keys():
                print(f"  - {filename}")

    # Project name determination
    if not project_name:
        from ai_generator.classifier import ProjectClassifier
        temp_classifier = ProjectClassifier()
        temp_spec = temp_classifier.classify(description)
        project_name = temp_spec.name

    # Interactive confirmation
    if interactive and not dry_run:
        print_section("❓ Подтверждение")
        print(f"Создать проект '{project_name}' типа '{ml_result.primary_type}'?")
        if ml_result.secondary_types:
            print(f"Вторичные типы: {', '.join(ml_result.secondary_types)}")
        response = input("Продолжить? [Y/n]: ").strip().lower()

        if response and response not in ['y', 'yes', 'да', 'д']:
            print("\n❌ Генерация отменена пользователем")
            return False

    # Dry run
    if dry_run:
        print_section("🔧 Команда для генерации (dry run):")
        generator_path = Path(__file__).parent / "project_template_generator.py"
        cmd = [
            "python",
            str(generator_path),
            "--name", project_name,
            "--type", ml_result.primary_type,
            "--output", output_dir
        ]
        print(f"  {' '.join(cmd)}")
        print("\n💡 Используйте флаг --execute для реальной генерации")
        print("\n📊 Статистика:")
        print(f"   Primary: {ml_result.primary_type} ({ml_result.primary_confidence:.1%})")
        print(f"   Structure: {len(adapted.directories)} dirs, {len(adapted.files)} files")
        print(f"   Adaptations: {len(adapted.adaptations)}")
        if generate_content:
            print(f"   Content files: {3 + len(content.code_examples)}")
        return True

    # Real generation
    print_section("🚀 Генерация проекта...")

    generator_path = Path(__file__).parent / "project_template_generator.py"

    cmd = [
        sys.executable,
        str(generator_path),
        "--name", project_name,
        "--type", ml_result.primary_type,
        "--output", output_dir
    ]

    # Run generator
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(result.stdout)

        # Save generated content if enabled
        if generate_content:
            project_path = Path(output_dir) / project_name

            # Save README
            readme_path = project_path / "README.md"
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(content.readme)
            print(f"✓ Saved: README.md")

            # Save ARCHITECTURE if generated
            if content.architecture:
                arch_path = project_path / "ARCHITECTURE.md"
                with open(arch_path, 'w', encoding='utf-8') as f:
                    f.write(content.architecture)
                print(f"✓ Saved: ARCHITECTURE.md")

            # Save CONTRIBUTING if generated
            if content.contributing:
                contrib_path = project_path / "CONTRIBUTING.md"
                with open(contrib_path, 'w', encoding='utf-8') as f:
                    f.write(content.contributing)
                print(f"✓ Saved: CONTRIBUTING.md")

            # Save CHECKLIST if generated
            if content.checklist:
                checklist_path = project_path / "CHECKLIST.md"
                with open(checklist_path, 'w', encoding='utf-8') as f:
                    f.write(content.checklist)
                print(f"✓ Saved: CHECKLIST.md")

            # Save code examples
            if content.code_examples:
                examples_dir = project_path / "examples"
                examples_dir.mkdir(exist_ok=True)

                for filename, code in content.code_examples.items():
                    example_path = examples_dir / filename
                    with open(example_path, 'w', encoding='utf-8') as f:
                        f.write(code)
                    print(f"✓ Saved: examples/{filename}")

        print_header("✅ ПРОЕКТ УСПЕШНО СОЗДАН!")
        print(f"📁 Расположение: {output_dir}/{project_name}")
        print(f"📦 Primary type: {ml_result.primary_type}")
        if ml_result.secondary_types:
            print(f"📦 Secondary types: {', '.join(ml_result.secondary_types)}")
        print(f"📊 Structure: {len(adapted.directories)} directories, {len(adapted.files)} files")
        print(f"🔧 Adaptations: {len(adapted.adaptations)} applied")

        print(f"\n💡 Следующие шаги:")
        print(f"   1. cd {output_dir}/{project_name}")
        if generate_content:
            print(f"   2. Review generated README.md and documentation")
            if content.code_examples:
                print(f"   3. Check examples/ for code snippets")
            if content.checklist:
                print(f"   4. Follow CHECKLIST.md for project setup")
        else:
            print(f"   2. Отредактируйте README.md с описанием проекта")
        print(f"   5. Запустите: python3 tools/health_metrics.py")
        print(f"   6. Начните развивать проект по методологии ⇑⇓↔\n")

        return True

    except subprocess.CalledProcessError as e:
        print(f"\n❌ Ошибка при генерации проекта:")
        print(e.stderr)
        return False
    except Exception as e:
        print(f"\n❌ Неожиданная ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="🤖 AI-powered генератор проектов V2 (Full Integration - Phases 1-4)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:

  # Простое описание (полная генерация)
  python ai_cli_v2.py "Финтех MVP на React, бюджет 3 млн ₽, команда 8, срок 4 месяца"

  # С указанием имени проекта
  python ai_cli_v2.py "Научное исследование микропластика" --name microplastic-study

  # Dry run (показать параметры без генерации)
  python ai_cli_v2.py "Healthcare телемедицина с AI" --dry-run

  # Без автоматической генерации контента
  python ai_cli_v2.py "E-commerce платформа" --no-content

Возможности V2:
  - Multi-label классификация (2-3 типа одновременно)
  - Template composition (3 стратегии)
  - Enhanced parameter extraction (15+ параметров)
  - Context-aware adaptation (20+ правил)
  - LLM content generation (README, ARCHITECTURE, examples)
        """
    )

    parser.add_argument(
        'description',
        type=str,
        help='Описание проекта на естественном языке'
    )

    parser.add_argument(
        '--name',
        type=str,
        default=None,
        help='Имя проекта (если не указано, генерируется автоматически)'
    )

    parser.add_argument(
        '--output',
        type=str,
        default='.',
        help='Директория для создания проекта (по умолчанию: текущая)'
    )

    parser.add_argument(
        '--interactive', '-i',
        action='store_true',
        help='Интерактивный режим с подтверждением'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Показать параметры без создания проекта'
    )

    parser.add_argument(
        '--execute',
        action='store_true',
        help='Выполнить генерацию (используется с --dry-run для отмены)'
    )

    parser.add_argument(
        '--no-content',
        action='store_true',
        help='Не генерировать автоматический контент (README, examples)'
    )

    args = parser.parse_args()

    # Если указан --execute, отменяем --dry-run
    if args.execute:
        args.dry_run = False

    # Генерация
    success = generate_from_description_v2(
        description=args.description,
        output_dir=args.output,
        project_name=args.name,
        interactive=args.interactive,
        dry_run=args.dry_run,
        generate_content=not args.no_content
    )

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
