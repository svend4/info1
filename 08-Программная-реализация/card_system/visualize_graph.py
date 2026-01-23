#!/usr/bin/env python3
"""
Визуализация графа связей между карточками

Генерирует ASCII-представление графа связей карточек.
Уровень абстракции: α=-4 (исполняемый код)
"""

import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict, deque

from card import Card, CardType
from card_manager import CardManager


class GraphVisualizer:
    """Визуализация графа связей карточек"""

    def __init__(self, manager: CardManager):
        self.manager = manager
        self.graph = manager.get_connection_graph()

    def visualize_ascii(self, start_id: str = None, max_depth: int = 3) -> str:
        """
        ASCII визуализация графа связей

        Args:
            start_id: ID начальной карточки (если None, показать все)
            max_depth: Максимальная глубина обхода
        """
        if start_id:
            return self._visualize_tree(start_id, max_depth)
        else:
            return self._visualize_all_components()

    def _visualize_tree(self, start_id: str, max_depth: int) -> str:
        """Визуализация дерева связей от одной карточки"""
        card = self.manager.load(start_id)
        if not card:
            return f"❌ Карточка {start_id} не найдена"

        lines = []
        lines.append(f"\n🌳 Граф связей для карточки: {card.title}")
        lines.append(f"   ID: {start_id}")
        lines.append(f"   Тип: {card.type.value}")
        lines.append("=" * 80)

        visited = set()
        self._build_tree_recursive(start_id, lines, visited, depth=0, max_depth=max_depth)

        return "\n".join(lines)

    def _build_tree_recursive(
        self,
        card_id: str,
        lines: List[str],
        visited: Set[str],
        depth: int = 0,
        max_depth: int = 3,
        prefix: str = "",
        is_last: bool = True
    ):
        """Рекурсивное построение дерева"""
        if depth > max_depth or card_id in visited:
            return

        visited.add(card_id)
        card = self.manager.load(card_id)
        if not card:
            return

        # Символы для рисования дерева
        if depth == 0:
            connector = ""
            new_prefix = ""
        else:
            connector = "└── " if is_last else "├── "
            new_prefix = prefix + ("    " if is_last else "│   ")

        # Иконка по типу
        icon = self._get_type_icon(card.type)

        # Вывод узла
        lines.append(f"{prefix}{connector}{icon} [{card.type.value}] {card.title}")

        # Дополнительная информация
        if card.tags:
            tag_prefix = prefix + ("    " if is_last else "│   ")
            lines.append(f"{tag_prefix}🏷️  {', '.join(card.tags[:3])}")

        # Рекурсия для связанных карточек
        linked = card.linked_cards
        for i, linked_id in enumerate(linked):
            if linked_id not in visited:
                is_last_child = (i == len(linked) - 1)
                self._build_tree_recursive(
                    linked_id, lines, visited,
                    depth + 1, max_depth,
                    new_prefix, is_last_child
                )

    def _visualize_all_components(self) -> str:
        """Визуализация всех компонент графа"""
        all_cards = self.manager.search(limit=1000)

        lines = []
        lines.append("\n📊 Полный граф связей всех карточек")
        lines.append("=" * 80)

        # Построить граф смежности
        adjacency = defaultdict(set)
        all_ids = set()

        for card in all_cards:
            all_ids.add(card.id)
            for linked_id in card.linked_cards:
                adjacency[card.id].add(linked_id)
                adjacency[linked_id].add(card.id)  # Двунаправленная связь

        # Найти компоненты связности
        components = self._find_components(all_ids, adjacency)

        lines.append(f"\n📈 Статистика графа:")
        lines.append(f"   Всего карточек: {len(all_ids)}")
        lines.append(f"   Компонент связности: {len(components)}")
        lines.append(f"   Изолированных карточек: {sum(1 for c in components if len(c) == 1)}")

        # Вывести компоненты
        lines.append(f"\n🔗 Компоненты связности:\n")

        for i, component in enumerate(sorted(components, key=len, reverse=True), 1):
            if len(component) == 1:
                continue  # Пропустить изолированные

            lines.append(f"Компонента #{i} ({len(component)} карточек):")
            lines.append("─" * 80)

            # Группировка по типам внутри компоненты
            by_type = defaultdict(list)
            for card_id in component:
                card = self.manager.load(card_id)
                if card:
                    by_type[card.type.value].append(card)

            for card_type, cards in sorted(by_type.items()):
                icon = self._get_type_icon(CardType(card_type))
                lines.append(f"  {icon} {card_type}: {len(cards)}")
                for card in cards[:3]:  # Показать первые 3
                    links_count = len(card.linked_cards)
                    lines.append(f"     • {card.title} (связей: {links_count})")
                if len(cards) > 3:
                    lines.append(f"     ... и ещё {len(cards) - 3}")

            lines.append("")

        return "\n".join(lines)

    def _find_components(
        self,
        all_ids: Set[str],
        adjacency: Dict[str, Set[str]]
    ) -> List[Set[str]]:
        """Найти компоненты связности в графе (BFS)"""
        visited = set()
        components = []

        for node_id in all_ids:
            if node_id in visited:
                continue

            # BFS для новой компоненты
            component = set()
            queue = deque([node_id])

            while queue:
                current = queue.popleft()
                if current in visited:
                    continue

                visited.add(current)
                component.add(current)

                # Добавить соседей
                for neighbor in adjacency.get(current, set()):
                    if neighbor not in visited:
                        queue.append(neighbor)

            components.append(component)

        return components

    def visualize_matrix(self, card_ids: List[str] = None) -> str:
        """Визуализация матрицы смежности"""
        if card_ids is None:
            all_cards = self.manager.search(limit=100)
            card_ids = [c.id for c in all_cards[:20]]  # Максимум 20 для читаемости

        if not card_ids:
            return "Нет карточек для визуализации"

        cards = {cid: self.manager.load(cid) for cid in card_ids}
        cards = {k: v for k, v in cards.items() if v}  # Удалить None

        lines = []
        lines.append("\n📊 Матрица смежности (связи между карточками)")
        lines.append("=" * 80)
        lines.append(f"Показано: {len(cards)} карточек\n")

        # Заголовок
        id_to_idx = {cid: i for i, cid in enumerate(cards.keys())}

        # Вывести легенду
        lines.append("Легенда:")
        for i, (cid, card) in enumerate(cards.items()):
            icon = self._get_type_icon(card.type)
            short_title = card.title[:30] + "..." if len(card.title) > 30 else card.title
            lines.append(f"  {i:2d}. {icon} {short_title}")

        lines.append("\nМатрица (1 = есть связь, . = нет связи):")
        lines.append("    " + "".join(f"{i:2d}" for i in range(len(cards))))
        lines.append("    " + "─" * (len(cards) * 2))

        # Построить матрицу
        for i, (cid1, card1) in enumerate(cards.items()):
            row = f"{i:2d} │"
            for j, cid2 in enumerate(cards.keys()):
                if cid2 in card1.linked_cards:
                    row += " 1"
                elif cid1 == cid2:
                    row += " ■"  # Диагональ
                else:
                    row += " ·"
            lines.append(row)

        return "\n".join(lines)

    def analyze_connections(self) -> str:
        """Анализ связей в графе"""
        all_cards = self.manager.search(limit=1000)

        lines = []
        lines.append("\n🔍 Анализ связей в графе")
        lines.append("=" * 80)

        # Подсчёт связей
        connection_counts = []
        for card in all_cards:
            connection_counts.append((card, len(card.linked_cards)))

        # Топ по количеству связей
        lines.append("\n📊 Топ-10 карточек по количеству связей:\n")
        for card, count in sorted(connection_counts, key=lambda x: x[1], reverse=True)[:10]:
            icon = self._get_type_icon(card.type)
            lines.append(f"  {icon} {card.title[:50]:50} — {count} связей")

        # Карточки без связей
        isolated = [card for card, count in connection_counts if count == 0]
        lines.append(f"\n🔴 Изолированных карточек (без связей): {len(isolated)}")
        if isolated:
            lines.append("   Примеры:")
            for card in isolated[:5]:
                icon = self._get_type_icon(card.type)
                lines.append(f"   • {icon} {card.title}")

        # Статистика по типам
        lines.append("\n📈 Связи по типам карточек:\n")
        by_type = defaultdict(list)
        for card, count in connection_counts:
            by_type[card.type.value].append(count)

        for card_type, counts in sorted(by_type.items()):
            if counts:
                avg = sum(counts) / len(counts)
                max_conn = max(counts)
                icon = self._get_type_icon(CardType(card_type))
                lines.append(f"  {icon} {card_type:12} — среднее: {avg:.1f}, максимум: {max_conn}")

        # Наиболее связанные пары типов
        lines.append("\n🔗 Наиболее связанные типы карточек:\n")
        type_connections = defaultdict(int)

        for card in all_cards:
            for linked_id in card.linked_cards:
                linked = self.manager.load(linked_id)
                if linked:
                    pair = tuple(sorted([card.type.value, linked.type.value]))
                    type_connections[pair] += 1

        for (type1, type2), count in sorted(type_connections.items(), key=lambda x: x[1], reverse=True)[:10]:
            icon1 = self._get_type_icon(CardType(type1))
            icon2 = self._get_type_icon(CardType(type2))
            lines.append(f"  {icon1} {type1} ↔ {icon2} {type2}: {count} связей")

        return "\n".join(lines)

    def find_paths(self, start_id: str, end_id: str, max_depth: int = 5) -> str:
        """Найти пути между двумя карточками"""
        start_card = self.manager.load(start_id)
        end_card = self.manager.load(end_id)

        if not start_card or not end_card:
            return "❌ Одна из карточек не найдена"

        lines = []
        lines.append(f"\n🔍 Поиск путей от '{start_card.title}' до '{end_card.title}'")
        lines.append("=" * 80)

        paths = self._bfs_paths(start_id, end_id, max_depth)

        if not paths:
            lines.append(f"\n❌ Пути не найдены (глубина поиска: {max_depth})")
        else:
            lines.append(f"\n✅ Найдено путей: {len(paths)}\n")

            for i, path in enumerate(paths[:5], 1):  # Показать первые 5 путей
                lines.append(f"Путь #{i} (длина: {len(path) - 1}):")

                for j, card_id in enumerate(path):
                    card = self.manager.load(card_id)
                    if card:
                        icon = self._get_type_icon(card.type)
                        indent = "  " * j
                        connector = "└→ " if j > 0 else ""
                        lines.append(f"{indent}{connector}{icon} {card.title}")

                lines.append("")

        return "\n".join(lines)

    def _bfs_paths(self, start_id: str, end_id: str, max_depth: int) -> List[List[str]]:
        """BFS поиск всех путей между карточками"""
        if start_id == end_id:
            return [[start_id]]

        queue = deque([([start_id], {start_id})])
        paths = []

        while queue:
            path, visited = queue.popleft()

            if len(path) > max_depth:
                continue

            current_id = path[-1]
            current_card = self.manager.load(current_id)

            if not current_card:
                continue

            for next_id in current_card.linked_cards:
                if next_id == end_id:
                    paths.append(path + [end_id])
                elif next_id not in visited:
                    new_visited = visited.copy()
                    new_visited.add(next_id)
                    queue.append((path + [next_id], new_visited))

        return paths

    @staticmethod
    def _get_type_icon(card_type: CardType) -> str:
        """Получить иконку для типа карточки"""
        icons = {
            CardType.TASK: "📋",
            CardType.MEDICINE: "💊",
            CardType.RECIPE: "🍳",
            CardType.SHOPPING: "🛒",
            CardType.CONTACT: "👤",
            CardType.APPOINTMENT: "📅",
            CardType.NOTE: "📝"
        }
        return icons.get(card_type, "📄")


def main():
    """Главная функция CLI"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Визуализация графа связей между карточками'
    )

    subparsers = parser.add_subparsers(dest='command', help='Команды визуализации')

    # Команда: tree
    tree_parser = subparsers.add_parser('tree', help='Показать дерево связей от карточки')
    tree_parser.add_argument('card_id', help='ID начальной карточки')
    tree_parser.add_argument('--depth', type=int, default=3, help='Максимальная глубина')

    # Команда: components
    components_parser = subparsers.add_parser('components', help='Показать компоненты связности')

    # Команда: matrix
    matrix_parser = subparsers.add_parser('matrix', help='Показать матрицу смежности')
    matrix_parser.add_argument('--ids', nargs='+', help='ID карточек для матрицы')

    # Команда: analyze
    analyze_parser = subparsers.add_parser('analyze', help='Анализ связей')

    # Команда: path
    path_parser = subparsers.add_parser('path', help='Найти путь между карточками')
    path_parser.add_argument('start_id', help='ID начальной карточки')
    path_parser.add_argument('end_id', help='ID конечной карточки')
    path_parser.add_argument('--depth', type=int, default=5, help='Максимальная глубина поиска')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    # Инициализация
    manager = CardManager()
    visualizer = GraphVisualizer(manager)

    # Выполнение команды
    if args.command == 'tree':
        print(visualizer.visualize_ascii(args.card_id, args.depth))

    elif args.command == 'components':
        print(visualizer.visualize_ascii())

    elif args.command == 'matrix':
        print(visualizer.visualize_matrix(args.ids))

    elif args.command == 'analyze':
        print(visualizer.analyze_connections())

    elif args.command == 'path':
        print(visualizer.find_paths(args.start_id, args.end_id, args.depth))

    else:
        parser.print_help()


if __name__ == '__main__':
    main()
