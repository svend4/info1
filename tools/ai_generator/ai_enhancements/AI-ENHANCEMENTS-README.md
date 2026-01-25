# AI Enhancements Module

Комплексный набор AI-powered инструментов для анализа, оптимизации и улучшения кода.

## 📋 Содержание

- [GPT-4 Integration](#gpt-4-integration) - Интеграция с GPT-4 для генерации кода
- [Code Reviewer](#code-reviewer) - Автоматическое ревью кода
- [Test Generator](#test-generator) - Автоматическая генерация тестов
- [Performance Optimizer](#performance-optimizer) - Анализ и оптимизация производительности
- [Bug Predictor](#bug-predictor) - ML-powered предсказание багов
- [Refactoring Engine](#refactoring-engine) - Автоматический рефакторинг

## 🚀 Быстрый старт

```python
from ai_enhancements import (
    GPT4Integration,
    CodeReviewer,
    TestGenerator,
    PerformanceOptimizer,
    BugPredictor,
    RefactoringEngine
)

# Генерация кода с GPT-4
gpt4 = GPT4Integration()
code = gpt4.generate_code("Create a function to validate email addresses")

# Ревью кода
reviewer = CodeReviewer(strict_mode=True)
review_result = reviewer.review_file("mycode.py")
print(f"Quality score: {review_result.quality_score}/100")

# Генерация тестов
test_gen = TestGenerator(framework=TestFramework.PYTEST)
tests = test_gen.generate_for_file("mycode.py")
test_gen.save_tests(tests, "test_mycode.py")

# Оптимизация производительности
optimizer = PerformanceOptimizer()
report = optimizer.analyze_file("mycode.py")
print(f"Potential speedup: {report.potential_speedup}")

# Предсказание багов
predictor = BugPredictor()
bug_report = predictor.predict_file("mycode.py")
print(f"Found {bug_report.total_predictions} potential bugs")

# Рефакторинг
refactorer = RefactoringEngine(aggressive=False)
plan = refactorer.analyze_file("mycode.py")
print(refactorer.generate_refactoring_report(plan))
```

---

## GPT-4 Integration

Интеграция с GPT-4 API для AI-assisted генерации кода.

### Возможности

- ✅ Генерация кода по описанию
- ✅ Автоматическое ревью кода
- ✅ Генерация тестов
- ✅ Рефакторинг и оптимизация
- ✅ Анализ багов
- ✅ Генерация документации
- ✅ Кеширование результатов
- ✅ Расчет стоимости

### Использование

```python
from ai_enhancements import GPT4Integration, GenerationTask, GPT4Model, GPT4Request

# Инициализация
gpt4 = GPT4Integration(api_key="your-api-key")

# Быстрая генерация кода
from ai_enhancements import generate_code
code = generate_code(
    "Create a function to merge two sorted lists",
    model=GPT4Model.GPT4_TURBO
)

# Продвинутое использование
request = GPT4Request(
    task_type=GenerationTask.CODE_GENERATION,
    prompt="Create a REST API endpoint for user authentication",
    context={
        'framework': 'Flask',
        'database': 'PostgreSQL',
        'auth_method': 'JWT'
    },
    model=GPT4Model.GPT4_TURBO,
    temperature=0.7
)

response = gpt4.generate(request)
print(f"Generated code:\n{response.content}")
print(f"Cost: ${response.cost}")
print(f"Quality score: {response.quality_score}")

# Статистика использования
stats = gpt4.get_statistics()
print(f"Total requests: {stats['total_requests']}")
print(f"Total cost: ${stats['total_cost_usd']}")
print(f"Average quality: {stats['average_quality_score']}")
```

### Поддерживаемые модели

| Модель | Input ($/1K tokens) | Output ($/1K tokens) | Лучше для |
|--------|---------------------|----------------------|-----------|
| GPT-4 | $0.03 | $0.06 | Сложные задачи |
| GPT-4 Turbo | $0.01 | $0.03 | Быстрая генерация |
| GPT-4o | $0.005 | $0.015 | Оптимальная цена/качество |
| GPT-4o Mini | $0.00015 | $0.0006 | Простые задачи |

### Типы задач

- `CODE_GENERATION` - Генерация нового кода
- `CODE_REVIEW` - Ревью существующего кода
- `TEST_GENERATION` - Генерация тестов
- `REFACTORING` - Рефакторинг кода
- `BUG_ANALYSIS` - Анализ багов
- `OPTIMIZATION` - Оптимизация производительности
- `DOCUMENTATION` - Генерация документации

---

## Code Reviewer

Автоматический анализ кода с выявлением проблем безопасности, производительности и качества.

### Возможности

- 🔍 AST-based статический анализ
- 🔒 Проверка безопасности (SQL injection, XSS, etc.)
- ⚡ Анализ производительности
- 📊 Метрики качества кода
- 📝 Проверка документации
- 🎯 Кастомные правила

### Использование

```python
from ai_enhancements import CodeReviewer, IssueSeverity

# Инициализация
reviewer = CodeReviewer(strict_mode=True)

# Ревью одного файла
result = reviewer.review_file("app.py")

print(f"Quality Score: {result.quality_score}/100")
print(f"Total Issues: {result.total_issues}")

# Группировка по серьезности
for severity, count in result.issues_by_severity.items():
    print(f"{severity}: {count}")

# Детали проблем
for issue in result.issues:
    if issue.severity == IssueSeverity.HIGH:
        print(f"\n🔴 {issue.message}")
        print(f"   Line {issue.line_number}: {issue.code_snippet}")
        print(f"   💡 {issue.suggestion}")

# Ревью всего проекта
results = reviewer.review_project("./src", extensions=['.py'])

# Генерация отчета
report = reviewer.generate_report(results, output_format='markdown')
with open('code_review.md', 'w') as f:
    f.write(report)
```

### Категории проверок

- **Security** - SQL injection, command injection, hardcoded secrets
- **Performance** - Неэффективные алгоритмы, антипаттерны
- **Code Quality** - Длина строк, форматирование
- **Best Practices** - Bare except, глобальные переменные
- **Bug Risk** - Потенциальные баги
- **Maintainability** - Сложность функций, большие классы
- **Documentation** - Отсутствующие docstrings

### Добавление кастомных правил

```python
reviewer.add_custom_rule(
    pattern=r'print\(',
    severity='low',
    category='code_quality',
    message='Debug print() statement found',
    suggestion='Remove or replace with proper logging'
)
```

---

## Test Generator

Автоматическая генерация comprehensive test suites.

### Возможности

- ✅ Генерация unit тестов
- ✅ Edge case тесты
- ✅ Integration тесты
- ✅ Performance тесты
- ✅ Поддержка pytest, unittest, doctest
- ✅ Автоматическая генерация fixtures
- ✅ Mock объектов

### Использование

```python
from ai_enhancements import TestGenerator, TestFramework

# Инициализация
test_gen = TestGenerator(framework=TestFramework.PYTEST)

# Генерация тестов для файла
test_suite = test_gen.generate_for_file("calculator.py")

print(f"Generated {len(test_suite.test_cases)} test cases")
print(f"Estimated coverage: {test_suite.coverage_estimate}%")

# Сохранение тестов
test_gen.save_tests(test_suite, "test_calculator.py")

# Генерация для конкретного кода
code = """
def add(a: int, b: int) -> int:
    return a + b
"""

test_suite = test_gen.generate_for_code(code, "math_utils")
print(test_suite.to_code())
```

### Типы генерируемых тестов

**Unit Tests** - Базовая функциональность
```python
def test_add_happy_path():
    result = add(2, 3)
    assert result == 5
```

**Edge Cases** - Граничные условия
```python
def test_add_with_zero():
    result = add(0, 5)
    assert result == 5

def test_add_negative_numbers():
    result = add(-2, -3)
    assert result == -5
```

**Error Handling** - Обработка ошибок
```python
def test_add_invalid_type():
    with pytest.raises(TypeError):
        add("2", 3)
```

### Integration Tests

```python
# Генерация интеграционных тестов
integration_suite = test_gen.generate_integration_tests([
    'user_service',
    'database',
    'auth_manager'
])
```

---

## Performance Optimizer

Анализ и оптимизация производительности кода.

### Возможности

- 📈 Анализ алгоритмической сложности
- 🔄 Обнаружение неэффективных паттернов
- 💾 Оптимизация использования памяти
- 📊 Рекомендации по структурам данных
- ⚡ Векторизация и кеширование
- 📉 Оценка потенциального ускорения

### Использование

```python
from ai_enhancements import PerformanceOptimizer

# Инициализация
optimizer = PerformanceOptimizer()

# Анализ файла
report = optimizer.analyze_file("data_processor.py")

print(f"Total issues: {report.total_issues}")
print(f"Potential speedup: {report.potential_speedup}")

# Детали проблем
for issue in report.issues:
    print(f"\n{issue.description}")
    print(f"Current: {issue.current_complexity}")
    print(f"Optimized: {issue.optimized_complexity}")
    print(f"Expected speedup: {issue.expected_speedup}")
    print(f"\nOriginal:\n{issue.original_code}")
    print(f"\nOptimized:\n{issue.optimized_code}")

# Общие рекомендации
suggestions = optimizer.generate_optimization_suggestions(code)
for suggestion in suggestions:
    print(f"💡 {suggestion}")
```

### Типы оптимизаций

**Algorithm** - Улучшение алгоритмов
```python
# Before: O(n²)
for i in items:
    if i in other_list:  # Linear search
        process(i)

# After: O(n)
other_set = set(other_list)
for i in items:
    if i in other_set:  # O(1) lookup
        process(i)
```

**Data Structure** - Правильные структуры данных
```python
# Before: List for membership testing
if user_id in user_list:  # O(n)

# After: Set for membership testing
if user_id in user_set:  # O(1)
```

**Caching** - Кеширование результатов
```python
from functools import lru_cache

@lru_cache(maxsize=128)
def expensive_calculation(n):
    # Cached results
    return result
```

---

## Bug Predictor

ML-powered предсказание потенциальных багов.

### Возможности

- 🐛 Предсказание null pointer errors
- 🔢 Обнаружение division by zero
- 🔒 Выявление race conditions
- 💧 Обнаружение resource leaks
- 🔄 Поиск infinite loops
- 📊 Risk scoring

### Использование

```python
from ai_enhancements import BugPredictor, BugSeverity

# Инициализация
predictor = BugPredictor()

# Предсказание багов
bug_report = predictor.predict_file("app.py")

print(f"Total predictions: {bug_report.total_predictions}")
print(f"High confidence: {bug_report.high_confidence_count}")
print(f"Risk score: {bug_report.risk_score}/100")

# Фильтрация по confidence
high_confidence_bugs = [
    p for p in bug_report.predictions
    if p.confidence >= 0.7
]

# Детали предсказаний
for prediction in high_confidence_bugs:
    print(f"\n{prediction.bug_type.value.upper()}")
    print(f"Severity: {prediction.severity.value}")
    print(f"Confidence: {prediction.confidence:.0%}")
    print(f"Line {prediction.line_number}: {prediction.description}")
    print(f"💡 {prediction.fix_suggestion}")

# Рекомендации по исправлению
recommendations = predictor.generate_fix_recommendations(bug_report)
for severity, fixes in recommendations.items():
    if fixes:
        print(f"\n{severity.upper()} priority:")
        for fix in fixes:
            print(f"  - {fix}")
```

### Типы багов

- `NULL_POINTER` - AttributeError, NoneType errors
- `INDEX_ERROR` - List/dict index out of range
- `DIVISION_BY_ZERO` - ZeroDivisionError
- `RACE_CONDITION` - Многопоточные конфликты
- `RESOURCE_LEAK` - Незакрытые файлы/соединения
- `INFINITE_LOOP` - Бесконечные циклы
- `TYPE_ERROR` - Несовместимые типы

---

## Refactoring Engine

Автоматический рефакторинг кода с сохранением функциональности.

### Возможности

- 🔧 Extract Method
- 📝 Rename Variable
- 🔢 Replace Magic Numbers
- 🧹 Remove Duplicate Code
- 🎯 Simplify Conditionals
- 💀 Remove Dead Code

### Использование

```python
from ai_enhancements import RefactoringEngine

# Инициализация
refactorer = RefactoringEngine(aggressive=False)

# Создание плана рефакторинга
plan = refactorer.analyze_file("legacy_code.py")

print(f"Total operations: {plan.total_operations}")
print(f"Estimated improvement: {plan.estimated_improvement}")

# Генерация отчета
report = refactorer.generate_refactoring_report(plan)
print(report)

# Применение безопасных рефакторингов
with open("legacy_code.py") as f:
    original_code = f.read()

refactored_code = refactorer.apply_all_safe_refactorings(
    original_code,
    plan
)

# Сохранение результата
with open("refactored_code.py", "w") as f:
    f.write(refactored_code)
```

### Типы рефакторинга

**Extract Method** - Извлечение методов
```python
# Before: Long method
def process_order(order):
    # 50+ lines of code
    ...

# After: Extracted methods
def process_order(order):
    validate_order(order)
    calculate_total(order)
    apply_discounts(order)
    finalize_order(order)
```

**Replace Magic Numbers** - Замена magic numbers
```python
# Before
if user.age > 18:
    if account.balance > 1000:
        ...

# After
ADULT_AGE = 18
MINIMUM_BALANCE = 1000

if user.age > ADULT_AGE:
    if account.balance > MINIMUM_BALANCE:
        ...
```

**Simplify Conditionals** - Упрощение условий
```python
# Before
if user.is_active and user.is_verified and user.has_permission and not user.is_blocked:
    ...

# After
def can_access(user):
    return (user.is_active and
            user.is_verified and
            user.has_permission and
            not user.is_blocked)

if can_access(user):
    ...
```

---

## 🔗 Интеграция всех модулей

Комплексный workflow с использованием всех AI enhancements:

```python
from ai_enhancements import *

def complete_code_analysis(file_path: str):
    """Полный анализ кода со всеми AI инструментами"""

    # 1. Ревью кода
    print("🔍 Reviewing code...")
    reviewer = CodeReviewer(strict_mode=True)
    review = reviewer.review_file(file_path)
    print(f"✅ Quality Score: {review.quality_score}/100")

    # 2. Предсказание багов
    print("\n🐛 Predicting bugs...")
    predictor = BugPredictor()
    bugs = predictor.predict_file(file_path)
    print(f"⚠️  Found {bugs.high_confidence_count} high-confidence bugs")

    # 3. Анализ производительности
    print("\n⚡ Analyzing performance...")
    optimizer = PerformanceOptimizer()
    perf = optimizer.analyze_file(file_path)
    print(f"🚀 Potential speedup: {perf.potential_speedup}")

    # 4. План рефакторинга
    print("\n🔧 Creating refactoring plan...")
    refactorer = RefactoringEngine()
    plan = refactorer.analyze_file(file_path)
    print(f"📝 {plan.total_operations} refactoring operations suggested")

    # 5. Генерация тестов
    print("\n✅ Generating tests...")
    test_gen = TestGenerator()
    tests = test_gen.generate_for_file(file_path)
    test_gen.save_tests(tests, f"test_{Path(file_path).name}")
    print(f"📊 Generated {len(tests.test_cases)} test cases")

    # Сводный отчет
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"Code Quality: {review.quality_score}/100")
    print(f"Bug Risk: {bugs.risk_score}/100")
    print(f"Performance Issues: {perf.total_issues}")
    print(f"Refactoring Opportunities: {plan.total_operations}")
    print(f"Test Coverage Estimate: {tests.coverage_estimate}%")

    return {
        'review': review,
        'bugs': bugs,
        'performance': perf,
        'refactoring': plan,
        'tests': tests
    }

# Использование
results = complete_code_analysis("myapp.py")
```

---

## 📊 Метрики и статистика

Все модули предоставляют детальные метрики:

```python
# Code Review метрики
{
    'total_lines': 500,
    'code_lines': 350,
    'functions': 25,
    'classes': 5,
    'avg_line_length': 45.2
}

# Bug Prediction метрики
{
    'total_predictions': 15,
    'high_confidence_count': 5,
    'risk_score': 35.5,
    'bugs_by_type': {...},
    'bugs_by_severity': {...}
}

# Performance метрики
{
    'total_issues': 8,
    'potential_speedup': '5x-10x',
    'issues_by_type': {...},
    'critical_issues': 2
}
```

---

## ⚙️ Конфигурация

### Environment Variables

```bash
# GPT-4 API
export OPENAI_API_KEY="your-api-key"

# Кеширование
export AI_CACHE_DIR="./ai_cache"
export AI_CACHE_ENABLED="true"
```

### Программная конфигурация

```python
# Настройка GPT-4
gpt4 = GPT4Integration(
    api_key="...",
    storage_path="./cache",
    cache_enabled=True
)

# Настройка Code Reviewer
reviewer = CodeReviewer(
    strict_mode=True  # Более строгие проверки
)

# Настройка Refactoring Engine
refactorer = RefactoringEngine(
    aggressive=True  # Более агрессивный рефакторинг
)
```

---

## 🎯 Best Practices

1. **Code Review** - Запускайте перед каждым commit
2. **Bug Prediction** - Используйте в CI/CD pipeline
3. **Performance Optimization** - Регулярный аудит критичных участков
4. **Test Generation** - Автоматизируйте для нового кода
5. **Refactoring** - Применяйте постепенно, тестируйте после каждого шага

---

## 📈 Performance

Все модули оптимизированы для производительности:

- **Code Reviewer**: ~100ms на 1000 строк
- **Bug Predictor**: ~150ms на 1000 строк
- **Performance Optimizer**: ~200ms на 1000 строк
- **Test Generator**: ~500ms на функцию
- **Refactoring Engine**: ~300ms на анализ

---

## 🔐 Безопасность

- ✅ Все анализы выполняются локально (кроме GPT-4)
- ✅ GPT-4 запросы кешируются
- ✅ Никакой код не отправляется без явного разрешения
- ✅ Все трансформации сохраняют функциональность
- ✅ Поддержка review перед применением

---

## 📝 Примеры использования

См. `example_integration.py` для полного примера интеграции всех модулей.

---

## 🤝 Поддержка

Для вопросов и предложений создавайте issue в репозитории проекта.

**Version:** 1.0.0
**Python:** 3.8+
**License:** MIT
