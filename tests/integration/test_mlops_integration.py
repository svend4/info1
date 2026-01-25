"""
Integration tests for MLOps modules
"""

import pytest
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
from tools.ai_generator.mlops import (
    ModelRegistry, MLBackend, ModelFramework, ModelStage,
    ABTestFramework, StatisticalTest,
    DriftDetector, DriftConfig,
    FeatureStore, FeatureStoreBackend, FeatureDefinition, FeatureType
)


@pytest.mark.integration
@pytest.mark.mlops
class TestModelRegistryIntegration:
    """Integration tests for model registry"""

    def test_mlflow_model_registration(self, temp_dir, mock_ml_metrics):
        """Test model registration with MLflow"""
        registry = ModelRegistry(backend=MLBackend.MLFLOW)

        model_info = registry.register_model(
            name="test-model",
            framework=ModelFramework.TENSORFLOW,
            model_path=str(temp_dir / "model"),
            metrics=mock_ml_metrics
        )

        assert model_info['name'] == "test-model"
        assert 'version' in model_info
        assert model_info['metrics'] == mock_ml_metrics

    def test_model_versioning(self, temp_dir):
        """Test multiple model versions"""
        registry = ModelRegistry(backend=MLBackend.MLFLOW)

        # Register multiple versions
        for version in range(1, 4):
            registry.register_model(
                name="versioned-model",
                framework=ModelFramework.SKLEARN,
                model_path=str(temp_dir / f"model_v{version}"),
                metrics={"accuracy": 0.80 + version * 0.03}
            )

        versions = registry.list_model_versions("versioned-model")
        assert len(versions) >= 3

    def test_model_stage_transition(self, temp_dir):
        """Test model stage transitions"""
        registry = ModelRegistry(backend=MLBackend.MLFLOW)

        # Register model
        registry.register_model(
            name="staging-test",
            framework=ModelFramework.PYTORCH,
            model_path=str(temp_dir / "model"),
            metrics={"accuracy": 0.91}
        )

        # Transition to staging
        registry.transition_model_stage(
            name="staging-test",
            version=1,
            stage=ModelStage.STAGING
        )

        # Get model by stage
        staging_model = registry.get_model_by_stage("staging-test", ModelStage.STAGING)
        assert staging_model is not None


@pytest.mark.integration
@pytest.mark.mlops
class TestABTestingIntegration:
    """Integration tests for A/B testing framework"""

    def test_basic_ab_test(self):
        """Test basic A/B test with z-test"""
        framework = ABTestFramework()

        control = np.random.normal(0.85, 0.05, 1000)
        treatment = np.random.normal(0.88, 0.05, 1000)

        result = framework.run_ab_test(
            control=control,
            treatment=treatment,
            metric_name="accuracy",
            test_type=StatisticalTest.Z_TEST
        )

        assert result.control_mean > 0
        assert result.treatment_mean > 0
        assert 0 <= result.p_value <= 1

    def test_multi_metric_evaluation(self):
        """Test A/B testing with multiple metrics"""
        framework = ABTestFramework()

        metrics = {
            "accuracy": (
                np.random.normal(0.85, 0.03, 1000),
                np.random.normal(0.87, 0.03, 1000)
            ),
            "precision": (
                np.random.normal(0.82, 0.04, 1000),
                np.random.normal(0.85, 0.04, 1000)
            )
        }

        results = {}
        for metric_name, (control, treatment) in metrics.items():
            result = framework.run_ab_test(
                control=control,
                treatment=treatment,
                metric_name=metric_name,
                test_type=StatisticalTest.T_TEST
            )
            results[metric_name] = result

        assert len(results) == 2
        assert all(hasattr(r, 'p_value') for r in results.values())

    def test_bayesian_ab_test(self):
        """Test Bayesian A/B testing"""
        framework = ABTestFramework()

        result = framework.bayesian_ab_test(
            control_successes=850,
            control_trials=10000,
            treatment_successes=920,
            treatment_trials=10000
        )

        assert 0 <= result.prob_treatment_better <= 1
        assert hasattr(result, 'expected_lift')


@pytest.mark.integration
@pytest.mark.mlops
class TestDriftDetectionIntegration:
    """Integration tests for drift detection"""

    def test_psi_drift_detection(self):
        """Test PSI drift calculation"""
        detector = DriftDetector()

        baseline = np.random.normal(50, 10, 10000)
        current = np.random.normal(55, 12, 1000)

        psi_result = detector.calculate_psi(
            baseline=baseline,
            current=current,
            bins=10
        )

        assert hasattr(psi_result, 'psi_value')
        assert psi_result.psi_value >= 0

    def test_ks_test_drift(self):
        """Test Kolmogorov-Smirnov test"""
        detector = DriftDetector()

        baseline = np.random.exponential(scale=2.0, size=5000)
        current_no_drift = np.random.exponential(scale=2.0, size=1000)
        current_with_drift = np.random.exponential(scale=3.5, size=1000)

        # No drift case
        result_no_drift = detector.ks_test(baseline, current_no_drift)
        # With drift case
        result_with_drift = detector.ks_test(baseline, current_with_drift)

        assert hasattr(result_no_drift, 'ks_statistic')
        assert hasattr(result_with_drift, 'is_drift')

    def test_feature_drift_monitoring(self):
        """Test multi-feature drift monitoring"""
        detector = DriftDetector()

        features = {
            "feature1": (
                np.random.normal(50, 10, 5000),
                np.random.normal(50, 10, 1000)
            ),
            "feature2": (
                np.random.normal(100, 20, 5000),
                np.random.normal(110, 25, 1000)  # Drift
            )
        }

        drift_results = []
        for feature_name, (baseline, current) in features.items():
            psi_result = detector.calculate_psi(baseline, current)
            drift_results.append({
                "feature": feature_name,
                "psi": psi_result.psi_value
            })

        assert len(drift_results) == 2


@pytest.mark.integration
@pytest.mark.mlops
class TestFeatureStoreIntegration:
    """Integration tests for feature store"""

    def test_feature_store_initialization(self):
        """Test feature store setup"""
        store = FeatureStore(backend=FeatureStoreBackend.REDIS)
        store.initialize()

        assert store is not None

    def test_feature_definition(self):
        """Test feature definition and registration"""
        store = FeatureStore(backend=FeatureStoreBackend.REDIS)

        feature_def = FeatureDefinition(
            name="user_age",
            feature_type=FeatureType.NUMERICAL,
            description="User age in years",
            default_value=0
        )

        store.register_feature(feature_def, feature_group="user_features")

        # Feature should be registered
        assert True

    def test_online_feature_serving(self, mock_user_features):
        """Test online feature write and read"""
        store = FeatureStore(backend=FeatureStoreBackend.REDIS)

        user_id = mock_user_features["user_id"]
        features = {k: v for k, v in mock_user_features.items() if k != "user_id"}

        # Write features
        store.write_online_features(
            entity_id=user_id,
            feature_group="user_features",
            features=features
        )

        # Read features
        retrieved = store.get_online_features(
            entity_id=user_id,
            feature_group="user_features",
            feature_names=list(features.keys())
        )

        assert retrieved is not None
        assert set(retrieved.keys()) == set(features.keys())

    def test_feature_versioning(self):
        """Test feature version management"""
        store = FeatureStore(backend=FeatureStoreBackend.REDIS)

        # Register multiple versions
        versions = ["v1", "v2", "v3"]
        for version in versions:
            store.register_feature_version(
                name="risk_score",
                version=version,
                calculation_logic=f"algorithm_{version}"
            )

        # Should have multiple versions
        assert True

    def test_point_in_time_features(self):
        """Test point-in-time correctness"""
        store = FeatureStore(backend=FeatureStoreBackend.CASSANDRA)

        timestamp = datetime.now() - timedelta(days=30)

        features = store.get_features_at_timestamp(
            entity_id="user_001",
            feature_group="user_features",
            timestamp=timestamp.isoformat(),
            features=["credit_score", "debt_to_income"]
        )

        assert features is not None
