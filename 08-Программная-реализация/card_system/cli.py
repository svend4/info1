#!/usr/bin/env python3
"""
CLI-интерфейс для управления карточной системой

Реализует команды для создания, просмотра, редактирования и удаления карточек.
Соответствует спецификациям уровня α=-1 (технические спецификации).
"""

import argparse
import sys
from pathlib import Path
from typing import Optional, List
import datetime

from card import (
    Card, CardType, CardStatus, CardPriority,
    TaskCard, MedicineCard, RecipeCard,
    ShoppingCard, ContactCard, AppointmentCard, NoteCard
)
from card_manager import CardManager


class CardCLI:
    """CLI-интерфейс для работы с карточками"""

    def __init__(self, cards_dir: str = "./cards"):
        self.manager = CardManager(cards_dir)
        self.cards_dir = cards_dir

    def create_card(self, args) -> None:
        """Создание новой карточки"""
        card_type = CardType(args.type)

        # Базовые параметры для всех карточек
        base_params = {
            'id': Card.generate_id(),
            'type': card_type,
            'title': args.title,
            'created': datetime.datetime.now(),
            'modified': datetime.datetime.now(),
            'status': CardStatus(args.status) if args.status else CardStatus.PENDING,
            'priority': CardPriority(args.priority) if args.priority else CardPriority.MEDIUM,
            'tags': args.tags.split(',') if args.tags else [],
            'content': args.content or ""
        }

        # Создание карточки нужного типа
        if card_type == CardType.TASK:
            card = TaskCard(**base_params)
        elif card_type == CardType.MEDICINE:
            card = MedicineCard(**base_params)
        elif card_type == CardType.RECIPE:
            card = RecipeCard(**base_params)
        elif card_type == CardType.SHOPPING:
            card = ShoppingCard(**base_params)
        elif card_type == CardType.CONTACT:
            card = ContactCard(**base_params)
        elif card_type == CardType.APPOINTMENT:
            card = AppointmentCard(**base_params)
        elif card_type == CardType.NOTE:
            card = NoteCard(**base_params)
        else:
            print(f"❌ Неизвестный тип карточки: {card_type}")
            sys.exit(1)

        # Сохранение
        self.manager.save(card)
        print(f"✅ Карточка создана: {card.id}")
        print(f"📝 Тип: {card.type.value}")
        print(f"📌 Заголовок: {card.title}")

    def list_cards(self, args) -> None:
        """Вывод списка карточек"""
        card_type = CardType(args.type) if args.type else None
        status = CardStatus(args.status) if args.status else None
        tags = args.tags.split(',') if args.tags else None

        cards = self.manager.search(
            card_type=card_type,
            status=status,
            tags=tags,
            limit=args.limit or 100
        )

        if not cards:
            print("📭 Карточек не найдено")
            return

        print(f"\n📚 Найдено карточек: {len(cards)}\n")
        print("─" * 80)

        for card in cards:
            self._print_card_summary(card)
            print("─" * 80)

    def show_card(self, args) -> None:
        """Показать детали карточки"""
        card = self.manager.load(args.id)

        if not card:
            print(f"❌ Карточка {args.id} не найдена")
            sys.exit(1)

        self._print_card_details(card)

        # Показать связанные карточки
        if card.linked_cards:
            print("\n🔗 Связанные карточки:")
            for linked_id in card.linked_cards:
                linked = self.manager.load(linked_id)
                if linked:
                    print(f"  • {linked_id}: {linked.title}")

    def update_card(self, args) -> None:
        """Обновление карточки"""
        card = self.manager.load(args.id)

        if not card:
            print(f"❌ Карточка {args.id} не найдена")
            sys.exit(1)

        # Обновление полей
        if args.title:
            card.title = args.title
        if args.status:
            card.status = CardStatus(args.status)
        if args.priority:
            card.priority = CardPriority(args.priority)
        if args.content:
            card.content = args.content
        if args.tags:
            card.tags = args.tags.split(',')

        card.modified = datetime.datetime.now()

        self.manager.save(card)
        print(f"✅ Карточка {args.id} обновлена")

    def delete_card(self, args) -> None:
        """Удаление карточки"""
        if not args.force:
            confirm = input(f"⚠️  Удалить карточку {args.id}? (yes/no): ")
            if confirm.lower() not in ['yes', 'y', 'да', 'д']:
                print("❌ Отменено")
                return

        success = self.manager.delete(args.id)

        if success:
            print(f"✅ Карточка {args.id} удалена")
        else:
            print(f"❌ Ошибка при удалении карточки {args.id}")

    def search_cards(self, args) -> None:
        """Поиск карточек по запросу"""
        cards = self.manager.search(
            query=args.query,
            card_type=CardType(args.type) if args.type else None,
            tags=args.tags.split(',') if args.tags else None,
            limit=args.limit or 50
        )

        if not cards:
            print(f"📭 По запросу '{args.query}' ничего не найдено")
            return

        print(f"\n🔍 Найдено: {len(cards)} карточек\n")
        print("─" * 80)

        for card in cards:
            self._print_card_summary(card)
            print("─" * 80)

    def link_cards(self, args) -> None:
        """Создать связь между карточками"""
        card1 = self.manager.load(args.id1)
        card2 = self.manager.load(args.id2)

        if not card1:
            print(f"❌ Карточка {args.id1} не найдена")
            sys.exit(1)
        if not card2:
            print(f"❌ Карточка {args.id2} не найдена")
            sys.exit(1)

        # Двунаправленная связь
        if args.id2 not in card1.linked_cards:
            card1.linked_cards.append(args.id2)
            card1.modified = datetime.datetime.now()
            self.manager.save(card1)

        if not args.one_way:
            if args.id1 not in card2.linked_cards:
                card2.linked_cards.append(args.id1)
                card2.modified = datetime.datetime.now()
                self.manager.save(card2)

        print(f"✅ Связь создана: {args.id1} ↔ {args.id2}")

    def stats(self, args) -> None:
        """Показать статистику по карточкам"""
        all_cards = self.manager.search(limit=10000)

        print("\n📊 Статистика карточной системы\n")
        print(f"📚 Всего карточек: {len(all_cards)}")

        # По типам
        print("\n📋 По типам:")
        by_type = {}
        for card in all_cards:
            by_type[card.type.value] = by_type.get(card.type.value, 0) + 1
        for card_type, count in sorted(by_type.items()):
            print(f"  • {card_type}: {count}")

        # По статусу
        print("\n🎯 По статусу:")
        by_status = {}
        for card in all_cards:
            by_status[card.status.value] = by_status.get(card.status.value, 0) + 1
        for status, count in sorted(by_status.items()):
            print(f"  • {status}: {count}")

        # По приоритету
        print("\n⚡ По приоритету:")
        by_priority = {}
        for card in all_cards:
            by_priority[card.priority.value] = by_priority.get(card.priority.value, 0) + 1
        for priority, count in sorted(by_priority.items()):
            print(f"  • {priority}: {count}")

        # Связи
        total_links = sum(len(card.linked_cards) for card in all_cards)
        print(f"\n🔗 Всего связей: {total_links}")

        # Теги
        all_tags = set()
        for card in all_cards:
            all_tags.update(card.tags)
        print(f"\n🏷️  Уникальных тегов: {len(all_tags)}")
        if all_tags:
            print(f"  Примеры: {', '.join(list(all_tags)[:10])}")

    def _print_card_summary(self, card: Card) -> None:
        """Краткий вывод информации о карточке"""
        status_icon = {
            'pending': '⏳',
            'in_progress': '🔄',
            'completed': '✅',
            'cancelled': '❌',
            'archived': '📦'
        }.get(card.status.value, '📝')

        priority_icon = {
            'low': '🟢',
            'medium': '🟡',
            'high': '🔴',
            'urgent': '🚨'
        }.get(card.priority.value, '⚪')

        print(f"{status_icon} {priority_icon} [{card.type.value}] {card.title}")
        print(f"   ID: {card.id}")
        print(f"   Создано: {card.created.strftime('%Y-%m-%d %H:%M')}")
        if card.tags:
            print(f"   Теги: {', '.join(card.tags)}")

    def _print_card_details(self, card: Card) -> None:
        """Подробный вывод информации о карточке"""
        print("\n" + "=" * 80)
        print(f"📝 {card.title}")
        print("=" * 80)
        print(f"ID: {card.id}")
        print(f"Тип: {card.type.value}")
        print(f"Статус: {card.status.value}")
        print(f"Приоритет: {card.priority.value}")
        print(f"Создано: {card.created.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Изменено: {card.modified.strftime('%Y-%m-%d %H:%M:%S')}")

        if card.tags:
            print(f"Теги: {', '.join(card.tags)}")

        if card.content:
            print("\n" + "─" * 80)
            print(card.content)
            print("─" * 80)

        # Специфичные поля для разных типов
        if isinstance(card, TaskCard):
            if card.due_date:
                print(f"Срок: {card.due_date}")
            if card.assignee:
                print(f"Ответственный: {card.assignee}")

        elif isinstance(card, ContactCard):
            if card.person.get('full_name'):
                print(f"Имя: {card.person['full_name']}")
            if card.contact_info.get('phone_mobile'):
                print(f"Телефон: {card.contact_info['phone_mobile']}")


def main():
    """Главная функция CLI"""
    parser = argparse.ArgumentParser(
        description='Система управления карточками для домашнего использования',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  # Создать задачу
  %(prog)s create -t task --title "Купить продукты" --priority high

  # Показать все карточки
  %(prog)s list

  # Поиск карточек
  %(prog)s search "лекарство"

  # Показать детали
  %(prog)s show card_20260123_120000_abc1

  # Статистика
  %(prog)s stats
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Доступные команды')

    # Команда: create
    create_parser = subparsers.add_parser('create', help='Создать новую карточку')
    create_parser.add_argument('-t', '--type', required=True,
                              choices=['task', 'medicine', 'recipe', 'shopping',
                                      'contact', 'appointment', 'note'],
                              help='Тип карточки')
    create_parser.add_argument('--title', required=True, help='Заголовок')
    create_parser.add_argument('--status', choices=['pending', 'in_progress', 'completed',
                                                     'cancelled', 'archived'],
                              help='Статус')
    create_parser.add_argument('--priority', choices=['low', 'medium', 'high', 'urgent'],
                              help='Приоритет')
    create_parser.add_argument('--tags', help='Теги через запятую')
    create_parser.add_argument('--content', help='Содержание карточки')

    # Команда: list
    list_parser = subparsers.add_parser('list', help='Показать список карточек')
    list_parser.add_argument('-t', '--type',
                            choices=['task', 'medicine', 'recipe', 'shopping',
                                    'contact', 'appointment', 'note'],
                            help='Фильтр по типу')
    list_parser.add_argument('--status', choices=['pending', 'in_progress', 'completed',
                                                   'cancelled', 'archived'],
                            help='Фильтр по статусу')
    list_parser.add_argument('--tags', help='Фильтр по тегам (через запятую)')
    list_parser.add_argument('--limit', type=int, help='Максимум карточек')

    # Команда: show
    show_parser = subparsers.add_parser('show', help='Показать детали карточки')
    show_parser.add_argument('id', help='ID карточки')

    # Команда: update
    update_parser = subparsers.add_parser('update', help='Обновить карточку')
    update_parser.add_argument('id', help='ID карточки')
    update_parser.add_argument('--title', help='Новый заголовок')
    update_parser.add_argument('--status', choices=['pending', 'in_progress', 'completed',
                                                     'cancelled', 'archived'],
                              help='Новый статус')
    update_parser.add_argument('--priority', choices=['low', 'medium', 'high', 'urgent'],
                              help='Новый приоритет')
    update_parser.add_argument('--tags', help='Новые теги (через запятую)')
    update_parser.add_argument('--content', help='Новое содержание')

    # Команда: delete
    delete_parser = subparsers.add_parser('delete', help='Удалить карточку')
    delete_parser.add_argument('id', help='ID карточки')
    delete_parser.add_argument('-f', '--force', action='store_true',
                              help='Без подтверждения')

    # Команда: search
    search_parser = subparsers.add_parser('search', help='Поиск карточек')
    search_parser.add_argument('query', help='Поисковый запрос')
    search_parser.add_argument('-t', '--type',
                              choices=['task', 'medicine', 'recipe', 'shopping',
                                      'contact', 'appointment', 'note'],
                              help='Фильтр по типу')
    search_parser.add_argument('--tags', help='Фильтр по тегам (через запятую)')
    search_parser.add_argument('--limit', type=int, help='Максимум результатов')

    # Команда: link
    link_parser = subparsers.add_parser('link', help='Связать карточки')
    link_parser.add_argument('id1', help='ID первой карточки')
    link_parser.add_argument('id2', help='ID второй карточки')
    link_parser.add_argument('--one-way', action='store_true',
                            help='Односторонняя связь')

    # Команда: stats
    stats_parser = subparsers.add_parser('stats', help='Показать статистику')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    # Инициализация CLI
    cli = CardCLI()

    # Выполнение команды
    command_map = {
        'create': cli.create_card,
        'list': cli.list_cards,
        'show': cli.show_card,
        'update': cli.update_card,
        'delete': cli.delete_card,
        'search': cli.search_cards,
        'link': cli.link_cards,
        'stats': cli.stats
    }

    command_func = command_map.get(args.command)
    if command_func:
        try:
            command_func(args)
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            sys.exit(1)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()
