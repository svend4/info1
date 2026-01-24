#!/usr/bin/env python3
"""
Сравнение классификаторов (A/B тестирование)

Сравнивает rule-based, ML и hybrid подходы.
"""

import json
from pathlib import Path
from typing import Dict, List

# Импорт классификаторов
from classifier import ProjectClassifier
try:
    from ml_classifier import MLClassifier
    from hybrid_classifier import HybridClassifier
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False


def evaluate_classifier(classifier, test_data: List[Dict], classifier_name: str) -> Dict:
    """Оценка классификатора"""
    correct = 0
    total = len(test_data)
    results = []

    for item in test_data:
        description = item['description']
        expected_type = item['primary_type']

        # Разные интерфейсы для разных классификаторов
        if classifier_name == 'rule-based':
            spec = classifier.classify(description)
            predicted_type = spec.primary_type
            confidence = spec.confidence
        elif classifier_name == 'ml':
            predicted_type, confidence, _ = classifier.predict(description)
        elif classifier_name == 'hybrid':
            result = classifier.classify(description)
            predicted_type = result['primary_type']
            confidence = result['confidence']

        is_correct = predicted_type == expected_type
        if is_correct:
            correct += 1

        results.append({
            'description': description,
            'expected': expected_type,
            'predicted': predicted_type,
            'confidence': confidence,
            'correct': is_correct
        })

    accuracy = correct / total if total > 0 else 0

    return {
        'name': classifier_name,
        'accuracy': accuracy,
        'correct': correct,
        'total': total,
        'results': results
    }


def main():
    """Сравнение всех классификаторов"""
    print("="*70)
    print("CLASSIFIER COMPARISON (A/B TESTING)")
    print("="*70)

    # Загрузка тестовых данных
    test_data_path = Path(__file__).parent / 'training_dataset.json'
    if not test_data_path.exists():
        print(f"❌ Тестовый датасет не найден: {test_data_path}")
        return

    with open(test_data_path, 'r', encoding='utf-8') as f:
        test_data = json.load(f)

    print(f"\n📊 Тестовый датасет: {len(test_data)} примеров")

    # 1. Rule-based классификатор
    print("\n1️⃣  Rule-based классификатор...")
    rule_classifier = ProjectClassifier()
    rule_metrics = evaluate_classifier(rule_classifier, test_data, 'rule-based')

    # 2. ML классификатор (если доступен)
    ml_metrics = None
    if ML_AVAILABLE:
        model_path = Path(__file__).parent / 'models' / 'project_classifier.pkl'
        if model_path.exists():
            print("\n2️⃣  ML классификатор...")
            ml_classifier = MLClassifier()
            ml_classifier.load_model(str(model_path))
            ml_metrics = evaluate_classifier(ml_classifier, test_data, 'ml')
        else:
            print("\n2️⃣  ML классификатор: модель не найдена")
    else:
        print("\n2️⃣  ML классификатор: scikit-learn не установлен")

    # 3. Гибридный классификатор (если ML доступен)
    hybrid_metrics = None
    if ML_AVAILABLE and ml_metrics:
        print("\n3️⃣  Гибридный классификатор...")
        hybrid_classifier = HybridClassifier(
            ml_model_path='models/project_classifier.pkl'
        )
        hybrid_metrics = evaluate_classifier(hybrid_classifier, test_data, 'hybrid')
    else:
        print("\n3️⃣  Гибридный классификатор: пропущен (требует ML)")

    # Сравнение результатов
    print("\n" + "="*70)
    print("РЕЗУЛЬТАТЫ СРАВНЕНИЯ")
    print("="*70)

    print(f"\n{'Классификатор':<20} {'Accuracy':<12} {'Correct/Total':<15}")
    print("-"*70)

    # Rule-based
    print(f"{'Rule-based':<20} {rule_metrics['accuracy']:.1%}{' '*6} "
          f"{rule_metrics['correct']}/{rule_metrics['total']}")

    # ML
    if ml_metrics:
        print(f"{'ML (TF-IDF+LogReg)':<20} {ml_metrics['accuracy']:.1%}{' '*6} "
              f"{ml_metrics['correct']}/{ml_metrics['total']}")

    # Hybrid
    if hybrid_metrics:
        print(f"{'Hybrid':<20} {hybrid_metrics['accuracy']:.1%}{' '*6} "
              f"{hybrid_metrics['correct']}/{hybrid_metrics['total']}")

    # Лучший подход
    print("\n" + "="*70)
    all_metrics = [rule_metrics]
    if ml_metrics:
        all_metrics.append(ml_metrics)
    if hybrid_metrics:
        all_metrics.append(hybrid_metrics)

    best = max(all_metrics, key=lambda x: x['accuracy'])
    print(f"🏆 Лучший подход: {best['name'].upper()} ({best['accuracy']:.1%})")

    # Анализ ошибок
    print("\n" + "="*70)
    print("АНАЛИЗ ОШИБОК")
    print("="*70)

    # Найдем примеры, где все ошибаются
    if ml_metrics and hybrid_metrics:
        all_wrong = []
        for i, item in enumerate(test_data):
            if (not rule_metrics['results'][i]['correct'] and
                not ml_metrics['results'][i]['correct'] and
                not hybrid_metrics['results'][i]['correct']):
                all_wrong.append(item)

        if all_wrong:
            print(f"\n❌ Примеры, где все ошибаются ({len(all_wrong)}):")
            for item in all_wrong[:3]:
                print(f"  • {item['description'][:60]}...")
                print(f"    Ожидается: {item['primary_type']}")
        else:
            print("\n✅ Нет примеров, где все ошибаются")

    # Примеры, где hybrid лучше
    if hybrid_metrics and ml_metrics:
        hybrid_wins = []
        for i, item in enumerate(test_data):
            if (hybrid_metrics['results'][i]['correct'] and
                not rule_metrics['results'][i]['correct']):
                hybrid_wins.append(item)

        if hybrid_wins:
            print(f"\n🎯 Примеры, где hybrid лучше rule-based ({len(hybrid_wins)}):")
            for item in hybrid_wins[:3]:
                print(f"  • {item['description'][:60]}...")

    print("\n" + "="*70)


if __name__ == '__main__':
    main()
