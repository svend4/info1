# GitHub Integration - Автоматическое создание репозиториев

🚀 **Автоматизация создания GitHub проектов с AI-generated структурой**

---

## 📋 Обзор

GitHub Integration позволяет автоматически создавать полноценные GitHub репозитории с:
- ✅ AI-generated структурой проекта
- ✅ Initial commit со всеми файлами
- ✅ Issue templates (bug report, feature request, question)
- ✅ Pull Request template
- ✅ GitHub Actions CI/CD workflows
- ✅ Labels для организации issues
- ✅ GitHub Project board с колонками
- ✅ Branch protection rules
- ✅ .gitignore под тип проекта

---

## 🎯 Возможности

### 1. Полная автоматизация
Один команда → готовый GitHub репозиторий с полной инфраструктурой

### 2. AI-Powered
Анализ описания проекта и генерация оптимальной структуры через ML + LLM

### 3. Best Practices
Автоматическая настройка CI/CD, issue templates, labels по industry standards

### 4. Гибкость
Поддержка private/public репозиториев, организаций, кастомизация всех параметров

---

## 🚀 Quick Start

### Установка

```bash
# Установка зависимостей
pip install requests pyyaml

# Настройка GitHub token
export GITHUB_TOKEN="ghp_your_token_here"
export GITHUB_USERNAME="your_username"
```

### Базовое использование

```bash
python github_project_creator.py \
  --description "AI-powered платформа для анализа медицинских данных" \
  --name "medical-data-analyzer" \
  --username "myusername"
```

### С дополнительными опциями

```bash
python github_project_creator.py \
  --description "Blockchain-based supply chain tracking system" \
  --name "supply-chain-tracker" \
  --username "myusername" \
  --organization "my-org" \
  --private \
  --output ./projects
```

---

## 🔐 Authentication

### Способ 1: Environment Variable (рекомендуется)

```bash
export GITHUB_TOKEN="ghp_xxxxxxxxxxxxx"
export GITHUB_USERNAME="your_username"
```

### Способ 2: GitHub CLI

```bash
# Установка GitHub CLI
brew install gh  # macOS
# или
sudo apt install gh  # Ubuntu

# Аутентификация
gh auth login

# Token будет автоматически использован
```

### Способ 3: Прямая передача

```python
from github_integration import GitHubAPI, GitHubConfig

config = GitHubConfig(
    token="ghp_your_token",
    username="your_username"
)

api = GitHubAPI(config)
```

---

## 📚 Подробное использование

### Программное использование (Python API)

```python
from github_project_creator import GitHubProjectCreator
from github_integration import GitHubConfig

# Конфигурация
config = GitHubConfig(
    token="ghp_xxxxx",
    username="myusername",
    organization=None,  # Опционально
    private=False
)

# Создание creator
creator = GitHubProjectCreator(config)

# Создание проекта
result = creator.create_complete_project(
    description="AI-powered финтех платформа для микрокредитования",
    project_name="micro-lending-platform",  # Опционально (auto-generate)
    private=False,
    output_dir=Path("./projects"),
    push_to_github=True,
    setup_project_board=True
)

# Результат
print(f"Repository URL: {result['repo_info'].html_url}")
print(f"Local path: {result['project_path']}")
print(f"Type: {result['classification'].primary_type}")
```

### CLI использование

```bash
# Полная команда со всеми опциями
python github_project_creator.py \
  --description "Описание проекта для AI анализа" \
  --name "project-name" \
  --username "github_username" \
  --organization "org_name" \
  --private \
  --output ./my_projects \
  --no-push \
  --no-project-board

# Минимальная команда (остальное auto)
python github_project_creator.py \
  --description "Онлайн-платформа для аренды недвижимости" \
  --username "myuser"
```

**Параметры:**

| Параметр | Описание | Обязательный |
|----------|----------|--------------|
| `--description` | Описание проекта для AI анализа | ✅ Да |
| `--name` | Название проекта (auto-generate если нет) | Нет |
| `--username` | GitHub username | ✅ Да* |
| `--organization` | GitHub organization | Нет |
| `--private` | Приватный репозиторий | Нет |
| `--output` | Директория для локального проекта | Нет |
| `--no-push` | Не push в GitHub (только локально) | Нет |
| `--no-project-board` | Не создавать Project board | Нет |

*Можно через `GITHUB_USERNAME` environment variable

---

## 🏗️ Что создаётся

### 1. Структура проекта
```
project-name/
├── src/                    # Основной код
├── tests/                  # Тесты
├── docs/                   # Документация
├── examples/               # Примеры кода (LLM-generated)
├── .github/
│   ├── workflows/
│   │   └── ci.yml         # CI/CD workflow
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.md
│   │   ├── feature_request.md
│   │   └── question.md
│   └── PULL_REQUEST_TEMPLATE.md
├── README.md              # LLM-generated
├── ARCHITECTURE.md        # LLM-generated
├── CONTRIBUTING.md        # LLM-generated
├── CHECKLIST.md          # LLM-generated
├── .gitignore
└── requirements.txt / package.json
```

### 2. GitHub настройки

- **Repository**: Создан на GitHub
- **Initial commit**: Вся структура закоммичена и запушена
- **Labels**: 11 стандартных labels (bug, enhancement, priority:high, etc.)
- **Issue templates**: 3 шаблона для разных типов issues
- **PR template**: Стандартный шаблон для pull requests
- **Workflows**: CI/CD pipeline (тесты, линтинг, coverage)
- **Project board**: Kanban board с колонками (Backlog, To Do, In Progress, Review, Done)

---

## 🔧 API Reference

### GitHubAPI

Wrapper вокруг GitHub REST API.

```python
from github_integration import GitHubAPI, GitHubConfig

config = GitHubConfig(token="...", username="...")
api = GitHubAPI(config)

# Создание репозитория
repo = api.create_repository(
    name="my-project",
    description="Project description",
    private=False,
    auto_init=False,
    gitignore_template="python",
    license_template="mit"
)

# Загрузка файла
api.upload_file(
    repo_full_name="username/repo",
    file_path="README.md",
    content="# My Project",
    commit_message="Add README"
)

# Создание issue template
api.create_issue_template(
    repo_full_name="username/repo",
    template_name="bug_report.md",
    template_content="..."
)

# Создание workflow
api.create_workflow(
    repo_full_name="username/repo",
    workflow_name="ci.yml",
    workflow_content="..."
)

# Создание labels
api.create_labels(
    repo_full_name="username/repo",
    labels=[
        {"name": "bug", "color": "d73a4a", "description": "Bug"},
        {"name": "enhancement", "color": "a2eeef", "description": "Feature"}
    ]
)

# Branch protection
api.enable_branch_protection(
    repo_full_name="username/repo",
    branch="main",
    require_reviews=True,
    required_approvals=1
)

# GitHub Project
project = api.create_project(
    repo_full_name="username/repo",
    name="Development Board",
    body="Main project board"
)

api.create_project_columns(
    project_id=project['id'],
    columns=["To Do", "In Progress", "Done"]
)
```

### LocalGitManager

Управление локальным git репозиторием.

```python
from github_integration import LocalGitManager
from pathlib import Path

git = LocalGitManager(Path("./my-project"))

# Инициализация repo
git.init_repo(default_branch="main")

# Создание .gitignore
git.create_gitignore(template="python")  # или "node", "java"

# Добавление файлов
git.add_all()

# Commit
git.commit("Initial commit")

# Добавление remote
git.add_remote("origin", "https://github.com/user/repo.git")

# Push
git.push(remote="origin", branch="main", set_upstream=True)
```

### GitHubProjectCreator

High-level interface для создания полного проекта.

```python
from github_project_creator import GitHubProjectCreator
from github_integration import GitHubConfig

config = GitHubConfig(token="...", username="...")
creator = GitHubProjectCreator(config)

result = creator.create_complete_project(
    description="Project description for AI analysis",
    project_name="my-project",
    private=False,
    output_dir=Path("./projects"),
    push_to_github=True,
    setup_project_board=True
)

# result содержит:
# - repo_info: RepoInfo
# - project_path: Path
# - classification: MLResult
# - structure: AdaptedStructure
```

---

## 🎨 Примеры

### Пример 1: Финтех стартап

```bash
python github_project_creator.py \
  --description "AI-powered платформа для автоматического кредитного скоринга с интеграцией банковских API" \
  --name "credit-scoring-ai" \
  --username "myuser" \
  --private
```

**Результат:**
- Тип: `fintech`
- Структура: ML модели, API интеграции, безопасность, compliance
- CI/CD: Python тесты, linting, security scanning
- GitHub Project: Настроен Kanban board

### Пример 2: E-commerce платформа

```bash
python github_project_creator.py \
  --description "Marketplace для аренды спортивного оборудования с онлайн-платежами и системой рейтингов" \
  --name "sports-rental-marketplace"
```

**Результат:**
- Тип: `web_app` (hybrid: `ecommerce`, `platform`)
- Структура: Frontend, Backend, Payment integration, Reviews
- CI/CD: Node.js тесты, ESLint, build проверка
- GitHub Project: Backlog с example issues

### Пример 3: ML система

```bash
python github_project_creator.py \
  --description "Система компьютерного зрения для автоматического контроля качества на производстве" \
  --name "vision-quality-control" \
  --organization "my-company"
```

**Результат:**
- Тип: `ml_system` (secondary: `automation`)
- Структура: ML pipeline, data processing, model serving, monitoring
- CI/CD: Python тесты, model validation, Docker build
- GitHub Project: ML workflow columns (Data, Training, Evaluation, Deployment)

---

## ⚙️ Кастомизация

### Issue Templates

Создаёте собственные issue templates:

```python
custom_template = """---
name: Performance Issue
about: Report performance problems
title: '[PERF] '
labels: performance
---

## Description
Describe the performance issue.

## Metrics
Current performance vs expected.
"""

api.create_issue_template(
    repo_full_name="username/repo",
    template_name="performance.md",
    template_content=custom_template
)
```

### Workflows

Кастомные GitHub Actions workflows:

```python
custom_workflow = """
name: Deploy to Production

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy
        run: ./deploy.sh
"""

api.create_workflow(
    repo_full_name="username/repo",
    workflow_name="deploy.yml",
    workflow_content=custom_workflow
)
```

### Labels

Собственные labels:

```python
custom_labels = [
    {"name": "critical", "color": "b60205", "description": "Critical issue"},
    {"name": "security", "color": "ee0701", "description": "Security vulnerability"},
    {"name": "technical-debt", "color": "fbca04", "description": "Technical debt"}
]

api.create_labels(repo_full_name="username/repo", labels=custom_labels)
```

---

## 🔒 Безопасность

### Token Permissions

Требуемые permissions для GitHub token:

- ✅ `repo` - Полный доступ к репозиториям
- ✅ `workflow` - Создание workflows
- ✅ `admin:org` - Если используются organizations (опционально)

### Создание токена

1. GitHub → Settings → Developer settings → Personal access tokens
2. Generate new token (classic)
3. Выбрать scopes: `repo`, `workflow`
4. Скопировать token

### Best Practices

- ✅ Используйте environment variables (не hardcode в коде)
- ✅ Ограничьте срок действия token
- ✅ Используйте минимальные необходимые permissions
- ✅ Не коммитьте token в git
- ✅ Добавьте `.env` в `.gitignore`

---

## 🐛 Troubleshooting

### "Failed to create repository: 401"

**Причина:** Неверный или истёкший GitHub token

**Решение:**
```bash
# Проверьте token
echo $GITHUB_TOKEN

# Создайте новый token на GitHub
# Убедитесь что выбраны нужные scopes
```

### "Failed to create repository: 422"

**Причина:** Репозиторий с таким именем уже существует

**Решение:**
```bash
# Используйте другое имя
python github_project_creator.py \
  --description "..." \
  --name "unique-project-name"
```

### "Permission denied (publickey)"

**Причина:** SSH ключ не настроен

**Решение:**
```bash
# Используем HTTPS вместо SSH (автоматически)
# Или настройте SSH ключ:
ssh-keygen -t ed25519 -C "your_email@example.com"
cat ~/.ssh/id_ed25519.pub
# Добавьте на GitHub → Settings → SSH keys
```

### "GitHub CLI config not found"

**Решение:**
```bash
# Установите GitHub CLI
brew install gh  # macOS
sudo apt install gh  # Ubuntu

# Или используйте environment variable
export GITHUB_TOKEN="ghp_xxxx"
```

---

## 📊 Статистика

**Автоматизация:**
- ⚡ 1 команда → полный GitHub repo
- 📁 10-50 файлов генерируется автоматически
- 🏷️ 11 labels создаётся
- 📋 3 issue templates + 1 PR template
- ⚙️ 1-3 GitHub Actions workflows
- 📊 1 Project board с 5 колонками

**Экономия времени:**
- Manual setup: ~2-3 часа
- С GitHub Integration: ~2-3 минуты
- **Экономия: 95-98%**

---

## 🚀 Roadmap

### Planned Features

- [ ] Support для GitHub Projects (Beta) - новый API
- [ ] Автоматическое создание Wiki
- [ ] Integration с external CI/CD (GitLab CI, CircleCI)
- [ ] Team и collaborators management
- [ ] Deploy keys и secrets setup
- [ ] Webhooks configuration
- [ ] GitHub Pages auto-deploy

---

## 📚 Связанные модули

- `multi_label_classifier.py` - Классификация типа проекта
- `enhanced_parameter_extractor.py` - Извлечение параметров
- `template_composer.py` - Композиция структуры
- `context_aware_adapter.py` - Адаптация под контекст
- `llm_content_generator.py` - Генерация документации

---

## ✅ Чеклист использования

Перед первым использованием:

- [ ] GitHub token создан с нужными permissions
- [ ] Token установлен в environment variable
- [ ] Username указан
- [ ] Dependencies установлены (`pip install requests pyyaml`)
- [ ] AI модели обучены (`ml_classifier.py --train`)

Для каждого проекта:

- [ ] Описание проекта подготовлено
- [ ] Имя проекта выбрано (или auto-generate)
- [ ] Определён public/private статус
- [ ] Output directory указана
- [ ] Запуск команды/скрипта
- [ ] Проверка созданного repo на GitHub
- [ ] Clone и начало работы

---

**Ready to automate your GitHub workflows!** 🚀
