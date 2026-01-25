# Machine Learning Operations (MLOps) Module

Production-grade MLOps система для AI Code Generator с complete model lifecycle management, auto-retraining, A/B testing, feature store, и drift detection.

## 📋 Содержание

- [Возможности](#возможности)
- [Компоненты](#компоненты)
- [Установка](#установка)
- [Быстрый старт](#быстрый-старт)
- [Примеры использования](#примеры-использования)

## 🚀 Возможности

### Model Registry
- ✅ MLflow-based model versioning
- ✅ Multi-framework support (scikit-learn, TensorFlow, PyTorch, XGBoost, LightGBM)
- ✅ Model promotion workflow (None → Staging → Production → Archived)
- ✅ Model signature verification
- ✅ Model comparison & metrics tracking
- ✅ Versioning & lineage tracking

### Auto-Retraining Pipeline
- ✅ Scheduled retraining (cron-based)
- ✅ Performance degradation triggers
- ✅ Data drift triggers
- ✅ New data threshold triggers
- ✅ Auto-promotion based on performance
- ✅ Retraining job tracking & monitoring

### A/B Testing Framework
- ✅ Multi-variant experiments (A/B/C/...)
- ✅ Statistical significance testing (z-test, p-values)
- ✅ Traffic splitting strategies (random, deterministic, weighted)
- ✅ Real-time metrics tracking
- ✅ Automatic winner detection
- ✅ 95% confidence level testing

### Feature Store
- ✅ Centralized feature management
- ✅ Feature versioning
- ✅ Point-in-time correctness
- ✅ Feature lineage tracking
- ✅ Training dataset materialization
- ✅ Validation rules
- ✅ Feature sets management

### Drift Detection
- ✅ Data drift detection (KS test, PSI)
- ✅ Prediction drift monitoring
- ✅ Concept drift detection
- ✅ Multi-severity levels (Low/Medium/High/Critical)
- ✅ Automatic alert triggering
- ✅ Drift history tracking

## 📦 Компоненты

### 1. Model Registry (`model_registry.py`)

MLflow-based model registry для versioning и deployment management.

**Основные классы:**
- `ModelRegistry` - Main registry manager
- `ModelVersion` - Model version metadata
- `ModelMetrics` - Performance metrics

**Пример:**
```python
from ai_generator.mlops import ModelRegistry, ModelMetrics, ModelFramework, ModelStage

registry = ModelRegistry(storage_path=Path("./models"))

# Register model
metrics = ModelMetrics(accuracy=0.95, precision=0.94, recall=0.93, f1_score=0.935)
version = registry.register_model(
    model_name="fraud_detector",
    model=trained_model,
    framework=ModelFramework.SCIKIT_LEARN,
    metrics=metrics,
    created_by="data_scientist@company.com",
    description="Fraud detection model v1",
    features=["amount", "merchant_category", "time_since_last_tx"]
)

# Load model
loaded_model = registry.load_model(version)

# Promote to production
registry.promote_model(
    model_name="fraud_detector",
    version=1,
    to_stage=ModelStage.PRODUCTION,
    promoted_by="ml_engineer@company.com",
    reason="Passed all validation tests"
)

# Compare models
comparison = registry.compare_models("fraud_detector", version1=1, version2=2)
print(f"Winner: v{comparison['winner']}")
```

### 2. Auto-Retraining Pipeline (`auto_retraining.py`)

Автоматическое переобучение моделей с monitoring и scheduling.

**Основные классы:**
- `AutoRetrainingPipeline` - Pipeline manager
- `RetrainingConfig` - Configuration
- `RetrainingJob` - Job tracking

**Пример:**
```python
from ai_generator.mlops import AutoRetrainingPipeline, RetrainingConfig, RetrainingTrigger

pipeline = AutoRetrainingPipeline(storage_path=Path("./retraining"))

# Configure auto-retraining
config = RetrainingConfig(
    model_name="fraud_detector",
    schedule_cron="0 2 * * 0",  # Weekly at 2am
    performance_threshold=0.85,  # Retrain if accuracy < 85%
    min_new_samples=10000,
    auto_promote=True
)
pipeline.configure_retraining(config)

# Trigger retraining
def train_model(X_train, X_val):
    model = RandomForestClassifier()
    model.fit(X_train, y_train)
    metrics = {'accuracy': 0.92, 'f1_score': 0.91}
    return model, metrics

job = pipeline.trigger_retraining(
    model_name="fraud_detector",
    trigger=RetrainingTrigger.SCHEDULED,
    training_data=new_data,
    training_func=train_model
)

# Check performance degradation
if pipeline.check_performance_degradation("fraud_detector", {'accuracy': 0.82}):
    pipeline.trigger_retraining(...)
```

### 3. A/B Testing Framework (`ab_testing.py`)

A/B тестирование моделей в production.

**Основные классы:**
- `ABTestingFramework` - A/B testing manager
- `ABExperiment` - Experiment configuration
- `ExperimentVariant` - Model variant

**Пример:**
```python
from ai_generator.mlops import ABTestingFramework, ExperimentVariant, VariantAssignment

ab_testing = ABTestingFramework(storage_path=Path("./experiments"))

# Create experiment
variants = [
    ExperimentVariant(
        variant_id="control",
        name="Current Model",
        model_version=1,
        traffic_percentage=50.0,
        is_control=True
    ),
    ExperimentVariant(
        variant_id="variant_a",
        name="New Model",
        model_version=2,
        traffic_percentage=50.0
    )
]

experiment = ab_testing.create_experiment(
    name="Fraud Detection v2 Test",
    model_name="fraud_detector",
    variants=variants,
    min_sample_size=10000,
    confidence_level=0.95
)

# Start experiment
ab_testing.start_experiment(experiment.experiment_id)

# Assign users to variants
for user_id in users:
    variant = ab_testing.assign_variant(experiment.experiment_id, user_id)
    prediction = models[variant.model_version].predict(...)

    # Record result
    ab_testing.record_prediction(
        experiment.experiment_id,
        variant.variant_id,
        success=True,
        latency_ms=45.2
    )

# Analyze results
results = ab_testing.analyze_experiment(experiment.experiment_id)
print(f"Winner: {results['winner']}")
print(f"Recommendation: {results['recommendation']}")
```

### 4. Feature Store (`feature_store.py`)

Централизованное управление features.

**Основные классы:**
- `MLFeatureStore` - Feature store manager
- `FeatureDefinition` - Feature metadata
- `FeatureSet` - Feature collections

**Пример:**
```python
from ai_generator.mlops import MLFeatureStore, FeatureType

feature_store = MLFeatureStore(storage_path=Path("./features"))

# Register features
feature_store.register_feature(
    feature_name="user_avg_transaction_amount",
    feature_type=FeatureType.FLOAT,
    entity="user",
    description="Average transaction amount for user (30 days)",
    transformation="AVG(transaction.amount) OVER (user_id, 30 days)",
    validation_rules={'min': 0, 'max': 100000}
)

# Write feature values
feature_store.write_features(
    entity_id="user_12345",
    features={
        "user_avg_transaction_amount": 234.56,
        "user_transaction_count": 45,
        "user_days_since_registration": 180
    }
)

# Read features
features = feature_store.read_features(
    entity_id="user_12345",
    feature_names=["user_avg_transaction_amount", "user_transaction_count"]
)

# Create feature set
feature_set = feature_store.create_feature_set(
    name="fraud_detection_features",
    features=[
        "user_avg_transaction_amount",
        "user_transaction_count",
        "merchant_risk_score",
        "transaction_amount"
    ]
)

# Materialize training dataset
dataset_path = feature_store.materialize_training_dataset(
    feature_set_id=feature_set.feature_set_id,
    entity_ids=user_ids,
    output_path=Path("training_data.json"),
    format="json"
)
```

### 5. Drift Detector (`drift_detector.py`)

Обнаружение data drift и model drift.

**Основные классы:**
- `ModelDriftDetector` - Drift detection manager
- `DriftReport` - Drift report
- `DriftMetrics` - Feature-level drift metrics

**Пример:**
```python
from ai_generator.mlops import ModelDriftDetector, DriftType

drift_detector = ModelDriftDetector(storage_path=Path("./drift"))

# Set reference distribution (baseline)
reference_data = {
    "transaction_amount": [100, 200, 150, 300, 250, ...],
    "merchant_category": ["retail", "food", "retail", ...],
    "time_since_last_tx": [3600, 7200, 1800, ...]
}

drift_detector.set_reference_distribution(
    model_name="fraud_detector",
    reference_data=reference_data
)

# Detect drift in production data
current_data = {
    "transaction_amount": [500, 600, 450, 700, ...],  # Higher amounts!
    "merchant_category": ["retail", "food", ...],
    "time_since_last_tx": [1200, 2400, ...]
}

drift_report = drift_detector.detect_drift(
    model_name="fraud_detector",
    current_data=current_data,
    drift_type=DriftType.DATA_DRIFT
)

print(f"Overall Drift Score: {drift_report.overall_drift_score:.3f}")
print(f"Drift Severity: {drift_report.drift_severity.value}")
print(f"Alert Triggered: {drift_report.alert_triggered}")

for feature in drift_report.drifted_features:
    print(f"  {feature.feature_name}: {feature.drift_score:.3f} ({feature.drift_severity.value})")

# Monitor prediction drift
pred_drift_report = drift_detector.monitor_prediction_drift(
    model_name="fraud_detector",
    reference_predictions=[0.1, 0.2, 0.05, 0.3, ...],
    current_predictions=[0.6, 0.7, 0.5, 0.8, ...]  # Much higher!
)

if pred_drift_report.alert_triggered:
    print("🚨 Prediction drift detected - model may need retraining")
```

## ⚡ Быстрый старт

### Complete MLOps Pipeline

```python
from pathlib import Path
from ai_generator.mlops import (
    ModelRegistry, ModelMetrics, ModelFramework,
    AutoRetrainingPipeline, RetrainingConfig,
    ABTestingFramework, ExperimentVariant,
    MLFeatureStore, FeatureType,
    ModelDriftDetector, DriftType
)

# 1. Setup components
registry = ModelRegistry(Path("./models"))
retraining = AutoRetrainingPipeline(Path("./retraining"))
ab_testing = ABTestingFramework(Path("./experiments"))
feature_store = MLFeatureStore(Path("./features"))
drift_detector = ModelDriftDetector(Path("./drift"))

# 2. Register features
feature_store.register_feature(
    "transaction_amount", FeatureType.FLOAT, "transaction"
)

# 3. Train and register model
metrics = ModelMetrics(accuracy=0.95, f1_score=0.94)
version = registry.register_model(
    model_name="fraud_detector",
    model=trained_model,
    framework=ModelFramework.SCIKIT_LEARN,
    metrics=metrics,
    created_by="ml_team"
)

# 4. Configure auto-retraining
config = RetrainingConfig(
    model_name="fraud_detector",
    performance_threshold=0.85,
    min_new_samples=10000,
    auto_promote=True
)
retraining.configure_retraining(config)

# 5. Setup drift monitoring
drift_detector.set_reference_distribution(
    "fraud_detector",
    reference_data
)

# 6. Run A/B test before full deployment
experiment = ab_testing.create_experiment(
    name="Fraud v2",
    model_name="fraud_detector",
    variants=[control_variant, new_variant]
)

# 7. Monitor in production
drift_report = drift_detector.detect_drift("fraud_detector", production_data)
if drift_report.alert_triggered:
    # Trigger retraining
    retraining.trigger_retraining(...)
```

## 📈 Metrics

- **Total Lines of Code**: ~3,000
- **Modules**: 5
- **ML Frameworks Supported**: 5
- **Drift Detection Methods**: 3 (KS test, PSI, Chi-squared)
- **Statistical Tests**: z-test, KS test

## 🔧 Architecture

```
mlops/
├── model_registry.py       # Model versioning & registry (600 LOC)
├── auto_retraining.py     # Auto-retraining pipeline (450 LOC)
├── ab_testing.py          # A/B testing framework (600 LOC)
├── feature_store.py       # Feature management (550 LOC)
└── drift_detector.py      # Drift detection (550 LOC)
```

## 🎯 Use Cases

### E-commerce Recommendation System
```python
# Track model performance, retrain when drift detected
drift_report = drift_detector.detect_drift("recommender", user_behavior_data)
if drift_report.drift_severity == DriftSeverity.HIGH:
    retraining.trigger_retraining("recommender", ...)
```

### Fraud Detection
```python
# A/B test new fraud model with statistical rigor
ab_testing.create_experiment(...)
results = ab_testing.analyze_experiment(...)
if results['winner'] == 'new_model':
    registry.promote_model("fraud_detector", version=2, to_stage=ModelStage.PRODUCTION)
```

### Real-time Prediction Service
```python
# Serve features for real-time inference
features = feature_store.read_features(
    entity_id=user_id,
    feature_names=["user_ltv", "user_recency", "user_frequency"]
)
prediction = model.predict([features])
```

## 📝 Best Practices

### Model Registry
- ✅ Always track metrics when registering models
- ✅ Use semantic versioning for major changes
- ✅ Maintain at least 3 production model versions
- ✅ Verify model signatures before deployment

### Auto-Retraining
- ✅ Set appropriate performance thresholds
- ✅ Use validation split for retraining
- ✅ Monitor retraining job logs
- ✅ Gradual rollout after retraining

### A/B Testing
- ✅ Ensure statistical significance (min 1000 samples)
- ✅ Run experiments for sufficient duration (1-2 weeks)
- ✅ Use control variant as baseline
- ✅ Monitor experiment health daily

### Feature Store
- ✅ Document feature transformations
- ✅ Set validation rules for data quality
- ✅ Track feature lineage
- ✅ Version features when logic changes

### Drift Detection
- ✅ Update reference distributions quarterly
- ✅ Set appropriate drift thresholds
- ✅ Investigate HIGH/CRITICAL drift immediately
- ✅ Combine with auto-retraining

## 📊 Integration with ML Platforms

```python
# MLflow integration
registry = ModelRegistry(
    storage_path=Path("./models"),
    mlflow_tracking_uri="http://mlflow:5000"
)

# Feast integration (feature store)
# Production: integrate with Feast, Tecton, or AWS Feature Store
```

## 🔒 Production Considerations

- **High Availability**: Use distributed storage (S3, GCS) for model registry
- **Monitoring**: Integrate with Prometheus/Grafana for drift metrics
- **Alerting**: Configure PagerDuty/Slack alerts for critical drift
- **Compliance**: Audit all model promotions and A/B tests
- **Performance**: Cache feature values for low-latency serving

## 📝 License

Part of AI Code Generator - MLOps Module
Version 1.0.0
