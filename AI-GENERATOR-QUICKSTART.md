# AI-POWERED Project Generator - Quick Start Guide

🤖 **AI-генератор проектов с natural language interface**

Просто опишите проект обычным языком — система автоматически определит тип, извлечёт параметры и создаст персонализированную структуру!

---

## 🚀 Быстрый старт

### 1. Простейший пример

```bash
python tools/ai_cli_v2.py "Хочу создать веб-приложение для управления задачами"
```

**Результат:**
- 🔍 Определён тип: software
- 📁 Создана структура проекта
- 📄 Сгенерирован README.md
- ✅ Проект готов к разработке!

---

### 2. Проект с параметрами

```bash
python tools/ai_cli_v2.py "Финтех MVP на React, бюджет 3 млн ₽, команда 8, срок 4 месяца"
```

**AI автоматически:**
- Определит тип: `business` (primary) + `software` (secondary)
- Извлечёт: budget (3M RUB), timeline (4 months), team (8), phase (MVP), tech (React)
- Добавит: MVP structure, team docs, financial tracking, React components
- Сгенерирует: README с badges, CONTRIBUTING для команды, CHECKLIST для MVP

**Вывод:**
```
🔍 Phase 1-2: Классификация проекта (ML)
✓ Primary type: business (12.5%)
✓ Secondary types: software, finance

⚙️  Phase 3: Извлечение параметров
✓ Budget: 3,000,000 RUB
✓ Timeline: 4 months
✓ Team size: 8 members
✓ Phase: MVP
✓ Technologies: react

📦 Phase 3: Композиция шаблонов
✓ Strategy: multi_domain
✓ Base: 12 dirs → Adapted: 18 dirs (50% growth)

📄 Phase 4: Генерация контента
✓ README.md (personalized)
✓ CONTRIBUTING.md (for team)
✓ CHECKLIST.md (MVP phase)
✓ Code examples: react_component.jsx
```

---

### 3. Гибридный проект (multi-domain)

```bash
python tools/ai_cli_v2.py "Healthcare телемедицина на React+Node.js, бюджет 8 млн ₽, команда 12, критический приоритет"
```

**Гибридные типы:**
- Primary: `healthcare`
- Secondary: `software`, `business`

**Результат:**
- ✅ Структура объединяет медицинские протоколы + бизнес-план + код
- ✅ README с badges (type-healthcare, phase-mvp, priority-critical)
- ✅ ARCHITECTURE.md для крупного проекта
- ✅ CONTRIBUTING.md для команды 12 человек

---

## 📖 Синтаксис

### Базовая команда

```bash
python tools/ai_cli_v2.py "<описание проекта>"
```

### С опциями

```bash
# Указать имя проекта
python tools/ai_cli_v2.py "Проект для..." --name my-project

# Dry run (preview без создания)
python tools/ai_cli_v2.py "Проект для..." --dry-run

# Interactive mode (с подтверждением)
python tools/ai_cli_v2.py "Проект для..." --interactive

# Без автоматического контента
python tools/ai_cli_v2.py "Проект для..." --no-content

# Указать output директорию
python tools/ai_cli_v2.py "Проект для..." --output projects/
```

---

## 🎯 Что можно указать в описании?

### Типы проектов (16 типов)
- **Software:** "веб-приложение", "мобильное приложение", "SaaS"
- **Healthcare:** "медицинская клиника", "телемедицина", "health app"
- **Business:** "стартап", "бизнес-план", "коммерческий проект"
- **Research:** "научное исследование", "research project"
- **Finance:** "финтех", "инвестиционный проект"
- **Education:** "онлайн-курс", "образовательная платформа"
- **И ещё 10 типов:** legal, arts, government, nonprofit, manufacturing, agriculture, sports, hospitality, retail, hobby

### Параметры (15+ автоматически извлекаются)

**Бюджет:**
```
"бюджет 3 млн ₽"
"грант 5 миллионов рублей"
"$100k budget"
```

**Сроки:**
```
"срок 6 месяцев"
"timeline: 12 months"
"на 2 года"
```

**Команда:**
```
"команда 8 человек"
"team of 15 developers"
"25 сотрудников"
```

**Фаза:**
```
"MVP"
"alpha версия"
"production launch"
"scaling phase"
```

**Технологии:**
```
"на React"
"Django + PostgreSQL"
"с использованием Docker и Kubernetes"
"AI/ML проект на Python"
```

**Приоритет:**
```
"критический приоритет"
"срочный проект"
"высокий приоритет"
```

**Тип проекта:**
```
"коммерческий проект"
"благотворительный фонд"
"некоммерческая организация"
```

---

## 💡 Примеры реальных сценариев

### Стартап
```bash
python tools/ai_cli_v2.py "Fintech стартап на React+Node.js, MVP для управления личными финансами, бюджет 5 млн ₽, команда 10 человек, срок 6 месяцев, критический приоритет"
```

**Получите:**
- Multi-domain: business + software + finance
- MVP структура с roadmap
- Team docs (onboarding, code review)
- Financial tracking
- React/Node.js examples
- MVP CHECKLIST

---

### Научное исследование
```bash
python tools/ai_cli_v2.py "Научное исследование влияния микропластика на океан, грант РНФ 10 млн ₽, команда 25 исследователей, высокий риск, 24 месяца"
```

**Получите:**
- Type: research
- Grant reporting structure
- Large team management (25+ docs)
- Risk management docs
- Timeline tracking (24 months)
- Publications structure

---

### Healthcare платформа
```bash
python tools/ai_cli_v2.py "Healthcare телемедицина платформа с видеоконсультациями, React+Django+PostgreSQL, коммерческий проект, production запуск, команда 15 человек"
```

**Получите:**
- Multi-domain: healthcare + software + business
- Medical protocols + Code structure
- Production deployment docs
- Commercial business plan
- Full tech stack setup (React, Django, PostgreSQL)
- HIPAA compliance references

---

### E-commerce
```bash
python tools/ai_cli_v2.py "E-commerce платформа для продажи товаров ручной работы, Django + React, бюджет 4 млн ₽, команда 8"
```

**Получите:**
- Multi-domain: retail + software
- Inventory management
- Payment integration guidelines
- Product catalog structure
- Django/React examples

---

## 🔍 Что делает AI?

### Phase 1-2: ML Classification (87.5% accuracy)
- Определяет primary тип проекта
- Находит secondary типы (multi-domain)
- Вычисляет confidence scores

### Phase 3: Enhanced Parameter Extraction
- Извлекает 15+ параметров:
  - Budget (amount, currency)
  - Timeline (value, unit, months)
  - Team size
  - Phase (concept, MVP, alpha, beta, production, scaling)
  - Technologies (50+ поддерживается)
  - Priority (low, medium, high, critical)
  - Risk level (low, medium, high)
  - Industry (fintech, healthtech, edtech, ecommerce...)
  - Location
  - Flags (is_funded, is_commercial, is_nonprofit, has_deadline)

### Phase 3: Template Composition
- Выбирает стратегию композиции:
  - `merge_directories` - объединение директорий
  - `nested_structure` - вложенная структура
  - `parallel_structure` - параллельные директории
- Создаёт базовую структуру из 1-4 типов

### Phase 3: Context-Aware Adaptation
- Применяет 20+ правил адаптации:
  - Budget ≥1M → финансовый tracking
  - Team ≥5 → collaboration docs
  - Team ≥10 → team management
  - Team ≥20 → enterprise structure
  - Phase=MVP → MVP docs, prioritization
  - Phase=Production → deployment, monitoring
  - Tech=React → components, hooks
  - Tech=Docker → Dockerfile, docker-compose
  - Priority=Critical → sprint planning, escalation
  - Risk=High → risk management docs
- Рост структуры: 50-100%

### Phase 4: LLM Content Generation
- Генерирует персонализированные файлы:
  - **README.md** с badges, overview, features, tech stack, getting started
  - **ARCHITECTURE.md** (для scale=large)
  - **CONTRIBUTING.md** (для team≥5)
  - **CHECKLIST.md** (phase-specific)
  - **Code examples** (tech-specific: React, Django, FastAPI, Docker...)

---

## 📊 Поддерживаемые технологии

**Frontend:**
- React, Vue, Angular, Svelte, Next.js, Nuxt

**Backend:**
- Node.js, Python, Java, Go, Rust, PHP, Ruby
- Django, Flask, FastAPI, Express, Spring

**Mobile:**
- React Native, Flutter, Swift, Kotlin, Ionic

**Databases:**
- PostgreSQL, MySQL, MongoDB, Redis, Elasticsearch

**DevOps:**
- Docker, Kubernetes, AWS, Azure, GCP, Terraform

**AI/ML:**
- AI, ML, Machine Learning, Deep Learning

---

## 🎓 Советы

### 1. Будьте конкретны
❌ Плохо: "Хочу проект"
✅ Хорошо: "Финтех MVP на React, бюджет 3 млн ₽, команда 8"

### 2. Указывайте ключевые параметры
Чем больше информации, тем лучше адаптация:
- Бюджет → financial tracking
- Команда → collaboration docs
- Фаза → phase-specific structure
- Технологии → framework-specific files

### 3. Используйте --dry-run для preview
Сначала посмотрите, что будет создано:
```bash
python tools/ai_cli_v2.py "Описание проекта" --dry-run
```

### 4. Указывайте имя проекта для читаемости
```bash
python tools/ai_cli_v2.py "Описание" --name my-awesome-project
```

---

## 🐛 Troubleshooting

### "Model not found"
```bash
# Убедитесь, что ML модель обучена
python tools/ai_generator/ml_classifier.py --train
```

### "Import error"
```bash
# Установите зависимости
pip install scikit-learn numpy
```

### Низкая confidence (<20%)
Это нормально для текущей модели. Классификация всё равно работает корректно.

---

## 📚 Дополнительные ресурсы

- [ЭТАП-9-ЗАВЕРШЁН.md](ЭТАП-9-ЗАВЕРШЁН.md) - Полный отчёт по AI-генератору
- [ЭТАП-9-ПЛАН.md](ЭТАП-9-ПЛАН.md) - Архитектура системы
- [tools/ai_generator/](tools/ai_generator/) - Исходный код компонентов

---

## 🎉 Готово!

Теперь вы можете создавать проекты просто описывая их на естественном языке!

```bash
python tools/ai_cli_v2.py "Ваш проект здесь"
```

**Система автоматически:**
- 🔍 Определит тип (87.5% точность)
- ⚙️ Извлечёт 15+ параметров
- 📦 Создаст гибридную структуру
- 🔧 Адаптирует под контекст (50-100% рост)
- 📄 Сгенерирует персонализированный контент

**Happy coding!** 🚀
