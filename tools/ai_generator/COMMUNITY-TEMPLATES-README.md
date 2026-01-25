# Community Templates - Marketplace для шаблонов

🌐 **Платформа для обмена и распространения проектных шаблонов**

---

## 📋 Обзор

Community Templates - это marketplace где разработчики могут:
- ✅ **Публиковать** свои проектные шаблоны
- ✅ **Находить** и устанавливать готовые шаблоны
- ✅ **Оценивать** и оставлять reviews
- ✅ **Fork-ать** и кастомизировать существующие шаблоны
- ✅ **Делиться** best practices с сообществом

---

## 🎯 Возможности

### 1. Template Registry
Централизованный реестр всех доступных шаблонов с метаданными

### 2. Search & Discovery
Мощный поиск по категориям, тегам, языкам, рейтингу

### 3. Ratings & Reviews
Система отзывов для оценки качества шаблонов

### 4. Fork & Customize
Возможность fork-а шаблонов для создания собственных вариантов

### 5. Version Management
Поддержка версий шаблонов и changelog

---

## 🚀 Quick Start

### Установка

```bash
# Marketplace использует локальное хранилище
# Автоматически создаётся в ~/.ai_generator/marketplace
```

### Поиск шаблонов

```bash
# Поиск web-приложений
python marketplace_cli.py search --category web_app

# Поиск по языку
python marketplace_cli.py search --language python --min-rating 4.0

# Поиск по тегам
python marketplace_cli.py search --tags "react,typescript"

# Топ популярных
python marketplace_cli.py popular --limit 10
```

### Установка шаблона

```bash
# Установка по ID
python marketplace_cli.py install abc123def456

# С кастомным именем
python marketplace_cli.py install abc123def456 --name my-awesome-project

# В определённую директорию
python marketplace_cli.py install abc123def456 --output ./projects
```

### Публикация шаблона

```bash
python marketplace_cli.py publish ./my-template \
  --name "react-typescript-starter" \
  --display-name "React + TypeScript Starter" \
  --description "Modern React app with TypeScript, Redux, and testing" \
  --author "John Doe" \
  --email "john@example.com" \
  --category "web_app" \
  --language "javascript" \
  --framework "react" \
  --tags "react,typescript,redux,testing" \
  --github-url "https://github.com/johndoe/react-ts-starter"
```

---

## 📚 CLI Commands

### `search` - Поиск шаблонов

```bash
marketplace-cli search [OPTIONS]

Options:
  --query TEXT           Search query
  --category TEXT        Category (web_app, ml_system, fintech, etc.)
  --tags TEXT            Tags (comma-separated)
  --language TEXT        Language (python, javascript, java, etc.)
  --min-rating FLOAT     Minimum rating (0.0-5.0)
  --sort-by TEXT         Sort by (downloads|rating|created_at|updated_at)
  --limit INT            Max results (default: 20)
```

**Примеры:**

```bash
# Все Python ML шаблоны
marketplace-cli search --category ml_system --language python

# Высокорейтинговые React шаблоны
marketplace-cli search --framework react --min-rating 4.5

# Недавние Django шаблоны
marketplace-cli search --tags django --sort-by created_at
```

### `info` - Информация о шаблоне

```bash
marketplace-cli info TEMPLATE_ID
```

**Пример:**

```bash
marketplace-cli info abc123def456

# Output:
# ==================================================
# 📦 React + TypeScript Starter
# ==================================================
#
# ID: abc123def456
# Category: web_app
# Language: javascript
# Framework: react
#
# Author: John Doe
# Email: john@example.com
#
# ⭐ 4.8/5.0 (47 reviews) | 📥 1,234 downloads
#
# Description:
# Modern React application starter with TypeScript...
```

### `install` - Установка шаблона

```bash
marketplace-cli install TEMPLATE_ID [OPTIONS]

Options:
  --name TEXT      Project name (default: template name)
  --output PATH    Output directory (default: current directory)
```

### `publish` - Публикация шаблона

```bash
marketplace-cli publish SOURCE_PATH [OPTIONS]

Required:
  --name TEXT            Template name (slug-friendly)
  --description TEXT     Description
  --author TEXT          Author name
  --category TEXT        Category
  --language TEXT        Programming language

Optional:
  --display-name TEXT    Display name (default: name)
  --email TEXT           Author email
  --framework TEXT       Framework
  --version TEXT         Version (default: 1.0.0)
  --license TEXT         License (default: MIT)
  --tags TEXT            Tags (comma-separated)
  --github-url TEXT      GitHub URL
  --homepage-url TEXT    Homepage URL
```

### `fork` - Fork шаблона

```bash
marketplace-cli fork TEMPLATE_ID [OPTIONS]

Required:
  --name TEXT           New template name
  --author TEXT         Your name

Optional:
  --description TEXT    Description (default: "Fork of...")
  --category TEXT       Category
  --tags TEXT           Tags
```

### `review` - Добавить отзыв

```bash
marketplace-cli review TEMPLATE_ID [OPTIONS]

Required:
  --author TEXT        Your name
  --rating INT         Rating (1-5)
  --title TEXT         Review title
  --comment TEXT       Review comment
```

**Пример:**

```bash
marketplace-cli review abc123def456 \
  --author "Jane Smith" \
  --rating 5 \
  --title "Excellent starter template!" \
  --comment "Saved me hours of setup. Everything works out of the box."
```

### `featured` - Featured шаблоны

```bash
marketplace-cli featured [--limit INT]
```

### `popular` - Популярные шаблоны

```bash
marketplace-cli popular [--limit INT]
```

---

## 🐍 Python API

### Базовое использование

```python
from pathlib import Path
from template_marketplace import TemplateMarketplace

# Создание marketplace
marketplace = TemplateMarketplace(Path.home() / '.ai_generator' / 'marketplace')

# Поиск
results = marketplace.search_templates(
    category='web_app',
    language='python',
    min_rating=4.0,
    limit=10
)

for template in results:
    print(f"{template.display_name} - ⭐ {template.rating}/5.0")

# Установка
project_path = marketplace.install_template(
    template_id='abc123def456',
    destination=Path('./projects'),
    project_name='my-project'
)

print(f"Installed to: {project_path}")
```

### Публикация шаблона

```python
metadata = {
    'name': 'django-rest-starter',
    'display_name': 'Django REST API Starter',
    'description': 'Production-ready Django REST framework template',
    'author': 'John Doe',
    'author_email': 'john@example.com',
    'category': 'api_service',
    'language': 'python',
    'framework': 'django',
    'tags': ['django', 'rest', 'api', 'postgresql'],
    'license': 'MIT',
    'github_url': 'https://github.com/johndoe/django-rest-starter'
}

template_id = marketplace.publish_template(
    source_path=Path('./my-django-template'),
    metadata=metadata
)

print(f"Published: {template_id}")
```

### Fork шаблона

```python
new_metadata = {
    'name': 'django-rest-graphql',
    'author': 'Jane Smith',
    'description': 'Django REST + GraphQL integration',
    'tags': ['django', 'rest', 'graphql']
}

new_template_id = marketplace.fork_template(
    template_id='abc123def456',
    new_metadata=new_metadata
)

print(f"Forked: {new_template_id}")
```

### Добавление отзыва

```python
marketplace.add_review(
    template_id='abc123def456',
    author='Bob Johnson',
    rating=5,
    title='Perfect for startups',
    comment='Used this for 3 projects. Solid foundation with all essentials.'
)
```

### Расширенный поиск

```python
# Поиск с множественными фильтрами
results = marketplace.search_templates(
    query='machine learning',
    category='ml_system',
    tags=['tensorflow', 'pytorch'],
    language='python',
    min_rating=4.0,
    sort_by='rating',
    limit=20
)

# Featured шаблоны
featured = marketplace.registry.get_featured(limit=10)

# Популярные
popular = marketplace.registry.get_popular(limit=10)

# Недавние
recent = marketplace.registry.get_recent(limit=10)
```

### Детальная информация

```python
info = marketplace.get_template_info('abc123def456')

print(f"Template: {info['metadata']['display_name']}")
print(f"Rating: {info['stats']['rating']}/5.0")
print(f"Downloads: {info['stats']['downloads']}")
print(f"Reviews: {info['stats']['reviews_count']}")

# Отзывы
for review in info['reviews']:
    print(f"\n{'⭐' * review['rating']} - {review['title']}")
    print(f"by {review['author']}: {review['comment']}")
```

---

## 📦 Структура Template

### Минимальный template

```
my-template/
├── README.md
├── src/
│   └── main.py
└── requirements.txt
```

### Рекомендуемая структура

```
my-template/
├── README.md              # Описание шаблона
├── TEMPLATE.md           # Инструкции по использованию
├── LICENSE               # Лицензия
├── .gitignore
├── src/                  # Исходный код
│   ├── __init__.py
│   └── main.py
├── tests/                # Тесты
│   └── test_main.py
├── docs/                 # Документация
│   └── guide.md
├── examples/             # Примеры
│   └── example.py
├── requirements.txt      # Зависимости
└── setup.py             # Setup скрипт
```

### Metadata best practices

```python
metadata = {
    # Обязательные поля
    'name': 'my-template',              # Slug-friendly
    'description': 'Clear description',  # 100-200 chars
    'author': 'Your Name',
    'category': 'web_app',              # Выберите подходящую
    'language': 'python',

    # Рекомендуемые
    'display_name': 'My Awesome Template',
    'framework': 'django',
    'tags': ['django', 'rest', 'api'],  # 3-7 тегов
    'license': 'MIT',
    'github_url': 'https://github.com/...',

    # Опциональные
    'author_email': 'you@example.com',
    'homepage_url': 'https://...',
    'version': '1.0.0'
}
```

---

## 🏷️ Categories

Доступные категории:

- `web_app` - Web приложения
- `mobile_app` - Мобильные приложения
- `ml_system` - ML/AI системы
- `data_analytics` - Data analytics
- `api_service` - API сервисы
- `fintech` - Финтех
- `ecommerce` - E-commerce
- `blockchain` - Blockchain
- `game` - Игры
- `automation` - Автоматизация
- `enterprise_system` - Enterprise системы
- `iot` - IoT
- `devtools` - Dev инструменты

---

## 🔖 Tags Best Practices

### Good tags

✅ Технологии: `react`, `django`, `tensorflow`, `postgresql`
✅ Patterns: `mvc`, `microservices`, `rest`, `graphql`
✅ Features: `auth`, `payments`, `real-time`, `analytics`
✅ Use cases: `starter`, `boilerplate`, `production-ready`

### Bad tags

❌ Слишком общие: `code`, `project`, `app`
❌ Дубликаты category: `web`, `mobile` (если category уже `web_app`)
❌ Subjective: `best`, `awesome`, `cool`

---

## ⭐ Ratings & Reviews

### Добавление отзыва

```python
marketplace.add_review(
    template_id='abc123',
    author='Your Name',
    rating=5,  # 1-5
    title='Short title',
    comment='Detailed feedback about the template...'
)
```

### Review guidelines

**Good reviews:**
- ✅ Specific (упомяните что понравилось/не понравилось)
- ✅ Constructive (предложите улучшения)
- ✅ Honest (объективная оценка)
- ✅ Detailed (помогите другим принять решение)

**Example:**

```
Rating: 5/5
Title: "Excellent Django starter for APIs"

Comment: "This template saved me 10+ hours of setup. The Django REST
framework configuration is production-ready with JWT auth, pagination,
and proper error handling. Documentation is clear. Only minor issue -
could use Docker Compose for local development. Highly recommended
for API projects."
```

---

## 🍴 Forking Templates

### Когда fork-ать?

- ✅ Хотите кастомизировать под свои нужды
- ✅ Добавляете новые features
- ✅ Адаптируете под другой use case
- ✅ Создаёте вариант для другого языка/фрейморка

### Fork workflow

```bash
# 1. Fork
marketplace-cli fork abc123def456 \
  --name "my-customized-version" \
  --author "Your Name" \
  --description "Fork with GraphQL support"

# 2. Modify
cd ~/.ai_generator/marketplace/templates/[new-id]
# Make your changes...

# 3. Publish (optional)
marketplace-cli publish ... --name "my-customized-version"
```

### Fork etiquette

- ✅ Сохраняйте оригинальную лицензию
- ✅ Указывайте автора оригинала
- ✅ Документируйте свои изменения
- ✅ Consider contributing back если улучшения универсальные

---

## 📊 Statistics

### Template metrics

```python
info = marketplace.get_template_info('template_id')

print(f"Downloads: {info['stats']['downloads']}")
print(f"Rating: {info['stats']['rating']}/5.0")
print(f"Reviews: {info['stats']['reviews_count']}")
```

### Leaderboards

```python
# Топ по downloads
popular = marketplace.registry.get_popular(limit=10)

# Топ по rating
top_rated = marketplace.search_templates(
    min_rating=4.5,
    sort_by='rating',
    limit=10
)

# Featured
featured = marketplace.registry.get_featured()
```

---

## 🔒 Security & Trust

### Verified templates

Templates помеченные как `is_verified=True` прошли проверку:
- ✅ Код reviewed
- ✅ Нет malware
- ✅ Best practices
- ✅ Актуальные зависимости

### Featured templates

Featured templates (`is_featured=True`) - высококачественные шаблоны:
- ✅ Высокий рейтинг (4.5+)
- ✅ Активное использование
- ✅ Хорошая документация
- ✅ Поддерживаются автором

### Before installing

- 📝 Проверьте reviews
- 📊 Посмотрите рейтинг
- 🐙 Изучите GitHub repo (если доступен)
- 📆 Проверьте когда обновлялся
- 👤 Проверьте автора

---

## 🎨 Examples

### Example 1: ML Research Template

```bash
# Публикация
marketplace-cli publish ./ml-research-template \
  --name "ml-research-template" \
  --display-name "ML Research Project Template" \
  --description "Template for ML research with experiment tracking, visualization, and paper reproduction" \
  --author "Dr. Smith" \
  --email "smith@university.edu" \
  --category "ml_system" \
  --language "python" \
  --framework "pytorch" \
  --tags "pytorch,research,experiments,wandb,mlflow" \
  --license "MIT" \
  --github-url "https://github.com/drsmith/ml-research"

# Установка
marketplace-cli install abc123 --name my-research-project

# Отзыв
marketplace-cli review abc123 \
  --author "PhD Student" \
  --rating 5 \
  --title "Perfect for research" \
  --comment "Used for 3 papers. Wandb integration is excellent."
```

### Example 2: Django SaaS Starter

```bash
# Fork существующего Django template
marketplace-cli fork def456 \
  --name "django-saas-stripe" \
  --author "SaaS Dev" \
  --description "Django SaaS with Stripe integration"

# Modify forked template...
# Add Stripe integration, subscription models, etc.

# Publish customized version
marketplace-cli publish ~/.ai_generator/marketplace/templates/xyz789 \
  --name "django-saas-stripe" \
  --display-name "Django SaaS + Stripe" \
  --description "Complete SaaS starter with Stripe subscriptions" \
  --author "SaaS Dev" \
  --category "web_app" \
  --language "python" \
  --framework "django" \
  --tags "django,saas,stripe,subscriptions,payments"
```

---

## 🚀 Advanced Usage

### Custom marketplace location

```python
from pathlib import Path
from template_marketplace import TemplateMarketplace

# Custom location
marketplace = TemplateMarketplace(Path('/custom/path/marketplace'))
```

### Batch operations

```python
# Install multiple templates
template_ids = ['abc123', 'def456', 'ghi789']

for tid in template_ids:
    project_path = marketplace.install_template(
        template_id=tid,
        destination=Path('./projects')
    )
    print(f"✅ {project_path}")
```

### Programmatic search

```python
# Complex search logic
def find_best_template(use_case: str, language: str):
    """Find best template for use case"""

    results = marketplace.search_templates(
        query=use_case,
        language=language,
        min_rating=4.0,
        sort_by='rating',
        limit=5
    )

    if not results:
        # Fallback to less strict search
        results = marketplace.search_templates(
            query=use_case,
            language=language,
            min_rating=3.0,
            limit=5
        )

    return results[0] if results else None

# Usage
best = find_best_template('rest api', 'python')
if best:
    print(f"Recommended: {best.display_name}")
    marketplace.install_template(best.id, Path('./projects'))
```

---

## 📚 Related Modules

- `multi_label_classifier.py` - AI classification
- `github_integration.py` - GitHub automation
- `llm_content_generator.py` - Content generation

---

## 🗺️ Roadmap

### Planned Features

- [ ] Web UI для marketplace
- [ ] REST API для remote access
- [ ] Template versioning с changelog
- [ ] Dependency management между templates
- [ ] Automated testing для templates
- [ ] Template analytics dashboard
- [ ] Collaboration features (co-authors)
- [ ] Template bundles (collections)

---

## ✅ Best Practices

### For Template Authors

- ✅ Включите подробный README
- ✅ Добавьте LICENSE файл
- ✅ Используйте semantic versioning
- ✅ Документируйте dependencies
- ✅ Добавьте examples
- ✅ Включите tests
- ✅ Поддерживайте актуальность

### For Template Users

- ✅ Читайте documentation
- ✅ Проверяйте compatibility
- ✅ Оставляйте reviews
- ✅ Report issues авторам
- ✅ Contribute improvements
- ✅ Share с сообществом

---

**Ready to share your templates with the community!** 🚀
