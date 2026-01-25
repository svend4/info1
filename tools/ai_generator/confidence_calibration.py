#!/usr/bin/env python3
"""
Confidence Calibration для ML модели

Проблема: Текущая модель выдаёт низкие confidence scores (10-20%)
даже для правильных предсказаний.

Решение: Calibration методы для получения более realistic probabilities.

Методы:
1. Platt Scaling (Logistic Regression calibration)
2. Isotonic Regression
3. Temperature Scaling
"""

import numpy as np
from sklearn.calibration import CalibratedClassifierCV
from sklearn.isotonic import IsotonicRegression
from sklearn.linear_model import LogisticRegression
import pickle
from pathlib import Path
import json


class ConfidenceCalibrator:
    """
    Калибратор confidence scores для ML классификатора

    Использует Platt Scaling и Isotonic Regression для
    калибровки вероятностей.
    """

    def __init__(self, base_classifier=None):
        """
        Args:
            base_classifier: Базовый классификатор для калибровки
        """
        self.base_classifier = base_classifier
        self.calibrated_classifier = None
        self.calibration_method = None

    def calibrate_platt(self, X_train, y_train, X_val, y_val):
        """
        Platt Scaling (Logistic Regression calibration)

        Обучает дополнительную логистическую регрессию на
        выходах базового классификатора.

        Args:
            X_train: Training features
            y_train: Training labels
            X_val: Validation features
            y_val: Validation labels
        """
        print("🔧 Applying Platt Scaling...")

        # Создаём calibrated classifier с методом 'sigmoid' (Platt)
        self.calibrated_classifier = CalibratedClassifierCV(
            self.base_classifier,
            method='sigmoid',
            cv='prefit'  # Используем уже обученную модель
        )

        # Калибруем на validation set
        self.calibrated_classifier.fit(X_val, y_val)
        self.calibration_method = 'platt'

        print("✅ Platt Scaling applied")

    def calibrate_isotonic(self, X_train, y_train, X_val, y_val):
        """
        Isotonic Regression calibration

        Более гибкий метод, чем Platt Scaling, но требует
        больше данных.

        Args:
            X_train: Training features
            y_train: Training labels
            X_val: Validation features
            y_val: Validation labels
        """
        print("🔧 Applying Isotonic Regression...")

        self.calibrated_classifier = CalibratedClassifierCV(
            self.base_classifier,
            method='isotonic',
            cv='prefit'
        )

        self.calibrated_classifier.fit(X_val, y_val)
        self.calibration_method = 'isotonic'

        print("✅ Isotonic Regression applied")

    def predict_proba(self, X):
        """
        Предсказание калиброванных вероятностей

        Args:
            X: Features

        Returns:
            Calibrated probabilities
        """
        if self.calibrated_classifier is None:
            raise ValueError("Calibrator not trained. Call calibrate_platt or calibrate_isotonic first.")

        return self.calibrated_classifier.predict_proba(X)

    def predict(self, X):
        """Предсказание класса"""
        if self.calibrated_classifier is None:
            raise ValueError("Calibrator not trained.")

        return self.calibrated_classifier.predict(X)

    def save(self, path: str):
        """Сохранение calibrated модели"""
        with open(path, 'wb') as f:
            pickle.dump(self, f)
        print(f"💾 Saved calibrated model to {path}")

    @staticmethod
    def load(path: str):
        """Загрузка calibrated модели"""
        with open(path, 'rb') as f:
            return pickle.load(f)


class TemperatureScaling:
    """
    Temperature Scaling для калибровки

    Простой и эффективный метод, особенно для neural networks.
    Использует один параметр T (temperature) для scaling logits.
    """

    def __init__(self):
        self.temperature = 1.0

    def fit(self, logits, labels):
        """
        Обучение temperature parameter

        Args:
            logits: Raw model outputs (before softmax)
            labels: True labels
        """
        from scipy.optimize import minimize

        def nll_loss(T):
            """Negative log-likelihood loss"""
            scaled_logits = logits / T
            probs = self._softmax(scaled_logits)
            # Compute NLL
            nll = -np.mean(np.log(probs[np.arange(len(labels)), labels] + 1e-10))
            return nll

        # Optimize temperature
        result = minimize(nll_loss, x0=1.0, bounds=[(0.1, 10.0)])
        self.temperature = result.x[0]

        print(f"✅ Temperature optimized: T = {self.temperature:.2f}")

    def predict_proba(self, logits):
        """Калиброванные вероятности"""
        scaled_logits = logits / self.temperature
        return self._softmax(scaled_logits)

    def _softmax(self, x):
        """Softmax function"""
        exp_x = np.exp(x - np.max(x, axis=1, keepdims=True))
        return exp_x / np.sum(exp_x, axis=1, keepdims=True)


def evaluate_calibration(y_true, y_probs, n_bins=10):
    """
    Оценка качества калибровки

    Вычисляет Expected Calibration Error (ECE) и
    строит reliability diagram.

    Args:
        y_true: True labels
        y_probs: Predicted probabilities
        n_bins: Количество bins для гистограммы

    Returns:
        ECE (Expected Calibration Error)
    """
    # Получаем max probability для каждого примера
    confidences = np.max(y_probs, axis=1)
    predictions = np.argmax(y_probs, axis=1)
    accuracies = (predictions == y_true)

    # Создаём bins
    bins = np.linspace(0, 1, n_bins + 1)
    bin_indices = np.digitize(confidences, bins) - 1

    # Для каждого bin вычисляем accuracy и average confidence
    bin_accuracies = []
    bin_confidences = []
    bin_counts = []

    for i in range(n_bins):
        mask = bin_indices == i
        if np.sum(mask) > 0:
            bin_accuracies.append(np.mean(accuracies[mask]))
            bin_confidences.append(np.mean(confidences[mask]))
            bin_counts.append(np.sum(mask))
        else:
            bin_accuracies.append(0)
            bin_confidences.append(0)
            bin_counts.append(0)

    # Expected Calibration Error
    ece = 0
    total = len(y_true)
    for acc, conf, count in zip(bin_accuracies, bin_confidences, bin_counts):
        ece += (count / total) * abs(acc - conf)

    return {
        'ece': ece,
        'bin_accuracies': bin_accuracies,
        'bin_confidences': bin_confidences,
        'bin_counts': bin_counts
    }


def main():
    """Калибровка существующей ML модели"""
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent))

    from ml_classifier import MLClassifier
    import json

    print("="*70)
    print("CONFIDENCE CALIBRATION")
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

    # Загрузка датасета
    dataset_path = Path(__file__).parent / 'training_dataset_full.json'
    print(f"\n2. Loading dataset from {dataset_path.name}...")

    with open(dataset_path, 'r', encoding='utf-8') as f:
        dataset = json.load(f)

    print(f"   Dataset size: {len(dataset)}")

    # Подготовка данных
    descriptions = [item['description'] for item in dataset]
    labels = [item['primary_type'] for item in dataset]

    # Векторизация
    X = ml_classifier.vectorizer.transform(descriptions)
    y = np.array([ml_classifier.label_encoder[label] for label in labels])

    # Train/val split (80/20)
    from sklearn.model_selection import train_test_split
    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    print(f"\n3. Split: {len(y_train)} train, {len(y_val)} validation")

    # Получаем uncalibrated probabilities
    uncal_probs_train = ml_classifier.classifier.predict_proba(X_train)
    uncal_probs_val = ml_classifier.classifier.predict_proba(X_val)

    # Оценка uncalibrated модели
    print("\n4. Evaluating uncalibrated model...")
    uncal_metrics = evaluate_calibration(y_val, uncal_probs_val)
    print(f"   Uncalibrated ECE: {uncal_metrics['ece']:.4f}")

    # Калибровка методом Platt
    print("\n5. Calibrating with Platt Scaling...")
    calibrator_platt = ConfidenceCalibrator(ml_classifier.classifier)
    calibrator_platt.calibrate_platt(X_train, y_train, X_val, y_val)

    cal_probs_platt = calibrator_platt.predict_proba(X_val)
    platt_metrics = evaluate_calibration(y_val, cal_probs_platt)
    print(f"   Platt ECE: {platt_metrics['ece']:.4f}")

    # Калибровка методом Isotonic
    print("\n6. Calibrating with Isotonic Regression...")
    calibrator_iso = ConfidenceCalibrator(ml_classifier.classifier)
    calibrator_iso.calibrate_isotonic(X_train, y_train, X_val, y_val)

    cal_probs_iso = calibrator_iso.predict_proba(X_val)
    iso_metrics = evaluate_calibration(y_val, cal_probs_iso)
    print(f"   Isotonic ECE: {iso_metrics['ece']:.4f}")

    # Сравнение
    print("\n" + "="*70)
    print("CALIBRATION RESULTS")
    print("="*70)
    print(f"Uncalibrated ECE: {uncal_metrics['ece']:.4f}")
    print(f"Platt ECE:        {platt_metrics['ece']:.4f} {'✅ BEST' if platt_metrics['ece'] < min(uncal_metrics['ece'], iso_metrics['ece']) else ''}")
    print(f"Isotonic ECE:     {iso_metrics['ece']:.4f} {'✅ BEST' if iso_metrics['ece'] < min(uncal_metrics['ece'], platt_metrics['ece']) else ''}")

    # Определяем лучший метод
    if platt_metrics['ece'] < iso_metrics['ece']:
        print("\n🏆 Best method: Platt Scaling")
        best_calibrator = calibrator_platt
        best_method = 'platt'
    else:
        print("\n🏆 Best method: Isotonic Regression")
        best_calibrator = calibrator_iso
        best_method = 'isotonic'

    # Сохранение calibrated модели
    output_path = Path(__file__).parent / 'models' / f'project_classifier_calibrated_{best_method}.pkl'
    best_calibrator.save(str(output_path))

    print(f"\n✅ Calibration complete!")
    print(f"\nNext steps:")
    print(f"  1. Use calibrated model in production")
    print(f"  2. Update ml_classifier.py to use calibrated predictions")
    print(f"  3. Test with: python -c \"from confidence_calibration import ConfidenceCalibrator; c = ConfidenceCalibrator.load('{output_path}'); print('Loaded OK')\"")


if __name__ == '__main__':
    main()
