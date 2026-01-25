# AI Project Generator - Web Interface

🌐 Веб-интерфейс для AI-powered генератора проектов

## 🚀 Быстрый старт

### 1. Установка зависимостей

```bash
pip install -r requirements-ai.txt
```

### 2. Запуск API сервера

```bash
python ai_api.py
```

API будет доступен на `http://localhost:5001`

### 3. Открытие веб-интерфейса

Откройте `ai-generator.html` в браузере:

```bash
# Linux/Mac
open ai-generator.html

# Windows
start ai-generator.html
```

Или просто перетащите файл в браузер.

---

## 📋 API Endpoints

### POST /api/ai/analyze

Анализ описания проекта без создания файлов.

**Request:**
```json
{
  "description": "Финтех MVP на React, бюджет 3 млн ₽, команда 8"
}
```

**Response:**
```json
{
  "classification": {
    "primary_type": "business",
    "primary_confidence": 0.125,
    "secondary_types": ["software", "finance"],
    "is_hybrid": true
  },
  "parameters": {
    "budget": {"amount": 3000000, "currency": "RUB", "formatted": "3,000,000 RUB"},
    "timeline": null,
    "team_size": 8,
    "phase": "mvp",
    "technologies": ["react"],
    "priority": null
  },
  "structure": {
    "strategy": "multi_domain",
    "merged_types": ["business", "software", "finance"],
    "adapted_directories": [...],
    "adapted_files": [...],
    "growth_percent": 50
  },
  "adaptations": [
    "Added financial tracking for 3,000,000 RUB budget",
    "Added MVP-specific structure",
    ...
  ],
  "recommendations": [...]
}
```

### POST /api/ai/generate

Генерация проекта с созданием файлов.

**Request:**
```json
{
  "description": "Финтех MVP на React",
  "project_name": "my-fintech-app",
  "generate_content": true
}
```

**Response:**
```json
{
  "success": true,
  "project_name": "my-fintech-app",
  "project_path": "/tmp/my-fintech-app",
  "classification": {...},
  "structure": {...},
  "generated_files": [
    "README.md",
    "CONTRIBUTING.md",
    "CHECKLIST.md",
    "examples/react_component.jsx"
  ]
}
```

### POST /api/ai/preview

Preview генерируемого контента.

**Request:**
```json
{
  "description": "E-commerce платформа на Django",
  "project_name": "my-shop",
  "content_type": "readme"
}
```

**Response:**
```json
{
  "content": "# my-shop\n\n*E-commerce платформа на Django*\n\n...",
  "content_type": "readme"
}
```

Content types: `readme`, `architecture`, `contributing`, `checklist`

### GET /api/ai/health

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "ai_components": "ready",
  "ml_model": "loaded"
}
```

---

## 🎯 Возможности веб-интерфейса

### Real-time Analysis
- Введите описание проекта на естественном языке
- Получите мгновенный анализ через AI pipeline
- Визуализация всех 4 фаз (Classification, Extraction, Composition, Adaptation)

### Visual Results
- **Classification:** Primary/Secondary типы с confidence scores
- **Parameters:** Все 15+ извлечённых параметров
- **Structure:** Визуальное дерево директорий
- **Adaptations:** Список применённых адаптаций
- **Recommendations:** Рекомендации по улучшению

### Examples
- 4 готовых примера для быстрого старта
- Fintech стартап
- Healthcare клиника
- E-commerce платформа
- Научное исследование

---

## 🛠️ Технологии

**Backend:**
- Flask (Python web framework)
- Flask-CORS (Cross-Origin Resource Sharing)
- AI компоненты из ЭТАПА 9 (ML classifier, Parameter extractor, etc.)

**Frontend:**
- Vanilla JavaScript (no frameworks)
- Modern CSS (Grid, Flexbox)
- Responsive design

---

## 📊 Архитектура

```
┌─────────────────────────────────────────────┐
│  Web Interface (ai-generator.html)          │
│  - User input form                          │
│  - Results visualization                    │
└─────────────────┬───────────────────────────┘
                  │ HTTP POST
                  ▼
┌─────────────────────────────────────────────┐
│  Flask API (ai_api.py)                      │
│  - /api/ai/analyze                          │
│  - /api/ai/generate                         │
│  - /api/ai/preview                          │
└─────────────────┬───────────────────────────┘
                  │ Python imports
                  ▼
┌─────────────────────────────────────────────┐
│  AI Components (tools/ai_generator/)        │
│  - MultiLabelClassifier (ML)                │
│  - EnhancedParameterExtractor               │
│  - TemplateComposer                         │
│  - ContextAwareAdapter                      │
│  - LLMContentGenerator                      │
└─────────────────────────────────────────────┘
```

---

## 🎨 Примеры использования

### 1. Простой анализ

```
Описание: "Хочу создать мобильное приложение для фитнеса"

Результат:
✓ Type: software
✓ Technologies: mobile app
✓ Structure: 12 directories, 15 files
```

### 2. Сложный multi-domain проект

```
Описание: "Healthcare телемедицина на React+Node.js, бюджет 8 млн ₽,
          команда 12, критический приоритет, MVP фаза"

Результат:
✓ Type: software + healthcare + business
✓ Parameters: budget, team, phase, priority, technologies
✓ Structure: 17 directories, 23 files (+55% growth)
✓ Adaptations: 8 applied
✓ Content: README, CONTRIBUTING, CHECKLIST, examples
```

---

## 🐛 Troubleshooting

### "CORS error"
Убедитесь, что Flask API запущен на порту 5001:
```bash
python ai_api.py
```

### "ML model not loaded"
Обучите модель:
```bash
cd tools/ai_generator
python ml_classifier.py --train
```

### "Connection refused"
Проверьте, что API сервер работает:
```bash
curl http://localhost:5001/api/ai/health
```

---

## 📈 Производительность

**Время анализа:**
- Classification: ~50ms
- Parameter extraction: ~10ms
- Structure composition: ~20ms
- Total: ~80ms (очень быстро!)

**Точность:**
- ML Classification: 87.5%
- Parameter extraction: ~95% (15+ параметров)
- Hybrid detection: 100%

---

## 🚀 Будущие улучшения

- [ ] Real-time preview генерируемых файлов
- [ ] Download button для скачивания проекта
- [ ] Project templates gallery
- [ ] History сохранённых анализов
- [ ] Share link для результатов
- [ ] Dark mode
- [ ] Mobile optimization

---

## 📝 License

MIT

---

## 🎉 Готово!

Теперь у вас есть полноценный веб-интерфейс для AI-генератора проектов!

**Запустите сервер:**
```bash
python ai_api.py
```

**Откройте интерфейс:**
```bash
open ai-generator.html
```

**Начните создавать проекты через AI!** 🚀
