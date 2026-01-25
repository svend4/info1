# Быстрый старт с генератором шаблонов проектов
*Уровень абстракции: α=-3 (практическое руководство)*
*Статус: ⇓ ВНИЗ (от генератора к готовому проекту)*
*Дата создания: 2026-01-24*

---

## 🚀 За 2 минуты к готовому проекту

Генератор шаблонов проектов — это инструмент ЭТАПА 8, который создаёт полноценную структуру проекта с интеграцией методологии ⇑⇓↔ для **любого из 16 типов проектов**.

---

## ⚡ Самый простой способ

### Шаг 1: Выберите тип проекта

```bash
python tools/project_template_generator.py --name my-project --type software
```

**Готово!** Проект создан в папке `my-project/`.

### Шаг 2: Перейдите в проект

```bash
cd my-project
ls
```

**Вы увидите:**
```
01-Концепция/
02-Архитектура/
03-Реализация/
docs/
tools/
src/
tests/
examples/
README.md
МЕТОДОЛОГИЯ.md
METRICS.md
.methodology.json
```

### Шаг 3: Проверьте метрики

```bash
python3 tools/health_metrics.py
```

**Результат:**
```
=== Метрики здоровья проекта ===

📊 Connection Density (CD): XX.XX%
   Целевой диапазон: 10-20%
   Статус: ✅ В норме

📊 Vertical Traceability (VT): XX.XX%
   Целевой диапазон: 40-60%
   Статус: ✅ В норме

📊 Cycle Rate (CR): X.XX
   Целевой диапазон: 0.8-1.2
   Статус: ✅ В норме

📊 Direction Balance (DB): XXX.XX%
   Целевой диапазон: 80-120%
   Статус: ✅ В норме
```

---

## 🎯 Все 16 типов проектов

### Технические
```bash
# Разработка ПО
python tools/project_template_generator.py --name web-app --type software

# Научное исследование
python tools/project_template_generator.py --name my-study --type research
```

### Бизнес и управление
```bash
# Бизнес-проект
python tools/project_template_generator.py --name startup --type business

# Финансы
python tools/project_template_generator.py --name fund --type finance

# Государственный проект
python tools/project_template_generator.py --name policy --type government

# Некоммерческая организация
python tools/project_template_generator.py --name charity --type nonprofit
```

### Производство и сельское хозяйство
```bash
# Производство
python tools/project_template_generator.py --name factory --type manufacturing

# Сельское хозяйство
python tools/project_template_generator.py --name farm --type agriculture
```

### Образование и здравоохранение
```bash
# Образование
python tools/project_template_generator.py --name course --type education

# Здравоохранение
python tools/project_template_generator.py --name clinic --type healthcare
```

### Юриспруденция и искусство
```bash
# Юридический проект
python tools/project_template_generator.py --name case --type legal

# Творческий проект
python tools/project_template_generator.py --name exhibition --type arts
```

### Спорт и гостеприимство
```bash
# Спортивный проект
python tools/project_template_generator.py --name academy --type sports

# Гостеприимство
python tools/project_template_generator.py --name hotel --type hospitality
```

### Розничная торговля и хобби
```bash
# Розничная торговля
python tools/project_template_generator.py --name store --type retail

# Хобби-проект
python tools/project_template_generator.py --name my-hobby --type hobby
```

---

## 🔧 Дополнительные опции

### Интеграция с Git

```bash
python tools/project_template_generator.py \
  --name my-project \
  --type software \
  --git
```

**Результат:**
- ✅ Инициализирован git repository
- ✅ Создан .gitignore
- ✅ Сделан initial commit

### Добавление CI/CD

```bash
python tools/project_template_generator.py \
  --name my-project \
  --type software \
  --ci
```

**Результат:**
- ✅ Создана .github/workflows/
- ✅ Добавлен CI workflow
- ✅ Добавлен тестовый pipeline

### Интеграция с GitHub

```bash
python tools/project_template_generator.py \
  --name my-project \
  --type software \
  --github \
  --github-visibility public
```

**Результат:**
- ✅ Создан GitHub repository
- ✅ Код запушен на GitHub
- ✅ Настроены Actions

### Добавление security инструментов

```bash
python tools/project_template_generator.py \
  --name my-project \
  --type software \
  --security
```

**Результат:**
- ✅ Добавлен Dependabot
- ✅ Добавлен CodeQL
- ✅ Добавлен security scanning

### Все опции сразу

```bash
python tools/project_template_generator.py \
  --name my-project \
  --type software \
  --ci-all
```

**Включает:**
- Git initialization
- CI/CD workflows
- Security scanning
- Quality checks
- Deploy pipeline

---

## 📊 Интерактивный режим

Не хотите запоминать все опции? Используйте интерактивный режим:

```bash
python tools/project_template_generator.py --interactive
```

**Генератор спросит:**
```
? Введите название проекта: my-awesome-project
? Выберите тип проекта:
  > software
    research
    business
    education
    [...]
? Инициализировать git? (Y/n): Y
? Добавить CI/CD? (Y/n): Y
? Добавить GitHub integration? (Y/n): n
```

---

## 🎨 Примеры использования

### Пример 1: Веб-приложение с полной настройкой

```bash
python tools/project_template_generator.py \
  --name my-web-app \
  --type software \
  --git \
  --ci \
  --security \
  --quality
```

**Что создано:**
- Структура software проекта
- Git repository с .gitignore
- GitHub Actions workflows (CI/CD)
- Security scanning (Dependabot, CodeQL)
- Quality checks (linting, formatting)
- Методология ⇑⇓↔ интегрирована
- Инструменты метрик включены

### Пример 2: Научное исследование

```bash
python tools/project_template_generator.py \
  --name cancer-study \
  --type research \
  --git
```

**Что создано:**
- Структура research проекта
- Папки: data/, analysis/, papers/, protocols/
- RESEARCH-PROTOCOL-TEMPLATE.md
- Инструменты для расчёта метрик
- Git repository

### Пример 3: Стартап

```bash
python tools/project_template_generator.py \
  --name fintech-startup \
  --type business \
  --templates
```

**Что создано:**
- Структура business проекта
- BUSINESS-PLAN-TEMPLATE.md (1200+ строк)
- MARKETING-STRATEGY-TEMPLATE.md
- Шаблоны для pitch deck
- Финансовые модели

---

## 📂 Структура созданного проекта

### Общая для всех типов

```
my-project/
├── 01-Концепция/           # Концептуальные документы (α=+1)
├── 02-Архитектура/         # Архитектурные решения (α=0)
├── 03-Реализация/          # Реализация проекта (α=-1)
├── docs/                   # Документация (α=-2)
├── tools/                  # Инструменты
│   ├── health_metrics.py   # Расчёт метрик CD, VT, CR, DB
│   └── README.md
├── README.md               # Главная страница (α=+1)
├── МЕТОДОЛОГИЯ.md          # Методология ⇑⇓↔ (α=+2)
├── METRICS.md              # Метрики проекта (α=+1)
└── .methodology.json       # Конфигурация методологии
```

### Специфичные для типа

#### Software
```
src/                # Исходный код
tests/              # Тесты
examples/           # Примеры использования
```

#### Healthcare
```
protocols/          # Медицинские протоколы
cases/              # Клинические случаи
research/           # Медицинские исследования
```

#### Agriculture
```
crops/              # Управление культурами
livestock/          # Управление скотом
equipment/          # Оборудование
```

#### Finance
```
portfolios/         # Портфели инвестиций
analysis/           # Финансовый анализ
reports/            # Отчёты
```

---

## 🎓 Что дальше?

### После создания проекта

1. **Прочитайте README.md** проекта
   ```bash
   cat README.md
   ```

2. **Изучите МЕТОДОЛОГИЮ.md**
   ```bash
   cat МЕТОДОЛОГИЯ.md
   ```

3. **Запустите метрики**
   ```bash
   python3 tools/health_metrics.py
   ```

4. **Начните разработку**
   - Добавьте документы в 01-Концепция/
   - Опишите архитектуру в 02-Архитектура/
   - Реализуйте проект в 03-Реализация/

5. **Отслеживайте прогресс**
   ```bash
   python3 tools/health_metrics.py  # После каждого цикла
   ```

---

## 🔍 Проверка созданной структуры

### Быстрая проверка

```bash
# Создать проект
python tools/project_template_generator.py --name test-project --type software

# Перейти в проект
cd test-project

# Проверить структуру
tree -L 2

# Проверить файлы
ls -la

# Проверить метрики
python3 tools/health_metrics.py
```

### Проверка интеграции методологии

```bash
# Проверить .methodology.json
cat .methodology.json

# Проверить α-уровни в документах
grep "Уровень абстракции" README.md
grep "Уровень абстракции" МЕТОДОЛОГИЯ.md

# Проверить статусы ⇑⇓↔
grep "Статус:" README.md
```

---

## ❓ Часто задаваемые вопросы

### Можно ли изменить тип проекта после создания?

Нет, тип проекта фиксируется при создании. Однако вы можете:
- Создать новый проект нужного типа
- Скопировать ваши файлы в новый проект

### Как добавить свой тип проекта?

1. Создайте папку в `tools/templates/your-type/`
2. Добавьте шаблоны в эту папку
3. Обновите `TEMPLATE_MAPPING` в `project_template_generator.py`
4. Добавьте логику создания структуры в `create_project_structure()`

### Можно ли использовать несколько типов одновременно?

Сейчас нет, но запланировано в ЭТАПЕ 9 (AI-assisted generation):
- Гибридная генерация (multi-domain)
- Автоматическое определение зависимостей
- Интеграция между доменами

### Как обновить уже созданный проект?

Метрики и инструменты можно обновить:
```bash
# Скопировать новую версию health_metrics.py
cp tools/health_metrics.py your-project/tools/

# Скопировать новые шаблоны
cp tools/templates/software/* your-project/docs/templates/
```

---

## 📚 Дополнительные ресурсы

### Документация

- [README.md](../README.md) — главная документация проекта
- [ЭТАП-8-COMPLETION-REPORT.md](../ЭТАП-8-COMPLETION-REPORT.md) — отчёт о завершении ЭТАПА 8
- [NEXT-STEPS.md](../NEXT-STEPS.md) — планы следующих этапов
- [tools/templates/README.md](templates/README.md) — документация шаблонов

### Примеры

- [demo-projects/](../demo-projects/) — 6 готовых демо-проектов
- [demo-projects/README.md](../demo-projects/README.md) — описание демо-проектов

### Инструменты

- [project_template_generator.py](project_template_generator.py) — исходный код генератора
- [health_metrics.py](health_metrics.py) — расчёт метрик CD, VT, CR, DB

---

## 🎯 Примеры команд для копирования

### Создать software проект
```bash
python tools/project_template_generator.py --name my-app --type software --git --ci
```

### Создать research проект
```bash
python tools/project_template_generator.py --name my-study --type research --git
```

### Создать business проект
```bash
python tools/project_template_generator.py --name my-startup --type business --templates
```

### Создать healthcare проект
```bash
python tools/project_template_generator.py --name clinic --type healthcare --git --security
```

### Создать agriculture проект
```bash
python tools/project_template_generator.py --name farm --type agriculture --git
```

### Создать проект с полной настройкой
```bash
python tools/project_template_generator.py \
  --name full-project \
  --type software \
  --ci-all
```

---

## 🚀 Начните прямо сейчас!

**Самая простая команда:**
```bash
python tools/project_template_generator.py --name my-project --type software
```

**За 2 минуты вы получите:**
- ✅ Полноценную структуру проекта
- ✅ Интеграцию методологии ⇑⇓↔
- ✅ Автоматический расчёт метрик
- ✅ Документацию и примеры
- ✅ Готовность к разработке

**Методология ⇑⇓↔ работает для вас! 🎯**

---

*Создано: 2026-01-24*
*Версия: 1.0*
*Статус: ⇓ Практическое руководство*
*ЭТАП 8: 100% покрытие всех 16 типов проектов* 🏆
