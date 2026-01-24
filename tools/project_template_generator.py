#!/usr/bin/env python3
"""
Project Template Generator — Генератор шаблонов проектов для методологии ⇑⇓↔

ЭТАП 8: Адаптация и масштабирование
Автоматическое создание структуры нового проекта с методологией ⇑⇓↔

Usage:
    python3 project_template_generator.py --name my_project --type software
    python3 project_template_generator.py --name research_lab --type research
    python3 project_template_generator.py --domain medicine --interactive

Author: Claude Code (Methodology ⇑⇓↔)
Version: 1.1
Date: 2026-01-24
"""

import argparse
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional


class ProjectTemplateGenerator:
    """
    Генератор шаблонов проектов для методологии ⇑⇓↔

    Создаёт базовую структуру директорий и ключевые документы
    с правильными метаданными (α-уровень, Статус, CYCLE).
    """

    # Типы проектов и их характеристики
    PROJECT_TYPES = {
        "software": {
            "name": "Software Project",
            "description": "Проект разработки программного обеспечения",
            "alpha_focus": "α=-4..+3",
            "key_docs": ["README.md", "ARCHITECTURE.md", "API-REFERENCE.md"]
        },
        "research": {
            "name": "Research Project",
            "description": "Научно-исследовательский проект",
            "alpha_focus": "α=+1..+4",
            "key_docs": ["README.md", "RESEARCH-PLAN.md", "HYPOTHESIS.md"]
        },
        "business": {
            "name": "Business Project",
            "description": "Бизнес-проект",
            "alpha_focus": "α=-2..+2",
            "key_docs": ["README.md", "BUSINESS-PLAN.md", "METRICS.md"]
        },
        "education": {
            "name": "Educational Project",
            "description": "Образовательный проект",
            "alpha_focus": "α=0..+3",
            "key_docs": ["README.md", "CURRICULUM.md", "LEARNING-GOALS.md"]
        },
        "legal": {
            "name": "Legal Project",
            "description": "Юридический проект",
            "alpha_focus": "α=-1..+3",
            "key_docs": ["README.md", "LEGAL-FRAMEWORK.md", "CASE-LAW.md"]
        },
        "healthcare": {
            "name": "Healthcare Project",
            "description": "Проект здравоохранения",
            "alpha_focus": "α=-2..+3",
            "key_docs": ["README.md", "CLINICAL-PROTOCOLS.md", "PATIENT-CARE.md"]
        },
        "arts": {
            "name": "Arts & Creative Project",
            "description": "Творческий/художественный проект",
            "alpha_focus": "α=-3..+4",
            "key_docs": ["README.md", "CREATIVE-VISION.md", "PORTFOLIO.md"]
        }
    }

    def __init__(self, project_name: str, project_type: str = "software",
                 output_dir: Optional[Path] = None):
        """
        Инициализация генератора

        Args:
            project_name: Имя проекта
            project_type: Тип проекта (software/research/business/education/legal/healthcare/arts)
            output_dir: Директория для создания проекта (по умолчанию текущая)
        """
        self.project_name = project_name
        self.project_type = project_type
        self.output_dir = output_dir or Path.cwd()
        self.project_dir = self.output_dir / project_name

        if project_type not in self.PROJECT_TYPES:
            raise ValueError(f"Неизвестный тип проекта: {project_type}. "
                           f"Доступные: {', '.join(self.PROJECT_TYPES.keys())}")

    def generate(self, interactive: bool = False):
        """
        Генерация структуры проекта

        Args:
            interactive: Интерактивный режим с вопросами
        """
        print(f"🚀 Генерация проекта: {self.project_name}")
        print(f"📦 Тип: {self.PROJECT_TYPES[self.project_type]['name']}")
        print(f"📁 Директория: {self.project_dir}\n")

        # 1. Создать структуру директорий
        self._create_directory_structure()

        # 2. Создать ключевые документы
        self._create_core_documents()

        # 3. Создать файлы конфигурации методологии
        self._create_methodology_config()

        # 4. Создать инструментальную директорию
        self._create_tools_directory()

        print("\n✅ Проект успешно создан!")
        print(f"\nСледующие шаги:")
        print(f"  1. cd {self.project_name}")
        print(f"  2. Отредактируйте README.md с описанием проекта")
        print(f"  3. Запустите: python3 tools/health_metrics.py")
        print(f"  4. Начните развивать проект по методологии ⇑⇓↔\n")

    def _create_directory_structure(self):
        """Создание базовой структуры директорий"""
        print("📂 Создание структуры директорий...")

        # Базовая структура для всех типов проектов
        dirs = [
            "01-Концепция",
            "02-Архитектура",
            "03-Реализация",
            "docs",
            "tools"
        ]

        # Дополнительные директории в зависимости от типа
        if self.project_type == "software":
            dirs.extend(["src", "tests", "examples"])
        elif self.project_type == "research":
            dirs.extend(["data", "experiments", "publications"])
        elif self.project_type == "business":
            dirs.extend(["reports", "presentations", "financials"])
        elif self.project_type == "education":
            dirs.extend(["lessons", "materials", "assessments"])
        elif self.project_type == "legal":
            dirs.extend(["cases", "contracts", "regulations"])
        elif self.project_type == "healthcare":
            dirs.extend(["protocols", "cases", "research"])
        elif self.project_type == "arts":
            dirs.extend(["works", "sketches", "portfolio"])

        for dir_name in dirs:
            dir_path = self.project_dir / dir_name
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"  ✓ {dir_name}/")

    def _create_core_documents(self):
        """Создание ключевых документов проекта"""
        print("\n📝 Создание ключевых документов...")

        # README.md (α=+1) — обзор проекта
        self._create_readme()

        # МЕТОДОЛОГИЯ.md (α=+2) — применение методологии
        self._create_methodology_doc()

        # METRICS.md (α=+1) — метрики проекта
        self._create_metrics_doc()

        # Тип-специфичные документы
        if self.project_type == "software":
            self._create_architecture_doc()
        elif self.project_type == "research":
            self._create_research_plan_doc()
        elif self.project_type == "business":
            self._create_business_plan_doc()
        elif self.project_type == "education":
            self._create_curriculum_doc()
        elif self.project_type == "legal":
            self._create_legal_framework_doc()
        elif self.project_type == "healthcare":
            self._create_clinical_protocols_doc()
        elif self.project_type == "arts":
            self._create_creative_vision_doc()

    def _create_readme(self):
        """Создание README.md"""
        content = f"""# {self.project_name}
*Уровень абстракции: α=+1 (методология)*
*Статус: ⇑ ВВЕРХ (создание концепции)*
*CYCLE: 1*

**Тип проекта:** {self.PROJECT_TYPES[self.project_type]['name']}
**Дата создания:** {datetime.now().strftime('%Y-%m-%d')}

---

## Описание

[Опишите проект здесь]

## Цели

1. [Цель 1]
2. [Цель 2]
3. [Цель 3]

## Структура проекта

- **01-Концепция/** — концептуальные документы (α=+1..+3)
- **02-Архитектура/** — архитектурные решения (α=0)
- **03-Реализация/** — конкретная реализация (α=-1..-4)
- **docs/** — дополнительная документация
- **tools/** — инструменты методологии ⇑⇓↔

## Методология ⇑⇓↔

Этот проект использует методологию параллельного двунаправленного развития:

- **⇑ ВВЕРХ**: Обобщение от частного к общему
- **⇓ ВНИЗ**: Детализация от общего к частному
- **↔ ГОРИЗОНТ**: Связывание родственных концепций

См. [МЕТОДОЛОГИЯ.md](МЕТОДОЛОГИЯ.md) для деталей.

## Метрики здоровья

Запустите анализ метрик:

```bash
python3 tools/health_metrics.py
```

Целевые значения:
- VT (Vertical Traceability): 22-44%
- DB (Directional Balance): <30%
- CD (Connectivity Density): 16.5-33%
- CR (Convergence Rate): 0.6-1.3

---

**Создано с помощью методологии параллельного двунаправленного развития (⇑⇓↔)**
"""

        path = self.project_dir / "README.md"
        path.write_text(content, encoding='utf-8')
        print(f"  ✓ README.md (α=+1)")

    def _create_methodology_doc(self):
        """Создание МЕТОДОЛОГИЯ.md"""
        content = f"""# Применение методологии ⇑⇓↔ к проекту {self.project_name}
*Уровень абстракции: α=+2 (принципы)*
*Статус: ⇓ ВНИЗ (применение принципов)*
*CYCLE: 1*

---

## Иерархия абстракций

Проект организован по 9 уровням абстракции:

### α=+4: Онтология
Фундаментальные концепции домена

### α=+3: Философия
Принципы и ценности проекта

### α=+2: Теория
Общие законы и паттерны

### α=+1: Методология
Подходы и практики

### α=0: Архитектура
Структурные решения

### α=-1: Спецификации
Детальные требования

### α=-2: Шаблоны
Типовые решения

### α=-3: Примеры
Конкретные случаи

### α=-4: Реализация
Исполняемый код/данные

---

## Операторы развития

### ⇑ ВВЕРХ (Обобщение)
Переход от частного к общему:
- От конкретных решений к паттернам
- От примеров к принципам
- От данных к теории

### ⇓ ВНИЗ (Детализация)
Переход от общего к частному:
- От принципов к практикам
- От теории к реализации
- От концепции к коду

### ↔ ГОРИЗОНТ (Связывание)
Создание связей на одном уровне:
- Аналогии между решениями
- Паттерны взаимодействия
- Референсы к родственным концепциям

---

## Метрики качества

### VT (Vertical Traceability)
Процент связей пересекающих уровни α

**Цель:** 22-44%

### DB (Directional Balance)
Баланс между операторами ⇑⇓↔

**Цель:** <30% (стандартное отклонение от идеального распределения)

### CD (Connectivity Density)
Плотность связей между документами

**Цель:** 16.5-33%

### CR (Convergence Rate)
Скорость изменения метрик

**Цель:** 0.6-1.3

---

## Рекомендации

1. **Начните с концепции** (α=+2..+3)
   - Определите философию и принципы
   - Создайте онтологию домена

2. **Детализируйте архитектуру** (α=0..+1)
   - Разработайте структурные решения
   - Определите методологию работы

3. **Реализуйте решения** (α=-1..-4)
   - Создайте спецификации
   - Напишите код/документацию

4. **Обобщайте опыт** (⇑ ВВЕРХ)
   - Извлекайте паттерны из реализации
   - Обновляйте принципы на основе практики

5. **Измеряйте прогресс**
   - Регулярно запускайте health_metrics.py
   - Отслеживайте изменения метрик

---

**Создано с помощью методологии параллельного двунаправленного развития (⇑⇓↔)**
"""

        path = self.project_dir / "МЕТОДОЛОГИЯ.md"
        path.write_text(content, encoding='utf-8')
        print(f"  ✓ МЕТОДОЛОГИЯ.md (α=+2)")

    def _create_metrics_doc(self):
        """Создание METRICS.md"""
        content = f"""# Метрики проекта {self.project_name}
*Уровень абстракции: α=+1 (методология)*
*Статус: ↔ ГОРИЗОНТ (мониторинг)*
*CYCLE: 1*

---

## Текущие метрики

*Первый запуск: {datetime.now().strftime('%Y-%m-%d')}*

### VT (Vertical Traceability)
**Текущее значение:** N/A (запустите health_metrics.py)
**Целевое значение:** 22-44%

### DB (Directional Balance)
**Текущее значение:** N/A
**Целевое значение:** <30%

### CD (Connectivity Density)
**Текущее значение:** N/A
**Целевое значение:** 16.5-33%

### CR (Convergence Rate)
**Текущее значение:** N/A
**Целевое значение:** 0.6-1.3

---

## История измерений

| Дата | VT | DB | CD | CR | Комментарий |
|------|-----|-----|-----|-----|-------------|
| {datetime.now().strftime('%Y-%m-%d')} | - | - | - | - | Инициализация проекта |

---

## Анализ

### Сильные стороны
[Добавится после первых измерений]

### Области улучшения
[Добавится после первых измерений]

### Рекомендации
[Добавится после первых измерений]

---

**Создано с помощью методологии параллельного двунаправленного развития (⇑⇓↔)**
"""

        path = self.project_dir / "METRICS.md"
        path.write_text(content, encoding='utf-8')
        print(f"  ✓ METRICS.md (α=+1)")

    def _create_architecture_doc(self):
        """Создание ARCHITECTURE.md для software проекта"""
        content = """# Архитектура проекта
*Уровень абстракции: α=0 (архитектура)*
*Статус: ↔ ГОРИЗОНТ (структурные решения)*
*CYCLE: 1*

---

## Обзор архитектуры

[Опишите общую архитектуру проекта]

## Компоненты

### Component 1
**Назначение:** [Описание]
**α-уровень:** [Укажите уровень]
**Связи:**
- ⇑ [Связь к концепции]
- ⇓ [Связь к реализации]
- ↔ [Связь к родственному компоненту]

---

**Создано с помощью методологии параллельного двунаправленного развития (⇑⇓↔)**
"""
        path = self.project_dir / "02-Архитектура" / "ARCHITECTURE.md"
        path.write_text(content, encoding='utf-8')
        print(f"  ✓ 02-Архитектура/ARCHITECTURE.md (α=0)")

    def _create_research_plan_doc(self):
        """Создание RESEARCH-PLAN.md для research проекта"""
        content = """# План исследования
*Уровень абстракции: α=+1 (методология)*
*Статус: ⇓ ВНИЗ (детализация плана)*
*CYCLE: 1*

---

## Исследовательский вопрос

[Сформулируйте главный вопрос исследования]

## Гипотезы

1. [Гипотеза 1]
2. [Гипотеза 2]
3. [Гипотеза 3]

## Методология

[Опишите методологию исследования]

---

**Создано с помощью методологии параллельного двунаправленного развития (⇑⇓↔)**
"""
        path = self.project_dir / "01-Концепция" / "RESEARCH-PLAN.md"
        path.write_text(content, encoding='utf-8')
        print(f"  ✓ 01-Концепция/RESEARCH-PLAN.md (α=+1)")

    def _create_business_plan_doc(self):
        """Создание BUSINESS-PLAN.md для business проекта"""
        content = """# Бизнес-план
*Уровень абстракции: α=+1 (методология)*
*Статус: ⇓ ВНИЗ (детализация стратегии)*
*CYCLE: 1*

---

## Видение

[Опишите видение проекта]

## Миссия

[Опишите миссию]

## Цели

1. [Цель 1]
2. [Цель 2]
3. [Цель 3]

---

**Создано с помощью методологии параллельного двунаправленного развития (⇑⇓↔)**
"""
        path = self.project_dir / "01-Концепция" / "BUSINESS-PLAN.md"
        path.write_text(content, encoding='utf-8')
        print(f"  ✓ 01-Концепция/BUSINESS-PLAN.md (α=+1)")

    def _create_curriculum_doc(self):
        """Создание CURRICULUM.md для education проекта"""
        content = """# Учебная программа
*Уровень абстракции: α=+1 (методология)*
*Статус: ⇓ ВНИЗ (детализация программы)*
*CYCLE: 1*

---

## Цели обучения

1. [Цель 1]
2. [Цель 2]
3. [Цель 3]

## Структура курса

### Модуль 1
[Описание]

### Модуль 2
[Описание]

---

**Создано с помощью методологии параллельного двунаправленного развития (⇑⇓↔)**
"""
        path = self.project_dir / "01-Концепция" / "CURRICULUM.md"
        path.write_text(content, encoding='utf-8')
        print(f"  ✓ 01-Концепция/CURRICULUM.md (α=+1)")

    def _create_legal_framework_doc(self):
        """Создание LEGAL-FRAMEWORK.md для legal проекта"""
        content = """# Правовая основа проекта
*Уровень абстракции: α=+1 (методология)*
*Статус: ⇓ ВНИЗ (детализация правового регулирования)*
*CYCLE: 1*

---

## Юрисдикция

[Укажите применимую юрисдикцию]

## Применимые законы и регуляции

### Закон 1
[Описание]

### Закон 2
[Описание]

## Правовые прецеденты

1. [Дело 1]
2. [Дело 2]

## Нормативная база

### α=+3: Правовые принципы
[Фундаментальные принципы права]

### α=+2: Законодательство
[Кодексы и законы]

### α=+1: Инструкции
[Подзаконные акты]

### α=-1: Шаблоны документов
[Типовые формы]

---

**Создано с помощью методологии параллельного двунаправленного развития (⇑⇓↔)**
"""
        path = self.project_dir / "01-Концепция" / "LEGAL-FRAMEWORK.md"
        path.write_text(content, encoding='utf-8')
        print(f"  ✓ 01-Концепция/LEGAL-FRAMEWORK.md (α=+1)")

    def _create_clinical_protocols_doc(self):
        """Создание CLINICAL-PROTOCOLS.md для healthcare проекта"""
        content = """# Клинические протоколы
*Уровень абстракции: α=-1 (спецификации)*
*Статус: ⇓ ВНИЗ (детализация медицинских процедур)*
*CYCLE: 1*

---

## Иерархия медицинских знаний

### α=+3: Медицинская философия
[Холистический подход, этика, принципы]

### α=+2: Теории болезней
[Патофизиология, этиология]

### α=+1: Клинические принципы
[Диагностика, лечение, профилактика]

### α=0: Диагнозы
[Классификация заболеваний (МКБ-10)]

### α=-1: Протоколы лечения
[Стандартные процедуры]

### α=-2: Шаблоны обследований
[Формы, чек-листы]

### α=-3: Истории болезней
[Конкретные случаи]

### α=-4: Лабораторные данные
[Анализы, показатели]

---

## Основные протоколы

### Протокол 1
[Описание процедуры]

### Протокол 2
[Описание процедуры]

---

**Создано с помощью методологии параллельного двунаправленного развития (⇑⇓↔)**
"""
        path = self.project_dir / "01-Концепция" / "CLINICAL-PROTOCOLS.md"
        path.write_text(content, encoding='utf-8')
        print(f"  ✓ 01-Концепция/CLINICAL-PROTOCOLS.md (α=-1)")

    def _create_creative_vision_doc(self):
        """Создание CREATIVE-VISION.md для arts проекта"""
        content = """# Творческое видение
*Уровень абстракции: α=+3 (философия)*
*Статус: ⇑ ВВЕРХ (создание художественной концепции)*
*CYCLE: 1*

---

## Художественная философия

[Опишите вашу творческую философию и ценности]

## Творческие принципы

1. [Принцип 1]
2. [Принцип 2]
3. [Принцип 3]

## Иерархия творчества

### α=+4: Онтология искусства
[Что такое искусство? Зачем творить?]

### α=+3: Эстетическая философия
[Ваш художественный стиль, ценности]

### α=+2: Творческие концепции
[Темы, мотивы, идеи]

### α=+1: Художественная методология
[Техники, подходы, процессы]

### α=0: Проекты
[Конкретные работы и серии]

### α=-1: Эскизы и наброски
[Предварительные варианты]

### α=-2: Шаблоны и паттерны
[Повторяющиеся элементы]

### α=-3: Портфолио
[Завершённые работы]

### α=-4: Техническое исполнение
[Материалы, инструменты, техника]

---

## Влияния и вдохновение

### Художники-предшественники
[Список влияний]

### Культурный контекст
[Описание контекста]

---

**Создано с помощью методологии параллельного двунаправленного развития (⇑⇓↔)**
"""
        path = self.project_dir / "01-Концепция" / "CREATIVE-VISION.md"
        path.write_text(content, encoding='utf-8')
        print(f"  ✓ 01-Концепция/CREATIVE-VISION.md (α=+3)")

    def _create_methodology_config(self):
        """Создание файла конфигурации методологии"""
        print("\n⚙️  Создание конфигурации методологии...")

        config = {
            "project_name": self.project_name,
            "project_type": self.project_type,
            "created": datetime.now().isoformat(),
            "methodology_version": "⇑⇓↔ v1.0",
            "cycle": 1,
            "metrics_targets": {
                "VT": {"min": 22.0, "max": 44.0},
                "DB": {"max": 30.0},
                "CD": {"min": 16.5, "max": 33.0},
                "CR": {"min": 0.6, "max": 1.3}
            },
            "alpha_levels": {
                "+4": "Онтология",
                "+3": "Философия",
                "+2": "Теория",
                "+1": "Методология",
                "0": "Архитектура",
                "-1": "Спецификации",
                "-2": "Шаблоны",
                "-3": "Примеры",
                "-4": "Реализация"
            }
        }

        config_path = self.project_dir / ".methodology.json"
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

        print(f"  ✓ .methodology.json")

    def _create_tools_directory(self):
        """Создание инструментальной директории с базовыми скриптами"""
        print("\n🛠️  Создание инструментов...")

        tools_dir = self.project_dir / "tools"

        # Копируем health_metrics.py из текущего проекта
        source_health_metrics = Path(__file__).parent / "health_metrics.py"
        if source_health_metrics.exists():
            import shutil
            dest = tools_dir / "health_metrics.py"
            shutil.copy2(source_health_metrics, dest)
            print(f"  ✓ health_metrics.py скопирован")
        else:
            print(f"  ⚠️  health_metrics.py не найден, создайте вручную")

        # Создаем README в tools/
        tools_readme = """# Инструменты методологии ⇑⇓↔

## health_metrics.py
Расчёт метрик здоровья проекта:
- VT (Vertical Traceability)
- DB (Directional Balance)
- CD (Connectivity Density)
- CR (Convergence Rate)

**Использование:**
```bash
python3 health_metrics.py
```

---

**Создано с помощью методологии параллельного двунаправленного развития (⇑⇓↔)**
"""
        (tools_dir / "README.md").write_text(tools_readme, encoding='utf-8')
        print(f"  ✓ tools/README.md")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Генератор шаблонов проектов для методологии ⇑⇓↔",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:

  # Создать software проект
  python3 project_template_generator.py --name my_app --type software

  # Создать research проект
  python3 project_template_generator.py --name phd_research --type research

  # Создать business проект
  python3 project_template_generator.py --name startup --type business

  # Создать education проект
  python3 project_template_generator.py --name online_course --type education

  # Создать legal проект
  python3 project_template_generator.py --name law_firm --type legal

  # Создать healthcare проект
  python3 project_template_generator.py --name clinic_system --type healthcare

  # Создать arts проект
  python3 project_template_generator.py --name art_portfolio --type arts

Доступные типы проектов: software, research, business, education, legal, healthcare, arts
        """
    )

    parser.add_argument(
        '--name',
        required=True,
        help='Название проекта'
    )

    parser.add_argument(
        '--type',
        default='software',
        choices=['software', 'research', 'business', 'education', 'legal', 'healthcare', 'arts'],
        help='Тип проекта (по умолчанию: software)'
    )

    parser.add_argument(
        '--output',
        type=Path,
        default=Path.cwd(),
        help='Директория для создания проекта (по умолчанию: текущая)'
    )

    parser.add_argument(
        '--interactive',
        action='store_true',
        help='Интерактивный режим с вопросами'
    )

    args = parser.parse_args()

    generator = ProjectTemplateGenerator(
        project_name=args.name,
        project_type=args.type,
        output_dir=args.output
    )

    generator.generate(interactive=args.interactive)


if __name__ == "__main__":
    main()
