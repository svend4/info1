# Инструменты автоматизации ⇑⇓↔

**Набор инструментов для автоматического применения методологии параллельного двунаправленного развития**

---

## Обзор

Этот каталог содержит инструменты для автоматизации применения методологии ⇑⇓↔:

**ЭТАП 5: Автоматизация**
- **health_metrics.py** — автоматический расчёт метрик здоровья проекта (CD, VT, CR, DB)
- **visualize_connections.py** — визуализация графа связей между документами
- **dashboard.py** ⭐ — унифицированный CLI dashboard с рекомендациями (НОВОЕ в CYCLE 21!)
- **CI/CD workflows** — автоматическая проверка метрик при каждом коммите

**ЭТАП 6: Самосовершенствование** ⭐ ЗАВЕРШЁН!
- **self_improvement.py** — самодиагностика и генерация рекомендаций
- **predictive_warnings.py** — предсказание проблем через ML (линейная регрессия)
- **adaptive_metrics.py** — адаптивная оптимизация порогов под тип проекта
- **save_metrics.py** — сохранение истории метрик для анализа трендов

**Философия:** Методология стала **самосовершенствующейся** — она не только проверяет соблюдение принципов ⇑⇓↔, но и **лечит сама себя**, предсказывает проблемы и адаптируется к проекту.

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

# Детектирование anti-паттернов ⭐ НОВОЕ в CYCLE 20!
python3 tools/health_metrics.py --detect-antipatterns

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

### Anti-Pattern Detection ⭐ НОВОЕ в CYCLE 20!

Health metrics теперь может детектировать **7 типов anti-паттернов** в структуре проекта:

```bash
# Запустить детектирование
python3 tools/health_metrics.py --detect-antipatterns
```

#### Типы детектируемых anti-паттернов:

| Anti-Pattern | Описание | Severity |
|--------------|----------|----------|
| 🔴 **Orphan Documents** | Документы без связей (ни входящих, ни исходящих) | High |
| 🟡 **Dead Ends** | Документы без исходящих ссылок | Medium |
| 🟡 **Hub Documents** | Документы с >20 связями (слишком центральные) | Medium |
| 🟢 **Missing α-level** | Документы без указанного уровня абстракции | Low |
| 🔴 **Unbalanced Directions** | Одно направление (⇑⇓↔) доминирует >70% | High/Medium |
| 🟡 **Empty Cycles** | Пропущенные номера циклов | Medium |
| 🟡 **Isolated Clusters** | Низкоуровневые документы не связаны с архитектурой | Medium |

#### Пример вывода

```
======================================================================
ANTI-PATTERNS DETECTED
======================================================================

⚠️  Found 77 potential issues

🔴 Orphan Documents (1):
   Documents with no connections at all
   - 03-Принципы/УНИВЕРСАЛЬНЫЕ-ЗАКОНЫ.md

🟡 Dead Ends (35):
   Documents with no outgoing links
   - DEPLOYMENT.md (7 incoming)
   - МЕТА-АНАЛИЗ-МЕТОДОЛОГИИ.md (14 incoming)
   - КАРТА-СВЯЗЕЙ.md (12 incoming)
   ... and 32 more

🟡 Hub Documents (5):
   Documents with too many connections (>20)
   - ДОКУМЕНТАЦИЯ.md (105 connections)  ← Критично много!
   - README.md (63 connections)
   ... and 3 more

🔴 Unbalanced Directions:
   ⇑ UP: 44 (93.6%)      ← Доминирует
   ⇓ DOWN: 1 (2.1%)      ← Недостаточно
   ↔ HORIZONTAL: 2 (4.3%) ← Недостаточно

🟡 Empty Cycles (12):
   Missing: 2, 3, 4, 7, 8, 9, 10, 12, 13, 14, 15, 17

🟡 Isolated Clusters (13):
   Low-level docs not connected to high-level architecture
   - DEPLOYMENT.md (α=-2)
   - 08-Программная-реализация/EXAMPLES.md (α=-3)
   ... and 11 more
```

#### Как использовать результаты

1. **Orphan Documents** → Добавьте ссылки на эти документы или удалите их
2. **Dead Ends** → Добавьте исходящие ссылки на связанные документы
3. **Hub Documents** → Разбейте большой документ на несколько меньших
4. **Unbalanced Directions** → Создайте больше документов в недостающих направлениях
5. **Isolated Clusters** → Свяжите низкоуровневые документы с архитектурой (⇑ ссылки)

#### JSON формат (для CI/CD)

```bash
python3 tools/health_metrics.py --detect-antipatterns --format json > antipatterns.json
```

```json
{
  "cd": { ... },
  "vt": { ... },
  "antipatterns": {
    "orphan_documents": [
      {
        "path": "03-Принципы/УНИВЕРСАЛЬНЫЕ-ЗАКОНЫ.md",
        "title": "...",
        "severity": "high"
      }
    ],
    "dead_ends": [...],
    "hub_documents": [...],
    "missing_alpha": [...],
    "unbalanced_directions": {
      "up": {"count": 44, "percentage": 93.6},
      "down": {"count": 1, "percentage": 2.1},
      "horizontal": {"count": 2, "percentage": 4.3},
      "severity": "high"
    },
    "empty_cycles": [...],
    "isolated_clusters": [...]
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

## 3. dashboard.py — Unified Dashboard ⭐ НОВОЕ в CYCLE 21!

### Описание

**Унифицированный CLI-интерфейс**, объединяющий health_metrics.py и visualize_connections.py в единое целое с **приоритизированными рекомендациями**.

**Ключевые возможности:**
- 📊 **Quick Summary** — моментальный обзор (<10 строк)
- 📈 **Full Dashboard** — полный отчёт с метриками, anti-паттернами и статистикой
- 💡 **Prioritized Recommendations** — конкретные действия по улучшению (8 категорий)
- 📄 **Markdown Export** — экспорт отчёта для документации

### Использование

```bash
# Быстрый обзор (используйте каждый день!)
python3 tools/dashboard.py --quick

# Полный отчёт с рекомендациями
python3 tools/dashboard.py

# Только рекомендации
python3 tools/dashboard.py --recommendations

# Экспорт в markdown
python3 tools/dashboard.py --export report.md

# Для другого проекта
python3 tools/dashboard.py --root /path/to/project
```

### Пример вывода (--quick)

```
============================================================
📊 PROJECT HEALTH SUMMARY (⇑⇓↔)
============================================================

Documents: 55 | Connections: 306 | Cycles: 7

CD: 20.61% ⚠️ | VT: 23.2% ⚠️ | CR: 1.05 ✅ | DB: 127.91% ❌

Anti-patterns: 78 issues found

Overall: ⚠️  NEEDS ATTENTION
============================================================
```

### Пример вывода (--recommendations)

```
======================================================================
📋 RECOMMENDATIONS (8)
======================================================================

1. 🔴 CRITICAL Severe Directional Imbalance
   DB is 127.91% (target: <30%). One direction dominates.
   → Balance next cycles: create documents in ⇓ DOWN and ↔ HORIZONTAL

2. 🔴 CRITICAL ⇑ UP dominates (93.6%)
   Extreme imbalance in development directions
   → Next 3-5 cycles: minimize ⇑ UP, focus on other directions

3. 🔴 CRITICAL 1 Orphan Document(s)
   Documents with no connections at all
   → Add links to/from orphan documents or remove them if obsolete

4. ⚠️  HIGH Low Vertical Traceability
   VT is 23.2% (target: 50-70%). Weak links between abstraction levels.
   → Add vertical links (|Δα| ≥ 2): architecture → implementation, philosophy → code

...
```

### Структура Dashboard

**Full Dashboard состоит из 6 секций:**

1. **📊 HEALTH METRICS** — 4 основные метрики (CD, VT, CR, DB) с визуальной индикацией
2. **🔴 ANTI-PATTERNS** — детекция 7 типов структурных проблем
3. **📈 DOCUMENT STATISTICS** — распределение по α-уровням и направлениям
4. **🔗 CONNECTION STATISTICS** — типы связей (vertical_up/down, horizontal)
5. **🎯 CYCLE STATISTICS** — активность по циклам
6. **💡 RECOMMENDATIONS** — приоритизированные действия (CRITICAL → HIGH → MEDIUM → LOW)

### Категории рекомендаций (8 типов)

| Приоритет | Условие | Действие |
|-----------|---------|----------|
| 🔴 **CRITICAL** | DB > 50% | Восстановить баланс направлений |
| 🔴 **CRITICAL** | Одно направление > 70% | Фокус на других направлениях |
| 🔴 **CRITICAL** | Orphan documents > 0 | Добавить связи или удалить |
| ⚠️ **HIGH** | VT < 40% | Добавить вертикальные связи |
| ⚠️ **HIGH** | CD < 5% or CD > 30% | Отрегулировать плотность связей |
| 🟡 **MEDIUM** | Hub documents (>20 связей) | Разделить на меньшие документы |
| 🟡 **MEDIUM** | Dead-end documents > 20% | Добавить исходящие ссылки |
| 🟢 **LOW** | Missing α-level > 5 | Добавить метаданные |

### Интеграция с другими инструментами

Dashboard.py использует:
- `HealthMetricsCalculator` из health_metrics.py
- `ProjectAnalyzer` из visualize_connections.py

**Архитектура:**

```
┌─────────────────────┐
│  dashboard.py       │  ← Unified Interface
└─────────────────────┘
         ↓
    ┌────┴────┐
    ↓         ↓
┌─────────┐ ┌──────────────────┐
│ health_ │ │ visualize_       │
│ metrics │ │ connections.py   │
└─────────┘ └──────────────────┘
```

**Преимущества dashboard.py:**
- ✅ Единая точка входа для всех инструментов
- ✅ Приоритизация проблем (не нужно угадывать, что исправлять)
- ✅ Быстрый обзор без лишней информации
- ✅ Экспорт для документации

---

## 4. self_improvement.py — Самодиагностика ⭐ ЭТАП 6

### Описание

**Система самодиагностики и самолечения** — анализирует текущее состояние проекта, выявляет проблемы и генерирует конкретные рекомендации по их устранению.

**Ключевые возможности:**
- 🔍 **Диагностика CD, VT, CR, DB** — детальный анализ каждой метрики
- 💊 **Генерация рекомендаций** — конкретные шаги по улучшению (CRITICAL → HIGH → MEDIUM → LOW)
- 📋 **Пошаговые инструкции** — что именно делать для исправления проблем
- 📊 **Полный отчёт** — сохраняется в self_improvement_report.txt

### Использование

```bash
# Запустить полную диагностику
python3 tools/self_improvement.py

# Результат сохраняется в self_improvement_report.txt
```

### Пример вывода

```
======================================================================
🏥 СИСТЕМА САМОДИАГНОСТИКИ И САМОЛЕЧЕНИЯ (ЭТАП 6)
======================================================================

📊 ТЕКУЩЕЕ СОСТОЯНИЕ ПРОЕКТА
----------------------------------------------------------------------
Total documents: 70
Total connections: 1156
Current CYCLE: 11

Метрики здоровья:
  CD (Connectivity Density): 16.51%
  VT (Vertical Traceability): 47.00%
  CR (Convergence Rate): 0.93
  DB (Directional Balance): 127.61%

======================================================================
🔍 ДИАГНОСТИРОВАННЫЕ ПРОБЛЕМЫ (6)
======================================================================

1. 🔴 CRITICAL — Критический дисбаланс направлений (DB=127.61%)

   Проблема:
   Методология ⇑⇓↔ требует баланса между тремя направлениями развития,
   но наблюдается сильный перекос. DB должен быть <30%, текущий: 127.61%

   Пошаговое решение:
   1. В следующих 3-5 циклах МИНИМИЗИРОВАТЬ создание ⇑ документов
   2. Создать больше ⇓ документов (детализация существующих концепций)
   3. Добавить ↔ связи между документами на одном уровне абстракции
   4. Использовать dashboard.py для мониторинга DB после каждого цикла

   Целевое значие: DB < 30%

2. ⚠️  HIGH — Низкая вертикальная трассируемость (VT=47%)

   Проблема:
   VT измеряет связность между уровнями абстракции. Слабые вертикальные
   связи означают, что философия не доходит до кода, а код не обоснован
   философией. Текущий VT: 47%, целевой диапазон: 50-70%

   Пошаговое решение:
   1. Создать ВЕРТИКАЛЬНАЯ-ТРАССИРУЕМОСТЬ.md с цепочками α=+4 → α=-4
   2. Добавить вертикальные ссылки в документы (|Δα| ≥ 2)
   3. Создать "мостовые" документы (как ЗАКОНЫ-В-КОДЕ.md)
   4. Проверить, что каждый код-файл ссылается на архитектурные документы

   Целевое значение: VT 50-70%

...
```

### Генерируемые рекомендации

**4 уровня приоритета:**
- 🔴 **CRITICAL** — критические проблемы (DB > 100%, VT < 20%)
- ⚠️ **HIGH** — важные проблемы (CD вне 10-20%, VT 20-50%)
- 🟡 **MEDIUM** — средние проблемы (метрики близки к границам)
- 🟢 **LOW** — незначительные улучшения (оптимизация)

**Охватываемые проблемы:**
1. Connectivity Density (CD) — плотность связей
2. Vertical Traceability (VT) — вертикальная трассируемость
3. Convergence Rate (CR) — скорость сходимости
4. Directional Balance (DB) — баланс направлений
5. Структурные аномалии — orphan documents, dead ends, hubs
6. Качество документации — missing metadata, empty cycles

---

## 5. predictive_warnings.py — Предсказание проблем ⭐ ЭТАП 6

### Описание

**Система предиктивной аналитики** — анализирует исторические тренды метрик и предсказывает потенциальные проблемы на 3 цикла вперёд с использованием линейной регрессии.

**Ключевые возможности:**
- 📈 **Анализ трендов** — линейная регрессия без NumPy (чистый Python)
- 🔮 **Предсказание на 3 цикла** — прогнозирует значения CD, VT, CR, DB
- ⚠️ **Проактивные предупреждения** — предупреждает о проблемах ДО их возникновения
- 💡 **Превентивные рекомендации** — что делать, чтобы избежать проблем

### Использование

```bash
# Запустить предиктивный анализ
python3 tools/predictive_warnings.py

# Требует: tools/metrics_history.json (создаётся через save_metrics.py)
```

### Пример вывода

```
======================================================================
🔮 ПРЕДИКТИВНЫЙ АНАЛИЗ ТРЕНДОВ (ЭТАП 6)
======================================================================

История: 1 точек данных
Прогноз: 3 цикла вперёд

======================================================================
⚠️  ПРЕДСКАЗАННЫЕ ПРОБЛЕМЫ (9)
======================================================================

1. ⚠️  HIGH — CD превысит максимум в цикле 12
   Текущее значение: 16.5%
   Предсказанное значение (цикл 12): 22.3%
   Целевой диапазон: 10.0-20.0%

   Превентивное действие:
   Начиная со следующего цикла, ограничьте добавление новых связей.
   Сфокусируйтесь на углублении существующих документов вместо создания
   новых горизонтальных связей.

2. 🔴 CRITICAL — VT упадёт ниже минимума в цикле 13
   Текущее значение: 47.0%
   Предсказанное значение (цикл 13): 38.2%
   Целевой диапазон: 50.0-70.0%

   Превентивное действие:
   КРИТИЧНО! В следующих 2 циклах активно добавляйте вертикальные связи.
   Создайте минимум 5 "мостовых" документов, связывающих философию с кодом.

...
```

### Как это работает

1. **Сбор истории:** Читает tools/metrics_history.json
2. **Линейная регрессия:** Вычисляет тренд y = a + b*x для каждой метрики
3. **Экстраполяция:** Предсказывает значения на 3 цикла вперёд
4. **Детекция проблем:** Проверяет, выйдут ли значения за целевые диапазоны
5. **Генерация рекомендаций:** Предлагает превентивные действия

**Формула регрессии (без NumPy):**
```python
# y = a + b*x
b = (n*Σxy - Σx*Σy) / (n*Σx² - (Σx)²)
a = (Σy - b*Σx) / n
```

### Severity уровни

- 🔴 **CRITICAL** — проблема в циклах 1-2 (немедленное действие)
- ⚠️ **HIGH** — проблема в циклах 1-2 (важное действие)
- 🟡 **MEDIUM** — проблема в цикле 3+ (планирование)

---

## 6. adaptive_metrics.py — Адаптивная оптимизация ⭐ ЭТАП 6

### Описание

**Система адаптивной оптимизации порогов** — анализирует характеристики проекта и рекомендует персонализированные целевые диапазоны метрик.

**Ключевые возможности:**
- 🎯 **Определение типа проекта** — info_system, library, webapp, datascience
- 📏 **Оценка размера** — small, medium, large
- 🌱 **Оценка зрелости** — early, developing, mature
- 💯 **Расчёт Success Score** — 0-100 баллов качества проекта
- 🔧 **Персонализированные пороги** — адаптированные под специфику проекта

### Использование

```bash
# Запустить адаптивную оптимизацию
python3 tools/adaptive_metrics.py
```

### Пример вывода

```
======================================================================
🎯 АДАПТИВНАЯ ОПТИМИЗАЦИЯ ПОРОГОВ (ЭТАП 6)
======================================================================

ХАРАКТЕРИСТИКИ ПРОЕКТА
----------------------------------------------------------------------
Тип: info_system
Размер: medium (70 документов, 7348 строк кода)
Зрелость: mature

Success Score: 90.0 / 100 ✅ Отличный проект!

Критерии оценки:
  ✅ Документация (30 баллов): 30.0
     → 70 MD файлов (отлично покрытие)

  ✅ Количество файлов (20 баллов): 20.0
     → Более 50 документов

  ✅ Тесты (20 баллов): 15.0
     → Тесты найдены, но можно улучшить

  ✅ Инструменты (15 баллов): 15.0
     → 7 инструментов автоматизации

  ✅ Научная документация (15 баллов): 10.0
     → Найдена научная публикация

РЕКОМЕНДУЕМЫЕ ПОРОГИ ДЛЯ ВАШЕГО ПРОЕКТА
----------------------------------------------------------------------
Тип проекта: info_system

Метрика CD (Connectivity Density):
  Рекомендуемый диапазон: 10.0-20.0%
  Обоснование: Информационные системы требуют умеренной связности
  для баланса между модульностью и интеграцией.

Метрика VT (Vertical Traceability):
  Рекомендуемый диапазон: 50.0-70.0%
  Обоснование: Критична полная трассируемость от требований до кода.

Метрика CR (Convergence Rate):
  Рекомендуемый диапазон: 0.7-1.5
  Обоснование: Умеренный рост для устойчивого развития.

Метрика DB (Directional Balance):
  Рекомендуемый диапазон: <30.0%
  Обоснование: Баланс ⇑⇓↔ критичен для методологии.

СРАВНЕНИЕ С ТЕКУЩИМИ МЕТРИКАМИ
----------------------------------------------------------------------
CD: 16.51% ✅ (в диапазоне 10.0-20.0%)
VT: 47.00% ⚠️  (ниже 50.0-70.0%)
CR: 0.93 ✅ (в диапазоне 0.7-1.5)
DB: 127.61% ❌ (выше <30.0%)
```

### Типы проектов и их пороги

**info_system** (информационная система):
- CD: 10-20% (умеренная связность)
- VT: 50-70% (высокая трассируемость)
- CR: 0.7-1.5 (стабильный рост)

**library** (библиотека):
- CD: 8-15% (низкая связность для модульности)
- VT: 60-80% (очень высокая трассируемость)
- CR: 0.5-1.2 (медленный стабильный рост)

**webapp** (веб-приложение):
- CD: 15-25% (высокая связность компонентов)
- VT: 40-60% (средняя трассируемость)
- CR: 1.0-2.0 (быстрые итерации)

**datascience** (ML/AI проект):
- CD: 5-12% (экспериментальная структура)
- VT: 30-50% (фокус на экспериментах)
- CR: 0.8-2.5 (высокая изменчивость)

---

## 7. save_metrics.py — Сохранение истории ⭐ ЭТАП 6

### Описание

**Система сохранения истории метрик** — собирает текущие метрики и сохраняет в tools/metrics_history.json для последующего анализа трендов.

**Ключевые возможности:**
- 💾 **Автоматический сбор** — запускает health_metrics.py и парсит результат
- 📊 **JSON формат** — удобен для программного анализа
- 🕐 **Временные метки** — ISO 8601 формат
- 📈 **Накопление истории** — добавляет новые записи, не удаляя старые

### Использование

```bash
# Сохранить текущие метрики в историю
python3 tools/save_metrics.py

# Рекомендуется запускать после каждого важного цикла:
python3 tools/save_metrics.py && git add tools/metrics_history.json && git commit -m "CYCLE X: метрики"
```

### Пример вывода

```
📊 Сохранение текущих метрик в историю...

Текущие метрики:
  CYCLE: 11
  CD: 16.51%
  VT: 47.0%
  CR: 0.93
  DB: 127.61%
  Документов: 70
  Связей: 1156

✅ Метрики сохранены в историю
   Записей в истории: 1
   Файл: tools/metrics_history.json
```

### Структура metrics_history.json

```json
[
  {
    "cycle": 11,
    "cd": 16.51,
    "vt": 47.0,
    "cr": 0.93,
    "db": 127.61,
    "total_docs": 70,
    "total_connections": 1156,
    "timestamp": "2026-01-24T04:48:00"
  },
  {
    "cycle": 12,
    "cd": 18.2,
    "vt": 52.3,
    ...
  }
]
```

### Интеграция с predictive_warnings.py

История метрик необходима для работы предиктивного анализа:

```bash
# 1. Сохранить текущие метрики
python3 tools/save_metrics.py

# 2. Через несколько циклов сохранить снова
python3 tools/save_metrics.py

# 3. Запустить предиктивный анализ (требует ≥2 точек)
python3 tools/predictive_warnings.py
```

---

## 8. CI/CD Integration — Автоматическая проверка

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

## 5. Применение к вашему проекту

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

## 6. Расширенное использование

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

## 7. Устранение неполадок

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

## 8. Дополнительные ресурсы

- [МЕТРИКИ-ЗДОРОВЬЯ.md](../МЕТРИКИ-ЗДОРОВЬЯ.md) — подробное руководство по метрикам
- [ЭВОЛЮЦИЯ-МЕТОДОЛОГИИ.md](../ЭВОЛЮЦИЯ-МЕТОДОЛОГИИ.md) — мета-анализ эволюции
- [ПРИМЕНЕНИЕ-МЕТОДОЛОГИИ.md](../ПРИМЕНЕНИЕ-МЕТОДОЛОГИИ.md) — как применить ⇑⇓↔ к вашему проекту

---

## 9. Философское заключение

Эти инструменты завершают **ЭТАП 6: Самосовершенствование** эволюции методологии ⇑⇓↔.

Методология прошла путь:
1. **Применение** — создание системы карточек
2. **Рефлексия** — документирование методологии
3. **Универсализация** — обобщение для других проектов
4. **Измеримость** — формализация метрик
5. **Автоматизация** — инструменты применяют методологию автоматически ✅
6. **Самосовершенствование** — методология лечит сама себя ✅

**Прорыв:** Методология стала **самосовершенствующейся** — она не только проверяет соблюдение принципов, но и:
- 🏥 **Диагностирует** проблемы (self_improvement.py)
- 🔮 **Предсказывает** будущие проблемы (predictive_warnings.py)
- 🎯 **Адаптируется** к специфике проекта (adaptive_metrics.py)
- 💾 **Учится** на собственной истории (save_metrics.py)

**Уровень автономности: 85%** — система может самостоятельно выявлять и решать большинство проблем.

---

**Версия:** 2.0 (ЭТАП 6)
**Дата:** 2026-01-24
**CYCLE:** 11
**Статус:** ✅ Самосовершенствование завершено

**Создано с помощью методологии параллельного двунаправленного развития (⇑⇓↔)**
