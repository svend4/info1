# Troubleshooting — Решение частых проблем

**α-уровень:** -1 (практическое руководство)
**Направление:** ⇓ ВНИЗ (детализация)
**Цикл:** 23

---

## Обзор

Этот документ содержит **решения частых проблем**, с которыми вы можете столкнуться при использовании методологии ⇑⇓↔ и инструментов автоматизации.

**Формат:** Проблема → Причина → Решение → Проверка

---

## 🔴 Проблемы с инструментами

### Проблема 1: "FileNotFoundError: [Errno 2] No such file or directory"

**Симптомы:**
```bash
$ python3 tools/health_metrics.py
Traceback (most recent call last):
  File "tools/health_metrics.py", line 45, in <module>
    with open('ДОКУМЕНТАЦИЯ.md', 'r') as f:
FileNotFoundError: [Errno 2] No such file or directory: 'ДОКУМЕНТАЦИЯ.md'
```

**Причина:** Запуск скрипта не из корня проекта.

**Решение:**
```bash
# Перейдите в корень проекта
cd /path/to/your/project

# Проверьте, что вы в правильной директории
ls -la | grep ДОКУМЕНТАЦИЯ.md

# Запустите скрипт
python3 tools/health_metrics.py
```

**Или используйте --root параметр:**
```bash
python3 tools/health_metrics.py --root /path/to/your/project
```

**Проверка:**
```bash
python3 tools/dashboard.py --quick
# Должно показать метрики без ошибок
```

---

### Проблема 2: "ModuleNotFoundError: No module named 'pathlib'"

**Симптомы:**
```bash
$ python tools/health_metrics.py
ModuleNotFoundError: No module named 'pathlib'
```

**Причина:** Используется Python 2.x или Python < 3.4.

**Решение:**
```bash
# Проверьте версию Python
python3 --version
# Должно быть 3.8+

# Используйте python3 вместо python
python3 tools/health_metrics.py
```

**Если Python 3.8+ не установлен:**
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3.9

# macOS
brew install python@3.9

# Windows
# Скачайте с https://www.python.org/downloads/
```

**Проверка:**
```bash
python3 --version
# Должно показать Python 3.8.0 или выше
```

---

### Проблема 3: Инструменты находят 0 документов

**Симптомы:**
```bash
$ python3 tools/health_metrics.py
Total documents: 0
Total connections: 0
```

**Причина:** Документы не соответствуют формату или находятся не в правильных директориях.

**Решение 1: Проверьте структуру проекта**
```bash
# Должны быть .md файлы в корне или подпапках
find . -name "*.md" -type f | head -10
```

**Решение 2: Проверьте метаданные документов**

Каждый документ должен содержать:
```markdown
**α-уровень:** X
**Направление:** ⇑ ВВЕРХ (или ⇓ ВНИЗ, или ↔ СВЯЗИ)
**Цикл:** Y
```

**Решение 3: Проверьте кодировку файлов**
```bash
# Должна быть UTF-8
file ДОКУМЕНТАЦИЯ.md
# Вывод: ДОКУМЕНТАЦИЯ.md: UTF-8 Unicode text
```

**Проверка:**
```bash
python3 -c "
from pathlib import Path
import re

docs = list(Path('.').rglob('*.md'))
print(f'Found {len(docs)} .md files')

# Проверить первый документ
if docs:
    with open(docs[0], 'r', encoding='utf-8') as f:
        content = f.read()
        if 'α-уровень' in content:
            print('✅ Metadata found')
        else:
            print('❌ No metadata')
"
```

---

### Проблема 4: "UnicodeDecodeError: 'charmap' codec can't decode"

**Симптомы (Windows):**
```bash
UnicodeDecodeError: 'charmap' codec can't decode byte 0x98 in position 123
```

**Причина:** Windows по умолчанию использует кодировку cp1252 вместо UTF-8.

**Решение:**
```bash
# Установите переменную окружения
set PYTHONUTF8=1

# Или используйте chcp
chcp 65001

# Запустите скрипт
python3 tools/health_metrics.py
```

**Постоянное решение (добавьте в .bashrc или .zshrc):**
```bash
export PYTHONUTF8=1
```

**Проверка:**
```bash
python3 -c "import sys; print(sys.getdefaultencoding())"
# Должно показать: utf-8
```

---

## 📊 Проблемы с метриками

### Проблема 5: DB (Directional Balance) = 0%

**Симптомы:**
```bash
DB (Directional Balance)
  Value: 0.0% ✅ (excellent)
```

**Причина:** Все документы имеют одинаковое направление или метаданные не парсятся.

**Диагностика:**
```bash
python3 tools/health_metrics.py --detect-antipatterns | grep "Unbalanced Directions"
```

**Решение:** Добавьте метаданные направлений к документам:
```markdown
**Направление:** ⇑ ВВЕРХ (обобщение)
# или
**Направление:** ⇓ ВНИЗ (детализация)
# или
**Направление:** ↔ СВЯЗИ (горизонтальные)
```

**Проверка:**
```bash
# Проверить распределение направлений
grep -r "Направление:" --include="*.md" . | wc -l
# Должно быть > 0
```

---

### Проблема 6: VT (Vertical Traceability) = 0%

**Симптомы:**
```bash
VT (Vertical Traceability)
  Value: 0.0% ❌ (critical)
```

**Причина:** Нет вертикальных связей между уровнями абстракции (|Δα| >= 2).

**Решение:** Добавьте связи между документами разных уровней:

```markdown
<!-- В документе α=+2 (методология) -->
См. также:
- [Практическое руководство](QUICK-START.md) (α=-1) ← Δα = 3
- [Примеры](tools/EXAMPLES.md) (α=-2) ← Δα = 4

<!-- В документе α=-2 (примеры) -->
См. также:
- [Методология](ДОКУМЕНТАЦИЯ.md) (α=+2) ← Δα = 4
```

**Проверка:**
```bash
python3 tools/health_metrics.py --metric vt
# Должно показать VT > 0%
```

---

### Проблема 7: CD (Connectivity Density) слишком высокий (>30%)

**Симптомы:**
```bash
CD (Connectivity Density)
  Value: 45.2% ⚠️ (high)
```

**Причина:** Слишком много связей → сложная навигация.

**Решение:**
1. Разбейте hub documents на меньшие части
2. Удалите дублирующиеся ссылки
3. Сгруппируйте похожие документы

**Пример рефакторинга:**
```markdown
<!-- Было: ДОКУМЕНТАЦИЯ.md со 100+ ссылками -->

<!-- Стало: разбили на 3 файла -->
- ДОКУМЕНТАЦИЯ-ОСНОВЫ.md (20 ссылок)
- ДОКУМЕНТАЦИЯ-МЕТРИКИ.md (15 ссылок)
- ДОКУМЕНТАЦИЯ-ИНСТРУМЕНТЫ.md (18 ссылок)
```

**Проверка:**
```bash
python3 tools/dashboard.py --recommendations | grep "Hub Document"
# Не должно быть документов с >20 связями
```

---

## 🔗 Проблемы со связями

### Проблема 8: Инструменты находят 0 связей

**Симптомы:**
```bash
Total connections: 0
```

**Причина:** Ссылки в неправильном формате или внешние (HTTP).

**Диагностика:**
```bash
# Проверить, есть ли вообще ссылки
grep -r "\[.*\](.*\.md)" --include="*.md" . | wc -l
```

**Решение:** Используйте правильный формат markdown-ссылок:

```markdown
✅ Правильно:
[Документация](ДОКУМЕНТАЦИЯ.md)
[Примеры](tools/EXAMPLES.md)
[Руководство](../QUICK-START.md)

❌ Неправильно:
<a href="ДОКУМЕНТАЦИЯ.md">Документация</a>
https://example.com/ДОКУМЕНТАЦИЯ.md
[Документация](ДОКУМЕНТАЦИЯ)  ← без .md
```

**Проверка:**
```bash
python3 tools/visualize_connections.py --format json --output graph.json
cat graph.json | jq '.connections | length'
# Должно быть > 0
```

---

### Проблема 9: Relative links не распознаются

**Симптомы:**
Ссылки вида `../ДОКУМЕНТАЦИЯ.md` или `./tools/README.md` не находятся.

**Причина:** Путь разрешается относительно документа, а не корня.

**Решение:** Инструменты автоматически разрешают относительные пути. Если не работает:

```bash
# Используйте абсолютные пути от корня
[Документация](/ДОКУМЕНТАЦИЯ.md)
[Примеры](/tools/EXAMPLES.md)
```

**Или проверьте, что ссылки корректны:**
```bash
# Из файла tools/README.md
[Документация](../ДОКУМЕНТАЦИЯ.md)  ✅ Работает
[Документация](ДОКУМЕНТАЦИЯ.md)     ❌ Не работает (ищет в tools/)
```

**Проверка:**
```bash
python3 -c "
from pathlib import Path

# Проверить относительный путь
source = Path('tools/README.md')
link = '../ДОКУМЕНТАЦИЯ.md'
target = (source.parent / link).resolve()
print(f'Resolves to: {target}')
print(f'Exists: {target.exists()}')
"
```

---

## 🔴 Проблемы с anti-паттернами

### Проблема 10: Слишком много orphan documents

**Симптомы:**
```bash
🔴 Orphan Documents (15):
   Documents with no connections at all
```

**Причина:** Документы не связаны с другими частями проекта.

**Решение:**
1. Добавьте ссылки НА orphan document из других документов
2. Добавьте ссылки ИЗ orphan document на другие документы
3. Удалите документ, если он устарел

**Пример исправления:**
```markdown
<!-- В КАРТА-РЕПОЗИТОРИЯ.md -->
См. также:
- [Orphan Document](path/to/orphan.md)

<!-- В orphan.md -->
См. также:
- [Документация](ДОКУМЕНТАЦИЯ.md)
- [Карта](КАРТА-РЕПОЗИТОРИЯ.md)
```

**Проверка:**
```bash
python3 tools/health_metrics.py --detect-antipatterns | grep "Orphan"
# Должно быть 0 или минимум
```

---

### Проблема 11: Слишком много dead-end documents

**Симптомы:**
```bash
🟡 Dead Ends (36):
   Documents without outgoing links
```

**Причина:** Документы не ссылаются ни на что (нет исходящих ссылок).

**Решение:** Добавьте секцию "См. также" в каждый dead-end документ:

```markdown
## См. также

- [Документация](ДОКУМЕНТАЦИЯ.md) — теоретические основы
- [Примеры](tools/EXAMPLES.md) — практические примеры
- [Карта](КАРТА-РЕПОЗИТОРИЯ.md) — навигация по проекту
```

**Массовое исправление (скрипт):**
```bash
#!/bin/bash
# add_see_also.sh

for file in $(python3 tools/health_metrics.py --detect-antipatterns | grep -A 100 "Dead Ends" | grep "\.md" | awk '{print $2}'); do
    echo "" >> "$file"
    echo "---" >> "$file"
    echo "" >> "$file"
    echo "## См. также" >> "$file"
    echo "" >> "$file"
    echo "- [Документация](ДОКУМЕНТАЦИЯ.md)" >> "$file"
    echo "- [Карта репозитория](КАРТА-РЕПОЗИТОРИЯ.md)" >> "$file"
done
```

**Проверка:**
```bash
python3 tools/dashboard.py --recommendations | grep "Dead-End"
# Количество должно уменьшиться
```

---

## 🚀 Проблемы с CI/CD

### Проблема 12: GitHub Actions workflow не запускается

**Симптомы:**
Workflow не появляется во вкладке Actions после push.

**Причина:** Неправильная конфигурация triggers или синтаксическая ошибка в YAML.

**Диагностика:**
```bash
# Проверить синтаксис YAML
yamllint .github/workflows/metrics.yml

# Или онлайн: https://www.yamllint.com/
```

**Решение:**
```yaml
# Проверьте секцию on:
on:
  push:
    branches:
      - main
      - master
  pull_request:
    branches:
      - main
      - master
```

**Проверка:**
```bash
# Сделайте тестовый коммит
echo "test" >> test.txt
git add test.txt
git commit -m "Test workflow trigger"
git push

# Проверьте на GitHub → Actions
```

---

### Проблема 13: Workflow падает с "Permission denied"

**Симптомы:**
```
Error: Permission denied (publickey)
fatal: Could not read from remote repository
```

**Причина:** Workflow не имеет прав на push в репозиторий (для metrics-history).

**Решение:** Добавьте permissions в workflow:

```yaml
jobs:
  track-metrics-over-time:
    permissions:
      contents: write  # Разрешить push
    runs-on: ubuntu-latest
    # ... остальное
```

**Проверка:**
```bash
# Проверьте логи workflow на GitHub
# Должно быть: ✅ Successfully pushed to metrics-history
```

---

### Проблема 14: PR комментарий не создаётся

**Симптомы:**
Workflow успешно завершается, но комментарий с метриками не появляется в PR.

**Причина:** У GitHub token нет прав на создание комментариев.

**Решение 1:** Добавьте permissions:

```yaml
jobs:
  calculate-metrics:
    permissions:
      pull-requests: write  # Разрешить комментировать PR
    # ... остальное
```

**Решение 2:** Используйте PAT (Personal Access Token):

```yaml
- name: Comment on PR
  uses: actions/github-script@v6
  with:
    github-token: ${{ secrets.GITHUB_TOKEN }}  # Или PAT
    # ... остальное
```

**Проверка:**
Создайте тестовый PR и проверьте комментарии.

---

## 📈 Проблемы с производительностью

### Проблема 15: Инструменты работают слишком медленно

**Симптомы:**
```bash
$ time python3 tools/health_metrics.py
real    2m15.432s  ← Слишком долго!
```

**Причина:** Большое количество документов или сложный граф связей.

**Решение 1: Используйте кэширование**

```python
# В health_metrics.py
import pickle
from pathlib import Path

cache_file = Path('.metrics-cache.pkl')
if cache_file.exists():
    with open(cache_file, 'rb') as f:
        cached_data = pickle.load(f)
    # Используйте cached_data
```

**Решение 2: Оптимизируйте граф**

```bash
# Найдите документы с большим количеством связей
python3 tools/health_metrics.py --detect-antipatterns | grep "Hub Documents"

# Разбейте их на меньшие части
```

**Решение 3: Используйте --quick режим**

```bash
python3 tools/dashboard.py --quick  # Быстрее чем полный анализ
```

**Проверка:**
```bash
time python3 tools/dashboard.py --quick
# Должно быть < 10 секунд для проектов <100 документов
```

---

## 🔧 Проблемы с миграцией

### Проблема 16: Не понятно, с чего начать миграцию

**Симптомы:**
Существующий проект, нужно применить методологию ⇑⇓↔.

**Решение:** Следуйте [MIGRATION-GUIDE.md](MIGRATION-GUIDE.md):

```bash
# Этап 0: Подготовка
cp -r info1/tools/ your-project/tools/

# Этап 1: Маркировка (добавьте метаданные к 5-10 ключевым документам)
# В каждом документе:
# **α-уровень:** X
# **Направление:** ⇑/⇓/↔
# **Цикл:** 1

# Этап 2: Первый цикл (создайте 1 новый документ в каждом направлении)

# Этап 3: Измерение
python3 tools/dashboard.py --quick

# Этап 4: Регулярные циклы
```

**Проверка:**
```bash
python3 tools/health_metrics.py
# Должны увидеть метрики > 0
```

---

### Проблема 17: После миграции DB > 100%

**Симптомы:**
```bash
DB (Directional Balance): 150.0% ❌ (critical)
```

**Причина:** Большинство документов в одном направлении (обычно ⇑ ВВЕРХ).

**Решение:** Создайте баланс:

```bash
# Проверьте распределение
python3 tools/health_metrics.py --detect-antipatterns | grep "Unbalanced"
# Вывод: ⇑ UP: 80 (95.2%), ⇓ DOWN: 2 (2.4%), ↔ HORIZONTAL: 2 (2.4%)

# Следующие 5 циклов: создавайте только ⇓ и ↔ документы
# Цель: довести до ~33% / 33% / 33%
```

**Примеры документов для баланса:**
- ⇓ ВНИЗ: руководства, примеры, troubleshooting, tutorials
- ↔ СВЯЗИ: карты, индексы, навигационные документы

**Проверка:**
```bash
python3 tools/dashboard.py --recommendations
# Первая рекомендация не должна быть про DB
```

---

## 💡 Лучшие практики для предотвращения проблем

### 1. Ежедневная проверка здоровья

```bash
# Добавьте в daily routine
python3 tools/dashboard.py --quick
```

### 2. Pre-commit hooks

```bash
# См. SETUP-CI-CD.md для настройки
chmod +x .git/hooks/pre-commit
```

### 3. Регулярный анализ anti-паттернов

```bash
# Раз в неделю
python3 tools/health_metrics.py --detect-antipatterns > antipatterns_$(date +%Y-%m-%d).txt
```

### 4. Документируйте метаданные

Всегда добавляйте к новым документам:
```markdown
**α-уровень:** X
**Направление:** ⇑/⇓/↔
**Цикл:** Y
```

### 5. Поддерживайте связность

Каждый новый документ должен иметь:
- Минимум 2-3 входящие ссылки
- Минимум 2-3 исходящие ссылки

---

## 🆘 Получение помощи

Если проблема не решена:

1. **Проверьте документацию:**
   - [tools/README.md](tools/README.md) — инструменты
   - [QUICK-START.md](QUICK-START.md) — быстрый старт
   - [tools/EXAMPLES.md](tools/EXAMPLES.md) — примеры

2. **Запустите диагностику:**
   ```bash
   python3 tools/dashboard.py --recommendations
   ```

3. **Проверьте логи:**
   ```bash
   python3 tools/health_metrics.py --debug 2>&1 | tee debug.log
   ```

4. **Создайте минимальный воспроизводимый пример:**
   ```bash
   # Создайте тестовый проект
   mkdir test-project
   cd test-project
   echo "# Test" > README.md
   cp -r /path/to/info1/tools/ .
   python3 tools/health_metrics.py
   ```

---

## См. также

- [tools/README.md](tools/README.md) — документация инструментов
- [tools/EXAMPLES.md](tools/EXAMPLES.md) — примеры использования
- [SETUP-CI-CD.md](SETUP-CI-CD.md) — настройка автоматизации
- [MIGRATION-GUIDE.md](MIGRATION-GUIDE.md) — миграция проектов
- [QUICK-START.md](QUICK-START.md) — быстрый старт

**Навигация:**
- ⇑ ВВЕРХ: [ДОКУМЕНТАЦИЯ.md](ДОКУМЕНТАЦИЯ.md) — теоретические основы
- ⇓ ВНИЗ: [tools/EXAMPLES.md](tools/EXAMPLES.md) — конкретные примеры
- ↔ СВЯЗИ: [КАРТА-РЕПОЗИТОРИЯ.md](КАРТА-РЕПОЗИТОРИЯ.md) — навигация
