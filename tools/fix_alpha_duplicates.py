#!/usr/bin/env python3
"""
Alpha Duplicates Fixer (ЭТАП 7 v0.6)

Удаление дубликатов α-уровней из документов.

Проблема: enrich_alpha.py добавлял α-уровни к документам, которые уже имели их,
создавая дубликаты. Это влияет на подсчет метрик VT.

Решение: Оставить только первое вхождение "Уровень абстракции: α=" в каждом файле.

Уровень абстракции: α=-4 (инструмент)
Статус: ⇓ ВНИЗ (исправление данных)
"""

import re
from pathlib import Path
from typing import Tuple


def fix_duplicates_in_file(file_path: Path, dry_run: bool = False) -> Tuple[bool, int]:
    """
    Удаление дубликатов α-уровней из файла

    Returns:
        (changed, duplicates_removed)
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Найти все вхождения α-уровня в метаданных (начинаются с * или **)
        # Паттерн должен находить только метаданные, а не упоминания в тексте
        pattern = r'^\*{1,2}Уровень абстракции:\**\s*α=[\+\-]?\d+[^\n]*\*{0,2}$'
        matches = list(re.finditer(pattern, content, re.MULTILINE))

        if len(matches) <= 1:
            return False, 0  # Нет дубликатов

        # Оставить только первое вхождение, удалить остальные
        duplicates_count = len(matches) - 1

        # Удалить с конца, чтобы не нарушить индексы
        new_content = content
        for match in reversed(matches[1:]):
            new_content = new_content[:match.start()] + new_content[match.end():]

        if dry_run:
            print(f"  [DRY RUN] {file_path.name}: удалить {duplicates_count} дубликатов")
        else:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"  ✅ {file_path.name}: удалено {duplicates_count} дубликатов")

        return True, duplicates_count

    except Exception as e:
        print(f"  ❌ {file_path.name}: {e}")
        return False, 0


def fix_all_duplicates(directory: Path = Path('.'), dry_run: bool = False) -> dict:
    """Удаление дубликатов во всех markdown файлах"""

    # Найти все markdown файлы
    md_files = list(directory.rglob("*.md"))

    # Исключить некоторые директории
    exclude = ['collective_network/', '.git/', 'node_modules/', '__pycache__']
    md_files = [f for f in md_files if not any(ex in str(f) for ex in exclude)]

    print(f"\n🔍 Проверка {len(md_files)} markdown файлов на дубликаты α-уровней")
    print(f"{'='*70}")

    files_fixed = 0
    total_duplicates = 0

    for md_file in sorted(md_files):
        changed, dup_count = fix_duplicates_in_file(md_file, dry_run)
        if changed:
            files_fixed += 1
            total_duplicates += dup_count

    print(f"{'='*70}")
    print(f"✅ Исправлено файлов: {files_fixed}")
    print(f"🗑️  Удалено дубликатов: {total_duplicates}")
    print(f"📊 Всего проверено: {len(md_files)}")

    return {
        'files_fixed': files_fixed,
        'duplicates_removed': total_duplicates,
        'total_checked': len(md_files)
    }


def main():
    import sys

    dry_run = '--dry-run' in sys.argv

    if dry_run:
        print("🔬 DRY RUN MODE (изменения не будут сохранены)")

    results = fix_all_duplicates(dry_run=dry_run)

    if dry_run:
        print("\n💡 Запустите без --dry-run для применения изменений")
    elif results['files_fixed'] > 0:
        print("\n✅ Дубликаты успешно удалены! Перезапустите health_metrics.py для обновления метрик.")


if __name__ == "__main__":
    main()
