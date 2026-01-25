# AI Generator Quick Start Guide

🚀 **Быстрый старт для использования AI-Powered Project Generator**

---

## 📋 Содержание

1. [Установка](#установка)
2. [Базовое использование](#базовое-использование)
3. [Web интерфейс](#web-интерфейс)
4. [Командная строка](#командная-строка)
5. [Production deployment](#production-deployment)
6. [Примеры](#примеры)

---

## 🔧 Установка

### Предварительные требования

```bash
# Python 3.9+
python --version

# Git
git --version
```

### Установка зависимостей

```bash
# Установка Python зависимостей
pip install -r 08-Программная-реализация/web/requirements-ai.txt

# Дополнительные зависимости для всех вариантов
pip install requests pyyaml schedule matplotlib
```

### Обучение ML модели (первый запуск)

```bash
cd tools/ai_generator
python ml_classifier.py --train

# Проверка модели
python ml_classifier.py --test
```

---

## 🎯 Базовое использование

### Вариант 1: Integrated Workflow (рекомендуется)

**Полный end-to-end процесс одной командой:**

```bash
cd tools/ai_generator

# Demo с примерами
python integrated_workflow.py --demo

# Свой проект
python integrated_workflow.py \
  --description "AI-powered платформа для анализа медицинских данных" \
  --name "medical-data-analyzer" \
  --output ./my_projects
```

**Что происходит:**
1. ✅ AI анализ описания
2. ✅ Генерация структуры
3. ✅ LLM content generation
4. ✅ Создание проекта
5. ✅ Health check

**Результат:**
```
my_projects/medical-data-analyzer/
├── README.md              # AI-generated
├── ARCHITECTURE.md        # AI-generated
├── CONTRIBUTING.md        # AI-generated
├── src/                   # Структура под тип проекта
├── tests/
├── docs/
└── examples/              # Code examples
```

---

## 🌐 Web интерфейс

### Запуск веб-интерфейса

```bash
cd 08-Программная-реализация/web

# Запуск API
python ai_api.py

# Откройте браузер
# http://localhost:5001/ai-generator.html
```

### Использование веб-интерфейса

1. **Описание проекта:** Введите описание в текстовое поле
2. **Или выберите пример:** 4 готовых примера
3. **Analyze:** Анализ без создания файлов
4. **Generate:** Полная генерация проекта

**Пример:**
```
Описание: "Финтех стартап для автоматизации инвестиций"

→ AI анализирует
→ Показывает: тип, параметры, структуру
→ Generate → скачивает ZIP с проектом
```

---

## 💻 Командная строка

### 1. Только AI анализ

```python
from tools.ai_generator.multi_label_classifier import MultiLabelClassifier
from tools.ai_generator.enhanced_parameter_extractor import EnhancedParameterExtractor

classifier = MultiLabelClassifier()
extractor = EnhancedParameterExtractor()

description = "Мобильное приложение для медитации"

result = classifier.classify(description)
params = extractor.extract(description)

print(f"Type: {result.primary_type}")
print(f"Confidence: {result.primary_confidence}")
print(f"Budget: {params.budget}")
print(f"Timeline: {params.timeline}")
```

### 2. Генерация структуры

```bash
cd tools
python project_template_generator.py \
  --name "my-awesome-app" \
  --type "web_app" \
  --output ./projects
```

### 3. GitHub auto-creation

```bash
cd tools/ai_generator

# Настройка
export GITHUB_TOKEN="ghp_your_token"
export GITHUB_USERNAME="your_username"

# Создание
python github_project_creator.py \
  --description "Blockchain supply chain tracker" \
  --name "supply-chain-tracker"

# Результат: полный GitHub repo с initial commit
```

### 4. Marketplace

```bash
cd tools/ai_generator

# Поиск templates
python marketplace_cli.py search --category web_app

# Установка
python marketplace_cli.py install abc123def456 --name my-project

# Публикация своего
python marketplace_cli.py publish ./my-template \
  --name "react-starter" \
  --category "web_app" \
  --language "javascript" \
  --author "Your Name" \
  --description "React starter template"
```

### 5. Health monitoring

```python
from pathlib import Path
from tools.ai_generator.project_evolution_tracker import ProjectEvolutionTracker

tracker = ProjectEvolutionTracker(Path('./my-project'))

# Initial snapshot
tracker.take_snapshot()
tracker.calculate_metrics()

# Health check
health = tracker.calculate_health_score()
print(f"Health: {health.overall_score}/100")

# Recommendations
for rec in health.recommendations:
    print(f"  → {rec}")
```

---

## 🐳 Production Deployment

### Docker (рекомендуется)

```bash
cd 08-Программная-реализация/web

# Конфигурация (создайте .env файл)
cat > .env <<EOF
SECRET_KEY=your-super-secret-key-change-this
API_KEYS=prod-key-1,prod-key-2,admin-key
FLASK_ENV=production
LOG_LEVEL=INFO
EOF

# Запуск
docker-compose up -d

# Проверка
curl http://localhost:8080/health
curl http://localhost:8080/api/ai/health
```

### Использование Production API

```bash
# Анализ (с API key)
curl -H "X-API-Key: prod-key-1" \
  -X POST http://localhost:8080/api/ai/analyze \
  -H "Content-Type: application/json" \
  -d '{"description": "Финтех платформа"}'

# Генерация
curl -H "X-API-Key: prod-key-1" \
  -X POST http://localhost:8080/api/ai/generate \
  -H "Content-Type: application/json" \
  -d '{
    "description": "E-commerce marketplace",
    "project_name": "my-marketplace",
    "generate_content": true
  }'

# Metrics
curl -H "X-API-Key: prod-key-1" \
  http://localhost:8080/api/ai/metrics
```

---

## 📚 Примеры

### Пример 1: Финтех стартап

```bash
python integrated_workflow.py \
  --description "AI-powered платформа для автоматического инвестиционного портфеля с risk analysis и robo-advisor" \
  --name "robo-invest" \
  --output ./projects \
  --github \
  --marketplace
```

**Результат:**
- ✅ Проект создан локально
- ✅ GitHub repo с initial commit
- ✅ Опубликован в marketplace
- ✅ Health score: 75/100

### Пример 2: ML Research Project

```bash
# 1. Генерация
python integrated_workflow.py \
  --description "ML research project for computer vision with experiment tracking" \
  --name "cv-research"

# 2. Health monitoring
cd projects/cv-research
python -c "
from pathlib import Path
from tools.ai_generator.project_evolution_tracker import ProjectEvolutionTracker

tracker = ProjectEvolutionTracker(Path('.'))
tracker.take_snapshot()
health = tracker.calculate_health_score()

print(f'Health: {health.overall_score}/100')
"
```

### Пример 3: E-commerce Platform

```bash
# Использование template из marketplace
cd tools/ai_generator

# Поиск e-commerce templates
python marketplace_cli.py search --category ecommerce

# Установка популярного template
python marketplace_cli.py popular --limit 5
```

---

## ✅ Checklist для первого запуска

- [ ] Python 3.9+ установлен
- [ ] Зависимости установлены
- [ ] ML модель обучена
- [ ] Запустили demo
- [ ] Создали свой первый проект

---

## 🎉 Готово!

Система готова к использованию:

- **Быстрый старт:** `python integrated_workflow.py --demo`
- **Web UI:** `python ai_api.py` → http://localhost:5001
- **Production:** `docker-compose up -d`

**Happy coding!** 🚀
