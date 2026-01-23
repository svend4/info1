# Setup CI/CD — Настройка автоматизации для вашего проекта

**α-уровень:** -1 (практическое руководство)
**Направление:** ⇓ ВНИЗ (детализация)
**Цикл:** 23

---

## Обзор

Это **пошаговое руководство** по настройке CI/CD для автоматической проверки метрик здоровья проекта, следующего методологии ⇑⇓↔.

**Что вы получите:**
- ✅ Автоматическая проверка метрик при каждом коммите
- ✅ Визуализация графа связей в артефактах
- ✅ PR комментарии с метриками и anti-паттернами
- ✅ История метрик во времени
- ✅ Pre-commit hooks для локальной проверки

**Время настройки:** 15-20 минут

---

## Вариант 1: GitHub Actions (рекомендуется) 🚀

### Шаг 1: Скопировать инструменты

```bash
# Скопировать папку tools/ из info1 в ваш проект
cp -r path/to/info1/tools/ your-project/tools/

# Структура должна быть:
# your-project/
# ├── tools/
# │   ├── health_metrics.py
# │   ├── visualize_connections.py
# │   ├── dashboard.py
# │   └── README.md
# └── .github/
#     └── workflows/
#         └── metrics.yml (создадим на следующем шаге)
```

### Шаг 2: Создать GitHub Actions workflow

Создайте файл `.github/workflows/metrics.yml`:

```yaml
name: Project Health Metrics

on:
  push:
    branches:
      - main
      - master
      - 'claude/**'
  pull_request:
    branches:
      - main
      - master
  workflow_dispatch:

jobs:
  calculate-metrics:
    name: Calculate and Check Health Metrics
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v3
        with:
          fetch-depth: 0  # Full history for cycle analysis

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'

      - name: Calculate health metrics
        id: metrics
        run: |
          echo "## 📊 Project Health Metrics (⇑⇓↔)" >> $GITHUB_STEP_SUMMARY
          echo "" >> $GITHUB_STEP_SUMMARY
          python3 tools/health_metrics.py --format text >> $GITHUB_STEP_SUMMARY

      - name: Detect anti-patterns
        id: antipatterns
        run: |
          echo "" >> $GITHUB_STEP_SUMMARY
          echo "## 🔍 Anti-Pattern Detection" >> $GITHUB_STEP_SUMMARY
          echo "" >> $GITHUB_STEP_SUMMARY
          python3 tools/health_metrics.py --detect-antipatterns >> $GITHUB_STEP_SUMMARY

      - name: Check metric thresholds
        id: check
        run: |
          if python3 tools/health_metrics.py --check-thresholds; then
            echo "status=success" >> $GITHUB_OUTPUT
            echo "✅ All metrics within optimal ranges" >> $GITHUB_STEP_SUMMARY
          else
            echo "status=warning" >> $GITHUB_OUTPUT
            echo "⚠️  Some metrics are outside optimal ranges" >> $GITHUB_STEP_SUMMARY
          fi

      - name: Export metrics as JSON artifact
        run: |
          python3 tools/health_metrics.py --format json > metrics.json

      - name: Upload metrics artifact
        uses: actions/upload-artifact@v3
        with:
          name: health-metrics
          path: metrics.json
          retention-days: 90

      - name: Generate anti-patterns JSON
        run: |
          python3 tools/health_metrics.py --detect-antipatterns --format json > antipatterns.json

      - name: Comment on PR (if applicable)
        if: github.event_name == 'pull_request'
        uses: actions/github-script@v6
        with:
          script: |
            const fs = require('fs');
            const metrics = JSON.parse(fs.readFileSync('metrics.json', 'utf8'));

            let antipatterns = {};
            try {
              antipatterns = JSON.parse(fs.readFileSync('antipatterns.json', 'utf8'));
            } catch (e) {
              console.log('Anti-patterns file not found, skipping');
            }

            let body = '## 📊 Project Health Metrics (⇑⇓↔)\n\n';

            // Format metrics
            const metricsData = [
              { name: 'CD (Connectivity Density)', key: 'cd' },
              { name: 'VT (Vertical Traceability)', key: 'vt' },
              { name: 'CR (Convergence Rate)', key: 'cr' },
              { name: 'DB (Directional Balance)', key: 'db' }
            ];

            for (const m of metricsData) {
              const data = metrics[m.key];
              const status = data.status === 'optimal' || data.status === 'excellent' || data.status === 'good' ? '✅' : '⚠️';
              body += `- **${m.name}**: ${data.value}${data.unit} ${status} (${data.status})\n`;
            }

            body += `\n**Documents**: ${metrics.metadata.total_documents} | **Connections**: ${metrics.metadata.total_connections} | **Cycles**: ${metrics.metadata.total_cycles}`;

            // Add anti-pattern summary if available
            if (antipatterns.summary) {
              const sum = antipatterns.summary;
              body += `\n\n### 🔍 Anti-Patterns Detected\n\n`;
              body += `- **Total Issues**: ${sum.total_antipatterns}\n`;
              if (sum.critical_count > 0) {
                body += `- 🔴 **Critical**: ${sum.critical_count}\n`;
              }
              if (sum.high_count > 0) {
                body += `- ⚠️  **High**: ${sum.high_count}\n`;
              }
              if (sum.medium_count > 0) {
                body += `- 🟡 **Medium**: ${sum.medium_count}\n`;
              }
            }

            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: body
            });

  visualize-connections:
    name: Generate Connection Visualizations
    runs-on: ubuntu-latest
    if: github.event_name == 'push'

    steps:
      - name: Checkout repository
        uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'

      - name: Generate DOT graph
        run: |
          python3 tools/visualize_connections.py --format dot --output graph.dot

      - name: Generate HTML visualization
        run: |
          python3 tools/visualize_connections.py --format html --output graph.html

      - name: Generate JSON graph
        run: |
          python3 tools/visualize_connections.py --format json --output graph.json

      - name: Upload visualizations
        uses: actions/upload-artifact@v3
        with:
          name: connection-visualizations
          path: |
            graph.dot
            graph.html
            graph.json
          retention-days: 90

  track-metrics-over-time:
    name: Track Metrics History
    runs-on: ubuntu-latest
    if: github.event_name == 'push' && (github.ref == 'refs/heads/main' || github.ref == 'refs/heads/master')

    steps:
      - name: Checkout repository
        uses: actions/checkout@v3
        with:
          fetch-depth: 0

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'

      - name: Calculate metrics
        run: |
          python3 tools/health_metrics.py --format json > current_metrics.json

      - name: Checkout metrics branch
        run: |
          git fetch origin metrics-history:metrics-history || git checkout -b metrics-history
          git checkout metrics-history || git checkout --orphan metrics-history

      - name: Append to history
        run: |
          mkdir -p history
          DATE=$(date +%Y-%m-%d-%H-%M-%S)
          COMMIT=$(git rev-parse HEAD)
          cp current_metrics.json history/${DATE}_${COMMIT:0:7}.json

          # Keep only last 100 entries
          cd history
          ls -t *.json | tail -n +101 | xargs -r rm
          cd ..

      - name: Commit and push history
        run: |
          git config user.name "GitHub Actions"
          git config user.email "actions@github.com"
          git add history/
          git commit -m "Update metrics history: $(date +%Y-%m-%d)" || echo "No changes to commit"
          git push origin metrics-history || echo "Push failed, continuing"
```

### Шаг 3: Закоммитить и запушить

```bash
git add .github/workflows/metrics.yml tools/
git commit -m "Add CI/CD: automated health metrics monitoring"
git push
```

### Шаг 4: Проверить результат

1. Перейдите на GitHub → вкладка **Actions**
2. Вы увидите запущенный workflow "Project Health Metrics"
3. Кликните на него, чтобы увидеть детали
4. Во вкладке **Summary** увидите метрики и anti-паттерны

**Пример вывода в GitHub Summary:**
```
📊 Project Health Metrics (⇑⇓↔)

CD (Connectivity Density)
  Value: 20.61% ⚠️ (moderate)
  Target: 10.0-20.0%

VT (Vertical Traceability)
  Value: 28.14% ⚠️ (poor)
  Target: 50.0-70.0%

...

🔍 Anti-Pattern Detection

🔴 Orphan Documents (1):
   Documents with no connections at all
   - path/to/document.md

...
```

---

## Вариант 2: GitLab CI/CD 🦊

Создайте файл `.gitlab-ci.yml`:

```yaml
stages:
  - analyze
  - visualize

health-metrics:
  stage: analyze
  image: python:3.9
  script:
    - python3 tools/health_metrics.py
    - python3 tools/health_metrics.py --detect-antipatterns
    - python3 tools/health_metrics.py --format json > metrics.json
  artifacts:
    paths:
      - metrics.json
    expire_in: 90 days
  rules:
    - if: '$CI_PIPELINE_SOURCE == "push" || $CI_PIPELINE_SOURCE == "merge_request_event"'

visualize-connections:
  stage: visualize
  image: python:3.9
  script:
    - python3 tools/visualize_connections.py --format html --output graph.html
    - python3 tools/visualize_connections.py --format dot --output graph.dot
    - python3 tools/visualize_connections.py --format json --output graph.json
  artifacts:
    paths:
      - graph.html
      - graph.dot
      - graph.json
    expire_in: 90 days
  rules:
    - if: '$CI_PIPELINE_SOURCE == "push"'
```

---

## Вариант 3: Локальные pre-commit hooks 🔒

### Установка pre-commit hook

Создайте файл `.git/hooks/pre-commit`:

```bash
#!/bin/bash

echo "🔍 Checking project health metrics..."

# Run quick dashboard check
python3 tools/dashboard.py --quick

# Check if metrics are within thresholds
if python3 tools/health_metrics.py --check-thresholds; then
    echo "✅ Metrics OK, proceeding with commit"
    exit 0
else
    echo ""
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

Сделайте hook исполняемым:

```bash
chmod +x .git/hooks/pre-commit
```

**Тестирование:**

```bash
# Создайте тестовый коммит
echo "test" >> test.txt
git add test.txt
git commit -m "Test pre-commit hook"

# Вы увидите проверку метрик перед коммитом
```

---

## Вариант 4: Jenkins Pipeline 🔧

Создайте `Jenkinsfile`:

```groovy
pipeline {
    agent any

    stages {
        stage('Setup') {
            steps {
                sh 'python3 --version'
            }
        }

        stage('Calculate Metrics') {
            steps {
                sh 'python3 tools/health_metrics.py'
                sh 'python3 tools/health_metrics.py --format json > metrics.json'
                archiveArtifacts artifacts: 'metrics.json', fingerprint: true
            }
        }

        stage('Detect Anti-Patterns') {
            steps {
                sh 'python3 tools/health_metrics.py --detect-antipatterns'
            }
        }

        stage('Visualize Connections') {
            steps {
                sh 'python3 tools/visualize_connections.py --format html --output graph.html'
                sh 'python3 tools/visualize_connections.py --format dot --output graph.dot'
                archiveArtifacts artifacts: 'graph.*', fingerprint: true
            }
        }

        stage('Check Thresholds') {
            steps {
                script {
                    def result = sh(
                        script: 'python3 tools/health_metrics.py --check-thresholds',
                        returnStatus: true
                    )
                    if (result != 0) {
                        unstable(message: "Metrics outside optimal ranges")
                    }
                }
            }
        }
    }

    post {
        always {
            publishHTML([
                reportDir: '.',
                reportFiles: 'graph.html',
                reportName: 'Connection Graph'
            ])
        }
    }
}
```

---

## Расширенные настройки 🎛️

### 1. Fail build при критических проблемах

Измените шаг "Check metric thresholds":

```yaml
- name: Check metric thresholds
  run: |
    if ! python3 tools/health_metrics.py --check-thresholds; then
      echo "❌ FAILED: Metrics outside optimal ranges"
      exit 1  # Fail the build
    fi
```

### 2. Уведомления в Slack

Добавьте шаг после проверки метрик:

```yaml
- name: Notify Slack
  if: failure()
  uses: 8398a7/action-slack@v3
  with:
    status: ${{ job.status }}
    text: '⚠️  Health metrics check failed!'
    webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

### 3. Генерация отчётов в markdown

Добавьте шаг:

```yaml
- name: Generate markdown report
  run: |
    python3 tools/dashboard.py --export health-report.md

- name: Upload report
  uses: actions/upload-artifact@v3
  with:
    name: health-report
    path: health-report.md
```

### 4. Сравнение с предыдущим коммитом

```yaml
- name: Compare with previous
  run: |
    git checkout HEAD~1
    python3 tools/health_metrics.py --format json > metrics_old.json
    git checkout -
    python3 tools/health_metrics.py --format json > metrics_new.json

    # Compare (requires jq)
    echo "## 📈 Metrics Comparison" >> $GITHUB_STEP_SUMMARY
    echo "" >> $GITHUB_STEP_SUMMARY
    echo "Old DB: $(jq -r '.db.value' metrics_old.json)" >> $GITHUB_STEP_SUMMARY
    echo "New DB: $(jq -r '.db.value' metrics_new.json)" >> $GITHUB_STEP_SUMMARY
```

---

## Troubleshooting 🔧

### Проблема: "ModuleNotFoundError: No module named 'pathlib'"

**Решение:** Используйте Python 3.8+

```yaml
- name: Set up Python
  uses: actions/setup-python@v4
  with:
    python-version: '3.9'  # Или выше
```

### Проблема: "Permission denied" при push в metrics-history

**Решение:** Дайте workflow права на запись:

```yaml
permissions:
  contents: write  # Разрешить push в репозиторий
```

### Проблема: Workflow не запускается на pull requests

**Решение:** Проверьте секцию `on:`:

```yaml
on:
  pull_request:
    branches:
      - main
      - master
```

### Проблема: Метрики показывают 0 документов

**Решение:** Убедитесь, что используете `fetch-depth: 0`:

```yaml
- name: Checkout repository
  uses: actions/checkout@v3
  with:
    fetch-depth: 0  # Важно!
```

---

## Рекомендации по использованию 💡

### Для небольших проектов (<50 документов):

- Используйте только `calculate-metrics` job
- Запускайте на каждом push
- Не требуйте прохождения проверок (warning mode)

### Для средних проектов (50-200 документов):

- Используйте все 3 jobs (metrics + visualize + history)
- Запускайте на push в main и на PR
- Требуйте прохождения проверок для merge

### Для крупных проектов (>200 документов):

- Используйте все jobs + кэширование
- Запускайте только на PR и push в main
- Добавьте manual trigger для on-demand анализа
- Используйте matrix strategy для параллельного анализа

**Пример с кэшированием:**

```yaml
- name: Cache analysis results
  uses: actions/cache@v3
  with:
    path: .metrics-cache
    key: metrics-${{ hashFiles('**/*.md') }}
```

---

## Интеграция с другими инструментами 🔗

### 1. Codecov (для покрытия кода)

```yaml
- name: Upload to Codecov
  uses: codecov/codecov-action@v3
  with:
    files: ./metrics.json
```

### 2. SonarQube (для качества кода)

```yaml
- name: SonarQube Scan
  uses: sonarsource/sonarqube-scan-action@master
  env:
    SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
    SONAR_HOST_URL: ${{ secrets.SONAR_HOST_URL }}
```

### 3. Dependabot (для зависимостей)

Создайте `.github/dependabot.yml`:

```yaml
version: 2
updates:
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
```

---

## Метрики эффективности CI/CD 📊

После настройки отслеживайте:

1. **Время выполнения workflow:** Должно быть <2 минут для небольших проектов
2. **Частота failed builds:** Не более 10% от общего числа
3. **Количество пойманных проблем:** Должно расти в первые недели, затем стабилизироваться
4. **Время до исправления:** От обнаружения проблемы до fix

---

## Следующие шаги 🚀

После настройки CI/CD:

1. ✅ Запустите первый workflow и проверьте результаты
2. ✅ Настройте уведомления (email, Slack, Discord)
3. ✅ Добавьте badge в README.md
4. ✅ Настройте branch protection rules
5. ✅ Обучите команду использованию dashboard

**Добавление badge в README:**

```markdown
![Health Metrics](https://github.com/username/repo/actions/workflows/metrics.yml/badge.svg)
```

---

## См. также

- [tools/README.md](tools/README.md) — документация инструментов
- [tools/EXAMPLES.md](tools/EXAMPLES.md) — примеры использования
- [QUICK-START.md](QUICK-START.md) — быстрый старт
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) — решение проблем

**Навигация:**
- ⇑ ВВЕРХ: [ДОКУМЕНТАЦИЯ.md](ДОКУМЕНТАЦИЯ.md) — теоретические основы методологии
- ⇓ ВНИЗ: [tools/EXAMPLES.md](tools/EXAMPLES.md) — конкретные примеры команд
- ↔ СВЯЗИ: [DEPLOYMENT.md](DEPLOYMENT.md) — развёртывание проекта
