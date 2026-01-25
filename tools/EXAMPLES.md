# Примеры использования инструментов — Практические сценарии
*Уровень абстракции: α=-2 (примеры)*

**Направление:** ⇓ ВНИЗ (детализация)
**Цикл:** 22

---

## Обзор

Этот документ содержит **конкретные примеры использования** инструментов автоматизации методологии ⇑⇓↔.

**Покрытые инструменты:**
- `dashboard.py` — унифицированный dashboard
- `health_metrics.py` — расчёт метрик здоровья
- `visualize_connections.py` — визуализация графа связей

**Формат:** Каждый пример включает команду, вывод и объяснение.

---

## 🎯 Сценарий 1: Ежедневная проверка здоровья проекта

**Задача:** Быстро проверить состояние проекта перед началом работы.

### Шаг 1: Запустить quick summary

```bash
python3 tools/dashboard.py --quick
```

**Вывод:**
```
============================================================
📊 PROJECT HEALTH SUMMARY (⇑⇓↔)
============================================================

Documents: 56 | Connections: 310 | Cycles: 7

CD: 20.61% ⚠️ | VT: 23.2% ⚠️ | CR: 1.05 ✅ | DB: 127.91% ❌

Anti-patterns: 78 issues found

Overall: ⚠️  NEEDS ATTENTION
============================================================
```

**Интерпретация:**
- ✅ **CR (1.05)** — сходимость в норме, структура логична
- ⚠️ **CD (20.61%)** — чуть выше оптимального, но приемлемо
- ⚠️ **VT (23.2%)** — низкая вертикальная трассируемость, нужно больше связей между уровнями
- ❌ **DB (127.91%)** — критический дисбаланс направлений!

**Действие:** DB критично — сегодня работаем над ⇓ ВНИЗ и ↔ СВЯЗИ.

---

## 🔍 Сценарий 2: Что нужно исправить в первую очередь?

**Задача:** Получить приоритизированный список проблем.

### Команда:

```bash
python3 tools/dashboard.py --recommendations
```

**Вывод:**
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

5. 🟡 MEDIUM Hub Document: ДОКУМЕНТАЦИЯ.md
   105 connections (target: <20)
   → Split hub document into smaller, focused documents

6. 🟡 MEDIUM 35 Dead-End Documents
   Documents without outgoing links
   → Add "See also" sections with links to related documents

7. 🟡 MEDIUM 13 Isolated Document(s)
   Low-level docs not connected to high-level architecture
   → Add upward links (⇑) from implementation to architecture

8. 🟢 LOW 10 Documents Missing α-level
   Documents without abstraction level metadata
   → Add "α-уровень: X" to document headers
```

**План действий:**
1. ✅ **Сейчас:** Создать документы в ⇓ ВНИЗ и ↔ СВЯЗИ (рекомендация #1, #2)
2. ⏳ **Завтра:** Добавить ссылки к orphan document (рекомендация #3)
3. ⏳ **На неделю:** Улучшить вертикальные связи (рекомендация #4)
4. ⏳ **На месяц:** Разбить ДОКУМЕНТАЦИЯ.md на части (рекомендация #5)

---

## 📊 Сценарий 3: Детальный анализ метрик

**Задача:** Получить подробную информацию о каждой метрике.

### Команда:

```bash
python3 tools/health_metrics.py
```

**Вывод:**
```
======================================================================
PROJECT HEALTH METRICS (⇑⇓↔ Methodology)
======================================================================

CD (Connectivity Density)
  Value: 20.61% ⚠️ (moderate)
  Target: 10.0-20.0%

  Formula: (total_connections / (total_docs * (total_docs - 1))) * 100
  Calculation: (306 / (56 * 55)) * 100 = 20.61%

VT (Vertical Traceability)
  Value: 23.2% ⚠️ (poor)
  Target: 50.0-70.0%

  Formula: (vertical_connections / total_connections) * 100
  Calculation: (71 / 306) * 100 = 23.2%

CR (Convergence Rate)
  Value: 1.05 ✅ (optimal)
  Target: 0.7-1.5

  Formula: avg_alpha_per_cycle
  High-level docs per cycle: ~1.05

DB (Directional Balance)
  Value: 127.91% ❌ (poor)
  Target: <30.0%

  Formula: max(up%, down%, horiz%) - min(up%, down%, horiz%)
  Directions: ⇑93.6% / ⇓2.1% / ↔4.3%
  Balance: 93.6% - 2.1% = 91.5% deviation

----------------------------------------------------------------------
METADATA
----------------------------------------------------------------------
Total documents: 56
Total connections: 306
Total cycles: 7
Analysis date: 2026-01-23T12:30:00

======================================================================
⚠️  PROJECT HEALTH: NEEDS ATTENTION
======================================================================
```

**Интерпретация:**
- **CD:** Чуть высоковато (20.61% vs 10-20%), но не критично. Документы хорошо связаны.
- **VT:** Только 23.2% связей вертикальные. Нужно добавить связи между философией/архитектурой/кодом.
- **CR:** Идеально (1.05). В каждом цикле создаём ~1 high-level документ.
- **DB:** Катастрофа. 93.6% документов — это ⇑ ВВЕРХ (обобщение), почти нет ⇓ и ↔.

---

## 🔴 Сценарий 4: Детекция anti-паттернов

**Задача:** Найти структурные проблемы в проекте.

### Команда:

```bash
python3 tools/health_metrics.py --detect-antipatterns
```

**Вывод:**
```
======================================================================
ANTI-PATTERNS DETECTED
======================================================================

⚠️  Found 78 potential issues

🔴 Orphan Documents (1):
   Documents with no connections at all
   - 03-Принципы/УНИВЕРСАЛЬНЫЕ-ЗАКОНЫ.md

🟡 Dead Ends (35):
   Documents with no outgoing links
   - DEPLOYMENT.md (7 incoming)
   - МЕТА-АНАЛИЗ-МЕТОДОЛОГИИ.md (14 incoming)
   - КАРТА-СВЯЗЕЙ.md (12 incoming)
   ... and 32 more

🟡 Hub Documents (1):
   Documents with too many connections (>20)
   - ДОКУМЕНТАЦИЯ.md (105 connections)  ← Критично много!

🟢 Missing α-level (10):
   Documents without abstraction level
   - 03-Робототехника-и-автоматизация/README.md
   - 04-Бытовые-циклы-и-задания/README.md
   ... and 8 more

🔴 Unbalanced Directions:
   ⇑ UP: 52 (93.6%)      ← Доминирует
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

**Действия по каждой проблеме:**

1. **Orphan document:** Добавить ссылки на `УНИВЕРСАЛЬНЫЕ-ЗАКОНЫ.md` или удалить (если дубликат)
2. **Dead ends:** Добавить "См. также" секции с 2-3 ссылками
3. **Hub document:** Разбить ДОКУМЕНТАЦИЯ.md на части:
   - ДОКУМЕНТАЦИЯ-ОСНОВЫ.md
   - ДОКУМЕНТАЦИЯ-МЕТРИКИ.md
   - ДОКУМЕНТАЦИЯ-ИНСТРУМЕНТЫ.md
4. **Missing α-level:** Добавить метаданные к каждому README.md
5. **Unbalanced directions:** Создать больше ⇓ и ↔ документов (в работе!)
6. **Isolated clusters:** Добавить upward links (⇑) от кода к архитектуре

---

## 📈 Сценарий 5: Визуализация графа связей

**Задача:** Создать интерактивную HTML-визуализацию графа связей.

### Команда:

```bash
python3 tools/visualize_connections.py --format html --output graph.html
```

**Вывод:**
```
Analyzing project structure...
Found 56 documents
Found 306 connections

Generating HTML visualization...
Saved to: graph.html

Open in browser to explore:
  file:///home/user/info1/graph.html
```

### Открыть в браузере:

```bash
# Linux
xdg-open graph.html

# macOS
open graph.html

# Windows
start graph.html
```

**Возможности:**
- Интерактивный граф с Force-directed layout
- Цветовая кодировка по типам связей:
  - 🔴 Vertical Up (⇑)
  - 🔵 Vertical Down (⇓)
  - 🟢 Horizontal (↔)
- Hover для просмотра названий документов
- Клик для выделения связанных узлов

---

## 🗺️ Сценарий 6: Генерация DOT-графа для Graphviz

**Задача:** Создать статическую визуализацию для документации.

### Команда:

```bash
# Генерация DOT-файла
python3 tools/visualize_connections.py --format dot --output graph.dot

# Конвертация в PNG (требуется Graphviz)
dot -Tpng graph.dot -o graph.png

# Конвертация в SVG (векторный формат)
dot -Tsvg graph.dot -o graph.svg
```

**Результат:**
- `graph.dot` — исходный формат Graphviz
- `graph.png` — растровое изображение
- `graph.svg` — векторное изображение (масштабируется без потерь)

**Использование:**
```markdown
## Граф связей проекта

![Project Connections](graph.svg)
```

---

## 🔬 Сценарий 7: JSON API для интеграции

**Задача:** Получить метрики в JSON для обработки другими инструментами.

### Команда:

```bash
python3 tools/health_metrics.py --format json > metrics.json
```

**Вывод (metrics.json):**
```json
{
  "cd": {
    "value": 20.61,
    "unit": "%",
    "threshold": {"min": 10.0, "max": 20.0},
    "status": "moderate"
  },
  "vt": {
    "value": 23.2,
    "unit": "%",
    "threshold": {"min": 50.0, "max": 70.0},
    "status": "poor"
  },
  "cr": {
    "value": 1.05,
    "unit": "",
    "threshold": {"min": 0.7, "max": 1.5},
    "status": "optimal"
  },
  "db": {
    "value": 127.91,
    "unit": "%",
    "threshold": {"min": 0.0, "max": 30.0},
    "status": "poor"
  },
  "metadata": {
    "total_documents": 56,
    "total_connections": 306,
    "total_cycles": 7,
    "analysis_date": "2026-01-23T12:30:00"
  }
}
```

### Использование в скрипте:

```python
import json

with open('metrics.json') as f:
    metrics = json.load(f)

# Проверить, все ли метрики в норме
critical_issues = []
for metric_name, data in metrics.items():
    if metric_name == 'metadata':
        continue
    if data['status'] in ['poor', 'critical']:
        critical_issues.append(f"{metric_name.upper()}: {data['value']}{data['unit']}")

if critical_issues:
    print(f"⚠️  Critical issues found: {', '.join(critical_issues)}")
else:
    print("✅ All metrics healthy!")
```

---

## ⚙️ Сценарий 8: CI/CD интеграция

**Задача:** Автоматически проверять метрики при каждом коммите.

### GitHub Actions (.github/workflows/metrics.yml):

```yaml
- name: Check metric thresholds
  run: |
    if python3 tools/health_metrics.py --check-thresholds; then
      echo "✅ All metrics within optimal ranges"
    else
      echo "⚠️  Some metrics are outside optimal ranges"
      exit 1  # Fail the build
    fi
```

**Поведение:**
- Exit code 0 если все метрики в норме
- Exit code 1 если хотя бы одна метрика вне целевого диапазона

### Локальный pre-commit hook:

```bash
#!/bin/bash
# .git/hooks/pre-commit

echo "Checking project health metrics..."

if python3 tools/health_metrics.py --check-thresholds; then
    echo "✅ Metrics OK, proceeding with commit"
    exit 0
else
    echo "⚠️  Metrics outside optimal ranges!"
    echo "Run 'python3 tools/dashboard.py --recommendations' for details"
    echo ""
    read -p "Commit anyway? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        exit 0
    else
        exit 1
    fi
fi
```

---

## 📦 Сценарий 9: Экспорт отчёта для документации

**Задача:** Создать markdown-отчёт для добавления в документацию.

### Команда:

```bash
python3 tools/dashboard.py --export health-report.md
```

**Результат (health-report.md):**
```markdown
# Project Health Report

**Generated:** 2026-01-23 12:30:00
**Tool:** dashboard.py

## Health Metrics

- **CD (Connectivity Density)**: 20.61% ⚠️ (moderate)
- **VT (Vertical Traceability)**: 23.2% ⚠️ (poor)
- **CR (Convergence Rate)**: 1.05 ✅ (optimal)
- **DB (Directional Balance)**: 127.91% ❌ (poor)

## Anti-Patterns

Total issues: 78

- 🔴 Orphan Documents: 1
- 🟡 Dead Ends: 35
- 🟡 Hub Documents: 1
- 🔴 Unbalanced Directions: HIGH severity

## Recommendations

1. 🔴 CRITICAL: Balance next cycles: create documents in ⇓ DOWN and ↔ HORIZONTAL
2. 🔴 CRITICAL: Next 3-5 cycles: minimize ⇑ UP, focus on other directions
...
```

**Использование:**
```bash
# Добавить в README
cat health-report.md >> README.md

# Создать отдельный документ
mv health-report.md docs/HEALTH-REPORT-2026-01-23.md
```

---

## 🎨 Сценарий 10: Анализ конкретной метрики

**Задача:** Глубокий анализ одной метрики.

### Пример 1: Connectivity Density

```bash
python3 tools/health_metrics.py --metric cd
```

**Вывод:**
```
CD: 20.61% (moderate)
```

### Пример 2: Vertical Traceability

```bash
python3 tools/health_metrics.py --metric vt --format json
```

**Вывод:**
```json
{
  "vt": {
    "value": 23.2,
    "unit": "%",
    "threshold": {"min": 50.0, "max": 70.0},
    "status": "poor"
  }
}
```

**Детальный анализ:**
```bash
# Посчитать вертикальные связи вручную
python3 tools/visualize_connections.py --format json --output graph.json
cat graph.json | jq '.connections[] | select(.type | contains("vertical"))' | wc -l
```

---

## 🔄 Сценарий 11: Мониторинг изменений метрик

**Задача:** Отследить, как метрики меняются во времени.

### Скрипт мониторинга:

```bash
#!/bin/bash
# monitor_metrics.sh

DATE=$(date +%Y-%m-%d-%H-%M-%S)
OUTPUT_DIR="metrics_history"
mkdir -p "$OUTPUT_DIR"

# Сохранить метрики
python3 tools/health_metrics.py --format json > "$OUTPUT_DIR/metrics_$DATE.json"

# Сохранить рекомендации
python3 tools/dashboard.py --recommendations > "$OUTPUT_DIR/recommendations_$DATE.txt"

echo "Saved to $OUTPUT_DIR/metrics_$DATE.json"
```

### Анализ изменений:

```bash
# Посмотреть DB за последние 5 измерений
for file in $(ls -t metrics_history/metrics_*.json | head -5); do
    echo -n "$(basename $file): "
    cat "$file" | jq -r '.db.value'
done
```

**Вывод:**
```
metrics_2026-01-23-12-30-00.json: 127.91
metrics_2026-01-22-10-15-30.json: 135.42
metrics_2026-01-21-14-20-10.json: 142.18
metrics_2026-01-20-09-45-22.json: 151.67
metrics_2026-01-19-16-30-45.json: 158.93
```

**Вывод:** DB улучшается! Было 158.93%, стало 127.91% (прогресс 19.5%).

---

## 💡 Полезные комбинации команд

### Быстрый чек перед коммитом:

```bash
python3 tools/dashboard.py --quick && \
python3 tools/health_metrics.py --check-thresholds && \
echo "✅ Ready to commit!"
```

### Полный анализ проекта:

```bash
# 1. Dashboard
python3 tools/dashboard.py --export report.md

# 2. Метрики
python3 tools/health_metrics.py --detect-antipatterns > antipatterns.txt

# 3. Визуализация
python3 tools/visualize_connections.py --format html --output graph.html

echo "Generated: report.md, antipatterns.txt, graph.html"
```

### Найти orphan documents:

```bash
python3 tools/health_metrics.py --detect-antipatterns --format json | \
jq -r '.antipatterns.orphan_documents[].path'
```

### Найти hub documents:

```bash
python3 tools/health_metrics.py --detect-antipatterns --format json | \
jq -r '.antipatterns.hub_documents[] | "\(.path) (\(.connection_count) connections)"'
```

---

## 🚀 Продвинутые сценарии

### Сценарий 12: Сравнение двух версий проекта

```bash
# Текущая версия
python3 tools/health_metrics.py --format json > metrics_current.json

# Переключиться на старый коммит
git stash
git checkout HEAD~10

# Старая версия
python3 tools/health_metrics.py --format json > metrics_old.json

# Вернуться обратно
git checkout -
git stash pop

# Сравнить
python3 - <<EOF
import json
with open('metrics_current.json') as f:
    current = json.load(f)
with open('metrics_old.json') as f:
    old = json.load(f)

for metric in ['cd', 'vt', 'cr', 'db']:
    old_val = old[metric]['value']
    new_val = current[metric]['value']
    delta = new_val - old_val
    symbol = '↑' if delta > 0 else '↓'
    print(f"{metric.upper()}: {old_val} → {new_val} ({symbol}{abs(delta):.2f})")
EOF
```

---

## См. также

### ⇑ ВВЕРХ (теория и методология)

**Документация инструментов:**
- [tools/README.md](README.md) — общая документация всех инструментов (α=-2)
- [МЕТРИКИ-ЗДОРОВЬЯ.md](../МЕТРИКИ-ЗДОРОВЬЯ.md) — теоретические основы метрик CD, VT, CR, DB

**Методология и стратегия:**
- [01-Концепция/МЕТОДОЛОГИЯ-ПАРАЛЛЕЛЬНОГО-РАЗВИТИЯ.md](../01-Концепция/МЕТОДОЛОГИЯ-ПАРАЛЛЕЛЬНОГО-РАЗВИТИЯ.md) — методология ⇑⇓↔
- [ДОКУМЕНТАЦИЯ.md](../ДОКУМЕНТАЦИЯ.md) — полная документация методологии
- [ROADMAP-2026.md](../ROADMAP-2026.md) — стратегия автоматизации (ЭТАП 5-6)
- [ЭВОЛЮЦИЯ-МЕТОДОЛОГИИ.md](../ЭВОЛЮЦИЯ-МЕТОДОЛОГИИ.md) — история развития этапов

### ⇓ ВНИЗ (исполняемый код)

**Python скрипты:**
- [tools/dashboard.py](dashboard.py) — унифицированный dashboard (α=-4)
- [tools/health_metrics.py](health_metrics.py) — расчёт метрик CD, VT, CR, DB
- [tools/visualize_connections.py](visualize_connections.py) — визуализация графа связей

**Практические примеры:**
- [08-Программная-реализация/EXAMPLES.md](../08-Программная-реализация/EXAMPLES.md) — примеры кода карточной системы (α=-3)
- [08-Программная-реализация/API-REFERENCE.md](../08-Программная-реализация/API-REFERENCE.md) — API reference

**CI/CD конфигурация:**
- [.github/workflows/metrics.yml](../.github/workflows/metrics.yml) — автоматические проверки метрик
- [SETUP-CI-CD.md](../SETUP-CI-CD.md) — руководство по настройке CI/CD (α=-1)

### ↔ СВЯЗИ (руководства и навигация)

**Руководства для пользователей:**
- [QUICKSTART.md](../QUICKSTART.md) — быстрый старт за 5 минут (α=-1)
- [MIGRATION-GUIDE.md](../MIGRATION-GUIDE.md) — миграция проектов на методологию
- [ПРИМЕНЕНИЕ-МЕТОДОЛОГИИ.md](../ПРИМЕНЕНИЕ-МЕТОДОЛОГИИ.md) — паттерны применения

**Навигация и анализ:**
- [КАРТА-РЕПОЗИТОРИЯ.md](../КАРТА-РЕПОЗИТОРИЯ.md) — полный навигационный индекс (α=0)
- [ПУТЕВОДИТЕЛЬ.md](../ПУТЕВОДИТЕЛЬ.md) — альтернативная навигация
- [АНАЛИЗ-КЛАСТЕРОВ-СВЯЗЕЙ.md](../АНАЛИЗ-КЛАСТЕРОВ-СВЯЗЕЙ.md) — кластерный анализ проекта
- [ВИЗУАЛИЗАЦИЯ-ИЕРАРХИИ.md](../ВИЗУАЛИЗАЦИЯ-ИЕРАРХИИ.md) — визуализация иерархии
