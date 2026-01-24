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
        },
        "finance": {
            "name": "Finance Project",
            "description": "Финансовый проект",
            "alpha_focus": "α=-3..+2",
            "key_docs": ["README.md", "FINANCIAL-STRATEGY.md", "PORTFOLIO-MANAGEMENT.md"]
        },
        "government": {
            "name": "Government Project",
            "description": "Проект государственного управления",
            "alpha_focus": "α=-1..+3",
            "key_docs": ["README.md", "PUBLIC-POLICY.md", "GOVERNANCE-FRAMEWORK.md"]
        },
        "nonprofit": {
            "name": "Nonprofit Project",
            "description": "Проект некоммерческой организации",
            "alpha_focus": "α=-1..+3",
            "key_docs": ["README.md", "MISSION-IMPACT.md", "FUNDRAISING.md"]
        },
        "manufacturing": {
            "name": "Manufacturing Project",
            "description": "Производственный проект",
            "alpha_focus": "α=-4..+2",
            "key_docs": ["README.md", "PRODUCTION-PROCESS.md", "QUALITY-CONTROL.md"]
        },
        "agriculture": {
            "name": "Agriculture Project",
            "description": "Сельскохозяйственный проект",
            "alpha_focus": "α=-3..+2",
            "key_docs": ["README.md", "CROP-MANAGEMENT.md", "SUSTAINABILITY.md"]
        },
        "sports": {
            "name": "Sports Project",
            "description": "Спортивный проект",
            "alpha_focus": "α=-3..+3",
            "key_docs": ["README.md", "TRAINING-PROGRAM.md", "PERFORMANCE-METRICS.md"]
        },
        "hospitality": {
            "name": "Hospitality & Tourism Project",
            "description": "Проект гостеприимства и туризма",
            "alpha_focus": "α=-2..+2",
            "key_docs": ["README.md", "SERVICE-STANDARDS.md", "GUEST-EXPERIENCE.md"]
        },
        "retail": {
            "name": "Retail Project",
            "description": "Проект розничной торговли",
            "alpha_focus": "α=-3..+1",
            "key_docs": ["README.md", "RETAIL-STRATEGY.md", "CUSTOMER-JOURNEY.md"]
        },
        "hobby": {
            "name": "Hobby & Personal Project",
            "description": "Проект хобби/увлечений (универсальный шаблон)",
            "alpha_focus": "α=-3..+3",
            "key_docs": ["README.md", "PROJECT-VISION.md", "LEARNING-LOG.md"]
        }
    }

    def __init__(self, project_name: str, project_type: str = "software",
                 output_dir: Optional[Path] = None):
        """
        Инициализация генератора

        Args:
            project_name: Имя проекта
            project_type: Тип проекта (software/research/business/education/legal/healthcare/arts/
                         finance/government/nonprofit/manufacturing/agriculture/sports/hospitality/retail/hobby)
            output_dir: Директория для создания проекта (по умолчанию текущая)
        """
        self.project_name = project_name
        self.project_type = project_type
        self.output_dir = output_dir or Path.cwd()
        self.project_dir = self.output_dir / project_name

        if project_type not in self.PROJECT_TYPES:
            raise ValueError(f"Неизвестный тип проекта: {project_type}. "
                           f"Доступные: {', '.join(self.PROJECT_TYPES.keys())}")

    def generate(self, interactive: bool = False, init_git: bool = False, create_github_repo: bool = False,
                 setup_ci: bool = False, setup_security: bool = False, setup_quality: bool = False,
                 setup_deploy: bool = False):
        """
        Генерация структуры проекта

        Args:
            interactive: Интерактивный режим с вопросами
            init_git: Инициализировать git репозиторий
            create_github_repo: Создать GitHub репозиторий (требует gh CLI)
            setup_ci: Настроить CI/CD (GitHub Actions workflows)
            setup_security: Добавить security scanning workflows
            setup_quality: Добавить code quality workflows
            setup_deploy: Добавить deployment workflows
        """
        # Интерактивный режим: задать вопросы пользователю
        if interactive:
            self._interactive_project_setup()
            # Обновляем параметры из интерактивного режима
            if hasattr(self, '_init_git'):
                init_git = self._init_git
            if hasattr(self, '_create_github'):
                create_github_repo = self._create_github
            if hasattr(self, '_setup_ci'):
                setup_ci = self._setup_ci
            if hasattr(self, '_setup_security'):
                setup_security = self._setup_security
            if hasattr(self, '_setup_quality'):
                setup_quality = self._setup_quality
            if hasattr(self, '_setup_deploy'):
                setup_deploy = self._setup_deploy

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

        # 5. Git/GitHub интеграция (если запрошено)
        if init_git or create_github_repo:
            self._setup_git_integration(init_git=init_git, create_github=create_github_repo)

        # 6. CI/CD интеграция (если запрошено)
        if setup_ci or setup_security or setup_quality or setup_deploy:
            self._setup_cicd_integration(
                include_basic=setup_ci,
                include_security=setup_security,
                include_quality=setup_quality,
                include_deploy=setup_deploy
            )

        print("\n✅ Проект успешно создан!")
        print(f"\nСледующие шаги:")
        print(f"  1. cd {self.project_name}")
        print(f"  2. Отредактируйте README.md с описанием проекта")
        print(f"  3. Запустите: python3 tools/health_metrics.py")
        if setup_ci or setup_security or setup_quality or setup_deploy:
            print(f"  4. Проверьте GitHub Actions workflows в .github/workflows/")
            if setup_security:
                print(f"  5. Настройте security scanning в GitHub Security settings")
            if setup_deploy:
                print(f"  6. Настройте deployment secrets и environments в GitHub")
            print(f"  7. Начните развивать проект по методологии ⇑⇓↔\n")
        else:
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
        elif self.project_type == "finance":
            dirs.extend(["portfolios", "analysis", "reports"])
        elif self.project_type == "government":
            dirs.extend(["policies", "programs", "regulations"])
        elif self.project_type == "nonprofit":
            dirs.extend(["programs", "campaigns", "grants"])
        elif self.project_type == "manufacturing":
            dirs.extend(["production", "quality", "inventory"])
        elif self.project_type == "agriculture":
            dirs.extend(["crops", "livestock", "equipment"])
        elif self.project_type == "sports":
            dirs.extend(["training", "events", "analytics"])
        elif self.project_type == "hospitality":
            dirs.extend(["services", "facilities", "events"])
        elif self.project_type == "retail":
            dirs.extend(["products", "inventory", "marketing"])
        elif self.project_type == "hobby":
            dirs.extend(["projects", "resources", "notes"])

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
        elif self.project_type == "finance":
            self._create_financial_strategy_doc()
        elif self.project_type == "government":
            self._create_public_policy_doc()
        elif self.project_type == "nonprofit":
            self._create_mission_impact_doc()
        elif self.project_type == "manufacturing":
            self._create_production_process_doc()
        elif self.project_type == "agriculture":
            self._create_crop_management_doc()
        elif self.project_type == "sports":
            self._create_training_program_doc()
        elif self.project_type == "hospitality":
            self._create_service_standards_doc()
        elif self.project_type == "retail":
            self._create_retail_strategy_doc()
        elif self.project_type == "hobby":
            self._create_project_vision_doc()

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

    def _create_financial_strategy_doc(self):
        """Создание FINANCIAL-STRATEGY.md для finance проекта"""
        content = """# Финансовая стратегия
*Уровень абстракции: α=+1 (методология)*
*Статус: ⇓ ВНИЗ (детализация финансовой стратегии)*
*CYCLE: 1*

---

## Финансовая философия

[Опишите базовые принципы управления финансами]

## Иерархия финансовых решений

### α=+2: Финансовая теория
[Теории инвестирования, управления рисками]

### α=+1: Финансовая стратегия
[Долгосрочные цели, allocation принципы]

### α=0: Портфели
[Структура активов]

### α=-1: Инструменты
[Акции, облигации, деривативы]

### α=-2: Транзакции
[Конкретные сделки]

### α=-3: Рыночные данные
[Котировки, показатели]

---

## Основные стратегии

### Стратегия 1
[Описание]

### Стратегия 2
[Описание]

---

**Создано с помощью методологии параллельного двунаправленного развития (⇑⇓↔)**
"""
        path = self.project_dir / "01-Концепция" / "FINANCIAL-STRATEGY.md"
        path.write_text(content, encoding='utf-8')
        print(f"  ✓ 01-Концепция/FINANCIAL-STRATEGY.md (α=+1)")

    def _create_public_policy_doc(self):
        """Создание PUBLIC-POLICY.md для government проекта"""
        content = """# Публичная политика
*Уровень абстракции: α=+2 (теория)*
*Статус: ⇓ ВНИЗ (детализация государственной политики)*
*CYCLE: 1*

---

## Политическая философия

[Опишите принципы государственного управления]

## Иерархия политических решений

### α=+3: Конституционные принципы
[Основы государственности, права человека]

### α=+2: Публичная политика
[Направления государственной политики]

### α=+1: Законодательство
[Законы, постановления]

### α=0: Программы
[Государственные программы]

### α=-1: Регламенты
[Процедуры, инструкции]

### α=-2: Услуги
[Конкретные государственные услуги]

---

## Ключевые направления

### Направление 1
[Описание]

### Направление 2
[Описание]

---

**Создано с помощью методологии параллельного двунаправленного развития (⇑⇓↔)**
"""
        path = self.project_dir / "01-Концепция" / "PUBLIC-POLICY.md"
        path.write_text(content, encoding='utf-8')
        print(f"  ✓ 01-Концепция/PUBLIC-POLICY.md (α=+2)")

    def _create_mission_impact_doc(self):
        """Создание MISSION-IMPACT.md для nonprofit проекта"""
        content = """# Миссия и социальное воздействие
*Уровень абстракции: α=+3 (философия)*
*Статус: ⇑ ВВЕРХ (создание социальной миссии)*
*CYCLE: 1*

---

## Социальная миссия

[Опишите миссию организации]

## Иерархия социального воздействия

### α=+3: Ценности и философия
[Базовые ценности организации]

### α=+2: Теория изменений
[Как организация создаёт перемены]

### α=+1: Стратегия воздействия
[Направления деятельности]

### α=0: Программы
[Конкретные программы]

### α=-1: Проекты
[Отдельные проекты]

### α=-2: Мероприятия
[События, активности]

### α=-3: Благополучатели
[Конкретные истории помощи]

---

## Ключевые программы

### Программа 1
[Описание]

### Программа 2
[Описание]

---

## Метрики воздействия

[Как измеряется социальный эффект]

---

**Создано с помощью методологии параллельного двунаправленного развития (⇑⇓↔)**
"""
        path = self.project_dir / "01-Концепция" / "MISSION-IMPACT.md"
        path.write_text(content, encoding='utf-8')
        print(f"  ✓ 01-Концепция/MISSION-IMPACT.md (α=+3)")

    def _create_production_process_doc(self):
        """Создание PRODUCTION-PROCESS.md для manufacturing проекта"""
        content = """# Производственный процесс
*Уровень абстракции: α=-1 (спецификации)*
*Статус: ⇓ ВНИЗ (детализация производственных процессов)*
*CYCLE: 1*

---

## Производственная философия

[Lean, Six Sigma, другие подходы]

## Иерархия производства

### α=+2: Производственная стратегия
[Стратегические цели производства]

### α=+1: Производственная система
[Общая организация производства]

### α=0: Производственные линии
[Основные линии]

### α=-1: Процессы
[Технологические процессы]

### α=-2: Операции
[Отдельные операции]

### α=-3: Инструкции
[Рабочие инструкции]

### α=-4: Параметры оборудования
[Настройки станков, режимы]

---

## Основные процессы

### Процесс 1
[Описание]

### Процесс 2
[Описание]

---

## Контроль качества

[Методы и стандарты]

---

**Создано с помощью методологии параллельного двунаправленного развития (⇑⇓↔)**
"""
        path = self.project_dir / "01-Концепция" / "PRODUCTION-PROCESS.md"
        path.write_text(content, encoding='utf-8')
        print(f"  ✓ 01-Концепция/PRODUCTION-PROCESS.md (α=-1)")

    def _create_crop_management_doc(self):
        """Создание CROP-MANAGEMENT.md для agriculture проекта"""
        content = """# Управление сельскохозяйственным производством
*Уровень абстракции: α=0 (концепция)*
*Статус: ⇓ ВНИЗ (детализация агротехнологий)*
*CYCLE: 1*

---

## Агрономическая философия

[Органическое/традиционное земледелие, sustainable agriculture]

## Иерархия сельского хозяйства

### α=+2: Агрономическая наука
[Теории почвоведения, растениеводства]

### α=+1: Системы земледелия
[Севооборот, системы обработки]

### α=0: Культуры
[Выращиваемые культуры]

### α=-1: Технологические карты
[Агротехнологии для каждой культуры]

### α=-2: Полевые работы
[Посев, уход, уборка]

### α=-3: Данные полей
[Урожайность, показатели]

---

## Основные культуры

### Культура 1
[Описание]

### Культура 2
[Описание]

---

## Устойчивость и экология

[Принципы устойчивого земледелия]

---

**Создано с помощью методологии параллельного двунаправленного развития (⇑⇓↔)**
"""
        path = self.project_dir / "01-Концепция" / "CROP-MANAGEMENT.md"
        path.write_text(content, encoding='utf-8')
        print(f"  ✓ 01-Концепция/CROP-MANAGEMENT.md (α=0)")

    def _create_training_program_doc(self):
        """Создание TRAINING-PROGRAM.md для sports проекта"""
        content = """# Тренировочная программа
*Уровень абстракции: α=+1 (методология)*
*Статус: ⇓ ВНИЗ (детализация тренировочного процесса)*
*CYCLE: 1*

---

## Философия тренировок

[Спортивная философия, принципы]

## Иерархия спортивной подготовки

### α=+3: Спортивная философия
[Олимпийские ценности, этика спорта]

### α=+2: Теория спорта
[Физиология, биомеханика]

### α=+1: Методология тренировок
[Системы подготовки]

### α=0: Тренировочные планы
[Макроциклы, мезоциклы]

### α=-1: Тренировочные занятия
[Отдельные тренировки]

### α=-2: Упражнения
[Конкретные упражнения]

### α=-3: Показатели
[Результаты, метрики]

---

## Основные направления подготовки

### Физическая подготовка
[Описание]

### Техническая подготовка
[Описание]

### Тактическая подготовка
[Описание]

### Психологическая подготовка
[Описание]

---

**Создано с помощью методологии параллельного двунаправленного развития (⇑⇓↔)**
"""
        path = self.project_dir / "01-Концепция" / "TRAINING-PROGRAM.md"
        path.write_text(content, encoding='utf-8')
        print(f"  ✓ 01-Концепция/TRAINING-PROGRAM.md (α=+1)")

    def _create_service_standards_doc(self):
        """Создание SERVICE-STANDARDS.md для hospitality проекта"""
        content = """# Стандарты обслуживания
*Уровень абстракции: α=-1 (спецификации)*
*Статус: ⇓ ВНИЗ (детализация стандартов сервиса)*
*CYCLE: 1*

---

## Философия гостеприимства

[Принципы работы с гостями]

## Иерархия сервиса

### α=+2: Культура гостеприимства
[Философия и ценности]

### α=+1: Концепция сервиса
[Общий подход к обслуживанию]

### α=0: Сервисные модули
[Регистрация, питание, размещение]

### α=-1: Стандарты
[Детальные стандарты обслуживания]

### α=-2: Процедуры
[Пошаговые инструкции]

### α=-3: Взаимодействия
[Конкретные сценарии с гостями]

---

## Ключевые стандарты

### Стандарт 1
[Описание]

### Стандарт 2
[Описание]

---

## Качество обслуживания

[Метрики удовлетворённости гостей]

---

**Создано с помощью методологии параллельного двунаправленного развития (⇑⇓↔)**
"""
        path = self.project_dir / "01-Концепция" / "SERVICE-STANDARDS.md"
        path.write_text(content, encoding='utf-8')
        print(f"  ✓ 01-Концепция/SERVICE-STANDARDS.md (α=-1)")

    def _create_retail_strategy_doc(self):
        """Создание RETAIL-STRATEGY.md для retail проекта"""
        content = """# Стратегия розничной торговли
*Уровень абстракции: α=+1 (методология)*
*Статус: ⇓ ВНИЗ (детализация торговой стратегии)*
*CYCLE: 1*

---

## Торговая философия

[Клиентоориентированность, ценностное предложение]

## Иерархия розничной торговли

### α=+1: Торговая стратегия
[Позиционирование, целевая аудитория]

### α=0: Форматы магазинов
[Типы точек продаж]

### α=-1: Ассортимент
[Товарные категории]

### α=-2: SKU
[Конкретные товары]

### α=-3: Транзакции
[Продажи, чеки]

---

## Customer Journey

### Этап 1: Привлечение
[Описание]

### Этап 2: Вовлечение
[Описание]

### Этап 3: Покупка
[Описание]

### Этап 4: Удержание
[Описание]

---

## Merchandising

[Принципы выкладки и презентации товара]

---

**Создано с помощью методологии параллельного двунаправленного развития (⇑⇓↔)**
"""
        path = self.project_dir / "01-Концепция" / "RETAIL-STRATEGY.md"
        path.write_text(content, encoding='utf-8')
        print(f"  ✓ 01-Концепция/RETAIL-STRATEGY.md (α=+1)")

    def _create_project_vision_doc(self):
        """Создание PROJECT-VISION.md для hobby проекта (универсальный шаблон)"""
        content = """# Видение проекта
*Уровень абстракции: α=+2 (теория)*
*Статус: ⇑ ВВЕРХ (создание концепции проекта)*
*CYCLE: 1*

---

## О проекте

[Опишите суть вашего хобби/увлечения]

## Философия и мотивация

### Почему это важно?
[Ваша мотивация]

### Какие ценности?
[Ценности, которые вы разделяете]

## Иерархия знаний

### α=+3: Философия домена
[Фундаментальные принципы вашей области]

### α=+2: Теория и концепции
[Основные теории, которые вы изучаете]

### α=+1: Методологии и подходы
[Методы и техники]

### α=0: Проекты
[Ваши конкретные проекты]

### α=-1: Задачи
[Детальные задачи]

### α=-2: Эксперименты
[Что вы пробуете]

### α=-3: Заметки и наблюдения
[Ваши записи]

---

## Цели и планы

### Краткосрочные цели (1-3 месяца)
1. [Цель 1]
2. [Цель 2]

### Долгосрочные цели (год+)
1. [Цель 1]
2. [Цель 2]

---

## Ресурсы

### Обучающие материалы
- [Книги, курсы, статьи]

### Инструменты
- [Что используете]

### Сообщество
- [Где общаетесь с единомышленниками]

---

## Прогресс

[Отслеживайте свой прогресс здесь]

---

**Создано с помощью методологии параллельного двунаправленного развития (⇑⇓↔)**

**ПРИМЕЧАНИЕ:** Это универсальный шаблон для хобби и увлечений.
Адаптируйте его под свой конкретный домен: фотография, музыка,
программирование, моделирование, кулинария, садоводство и т.д.
"""
        path = self.project_dir / "01-Концепция" / "PROJECT-VISION.md"
        path.write_text(content, encoding='utf-8')
        print(f"  ✓ 01-Концепция/PROJECT-VISION.md (α=+2)")

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

    def _interactive_project_setup(self):
        """Интерактивный режим: задать вопросы пользователю"""
        print("\n🤖 Интерактивный режим настройки проекта\n")
        print("=" * 60)

        # 1. Подтверждение типа проекта или выбор нового
        print(f"\nВыбран тип проекта: {self.PROJECT_TYPES[self.project_type]['name']}")
        print(f"Описание: {self.PROJECT_TYPES[self.project_type]['description']}")
        print(f"Фокус α-уровней: {self.PROJECT_TYPES[self.project_type]['alpha_focus']}")

        change_type = input("\nИзменить тип проекта? (y/N): ").strip().lower()

        if change_type == 'y':
            print("\nДоступные типы проектов:\n")
            types_list = list(self.PROJECT_TYPES.keys())
            for idx, ptype in enumerate(types_list, 1):
                info = self.PROJECT_TYPES[ptype]
                print(f"  {idx:2d}. {ptype:15s} - {info['description']}")

            while True:
                try:
                    choice = input(f"\nВыберите тип (1-{len(types_list)}): ").strip()
                    choice_idx = int(choice) - 1
                    if 0 <= choice_idx < len(types_list):
                        self.project_type = types_list[choice_idx]
                        print(f"✓ Выбран тип: {self.PROJECT_TYPES[self.project_type]['name']}")
                        break
                    else:
                        print(f"Пожалуйста, введите число от 1 до {len(types_list)}")
                except ValueError:
                    print("Пожалуйста, введите число")

        # 2. Дополнительная настройка проекта
        print("\n" + "=" * 60)
        print("\n📋 Дополнительные параметры\n")

        # 3. Git интеграция
        init_git = input("Инициализировать Git репозиторий? (Y/n): ").strip().lower()
        self._init_git = init_git != 'n'

        if self._init_git:
            create_github = input("Создать GitHub репозиторий? (требует gh CLI) (y/N): ").strip().lower()
            self._create_github = create_github == 'y'

            if self._create_github:
                self._github_visibility = input("  Visibility (public/private) [private]: ").strip() or "private"
                self._github_description = input(f"  Описание репозитория [{self.project_name}]: ").strip() or self.project_name
        else:
            self._create_github = False

        # 4. CI/CD интеграция
        setup_ci = input("Настроить базовые CI/CD workflows? (y/N): ").strip().lower()
        self._setup_ci = setup_ci == 'y'

        if self._setup_ci:
            print("  ℹ️  Базовые workflows: methodology check, documentation check, тестирование")

        # 4.1. Расширенные CI/CD опции (v0.5)
        setup_security = input("Добавить security scanning workflows? (Trivy, SAST) (y/N): ").strip().lower()
        self._setup_security = setup_security == 'y'

        if self._setup_security:
            print("  ℹ️  Security: уязвимости, secrets detection, SAST, license compliance")

        setup_quality = input("Добавить code quality workflows? (linting, coverage) (y/N): ").strip().lower()
        self._setup_quality = setup_quality == 'y'

        if self._setup_quality:
            print("  ℹ️  Quality: code analysis, coverage, complexity, documentation quality")

        setup_deploy = input("Добавить deployment workflows? (Docker, staging, production) (y/N): ").strip().lower()
        self._setup_deploy = setup_deploy == 'y'

        if self._setup_deploy:
            print("  ℹ️  Deployment: Docker images, staging/production deploy, rollback")

        # 5. Подтверждение
        print("\n" + "=" * 60)
        print("\n📦 Итоговая конфигурация:\n")
        print(f"  Название:     {self.project_name}")
        print(f"  Тип:          {self.PROJECT_TYPES[self.project_type]['name']}")
        print(f"  Директория:   {self.project_dir}")
        print(f"  Git init:     {'Да' if self._init_git else 'Нет'}")
        if self._init_git and self._create_github:
            print(f"  GitHub repo:  Да ({self._github_visibility})")
        print(f"  CI/CD:        {'Да' if self._setup_ci else 'Нет'}")
        if hasattr(self, '_setup_security') and self._setup_security:
            print(f"  Security:     Да")
        if hasattr(self, '_setup_quality') and self._setup_quality:
            print(f"  Quality:      Да")
        if hasattr(self, '_setup_deploy') and self._setup_deploy:
            print(f"  Deployment:   Да")
        print()

        confirm = input("Продолжить создание проекта? (Y/n): ").strip().lower()
        if confirm == 'n':
            print("\n❌ Создание проекта отменено")
            exit(0)

        print("\n" + "=" * 60 + "\n")

    def _setup_git_integration(self, init_git: bool = True, create_github: bool = False):
        """Настройка Git/GitHub интеграции"""
        import subprocess
        import os

        original_dir = os.getcwd()

        try:
            os.chdir(self.project_dir)

            if init_git:
                print("\n🔧 Настройка Git...")

                # Инициализация git
                result = subprocess.run(['git', 'init'], capture_output=True, text=True)
                if result.returncode == 0:
                    print("  ✓ Git репозиторий инициализирован")

                    # Создание .gitignore
                    gitignore_content = """# Методология ⇑⇓↔
__pycache__/
*.pyc
.DS_Store
.vscode/
.idea/

# Временные файлы
*.tmp
*.log
.cache/

# Виртуальное окружение
venv/
env/
"""
                    with open('.gitignore', 'w') as f:
                        f.write(gitignore_content)
                    print("  ✓ .gitignore создан")

                    # Первый коммит
                    subprocess.run(['git', 'add', '.'], capture_output=True)
                    commit_msg = f"Initial commit: {self.PROJECT_TYPES[self.project_type]['name']}\n\nСоздано с помощью методологии ⇑⇓↔"
                    result = subprocess.run(['git', 'commit', '--no-gpg-sign', '-m', commit_msg], capture_output=True, text=True)
                    if result.returncode == 0:
                        print("  ✓ Начальный коммит создан")
                    else:
                        print(f"  ⚠️  Ошибка создания коммита: {result.stderr}")
                else:
                    print(f"  ⚠️  Ошибка инициализации git: {result.stderr}")

            if create_github:
                print("\n🐙 Создание GitHub репозитория...")

                # Проверка наличия gh CLI
                gh_check = subprocess.run(['gh', '--version'], capture_output=True)
                if gh_check.returncode != 0:
                    print("  ⚠️  gh CLI не установлен. Пропускаем создание GitHub репозитория")
                    print("     Установите: https://cli.github.com/")
                else:
                    # Получение параметров из интерактивного режима или использование значений по умолчанию
                    visibility = getattr(self, '_github_visibility', 'private')
                    description = getattr(self, '_github_description', self.project_name)

                    gh_cmd = [
                        'gh', 'repo', 'create', self.project_name,
                        f'--{visibility}',
                        '--source=.',
                        '--push',
                        f'--description={description}'
                    ]

                    result = subprocess.run(gh_cmd, capture_output=True, text=True)
                    if result.returncode == 0:
                        print(f"  ✓ GitHub репозиторий создан ({visibility})")
                        print(f"  ✓ Код запушен в GitHub")
                    else:
                        print(f"  ⚠️  Ошибка создания GitHub репозитория:")
                        print(f"     {result.stderr}")

        finally:
            os.chdir(original_dir)

    def _setup_cicd_integration(self, include_basic: bool = True, include_security: bool = False,
                                include_quality: bool = False, include_deploy: bool = False):
        """Настройка CI/CD (GitHub Actions workflows)"""
        print("\n⚙️  Настройка CI/CD...")

        # Создаем .github/workflows директорию
        workflows_dir = self.project_dir / ".github" / "workflows"
        workflows_dir.mkdir(parents=True, exist_ok=True)
        print(f"  ✓ Создана директория .github/workflows/")

        # Определяем, какие workflows нужны для этого типа проекта
        workflows_to_copy = self._get_cicd_workflows_for_type(
            include_basic=include_basic,
            include_security=include_security,
            include_quality=include_quality,
            include_deploy=include_deploy
        )

        # Путь к CI шаблонам
        ci_templates_dir = Path(__file__).parent / "ci_templates"

        copied_count = 0
        for workflow_file in workflows_to_copy:
            source = ci_templates_dir / workflow_file
            dest = workflows_dir / workflow_file

            if source.exists():
                import shutil
                shutil.copy2(source, dest)
                print(f"  ✓ {workflow_file}")
                copied_count += 1
            else:
                print(f"  ⚠️  Шаблон {workflow_file} не найден")

        if copied_count > 0:
            print(f"\n✅ Настроено {copied_count} CI/CD workflow(s)")
            print(f"   Workflows будут запускаться автоматически при push/PR")
        else:
            print(f"  ⚠️  Не удалось скопировать workflows")

    def _get_cicd_workflows_for_type(self, include_basic: bool = True, include_security: bool = False,
                                     include_quality: bool = False, include_deploy: bool = False) -> list:
        """Определяет, какие CI/CD workflows нужны для типа проекта"""

        workflows = []

        # Базовые workflows (если запрошены)
        if include_basic:
            # Универсальные workflows для всех типов
            workflows.extend([
                "methodology_check.yml",
                "documentation_check.yml"
            ])

            # Специфичные workflows для типов проектов
            if self.project_type == "software":
                workflows.append("software_ci.yml")
            elif self.project_type == "research":
                workflows.append("research_ci.yml")

        # Security scanning workflows (v0.5)
        if include_security:
            workflows.append("security_scan.yml")

        # Code quality workflows (v0.5)
        if include_quality:
            workflows.append("code_quality.yml")

        # Deployment workflows (v0.5)
        if include_deploy:
            workflows.append("deployment.yml")

        return workflows


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

  # v0.3: Новые типы проектов

  # Создать finance проект
  python3 project_template_generator.py --name investment_fund --type finance

  # Создать government проект
  python3 project_template_generator.py --name public_service --type government

  # Создать nonprofit проект
  python3 project_template_generator.py --name charity_org --type nonprofit

  # Создать manufacturing проект
  python3 project_template_generator.py --name factory --type manufacturing

  # Создать agriculture проект
  python3 project_template_generator.py --name farm --type agriculture

  # Создать sports проект
  python3 project_template_generator.py --name athletics_team --type sports

  # Создать hospitality проект
  python3 project_template_generator.py --name hotel --type hospitality

  # Создать retail проект
  python3 project_template_generator.py --name store_chain --type retail

  # Создать hobby проект (универсальный шаблон)
  python3 project_template_generator.py --name photography --type hobby

  # v0.3: Интерактивный режим и Git/GitHub интеграция

  # Интерактивный режим
  python3 project_template_generator.py --name my_project --type software --interactive

  # С Git инициализацией
  python3 project_template_generator.py --name my_app --type software --git

  # С созданием GitHub репозитория (приватного)
  python3 project_template_generator.py --name startup --type business --github

  # С созданием публичного GitHub репозитория
  python3 project_template_generator.py --name open_source --type software --github --github-visibility public

Доступные типы: software, research, business, education, legal, healthcare, arts,
                finance, government, nonprofit, manufacturing, agriculture, sports,
                hospitality, retail, hobby (универсальный)
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
        choices=['software', 'research', 'business', 'education', 'legal', 'healthcare', 'arts',
                'finance', 'government', 'nonprofit', 'manufacturing', 'agriculture', 'sports',
                'hospitality', 'retail', 'hobby'],
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

    parser.add_argument(
        '--git',
        action='store_true',
        help='Инициализировать Git репозиторий'
    )

    parser.add_argument(
        '--github',
        action='store_true',
        help='Создать GitHub репозиторий (требует gh CLI и --git)'
    )

    parser.add_argument(
        '--github-visibility',
        choices=['public', 'private'],
        default='private',
        help='Visibility GitHub репозитория (по умолчанию: private)'
    )

    parser.add_argument(
        '--ci',
        '--cicd',
        action='store_true',
        dest='ci',
        help='Настроить базовые CI/CD workflows (methodology, documentation, testing)'
    )

    parser.add_argument(
        '--security',
        action='store_true',
        help='Добавить security scanning workflows (Trivy, SAST, secrets detection)'
    )

    parser.add_argument(
        '--quality',
        action='store_true',
        help='Добавить code quality workflows (linting, coverage, complexity)'
    )

    parser.add_argument(
        '--deploy',
        action='store_true',
        help='Добавить deployment workflows (Docker, staging, production)'
    )

    parser.add_argument(
        '--ci-all',
        action='store_true',
        help='Включить все CI/CD workflows (--ci --security --quality --deploy)'
    )

    args = parser.parse_args()

    # Если --ci-all указан, включить все CI/CD опции
    if args.ci_all:
        args.ci = True
        args.security = True
        args.quality = True
        args.deploy = True

    # Если --github указан, автоматически включить --git
    if args.github:
        args.git = True

    generator = ProjectTemplateGenerator(
        project_name=args.name,
        project_type=args.type,
        output_dir=args.output
    )

    # Если используется GitHub, сохранить параметры
    if args.github:
        generator._github_visibility = args.github_visibility
        generator._github_description = args.name

    generator.generate(
        interactive=args.interactive,
        init_git=args.git,
        create_github_repo=args.github,
        setup_ci=args.ci,
        setup_security=args.security,
        setup_quality=args.quality,
        setup_deploy=args.deploy
    )


if __name__ == "__main__":
    main()
