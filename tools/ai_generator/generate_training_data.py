#!/usr/bin/env python3
"""
Генератор обучающих данных для ML-классификатора

Создаёт вариации существующих примеров для увеличения датасета.
"""

import json
import random
from typing import List, Dict

# Шаблоны описаний для каждого типа проекта
DESCRIPTION_TEMPLATES = {
    'software': [
        "Разработка {product} для {purpose}",
        "Создание {product} с использованием {tech}",
        "{product} на базе {tech}",
        "Мобильное приложение для {purpose}",
        "Веб-сервис {product}",
        "API для {purpose}",
        "SaaS платформа {product}",
        "Десктопное приложение для {purpose}",
    ],
    'research': [
        "Исследование {topic} в области {field}",
        "Научная работа по {topic}",
        "Диссертация на тему {topic}",
        "Эксперимент по изучению {topic}",
        "Анализ {topic} методом {method}",
        "Грант на исследование {topic}",
    ],
    'business': [
        "Стартап в области {industry}",
        "Бизнес-план для {product}",
        "Открытие {business_type} в сфере {industry}",
        "Компания по производству {product}",
        "Франшиза {business_type}",
        "Инвестиционный проект в {industry}",
    ],
    'education': [
        "Курс {subject} для {audience}",
        "Образовательная программа по {subject}",
        "Тренинг {subject}",
        "Онлайн-курс {subject}",
        "Учебный план по {subject}",
        "Семинар на тему {subject}",
    ],
    'legal': [
        "Юридическое сопровождение {service_type}",
        "Консультация по вопросам {legal_area}",
        "Подготовка документов для {purpose}",
        "Представление интересов в {court_type}",
        "Правовой аудит {subject}",
    ],
    'healthcare': [
        "{facility_type} с отделением {specialization}",
        "Медицинский центр {specialization}",
        "Программа лечения {condition}",
        "Диагностика и лечение {condition}",
        "Телемедицина для {purpose}",
    ],
    'arts': [
        "Выставка {art_type}",
        "Творческий проект {art_form}",
        "Арт-инсталляция {theme}",
        "Концерт {genre}",
        "Галерея {art_type}",
    ],
    'finance': [
        "Управление {asset_type}",
        "Инвестирование в {market}",
        "Портфель {investment_type}",
        "Финансовое планирование для {client_type}",
        "Консультация по {service}",
    ],
    'government': [
        "Программа {initiative} для {target}",
        "Государственный проект {purpose}",
        "Госуслуга {service_name}",
        "Муниципальная инициатива {purpose}",
        "Цифровизация {department}",
    ],
    'nonprofit': [
        "Благотворительный фонд {mission}",
        "НКО по {cause}",
        "Волонтёрская программа {purpose}",
        "Социальный проект помощи {target}",
        "Некоммерческая организация {mission}",
    ],
    'manufacturing': [
        "Производство {product}",
        "Завод по выпуску {product}",
        "Производственная линия {product}",
        "Фабрика {product}",
        "Цех по изготовлению {product}",
    ],
    'agriculture': [
        "Выращивание {crop}",
        "Фермерское хозяйство {type}",
        "Животноводческая ферма {livestock}",
        "Агрокомплекс {focus}",
        "Тепличное хозяйство {crop}",
    ],
    'sports': [
        "Тренировочная программа по {sport}",
        "Спортивная секция {sport}",
        "Фитнес-клуб с {facility}",
        "Академия {sport} для {age_group}",
        "Спортивный лагерь {sport}",
    ],
    'hospitality': [
        "{facility_type} на {capacity} мест",
        "Ресторан {cuisine}",
        "Туристический {service}",
        "Отель категории {stars} звёзд",
        "Гостиничный комплекс с {amenity}",
    ],
    'retail': [
        "Магазин {product_category}",
        "Интернет-магазин {product}",
        "Торговая сеть {format}",
        "Маркетплейс {niche}",
        "Розничная точка {product}",
    ],
    'hobby': [
        "Блог о {topic}",
        "Коллекция {items}",
        "Канал на YouTube про {topic}",
        "Личный проект {description}",
        "Творческий дневник {theme}",
    ],
}

# Словари для подстановки
REPLACEMENTS = {
    'product': ['мобильного приложения', 'веб-платформы', 'системы', 'сервиса', 'инструмента'],
    'purpose': ['управления задачами', 'учёта расходов', 'коммуникации', 'аналитики', 'автоматизации'],
    'tech': ['React', 'Python', 'Node.js', 'Django', 'Vue.js', 'FastAPI'],
    'topic': ['экологии', 'климата', 'биологии', 'физики', 'химии'],
    'field': ['медицины', 'IT', 'образования', 'энергетики'],
    'method': ['эксперимента', 'опроса', 'наблюдения', 'моделирования'],
    'industry': ['финтех', 'ритейла', 'образования', 'здравоохранения', 'логистики'],
    'business_type': ['кафе', 'магазина', 'компании', 'агентства'],
    'subject': ['программирования', 'маркетинга', 'дизайна', 'менеджмента', 'английского языка'],
    'audience': ['начинающих', 'профессионалов', 'студентов', 'детей'],
    'service_type': ['сделок', 'споров', 'договоров', 'регистрации'],
    'legal_area': ['налогового права', 'трудового права', 'корпоративного права'],
    'court_type': ['арбитражном суде', 'гражданском суде'],
    'facility_type': ['Клиника', 'Больница', 'Поликлиника', 'Медцентр'],
    'specialization': ['кардиологии', 'неврологии', 'хирургии', 'педиатрии'],
    'condition': ['диабета', 'гипертонии', 'астмы'],
    'art_type': ['современного искусства', 'живописи', 'скульптуры', 'фотографии'],
    'art_form': ['в области музыки', 'танца', 'театра', 'кино'],
    'theme': ['на тему природы', 'городской среды', 'человека'],
    'genre': ['классической музыки', 'джаза', 'рока'],
    'asset_type': ['инвестиционным портфелем', 'активами', 'капиталом'],
    'market': ['акции', 'облигации', 'недвижимость', 'криптовалюту'],
    'investment_type': ['акций', 'облигаций', 'фондов'],
    'client_type': ['физических лиц', 'компаний', 'стартапов'],
    'service': ['инвестициям', 'налогам', 'кредитам'],
    'initiative': ['цифровизации', 'благоустройства', 'развития'],
    'target': ['граждан', 'бизнеса', 'молодёжи'],
    'purpose': ['улучшения сервиса', 'повышения качества', 'оптимизации'],
    'service_name': ['по оформлению документов', 'онлайн-записи', 'оплаты штрафов'],
    'department': ['госуслуг', 'ЖКХ', 'образования'],
    'mission': ['помощи детям', 'защиты животных', 'экологии'],
    'cause': ['поддержке малого бизнеса', 'развитию культуры', 'защите прав'],
    'crop': ['овощей', 'фруктов', 'зерновых', 'ягод'],
    'type': ['молочного направления', 'растениеводческое', 'комбинированное'],
    'livestock': ['крупного рогатого скота', 'свиней', 'птицы'],
    'focus': ['по выращиванию томатов', 'по производству молока'],
    'sport': ['футбола', 'тенниса', 'плавания', 'бокса', 'йоги'],
    'facility': ['бассейном', 'тренажёрным залом', 'сауной'],
    'age_group': ['детей', 'взрослых', 'юниоров'],
    'capacity': ['50', '100', '200', '30'],
    'cuisine': ['итальянской кухни', 'японской кухни', 'европейской кухни'],
    'stars': ['3', '4', '5'],
    'amenity': ['рестораном', 'спа-центром', 'конференц-залом'],
    'product_category': ['одежды', 'электроники', 'косметики', 'спорттоваров'],
    'format': ['супермаркетов', 'бутиков', 'дискаунтеров'],
    'niche': ['товаров ручной работы', 'эко-товаров', 'детских товаров'],
    'items': ['марок', 'монет', 'книг', 'виниловых пластинок'],
    'topic': ['путешествиях', 'кулинарии', 'фотографии', 'технологиях'],
    'description': ['по рисованию', 'по изучению языков', 'по музыке'],
}


def generate_description(project_type: str) -> str:
    """Генерация случайного описания для типа проекта"""
    templates = DESCRIPTION_TEMPLATES.get(project_type, [])
    if not templates:
        return f"Проект типа {project_type}"

    template = random.choice(templates)

    # Подстановка значений
    for key, values in REPLACEMENTS.items():
        if f'{{{key}}}' in template:
            template = template.replace(f'{{{key}}}', random.choice(values))

    return template


def generate_examples_for_type(project_type: str, count: int, start_id: int) -> List[Dict]:
    """Генерация примеров для одного типа проекта"""
    examples = []

    for i in range(count):
        example = {
            'id': f'{start_id + i:03d}',
            'description': generate_description(project_type),
            'primary_type': project_type,
            'secondary_types': [],
            'features': {}
        }
        examples.append(example)

    return examples


def generate_full_dataset(examples_per_type: int = 15) -> List[Dict]:
    """Генерация полного датасета"""
    all_types = list(DESCRIPTION_TEMPLATES.keys())
    all_examples = []
    current_id = 1

    for project_type in all_types:
        examples = generate_examples_for_type(project_type, examples_per_type, current_id)
        all_examples.extend(examples)
        current_id += examples_per_type

    return all_examples


def main():
    """Генерация и сохранение датасета"""
    import argparse

    parser = argparse.ArgumentParser(description='Генератор обучающих данных')
    parser.add_argument('--count', type=int, default=15,
                       help='Количество примеров на тип (default: 15)')
    parser.add_argument('--output', default='training_dataset_generated.json',
                       help='Выходной файл (default: training_dataset_generated.json)')
    parser.add_argument('--merge', default=None,
                       help='Объединить с существующим датасетом')

    args = parser.parse_args()

    # Генерация
    print(f"Генерация {args.count} примеров для каждого из 16 типов...")
    dataset = generate_full_dataset(args.count)

    # Объединение с существующим
    if args.merge:
        try:
            with open(args.merge, 'r', encoding='utf-8') as f:
                existing = json.load(f)
            dataset = existing + dataset
            print(f"Объединено с {len(existing)} существующими примерами")
        except FileNotFoundError:
            print(f"Файл {args.merge} не найден, создаётся новый датасет")

    # Сохранение
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(dataset, f, ensure_ascii=False, indent=2)

    print(f"✅ Сохранено {len(dataset)} примеров в {args.output}")

    # Статистика
    type_counts = {}
    for ex in dataset:
        t = ex['primary_type']
        type_counts[t] = type_counts.get(t, 0) + 1

    print("\nСтатистика по типам:")
    for project_type in sorted(type_counts.keys()):
        print(f"  {project_type}: {type_counts[project_type]} примеров")


if __name__ == '__main__':
    main()
