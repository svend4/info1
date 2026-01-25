# Advanced Features - Cutting-edge AI Capabilities

🚀 **Расширенные возможности для AI-powered генератора проектов**

---

## 📋 Обзор

Advanced Features включает cutting-edge функциональность:
- ✅ **Project Evolution Tracking** - отслеживание изменений проекта
- ✅ **Technical Debt Detection** - автоматическое обнаружение проблем
- ✅ **Health Monitoring** - мониторинг здоровья проекта
- ✅ **Refactoring Suggestions** - AI-powered рекомендации
- ✅ **Code Metrics** - детальные метрики кода
- ✅ **Trend Analysis** - анализ трендов развития

---

## 🎯 Возможности

### 1. Project Evolution Tracking

Автоматическое отслеживание как проект развивается:
- Snapshots структуры проекта
- Изменения в количестве файлов и строк кода
- History всех изменений
- Сравнение между versions

### 2. Code Metrics

Детальные метрики качества кода:
- Lines of Code (LOC)
- Code vs Comments ratio
- Cyclomatic complexity
- Functions и classes count
- Test coverage
- Duplication detection

### 3. Technical Debt Detection

Автоматическое обнаружение проблем:
- Слишком большие функции
- Missing docstrings
- Code smells
- Security vulnerabilities
- Complexity hotspots
- Dead code

### 4. Health Monitoring

Комплексная оценка здоровья проекта:
- Overall health score (0-100)
- Structure quality
- Code quality
- Test coverage
- Documentation completeness
- Maintainability score

### 5. Refactoring Suggestions

AI-powered рекомендации по улучшению:
- Extract method
- Simplify complex functions
- Add missing tests
- Improve documentation
- Reduce duplication

---

## 🚀 Quick Start

### Project Evolution Tracking

```python
from pathlib import Path
from project_evolution_tracker import ProjectEvolutionTracker

# Создание tracker
tracker = ProjectEvolutionTracker(Path('./my-project'))

# Создание snapshot
snapshot = tracker.take_snapshot()
print(f"Snapshot: {snapshot.files_count} files, {snapshot.lines_of_code} LOC")

# Вычисление metrics
metrics = tracker.calculate_metrics()
print(f"Metrics: {metrics.code_lines} LOC, {metrics.functions_count} functions")

# Обнаружение technical debt
debt = tracker.detect_technical_debt()
print(f"Technical debt: {len(debt)} items")

# Health score
health = tracker.calculate_health_score()
print(f"Health: {health.overall_score}/100")

# Полный отчёт
report = tracker.get_evolution_report()
print(json.dumps(report, indent=2))
```

---

## 📊 Project Evolution Tracking

### Taking Snapshots

```python
tracker = ProjectEvolutionTracker(Path('./my-project'))

# Initial snapshot
tracker.take_snapshot()

# ... работаем над проектом ...

# Ещё snapshot
tracker.take_snapshot()

# Сравнение
first = tracker.snapshots[0]
latest = tracker.snapshots[-1]

print(f"Files: {first.files_count} → {latest.files_count}")
print(f"LOC: {first.lines_of_code} → {latest.lines_of_code}")
```

### Structure Changes

```python
# Получить изменённые файлы
first_hashes = tracker.snapshots[0].file_hashes
latest_hashes = tracker.snapshots[-1].file_hashes

added_files = set(latest_hashes.keys()) - set(first_hashes.keys())
removed_files = set(first_hashes.keys()) - set(latest_hashes.keys())
modified_files = {
    f for f in first_hashes
    if f in latest_hashes and first_hashes[f] != latest_hashes[f]
}

print(f"Added: {len(added_files)}")
print(f"Removed: {len(removed_files)}")
print(f"Modified: {len(modified_files)}")
```

### Evolution Report

```python
report = tracker.get_evolution_report()

print(f"Tracking period: {report['tracking_period']['start']} → {report['tracking_period']['end']}")
print(f"\nGrowth:")
print(f"  Files: {report['growth']['files']['change']} ({report['growth']['files']['change_percent']}%)")
print(f"  LOC: {report['growth']['lines_of_code']['change']} ({report['growth']['lines_of_code']['change_percent']}%)")
print(f"\nTechnical Debt:")
print(f"  Total: {report['technical_debt']['total_items']}")
print(f"  Critical: {report['technical_debt']['critical']}")
print(f"  Effort: {report['technical_debt']['estimated_effort_hours']} hours")
print(f"\nHealth Score: {report['current_health']['overall_score']}/100")
```

---

## 📈 Code Metrics

### Basic Metrics

```python
metrics = tracker.calculate_metrics()

print(f"Total Lines: {metrics.total_lines}")
print(f"Code Lines: {metrics.code_lines}")
print(f"Comment Lines: {metrics.comment_lines}")
print(f"Blank Lines: {metrics.blank_lines}")
print(f"\nFiles: {metrics.files_count}")
print(f"Functions: {metrics.functions_count}")
print(f"Classes: {metrics.classes_count}")
```

### Metrics Over Time

```python
# Собираем metrics регулярно
import schedule
import time

def collect_metrics():
    tracker.calculate_metrics()
    tracker.take_snapshot()

# Каждый день в полночь
schedule.every().day.at("00:00").do(collect_metrics)

while True:
    schedule.run_pending()
    time.sleep(3600)
```

### Metrics Trends

```python
# Анализ трендов
metrics_history = tracker.metrics

dates = [m.timestamp for m in metrics_history]
loc_values = [m.code_lines for m in metrics_history]
complexity_values = [m.average_complexity for m in metrics_history]

# Рост LOC
loc_growth_rate = (loc_values[-1] - loc_values[0]) / len(loc_values)
print(f"LOC growth rate: {loc_growth_rate:.1f} lines per snapshot")

# Complexity trend
if complexity_values[-1] > complexity_values[0]:
    print("⚠️  Complexity is increasing!")
else:
    print("✅ Complexity is stable or decreasing")
```

---

## 🐛 Technical Debt Detection

### Detecting Debt

```python
debt_items = tracker.detect_technical_debt()

# Group by severity
critical = [d for d in debt_items if d.severity == 'critical']
high = [d for d in debt_items if d.severity == 'high']
medium = [d for d in debt_items if d.severity == 'medium']
low = [d for d in debt_items if d.severity == 'low']

print(f"Critical: {len(critical)}")
print(f"High: {len(high)}")
print(f"Medium: {len(medium)}")
print(f"Low: {len(low)}")
```

### Prioritizing Debt

```python
# Sort by effort (quick wins first)
quick_wins = sorted(debt_items, key=lambda d: d.effort_minutes)[:5]

print("Quick wins (lowest effort):")
for debt in quick_wins:
    print(f"\n{debt.category} - {debt.severity}")
    print(f"  File: {debt.file_path}:{debt.line_number}")
    print(f"  Issue: {debt.description}")
    print(f"  Fix: {debt.suggestion}")
    print(f"  Effort: {debt.effort_minutes} minutes")
```

### Tracking Debt Over Time

```python
# Регулярное обнаружение
debt_counts = []

for _ in range(30):  # 30 дней
    current_debt = len(tracker.debt_items)
    debt_counts.append(current_debt)

    # New debt detection
    tracker.detect_technical_debt()

    time.sleep(86400)  # 1 день

# Анализ тренда
if debt_counts[-1] > debt_counts[0]:
    print("⚠️  Technical debt is increasing!")
else:
    print("✅ Technical debt is being addressed")
```

---

## 💚 Health Monitoring

### Health Score Components

```python
health = tracker.calculate_health_score()

print(f"Overall Health: {health.overall_score}/100")
print(f"\nComponent Scores:")
print(f"  Structure: {health.structure_score}/100")
print(f"  Code Quality: {health.code_quality_score}/100")
print(f"  Test Coverage: {health.test_coverage_score}/100")
print(f"  Documentation: {health.documentation_score}/100")
print(f"  Maintainability: {health.maintainability_score}/100")
```

### Health Alerts

```python
def check_health_alerts():
    health = tracker.calculate_health_score()

    if health.overall_score < 60:
        print("🚨 CRITICAL: Project health below 60!")
        send_alert(f"Project health: {health.overall_score}/100")

    if health.test_coverage_score < 50:
        print("⚠️  WARNING: Low test coverage")

    if health.code_quality_score < 50:
        print("⚠️  WARNING: Poor code quality")

    return health

# Check daily
schedule.every().day.at("09:00").do(check_health_alerts)
```

### Health Trends

```python
# Health over time
health_history = tracker.health_history

dates = [h.timestamp for h in health_history]
scores = [h.overall_score for h in health_history]

# Визуализация (требует matplotlib)
import matplotlib.pyplot as plt

plt.plot(dates, scores)
plt.xlabel('Date')
plt.ylabel('Health Score')
plt.title('Project Health Over Time')
plt.axhline(y=70, color='r', linestyle='--', label='Target')
plt.legend()
plt.show()
```

---

## 🔧 Refactoring Suggestions

### Getting Suggestions

```python
def get_refactoring_suggestions(tracker):
    """Generate refactoring suggestions"""
    suggestions = []

    # Technical debt items
    for debt in tracker.debt_items:
        if debt.severity in ['critical', 'high']:
            suggestions.append({
                'priority': 'high' if debt.severity == 'critical' else 'medium',
                'type': debt.category,
                'file': debt.file_path,
                'line': debt.line_number,
                'description': debt.description,
                'suggestion': debt.suggestion,
                'effort_minutes': debt.effort_minutes
            })

    # Metrics-based suggestions
    latest_metrics = tracker.metrics[-1]

    if latest_metrics.average_complexity > 10:
        suggestions.append({
            'priority': 'medium',
            'type': 'complexity',
            'description': 'High average complexity detected',
            'suggestion': 'Review complex functions and consider refactoring',
            'effort_minutes': 120
        })

    if latest_metrics.test_coverage and latest_metrics.test_coverage < 70:
        suggestions.append({
            'priority': 'high',
            'type': 'testing',
            'description': f'Test coverage is {latest_metrics.test_coverage}%',
            'suggestion': 'Add tests to reach 70% coverage',
            'effort_minutes': 180
        })

    # Sort by priority
    priority_order = {'high': 0, 'medium': 1, 'low': 2}
    suggestions.sort(key=lambda s: priority_order.get(s['priority'], 3))

    return suggestions

# Usage
suggestions = get_refactoring_suggestions(tracker)

print(f"Refactoring Suggestions ({len(suggestions)} items):\n")
for i, sug in enumerate(suggestions[:10], 1):
    print(f"{i}. [{sug['priority'].upper()}] {sug['type']}")
    print(f"   {sug['description']}")
    print(f"   → {sug['suggestion']}")
    print(f"   Effort: {sug['effort_minutes']} minutes\n")
```

---

## 📊 Analytics & Reporting

### Daily Report

```python
def generate_daily_report(tracker):
    """Generate daily project report"""

    # Latest data
    snapshot = tracker.snapshots[-1]
    metrics = tracker.metrics[-1]
    health = tracker.health_history[-1]

    report = f"""
📊 Daily Project Report - {datetime.now().strftime('%Y-%m-%d')}
{'='*70}

📦 Project Overview:
   Files: {snapshot.files_count}
   LOC: {metrics.code_lines:,}
   Functions: {metrics.functions_count}
   Classes: {metrics.classes_count}

💚 Health Score: {health.overall_score}/100
   Structure: {health.structure_score}/100
   Code Quality: {health.code_quality_score}/100
   Tests: {health.test_coverage_score}/100
   Docs: {health.documentation_score}/100

🐛 Technical Debt:
   Total: {len(tracker.debt_items)} items
   Critical: {len([d for d in tracker.debt_items if d.severity == 'critical'])}
   Estimated effort: {sum(d.effort_minutes for d in tracker.debt_items)/60:.1f} hours

⚠️  Issues:
"""

    for issue in health.issues:
        report += f"   - {issue}\n"

    report += "\n💡 Recommendations:\n"
    for rec in health.recommendations:
        report += f"   - {rec}\n"

    return report

# Generate and send
report = generate_daily_report(tracker)
print(report)

# Email или Slack notification
# send_email(report)
# send_slack_message(report)
```

### Weekly Summary

```python
def generate_weekly_summary(tracker):
    """Weekly summary with trends"""

    # Last 7 snapshots
    recent_snapshots = tracker.snapshots[-7:]
    recent_metrics = tracker.metrics[-7:]

    if len(recent_snapshots) < 2:
        return "Not enough data for weekly summary"

    first = recent_snapshots[0]
    last = recent_snapshots[-1]

    files_change = last.files_count - first.files_count
    loc_change = recent_metrics[-1].code_lines - recent_metrics[0].code_lines

    summary = f"""
📈 Weekly Summary
{'='*70}

Growth:
  Files: {first.files_count} → {last.files_count} ({files_change:+d})
  LOC: {recent_metrics[0].code_lines} → {recent_metrics[-1].code_lines} ({loc_change:+d})

Health Trend:
  Start: {tracker.health_history[-7].overall_score}/100
  End: {tracker.health_history[-1].overall_score}/100
  Change: {tracker.health_history[-1].overall_score - tracker.health_history[-7].overall_score:+.1f}

Top Issues:
"""

    # Top debt items by severity
    critical = [d for d in tracker.debt_items if d.severity == 'critical']
    for i, debt in enumerate(critical[:3], 1):
        summary += f"  {i}. {debt.description} ({debt.file_path})\n"

    return summary

print(generate_weekly_summary(tracker))
```

---

## 🔔 Automation & Integration

### CI/CD Integration

```yaml
# .github/workflows/health-check.yml
name: Project Health Check

on:
  push:
    branches: [ main, develop ]
  schedule:
    - cron: '0 0 * * *'  # Daily at midnight

jobs:
  health-check:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Install dependencies
      run: pip install -r requirements.txt

    - name: Run health check
      run: |
        python -c "
        from pathlib import Path
        from project_evolution_tracker import ProjectEvolutionTracker

        tracker = ProjectEvolutionTracker(Path('.'))
        tracker.take_snapshot()
        tracker.calculate_metrics()
        health = tracker.calculate_health_score()

        print(f'Health Score: {health.overall_score}/100')

        if health.overall_score < 60:
            print('❌ Health score below threshold!')
            exit(1)
        "

    - name: Upload report
      uses: actions/upload-artifact@v3
      with:
        name: health-report
        path: .ai_tracker/
```

### Pre-commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit

# Check project health before commit
python -c "
from pathlib import Path
from project_evolution_tracker import ProjectEvolutionTracker

tracker = ProjectEvolutionTracker(Path('.'))
health = tracker.calculate_health_score()

if health.overall_score < 50:
    print('❌ Cannot commit: Health score too low ({}/100)'.format(health.overall_score))
    exit(1)

print('✅ Health check passed ({}/100)'.format(health.overall_score))
"

exit $?
```

### Slack Notifications

```python
import requests

def send_health_alert_to_slack(tracker, webhook_url):
    """Send health alert to Slack"""

    health = tracker.health_history[-1]

    if health.overall_score < 60:
        message = {
            "text": f"🚨 Project Health Alert!",
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Project Health Score:* {health.overall_score}/100 🔴"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Issues:*\n" + "\n".join(f"• {issue}" for issue in health.issues)
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Recommendations:*\n" + "\n".join(f"• {rec}" for rec in health.recommendations)
                    }
                }
            ]
        }

        requests.post(webhook_url, json=message)

# Usage
send_health_alert_to_slack(tracker, "https://hooks.slack.com/services/...")
```

---

## 🎯 Best Practices

### Regular Tracking

```python
# Setup tracking schedule
import schedule

def daily_tracking():
    tracker.take_snapshot()
    tracker.calculate_metrics()
    tracker.detect_technical_debt()
    health = tracker.calculate_health_score()

    # Generate reports
    if health.overall_score < 70:
        send_alert(health)

# Run daily
schedule.every().day.at("00:00").do(daily_tracking)
```

### Set Health Goals

```python
HEALTH_GOALS = {
    'overall_score': 80,
    'structure_score': 85,
    'code_quality_score': 80,
    'test_coverage_score': 75,
    'documentation_score': 70,
    'maintainability_score': 80
}

def check_health_goals(health):
    """Check if health meets goals"""
    passed = True

    for metric, target in HEALTH_GOALS.items():
        actual = getattr(health, metric)
        if actual < target:
            print(f"❌ {metric}: {actual}/100 (target: {target})")
            passed = False
        else:
            print(f"✅ {metric}: {actual}/100")

    return passed
```

### Track Improvements

```python
def track_debt_resolution():
    """Track technical debt being resolved"""

    initial_debt = len(tracker.debt_items)

    # Work on project...
    # Fix some debt items...

    current_debt = len(tracker.debt_items)
    resolved = initial_debt - current_debt

    print(f"Resolved {resolved} debt items")
    print(f"Remaining: {current_debt}")

    if resolved > 0:
        print("✅ Making progress on technical debt!")
    else:
        print("⚠️  No debt resolved this period")
```

---

## 📚 Related Modules

- `multi_label_classifier.py` - AI classification
- `llm_content_generator.py` - Content generation
- `github_integration.py` - GitHub automation
- `template_marketplace.py` - Community templates

---

## 🗺️ Future Enhancements

### Planned Features

- [ ] AI-powered code review
- [ ] Automated refactoring (not just suggestions)
- [ ] Performance profiling integration
- [ ] Security vulnerability scanning
- [ ] Dependency updates tracking
- [ ] Team productivity metrics
- [ ] Custom health score formulas
- [ ] Integration with SonarQube, CodeClimate

---

**Ready for advanced project monitoring!** 🚀
