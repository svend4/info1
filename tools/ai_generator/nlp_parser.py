#!/usr/bin/env python3
"""
Natural Language Parser for Project Descriptions

Парсинг естественно-языковых описаний проектов и извлечение ключевой информации.

Уровень абстракции: α=-4 (исполняемый код)
Связи:
  ⇑ ../ЭТАП-9-ПЛАН.md (α=+1) — архитектура AI-системы
  ↔ classifier.py (α=-4) — классификация типов проектов
"""

import re
from typing import Dict, List, Optional, Set
from dataclasses import dataclass


@dataclass
class ParsedProject:
    """Результат парсинга описания проекта"""

    raw_description: str
    keywords: List[str]
    detected_types: List[str]
    confidence_scores: Dict[str, float]
    extracted_features: Dict[str, any]
    scale: Optional[str] = None
    budget: Optional[str] = None
    timeline: Optional[str] = None
    team_size: Optional[int] = None


class NLPParser:
    """
    Парсер естественно-языковых описаний проектов

    Фаза 1: Rule-based подход с keyword matching
    Фаза 2: Замена на ML-модели (BERT/DistilBERT)
    """

    # Ключевые слова для каждого типа проекта
    TYPE_KEYWORDS = {
        'software': {
            'keywords': [
                'приложение', 'app', 'сайт', 'веб', 'web', 'api',
                'backend', 'frontend', 'мобильное', 'mobile',
                'программа', 'софт', 'код', 'разработка',
                'react', 'vue', 'angular', 'node', 'python', 'java'
            ],
            'weight': 1.0
        },
        'research': {
            'keywords': [
                'исследование', 'research', 'эксперимент', 'experiment',
                'гипотеза', 'hypothesis', 'данные', 'data', 'анализ',
                'научн', 'science', 'изучение', 'study', 'грант',
                'публикация', 'статья', 'диссертация'
            ],
            'weight': 1.0
        },
        'business': {
            'keywords': [
                'бизнес', 'business', 'стартап', 'startup', 'компания',
                'предприниматель', 'entrepreneur', 'продажи', 'sales',
                'маркетинг', 'marketing', 'бизнес-план', 'инвестиции',
                'revenue', 'выручка', 'прибыль', 'roi'
            ],
            'weight': 1.0
        },
        'education': {
            'keywords': [
                'образование', 'education', 'обучение', 'learning',
                'курс', 'course', 'урок', 'lesson', 'студент', 'student',
                'преподаватель', 'teacher', 'школа', 'университет',
                'lms', 'elearning', 'онлайн-курс', 'учебный', 'педагог'
            ],
            'weight': 1.3  # Увеличен вес для education
        },
        'legal': {
            'keywords': [
                'юридический', 'legal', 'право', 'law', 'суд', 'court',
                'договор', 'contract', 'иск', 'lawyer', 'адвокат',
                'compliance', 'законодательство', 'юрист'
            ],
            'weight': 1.0
        },
        'healthcare': {
            'keywords': [
                'здравоохранение', 'healthcare', 'медицин', 'medical',
                'клиника', 'clinic', 'больница', 'hospital', 'врач',
                'doctor', 'пациент', 'patient', 'лечение', 'treatment',
                'диагностика', 'ehr', 'emr', 'здоровье', 'терапия'
            ],
            'weight': 1.3  # Увеличен вес для healthcare
        },
        'arts': {
            'keywords': [
                'искусство', 'art', 'творчество', 'creative', 'дизайн',
                'design', 'выставка', 'exhibition', 'галерея', 'gallery',
                'художник', 'artist', 'музыка', 'music', 'театр', 'theater',
                'культурный', 'арт-проект'
            ],
            'weight': 1.3  # Увеличен вес для arts
        },
        'finance': {
            'keywords': [
                'финансы', 'finance', 'инвестиции', 'investment',
                'банк', 'bank', 'кредит', 'loan', 'портфель', 'portfolio',
                'акции', 'stocks', 'трейдинг', 'trading', 'бухгалтерия'
            ],
            'weight': 1.0
        },
        'government': {
            'keywords': [
                'государств', 'government', 'госуслуга', 'public service',
                'муниципал', 'municipal', 'администрация', 'мэрия',
                'чиновник', 'official', 'бюджет', 'регулирование',
                'гос', 'публичный', 'федеральный'
            ],
            'weight': 1.3  # Увеличен вес для government
        },
        'nonprofit': {
            'keywords': [
                'некоммерческ', 'nonprofit', 'ngo', 'благотворительн',
                'charity', 'волонтёр', 'volunteer', 'фонд', 'foundation',
                'донор', 'donor', 'гранты', 'помощь'
            ],
            'weight': 1.0
        },
        'manufacturing': {
            'keywords': [
                'производство', 'manufacturing', 'завод', 'factory',
                'производственн', 'промышленн', 'industry', 'цех',
                'оборудование', 'equipment', 'качество', 'quality control'
            ],
            'weight': 1.0
        },
        'agriculture': {
            'keywords': [
                'сельское хозяйство', 'agriculture', 'ферма', 'farm',
                'урожай', 'crop', 'животноводство', 'livestock',
                'агро', 'agro', 'поле', 'field', 'посев',
                'фермер', 'хозяйство'
            ],
            'weight': 1.3  # Увеличен вес для agriculture
        },
        'sports': {
            'keywords': [
                'спорт', 'sport', 'тренировка', 'training', 'атлет',
                'athlete', 'соревнование', 'competition', 'фитнес',
                'fitness', 'команда', 'team', 'тренер', 'coach'
            ],
            'weight': 1.0
        },
        'hospitality': {
            'keywords': [
                'гостиниц', 'hotel', 'отель', 'ресторан', 'restaurant',
                'туризм', 'tourism', 'гость', 'guest', 'бронирование',
                'booking', 'hospitality', 'путешеств', 'travel'
            ],
            'weight': 1.0
        },
        'retail': {
            'keywords': [
                'розничн', 'retail', 'магазин', 'store', 'shop',
                'продажа', 'торговля', 'товар', 'product', 'покупател',
                'customer', 'ecommerce', 'маркетплейс', 'marketplace'
            ],
            'weight': 1.0
        },
        'hobby': {
            'keywords': [
                'хобби', 'hobby', 'личный', 'personal', 'увлечение',
                'passion', 'коллекция', 'collection', 'досуг', 'leisure',
                'творческий проект', 'pet project', 'для себя',
                'блог', 'blog', 'дневник'
            ],
            'weight': 1.3  # Увеличен вес для hobby
        }
    }

    # Паттерны для извлечения параметров
    BUDGET_PATTERNS = [
        r'(\d+(?:[.,]\d+)?)\s*(?:млн|миллион|million|m)\s*(?:₽|руб|rub|рублей)',
        r'(\d+(?:[.,]\d+)?)\s*(?:тыс|тысяч|thousand|k)\s*(?:₽|руб|rub|рублей)',
        r'бюджет[:\s]+(\d+(?:[.,]\d+)?)',
        r'грант[:\s]+(\d+(?:[.,]\d+)?)',
    ]

    TIMELINE_PATTERNS = [
        r'(\d+)\s*(?:месяц|мес|month)',
        r'(\d+)\s*(?:год|лет|year)',
        r'(\d+)\s*(?:недел|week)',
    ]

    TEAM_PATTERNS = [
        r'(\d+)\s*(?:сотрудник|человек|people|member)',
        r'команда\s*(?:из\s*)?(\d+)',
    ]

    SCALE_KEYWORDS = {
        'small': ['маленький', 'small', 'мини', 'простой', 'базовый'],
        'medium': ['средний', 'medium', 'обычный', 'стандартный'],
        'large': ['большой', 'large', 'крупный', 'масштабный', 'enterprise']
    }

    def __init__(self):
        """Инициализация парсера"""
        pass

    def parse(self, description: str) -> ParsedProject:
        """
        Парсинг описания проекта

        Args:
            description: Текстовое описание проекта на естественном языке

        Returns:
            ParsedProject с извлечённой информацией
        """
        description_lower = description.lower()

        # Извлечение ключевых слов
        keywords = self._extract_keywords(description_lower)

        # Определение типов проектов
        detected_types, confidence_scores = self._detect_project_types(description_lower)

        # Извлечение параметров
        extracted_features = {
            'budget': self._extract_budget(description),
            'timeline': self._extract_timeline(description),
            'team_size': self._extract_team_size(description),
            'scale': self._extract_scale(description_lower),
            'technologies': self._extract_technologies(description),
        }

        return ParsedProject(
            raw_description=description,
            keywords=keywords,
            detected_types=detected_types,
            confidence_scores=confidence_scores,
            extracted_features=extracted_features,
            scale=extracted_features['scale'],
            budget=extracted_features['budget'],
            timeline=extracted_features['timeline'],
            team_size=extracted_features['team_size']
        )

    def _extract_keywords(self, text: str) -> List[str]:
        """Извлечение ключевых слов из текста"""
        # Простая токенизация по словам
        words = re.findall(r'\b\w+\b', text)

        # Фильтрация стоп-слов (упрощённо)
        stop_words = {'я', 'хочу', 'нужно', 'создать', 'для', 'в', 'на', 'с', 'и', 'или'}
        keywords = [w for w in words if w not in stop_words and len(w) > 2]

        return keywords[:20]  # Топ-20 слов

    def _detect_project_types(self, text: str) -> tuple[List[str], Dict[str, float]]:
        """
        Определение типов проектов на основе ключевых слов

        Returns:
            (sorted_types, confidence_scores)
        """
        scores = {}

        for project_type, config in self.TYPE_KEYWORDS.items():
            score = 0.0
            for keyword in config['keywords']:
                if keyword in text:
                    score += config['weight']

            if score > 0:
                scores[project_type] = score

        # Нормализация scores к [0, 1]
        if scores:
            max_score = max(scores.values())
            normalized_scores = {k: v / max_score for k, v in scores.items()}
        else:
            normalized_scores = {}

        # Сортировка по confidence
        sorted_types = sorted(normalized_scores.items(), key=lambda x: x[1], reverse=True)

        # Возврат топ-3 типов с confidence > 0.3
        top_types = [t for t, s in sorted_types if s >= 0.3][:3]

        # Если ничего не найдено, дефолт к software
        if not top_types:
            top_types = ['software']
            normalized_scores = {'software': 0.5}

        return top_types, normalized_scores

    def _extract_budget(self, text: str) -> Optional[str]:
        """Извлечение бюджета из текста"""
        for pattern in self.BUDGET_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0)
        return None

    def _extract_timeline(self, text: str) -> Optional[str]:
        """Извлечение временных рамок из текста"""
        for pattern in self.TIMELINE_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0)
        return None

    def _extract_team_size(self, text: str) -> Optional[int]:
        """Извлечение размера команды из текста"""
        for pattern in self.TEAM_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    return int(match.group(1))
                except (ValueError, IndexError):
                    pass
        return None

    def _extract_scale(self, text: str) -> Optional[str]:
        """Определение масштаба проекта"""
        for scale, keywords in self.SCALE_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text:
                    return scale
        return 'medium'  # default

    def _extract_technologies(self, text: str) -> List[str]:
        """Извлечение упоминаний технологий"""
        tech_keywords = [
            'react', 'vue', 'angular', 'node', 'python', 'java', 'c++',
            'docker', 'kubernetes', 'aws', 'azure', 'gcp', 'postgresql',
            'mongodb', 'redis', 'fastapi', 'django', 'flask'
        ]

        found_techs = []
        text_lower = text.lower()
        for tech in tech_keywords:
            if tech in text_lower:
                found_techs.append(tech)

        return found_techs


def main():
    """Тестирование парсера"""
    parser = NLPParser()

    test_cases = [
        "Хочу создать веб-приложение для управления задачами с React frontend",
        "Научное исследование микропластика в океане, грант РНФ 4.5 млн ₽, 24 месяца",
        "Планирую открыть клинику на 50 сотрудников с бизнес-планом",
        "Мобильное приложение для учёта финансов",
        "Интернет-магазин одежды с доставкой"
    ]

    print("=" * 70)
    print("NLP PARSER TESTING")
    print("=" * 70)

    for i, description in enumerate(test_cases, 1):
        print(f"\n{'='*70}")
        print(f"Test Case {i}")
        print(f"{'='*70}")
        print(f"Описание: {description}\n")

        result = parser.parse(description)

        print(f"Detected types: {result.detected_types}")
        print(f"Confidence: {result.confidence_scores}")
        print(f"Keywords: {result.keywords[:10]}")
        print(f"Budget: {result.budget}")
        print(f"Timeline: {result.timeline}")
        print(f"Team size: {result.team_size}")
        print(f"Scale: {result.scale}")
        print(f"Technologies: {result.extracted_features.get('technologies', [])}")


if __name__ == '__main__':
    main()
