#!/usr/bin/env python3
"""
Гибридный классификатор (Фаза 2 ЭТАПА 9)

Комбинирует rule-based и ML подходы для лучшей точности.
"""

import json
from typing import Dict, List, Tuple
from pathlib import Path

# Импорт наших классификаторов
from nlp_parser import NLPParser
from classifier import ProjectClassifier

# Опциональный импорт ML
try:
    from ml_classifier import MLClassifier
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False


class HybridClassifier:
    """
    Гибридный классификатор проектов

    Стратегия:
    1. Запускает оба классификатора (rule-based + ML)
    2. Комбинирует результаты с взвешиванием
    3. Использует ML для уточнения в неоднозначных случаях
    """

    def __init__(self, ml_model_path: str = None):
        """
        Инициализация гибридного классификатора

        Args:
            ml_model_path: Путь к обученной ML модели (опционально)
        """
        # Rule-based классификатор (всегда доступен)
        self.rule_classifier = ProjectClassifier()

        # ML классификатор (опционально)
        self.ml_classifier = None
        if ML_AVAILABLE and ml_model_path:
            try:
                self.ml_classifier = MLClassifier()
                model_path = Path(__file__).parent / ml_model_path
                if model_path.exists():
                    self.ml_classifier.load_model(str(model_path))
                    print(f"✅ ML модель загружена: {ml_model_path}")
            except Exception as e:
                print(f"⚠️  Не удалось загрузить ML модель: {e}")
                self.ml_classifier = None

        # Веса для комбинирования (можно настраивать)
        self.rule_weight = 0.6  # 60% rule-based
        self.ml_weight = 0.4    # 40% ML

    def classify(self, description: str) -> Dict:
        """
        Классификация проекта с использованием гибридного подхода

        Args:
            description: Описание проекта

        Returns:
            Dict с результатами классификации
        """
        # 1. Rule-based классификация
        rule_spec = self.rule_classifier.classify(description)

        result = {
            'description': description,
            'primary_type': rule_spec.primary_type,
            'secondary_types': rule_spec.secondary_types,
            'confidence': rule_spec.confidence,
            'project_name': rule_spec.name,  # ProjectSpec.name
            'method': 'rule-based',  # По умолчанию
            'rule_based_result': {
                'type': rule_spec.primary_type,
                'confidence': rule_spec.confidence
            }
        }

        # 2. ML классификация (если доступна)
        if self.ml_classifier:
            try:
                ml_type, ml_confidence, ml_scores = self.ml_classifier.predict(description)

                result['ml_result'] = {
                    'type': ml_type,
                    'confidence': ml_confidence,
                    'all_scores': ml_scores
                }

                # 3. Комбинирование результатов
                combined_type, combined_confidence = self._combine_results(
                    rule_spec.primary_type, rule_spec.confidence,
                    ml_type, ml_confidence,
                    ml_scores
                )

                result['primary_type'] = combined_type
                result['confidence'] = combined_confidence
                result['method'] = 'hybrid'

                # Добавляем вторичные типы из ML scores
                result['secondary_types'] = self._extract_secondary_types(
                    ml_scores, combined_type
                )

            except Exception as e:
                print(f"⚠️  ML классификация не удалась: {e}")

        return result

    def _combine_results(
        self,
        rule_type: str,
        rule_conf: float,
        ml_type: str,
        ml_conf: float,
        ml_scores: Dict[str, float]
    ) -> Tuple[str, float]:
        """
        Комбинирование результатов rule-based и ML

        Стратегии:
        1. Если оба согласны - высокая уверенность
        2. Если не согласны - взвешенное голосование
        3. Учитываем уверенность каждого метода
        """
        # Стратегия 1: Согласие
        if rule_type == ml_type:
            # Оба метода согласны - повышаем уверенность
            combined_confidence = min(
                (rule_conf * self.rule_weight + ml_conf * self.ml_weight) * 1.2,
                1.0
            )
            return rule_type, combined_confidence

        # Стратегия 2: Разногласие - взвешенное голосование
        # Создаем объединенные scores
        combined_scores = {}

        # Добавляем rule-based score
        combined_scores[rule_type] = rule_conf * self.rule_weight

        # Добавляем ML scores
        for proj_type, score in ml_scores.items():
            if proj_type in combined_scores:
                combined_scores[proj_type] += score * self.ml_weight
            else:
                combined_scores[proj_type] = score * self.ml_weight

        # Выбираем тип с максимальным score
        best_type = max(combined_scores.items(), key=lambda x: x[1])

        return best_type[0], best_type[1]

    def _extract_secondary_types(
        self,
        ml_scores: Dict[str, float],
        primary_type: str,
        threshold: float = 0.15
    ) -> List[str]:
        """
        Извлечение вторичных типов из ML scores

        Args:
            ml_scores: Scores от ML модели
            primary_type: Основной тип (исключаем из вторичных)
            threshold: Минимальный score для вторичного типа
        """
        secondary = []

        for proj_type, score in ml_scores.items():
            if proj_type != primary_type and score >= threshold:
                secondary.append(proj_type)

        # Возвращаем топ-2 вторичных типа
        return secondary[:2]

    def evaluate(self, test_dataset_path: str) -> Dict:
        """
        Оценка качества гибридного классификатора

        Args:
            test_dataset_path: Путь к тестовому датасету

        Returns:
            Dict с метриками качества
        """
        # Загрузка тестового датасета
        with open(test_dataset_path, 'r', encoding='utf-8') as f:
            test_data = json.load(f)

        correct = 0
        total = len(test_data)

        results = []

        for item in test_data:
            description = item['description']
            expected_type = item['primary_type']

            result = self.classify(description)
            predicted_type = result['primary_type']

            is_correct = predicted_type == expected_type
            if is_correct:
                correct += 1

            results.append({
                'description': description,
                'expected': expected_type,
                'predicted': predicted_type,
                'confidence': result['confidence'],
                'method': result['method'],
                'correct': is_correct
            })

        accuracy = correct / total if total > 0 else 0

        return {
            'accuracy': accuracy,
            'correct': correct,
            'total': total,
            'results': results
        }


def main():
    """Тестирование гибридного классификатора"""
    import argparse

    parser = argparse.ArgumentParser(description='Гибридный классификатор')
    parser.add_argument('--test', nargs='+',
                       help='Тестовые описания')
    parser.add_argument('--evaluate',
                       help='Путь к тестовому датасету для оценки')
    parser.add_argument('--ml-model', default='models/project_classifier.pkl',
                       help='Путь к ML модели')

    args = parser.parse_args()

    # Инициализация
    classifier = HybridClassifier(ml_model_path=args.ml_model)

    if args.test:
        # Тестирование на примерах
        print("="*70)
        print("HYBRID CLASSIFIER TESTING")
        print("="*70)

        for description in args.test:
            result = classifier.classify(description)

            print(f"\n📝 Описание: {description}")
            print(f"✓ Тип: {result['primary_type']}")
            print(f"✓ Уверенность: {result['confidence']:.1%}")
            print(f"✓ Метод: {result['method']}")

            if result.get('secondary_types'):
                print(f"✓ Вторичные типы: {', '.join(result['secondary_types'])}")

            if result['method'] == 'hybrid':
                print(f"\n📊 Детали:")
                print(f"  Rule-based: {result['rule_based_result']['type']} "
                      f"({result['rule_based_result']['confidence']:.1%})")
                print(f"  ML: {result['ml_result']['type']} "
                      f"({result['ml_result']['confidence']:.1%})")

            print("-"*70)

    elif args.evaluate:
        # Оценка на датасете
        dataset_path = Path(__file__).parent / args.evaluate
        if not dataset_path.exists():
            print(f"❌ Датасет не найден: {dataset_path}")
            return

        print("="*70)
        print("HYBRID CLASSIFIER EVALUATION")
        print("="*70)

        metrics = classifier.evaluate(str(dataset_path))

        print(f"\n📊 Результаты:")
        print(f"   Accuracy: {metrics['accuracy']:.1%}")
        print(f"   Correct: {metrics['correct']}/{metrics['total']}")

        # Показываем ошибки
        errors = [r for r in metrics['results'] if not r['correct']]
        if errors:
            print(f"\n❌ Ошибки классификации ({len(errors)}):")
            for err in errors[:5]:  # Показываем первые 5
                print(f"  • {err['description'][:50]}...")
                print(f"    Expected: {err['expected']}, Got: {err['predicted']}")

        print("="*70)

    else:
        parser.print_help()


if __name__ == '__main__':
    main()
