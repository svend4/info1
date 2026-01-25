#!/usr/bin/env python3
"""
AI-powered CLI для генерации проектов

Интерфейс командной строки с поддержкой естественного языка.
Позволяет пользователям описывать проекты обычным языком вместо явного указания типа.

Уровень абстракции: α=-3 (пользовательский интерфейс)
Связи:
  ⇑ ЭТАП-9-ПЛАН.md (α=+1) — концепция AI-генерации
  ↔ ai_generator/ (α=-4) — AI компоненты
  ↔ project_template_generator.py (α=-4) — генератор проектов

Использование:
  python ai_cli.py "Хочу создать веб-приложение для управления задачами"
  python ai_cli.py "Научное исследование микропластика, грант 4.5 млн ₽"
"""

import sys
import os
import argparse
import subprocess
from pathlib import Path

# Добавление ai_generator в путь
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ai_generator'))

from ai_generator.classifier import ProjectClassifier


def print_header(text: str):
    """Красивый заголовок"""
    print("\n" + "=" * 70)
    print(text)
    print("=" * 70 + "\n")


def print_section(title: str):
    """Секция вывода"""
    print(f"\n{title}")
    print("-" * 70)


def generate_from_description(description: str, output_dir: str = ".",
                              project_name: str = None, interactive: bool = False,
                              dry_run: bool = False):
    """
    Генерация проекта на основе естественно-языкового описания

    Args:
        description: Описание проекта
        output_dir: Директория для создания проекта
        project_name: Имя проекта (опционально)
        interactive: Интерактивный режим с подтверждением
        dry_run: Только показать параметры, не создавать проект
    """
    print_header("🤖 AI-POWERED PROJECT GENERATOR")

    print(f"📝 Ваше описание:")
    print(f"   {description}\n")

    # Классификация проекта
    print("🔍 Анализирую описание...")
    classifier = ProjectClassifier()
    spec = classifier.classify(description, project_name)

    # Вывод результатов анализа
    print_section("📊 Результаты анализа:")
    print(f"✓ Определён тип проекта: {spec.primary_type}")
    print(f"✓ Уверенность: {spec.confidence:.0%}")
    print(f"✓ Предложенное имя: {spec.name}")

    if spec.secondary_types:
        print(f"✓ Дополнительные типы: {', '.join(spec.secondary_types)}")

    # Параметры проекта
    params_shown = False
    for key, value in spec.parameters.items():
        if value and value != []:
            if not params_shown:
                print_section("⚙️  Извлечённые параметры:")
                params_shown = True

            if isinstance(value, list):
                value_str = ', '.join(value)
            else:
                value_str = str(value)

            print(f"  • {key}: {value_str}")

    # Рекомендации
    recommendations = classifier.recommend_structure(spec)
    if recommendations['suggestions']:
        print_section("💡 Рекомендации:")
        for suggestion in recommendations['suggestions']:
            print(f"  • {suggestion}")

    # Интерактивное подтверждение
    if interactive and not dry_run:
        print_section("❓ Подтверждение")
        print(f"Создать проект '{spec.name}' типа '{spec.primary_type}'?")
        response = input("Продолжить? [Y/n]: ").strip().lower()

        if response and response not in ['y', 'yes', 'да', 'д']:
            print("\n❌ Генерация отменена пользователем")
            return False

    # Dry run - только показываем, что будет сделано
    if dry_run:
        print_section("🔧 Команда для генерации (dry run):")
        generator_path = Path(__file__).parent / "project_template_generator.py"
        cmd = [
            "python",
            str(generator_path),
            "--name", spec.name,
            "--type", spec.primary_type,
            "--output", output_dir
        ]
        print(f"  {' '.join(cmd)}")
        print("\n💡 Используйте флаг --execute для реальной генерации")
        return True

    # Реальная генерация
    print_section("🚀 Генерация проекта...")

    generator_path = Path(__file__).parent / "project_template_generator.py"

    cmd = [
        sys.executable,
        str(generator_path),
        "--name", spec.name,
        "--type", spec.primary_type,
        "--output", output_dir
    ]

    # Запуск генератора
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)

        # Вывод результата генератора
        print(result.stdout)

        print_header("✅ ПРОЕКТ УСПЕШНО СОЗДАН!")
        print(f"📁 Расположение: {output_dir}/{spec.name}")
        print(f"📦 Тип: {spec.primary_type}")
        print(f"\n💡 Следующие шаги:")
        print(f"   1. cd {output_dir}/{spec.name}")
        print(f"   2. Отредактируйте README.md с описанием проекта")
        print(f"   3. Запустите: python3 tools/health_metrics.py")
        print(f"   4. Начните развивать проект по методологии ⇑⇓↔\n")

        return True

    except subprocess.CalledProcessError as e:
        print(f"\n❌ Ошибка при генерации проекта:")
        print(e.stderr)
        return False
    except Exception as e:
        print(f"\n❌ Неожиданная ошибка: {e}")
        return False


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="🤖 AI-powered генератор проектов на основе естественного языка",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:

  # Простое описание
  python ai_cli.py "Хочу создать веб-приложение для управления задачами"

  # С указанием имени проекта
  python ai_cli.py "Научное исследование микропластика" --name microplastic-study

  # Интерактивный режим с подтверждением
  python ai_cli.py "Открываю клинику на 50 сотрудников" --interactive

  # Dry run (показать параметры без генерации)
  python ai_cli.py "Стартап в области fintech" --dry-run

  # Указание директории вывода
  python ai_cli.py "Мобильное приложение для финансов" --output projects/

Поддерживаемые типы проектов:
  software, research, business, education, legal, healthcare,
  arts, finance, government, nonprofit, manufacturing, agriculture,
  sports, hospitality, retail, hobby
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

    args = parser.parse_args()

    # Если указан --execute, отменяем --dry-run
    if args.execute:
        args.dry_run = False

    # Генерация
    success = generate_from_description(
        description=args.description,
        output_dir=args.output,
        project_name=args.name,
        interactive=args.interactive,
        dry_run=args.dry_run
    )

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
