#!/usr/bin/env python3
"""
Example: A/B Testing for ML Models

This example demonstrates statistical A/B testing for model comparison
with z-tests, t-tests, chi-square, and Bayesian optimization.
"""

from pathlib import Path
import numpy as np
from tools.ai_generator.mlops import (
    ABTestFramework,
    ABTestConfig,
    StatisticalTest,
    ABTestResult,
    BayesianOptimizer
)


def example_basic_ab_test():
    """Basic A/B test between two models"""
    print("=" * 60)
    print("Example 1: Basic A/B Test")
    print("=" * 60)

    framework = ABTestFramework()

    # Simulate model performance data
    model_a_metrics = np.random.normal(0.85, 0.05, 1000)  # Control: 85% accuracy
    model_b_metrics = np.random.normal(0.88, 0.05, 1000)  # Treatment: 88% accuracy

    # Run A/B test
    result = framework.run_ab_test(
        control=model_a_metrics,
        treatment=model_b_metrics,
        metric_name="accuracy",
        test_type=StatisticalTest.Z_TEST,
        alpha=0.05
    )

    print(f"📊 A/B Test Results:")
    print(f"   Control (Model A): {result.control_mean:.4f} ± {result.control_std:.4f}")
    print(f"   Treatment (Model B): {result.treatment_mean:.4f} ± {result.treatment_std:.4f}")
    print(f"   Difference: {result.absolute_difference:.4f} ({result.relative_difference:.2%})")

    print(f"\n📈 Statistical Significance:")
    print(f"   p-value: {result.p_value:.6f}")
    print(f"   Statistically significant: {'Yes ✅' if result.is_significant else 'No ❌'}")
    print(f"   Confidence level: {(1 - result.alpha) * 100:.0f}%")

    if result.is_significant:
        print(f"\n🎯 Recommendation: Deploy Model B (Treatment)")
        print(f"   Expected improvement: {result.relative_difference:.2%}")
    else:
        print(f"\n⚠️ Recommendation: Insufficient evidence to switch models")
    print()


def example_multi_metric_test():
    """A/B test with multiple metrics"""
    print("=" * 60)
    print("Example 2: Multi-Metric A/B Test")
    print("=" * 60)

    framework = ABTestFramework()

    # Multiple metrics to evaluate
    metrics = {
        "accuracy": (np.random.normal(0.85, 0.03, 1000), np.random.normal(0.87, 0.03, 1000)),
        "precision": (np.random.normal(0.82, 0.04, 1000), np.random.normal(0.86, 0.04, 1000)),
        "recall": (np.random.normal(0.79, 0.05, 1000), np.random.normal(0.84, 0.05, 1000)),
        "f1_score": (np.random.normal(0.80, 0.04, 1000), np.random.normal(0.85, 0.04, 1000)),
    }

    print("📊 Multi-Metric Comparison:\n")

    results = {}
    for metric_name, (control, treatment) in metrics.items():
        result = framework.run_ab_test(
            control=control,
            treatment=treatment,
            metric_name=metric_name,
            test_type=StatisticalTest.T_TEST
        )
        results[metric_name] = result

        symbol = "✅" if result.is_significant else "❌"
        print(f"   {metric_name.upper()}: {symbol}")
        print(f"      Control: {result.control_mean:.4f}")
        print(f"      Treatment: {result.treatment_mean:.4f}")
        print(f"      Improvement: {result.relative_difference:+.2%}")
        print(f"      p-value: {result.p_value:.4f}\n")

    # Overall recommendation
    significant_count = sum(1 for r in results.values() if r.is_significant)
    print(f"🎯 Overall Results:")
    print(f"   Significant improvements: {significant_count}/{len(results)}")

    if significant_count >= len(results) * 0.75:
        print(f"   ✅ Strong evidence to deploy new model")
    elif significant_count >= len(results) * 0.5:
        print(f"   ⚠️ Mixed results - consider additional testing")
    else:
        print(f"   ❌ Insufficient evidence - keep current model")
    print()


def example_sequential_testing():
    """Sequential A/B testing with early stopping"""
    print("=" * 60)
    print("Example 3: Sequential Testing")
    print("=" * 60)

    framework = ABTestFramework()

    config = ABTestConfig(
        min_sample_size=100,
        max_sample_size=10000,
        alpha=0.05,
        power=0.80,
        mde=0.02,  # Minimum detectable effect: 2%
        enable_sequential=True
    )

    print("🔄 Running sequential test with early stopping...")
    print(f"   Min samples: {config.min_sample_size}")
    print(f"   Max samples: {config.max_sample_size}")
    print(f"   MDE: {config.mde:.2%}\n")

    # Simulate sequential data collection
    checkpoints = [100, 500, 1000, 2000, 5000]

    for n in checkpoints:
        control = np.random.normal(0.80, 0.05, n)
        treatment = np.random.normal(0.83, 0.05, n)  # 3% improvement

        result = framework.run_ab_test(
            control=control,
            treatment=treatment,
            metric_name="conversion_rate",
            test_type=StatisticalTest.Z_TEST,
            config=config
        )

        print(f"   Checkpoint at n={n}:")
        print(f"      Difference: {result.relative_difference:+.2%}")
        print(f"      p-value: {result.p_value:.4f}")

        if result.is_significant and n >= config.min_sample_size:
            print(f"      🎯 EARLY STOP: Significant result detected!")
            print(f"      Samples saved: {config.max_sample_size - n}")
            break
        elif n < config.max_sample_size:
            print(f"      ⏸️ Continue collecting data...\n")
        else:
            print(f"      ⚠️ Max samples reached\n")
    print()


def example_chi_square_test():
    """Chi-square test for categorical outcomes"""
    print("=" * 60)
    print("Example 4: Chi-Square Test (Categorical)")
    print("=" * 60)

    framework = ABTestFramework()

    # Simulate classification results
    # Control model predictions
    control_predictions = {
        "class_A": 450,
        "class_B": 320,
        "class_C": 230
    }

    # Treatment model predictions
    treatment_predictions = {
        "class_A": 520,
        "class_B": 280,
        "class_C": 200
    }

    result = framework.chi_square_test(
        control=control_predictions,
        treatment=treatment_predictions
    )

    print("📊 Chi-Square Test Results:")
    print("\n   Control Model:")
    for class_name, count in control_predictions.items():
        pct = count / sum(control_predictions.values()) * 100
        print(f"      {class_name}: {count} ({pct:.1f}%)")

    print("\n   Treatment Model:")
    for class_name, count in treatment_predictions.items():
        pct = count / sum(treatment_predictions.values()) * 100
        print(f"      {class_name}: {count} ({pct:.1f}%)")

    print(f"\n📈 Statistics:")
    print(f"   Chi-square statistic: {result.chi_square_stat:.2f}")
    print(f"   p-value: {result.p_value:.4f}")
    print(f"   Degrees of freedom: {result.degrees_of_freedom}")
    print(f"   Significant difference: {'Yes ✅' if result.is_significant else 'No ❌'}")
    print()


def example_bayesian_ab_test():
    """Bayesian A/B testing"""
    print("=" * 60)
    print("Example 5: Bayesian A/B Test")
    print("=" * 60)

    framework = ABTestFramework()

    # Simulate conversion data
    control_conversions = 850
    control_total = 10000
    treatment_conversions = 920
    treatment_total = 10000

    result = framework.bayesian_ab_test(
        control_successes=control_conversions,
        control_trials=control_total,
        treatment_successes=treatment_conversions,
        treatment_trials=treatment_total,
        prior_alpha=1,
        prior_beta=1
    )

    print("📊 Bayesian A/B Test Results:")
    print(f"\n   Control:")
    print(f"      Conversions: {control_conversions}/{control_total}")
    print(f"      Rate: {control_conversions/control_total:.4f}")

    print(f"\n   Treatment:")
    print(f"      Conversions: {treatment_conversions}/{treatment_total}")
    print(f"      Rate: {treatment_conversions/treatment_total:.4f}")

    print(f"\n📈 Bayesian Analysis:")
    print(f"   P(Treatment > Control): {result.prob_treatment_better:.2%}")
    print(f"   Expected lift: {result.expected_lift:.2%}")
    print(f"   95% Credible Interval: [{result.ci_lower:.4f}, {result.ci_upper:.4f}]")

    if result.prob_treatment_better > 0.95:
        print(f"\n✅ Strong evidence for treatment (> 95% probability)")
    elif result.prob_treatment_better > 0.90:
        print(f"\n⚠️ Moderate evidence for treatment (> 90% probability)")
    else:
        print(f"\n❌ Insufficient evidence to switch")
    print()


def example_multi_armed_bandit():
    """Multi-armed bandit for adaptive testing"""
    print("=" * 60)
    print("Example 6: Multi-Armed Bandit")
    print("=" * 60)

    framework = ABTestFramework()

    # Simulate 4 models with different performance
    models = {
        "model_v1": {"true_ctr": 0.08},
        "model_v2": {"true_ctr": 0.10},
        "model_v3": {"true_ctr": 0.09},
        "model_v4": {"true_ctr": 0.11},  # Best model
    }

    print("🎰 Multi-Armed Bandit Simulation")
    print(f"   Models: {len(models)}")
    print(f"   Strategy: Thompson Sampling\n")

    bandit = framework.create_bandit(
        arms=list(models.keys()),
        strategy="thompson_sampling",
        n_iterations=1000
    )

    # Run bandit
    results = bandit.run()

    print("📊 Results after 1000 iterations:")
    for model_name in models.keys():
        pulls = results['pulls'][model_name]
        rewards = results['rewards'][model_name]
        avg_reward = rewards / pulls if pulls > 0 else 0

        print(f"\n   {model_name}:")
        print(f"      Pulls: {pulls}")
        print(f"      Avg reward: {avg_reward:.4f}")
        print(f"      True CTR: {models[model_name]['true_ctr']:.4f}")

    best_model = max(results['pulls'].items(), key=lambda x: x[1])[0]
    print(f"\n🏆 Most selected model: {best_model}")
    print(f"   (Bandit automatically identified the best performer)")
    print()


def example_power_analysis():
    """Statistical power analysis"""
    print("=" * 60)
    print("Example 7: Power Analysis")
    print("=" * 60)

    framework = ABTestFramework()

    # Calculate required sample size
    power_results = framework.calculate_sample_size(
        baseline_rate=0.10,  # 10% baseline conversion
        mde=0.02,  # Want to detect 2% improvement (20% relative)
        alpha=0.05,
        power=0.80
    )

    print("📊 Power Analysis:")
    print(f"   Baseline rate: {power_results['baseline_rate']:.2%}")
    print(f"   Minimum detectable effect: {power_results['mde']:.2%}")
    print(f"   Significance level (α): {power_results['alpha']:.2%}")
    print(f"   Statistical power (1-β): {power_results['power']:.0%}")

    print(f"\n📈 Required Sample Size:")
    print(f"   Per variant: {power_results['sample_size_per_variant']:,}")
    print(f"   Total: {power_results['total_sample_size']:,}")

    print(f"\n⏱️ Duration estimates:")
    daily_traffic = 10000
    days_needed = power_results['total_sample_size'] / daily_traffic
    print(f"   At 10k daily traffic: {days_needed:.1f} days")

    # Sensitivity analysis
    print(f"\n🔍 Sensitivity Analysis:")
    for mde in [0.01, 0.02, 0.03, 0.05]:
        result = framework.calculate_sample_size(
            baseline_rate=0.10,
            mde=mde,
            alpha=0.05,
            power=0.80
        )
        print(f"   MDE {mde:.2%}: {result['sample_size_per_variant']:,} samples/variant")
    print()


def example_winner_selection():
    """Automated winner selection with guardrails"""
    print("=" * 60)
    print("Example 8: Automated Winner Selection")
    print("=" * 60)

    framework = ABTestFramework()

    # Simulate A/B test results
    models = {
        "current_model": {
            "accuracy": 0.85,
            "latency_ms": 45,
            "throughput": 1000,
            "cost_per_prediction": 0.001
        },
        "new_model": {
            "accuracy": 0.88,
            "latency_ms": 52,  # Slightly slower
            "throughput": 950,
            "cost_per_prediction": 0.0012  # Slightly more expensive
        }
    }

    # Define guardrails
    guardrails = {
        "max_latency_ms": 60,
        "min_throughput": 900,
        "max_cost_per_prediction": 0.0015,
        "min_accuracy_improvement": 0.02
    }

    winner = framework.select_winner(
        models=models,
        primary_metric="accuracy",
        guardrails=guardrails,
        weights={
            "accuracy": 0.5,
            "latency": 0.25,
            "cost": 0.25
        }
    )

    print("🏆 Winner Selection:")
    print(f"\n   Current Model:")
    for metric, value in models["current_model"].items():
        print(f"      {metric}: {value}")

    print(f"\n   New Model:")
    for metric, value in models["new_model"].items():
        print(f"      {metric}: {value}")

    print(f"\n⚖️ Guardrails Check:")
    for check, status in winner['guardrails_status'].items():
        symbol = "✅" if status else "❌"
        print(f"      {check}: {symbol}")

    print(f"\n🎯 Decision: {winner['selected_model']}")
    print(f"   Reason: {winner['reason']}")
    print(f"   Composite score: {winner['composite_score']:.4f}")
    print()


if __name__ == "__main__":
    print("\n🧪 A/B Testing Examples")
    print("=" * 60)
    print()

    # Run all examples
    example_basic_ab_test()
    example_multi_metric_test()
    example_sequential_testing()
    example_chi_square_test()
    example_bayesian_ab_test()
    example_multi_armed_bandit()
    example_power_analysis()
    example_winner_selection()

    print("=" * 60)
    print("✅ All A/B testing examples completed!")
    print("=" * 60)
    print("\n📚 A/B Testing Best Practices:")
    print("   1. Define success metrics before starting")
    print("   2. Calculate required sample size (power analysis)")
    print("   3. Run tests for sufficient duration (account for weekly patterns)")
    print("   4. Use multiple metrics, not just primary")
    print("   5. Implement guardrails for business constraints")
    print("   6. Consider sequential testing for faster results")
    print("   7. Document all test parameters and results")
    print("   8. Validate AA tests before running AB tests")
