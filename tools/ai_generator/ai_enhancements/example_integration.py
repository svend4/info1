#!/usr/bin/env python3
"""
AI Enhancements - Complete Integration Example

Демонстрация использования всех AI-powered модулей вместе.
"""

from pathlib import Path
from ai_enhancements import (
    GPT4Integration,
    CodeReviewer,
    TestGenerator,
    PerformanceOptimizer,
    BugPredictor,
    RefactoringEngine,
    GenerationTask,
    GPT4Model,
    GPT4Request,
    TestFramework
)


def step_1_gpt4_code_generation():
    """Шаг 1: Генерация кода с GPT-4"""
    print("=" * 70)
    print("STEP 1: GPT-4 CODE GENERATION")
    print("=" * 70)

    gpt4 = GPT4Integration()

    # Пример 1: Быстрая генерация
    print("\n📝 Generating simple function...")
    from ai_enhancements import generate_code

    code = generate_code(
        "Create a function to validate email addresses",
        model=GPT4Model.GPT4O_MINI
    )
    print("✅ Generated code preview:")
    print(code[:200] + "...")

    # Пример 2: Сложная генерация с контекстом
    print("\n📝 Generating API endpoint...")
    request = GPT4Request(
        task_type=GenerationTask.CODE_GENERATION,
        prompt="Create a RESTful API endpoint for user registration with validation",
        context={
            'framework': 'Flask',
            'database': 'SQLAlchemy',
            'auth': 'JWT'
        },
        model=GPT4Model.GPT4_TURBO
    )

    response = gpt4.generate(request)
    print(f"✅ Generated (cost: ${response.cost}, quality: {response.quality_score:.2f})")

    # Статистика
    stats = gpt4.get_statistics()
    print(f"\n📊 GPT-4 Statistics:")
    print(f"   Total requests: {stats['total_requests']}")
    print(f"   Total cost: ${stats['total_cost_usd']:.4f}")
    print(f"   Avg quality: {stats['average_quality_score']:.2f}")

    return code


def step_2_code_review(code: str):
    """Шаг 2: Автоматическое ревью кода"""
    print("\n" + "=" * 70)
    print("STEP 2: AUTOMATED CODE REVIEW")
    print("=" * 70)

    reviewer = CodeReviewer(strict_mode=True)

    # Ревью сгенерированного кода
    print("\n🔍 Reviewing generated code...")
    review_result = reviewer.review_code(code, "generated_code.py")

    print(f"\n✅ Review Complete:")
    print(f"   Quality Score: {review_result.quality_score}/100")
    print(f"   Total Issues: {review_result.total_issues}")

    # Группировка по серьезности
    print(f"\n📊 Issues by Severity:")
    for severity, count in review_result.issues_by_severity.items():
        print(f"   {severity}: {count}")

    # Показываем несколько проблем
    if review_result.issues:
        print(f"\n⚠️  Sample Issues:")
        for issue in review_result.issues[:3]:
            print(f"\n   Line {issue.line_number}: {issue.message}")
            print(f"   Category: {issue.category.value}")
            print(f"   💡 {issue.suggestion}")

    # Добавление кастомного правила
    print(f"\n🔧 Adding custom rule...")
    reviewer.add_custom_rule(
        pattern=r'TODO:',
        severity='low',
        category='code_quality',
        message='TODO comment found',
        suggestion='Complete TODO or create ticket'
    )

    return review_result


def step_3_bug_prediction(code: str):
    """Шаг 3: Предсказание потенциальных багов"""
    print("\n" + "=" * 70)
    print("STEP 3: BUG PREDICTION")
    print("=" * 70)

    predictor = BugPredictor()

    print("\n🐛 Analyzing for potential bugs...")
    bug_report = predictor.predict_bugs(code, "generated_code.py")

    print(f"\n✅ Analysis Complete:")
    print(f"   Total Predictions: {bug_report.total_predictions}")
    print(f"   High Confidence: {bug_report.high_confidence_count}")
    print(f"   Risk Score: {bug_report.risk_score:.1f}/100")

    # Метрики
    print(f"\n📊 Bugs by Type:")
    for bug_type, count in bug_report.metrics['bugs_by_type'].items():
        print(f"   {bug_type}: {count}")

    # Высокоуверенные предсказания
    high_conf = [p for p in bug_report.predictions if p.confidence >= 0.7]
    if high_conf:
        print(f"\n⚠️  High-Confidence Predictions:")
        for pred in high_conf[:3]:
            print(f"\n   {pred.bug_type.value.upper()}")
            print(f"   Confidence: {pred.confidence:.0%}")
            print(f"   Line {pred.line_number}: {pred.description}")
            print(f"   💡 {pred.fix_suggestion}")

    # Рекомендации
    recommendations = predictor.generate_fix_recommendations(bug_report)
    print(f"\n🔧 Fix Recommendations:")
    for severity, fixes in recommendations.items():
        if fixes:
            print(f"\n   {severity.upper()}:")
            for fix in fixes[:2]:
                print(f"   - {fix}")

    return bug_report


def step_4_performance_optimization(code: str):
    """Шаг 4: Анализ производительности"""
    print("\n" + "=" * 70)
    print("STEP 4: PERFORMANCE OPTIMIZATION")
    print("=" * 70)

    optimizer = PerformanceOptimizer()

    print("\n⚡ Analyzing performance...")
    report = optimizer.analyze_code(code, "generated_code.py")

    print(f"\n✅ Analysis Complete:")
    print(f"   Total Issues: {report.total_issues}")
    print(f"   Potential Speedup: {report.potential_speedup}")

    # Метрики
    print(f"\n📊 Metrics:")
    print(f"   Total Lines: {report.metrics['total_lines']}")
    print(f"   Code Lines: {report.metrics['code_lines']}")
    print(f"   Loops: {report.metrics['loop_count']}")

    # Проблемы производительности
    if report.issues:
        print(f"\n🔍 Performance Issues:")
        for issue in report.issues[:3]:
            print(f"\n   {issue.description}")
            print(f"   Current: {issue.current_complexity}")
            print(f"   Optimized: {issue.optimized_complexity}")
            print(f"   Expected Speedup: {issue.expected_speedup}")

    # Общие рекомендации
    suggestions = optimizer.generate_optimization_suggestions(code)
    if suggestions:
        print(f"\n💡 General Suggestions:")
        for suggestion in suggestions[:3]:
            print(f"   - {suggestion}")

    return report


def step_5_test_generation(code: str):
    """Шаг 5: Генерация тестов"""
    print("\n" + "=" * 70)
    print("STEP 5: AUTOMATED TEST GENERATION")
    print("=" * 70)

    test_gen = TestGenerator(framework=TestFramework.PYTEST)

    print("\n✅ Generating tests...")
    test_suite = test_gen.generate_for_code(code, "generated_module")

    print(f"\n✅ Generation Complete:")
    print(f"   Test Cases: {len(test_suite.test_cases)}")
    print(f"   Estimated Coverage: {test_suite.coverage_estimate}%")

    # Типы тестов
    test_types = {}
    for test in test_suite.test_cases:
        test_type = test.test_type.value
        test_types[test_type] = test_types.get(test_type, 0) + 1

    print(f"\n📊 Test Types:")
    for test_type, count in test_types.items():
        print(f"   {test_type}: {count}")

    # Примеры тестов
    print(f"\n🧪 Sample Test Cases:")
    for test in test_suite.test_cases[:2]:
        print(f"\n   {test.name}:")
        print(f"   Type: {test.test_type.value}")
        print(f"   Description: {test.description}")

    # Генерация performance теста
    print(f"\n⚡ Generating performance test...")
    perf_test = test_gen.generate_performance_tests(
        "process_data",
        "generated_module"
    )
    print(f"   ✅ Performance test: {perf_test.name}")

    return test_suite


def step_6_refactoring(code: str):
    """Шаг 6: Автоматический рефакторинг"""
    print("\n" + "=" * 70)
    print("STEP 6: AUTOMATED REFACTORING")
    print("=" * 70)

    refactorer = RefactoringEngine(aggressive=False)

    print("\n🔧 Creating refactoring plan...")
    plan = refactorer.create_refactoring_plan(code, "generated_code.py")

    print(f"\n✅ Plan Created:")
    print(f"   Total Operations: {plan.total_operations}")
    print(f"   Estimated Improvement: {plan.estimated_improvement}")

    # Риски
    print(f"\n⚠️  Risks:")
    for risk in plan.risks:
        print(f"   - {risk}")

    # Группировка операций по типу
    ops_by_type = {}
    for op in plan.operations:
        op_type = op.refactoring_type.value
        ops_by_type[op_type] = ops_by_type.get(op_type, 0) + 1

    print(f"\n📊 Operations by Type:")
    for op_type, count in ops_by_type.items():
        print(f"   {op_type}: {count}")

    # Примеры операций
    if plan.operations:
        print(f"\n🔍 Sample Operations:")
        for op in plan.operations[:3]:
            print(f"\n   {op.refactoring_type.value.upper()}")
            print(f"   Description: {op.description}")
            print(f"   Impact: {op.impact}")
            print(f"   Confidence: {op.confidence:.0%}")
            print(f"   Requires Review: {op.requires_review}")

    # Генерация полного отчета
    print(f"\n📄 Generating detailed report...")
    report = refactorer.generate_refactoring_report(plan)
    # Показываем первые 500 символов
    print(report[:500] + "...\n")

    return plan


def step_7_integration_workflow():
    """Шаг 7: Комплексный workflow"""
    print("\n" + "=" * 70)
    print("STEP 7: COMPLETE INTEGRATION WORKFLOW")
    print("=" * 70)

    sample_code = '''
def process_user_data(users):
    result = []
    for user in users:
        if user.age > 18:
            if user.is_active == True:
                if user.has_permission('read'):
                    temp = user.name + " " + str(user.age)
                    result.append(temp)
    return result

def calculate_total(items):
    total = 0
    for i in range(len(items)):
        total = total + items[i]['price'] * items[i]['quantity']
    return total
'''

    print("\n🔄 Running complete analysis pipeline...")

    # 1. Code Review
    print("\n1️⃣  Code Review...")
    reviewer = CodeReviewer()
    review = reviewer.review_code(sample_code)
    print(f"   Quality: {review.quality_score}/100")

    # 2. Bug Prediction
    print("\n2️⃣  Bug Prediction...")
    predictor = BugPredictor()
    bugs = predictor.predict_bugs(sample_code)
    print(f"   Risk: {bugs.risk_score:.1f}/100")

    # 3. Performance Analysis
    print("\n3️⃣  Performance Analysis...")
    optimizer = PerformanceOptimizer()
    perf = optimizer.analyze_code(sample_code)
    print(f"   Speedup: {perf.potential_speedup}")

    # 4. Refactoring
    print("\n4️⃣  Refactoring Plan...")
    refactorer = RefactoringEngine()
    plan = refactorer.create_refactoring_plan(sample_code)
    print(f"   Operations: {plan.total_operations}")

    # 5. Test Generation
    print("\n5️⃣  Test Generation...")
    test_gen = TestGenerator()
    tests = test_gen.generate_for_code(sample_code, "user_module")
    print(f"   Tests: {len(tests.test_cases)}")

    # Сводка
    print("\n" + "=" * 70)
    print("INTEGRATION SUMMARY")
    print("=" * 70)
    print(f"✅ Code Quality Score: {review.quality_score}/100")
    print(f"⚠️  Bug Risk Score: {bugs.risk_score:.1f}/100")
    print(f"🚀 Performance Improvement: {perf.potential_speedup}")
    print(f"🔧 Refactoring Operations: {plan.total_operations}")
    print(f"🧪 Generated Tests: {len(tests.test_cases)}")
    print(f"📊 Estimated Coverage: {tests.coverage_estimate}%")

    return {
        'review': review,
        'bugs': bugs,
        'performance': perf,
        'refactoring': plan,
        'tests': tests
    }


def main():
    """Основная демонстрация"""
    print("\n" + "=" * 70)
    print("AI ENHANCEMENTS - COMPLETE INTEGRATION EXAMPLE")
    print("=" * 70)
    print("\nDemonstrating all AI-powered code analysis and generation tools\n")

    try:
        # Шаг 1: Генерация кода
        generated_code = step_1_gpt4_code_generation()

        # Шаг 2: Ревью кода
        review_result = step_2_code_review(generated_code)

        # Шаг 3: Предсказание багов
        bug_report = step_3_bug_prediction(generated_code)

        # Шаг 4: Оптимизация производительности
        perf_report = step_4_performance_optimization(generated_code)

        # Шаг 5: Генерация тестов
        test_suite = step_5_test_generation(generated_code)

        # Шаг 6: Рефакторинг
        refactor_plan = step_6_refactoring(generated_code)

        # Шаг 7: Интеграция
        integration_results = step_7_integration_workflow()

        # Финальная сводка
        print("\n" + "=" * 70)
        print("✅ DEMONSTRATION COMPLETE")
        print("=" * 70)
        print("\nAll AI enhancement modules successfully demonstrated!")
        print("\nModules tested:")
        print("  ✅ GPT-4 Integration - Code generation with AI")
        print("  ✅ Code Reviewer - Automated code quality analysis")
        print("  ✅ Bug Predictor - ML-powered bug detection")
        print("  ✅ Performance Optimizer - Performance analysis & suggestions")
        print("  ✅ Test Generator - Automated test suite generation")
        print("  ✅ Refactoring Engine - Automated code refactoring")
        print("\n🎉 Integration successful! Ready for production use.")

    except Exception as e:
        print(f"\n❌ Error during demonstration: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
