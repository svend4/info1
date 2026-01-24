#!/usr/bin/env python3
"""
Alpha Level Enrichment Tool (ЭТАП 7 v0.7)

Добавление уровней абстракции α к документам для улучшения VT.

Стратегия классификации:
  α=+4: Онтология (фундаментальные концепции)
  α=+3: Философия (принципы и ценности)
  α=+2: Законы и теория (ЭТАПЫ, метрики)
  α=+1: Методология и руководства (как делать)
  α=0:  Архитектура и дизайн
  α=-1: Спецификации и шаблоны
  α=-2: Примеры и туториалы
  α=-3: Конфигурация
  α=-4: Исполняемый код

Уровень абстракции: α=-4 (инструмент)
Статус: ⇓ ВНИЗ (автоматизация)

Вертикальные связи:
    ⇑ ЭТАП-7-КОЛЛЕКТИВНЫЙ-ИНТЕЛЛЕКТ.md (α=+2) — стратегия VT
    ⇑ collective_network/validation_report.md — рекомендация обогащения α
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Tuple


class AlphaEnrichment:
    """Автоматическое добавление α-уровней к документам"""

    # Ключевые слова для классификации
    KEYWORDS = {
        '+4': ['онтология', 'ontology', 'фундаментал'],
        '+3': ['философия', 'philosophy', 'принцип', 'ценност', 'этика'],
        '+2': ['этап', 'метрик', 'закон', 'теория', 'паттерн', 'знания'],
        '+1': ['методология', 'руководство', 'guide', 'применение', 'индекс'],
        '0':  ['архитектур', 'architecture', 'дизайн', 'design', 'структура'],
        '-1': ['спецификаци', 'specification', 'changelog', 'roadmap'],
        '-2': ['пример', 'example', 'tutorial', 'quickstart'],
        '-3': ['конфигурац', 'config', 'setup'],
        '-4': ['код', 'code', '.py', 'исполняемый']
    }

    # Явные правила для конкретных файлов
    # Используется проверка: filename in EXPLICIT_RULES or str(path) in EXPLICIT_RULES
    EXPLICIT_RULES = {
        # Корневые файлы
        'МЕТРИКИ-ЗДОРОВЬЯ.md': '+2',  # Законы метрик
        'ЭВОЛЮЦИЯ-МЕТОДОЛОГИИ.md': '+2',  # Законы эволюции
        'ЭТАП-6-САМОСОВЕРШЕНСТВОВАНИЕ.md': '+2',  # Законы ЭТАПА
        'БУДУЩЕЕ-МЕТОДОЛОГИИ.md': '+3',  # Философия будущего
        'ФИЛОСОФИЯ-ПРОЕКТА.md': '+3',  # Философия
        'ОНТОЛОГИЯ.md': '+4',  # Онтология
        'README.md': '+1',  # Руководство
        'ARCHITECTURE.md': '0',  # Архитектура
        'КАРТА-СВЯЗЕЙ.md': '+1',  # Метаданные
        'CHANGELOG.md': '-1',  # Спецификация
        'ROADMAP.md': '-1',  # Спецификация
        'QUICKSTART.md': '-2',  # Туториал
        'CONTRIBUTING.md': '+1',  # Руководство
        'РЕЗЮМЕ-ПРОЕКТА.md': '+1',  # Обзор
        'ПРИМЕНЕНИЕ-МЕТОДОЛОГИИ.md': '+1',  # Методология
        # Поддиректории (полные пути от корня проекта)
        'ШАБЛОНЫ-КАРТОЧЕК.md': '-1',  # Шаблоны
        'ТЕХНИЧЕСКИЕ-СПЕЦИФИКАЦИИ.md': '-1',  # Спецификации
        'API-REFERENCE.md': '-1',  # API спецификация
        # Паттерны для примеров
        'EXAMPLES.md': '-2',  # Примеры
    }

    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.enriched_count = 0
        self.skipped_count = 0

    def classify_document(self, file_path: Path, content: str) -> str:
        """Определение α-уровня для документа"""
        filename = file_path.name

        # Явное правило по имени файла
        if filename in self.EXPLICIT_RULES:
            return self.EXPLICIT_RULES[filename]

        # Проверка директории Примеры/ - все файлы там α=-2
        if '/Примеры/' in str(file_path) or '\\Примеры\\' in str(file_path):
            if not re.search(r'Уровень абстракции:\s*α=', content):
                return '-2'

        # Уже имеет α
        if re.search(r'Уровень абстракции:\s*α=', content):
            return None  # Skip

        # Анализ по ключевым словам
        content_lower = content.lower()
        scores = {}

        for alpha, keywords in self.KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in content_lower)
            if score > 0:
                scores[alpha] = score

        if not scores:
            return '+1'  # Default: методология

        # Выбрать α с максимальным score
        best_alpha = max(scores, key=scores.get)
        return best_alpha

    def alpha_to_description(self, alpha: str) -> str:
        """Описание α-уровня"""
        descriptions = {
            '+4': 'онтология',
            '+3': 'философия',
            '+2': 'законы и теория',
            '+1': 'методология',
            '0': 'архитектура',
            '-1': 'спецификация',
            '-2': 'примеры',
            '-3': 'конфигурация',
            '-4': 'код'
        }
        return descriptions.get(alpha, 'документ')

    def add_alpha_to_document(self, file_path: Path) -> bool:
        """Добавление α-уровня к документу"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Определить α
            alpha = self.classify_document(file_path, content)

            if alpha is None:
                print(f"  ⏭  {file_path.name}: уже имеет α")
                self.skipped_count += 1
                return False

            # Найти место для вставки (после заголовка, перед первым параграфом)
            lines = content.split('\n')
            insert_index = -1

            # Найти первый заголовок
            for i, line in enumerate(lines):
                if line.startswith('#') and not line.startswith('##'):
                    insert_index = i + 1
                    break

            if insert_index == -1:
                print(f"  ⚠️  {file_path.name}: заголовок не найден")
                self.skipped_count += 1
                return False

            # Вставить α-уровень
            alpha_line = f"\n*Уровень абстракции: α={alpha} ({self.alpha_to_description(alpha)})*"

            # Проверить, есть ли уже метаданные
            if insert_index < len(lines) and lines[insert_index].strip().startswith('*'):
                # Вставить в начало метаданных
                lines.insert(insert_index, alpha_line.strip())
            else:
                # Вставить новую строку метаданных
                lines.insert(insert_index, alpha_line.strip())

            new_content = '\n'.join(lines)

            if self.dry_run:
                print(f"  [DRY RUN] {file_path.name}: α={alpha}")
            else:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"  ✅ {file_path.name}: α={alpha}")

            self.enriched_count += 1
            return True

        except Exception as e:
            print(f"  ❌ {file_path.name}: {e}")
            return False

    def enrich_directory(self, directory: Path, pattern: str = "*.md", recursive: bool = False) -> Dict[str, int]:
        """Обогащение всех документов в директории"""
        if recursive:
            md_files = list(directory.rglob(pattern))
        else:
            md_files = list(directory.glob(pattern))

        # Исключить некоторые файлы
        exclude = ['collective_network/', '.git/', 'node_modules/', '__pycache__']
        md_files = [f for f in md_files if not any(ex in str(f) for ex in exclude)]

        print(f"\n🔍 Найдено {len(md_files)} markdown файлов")
        print(f"{'='*70}")

        for md_file in sorted(md_files):
            self.add_alpha_to_document(md_file)

        print(f"{'='*70}")
        print(f"✅ Обогащено: {self.enriched_count}")
        print(f"⏭  Пропущено: {self.skipped_count}")
        print(f"📊 Всего: {len(md_files)}")

        return {
            'enriched': self.enriched_count,
            'skipped': self.skipped_count,
            'total': len(md_files)
        }


def main():
    import sys

    dry_run = '--dry-run' in sys.argv
    recursive = '--recursive' in sys.argv or '--subdirs' in sys.argv

    if dry_run:
        print("🔬 DRY RUN MODE (изменения не будут сохранены)")

    if recursive:
        print("🔄 RECURSIVE MODE (включая поддиректории)")

    enricher = AlphaEnrichment(dry_run=dry_run)

    # Обогатить корневую директорию
    results = enricher.enrich_directory(Path('.'), recursive=recursive)

    if dry_run:
        print("\n💡 Запустите без --dry-run для применения изменений")


if __name__ == "__main__":
    main()
