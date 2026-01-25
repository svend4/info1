#!/usr/bin/env python3
"""
Data Augmentation для расширения training dataset

Автоматическая генерация вариаций существующих примеров для
увеличения размера датасета с 240 до 500+ примеров.

Методы:
1. Synonym replacement (замена синонимами)
2. Random insertion (вставка слов)
3. Random swap (перестановка слов)
4. Back-translation simulation (симуляция обратного перевода)
5. Paraphrasing (перефразирование)
"""

import json
import random
from pathlib import Path
from typing import List, Dict
import re


class DataAugmentor:
    """
    Augmentор для расширения датасета

    Генерирует вариации описаний проектов для увеличения
    размера training dataset.
    """

    # Синонимы для ключевых слов
    SYNONYMS = {
        # Действия
        'создать': ['разработать', 'сделать', 'построить', 'реализовать'],
        'хочу': ['планирую', 'нужно', 'требуется', 'необходимо'],
        'открыть': ['запустить', 'организовать', 'основать'],

        # Типы проектов
        'приложение': ['app', 'программа', 'софт', 'система'],
        'веб': ['web', 'онлайн', 'интернет'],
        'мобильное': ['mobile', 'для телефона', 'смартфон'],
        'платформа': ['система', 'сервис', 'решение'],

        # Бизнес
        'стартап': ['startup', 'новый бизнес', 'компания'],
        'бизнес': ['коммерческий проект', 'предприятие'],
        'компания': ['фирма', 'организация', 'предприятие'],

        # Финансы
        'бюджет': ['финансирование', 'средства', 'капитал'],
        'млн': ['миллион', 'million'],
        'тыс': ['тысяч', 'thousand'],

        # Команда
        'команда': ['team', 'группа', 'коллектив'],
        'человек': ['сотрудник', 'специалист', 'member'],
        'разработчик': ['developer', 'программист', 'engineer'],

        # Технологии
        'технология': ['tech', 'стек', 'инструмент'],
        'использование': ['с применением', 'на базе', 'с помощью'],

        # Сроки
        'срок': ['deadline', 'период', 'timeline'],
        'месяц': ['мес', 'month'],
        'год': ['лет', 'year'],
    }

    # Шаблоны для вставки
    INSERTIONS = {
        'intensity': ['очень', 'максимально', 'крайне', 'весьма'],
        'planning': ['планирую', 'собираюсь', 'хочу'],
        'quality': ['качественный', 'профессиональный', 'надёжный'],
        'modern': ['современный', 'инновационный', 'передовой'],
        'time': ['срочно', 'быстро', 'в ближайшее время'],
    }

    def __init__(self, dataset_path: str = None):
        """
        Args:
            dataset_path: Путь к исходному датасету
        """
        if dataset_path is None:
            dataset_path = Path(__file__).parent / 'training_dataset_full.json'

        self.dataset_path = Path(dataset_path)
        self.dataset = self._load_dataset()

    def _load_dataset(self) -> List[Dict]:
        """Загрузка исходного датасета"""
        with open(self.dataset_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def augment_all(self, target_size: int = 500, augmentations_per_sample: int = 2) -> List[Dict]:
        """
        Расширение всего датасета

        Args:
            target_size: Целевой размер датасета
            augmentations_per_sample: Количество вариаций на пример

        Returns:
            Расширенный датасет
        """
        current_size = len(self.dataset)
        print(f"📊 Current dataset size: {current_size}")
        print(f"🎯 Target size: {target_size}")

        if current_size >= target_size:
            print("✓ Dataset already at target size")
            return self.dataset

        augmented = list(self.dataset)  # Copy original
        needed = target_size - current_size

        print(f"📈 Generating {needed} augmented examples...")

        generated = 0
        while generated < needed:
            # Выбираем случайный пример
            sample = random.choice(self.dataset)

            # Генерируем вариацию
            aug_sample = self.augment_sample(sample)

            # Проверяем уникальность
            if not self._is_duplicate(aug_sample['description'], augmented):
                augmented.append(aug_sample)
                generated += 1

                if generated % 50 == 0:
                    print(f"  Generated {generated}/{needed}...")

        print(f"✅ Augmentation complete: {len(augmented)} total examples")
        return augmented

    def augment_sample(self, sample: Dict) -> Dict:
        """
        Генерация одной вариации примера

        Args:
            sample: Исходный пример

        Returns:
            Augmented пример
        """
        description = sample['description']

        # Выбираем случайную технику аугментации
        technique = random.choice([
            'synonym_replacement',
            'random_insertion',
            'random_swap',
            'paraphrase'
        ])

        if technique == 'synonym_replacement':
            new_desc = self._synonym_replacement(description)
        elif technique == 'random_insertion':
            new_desc = self._random_insertion(description)
        elif technique == 'random_swap':
            new_desc = self._random_swap(description)
        else:  # paraphrase
            new_desc = self._paraphrase(description)

        # Создаем новый пример с тем же типом
        return {
            'id': f"aug_{sample['id']}_{random.randint(1000, 9999)}",
            'description': new_desc,
            'primary_type': sample['primary_type'],
            'secondary_types': sample.get('secondary_types', []),
            'features': sample.get('features', {}),
            'augmented': True,
            'source_id': sample['id']
        }

    def _synonym_replacement(self, text: str, n: int = 2) -> str:
        """Замена n слов синонимами"""
        words = text.split()

        # Находим слова для замены
        replaceable = []
        for i, word in enumerate(words):
            word_lower = word.lower()
            if word_lower in self.SYNONYMS:
                replaceable.append(i)

        if not replaceable:
            return text

        # Выбираем случайные слова для замены
        to_replace = random.sample(replaceable, min(n, len(replaceable)))

        for idx in to_replace:
            word_lower = words[idx].lower()
            synonyms = self.SYNONYMS[word_lower]
            words[idx] = random.choice(synonyms)

        return ' '.join(words)

    def _random_insertion(self, text: str, n: int = 1) -> str:
        """Вставка n случайных слов"""
        words = text.split()

        for _ in range(n):
            # Выбираем категорию и слово
            category = random.choice(list(self.INSERTIONS.keys()))
            word = random.choice(self.INSERTIONS[category])

            # Вставляем в случайную позицию
            insert_pos = random.randint(0, len(words))
            words.insert(insert_pos, word)

        return ' '.join(words)

    def _random_swap(self, text: str, n: int = 2) -> str:
        """Перестановка n пар слов"""
        words = text.split()

        if len(words) < 2:
            return text

        for _ in range(n):
            # Выбираем две случайные позиции
            idx1 = random.randint(0, len(words) - 1)
            idx2 = random.randint(0, len(words) - 1)

            # Меняем местами
            words[idx1], words[idx2] = words[idx2], words[idx1]

        return ' '.join(words)

    def _paraphrase(self, text: str) -> str:
        """Перефразирование через структурные изменения"""
        # Паттерны перефразирования
        patterns = [
            # "Хочу создать X" -> "Планирую разработать X"
            (r'Хочу создать', lambda: random.choice(['Планирую разработать', 'Нужно сделать', 'Требуется построить'])),

            # "на React" -> "с использованием React"
            (r'на (React|Vue|Angular|Django|Flask)', lambda m: f"с использованием {m.group(1)}"),

            # "бюджет X" -> "финансирование X"
            (r'бюджет', lambda: random.choice(['финансирование', 'капитал', 'средства'])),

            # "команда 8" -> "8 человек в команде"
            (r'команда (\d+)', lambda m: f"{m.group(1)} человек в команде"),
        ]

        result = text
        for pattern, replacement in patterns:
            if random.random() < 0.5:  # 50% шанс применить
                result = re.sub(pattern, replacement() if callable(replacement) else replacement, result)

        return result

    def _is_duplicate(self, description: str, dataset: List[Dict]) -> bool:
        """Проверка на дубликаты"""
        description_lower = description.lower()
        for item in dataset:
            if item['description'].lower() == description_lower:
                return True
        return False

    def save_augmented(self, augmented_data: List[Dict], output_path: str = None):
        """Сохранение расширенного датасета"""
        if output_path is None:
            output_path = Path(__file__).parent / 'training_dataset_augmented.json'

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(augmented_data, f, ensure_ascii=False, indent=2)

        print(f"💾 Saved to {output_path}")

    def get_statistics(self, dataset: List[Dict]) -> Dict:
        """Статистика по датасету"""
        stats = {
            'total': len(dataset),
            'original': sum(1 for item in dataset if not item.get('augmented', False)),
            'augmented': sum(1 for item in dataset if item.get('augmented', False)),
            'by_type': {}
        }

        for item in dataset:
            ptype = item['primary_type']
            stats['by_type'][ptype] = stats['by_type'].get(ptype, 0) + 1

        return stats


def main():
    """Основная функция для запуска аугментации"""
    import argparse

    parser = argparse.ArgumentParser(description='Data Augmentation для ML датасета')
    parser.add_argument('--target-size', type=int, default=500,
                       help='Целевой размер датасета (default: 500)')
    parser.add_argument('--input', type=str, default=None,
                       help='Путь к исходному датасету')
    parser.add_argument('--output', type=str, default=None,
                       help='Путь для сохранения результата')
    parser.add_argument('--stats', action='store_true',
                       help='Показать только статистику')

    args = parser.parse_args()

    print("="*70)
    print("DATA AUGMENTATION FOR ML TRAINING")
    print("="*70)

    augmentor = DataAugmentor(dataset_path=args.input)

    if args.stats:
        # Только статистика
        stats = augmentor.get_statistics(augmentor.dataset)
        print("\n📊 Current Dataset Statistics:")
        print(f"  Total: {stats['total']}")
        print(f"  Original: {stats['original']}")
        print(f"  Augmented: {stats['augmented']}")
        print(f"\n  By type:")
        for ptype, count in sorted(stats['by_type'].items()):
            print(f"    {ptype}: {count}")
        return

    # Аугментация
    augmented = augmentor.augment_all(target_size=args.target_size)

    # Сохранение
    augmentor.save_augmented(augmented, output_path=args.output)

    # Статистика
    stats = augmentor.get_statistics(augmented)
    print("\n📊 Final Dataset Statistics:")
    print(f"  Total: {stats['total']}")
    print(f"  Original: {stats['original']}")
    print(f"  Augmented: {stats['augmented']}")
    print(f"\n  By type (top 5):")
    for ptype, count in sorted(stats['by_type'].items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"    {ptype}: {count}")

    print("\n✅ Augmentation complete!")
    print(f"\nNext steps:")
    print(f"  1. Review augmented data: training_dataset_augmented.json")
    print(f"  2. Retrain model: python ml_classifier.py --train --dataset training_dataset_augmented.json")
    print(f"  3. Evaluate: python compare_classifiers.py")


if __name__ == '__main__':
    main()
