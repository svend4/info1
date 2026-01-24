# Шаблоны документации для проектов методологии ⇑⇓↔
*Уровень абстракции: α=-1 (инструментарий)*
*Статус: ↔ ГОРИЗОНТ (коллекция шаблонов)*
*CYCLE: 1*

---

## Обзор

Эта директория содержит расширенные шаблоны документации для каждого из 16 типов проектов, поддерживаемых генератором `project_template_generator.py`.

**Версия:** v0.7 (Фаза 0.8 — ЭТАП 8)

---

## Структура

```
templates/
├── README.md (этот файл)
├── software/          # Шаблоны для software проектов
│   ├── ARCHITECTURE-TEMPLATE.md
│   ├── API-DESIGN-TEMPLATE.md
│   ├── TESTING-STRATEGY-TEMPLATE.md
│   ├── DEPLOYMENT-GUIDE-TEMPLATE.md
│   └── CONTRIBUTING-TEMPLATE.md
├── research/          # Шаблоны для научных исследований
│   ├── RESEARCH-PROTOCOL-TEMPLATE.md
│   ├── DATA-ANALYSIS-PLAN-TEMPLATE.md
│   ├── LITERATURE-REVIEW-TEMPLATE.md
│   └── ETHICS-SUBMISSION-TEMPLATE.md
├── business/          # Шаблоны для бизнес-проектов
│   ├── BUSINESS-PLAN-TEMPLATE.md
│   ├── MARKETING-STRATEGY-TEMPLATE.md
│   ├── FINANCIAL-MODEL-TEMPLATE.xlsx
│   └── INVESTOR-DECK-TEMPLATE.md
├── education/         # Шаблоны для образовательных проектов
│   ├── CURRICULUM-DESIGN-TEMPLATE.md
│   ├── LESSON-PLAN-TEMPLATE.md
│   ├── ASSESSMENT-RUBRIC-TEMPLATE.md
│   └── LEARNING-OBJECTIVES-TEMPLATE.md
├── legal/             # Шаблоны для юридических проектов
│   ├── CASE-BRIEF-TEMPLATE.md
│   ├── LEGAL-MEMORANDUM-TEMPLATE.md
│   └── CONTRACT-TEMPLATE.md
├── healthcare/        # Шаблоны для медицинских проектов
│   ├── CLINICAL-PROTOCOL-TEMPLATE.md
│   ├── PATIENT-CARE-PLAN-TEMPLATE.md
│   └── QUALITY-IMPROVEMENT-TEMPLATE.md
├── arts/              # Шаблоны для творческих проектов
│   ├── CREATIVE-BRIEF-TEMPLATE.md
│   ├── PORTFOLIO-STRUCTURE-TEMPLATE.md
│   └── EXHIBITION-PROPOSAL-TEMPLATE.md
├── finance/           # Шаблоны для финансовых проектов
│   ├── INVESTMENT-THESIS-TEMPLATE.md
│   ├── PORTFOLIO-ANALYSIS-TEMPLATE.md
│   └── RISK-ASSESSMENT-TEMPLATE.md
├── government/        # Шаблоны для госпроектов
│   ├── POLICY-PROPOSAL-TEMPLATE.md
│   ├── PUBLIC-CONSULTATION-TEMPLATE.md
│   └── IMPACT-ASSESSMENT-TEMPLATE.md
├── nonprofit/         # Шаблоны для НКО
│   ├── GRANT-PROPOSAL-TEMPLATE.md
│   ├── IMPACT-REPORT-TEMPLATE.md
│   └── VOLUNTEER-PROGRAM-TEMPLATE.md
├── manufacturing/     # Шаблоны для производства
│   ├── PRODUCTION-PLAN-TEMPLATE.md
│   ├── QUALITY-CONTROL-TEMPLATE.md
│   └── SUPPLY-CHAIN-TEMPLATE.md
├── agriculture/       # Шаблоны для сельского хозяйства
│   ├── CROP-PLAN-TEMPLATE.md
│   ├── SUSTAINABILITY-PLAN-TEMPLATE.md
│   └── FARM-MANAGEMENT-TEMPLATE.md
├── sports/            # Шаблоны для спортивных проектов
│   ├── TRAINING-PROGRAM-TEMPLATE.md
│   ├── ATHLETE-DEVELOPMENT-TEMPLATE.md
│   └── COMPETITION-PLAN-TEMPLATE.md
├── hospitality/       # Шаблоны для гостеприимства
│   ├── SERVICE-STANDARDS-TEMPLATE.md
│   ├── MENU-DESIGN-TEMPLATE.md
│   └── GUEST-EXPERIENCE-TEMPLATE.md
├── retail/            # Шаблоны для розничной торговли
│   ├── MERCHANDISING-PLAN-TEMPLATE.md
│   ├── CUSTOMER-JOURNEY-TEMPLATE.md
│   └── INVENTORY-MANAGEMENT-TEMPLATE.md
└── hobby/             # Универсальные шаблоны
    ├── PROJECT-ROADMAP-TEMPLATE.md
    ├── LEARNING-LOG-TEMPLATE.md
    └── DOCUMENTATION-GUIDE-TEMPLATE.md
```

---

## Использование шаблонов

### Автоматическое использование

Генератор проектов автоматически копирует релевантные шаблоны при создании проекта:

```bash
# Создать software проект с расширенными шаблонами
python3 tools/project_template_generator.py --name my_app --type software --templates

# Создать research проект с шаблонами
python3 tools/project_template_generator.py --name my_study --type research --templates

# Создать business проект с шаблонами
python3 tools/project_template_generator.py --name my_startup --type business --templates
```

**Флаг `--templates`:**
- Копирует все релевантные шаблоны из `templates/{type}/` в проект
- Создаёт директорию `docs/templates/` в проекте
- Добавляет примеры и руководства

### Ручное использование

Вы также можете копировать шаблоны вручную:

```bash
# Скопировать конкретный шаблон
cp tools/templates/software/ARCHITECTURE-TEMPLATE.md my_project/docs/ARCHITECTURE.md

# Скопировать все шаблоны типа
cp tools/templates/software/* my_project/docs/templates/
```

---

## Типы шаблонов по категориям

### Архитектурные шаблоны
**Используется в:** software, manufacturing, infrastructure
**Примеры:**
- ARCHITECTURE-TEMPLATE.md
- SYSTEM-DESIGN-TEMPLATE.md
- DEPLOYMENT-ARCHITECTURE-TEMPLATE.md

### Стратегические шаблоны
**Используется в:** business, government, nonprofit
**Примеры:**
- BUSINESS-PLAN-TEMPLATE.md
- STRATEGY-DOCUMENT-TEMPLATE.md
- ROADMAP-TEMPLATE.md

### Исследовательские шаблоны
**Используется в:** research, healthcare, education
**Примеры:**
- RESEARCH-PROTOCOL-TEMPLATE.md
- HYPOTHESIS-TESTING-TEMPLATE.md
- DATA-ANALYSIS-PLAN-TEMPLATE.md

### Операционные шаблоны
**Используется в:** все типы
**Примеры:**
- OPERATIONS-MANUAL-TEMPLATE.md
- PROCESS-DOCUMENTATION-TEMPLATE.md
- SOP-TEMPLATE.md

---

## Особенности шаблонов

### 1. Соответствие методологии ⇑⇓↔

Все шаблоны включают:
- **α-уровень** — указание уровня абстракции
- **Статус** — направление развития (⇑⇓↔)
- **CYCLE** — номер цикла итерации
- **Связи** — вертикальные (⇑⇓) и горизонтальные (↔) связи с другими документами

**Пример:**
```markdown
# Document Title
*Уровень абстракции: α=+1 (принципы)*
*Статус: ⇑ ВВЕРХ (от практики к теории)*
*CYCLE: 1*
```

### 2. Практические примеры

Каждый шаблон содержит:
- Инструкции по заполнению
- Примеры хорошего заполнения
- Таблицы и диаграммы
- Чек-листы для самопроверки

### 3. Адаптируемость

Шаблоны можно:
- Использовать как есть
- Модифицировать под конкретный проект
- Комбинировать между собой
- Расширять новыми разделами

### 4. Интеграция с CI/CD

Некоторые шаблоны интегрируются с workflows:
- Documentation checks валидируют наличие требуемых разделов
- Quality checks проверяют completeness
- Methodology checks проверяют α-уровни и статусы

---

## Рекомендации по использованию

### Для software проектов

**Обязательные шаблоны:**
1. ARCHITECTURE-TEMPLATE.md — архитектура системы
2. API-DESIGN-TEMPLATE.md — спецификация API
3. TESTING-STRATEGY-TEMPLATE.md — стратегия тестирования

**Опциональные:**
- DEPLOYMENT-GUIDE-TEMPLATE.md — для production-ready проектов
- CONTRIBUTING-TEMPLATE.md — для open-source проектов

### Для research проектов

**Обязательные шаблоны:**
1. RESEARCH-PROTOCOL-TEMPLATE.md — протокол исследования
2. DATA-ANALYSIS-PLAN-TEMPLATE.md — план анализа данных

**Опциональные:**
- ETHICS-SUBMISSION-TEMPLATE.md — для клинических исследований
- LITERATURE-REVIEW-TEMPLATE.md — для систематических обзоров

### Для business проектов

**Обязательные шаблоны:**
1. BUSINESS-PLAN-TEMPLATE.md — бизнес-план

**Опциональные:**
- MARKETING-STRATEGY-TEMPLATE.md — для маркетинг-фокуса
- FINANCIAL-MODEL-TEMPLATE.xlsx — для fundraising
- INVESTOR-DECK-TEMPLATE.md — для pitch presentations

---

## Создание собственных шаблонов

### 1. Структура

Каждый шаблон должен включать:

```markdown
# [Title]
*Уровень абстракции: α=[level] ([description])*
*Статус: [⇑⇓↔] [description]*
*CYCLE: 1*

---

## Section 1
[Content with instructions in brackets]

## Section 2
[Examples and tables]

---

## Связь с методологией ⇑⇓↔

**Вертикальные связи:**
- ⬆️ ВВЕРХ (α=[level]): [Link to higher abstraction]
- ⬇️ ВНИЗ (α=[level]): [Link to lower abstraction]

**Горизонтальные связи:**
- ↔️ [Type]: [Related documents]

---

**Создано с помощью методологии ⇑⇓↔**
**Version:** 1.0
**Date:** [date]
```

### 2. Добавление в генератор

Чтобы добавить новый шаблон:

1. Создайте файл в `tools/templates/{type}/`
2. Обновите `project_template_generator.py`:
   ```python
   TEMPLATE_MAPPING = {
       "software": [
           "ARCHITECTURE-TEMPLATE.md",
           "API-DESIGN-TEMPLATE.md",
           "YOUR-NEW-TEMPLATE.md"  # Add here
       ],
       # ...
   }
   ```

---

## Статистика

**Всего шаблонов:** 48+ (8 реализовано в v0.6-v0.7)
**Типов проектов покрыто:** 8 из 16
**Реализованные типы:** software, research, business, education, legal, healthcare, arts
**Общий объём шаблонов:** ~7,650 строк
**Средний размер шаблона:** 900+ строк

---

## Обновления

### v0.7 (Фаза 0.8 — 2026-01-24)
- ✅ Добавлены шаблоны для education проектов
  - CURRICULUM-DESIGN-TEMPLATE.md (900+ lines)
- ✅ Добавлены шаблоны для legal проектов
  - LEGAL-MEMORANDUM-TEMPLATE.md (850+ lines)
- ✅ Добавлены шаблоны для healthcare проектов
  - CLINICAL-PROTOCOL-TEMPLATE.md (1100+ lines)
- ✅ Добавлены шаблоны для arts проектов
  - CREATIVE-BRIEF-TEMPLATE.md (900+ lines)
- ✅ Обновлён TEMPLATE_MAPPING в генераторе
- ✅ Всего 8 типов проектов покрыты шаблонами (из 16)

### v0.6 (Фаза 0.8 — 2026-01-24)
- ✅ Создана инфраструктура шаблонов
- ✅ Добавлены шаблоны для software проектов
  - ARCHITECTURE-TEMPLATE.md
  - API-DESIGN-TEMPLATE.md
- ✅ Добавлены шаблоны для research проектов
  - RESEARCH-PROTOCOL-TEMPLATE.md
- ✅ Добавлены шаблоны для business проектов
  - BUSINESS-PLAN-TEMPLATE.md

### Планируется в v0.8
- Завершение всех 48+ шаблонов (остальные 8 типов)
- Интеграция с IDE (VS Code extension)
- Автоматическое заполнение на основе AI
- Темплейт-валидация в CI/CD

---

## Поддержка и контрибьюции

### Сообщить о проблеме
GitHub Issues: [link]

### Предложить улучшение
Pull Request в директорию `tools/templates/`

### Добавить новый шаблон
1. Fork репозитория
2. Создайте шаблон по структуре выше
3. Добавьте примеры
4. Submit PR

---

## Связь с методологией ⇑⇓↔

**Вертикальные связи:**
- ⬆️ ВВЕРХ (α=0): [project_template_generator.py] — Генератор проектов
- ⬇️ ВНИЗ (α=-2): [Конкретные шаблоны в поддиректориях]

**Горизонтальные связи:**
- ↔️ ИНСТРУМЕНТЫ: GENERATOR-GUIDE.md, ЭТАП-8-УНИВЕРСАЛЬНАЯ-МЕТА-МЕТОДОЛОГИЯ.md

---

**Создано с помощью методологии ⇑⇓↔**
**Версия:** 1.1 (v0.7)
**Дата создания:** 2026-01-24
**Последнее обновление:** 2026-01-24 (v0.7 — education, legal, healthcare, arts)
