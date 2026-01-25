#!/usr/bin/env python3
"""
Active Learning Framework

Автоматическое определение наиболее информативных примеров
для аннотации и добавления в training set.

Стратегии:
1. Uncertainty Sampling - примеры с наименьшей уверенностью
2. Query-by-Committee - примеры где модели не согласны
3. Expected Model Change - примеры которые больше всего изменят модель
"""

import numpy as np
from typing import List, Dict, Tuple
import json
from pathlib import Path


class ActiveLearner:
    """
    Active Learning для улучшения ML модели

    Находит наиболее информативные примеры для аннотации,
    которые помогут улучшить модель.
    """

    def __init__(self, classifier, vectorizer):
        """
        Args:
            classifier: Обученный классификатор
            vectorizer: Vectorizer для текста
        """
        self.classifier = classifier
        self.vectorizer = vectorizer
        self.labeled_pool = []
        self.unlabeled_pool = []

    def uncertainty_sampling(self, X, n_samples: int = 10) -> List[int]:
        """
        Uncertainty Sampling

        Выбирает примеры с наименьшей уверенностью модели.

        Strategies:
        - Least Confidence: 1 - max(P(y|x))
        - Margin: P(y1|x) - P(y2|x)  (разница между топ-2)
        - Entropy: -sum(P(y|x) * log(P(y|x)))

        Args:
            X: Feature matrix
            n_samples: Количество примеров для выбора

        Returns:
            Indices наиболее неопределённых примеров
        """
        probs = self.classifier.predict_proba(X)

        # Вычисляем uncertainty scores
        # Используем entropy как меру неопределённости
        entropy = -np.sum(probs * np.log(probs + 1e-10), axis=1)

        # Выбираем примеры с максимальной энтропией
        most_uncertain = np.argsort(entropy)[-n_samples:]

        return most_uncertain.tolist()

    def margin_sampling(self, X, n_samples: int = 10) -> List[int]:
        """
        Margin Sampling

        Выбирает примеры где разница между топ-2 предсказаниями
        наименьшая (модель не уверена между двумя классами).

        Args:
            X: Feature matrix
            n_samples: Количество примеров

        Returns:
            Indices примеров с наименьшим margin
        """
        probs = self.classifier.predict_proba(X)

        # Сортируем вероятности и берём топ-2
        sorted_probs = np.sort(probs, axis=1)

        # Margin = разница между топ-1 и топ-2
        margins = sorted_probs[:, -1] - sorted_probs[:, -2]

        # Выбираем примеры с наименьшим margin
        smallest_margins = np.argsort(margins)[:n_samples]

        return smallest_margins.tolist()

    def diverse_sampling(self, X, n_samples: int = 10) -> List[int]:
        """
        Diversity Sampling

        Выбирает разнообразные примеры для покрытия
        разных областей feature space.

        Args:
            X: Feature matrix
            n_samples: Количество примеров

        Returns:
            Indices разнообразных примеров
        """
        from sklearn.cluster import KMeans

        # Кластеризация
        kmeans = KMeans(n_clusters=n_samples, random_state=42)
        kmeans.fit(X)

        # Для каждого кластера находим ближайший пример к центроиду
        centers = kmeans.cluster_centers_
        selected = []

        for center in centers:
            # Находим ближайший пример к центру кластера
            distances = np.linalg.norm(X.toarray() - center, axis=1)
            closest = np.argmin(distances)
            selected.append(closest)

        return selected

    def query_by_committee(self, X, committee_models, n_samples: int = 10) -> List[int]:
        """
        Query by Committee

        Использует несколько моделей (committee) и выбирает
        примеры где модели не согласны.

        Args:
            X: Feature matrix
            committee_models: List моделей
            n_samples: Количество примеров

        Returns:
            Indices примеров с максимальным disagreement
        """
        # Получаем предсказания от всех моделей
        all_predictions = []
        for model in committee_models:
            preds = model.predict(X)
            all_predictions.append(preds)

        all_predictions = np.array(all_predictions)

        # Вычисляем vote entropy для каждого примера
        disagreement = []
        for i in range(X.shape[0]):
            votes = all_predictions[:, i]
            # Подсчитываем голоса
            unique, counts = np.unique(votes, return_counts=True)
            probs = counts / len(committee_models)
            # Entropy
            entropy = -np.sum(probs * np.log(probs + 1e-10))
            disagreement.append(entropy)

        disagreement = np.array(disagreement)

        # Выбираем примеры с максимальным disagreement
        most_disagreed = np.argsort(disagreement)[-n_samples:]

        return most_disagreed.tolist()

    def suggest_annotations(
        self,
        unlabeled_descriptions: List[str],
        strategy: str = 'uncertainty',
        n_samples: int = 20
    ) -> List[Dict]:
        """
        Предложение примеров для аннотации

        Args:
            unlabeled_descriptions: Список unlabeled описаний
            strategy: Стратегия ('uncertainty', 'margin', 'diverse')
            n_samples: Количество примеров

        Returns:
            List с предложениями для аннотации
        """
        # Векторизация
        X = self.vectorizer.transform(unlabeled_descriptions)

        # Выбор стратегии
        if strategy == 'uncertainty':
            selected_indices = self.uncertainty_sampling(X, n_samples)
        elif strategy == 'margin':
            selected_indices = self.margin_sampling(X, n_samples)
        elif strategy == 'diverse':
            selected_indices = self.diverse_sampling(X, n_samples)
        else:
            raise ValueError(f"Unknown strategy: {strategy}")

        # Получаем predictions для выбранных примеров
        suggestions = []
        for idx in selected_indices:
            description = unlabeled_descriptions[idx]
            X_sample = X[idx]

            # Предсказание
            probs = self.classifier.predict_proba(X_sample)[0]
            pred_label = self.classifier.predict(X_sample)[0]

            # Топ-3 предсказания
            top_3_indices = np.argsort(probs)[-3:][::-1]

            suggestions.append({
                'index': idx,
                'description': description,
                'predicted_type': pred_label,
                'confidence': float(probs[pred_label]),
                'top_3_predictions': [
                    {
                        'type': int(top_3_indices[i]),
                        'confidence': float(probs[top_3_indices[i]])
                    }
                    for i in range(len(top_3_indices))
                ],
                'strategy': strategy
            })

        return suggestions

    def save_suggestions(self, suggestions: List[Dict], output_path: str):
        """Сохранение предложений для аннотации"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(suggestions, f, ensure_ascii=False, indent=2)

        print(f"💾 Saved {len(suggestions)} suggestions to {output_path}")


class FeedbackCollector:
    """
    Сборщик feedback от пользователей

    Собирает правильные аннотации и добавляет в training set.
    """

    def __init__(self, dataset_path: str):
        self.dataset_path = Path(dataset_path)
        self.dataset = self._load_dataset()

    def _load_dataset(self) -> List[Dict]:
        """Загрузка датасета"""
        if self.dataset_path.exists():
            with open(self.dataset_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []

    def add_annotation(
        self,
        description: str,
        correct_type: str,
        secondary_types: List[str] = None,
        features: Dict = None
    ):
        """
        Добавление новой аннотации

        Args:
            description: Описание проекта
            correct_type: Правильный тип
            secondary_types: Вторичные типы
            features: Дополнительные features
        """
        new_id = f"user_{len(self.dataset) + 1:04d}"

        annotation = {
            'id': new_id,
            'description': description,
            'primary_type': correct_type,
            'secondary_types': secondary_types or [],
            'features': features or {},
            'source': 'user_feedback'
        }

        self.dataset.append(annotation)
        print(f"✅ Added annotation: {new_id} ({correct_type})")

    def save(self):
        """Сохранение обновлённого датасета"""
        with open(self.dataset_path, 'w', encoding='utf-8') as f:
            json.dump(self.dataset, f, ensure_ascii=False, indent=2)

        print(f"💾 Saved {len(self.dataset)} annotations to {self.dataset_path}")


def main():
    """Active Learning workflow"""
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent))

    from ml_classifier import MLClassifier

    print("="*70)
    print("ACTIVE LEARNING - ANNOTATION SUGGESTIONS")
    print("="*70)

    # Загрузка модели
    model_path = Path(__file__).parent / 'models' / 'project_classifier.pkl'
    if not model_path.exists():
        print("❌ ML model not found. Train it first:")
        print("   python ml_classifier.py --train")
        return

    print("\n1. Loading ML model...")
    ml_classifier = MLClassifier()
    ml_classifier.load_model(str(model_path))

    # Создаём active learner
    learner = ActiveLearner(ml_classifier.classifier, ml_classifier.vectorizer)

    # Примеры unlabeled данных (можно собрать из production logs)
    unlabeled_examples = [
        "Создать систему учёта для производства мебели",
        "Разработка криптовалютного трейдинг-бота на Python",
        "Онлайн-платформа для бронирования переговорных комнат",
        "Мобильное приложение для медитации и mindfulness",
        "AI-система для анализа рентгеновских снимков",
        "Блокчейн-решение для supply chain tracking",
        "VR тренажёр для обучения хирургов",
        "Система управления складом с RFID",
        "Платформа для краудфандинга социальных проектов",
        "IoT решение для умного сельского хозяйства",
        "Telegram бот для управления личными финансами",
        "Сервис для онлайн-репетиторства по математике",
        "Marketplace для аренды спортивного оборудования",
        "Система мониторинга энергопотребления предприятия",
        "Приложение для планирования свадеб",
        "Платформа для обмена навыками и знаниями",
        "Сервис доставки здорового питания с персонализацией",
        "CRM система для автосервиса",
        "Приложение для отслеживания углеродного следа",
        "Платформа для виртуальных экскурсий по музеям",
    ]

    print(f"\n2. Unlabeled pool: {len(unlabeled_examples)} examples")

    # Получаем suggestions с разными стратегиями
    strategies = ['uncertainty', 'margin', 'diverse']

    all_suggestions = {}
    for strategy in strategies:
        print(f"\n3. Running {strategy} sampling...")
        suggestions = learner.suggest_annotations(
            unlabeled_examples,
            strategy=strategy,
            n_samples=5
        )

        all_suggestions[strategy] = suggestions

        print(f"\n   Top 3 suggestions ({strategy}):")
        for i, sug in enumerate(suggestions[:3], 1):
            # Декодируем predicted type
            pred_type_idx = sug['predicted_type']
            pred_type = ml_classifier.label_decoder.get(pred_type_idx, f'unknown_{pred_type_idx}')

            print(f"   {i}. {sug['description'][:60]}...")
            print(f"      Predicted: {pred_type} ({sug['confidence']:.2%})")

    # Сохранение suggestions
    output_path = Path(__file__).parent / 'active_learning_suggestions.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        # Преобразуем для сохранения
        save_data = {
            strategy: [
                {
                    **sug,
                    'predicted_type_name': ml_classifier.label_decoder.get(
                        sug['predicted_type'],
                        f'unknown_{sug["predicted_type"]}'
                    )
                }
                for sug in suggestions
            ]
            for strategy, suggestions in all_suggestions.items()
        }
        json.dump(save_data, f, ensure_ascii=False, indent=2)

    print(f"\n💾 Saved suggestions to {output_path}")

    print("\n" + "="*70)
    print("NEXT STEPS")
    print("="*70)
    print("1. Review suggestions in: active_learning_suggestions.json")
    print("2. Annotate most informative examples")
    print("3. Add to training dataset:")
    print("   python active_learning.py --add-feedback")
    print("4. Retrain model with expanded dataset")
    print("5. Repeat cycle!")


if __name__ == '__main__':
    main()
