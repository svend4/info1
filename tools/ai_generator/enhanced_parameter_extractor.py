#!/usr/bin/env python3
"""
Enhanced Parameter Extractor (Фаза 3 ЭТАПА 9)

Расширенное извлечение параметров из описаний проектов.
Извлекает: budget, timeline, team, phase, audience, риски, приоритеты и др.
"""

import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import json


@dataclass
class ExtractedParameters:
    """Извлечённые параметры проекта"""
    # Базовые параметры
    budget: Optional[Dict[str, Any]] = None
    timeline: Optional[Dict[str, Any]] = None
    team_size: Optional[int] = None
    scale: Optional[str] = None

    # Расширенные параметры
    phase: Optional[str] = None  # MVP, alpha, beta, production, etc.
    target_audience: List[str] = None
    priority: Optional[str] = None  # low, medium, high, critical
    risk_level: Optional[str] = None  # low, medium, high
    technologies: List[str] = None
    dependencies: List[str] = None
    stakeholders: List[str] = None
    location: Optional[str] = None
    industry: Optional[str] = None

    # Дополнительные признаки
    has_deadline: bool = False
    is_funded: bool = False
    has_team: bool = False
    is_commercial: bool = False
    is_nonprofit: bool = False

    def __post_init__(self):
        """Инициализация пустых списков"""
        if self.target_audience is None:
            self.target_audience = []
        if self.technologies is None:
            self.technologies = []
        if self.dependencies is None:
            self.dependencies = []
        if self.stakeholders is None:
            self.stakeholders = []


class EnhancedParameterExtractor:
    """
    Расширенный экстрактор параметров

    Извлекает более 15 типов параметров из описания проекта.
    """

    # Паттерны для бюджета (расширенные)
    BUDGET_PATTERNS = [
        # Миллионы
        (r'(\d+(?:[.,]\d+)?)\s*(?:млн|миллион|million|m)\s*(?:₽|руб|rub|рублей)', 'RUB', 1_000_000),
        (r'(\d+(?:[.,]\d+)?)\s*(?:млн|million|m)\s*(?:\$|usd|dollar)', 'USD', 1_000_000),
        (r'(\d+(?:[.,]\d+)?)\s*(?:млн|million|m)\s*(?:€|eur|euro)', 'EUR', 1_000_000),
        # Тысячи
        (r'(\d+(?:[.,]\d+)?)\s*(?:тыс|тысяч|thousand|k)\s*(?:₽|руб|rub|рублей)', 'RUB', 1_000),
        (r'(\d+(?:[.,]\d+)?)\s*(?:тыс|thousand|k)\s*(?:\$|usd|dollar)', 'USD', 1_000),
        # Простые числа с валютой
        (r'(\d+(?:[.,]\d+)?)\s*(?:₽|руб|rub|рублей)', 'RUB', 1),
        (r'\$\s*(\d+(?:[.,]\d+)?)', 'USD', 1),
        (r'€\s*(\d+(?:[.,]\d+)?)', 'EUR', 1),
        # Ключевые слова
        (r'бюджет[:\s]+(\d+(?:[.,]\d+)?)', 'RUB', 1),
        (r'грант[:\s]+(\d+(?:[.,]\d+)?)', 'RUB', 1),
        (r'инвестиц[иі][яі][:\s]+(\d+(?:[.,]\d+)?)', 'RUB', 1),
    ]

    # Паттерны для временных рамок (расширенные)
    TIMELINE_PATTERNS = [
        (r'(\d+)\s*(?:месяц|мес|month)', 'months'),
        (r'(\d+)\s*(?:год|лет|year)', 'years'),
        (r'(\d+)\s*(?:недел|week)', 'weeks'),
        (r'(\d+)\s*(?:дн|день|day)', 'days'),
        (r'(\d+)\s*(?:квартал|quarter|q)', 'quarters'),
    ]

    # Паттерны для команды
    TEAM_PATTERNS = [
        r'(\d+)\s*(?:сотрудник|человек|people|member)',
        r'команда\s*(?:из\s*)?(\d+)',
        r'(\d+)\s*(?:разработчик|developer)',
        r'(\d+)\s*(?:специалист|expert)',
    ]

    # Фаза/стадия проекта
    PHASE_KEYWORDS = {
        'concept': ['концепция', 'идея', 'concept', 'idea'],
        'planning': ['планирование', 'planning', 'план', 'подготовка'],
        'mvp': ['mvp', 'минимальный продукт', 'прототип', 'prototype'],
        'alpha': ['alpha', 'альфа', 'ранняя версия'],
        'beta': ['beta', 'бета', 'тестирование', 'testing'],
        'production': ['production', 'продакшн', 'запуск', 'launch', 'релиз', 'release'],
        'scaling': ['масштабирование', 'scaling', 'рост', 'growth', 'расширение'],
    }

    # Целевая аудитория
    AUDIENCE_KEYWORDS = [
        'студент', 'student',
        'профессионал', 'professional',
        'начинающ', 'beginner',
        'дети', 'children', 'kids',
        'взрослые', 'adults',
        'пенсионер', 'elderly', 'senior',
        'бизнес', 'business', 'компани',
        'предприниматель', 'entrepreneur',
        'инвестор', 'investor',
        'разработчик', 'developer',
        'дизайнер', 'designer',
    ]

    # Приоритет
    PRIORITY_KEYWORDS = {
        'low': ['низкий', 'low', 'не срочно', 'можно отложить'],
        'medium': ['средний', 'medium', 'обычный', 'нормальный'],
        'high': ['высокий', 'high', 'важный', 'приоритетный'],
        'critical': ['критический', 'critical', 'срочный', 'urgent', 'немедленно'],
    }

    # Уровень риска
    RISK_KEYWORDS = {
        'low': ['низкий риск', 'надёжн', 'стабильн', 'проверен'],
        'medium': ['средний риск', 'умеренн'],
        'high': ['высокий риск', 'рискован', 'эксперимент', 'иннова', 'новатор'],
    }

    # Технологии (расширенный список)
    TECH_KEYWORDS = [
        # Frontend
        'react', 'vue', 'angular', 'svelte', 'next.js', 'nuxt',
        # Backend
        'node', 'python', 'java', 'go', 'rust', 'php', 'ruby',
        'django', 'flask', 'fastapi', 'spring', 'express',
        # Mobile
        'react native', 'flutter', 'swift', 'kotlin', 'ionic',
        # Databases
        'postgresql', 'mysql', 'mongodb', 'redis', 'elasticsearch',
        # DevOps
        'docker', 'kubernetes', 'aws', 'azure', 'gcp', 'terraform',
        # Other
        'blockchain', 'ai', 'ml', 'machine learning', 'deep learning',
    ]

    # Индустрии/домены
    INDUSTRY_KEYWORDS = {
        'fintech': ['fintech', 'финтех', 'финанс', 'банк', 'platezh'],
        'healthtech': ['healthtech', 'медтех', 'медицин', 'здоровье', 'health'],
        'edtech': ['edtech', 'едтех', 'образован', 'обучен', 'education'],
        'ecommerce': ['ecommerce', 'e-commerce', 'интернет-магазин', 'marketplace'],
        'logistics': ['логистика', 'logistics', 'доставка', 'транспорт'],
        'agritech': ['agritech', 'агротех', 'сельское хозяйство', 'agriculture'],
        'proptech': ['proptech', 'недвижимость', 'real estate'],
    }

    def __init__(self):
        """Инициализация экстрактора"""
        pass

    def extract(self, description: str) -> ExtractedParameters:
        """
        Извлечение всех параметров из описания

        Args:
            description: Описание проекта

        Returns:
            ExtractedParameters со всеми извлечёнными параметрами
        """
        text = description.lower()

        return ExtractedParameters(
            budget=self._extract_budget(description),
            timeline=self._extract_timeline(description),
            team_size=self._extract_team_size(description),
            scale=self._extract_scale(text),
            phase=self._extract_phase(text),
            target_audience=self._extract_audience(text),
            priority=self._extract_priority(text),
            risk_level=self._extract_risk(text),
            technologies=self._extract_technologies(text),
            dependencies=self._extract_dependencies(text),
            stakeholders=self._extract_stakeholders(text),
            location=self._extract_location(description),
            industry=self._extract_industry(text),
            has_deadline=self._has_deadline(text),
            is_funded=self._is_funded(text),
            has_team=self._extract_team_size(description) is not None,
            is_commercial=self._is_commercial(text),
            is_nonprofit=self._is_nonprofit(text),
        )

    def _extract_budget(self, text: str) -> Optional[Dict[str, Any]]:
        """Извлечение бюджета с валютой и суммой"""
        for pattern, currency, multiplier in self.BUDGET_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    amount = float(match.group(1).replace(',', '.'))
                    total = amount * multiplier
                    return {
                        'amount': total,
                        'currency': currency,
                        'formatted': f"{total:,.0f} {currency}",
                        'original': match.group(0)
                    }
                except (ValueError, IndexError):
                    pass
        return None

    def _extract_timeline(self, text: str) -> Optional[Dict[str, Any]]:
        """Извлечение временных рамок"""
        for pattern, unit in self.TIMELINE_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    value = int(match.group(1))
                    # Конвертация в месяцы для унификации
                    if unit == 'years':
                        months = value * 12
                    elif unit == 'months':
                        months = value
                    elif unit == 'weeks':
                        months = value / 4.0
                    elif unit == 'quarters':
                        months = value * 3
                    elif unit == 'days':
                        months = value / 30.0
                    else:
                        months = value

                    return {
                        'value': value,
                        'unit': unit,
                        'months': round(months, 1),
                        'formatted': f"{value} {unit}",
                        'original': match.group(0)
                    }
                except (ValueError, IndexError):
                    pass
        return None

    def _extract_team_size(self, text: str) -> Optional[int]:
        """Извлечение размера команды"""
        for pattern in self.TEAM_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    return int(match.group(1))
                except (ValueError, IndexError):
                    pass
        return None

    def _extract_scale(self, text: str) -> Optional[str]:
        """Определение масштаба"""
        scale_keywords = {
            'small': ['маленький', 'small', 'мини', 'простой', 'базовый'],
            'medium': ['средний', 'medium', 'обычный', 'стандартный'],
            'large': ['большой', 'large', 'крупный', 'масштабный', 'enterprise']
        }

        for scale, keywords in scale_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    return scale
        return 'medium'

    def _extract_phase(self, text: str) -> Optional[str]:
        """Определение фазы/стадии проекта"""
        for phase, keywords in self.PHASE_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text:
                    return phase
        return None

    def _extract_audience(self, text: str) -> List[str]:
        """Извлечение целевой аудитории"""
        found = []
        for keyword in self.AUDIENCE_KEYWORDS:
            if keyword in text:
                found.append(keyword)
        return found[:3]  # Топ-3

    def _extract_priority(self, text: str) -> Optional[str]:
        """Определение приоритета"""
        for priority, keywords in self.PRIORITY_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text:
                    return priority
        return None

    def _extract_risk(self, text: str) -> Optional[str]:
        """Определение уровня риска"""
        for risk, keywords in self.RISK_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text:
                    return risk
        return None

    def _extract_technologies(self, text: str) -> List[str]:
        """Извлечение технологий"""
        found = []
        for tech in self.TECH_KEYWORDS:
            if tech in text:
                found.append(tech)
        return found

    def _extract_dependencies(self, text: str) -> List[str]:
        """Извлечение зависимостей"""
        deps_keywords = [
            'зависит от', 'требует', 'depends on', 'requires',
            'интеграция с', 'integration with'
        ]
        dependencies = []

        for keyword in deps_keywords:
            if keyword in text:
                # Простое извлечение следующего слова после ключевого
                pattern = rf'{keyword}\s+(\w+)'
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    dependencies.append(match.group(1))

        return dependencies

    def _extract_stakeholders(self, text: str) -> List[str]:
        """Извлечение стейкхолдеров"""
        stakeholder_keywords = [
            'инвестор', 'investor', 'заказчик', 'customer', 'client',
            'партнёр', 'partner', 'пользователь', 'user',
        ]
        found = []
        for keyword in stakeholder_keywords:
            if keyword in text:
                found.append(keyword)
        return found

    def _extract_location(self, text: str) -> Optional[str]:
        """Извлечение локации"""
        # Простые паттерны для городов
        city_pattern = r'(?:в|из)\s+(москв|санкт-петербург|спб|екатеринбург|новосибирск|казан|нижн)'
        match = re.search(city_pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)
        return None

    def _extract_industry(self, text: str) -> Optional[str]:
        """Определение индустрии"""
        for industry, keywords in self.INDUSTRY_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text:
                    return industry
        return None

    def _has_deadline(self, text: str) -> bool:
        """Проверка наличия дедлайна"""
        deadline_keywords = ['дедлайн', 'deadline', 'срок', 'к концу', 'до', 'к дате']
        return any(kw in text for kw in deadline_keywords)

    def _is_funded(self, text: str) -> bool:
        """Проверка наличия финансирования"""
        funded_keywords = ['грант', 'grant', 'инвестиц', 'investment', 'финансиров', 'funded']
        return any(kw in text for kw in funded_keywords)

    def _is_commercial(self, text: str) -> bool:
        """Проверка коммерческого характера"""
        commercial_keywords = ['коммерческ', 'commercial', 'продаж', 'sales', 'прибыл', 'profit']
        return any(kw in text for kw in commercial_keywords)

    def _is_nonprofit(self, text: str) -> bool:
        """Проверка некоммерческого характера"""
        nonprofit_keywords = ['благотворител', 'charity', 'волонтёр', 'volunteer', 'нко', 'nonprofit']
        return any(kw in text for kw in nonprofit_keywords)

    def to_dict(self, params: ExtractedParameters) -> Dict:
        """Преобразование в словарь"""
        return asdict(params)

    def to_json(self, params: ExtractedParameters) -> str:
        """Преобразование в JSON"""
        return json.dumps(self.to_dict(params), ensure_ascii=False, indent=2)


def main():
    """Тестирование экстрактора"""
    extractor = EnhancedParameterExtractor()

    test_cases = [
        "Создать MVP финтех-приложения на React для студентов, бюджет 2.5 млн ₽, срок 6 месяцев",
        "Научное исследование с высоким риском, грант РНФ 4.5 млн ₽, команда из 8 человек",
        "Срочный проект! Критический приоритет. Нужен launch в продакшн через 3 месяца",
        "Благотворительный фонд помощи детям, требует интеграции с банковскими системами",
        "E-commerce платформа для малого бизнеса в Москве, Python + Django + PostgreSQL",
    ]

    print("="*70)
    print("ENHANCED PARAMETER EXTRACTOR - TESTING")
    print("="*70)

    for i, desc in enumerate(test_cases, 1):
        print(f"\n{'='*70}")
        print(f"Тест {i}: {desc}")
        print('='*70)

        params = extractor.extract(desc)

        print(f"\n💰 Budget: {params.budget}")
        print(f"⏱️  Timeline: {params.timeline}")
        print(f"👥 Team size: {params.team_size}")
        print(f"📏 Scale: {params.scale}")
        print(f"🔄 Phase: {params.phase}")
        print(f"🎯 Target audience: {params.target_audience}")
        print(f"⚡ Priority: {params.priority}")
        print(f"⚠️  Risk level: {params.risk_level}")
        print(f"💻 Technologies: {params.technologies}")
        print(f"📍 Location: {params.location}")
        print(f"🏭 Industry: {params.industry}")
        print(f"")
        print(f"Flags:")
        print(f"  - Has deadline: {params.has_deadline}")
        print(f"  - Is funded: {params.is_funded}")
        print(f"  - Has team: {params.has_team}")
        print(f"  - Is commercial: {params.is_commercial}")
        print(f"  - Is nonprofit: {params.is_nonprofit}")


if __name__ == '__main__':
    main()
