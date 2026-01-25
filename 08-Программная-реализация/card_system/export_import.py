#!/usr/bin/env python3
"""
Утилиты импорта и экспорта карточек

Поддерживаемые форматы:
- JSON: экспорт/импорт в структурированном формате
- CSV: экспорт для анализа в Excel/Google Sheets
- Archive: создание ZIP-архива всех карточек
- Markdown: массовый экспорт/импорт

Уровень абстракции: α=-4 (исполняемый код)
"""

import json
import csv
import zipfile
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

from card import Card, CardType, CardStatus, Priority
from card_manager import CardManager


class CardExporter:
    """Экспорт карточек в различные форматы"""

    def __init__(self, manager: CardManager):
        self.manager = manager

    def export_to_json(
        self,
        output_file: Path,
        card_ids: Optional[List[str]] = None,
        pretty: bool = True
    ) -> int:
        """
        Экспорт карточек в JSON

        Args:
            output_file: Путь к выходному файлу
            card_ids: Список ID карточек (если None, экспортировать все)
            pretty: Форматировать JSON с отступами

        Returns:
            int: Количество экспортированных карточек
        """
        # Получить карточки
        if card_ids:
            cards = [self.manager.read(cid) for cid in card_ids]
            cards = [c for c in cards if c is not None]
        else:
            cards = self.manager.search(limit=10000)

        # Конвертировать в словари
        cards_data = []
        for card in cards:
            card_dict = self._card_to_dict(card)
            cards_data.append(card_dict)

        # Метаданные экспорта
        export_data = {
            "export_date": datetime.now().isoformat(),
            "export_version": "1.0",
            "total_cards": len(cards_data),
            "cards": cards_data
        }

        # Сохранить
        with open(output_file, 'w', encoding='utf-8') as f:
            if pretty:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            else:
                json.dump(export_data, f, ensure_ascii=False)

        return len(cards_data)

    def export_to_csv(
        self,
        output_file: Path,
        card_ids: Optional[List[str]] = None,
        include_content: bool = False
    ) -> int:
        """
        Экспорт карточек в CSV

        Args:
            output_file: Путь к выходному файлу
            card_ids: Список ID карточек (если None, экспортировать все)
            include_content: Включать ли содержимое (content)

        Returns:
            int: Количество экспортированных карточек
        """
        # Получить карточки
        if card_ids:
            cards = [self.manager.read(cid) for cid in card_ids]
            cards = [c for c in cards if c is not None]
        else:
            cards = self.manager.search(limit=10000)

        if not cards:
            return 0

        # Определить поля CSV
        fields = [
            'id', 'type', 'title', 'created', 'modified',
            'status', 'priority', 'tags'
        ]

        if include_content:
            fields.append('content')

        # Записать CSV
        with open(output_file, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()

            for card in cards:
                row = {
                    'id': card.id,
                    'type': card.type.value,
                    'title': card.title,
                    'created': card.created.isoformat(),
                    'modified': card.modified.isoformat(),
                    'status': card.status.value if card.status else '',
                    'priority': card.priority.value if card.priority else '',
                    'tags': ','.join(card.tags)
                }

                if include_content:
                    # Экранировать переводы строк
                    row['content'] = card.content.replace('\n', '\\n')

                writer.writerow(row)

        return len(cards)

    def export_to_archive(
        self,
        output_file: Path,
        card_ids: Optional[List[str]] = None
    ) -> int:
        """
        Создать ZIP-архив с карточками в формате Markdown

        Args:
            output_file: Путь к ZIP-архиву
            card_ids: Список ID карточек (если None, экспортировать все)

        Returns:
            int: Количество экспортированных карточек
        """
        # Получить карточки
        if card_ids:
            cards = [self.manager.read(cid) for cid in card_ids]
            cards = [c for c in cards if c is not None]
        else:
            cards = self.manager.search(limit=10000)

        # Создать ZIP
        with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
            for card in cards:
                # Имя файла в архиве
                filename = f"{card.type.value}/{card.id}.md"

                # Markdown содержимое
                markdown = card.to_markdown()

                # Добавить в архив
                zf.writestr(filename, markdown)

            # Добавить метаданные
            metadata = {
                "export_date": datetime.now().isoformat(),
                "total_cards": len(cards),
                "types": self._get_types_stats(cards)
            }
            zf.writestr("metadata.json", json.dumps(metadata, indent=2))

        return len(cards)

    def export_stats_report(self, output_file: Path) -> Dict[str, Any]:
        """
        Создать отчёт со статистикой в JSON

        Args:
            output_file: Путь к выходному файлу

        Returns:
            Dict: Статистика
        """
        stats = self.manager.get_stats()

        # Расширенная статистика
        all_cards = self.manager.search(limit=10000)
        stats['total_cards'] = len(all_cards)
        stats['by_status'] = self._count_by_attribute(all_cards, 'status')
        stats['by_priority'] = self._count_by_attribute(all_cards, 'priority')
        stats['by_type'] = self._count_by_attribute(all_cards, 'type')

        # Топ-10 тегов
        tag_counts = {}
        for card in all_cards:
            for tag in card.tags:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1

        stats['top_tags'] = sorted(
            tag_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]

        # Сохранить
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2, default=str)

        return stats

    def _card_to_dict(self, card: Card) -> Dict[str, Any]:
        """Конвертировать карточку в словарь"""
        data = {
            'id': card.id,
            'type': card.type.value,
            'title': card.title,
            'created': card.created.isoformat(),
            'modified': card.modified.isoformat(),
            'status': card.status.value if card.status else None,
            'priority': card.priority.value if card.priority else None,
            'tags': card.tags,
            'linked_cards': card.linked_cards,
            'content': card.content
        }

        # Добавить специфичные поля по типу
        if hasattr(card, '__dict__'):
            for key, value in card.__dict__.items():
                if key not in data and not key.startswith('_'):
                    # Конвертировать datetime в ISO
                    if isinstance(value, datetime):
                        data[key] = value.isoformat()
                    else:
                        data[key] = value

        return data

    def _get_types_stats(self, cards: List[Card]) -> Dict[str, int]:
        """Подсчёт карточек по типам"""
        stats = {}
        for card in cards:
            type_value = card.type.value
            stats[type_value] = stats.get(type_value, 0) + 1
        return stats

    def _count_by_attribute(self, cards: List[Card], attr: str) -> Dict[str, int]:
        """Подсчёт по атрибуту"""
        counts = {}
        for card in cards:
            value = getattr(card, attr, None)
            if value:
                key = value.value if hasattr(value, 'value') else str(value)
                counts[key] = counts.get(key, 0) + 1
        return counts


class CardImporter:
    """Импорт карточек из различных форматов"""

    def __init__(self, manager: CardManager):
        self.manager = manager

    def import_from_json(
        self,
        input_file: Path,
        overwrite: bool = False
    ) -> Dict[str, int]:
        """
        Импорт карточек из JSON

        Args:
            input_file: Путь к JSON-файлу
            overwrite: Перезаписывать существующие карточки

        Returns:
            Dict: Статистика импорта (imported, skipped, errors)
        """
        stats = {'imported': 0, 'skipped': 0, 'errors': 0}

        # Загрузить JSON
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        cards_data = data.get('cards', [])

        for card_data in cards_data:
            try:
                # Проверить, существует ли карточка
                card_id = card_data.get('id')
                existing = self.manager.read(card_id) if card_id else None

                if existing and not overwrite:
                    stats['skipped'] += 1
                    continue

                # Импортировать
                self._import_card_from_dict(card_data, overwrite)
                stats['imported'] += 1

            except Exception as e:
                print(f"⚠️  Ошибка импорта карточки {card_data.get('id', '?')}: {e}")
                stats['errors'] += 1

        return stats

    def import_from_archive(
        self,
        archive_file: Path,
        overwrite: bool = False
    ) -> Dict[str, int]:
        """
        Импорт карточек из ZIP-архива

        Args:
            archive_file: Путь к ZIP-архиву
            overwrite: Перезаписывать существующие карточки

        Returns:
            Dict: Статистика импорта
        """
        stats = {'imported': 0, 'skipped': 0, 'errors': 0}

        with zipfile.ZipFile(archive_file, 'r') as zf:
            for filename in zf.namelist():
                if not filename.endswith('.md'):
                    continue

                try:
                    # Прочитать Markdown
                    markdown = zf.read(filename).decode('utf-8')

                    # Парсинг
                    card = Card.from_markdown(markdown)

                    # Проверить существование
                    existing = self.manager.read(card.id)

                    if existing and not overwrite:
                        stats['skipped'] += 1
                        continue

                    # Создать или обновить
                    if existing:
                        self.manager.update(card.id, **card.__dict__)
                    else:
                        self.manager.create(card)

                    stats['imported'] += 1

                except Exception as e:
                    print(f"⚠️  Ошибка импорта {filename}: {e}")
                    stats['errors'] += 1

        return stats

    def import_from_directory(
        self,
        directory: Path,
        overwrite: bool = False,
        recursive: bool = True
    ) -> Dict[str, int]:
        """
        Импорт карточек из директории с Markdown-файлами

        Args:
            directory: Директория с .md файлами
            overwrite: Перезаписывать существующие карточки
            recursive: Рекурсивный поиск в поддиректориях

        Returns:
            Dict: Статистика импорта
        """
        stats = {'imported': 0, 'skipped': 0, 'errors': 0}

        # Найти все .md файлы
        pattern = "**/*.md" if recursive else "*.md"
        md_files = Path(directory).glob(pattern)

        for md_file in md_files:
            try:
                # Прочитать файл
                markdown = md_file.read_text(encoding='utf-8')

                # Парсинг
                card = Card.from_markdown(markdown)

                # Проверить существование
                existing = self.manager.read(card.id)

                if existing and not overwrite:
                    stats['skipped'] += 1
                    continue

                # Создать или обновить
                if existing:
                    self.manager.update(card.id, **card.__dict__)
                else:
                    self.manager.create(card)

                stats['imported'] += 1

            except Exception as e:
                print(f"⚠️  Ошибка импорта {md_file}: {e}")
                stats['errors'] += 1

        return stats

    def _import_card_from_dict(self, data: Dict[str, Any], overwrite: bool = False):
        """Импорт карточки из словаря"""
        # Конвертировать строки обратно в enum и datetime
        if 'type' in data:
            data['type'] = CardType(data['type'])
        if 'status' in data and data['status']:
            data['status'] = CardStatus(data['status'])
        if 'priority' in data and data['priority']:
            data['priority'] = Priority(data['priority'])

        # Конвертировать ISO-строки в datetime
        for field in ['created', 'modified', 'due_date', 'appointment_date', 'reminder', 'reminder_time']:
            if field in data and isinstance(data[field], str):
                data[field] = datetime.fromisoformat(data[field])

        # Создать карточку
        card_id = data.get('id')
        existing = self.manager.read(card_id) if card_id else None

        if existing and overwrite:
            # Обновить
            self.manager.update(card_id, **data)
        else:
            # Создать новую (Card.create использует тип для выбора класса)
            card_type = data.get('type', CardType.NOTE)
            card = Card.create(card_type, **data)
            self.manager.create(card)


def main():
    """CLI для экспорта/импорта"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Импорт/экспорт карточек'
    )

    subparsers = parser.add_subparsers(dest='command', help='Команды')

    # Экспорт в JSON
    export_json = subparsers.add_parser('export-json', help='Экспорт в JSON')
    export_json.add_argument('output', type=Path, help='Выходной файл')
    export_json.add_argument('--cards-dir', type=Path, default=Path('./cards'), help='Директория карточек')
    export_json.add_argument('--compact', action='store_true', help='Компактный JSON')

    # Экспорт в CSV
    export_csv = subparsers.add_parser('export-csv', help='Экспорт в CSV')
    export_csv.add_argument('output', type=Path, help='Выходной файл')
    export_csv.add_argument('--cards-dir', type=Path, default=Path('./cards'), help='Директория карточек')
    export_csv.add_argument('--with-content', action='store_true', help='Включить содержимое')

    # Экспорт в архив
    export_zip = subparsers.add_parser('export-zip', help='Экспорт в ZIP-архив')
    export_zip.add_argument('output', type=Path, help='Выходной файл')
    export_zip.add_argument('--cards-dir', type=Path, default=Path('./cards'), help='Директория карточек')

    # Экспорт статистики
    export_stats = subparsers.add_parser('export-stats', help='Экспорт статистики')
    export_stats.add_argument('output', type=Path, help='Выходной файл')
    export_stats.add_argument('--cards-dir', type=Path, default=Path('./cards'), help='Директория карточек')

    # Импорт из JSON
    import_json = subparsers.add_parser('import-json', help='Импорт из JSON')
    import_json.add_argument('input', type=Path, help='Входной файл')
    import_json.add_argument('--cards-dir', type=Path, default=Path('./cards'), help='Директория карточек')
    import_json.add_argument('--overwrite', action='store_true', help='Перезаписать существующие')

    # Импорт из архива
    import_zip = subparsers.add_parser('import-zip', help='Импорт из ZIP-архива')
    import_zip.add_argument('input', type=Path, help='Входной файл')
    import_zip.add_argument('--cards-dir', type=Path, default=Path('./cards'), help='Директория карточек')
    import_zip.add_argument('--overwrite', action='store_true', help='Перезаписать существующие')

    # Импорт из директории
    import_dir = subparsers.add_parser('import-dir', help='Импорт из директории')
    import_dir.add_argument('input', type=Path, help='Входная директория')
    import_dir.add_argument('--cards-dir', type=Path, default=Path('./cards'), help='Директория карточек')
    import_dir.add_argument('--overwrite', action='store_true', help='Перезаписать существующие')
    import_dir.add_argument('--no-recursive', action='store_true', help='Не искать в поддиректориях')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Инициализация
    manager = CardManager(cards_dir=args.cards_dir)

    # Выполнение команды
    if args.command == 'export-json':
        exporter = CardExporter(manager)
        count = exporter.export_to_json(args.output, pretty=not args.compact)
        print(f"✅ Экспортировано {count} карточек в {args.output}")

    elif args.command == 'export-csv':
        exporter = CardExporter(manager)
        count = exporter.export_to_csv(args.output, include_content=args.with_content)
        print(f"✅ Экспортировано {count} карточек в {args.output}")

    elif args.command == 'export-zip':
        exporter = CardExporter(manager)
        count = exporter.export_to_archive(args.output)
        print(f"✅ Экспортировано {count} карточек в {args.output}")

    elif args.command == 'export-stats':
        exporter = CardExporter(manager)
        stats = exporter.export_stats_report(args.output)
        print(f"✅ Статистика сохранена в {args.output}")
        print(f"   Всего карточек: {stats.get('total_cards', 0)}")

    elif args.command == 'import-json':
        importer = CardImporter(manager)
        stats = importer.import_from_json(args.input, overwrite=args.overwrite)
        print(f"✅ Импорт завершён:")
        print(f"   Импортировано: {stats['imported']}")
        print(f"   Пропущено: {stats['skipped']}")
        print(f"   Ошибок: {stats['errors']}")

    elif args.command == 'import-zip':
        importer = CardImporter(manager)
        stats = importer.import_from_archive(args.input, overwrite=args.overwrite)
        print(f"✅ Импорт завершён:")
        print(f"   Импортировано: {stats['imported']}")
        print(f"   Пропущено: {stats['skipped']}")
        print(f"   Ошибок: {stats['errors']}")

    elif args.command == 'import-dir':
        importer = CardImporter(manager)
        stats = importer.import_from_directory(
            args.input,
            overwrite=args.overwrite,
            recursive=not args.no_recursive
        )
        print(f"✅ Импорт завершён:")
        print(f"   Импортировано: {stats['imported']}")
        print(f"   Пропущено: {stats['skipped']}")
        print(f"   Ошибок: {stats['errors']}")


if __name__ == '__main__':
    main()
