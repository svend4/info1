#!/usr/bin/env python3
"""
Утилита резервного копирования и восстановления данных карточной системы

Позволяет создавать резервные копии всех карточек и восстанавливать их.
Поддерживает форматы JSON и ZIP.

α-уровень: -4 (исполняемый код)
"""

import sys
import os
import json
import shutil
import zipfile
import argparse
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

# Добавляем путь к card_system в PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent))

from card_manager import CardManager
from card import Card


class BackupManager:
    """Менеджер резервного копирования"""

    def __init__(self, data_dir: str = None):
        """
        Инициализация менеджера

        Args:
            data_dir: Директория с данными карточек
        """
        if data_dir is None:
            data_dir = str(Path.home() / '.card_system' / 'cards')

        self.data_dir = Path(data_dir)
        self.manager = CardManager(str(self.data_dir))

    def create_backup(self, backup_path: str, format: str = 'json', compress: bool = True) -> str:
        """
        Создать резервную копию всех карточек

        Args:
            backup_path: Путь для сохранения резервной копии
            format: Формат (json или zip)
            compress: Сжимать ли данные

        Returns:
            Путь к созданной резервной копии
        """
        print(f"📦 Создание резервной копии...")
        print(f"Источник: {self.data_dir}")

        # Получить все карточки
        all_cards = self.manager.list_cards()

        if not all_cards:
            print("⚠️  Нет карточек для резервного копирования")
            return None

        print(f"Найдено карточек: {len(all_cards)}")

        # Подготовить данные для резервной копии
        backup_data = {
            'metadata': {
                'created_at': datetime.now().isoformat(),
                'version': '1.0',
                'total_cards': len(all_cards),
                'source_dir': str(self.data_dir)
            },
            'cards': [card.to_dict() for card in all_cards]
        }

        # Определить финальный путь
        if not backup_path:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = f'backup_{timestamp}.json'

        backup_path = Path(backup_path)

        # Создать директорию, если не существует
        backup_path.parent.mkdir(parents=True, exist_ok=True)

        if format == 'zip' or compress:
            # Создать ZIP архив
            self._create_zip_backup(backup_data, backup_path)
        else:
            # Создать JSON файл
            self._create_json_backup(backup_data, backup_path)

        file_size = backup_path.stat().st_size
        print(f"✅ Резервная копия создана: {backup_path}")
        print(f"Размер: {file_size:,} байт ({file_size / 1024:.1f} KB)")

        return str(backup_path)

    def _create_json_backup(self, data: Dict, path: Path):
        """Создать JSON резервную копию"""
        if not str(path).endswith('.json'):
            path = path.with_suffix('.json')

        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _create_zip_backup(self, data: Dict, path: Path):
        """Создать ZIP резервную копию"""
        if not str(path).endswith('.zip'):
            path = path.with_suffix('.zip')

        # Создать временный JSON файл
        temp_json = path.with_suffix('.temp.json')
        with open(temp_json, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        # Создать ZIP архив
        with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(temp_json, 'backup.json')

        # Удалить временный файл
        temp_json.unlink()

    def restore_backup(self, backup_path: str, merge: bool = False, dry_run: bool = False) -> int:
        """
        Восстановить данные из резервной копии

        Args:
            backup_path: Путь к резервной копии
            merge: Объединить с существующими данными (иначе заменить)
            dry_run: Только показать что будет восстановлено

        Returns:
            Количество восстановленных карточек
        """
        backup_path = Path(backup_path)

        if not backup_path.exists():
            print(f"❌ Файл резервной копии не найден: {backup_path}")
            return 0

        print(f"📂 Восстановление из: {backup_path}")

        # Загрузить данные
        if str(backup_path).endswith('.zip'):
            data = self._load_zip_backup(backup_path)
        else:
            data = self._load_json_backup(backup_path)

        if not data:
            print("❌ Не удалось загрузить резервную копию")
            return 0

        # Показать информацию о резервной копии
        metadata = data.get('metadata', {})
        cards_data = data.get('cards', [])

        print(f"\nИнформация о резервной копии:")
        print(f"  Создана: {metadata.get('created_at', 'Неизвестно')}")
        print(f"  Версия: {metadata.get('version', 'Неизвестно')}")
        print(f"  Карточек: {metadata.get('total_cards', len(cards_data))}")
        print()

        if dry_run:
            print("🔍 Режим dry-run: показываю что будет восстановлено")
            self._show_restore_preview(cards_data)
            return 0

        # Подтверждение
        if not merge and self.manager.list_cards():
            print(f"⚠️  ВНИМАНИЕ!")
            print(f"Текущих карточек в системе: {len(self.manager.list_cards())}")
            print(f"Они будут УДАЛЕНЫ и заменены на {len(cards_data)} из резервной копии")
            response = input("\nПродолжить? (yes/no): ")
            if response.lower() not in ['yes', 'y', 'да']:
                print("Отменено")
                return 0

        # Восстановление
        restored_count = 0

        if not merge:
            # Очистить существующие данные
            print("🗑️  Очистка текущих данных...")
            self._clear_current_data()

        print(f"📥 Восстановление карточек...")
        for card_dict in cards_data:
            try:
                card = Card.from_dict(card_dict)
                self.manager.add_card(card)
                restored_count += 1
                print(f"  ✓ {card.title} ({card.type})")
            except Exception as e:
                print(f"  ✗ Ошибка при восстановлении: {e}")

        print(f"\n✅ Восстановлено карточек: {restored_count}/{len(cards_data)}")

        return restored_count

    def _load_json_backup(self, path: Path) -> Optional[Dict]:
        """Загрузить JSON резервную копию"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Ошибка чтения JSON: {e}")
            return None

    def _load_zip_backup(self, path: Path) -> Optional[Dict]:
        """Загрузить ZIP резервную копию"""
        try:
            with zipfile.ZipFile(path, 'r') as zipf:
                with zipf.open('backup.json') as f:
                    return json.load(f)
        except Exception as e:
            print(f"❌ Ошибка чтения ZIP: {e}")
            return None

    def _clear_current_data(self):
        """Очистить текущие данные"""
        for card in self.manager.list_cards():
            self.manager.delete_card(card.id)

    def _show_restore_preview(self, cards_data: List[Dict]):
        """Показать предварительный просмотр восстановления"""
        # Группировка по типам
        by_type = {}
        for card_dict in cards_data:
            card_type = card_dict.get('type', 'unknown')
            if card_type not in by_type:
                by_type[card_type] = []
            by_type[card_type].append(card_dict)

        print("\nБудет восстановлено:")
        for card_type, cards in sorted(by_type.items()):
            print(f"  {card_type}: {len(cards)} карточек")
            for card in cards[:3]:  # Показать первые 3
                print(f"    - {card.get('title', 'Без названия')}")
            if len(cards) > 3:
                print(f"    ... и еще {len(cards) - 3}")
        print()

    def list_backups(self, backup_dir: str = '.') -> List[Path]:
        """
        Показать список доступных резервных копий

        Args:
            backup_dir: Директория с резервными копиями

        Returns:
            Список путей к резервным копиям
        """
        backup_dir = Path(backup_dir)

        backups = []
        for ext in ['*.json', '*.zip']:
            backups.extend(backup_dir.glob(f'backup_{ext}'))

        if not backups:
            print("📂 Резервных копий не найдено")
            return []

        print(f"📂 Найдено резервных копий: {len(backups)}")
        print()

        for backup_path in sorted(backups, reverse=True):
            size = backup_path.stat().st_size
            mtime = datetime.fromtimestamp(backup_path.stat().st_mtime)
            print(f"  • {backup_path.name}")
            print(f"    Размер: {size:,} байт ({size / 1024:.1f} KB)")
            print(f"    Изменён: {mtime.strftime('%Y-%m-%d %H:%M:%S')}")
            print()

        return backups


def main():
    """Главная функция CLI"""
    parser = argparse.ArgumentParser(
        description='Утилита резервного копирования карточной системы',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:

  # Создать резервную копию
  python backup_restore.py backup

  # Создать резервную копию в определенный файл
  python backup_restore.py backup --output my_backup.zip

  # Восстановить из резервной копии (заменить данные)
  python backup_restore.py restore backup_20260124_120000.zip

  # Восстановить и объединить с текущими данными
  python backup_restore.py restore backup.zip --merge

  # Показать что будет восстановлено (без изменений)
  python backup_restore.py restore backup.zip --dry-run

  # Показать список резервных копий
  python backup_restore.py list
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Команда')

    # Команда backup
    backup_parser = subparsers.add_parser('backup', help='Создать резервную копию')
    backup_parser.add_argument('-o', '--output', help='Путь для сохранения', default=None)
    backup_parser.add_argument('-f', '--format', choices=['json', 'zip'], default='zip', help='Формат')
    backup_parser.add_argument('--no-compress', action='store_true', help='Не сжимать')
    backup_parser.add_argument('-d', '--data-dir', help='Директория с данными', default=None)

    # Команда restore
    restore_parser = subparsers.add_parser('restore', help='Восстановить из резервной копии')
    restore_parser.add_argument('backup_file', help='Файл резервной копии')
    restore_parser.add_argument('--merge', action='store_true', help='Объединить с текущими данными')
    restore_parser.add_argument('--dry-run', action='store_true', help='Показать изменения без применения')
    restore_parser.add_argument('-d', '--data-dir', help='Директория с данными', default=None)

    # Команда list
    list_parser = subparsers.add_parser('list', help='Показать список резервных копий')
    list_parser.add_argument('-d', '--dir', help='Директория для поиска', default='.')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    try:
        if args.command == 'backup':
            manager = BackupManager(args.data_dir)
            compress = not args.no_compress
            manager.create_backup(args.output, args.format, compress)

        elif args.command == 'restore':
            manager = BackupManager(args.data_dir)
            manager.restore_backup(args.backup_file, args.merge, args.dry_run)

        elif args.command == 'list':
            manager = BackupManager()
            manager.list_backups(args.dir)

    except KeyboardInterrupt:
        print("\n\n❌ Прервано пользователем")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
