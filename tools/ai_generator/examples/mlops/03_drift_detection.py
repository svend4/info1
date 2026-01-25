#!/usr/bin/env python3
"""
Example: Model Drift Detection

This example demonstrates monitoring for data drift, concept drift,
and model performance degradation using PSI, KS tests, and more.
"""

from pathlib import Path
import numpy as np
from tools.ai_generator.mlops import (
    DriftDetector,
    DriftConfig,
    DriftType,
    DriftSeverity,
    DriftAlert
)


def example_psi_drift_detection():
    """Population Stability Index (PSI) for drift detection"""
    print("=" * 60)
    print("Example 1: PSI Drift Detection")
    print("=" * 60)

    detector = DriftDetector()

    # Training data distribution (baseline)
    training_data = np.random.normal(50, 10, 10000)

    # Production data with drift
    production_data = np.random.normal(55, 12, 1000)  # Mean shifted, more variance

    # Calculate PSI
    psi_result = detector.calculate_psi(
        baseline=training_data,
        current=production_data,
        bins=10
    )

    print(f"📊 PSI Analysis:")
    print(f"   PSI Score: {psi_result.psi_value:.4f}")
    print(f"   Interpretation: {psi_result.interpretation}")

    print(f"\n🚦 Drift Severity:")
    if psi_result.psi_value < 0.1:
        print(f"   ✅ No drift (PSI < 0.1)")
    elif psi_result.psi_value < 0.2:
        print(f"   ⚠️ Moderate drift (0.1 ≤ PSI < 0.2)")
    else:
        print(f"   🔴 Significant drift (PSI ≥ 0.2)")

    print(f"\n📈 Distribution comparison:")
    print(f"   Training mean: {np.mean(training_data):.2f}")
    print(f"   Production mean: {np.mean(production_data):.2f}")
    print(f"   Training std: {np.std(training_data):.2f}")
    print(f"   Production std: {np.std(production_data):.2f}")
    print()


def example_ks_test():
    """Kolmogorov-Smirnov test for distribution drift"""
    print("=" * 60)
    print("Example 2: KS Test for Distribution Drift")
    print("=" * 60)

    detector = DriftDetector()

    # Baseline distribution
    baseline = np.random.exponential(scale=2.0, size=5000)

    # Test different scenarios
    scenarios = [
        ("No drift", np.random.exponential(scale=2.0, size=1000)),
        ("Slight drift", np.random.exponential(scale=2.3, size=1000)),
        ("Significant drift", np.random.exponential(scale=3.5, size=1000)),
        ("Different distribution", np.random.normal(2.0, 1.0, 1000))
    ]

    print("📊 KS Test Results:\n")

    for scenario_name, current_data in scenarios:
        ks_result = detector.ks_test(
            baseline=baseline,
            current=current_data,
            alpha=0.05
        )

        symbol = "🔴" if ks_result.is_drift else "✅"
        print(f"   {symbol} {scenario_name}:")
        print(f"      KS statistic: {ks_result.ks_statistic:.4f}")
        print(f"      p-value: {ks_result.p_value:.4f}")
        print(f"      Drift detected: {'Yes' if ks_result.is_drift else 'No'}\n")
    print()


def example_feature_drift_monitoring():
    """Monitor drift across multiple features"""
    print("=" * 60)
    print("Example 3: Multi-Feature Drift Monitoring")
    print("=" * 60)

    detector = DriftDetector()

    # Simulate multi-feature dataset
    n_samples = 5000

    # Baseline (training data)
    baseline_features = {
        "age": np.random.normal(45, 15, n_samples),
        "income": np.random.lognormal(10.5, 0.8, n_samples),
        "credit_score": np.random.normal(680, 80, n_samples),
        "loan_amount": np.random.normal(250000, 100000, n_samples)
    }

    # Current data with drift in some features
    current_features = {
        "age": np.random.normal(45, 15, 1000),  # No drift
        "income": np.random.lognormal(10.8, 0.9, 1000),  # Drift
        "credit_score": np.random.normal(700, 75, 1000),  # Slight drift
        "loan_amount": np.random.normal(280000, 110000, 1000)  # Drift
    }

    print("📊 Feature-level Drift Analysis:\n")

    drift_summary = []
    for feature_name in baseline_features.keys():
        psi_result = detector.calculate_psi(
            baseline=baseline_features[feature_name],
            current=current_features[feature_name]
        )

        ks_result = detector.ks_test(
            baseline=baseline_features[feature_name],
            current=current_features[feature_name]
        )

        drift_summary.append({
            "feature": feature_name,
            "psi": psi_result.psi_value,
            "ks_pvalue": ks_result.p_value,
            "has_drift": psi_result.psi_value > 0.2
        })

        status = "🔴" if psi_result.psi_value > 0.2 else "⚠️" if psi_result.psi_value > 0.1 else "✅"
        print(f"   {status} {feature_name}:")
        print(f"      PSI: {psi_result.psi_value:.4f}")
        print(f"      KS p-value: {ks_result.p_value:.4f}\n")

    drifted_features = [f for f in drift_summary if f["has_drift"]]
    print(f"⚠️ Features with significant drift: {len(drifted_features)}/{len(baseline_features)}")

    if drifted_features:
        print(f"   Affected: {', '.join([f['feature'] for f in drifted_features])}")
    print()


def example_concept_drift():
    """Detect concept drift (relationship between features and target)"""
    print("=" * 60)
    print("Example 4: Concept Drift Detection")
    print("=" * 60)

    detector = DriftDetector()

    # Simulate model predictions over time
    weeks = 12
    baseline_accuracy = 0.92

    weekly_performance = []
    for week in range(weeks):
        # Simulate gradual concept drift
        drift_factor = 0.02 * (week / weeks)
        week_accuracy = baseline_accuracy - drift_factor + np.random.normal(0, 0.01)

        weekly_performance.append({
            "week": week + 1,
            "accuracy": week_accuracy
        })

    print("📊 Weekly Model Performance:\n")
    for perf in weekly_performance:
        week_num = perf["week"]
        acc = perf["accuracy"]

        # Visual indicator
        bars = "█" * int(acc * 50)
        symbol = "🔴" if acc < 0.88 else "⚠️" if acc < 0.90 else "✅"

        print(f"   Week {week_num:2d}: {symbol} {bars} {acc:.3f}")

    # Detect concept drift using performance degradation
    concept_drift = detector.detect_concept_drift(
        baseline_performance=baseline_accuracy,
        current_performances=[p["accuracy"] for p in weekly_performance[-4:]],
        threshold=0.03
    )

    print(f"\n🔍 Concept Drift Analysis:")
    print(f"   Baseline accuracy: {baseline_accuracy:.3f}")
    print(f"   Recent average: {np.mean([p['accuracy'] for p in weekly_performance[-4:]]):.3f}")
    print(f"   Degradation: {concept_drift.degradation:.3f}")
    print(f"   Drift detected: {'Yes 🔴' if concept_drift.is_drift else 'No ✅'}")

    if concept_drift.is_drift:
        print(f"\n   ⚠️ ACTION REQUIRED: Retrain model with recent data")
    print()


def example_prediction_drift():
    """Monitor drift in model predictions"""
    print("=" * 60)
    print("Example 5: Prediction Drift Monitoring")
    print("=" * 60)

    detector = DriftDetector()

    # Baseline prediction distribution (from validation set)
    baseline_predictions = np.random.beta(8, 2, 10000)  # Skewed towards 1

    # Production predictions showing drift
    production_predictions = np.random.beta(5, 5, 1000)  # More centered

    # Detect drift in predictions
    pred_drift = detector.detect_prediction_drift(
        baseline=baseline_predictions,
        current=production_predictions
    )

    print("📊 Prediction Drift Analysis:")
    print(f"\n   Baseline predictions:")
    print(f"      Mean: {np.mean(baseline_predictions):.3f}")
    print(f"      Std: {np.std(baseline_predictions):.3f}")
    print(f"      Median: {np.median(baseline_predictions):.3f}")

    print(f"\n   Production predictions:")
    print(f"      Mean: {np.mean(production_predictions):.3f}")
    print(f"      Std: {np.std(production_predictions):.3f}")
    print(f"      Median: {np.median(production_predictions):.3f}")

    print(f"\n   🔍 Drift metrics:")
    print(f"      PSI: {pred_drift.psi:.4f}")
    print(f"      KS statistic: {pred_drift.ks_stat:.4f}")
    print(f"      Drift severity: {pred_drift.severity.value}")

    if pred_drift.is_drift:
        print(f"\n   ⚠️ Prediction drift detected!")
        print(f"   Possible causes:")
        print(f"      - Input data distribution has changed")
        print(f"      - Model degradation over time")
        print(f"      - Population shift in users")
    print()


def example_target_drift():
    """Detect drift in target variable when labels are available"""
    print("=" * 60)
    print("Example 6: Target Variable Drift")
    print("=" * 60)

    detector = DriftDetector()

    # Historical target distribution (e.g., churn rate)
    historical_targets = np.random.binomial(1, 0.15, 10000)  # 15% positive class

    # Recent targets showing increased churn
    recent_targets = np.random.binomial(1, 0.22, 1000)  # 22% positive class

    target_drift = detector.detect_target_drift(
        baseline=historical_targets,
        current=recent_targets
    )

    print("📊 Target Variable Analysis:")
    print(f"\n   Historical data:")
    print(f"      Positive class: {np.mean(historical_targets):.2%}")
    print(f"      Negative class: {1 - np.mean(historical_targets):.2%}")

    print(f"\n   Recent data:")
    print(f"      Positive class: {np.mean(recent_targets):.2%}")
    print(f"      Negative class: {1 - np.mean(recent_targets):.2%}")

    print(f"\n   📈 Change:")
    print(f"      Absolute: {target_drift.absolute_change:+.2%}")
    print(f"      Relative: {target_drift.relative_change:+.2%}")
    print(f"      Drift detected: {'Yes 🔴' if target_drift.is_drift else 'No ✅'}")

    if target_drift.is_drift:
        print(f"\n   ⚠️ Target distribution has shifted significantly")
        print(f"   Recommended actions:")
        print(f"      1. Investigate root cause of shift")
        print(f"      2. Retrain model with recent data")
        print(f"      3. Adjust decision thresholds if needed")
    print()


def example_automated_monitoring():
    """Automated drift monitoring with alerts"""
    print("=" * 60)
    print("Example 7: Automated Drift Monitoring")
    print("=" * 60)

    config = DriftConfig(
        psi_threshold=0.2,
        ks_threshold=0.05,
        check_interval_hours=24,
        alert_on_drift=True,
        auto_retrain_on_drift=False
    )

    detector = DriftDetector(config=config)

    # Setup monitoring
    monitor = detector.setup_monitoring(
        features=["age", "income", "credit_score"],
        baseline_data_path="./data/training_data.parquet",
        production_data_source="kafka://ml-predictions"
    )

    print("✅ Automated monitoring configured")
    print(f"\n📋 Configuration:")
    print(f"   PSI threshold: {config.psi_threshold}")
    print(f"   KS significance: {config.ks_threshold}")
    print(f"   Check frequency: Every {config.check_interval_hours}h")
    print(f"   Alert enabled: {config.alert_on_drift}")

    # Simulate monitoring check
    print(f"\n🔍 Running drift check...")

    drift_report = detector.check_drift(
        features=monitor.features,
        time_window="24h"
    )

    print(f"\n📊 Drift Report:")
    print(f"   Features monitored: {len(drift_report.features)}")
    print(f"   Features with drift: {drift_report.drifted_count}")
    print(f"   Overall status: {drift_report.status.value}")

    if drift_report.drifted_count > 0:
        print(f"\n   ⚠️ Drifted features:")
        for feature in drift_report.drifted_features:
            print(f"      - {feature['name']}: PSI = {feature['psi']:.4f}")

        print(f"\n   📧 Alerts sent to: {config.alert_email}")
    print()


def example_drift_correction():
    """Strategies for handling detected drift"""
    print("=" * 60)
    print("Example 8: Drift Correction Strategies")
    print("=" * 60)

    detector = DriftDetector()

    print("🔧 Drift Correction Strategies:\n")

    strategies = [
        {
            "name": "Periodic Retraining",
            "description": "Retrain model on schedule (weekly/monthly)",
            "when_to_use": "Gradual drift patterns",
            "cost": "Medium",
            "effectiveness": "High"
        },
        {
            "name": "Trigger-based Retraining",
            "description": "Retrain when drift exceeds threshold",
            "when_to_use": "Sudden drift events",
            "cost": "Low",
            "effectiveness": "Very High"
        },
        {
            "name": "Online Learning",
            "description": "Continuously update model with new data",
            "when_to_use": "High-velocity data streams",
            "cost": "High",
            "effectiveness": "Very High"
        },
        {
            "name": "Ensemble Models",
            "description": "Combine recent and historical models",
            "when_to_use": "Uncertain drift patterns",
            "cost": "Medium",
            "effectiveness": "Medium"
        },
        {
            "name": "Feature Engineering",
            "description": "Add temporal features or adjust existing",
            "when_to_use": "Known seasonal patterns",
            "cost": "Medium",
            "effectiveness": "High"
        }
    ]

    for i, strategy in enumerate(strategies, 1):
        print(f"   {i}. {strategy['name']}")
        print(f"      Description: {strategy['description']}")
        print(f"      Best for: {strategy['when_to_use']}")
        print(f"      Cost: {strategy['cost']} | Effectiveness: {strategy['effectiveness']}\n")

    print("📋 Recommended approach:")
    print("   1. Set up automated drift monitoring")
    print("   2. Define drift thresholds based on business impact")
    print("   3. Implement trigger-based retraining")
    print("   4. Maintain model performance dashboards")
    print("   5. Document all drift incidents and resolutions")
    print()


def example_drift_dashboard():
    """Generate drift monitoring dashboard"""
    print("=" * 60)
    print("Example 9: Drift Monitoring Dashboard")
    print("=" * 60)

    detector = DriftDetector()

    # Generate dashboard
    dashboard = detector.create_dashboard(
        model_name="credit-risk-model",
        features=["age", "income", "credit_score", "debt_ratio"],
        time_range="30d",
        output_path="./output/drift_dashboard.html"
    )

    print("✅ Drift dashboard generated")
    print(f"📊 Dashboard sections:")
    print(f"   1. Feature-level PSI trends")
    print(f"   2. Distribution comparisons")
    print(f"   3. Prediction drift over time")
    print(f"   4. Model performance metrics")
    print(f"   5. Alert history")

    print(f"\n📈 Key visualizations:")
    print(f"   - PSI heatmap across features")
    print(f"   - Time series of drift metrics")
    print(f"   - Distribution overlay plots")
    print(f"   - Correlation drift matrix")

    print(f"\n📄 Output: {dashboard.file_path}")
    print(f"   Share with: ML Engineers, Data Scientists, Product Managers")
    print()


if __name__ == "__main__":
    print("\n📉 Drift Detection Examples")
    print("=" * 60)
    print()

    # Run all examples
    example_psi_drift_detection()
    example_ks_test()
    example_feature_drift_monitoring()
    example_concept_drift()
    example_prediction_drift()
    example_target_drift()
    example_automated_monitoring()
    example_drift_correction()
    example_drift_dashboard()

    print("=" * 60)
    print("✅ All drift detection examples completed!")
    print("=" * 60)
    print("\n📚 Drift Monitoring Best Practices:")
    print("   1. Monitor multiple drift types (data, concept, target)")
    print("   2. Set appropriate thresholds based on business impact")
    print("   3. Implement automated monitoring and alerting")
    print("   4. Track drift metrics alongside model performance")
    print("   5. Maintain baseline data from training")
    print("   6. Document drift incidents and corrective actions")
    print("   7. Retrain models proactively when drift detected")
    print("   8. Use multiple statistical tests for confirmation")
