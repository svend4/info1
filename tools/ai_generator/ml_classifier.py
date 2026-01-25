#!/usr/bin/env python3
"""
ML-классификатор проектов (Фаза 2 ЭТАПА 9)

Baseline: TF-IDF + Logistic Regression
Advanced: DistilBERT (TODO)
"""

import json
import pickle
from typing import List, Dict, Tuple
from pathlib import Path

# Попытка импорта ML библиотек (опционально)
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import classification_report, accuracy_score, f1_score
    import numpy as np
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    print("⚠️  scikit-learn не установлен. Используйте: pip install scikit-learn")


class MLClassifier:
    """
    ML-классификатор проектов

    Baseline: TF-IDF + Logistic Regression
    """

    def __init__(self):
        """Инициализация классификатора"""
        if not SKLEARN_AVAILABLE:
            raise ImportError("scikit-learn required for MLClassifier")

        self.vectorizer = TfidfVectorizer(
            max_features=500,
            ngram_range=(1, 2),  # unigrams + bigrams
            min_df=2,
            strip_accents='unicode'
        )
        self.classifier = LogisticRegression(
            max_iter=1000,
            random_state=42
        )
        self.label_encoder = {}
        self.label_decoder = {}
        self.is_trained = False

    def load_dataset(self, dataset_path: str) -> Tuple[List[str], List[str]]:
        """Загрузка датасета из JSON"""
        with open(dataset_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        descriptions = [item['description'] for item in data]
        labels = [item['primary_type'] for item in data]

        return descriptions, labels

    def train(self, dataset_path: str, test_size: float = 0.2):
        """
        Обучение классификатора

        Args:
            dataset_path: Путь к датасету (JSON)
            test_size: Размер тестовой выборки (0.2 = 20%)
        """
        print("📚 Загрузка датасета...")
        X, y = self.load_dataset(dataset_path)

        print(f"   Примеров: {len(X)}")

        # Кодирование меток
        unique_labels = sorted(set(y))
        self.label_encoder = {label: i for i, label in enumerate(unique_labels)}
        self.label_decoder = {i: label for label, i in self.label_encoder.items()}

        y_encoded = [self.label_encoder[label] for label in y]

        # Разделение на train/test
        print(f"📊 Разделение на train ({100-test_size*100:.0f}%) / test ({test_size*100:.0f}%)...")
        X_train, X_test, y_train, y_test = train_test_split(
            X, y_encoded, test_size=test_size, random_state=42, stratify=y_encoded
        )

        print(f"   Train: {len(X_train)} примеров")
        print(f"   Test: {len(X_test)} примеров")

        # Векторизация
        print("🔢 TF-IDF векторизация...")
        X_train_vec = self.vectorizer.fit_transform(X_train)
        X_test_vec = self.vectorizer.transform(X_test)

        # Обучение
        print("🤖 Обучение Logistic Regression...")
        self.classifier.fit(X_train_vec, y_train)

        # Оценка
        print("\n📈 Результаты на тестовой выборке:")
        y_pred = self.classifier.predict(X_test_vec)

        accuracy = accuracy_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred, average='weighted')

        print(f"   Accuracy: {accuracy:.1%}")
        print(f"   F1-score (weighted): {f1:.3f}")

        # Детальный отчёт
        print("\n📋 Classification Report:")
        target_names = [self.label_decoder[i] for i in sorted(self.label_decoder.keys())]
        print(classification_report(y_test, y_pred, target_names=target_names, zero_division=0))

        self.is_trained = True

        return accuracy, f1

    def predict(self, description: str) -> Tuple[str, float, Dict[str, float]]:
        """
        Предсказание типа проекта

        Args:
            description: Описание проекта

        Returns:
            (primary_type, confidence, all_scores)
        """
        if not self.is_trained:
            raise ValueError("Model not trained. Call train() first.")

        # Векторизация
        X_vec = self.vectorizer.transform([description])

        # Предсказание
        pred_proba = self.classifier.predict_proba(X_vec)[0]
        pred_label = self.classifier.predict(X_vec)[0]

        # Декодирование
        primary_type = self.label_decoder[pred_label]
        confidence = float(pred_proba[pred_label])

        # Все scores
        all_scores = {
            self.label_decoder[i]: float(prob)
            for i, prob in enumerate(pred_proba)
        }

        # Сортировка по убыванию
        all_scores = dict(sorted(all_scores.items(), key=lambda x: x[1], reverse=True))

        return primary_type, confidence, all_scores

    def save_model(self, model_path: str):
        """Сохранение обученной модели"""
        if not self.is_trained:
            raise ValueError("Model not trained yet")

        model_data = {
            'vectorizer': self.vectorizer,
            'classifier': self.classifier,
            'label_encoder': self.label_encoder,
            'label_decoder': self.label_decoder
        }

        with open(model_path, 'wb') as f:
            pickle.dump(model_data, f)

        print(f"✅ Модель сохранена: {model_path}")

    def load_model(self, model_path: str):
        """Загрузка обученной модели"""
        with open(model_path, 'rb') as f:
            model_data = pickle.load(f)

        self.vectorizer = model_data['vectorizer']
        self.classifier = model_data['classifier']
        self.label_encoder = model_data['label_encoder']
        self.label_decoder = model_data['label_decoder']
        self.is_trained = True

        print(f"✅ Модель загружена: {model_path}")


def main():
    """Обучение и тестирование ML-классификатора"""
    import argparse

    parser = argparse.ArgumentParser(description='ML-классификатор проектов')
    parser.add_argument('--train', action='store_true',
                       help='Обучить модель')
    parser.add_argument('--dataset', default='training_dataset_full.json',
                       help='Путь к датасету (default: training_dataset_full.json)')
    parser.add_argument('--test', nargs='+',
                       help='Тестовые описания для классификации')
    parser.add_argument('--model', default='models/project_classifier.pkl',
                       help='Путь к модели (default: models/project_classifier.pkl)')

    args = parser.parse_args()

    if not SKLEARN_AVAILABLE:
        print("❌ scikit-learn не установлен")
        print("   Установите: pip install scikit-learn")
        return

    classifier = MLClassifier()

    if args.train:
        # Обучение
        dataset_path = Path(__file__).parent / args.dataset
        if not dataset_path.exists():
            print(f"❌ Датасет не найден: {dataset_path}")
            return

        print("="*70)
        print("ML CLASSIFIER TRAINING")
        print("="*70)

        accuracy, f1 = classifier.train(str(dataset_path))

        # Сохранение модели
        model_path = Path(__file__).parent / args.model
        model_path.parent.mkdir(exist_ok=True)
        classifier.save_model(str(model_path))

        print("\n" + "="*70)
        print(f"✅ Обучение завершено!")
        print(f"   Accuracy: {accuracy:.1%}")
        print(f"   F1-score: {f1:.3f}")
        print("="*70)

    elif args.test:
        # Тестирование
        model_path = Path(__file__).parent / args.model
        if not model_path.exists():
            print(f"❌ Модель не найдена: {model_path}")
            print("   Сначала обучите модель: --train")
            return

        classifier.load_model(str(model_path))

        print("="*70)
        print("ML CLASSIFIER TESTING")
        print("="*70)

        for description in args.test:
            primary_type, confidence, all_scores = classifier.predict(description)

            print(f"\n📝 Описание: {description}")
            print(f"✓ Тип: {primary_type}")
            print(f"✓ Уверенность: {confidence:.1%}")

            print(f"\n📊 Топ-5 типов:")
            for i, (t, score) in enumerate(list(all_scores.items())[:5], 1):
                print(f"   {i}. {t}: {score:.1%}")

            print("-"*70)

    else:
        parser.print_help()


if __name__ == '__main__':
    main()
