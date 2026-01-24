# 🚀 Руководство по генератору проектов
*Уровень абстракции: α=-1 (инструкция)*
*Статус: ↔ ГОРИЗОНТ (обзор инструмента)*
*CYCLE: 3*
*Версия: v0.4*

---

## Введение

`project_template_generator.py` — инструмент для автоматической генерации структуры нового проекта с встроенной методологией **⇑⇓↔** (Параллельная Двунаправленная Разработка).

**Возможности v0.4:**
- ✅ **16 типов проектов** (software, research, business, education, legal, healthcare, arts, finance, government, nonprofit, manufacturing, agriculture, sports, hospitality, retail, hobby)
- ✅ **Интерактивный режим** с пошаговыми вопросами
- ✅ **Git/GitHub интеграция** — автоматическая инициализация репозитория и создание на GitHub
- ✅ **CI/CD интеграция** — GitHub Actions workflows для автоматического тестирования ⭐ НОВОЕ
- ✅ Автоматическое создание иерархии α-уровней
- ✅ Встроенные метрики здоровья (VT, DB, CD, CR)
- ✅ Доменно-специфичные документы для каждого типа
- ✅ Копирование инструментов валидации
- ✅ Универсальный шаблон **hobby** для любых доменов

---

## Быстрый старт

### Базовое использование

```bash
python3 tools/project_template_generator.py --name my_project --type software
```

**Что создаётся:**
```
my_project/
├── 01-Концепция/          # α=+1..+4
├── 02-Архитектура/        # α=-1..+1
├── 03-Реализация/         # α=-4..-1
├── docs/                  # Документация
├── tools/                 # Инструменты валидации
│   └── health_metrics.py  # Автоматически скопирован
├── .methodology.json      # Конфигурация методологии
├── README.md              # Главная страница (α=+1)
├── МЕТОДОЛОГИЯ.md         # Описание ⇑⇓↔ (α=+2)
└── METRICS.md             # Метрики здоровья (α=+1)
```

### Проверка метрик

```bash
cd my_project
python3 tools/health_metrics.py
```

---

## 📦 Типы проектов

### 1. Software (Программное обеспечение)

**Фокус:** α=-4..+2 (от кода до архитектуры)

```bash
python3 tools/project_template_generator.py --name web_app --type software
```

**Специфичные директории:**
- `src/` — исходный код
- `tests/` — тесты
- `config/` — конфигурация

**Ключевые документы:**
- `README.md` — описание проекта
- `ARCHITECTURE.md` (α=-1) — техническая архитектура
- `API-SPEC.md` (α=-2) — спецификация API

**Пример иерархии:**
```
α=+2: Архитектурные паттерны (MVC, микросервисы)
α=+1: Модульная структура
α=0:  Компоненты
α=-1: Классы и интерфейсы
α=-2: Функции
α=-3: Строки кода
α=-4: Скомпилированный код
```

---

### 2. Research (Научное исследование)

**Фокус:** α=-1..+4 (от данных до философии науки)

```bash
python3 tools/project_template_generator.py --name quantum_study --type research
```

**Специфичные директории:**
- `data/` — экспериментальные данные
- `notebooks/` — Jupyter notebooks
- `papers/` — публикации

**Ключевые документы:**
- `README.md` — краткое описание
- `HYPOTHESIS.md` (α=+2) — научная гипотеза
- `METHODOLOGY.md` (α=+1) — методология исследования

**Пример иерархии:**
```
α=+4: Философия науки
α=+3: Научная парадигма (квантовая механика)
α=+2: Теория и гипотеза
α=+1: Методология эксперимента
α=0:  План эксперимента
α=-1: Протокол измерений
α=-2: Сырые данные
```

---

### 3. Business (Бизнес-проект)

**Фокус:** α=-2..+3 (от метрик до стратегии)

```bash
python3 tools/project_template_generator.py --name startup_x --type business
```

**Специфичные директории:**
- `business_plan/` — бизнес-планы
- `marketing/` — маркетинговые материалы
- `finance/` — финансовые модели

**Ключевые документы:**
- `README.md` — обзор бизнеса
- `BUSINESS-MODEL.md` (α=+1) — бизнес-модель
- `STRATEGY.md` (α=+2) — стратегия развития

**Пример иерархии:**
```
α=+3: Миссия и ценности
α=+2: Бизнес-стратегия
α=+1: Бизнес-модель (Canvas)
α=0:  Продукты и услуги
α=-1: Процессы и процедуры
α=-2: KPI и метрики
α=-3: Транзакции
```

---

### 4. Education (Образовательный проект)

**Фокус:** α=-3..+3 (от заданий до философии образования)

```bash
python3 tools/project_template_generator.py --name ai_course --type education
```

**Специфичные директории:**
- `lessons/` — учебные материалы
- `assignments/` — задания
- `resources/` — дополнительные ресурсы

**Ключевые документы:**
- `README.md` — описание курса
- `CURRICULUM.md` (α=+1) — учебный план
- `PEDAGOGY.md` (α=+2) — педагогическая методология

**Пример иерархии:**
```
α=+3: Философия образования
α=+2: Педагогические теории
α=+1: Учебный план (curriculum)
α=0:  Модули курса
α=-1: Уроки
α=-2: Упражнения
α=-3: Ответы и решения
```

---

### 5. Legal (Юридический проект)

**Фокус:** α=-1..+3 (от шаблонов до правовых принципов)

```bash
python3 tools/project_template_generator.py --name law_practice --type legal
```

**Специфичные директории:**
- `cases/` — юридические дела
- `contracts/` — контракты и договоры
- `regulations/` — нормативные акты

**Ключевые документы:**
- `README.md` — обзор практики
- `LEGAL-FRAMEWORK.md` (α=+1) — правовая основа
- `CASE-LAW.md` (α=-1) — прецедентное право

**Пример иерархии:**
```
α=+3: Правовые принципы (справедливость, равенство)
α=+2: Законодательство (конституция, кодексы)
α=+1: Инструкции и регламенты
α=0:  Дела и прецеденты
α=-1: Шаблоны документов
α=-2: Конкретные договоры
```

**Пример использования:**
```bash
cd law_practice
# Добавьте дело в cases/
mkdir cases/case_2024_001
# Обновите LEGAL-FRAMEWORK.md с применимыми законами
# Проверьте метрики
python3 tools/health_metrics.py
```

---

### 6. Healthcare (Проект здравоохранения)

**Фокус:** α=-2..+3 (от данных пациентов до медицинской философии)

```bash
python3 tools/project_template_generator.py --name clinic_network --type healthcare
```

**Специфичные директории:**
- `protocols/` — клинические протоколы
- `cases/` — истории болезней (деперсонализированные)
- `research/` — медицинские исследования

**Ключевые документы:**
- `README.md` — описание проекта
- `CLINICAL-PROTOCOLS.md` (α=-1) — протоколы лечения
- `PATIENT-CARE.md` (α=+1) — принципы ухода за пациентами

**Пример иерархии:**
```
α=+3: Медицинская философия (холизм, этика)
α=+2: Теории болезней (патофизиология)
α=+1: Клинические принципы
α=0:  Диагнозы (МКБ-10)
α=-1: Протоколы лечения
α=-2: Шаблоны обследований
α=-3: Истории болезней
α=-4: Лабораторные данные
```

**Пример использования:**
```bash
cd clinic_network
# Добавьте протокол в protocols/
echo "## Протокол лечения гипертонии" > protocols/hypertension.md
# Обновите CLINICAL-PROTOCOLS.md
# Проверьте метрики
python3 tools/health_metrics.py
```

---

### 7. Arts (Творческий/Художественный проект)

**Фокус:** α=-3..+4 (от технического исполнения до онтологии искусства)

```bash
python3 tools/project_template_generator.py --name art_installation --type arts
```

**Специфичные директории:**
- `works/` — готовые произведения
- `sketches/` — эскизы и наброски
- `portfolio/` — портфолио

**Ключевые документы:**
- `README.md` — обзор творчества
- `CREATIVE-VISION.md` (α=+3) — творческое видение
- `PORTFOLIO.md` (α=-1) — каталог работ

**Пример иерархии:**
```
α=+4: Онтология искусства (Что такое искусство?)
α=+3: Эстетическая философия (стиль, ценности)
α=+2: Творческие концепции (темы, мотивы)
α=+1: Художественная методология
α=0:  Проекты и серии
α=-1: Эскизы и наброски
α=-2: Материалы и техники
α=-3: Физическое воплощение
α=-4: Техническое исполнение (освещение, монтаж)
```

**Пример использования:**
```bash
cd art_installation
# Добавьте эскиз в sketches/
mkdir sketches/sculpture_series_2026
# Обновите CREATIVE-VISION.md с философией
# Добавьте работу в портфолио
echo "## Скульптура: Время в камне" >> PORTFOLIO.md
# Проверьте метрики
python3 tools/health_metrics.py
```

---

### 8. Finance (Финансовый проект)

**Фокус:** α=-3..+2 (от транзакций до финансовой теории)

```bash
python3 tools/project_template_generator.py --name investment_fund --type finance
```

**Ключевые документы:** FINANCIAL-STRATEGY.md (α=+1)
**Примеры:** инвестиционный фонд, финансовое планирование, управление портфелем

---

### 9. Government (Государственное управление)

**Фокус:** α=-1..+3 (от услуг до конституционных принципов)

```bash
python3 tools/project_template_generator.py --name public_service --type government
```

**Ключевые документы:** PUBLIC-POLICY.md (α=+2)
**Примеры:** государственная программа, электронные услуги, муниципальный проект

---

### 10. Nonprofit (Некоммерческая организация)

**Фокус:** α=-1..+3 (от мероприятий до социальной миссии)

```bash
python3 tools/project_template_generator.py --name charity_org --type nonprofit
```

**Ключевые документы:** MISSION-IMPACT.md (α=+3)
**Примеры:** благотворительный фонд, социальный проект, НКО

---

### 11. Manufacturing (Производство)

**Фокус:** α=-4..+2 (от параметров оборудования до производственной стратегии)

```bash
python3 tools/project_template_generator.py --name factory --type manufacturing
```

**Ключевые документы:** PRODUCTION-PROCESS.md (α=-1)
**Примеры:** завод, производственная линия, Lean/Six Sigma проект

---

### 12. Agriculture (Сельское хозяйство)

**Фокус:** α=-3..+2 (от данных полей до агрономической науки)

```bash
python3 tools/project_template_generator.py --name farm --type agriculture
```

**Ключевые документы:** CROP-MANAGEMENT.md (α=0)
**Примеры:** ферма, органическое земледелие, агротехнологии

---

### 13. Sports (Спортивный проект)

**Фокус:** α=-3..+3 (от показателей до спортивной философии)

```bash
python3 tools/project_template_generator.py --name athletics_team --type sports
```

**Ключевые документы:** TRAINING-PROGRAM.md (α=+1)
**Примеры:** спортивная команда, фитнес-программа, спортивная школа

---

### 14. Hospitality (Гостеприимство и туризм)

**Фокус:** α=-2..+2 (от процедур до культуры гостеприимства)

```bash
python3 tools/project_template_generator.py --name hotel --type hospitality
```

**Ключевые документы:** SERVICE-STANDARDS.md (α=-1)
**Примеры:** отель, ресторан, туристическое агентство

---

### 15. Retail (Розничная торговля)

**Фокус:** α=-3..+1 (от транзакций до торговой стратегии)

```bash
python3 tools/project_template_generator.py --name store_chain --type retail
```

**Ключевые документы:** RETAIL-STRATEGY.md (α=+1)
**Примеры:** магазин, торговая сеть, e-commerce

---

### 16. Hobby (Универсальный шаблон)

**Фокус:** α=-3..+3 (универсальный для любого домена)

```bash
python3 tools/project_template_generator.py --name photography --type hobby
```

**Ключевые документы:** PROJECT-VISION.md (α=+2)

**⭐ ОСОБЕННОСТЬ:** Универсальный шаблон для доменов, не вошедших в стандартный набор.

**Примеры использования:**
- Фотография, музыка, живопись
- Программирование как хобби
- Кулинария, садоводство
- Моделирование, DIY проекты
- Любое личное увлечение

**Пример:**
```bash
cd photography
# Адаптируйте PROJECT-VISION.md под свой домен
# Создайте структуру под свои нужды
python3 tools/health_metrics.py
```

---

## 🔧 Расширенное использование

### Проверка доступных типов

```bash
python3 tools/project_template_generator.py --help
```

### Структура .methodology.json

Каждый проект содержит конфигурационный файл:

```json
{
  "project_name": "my_project",
  "project_type": "software",
  "created_at": "2026-01-24T12:00:00",
  "alpha_levels": {
    "min": -4,
    "max": 4
  },
  "methodology": "Parallel Bidirectional Development (⇑⇓↔)",
  "directions": {
    "up": "⇑ ВВЕРХ",
    "down": "⇓ ВНИЗ",
    "horizontal": "↔ ГОРИЗОНТ"
  },
  "metrics": {
    "VT": "Vertical Traceability (22-44%)",
    "DB": "Directional Balance (<30%)",
    "CD": "Connectivity Density (16.5-33%)",
    "CR": "Convergence Rate (0.6-1.3)"
  }
}
```

---

## 📊 Метрики здоровья проекта

После создания проекта используйте `health_metrics.py`:

```bash
cd my_project
python3 tools/health_metrics.py
```

**Целевые диапазоны:**
- **VT** (Vertical Traceability): 22-44%
- **DB** (Directional Balance): <30%
- **CD** (Connectivity Density): 16.5-33%
- **CR** (Convergence Rate): 0.6-1.3

**Как улучшить метрики:**

1. **VT слишком низкая** → добавьте вертикальные связи (⇅) между уровнями
2. **DB слишком высокая** → добавьте явные статусы "Статус: ⇑/⇓/↔" в документы
3. **CD слишком высокая** → удалите избыточные связи
4. **CR > 1.3** → уменьшите пересечения между направлениями

---

## 🤖 Интерактивный режим (v0.3)

Интерактивный режим помогает настроить проект с помощью пошаговых вопросов.

### Запуск

```bash
python3 tools/project_template_generator.py --name my_project --type software --interactive
```

### Что спрашивает интерактивный режим:

1. **Подтверждение типа проекта**
   - Показывает выбранный тип и его характеристики
   - Предлагает изменить тип, если нужно

2. **Выбор нового типа (опционально)**
   - Показывает все 16 доступных типов
   - Позволяет выбрать другой тип проекта

3. **Git интеграция**
   - Инициализировать Git репозиторий?
   - Создать GitHub репозиторий? (требует gh CLI)
   - Visibility (public/private)
   - Описание репозитория

4. **Итоговое подтверждение**
   - Показывает финальную конфигурацию
   - Запрашивает подтверждение перед созданием

### Пример интерактивной сессии:

```
$ python3 tools/project_template_generator.py --name my_app --type software --interactive

🤖 Интерактивный режим настройки проекта

============================================================

Выбран тип проекта: Software Project
Описание: Проект разработки программного обеспечения
Фокус α-уровней: α=-4..+3

Изменить тип проекта? (y/N): n

============================================================

📋 Дополнительные параметры

Инициализировать Git репозиторий? (Y/n): y
Создать GitHub репозиторий? (требует gh CLI) (y/N): y
  Visibility (public/private) [private]: public
  Описание репозитория [my_app]: Мое новое приложение

============================================================

📦 Итоговая конфигурация:

  Название:     my_app
  Тип:          Software Project
  Директория:   /current/path/my_app
  Git init:     Да
  GitHub repo:  Да (public)

Продолжить создание проекта? (Y/n): y
```

---

## 🔧 Git/GitHub интеграция (v0.3)

### Базовая Git интеграция

Автоматическая инициализация Git репозитория:

```bash
python3 tools/project_template_generator.py --name my_project --type software --git
```

**Что создаётся:**
- Инициализация Git репозитория (`git init`)
- Создание `.gitignore` с базовыми правилами
- Автоматический первый коммит

### GitHub интеграция

Создание репозитория на GitHub (требует [gh CLI](https://cli.github.com/)):

```bash
# Приватный репозиторий (по умолчанию)
python3 tools/project_template_generator.py --name my_project --type software --github

# Публичный репозиторий
python3 tools/project_template_generator.py --name open_source --type software --github --github-visibility public
```

**Что происходит:**
1. Инициализация Git (автоматически включается с `--github`)
2. Создание `.gitignore`
3. Первый коммит
4. Создание репозитория на GitHub
5. Автоматический push кода

**Требования:**
- Установленный [gh CLI](https://cli.github.com/)
- Авторизация: `gh auth login`

### Примеры

```bash
# Только Git
python3 tools/project_template_generator.py --name local_project --type hobby --git

# Git + GitHub (приватный)
python3 tools/project_template_generator.py --name startup --type business --github

# Git + GitHub (публичный) + интерактивный режим
python3 tools/project_template_generator.py --name community --type nonprofit --interactive
```

---

## ⚙️ CI/CD интеграция (v0.4)

### Автоматическое тестирование

Генератор может автоматически настроить CI/CD с помощью GitHub Actions workflows.

```bash
# С CI/CD
python3 tools/project_template_generator.py --name my_project --type software --ci

# С Git + GitHub + CI/CD
python3 tools/project_template_generator.py --name my_project --type software --github --ci
```

### Что создаётся

Генератор создаёт `.github/workflows/` с workflow файлами:

**Универсальные workflows (для всех типов):**
1. **methodology_check.yml** — проверка соблюдения методологии ⇑⇓↔
   - Проверка α-уровней в документах
   - Проверка статусов направлений (⇑⇓↔)
   - Валидация .methodology.json
   - Проверка CYCLE progression
   - Генерация отчёта о методологии

2. **documentation_check.yml** — проверка качества документации
   - Markdown linting
   - Проверка битых ссылок
   - Проверка структуры (01-Концепция, 02-Архитектура, 03-Реализация)
   - Проверка метаданных (α-level, статус, CYCLE)
   - Генерация отчёта о документации

**Специфичные workflows:**

**Software projects:**
- **software_ci.yml** — полный CI/CD pipeline
  - Тесты на Python 3.9-3.12
  - Линтинг (flake8, black, mypy)
  - Coverage отчёты (Codecov)
  - Сборка пакетов
  - Security scanning (Trivy)
  - Проверка метрик методологии

**Research projects:**
- **research_ci.yml** — валидация исследований
  - Проверка структуры данных
  - Валидация CSV/JSON файлов
  - Выполнение Jupyter notebooks
  - Проверка репродуцируемости (requirements.txt)
  - Проверка исследовательской документации (HYPOTHESIS.md, METHODOLOGY.md)

### Примеры использования

```bash
# Software проект с полным CI/CD
python3 tools/project_template_generator.py --name web_app --type software --github --ci

# Research проект с валидацией данных
python3 tools/project_template_generator.py --name experiment --type research --github --ci

# Hobby проект с базовыми проверками
python3 tools/project_template_generator.py --name photography --type hobby --ci
```

### Триггеры workflows

Workflows запускаются автоматически:
- ✅ При `push` в main/master/develop ветки
- ✅ При создании Pull Request
- ✅ По расписанию (еженедельно по понедельникам)

### Метрики и отчёты

CI/CD проверяет метрики методологии:
- **VT** (Vertical Traceability): 22-44%
- **DB** (Directional Balance): <30%
- **CD** (Connectivity Density): 16.5-33%
- **CR** (Convergence Rate): 0.6-1.3

Отчёты загружаются как артефакты (доступны 30 дней).

### Интерактивный режим

В интерактивном режиме генератор спросит о CI/CD:

```
Настроить CI/CD (GitHub Actions)? (y/N): y
  ℹ️  Будут созданы GitHub Actions workflows для автоматического тестирования
```

---

## 🎯 Рекомендации по развитию проекта

### 1. Начните с философии (⇑ ВВЕРХ)

Для любого типа проекта сначала определите высокоуровневую цель:

```markdown
# 01-Концепция/PHILOSOPHY.md
*Уровень абстракции: α=+3*
*Статус: ⇑ ВВЕРХ*

## Зачем существует этот проект?
[Ответ на фундаментальный вопрос]
```

### 2. Детализируйте реализацию (⇓ ВНИЗ)

Создавайте конкретные спецификации и код:

```markdown
# 03-Реализация/module_spec.md
*Уровень абстракции: α=-2*
*Статус: ⇓ ВНИЗ*

## Функция calculate()
[Детальное описание]
```

### 3. Связывайте уровни (↔ ГОРИЗОНТ)

Создавайте обзорные документы:

```markdown
# КАРТА-СВЯЗЕЙ.md
*Уровень абстракции: α=0*
*Статус: ↔ ГОРИЗОНТ*

## Навигация по проекту
[Связи между документами]
```

---

## 🚀 Примеры реальных сценариев

### Сценарий 1: Запуск стартапа

```bash
# 1. Создайте бизнес-проект
python3 tools/project_template_generator.py --name my_startup --type business

cd my_startup

# 2. Определите стратегию (⇑)
vim 01-Концепция/STRATEGY.md

# 3. Создайте бизнес-модель (⇓)
vim BUSINESS-MODEL.md

# 4. Проверьте метрики
python3 tools/health_metrics.py
```

### Сценарий 2: Онлайн-курс

```bash
# 1. Создайте образовательный проект
python3 tools/project_template_generator.py --name ml_course --type education

cd ml_course

# 2. Определите педагогику (⇑)
vim 01-Концепция/PEDAGOGY.md

# 3. Создайте учебный план (↔)
vim CURRICULUM.md

# 4. Добавьте уроки (⇓)
mkdir lessons/week_01
vim lessons/week_01/intro.md
```

### Сценарий 3: Медицинский исследовательский проект

```bash
# 1. Создайте healthcare проект
python3 tools/project_template_generator.py --name covid_research --type healthcare

cd covid_research

# 2. Определите этические принципы (⇑)
vim 01-Концепция/ETHICS.md

# 3. Создайте протоколы (⇓)
vim 01-Концепция/CLINICAL-PROTOCOLS.md

# 4. Добавьте данные исследований
mkdir research/cohort_2024
```

---

## 🔄 Интеграция с существующим проектом

Если у вас уже есть проект, вы можете адаптировать структуру:

```bash
# 1. Создайте временный шаблон
python3 tools/project_template_generator.py --name temp_template --type software

# 2. Скопируйте нужные файлы в свой проект
cp temp_template/МЕТОДОЛОГИЯ.md my_existing_project/
cp temp_template/.methodology.json my_existing_project/
cp -r temp_template/tools my_existing_project/

# 3. Проверьте метрики
cd my_existing_project
python3 tools/health_metrics.py
```

---

## 📚 Дополнительная документация

- **МЕТОДОЛОГИЯ.md** — описание ⇑⇓↔ в каждом проекте
- **METRICS.md** — детали метрик здоровья
- **collective_network/** — примеры из info1 проекта
- **ЭТАП-8-УНИВЕРСАЛЬНАЯ-МЕТА-МЕТОДОЛОГИЯ.md** — видение универсализации

---

## ❓ FAQ

**Q: Можно ли изменить структуру после создания?**
A: Да, структура полностью редактируемая. Используйте её как стартовый шаблон.

**Q: Как добавить свой тип проекта?**
A: Отредактируйте `project_template_generator.py`, добавив новый ключ в `PROJECT_TYPES` и соответствующие методы.

**Q: Что делать, если метрики вне диапазона?**
A: См. раздел "Метрики здоровья проекта" выше. Обычно достаточно добавить явные статусы и вертикальные связи.

**Q: Работает ли генератор для не-русских проектов?**
A: Да, но шаблоны на русском. Можно легко адаптировать, изменив строки в генераторе.

**Q: Как использовать интерактивный режим?**
A: Добавьте флаг `--interactive` при запуске. Генератор задаст вопросы о конфигурации проекта.

**Q: Нужен ли gh CLI для работы генератора?**
A: Нет, gh CLI нужен только для создания GitHub репозитория (флаг `--github`). Git интеграция (`--git`) работает без него.

**Q: Какой тип выбрать, если мой домен не указан?**
A: Используйте универсальный тип `hobby` — он подходит для любого домена. Адаптируйте PROJECT-VISION.md под вашу область.

**Q: Можно ли создать публичный GitHub репозиторий?**
A: Да, используйте `--github --github-visibility public`.

**Q: Как настроить CI/CD?**
A: Добавьте флаг `--ci` при создании проекта. Генератор создаст GitHub Actions workflows.

**Q: Какие CI/CD workflows создаются?**
A: Универсальные (проверка методологии и документации) для всех типов + специфичные для software и research проектов.

**Q: Будут ли workflows работать без GitHub?**
A: Workflows используют GitHub Actions, поэтому требуют GitHub репозиторий. Для локального CI можно адаптировать workflows.

---

## 🎉 Итоги

`project_template_generator.py` v0.4 — это:
- ✅ **16 доменов** (software, research, business, education, legal, healthcare, arts, finance, government, nonprofit, manufacturing, agriculture, sports, hospitality, retail, hobby)
- ✅ **Интерактивный режим** — пошаговая настройка проекта
- ✅ **Git/GitHub интеграция** — автоматическая инициализация и публикация
- ✅ **CI/CD интеграция** — GitHub Actions workflows для автоматического тестирования ⭐ НОВОЕ
- ✅ Автоматическая структура α-уровней
- ✅ Встроенные метрики здоровья
- ✅ Доменно-специфичные документы
- ✅ Универсальный шаблон **hobby** для любых доменов
- ✅ Копирование инструментов валидации

**Следующие шаги:**
1. Создайте проект:
   ```bash
   # Быстрый старт
   python3 tools/project_template_generator.py --name X --type Y

   # С Git/GitHub + CI/CD (v0.4)
   python3 tools/project_template_generator.py --name X --type Y --github --ci

   # Интерактивный режим
   python3 tools/project_template_generator.py --name X --type Y --interactive
   ```

2. Определите философию (⇑)
3. Детализируйте реализацию (⇓)
4. Создайте навигацию (↔)
5. Проверьте метрики: `python3 tools/health_metrics.py`
6. (v0.4) Workflows автоматически проверят проект при push

---

**Что нового в v0.4:**
- ⚙️ **CI/CD интеграция** — автоматическое тестирование через GitHub Actions
- 📊 **Проверка методологии** — автоматическая валидация метрик ⇑⇓↔
- 📝 **Проверка документации** — линтинг, битые ссылки, структура
- 🔬 **Специфичные workflows** — software CI (тесты, линтинг), research CI (данные, notebooks)
- 🔒 **Security scanning** — Trivy для software проектов
- 📈 **Отчёты** — автоматическая генерация отчётов о качестве

**Changelog v0.3→v0.4:**
- +4 CI/CD workflow шаблона
- +1 флаг --ci/--cicd
- +2 метода в генераторе (_setup_cicd_integration, _get_cicd_workflows_for_type)
- Обновлён интерактивный режим (вопрос о CI/CD)

---

*Версия: v0.4*
*Дата: 2026-01-24*
*Проект: info1 — ЭТАП 8 v0.4*
