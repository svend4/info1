# Инструменты автоматизации ⇑⇓↔

**Набор инструментов для автоматического применения методологии параллельного двунаправленного развития**

---

## Обзор

Этот каталог содержит инструменты для автоматизации применения методологии ⇑⇓↔:

- **health_metrics.py** — автоматический расчёт метрик здоровья проекта (CD, VT, CR, DB)
- **visualize_connections.py** — визуализация графа связей между документами
- **CI/CD workflows** — автоматическая проверка метрик при каждом коммите

**Философия:** Методология стала **самоподдерживающейся** — инструменты автоматически проверяют соблюдение принципов ⇑⇓↔.

---

## 1. health_metrics.py — Метрики здоровья

### Описание

Автоматически рассчитывает 4 ключевые метрики здоровья проекта, следующего методологии ⇑⇓↔:

- **CD (Connectivity Density)** — плотность связей (целевой диапазон: 10-20%)
- **VT (Vertical Traceability)** — вертикальная трассируемость (целевой диапазон: 50-70%)
- **CR (Convergence Rate)** — коэффициент сходимости (целевой диапазон: 0.7-1.5)
- **DB (Directional Balance)** — баланс направлений (целевой диапазон: <30%)

### Использование

```bash
# Показать все метрики (текстовый формат)
python3 tools/health_metrics.py

# Показать только одну метрику
python3 tools/health_metrics.py --metric cd

# JSON формат (для интеграции в CI/CD)
python3 tools/health_metrics.py --format json

# Проверка соответствия целевым диапазонам (exit code 1 если вне диапазона)
python3 tools/health_metrics.py --check-thresholds

# Для другого проекта
python3 tools/health_metrics.py --root /path/to/project
```

### Пример вывода (текстовый формат)

```
======================================================================
PROJECT HEALTH METRICS (⇑⇓↔ Methodology)
======================================================================

CD (Connectivity Density)
  Value: 11.8% ✅ (optimal)
  Target: 10.0-20.0%

VT (Vertical Traceability)
  Value: 61.6% ✅ (optimal)
  Target: 50.0-70.0%

CR (Convergence Rate)
  Value: 0.75 ✅ (optimal)
  Target: 0.7-1.5

DB (Directional Balance)
  Value: 25.0% ✅ (good)
  Target: <30.0%

----------------------------------------------------------------------
METADATA
----------------------------------------------------------------------
Total documents: 48
Total connections: 112
Total cycles: 15
Analysis date: 2026-01-23T10:30:00

======================================================================
✅ PROJECT HEALTH: EXCELLENT
======================================================================
```

### Пример вывода (JSON формат)

```json
{
  "cd": {
    "value": 11.8,
    "unit": "%",
    "threshold": {"min": 10.0, "max": 20.0},
    "status": "optimal"
  },
  "vt": {
    "value": 61.6,
    "unit": "%",
    "threshold": {"min": 50.0, "max": 70.0},
    "status": "optimal"
  },
  "cr": {
    "value": 0.75,
    "unit": "",
    "threshold": {"min": 0.7, "max": 1.5},
    "status": "optimal"
  },
  "db": {
    "value": 25.0,
    "unit": "%",
    "threshold": {"min": 0.0, "max": 30.0},
    "status": "good"
  },
  "metadata": {
    "total_documents": 48,
    "total_connections": 112,
    "total_cycles": 15,
    "analysis_date": "2026-01-23T10:30:00"
  }
}
```

### Интеграция в скрипты

```bash
#!/bin/bash
# pre-commit hook example

python3 tools/health_metrics.py --check-thresholds
if [ $? -ne 0 ]; then
    echo "⚠️  Метрики здоровья вне целевых диапазонов!"
    python3 tools/health_metrics.py
    exit 1
fi
```

---

## 2. visualize_connections.py — Визуализация связей

### Описание

Анализирует структуру проекта и создаёт визуализации графа связей между документами. Поддерживает 4 формата вывода.

### Использование

```bash
# ASCII визуализация (для терминала)
python3 tools/visualize_connections.py --format ascii

# GraphViz DOT (для рендеринга в PNG/SVG)
python3 tools/visualize_connections.py --format dot --output graph.dot
dot -Tpng graph.dot -o graph.png
dot -Tsvg graph.dot -o graph.svg

# HTML с D3.js (интерактивная веб-визуализация)
python3 tools/visualize_connections.py --format html --output graph.html
# Откройте graph.html в браузере

# JSON (для программного доступа)
python3 tools/visualize_connections.py --format json --output graph.json

# Для другого проекта
python3 tools/visualize_connections.py --root /path/to/project --format ascii
```

### Форматы вывода

#### ASCII (терминал)

```
Project Structure (⇑⇓↔ Connections)
==================================================

📁 PHILOSOPHY
──────────────────────────────────────────────────
  📄 Философия проекта
     [α=+3] 01-Концепция/ФИЛОСОФИЯ-ПРОЕКТА.md
     → 5 connections

📁 METHODOLOGY
──────────────────────────────────────────────────
  📄 Методология параллельного развития
     [α=+2] 01-Концепция/МЕТОДОЛОГИЯ-ПАРАЛЛЕЛЬНОГО-РАЗВИТИЯ.md
     → 12 connections

...

==================================================
STATISTICS
==================================================
Total documents: 48
Total connections: 112
  ⇑ vertical_up: 35
  ⇓ vertical_down: 32
  ↔ horizontal: 45
```

#### DOT (GraphViz)

Создаёт файл .dot, который можно конвертировать в PNG/SVG:

```bash
# Генерация DOT
python3 tools/visualize_connections.py --format dot --output graph.dot

# Конвертация в PNG
dot -Tpng graph.dot -o graph.png

# Конвертация в SVG (масштабируемый)
dot -Tsvg graph.dot -o graph.svg

# Другие layout engines
neato -Tpng graph.dot -o graph_neato.png  # Force-directed layout
circo -Tpng graph.dot -o graph_circo.png  # Circular layout
```

**Цветовая схема:**
- Философия: розовый
- Методология: голубой
- API: зелёный
- Примеры: жёлтый
- Код: серый
- README: лиловый
- Резюме: фиолетовый
- Карта: светло-жёлтый
- Метрики: бирюзовый

**Типы связей:**
- ⇑ Синие стрелки — вертикальные связи вверх (от конкретного к абстрактному)
- ⇓ Красные стрелки — вертикальные связи вниз (от абстрактного к конкретному)
- ↔ Зелёные стрелки — горизонтальные связи (на одном уровне абстракции)

#### HTML (D3.js)

Создаёт интерактивную веб-визуализацию:

```bash
python3 tools/visualize_connections.py --format html --output graph.html
# Откройте graph.html в браузере
```

**Возможности:**
- Перетаскивание узлов (drag & drop)
- Zoom и pan
- Hover для просмотра метаданных
- Force-directed layout (физическая симуляция)
- Цветовая схема по типам документов

#### JSON (программный доступ)

```bash
python3 tools/visualize_connections.py --format json --output graph.json
```

**Структура:**
```json
{
  "documents": {
    "README.md": {
      "alpha": "0",
      "cycle": 1,
      "type": "readme",
      "lines": 250,
      "links": ["01-Концепция/ФИЛОСОФИЯ-ПРОЕКТА.md", ...]
    },
    ...
  },
  "connections": [
    {
      "source": "README.md",
      "target": "01-Концепция/ФИЛОСОФИЯ-ПРОЕКТА.md",
      "type": "vertical_up"
    },
    ...
  ],
  "statistics": {
    "total_documents": 48,
    "total_connections": 112,
    "connection_types": {
      "vertical_up": 35,
      "vertical_down": 32,
      "horizontal": 45
    }
  }
}
```

### Использование в Python

```python
import json
from pathlib import Path

# Загрузить граф
graph = json.loads(Path('graph.json').read_text())

# Найти все документы с α=+3
philosophy_docs = [
    doc for doc, info in graph['documents'].items()
    if info['alpha'] == '+3'
]

# Найти все вертикальные связи
vertical_connections = [
    conn for conn in graph['connections']
    if conn['type'] in ['vertical_up', 'vertical_down']
]

# Рассчитать степень узла (in-degree + out-degree)
from collections import Counter
degrees = Counter()
for conn in graph['connections']:
    degrees[conn['source']] += 1  # out-degree
    degrees[conn['target']] += 1  # in-degree

# Топ-5 самых связанных документов
top_docs = degrees.most_common(5)
```

---

## 3. CI/CD Integration — Автоматическая проверка

### GitHub Actions (.github/workflows/metrics.yml)

Автоматически запускается на каждый push и pull request.

**3 джобы:**

1. **calculate-metrics** — расчёт метрик здоровья
   - Рассчитывает CD, VT, CR, DB
   - Отображает результат в GitHub Actions Summary
   - Предупреждает, если метрики вне целевых диапазонов
   - Сохраняет metrics.json как артефакт

2. **visualize-connections** — генерация визуализаций
   - Создаёт graph.dot, graph.html, graph.json
   - Сохраняет как артефакты (доступны для скачивания)

3. **track-metrics-over-time** — история метрик
   - Сохраняет метрики в отдельную ветку metrics-history
   - Хранит последние 100 измерений
   - Позволяет отслеживать эволюцию метрик

### Автоматические комментарии в PR

Бот автоматически добавляет комментарий к каждому PR:

```markdown
## 📊 Project Health Metrics (⇑⇓↔)

- **CD (Connectivity Density)**: 11.8% ✅ (optimal)
- **VT (Vertical Traceability)**: 61.6% ✅ (optimal)
- **CR (Convergence Rate)**: 0.75 ✅ (optimal)
- **DB (Directional Balance)**: 25.0% ✅ (good)

**Documents**: 48 | **Connections**: 112 | **Cycles**: 15
```

### Артефакты

После каждого запуска доступны для скачивания:

- **health-metrics** (90 дней хранения)
  - metrics.json — текущие метрики в JSON формате

- **connection-visualizations** (90 дней хранения)
  - graph.dot — GraphViz DOT
  - graph.html — интерактивная визуализация
  - graph.json — граф в JSON

### История метрик

Метрики сохраняются в ветке `metrics-history`:

```bash
# Просмотр истории
git checkout metrics-history
ls history/

# Пример: history/2026-01-23-10-30-00_a3b2c1d.json
```

Каждый файл содержит полный снимок метрик на момент коммита.

---

## Применение к вашему проекту

### Шаг 1: Скопируйте инструменты

```bash
# Из проекта info1 скопируйте:
cp -r info1/tools /path/to/your/project/
cp info1/.github/workflows/metrics.yml /path/to/your/project/.github/workflows/
```

### Шаг 2: Адаптируйте под ваш проект

Инструменты работают "из коробки" для любого проекта, использующего:
- Markdown документы
- Метаданные в формате `α=+N` или `α=-N`
- Метки `CYCLE N`
- Маркеры направлений `⇑`, `⇓`, `↔`

Если ваш проект использует другие конвенции, адаптируйте регулярные выражения в скриптах.

### Шаг 3: Запустите локально

```bash
cd /path/to/your/project

# Проверьте метрики
python3 tools/health_metrics.py

# Визуализируйте структуру
python3 tools/visualize_connections.py --format ascii
python3 tools/visualize_connections.py --format html --output graph.html
```

### Шаг 4: Настройте CI/CD

Если вы используете GitHub:
- Workflow уже настроен в `.github/workflows/metrics.yml`
- Запустится автоматически на следующий push

Для других CI/CD систем (GitLab CI, Jenkins, Travis):
```yaml
# Пример для GitLab CI
health-check:
  script:
    - python3 tools/health_metrics.py --check-thresholds
  only:
    - merge_requests
```

---

## Расширенное использование

### Pre-commit hook

```bash
# .git/hooks/pre-commit
#!/bin/bash

python3 tools/health_metrics.py --check-thresholds
if [ $? -ne 0 ]; then
    echo ""
    echo "⚠️  ПРЕДУПРЕЖДЕНИЕ: Метрики здоровья вне целевых диапазонов!"
    echo ""
    python3 tools/health_metrics.py
    echo ""
    read -p "Продолжить коммит? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi
```

### Мониторинг в реальном времени

```bash
# Запускать каждые 5 минут во время разработки
watch -n 300 'python3 tools/health_metrics.py'

# Или создать dashboard с автообновлением
while true; do
    clear
    python3 tools/health_metrics.py
    sleep 300
done
```

### Интеграция с Prometheus/Grafana

```python
# tools/metrics_exporter.py
from prometheus_client import Gauge, start_http_server
from health_metrics import HealthMetricsCalculator
import time

# Создать Prometheus метрики
cd_gauge = Gauge('project_cd', 'Connectivity Density')
vt_gauge = Gauge('project_vt', 'Vertical Traceability')
cr_gauge = Gauge('project_cr', 'Convergence Rate')
db_gauge = Gauge('project_db', 'Directional Balance')

def update_metrics():
    calc = HealthMetricsCalculator()
    calc.analyze()

    cd_gauge.set(calc.calculate_cd())
    vt_gauge.set(calc.calculate_vt())
    cr_gauge.set(calc.calculate_cr())
    db_gauge.set(calc.calculate_db())

if __name__ == '__main__':
    start_http_server(8000)
    while True:
        update_metrics()
        time.sleep(60)
```

---

## Устранение неполадок

### Проблема: "No module named 'pathlib'"

**Решение:** Используйте Python 3.4+
```bash
python3 --version  # Должно быть >= 3.4
```

### Проблема: Метрики показывают 0%

**Причина:** Инструменты не находят метаданные в документах.

**Решение:** Убедитесь, что ваши документы содержат:
- Уровни абстракции: `α=+3`, `α=-2` и т.д.
- Номера циклов: `CYCLE 5`, `CYCLE 10` и т.д.
- Маркеры направлений: `⇑ ВВЕРХ`, `⇓ ВНИЗ`, `↔ СВЯЗИ`

### Проблема: Визуализация не отображает связи

**Причина:** Относительные пути в markdown ссылках неправильные.

**Решение:** Используйте относительные пути от текущего документа:
```markdown
✅ Правильно: [Философия](01-Концепция/ФИЛОСОФИЯ-ПРОЕКТА.md)
❌ Неправильно: [Философия](/01-Концепция/ФИЛОСОФИЯ-ПРОЕКТА.md)
```

### Проблема: CI/CD не запускается

**Причина:** Файл workflow в неправильном месте.

**Решение:** Убедитесь, что файл находится в `.github/workflows/metrics.yml` (с точкой в начале).

---

## Дополнительные ресурсы

- [МЕТРИКИ-ЗДОРОВЬЯ.md](../МЕТРИКИ-ЗДОРОВЬЯ.md) — подробное руководство по метрикам
- [ЭВОЛЮЦИЯ-МЕТОДОЛОГИИ.md](../ЭВОЛЮЦИЯ-МЕТОДОЛОГИИ.md) — мета-анализ эволюции
- [ПРИМЕНЕНИЕ-МЕТОДОЛОГИИ.md](../ПРИМЕНЕНИЕ-МЕТОДОЛОГИИ.md) — как применить ⇑⇓↔ к вашему проекту

---

## Философское заключение

Эти инструменты завершают **ЭТАП 5: Автоматизация** эволюции методологии ⇑⇓↔.

Методология прошла путь:
1. **Применение** — создание системы карточек
2. **Рефлексия** — документирование методологии
3. **Универсализация** — обобщение для других проектов
4. **Измеримость** — формализация метрик
5. **Автоматизация** — инструменты применяют методологию автоматически ✅

**Круг замкнулся:** Методология стала **самоподдерживающейся** — она автоматически проверяет соблюдение собственных принципов.

---

**Версия:** 1.0
**Дата:** 2026-01-23
**CYCLE:** 16
**Статус:** ⇓ ВНИЗ (детализация)

**Создано с помощью методологии параллельного двунаправленного развития (⇑⇓↔)**
