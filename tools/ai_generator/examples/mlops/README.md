# MLOps & Model Management Examples

Comprehensive examples demonstrating all 4 MLOps modules in the AI Generator Toolkit.

## Examples Overview

### 01. Model Registry
**File:** `01_model_registry.py`

Model versioning and lifecycle management:
- ✅ MLflow model registry
- ✅ Model versioning with semantic versioning
- ✅ Model stage transitions (Staging → Production)
- ✅ Model comparison and selection
- ✅ Kubeflow registry integration
- ✅ DVC model tracking
- ✅ Rich metadata management
- ✅ Model lineage tracking

**Run example:**
```bash
python 01_model_registry.py
```

**Key concepts:**
- Model versioning and governance
- Multi-stage deployment workflows
- Model performance tracking
- Automated model comparison

---

### 02. A/B Testing
**File:** `02_ab_testing.py`

Statistical A/B testing for model comparison:
- ✅ Basic A/B tests (z-test, t-test)
- ✅ Multi-metric evaluation
- ✅ Sequential testing with early stopping
- ✅ Chi-square tests for categorical outcomes
- ✅ Bayesian A/B testing
- ✅ Multi-armed bandits (Thompson Sampling)
- ✅ Statistical power analysis
- ✅ Automated winner selection with guardrails

**Run example:**
```bash
python 02_ab_testing.py
```

**Key concepts:**
- Statistical significance testing
- Sample size calculation
- Bayesian inference
- Multi-armed bandit optimization

---

### 03. Drift Detection
**File:** `03_drift_detection.py`

Comprehensive drift monitoring:
- ✅ PSI (Population Stability Index) drift detection
- ✅ KS (Kolmogorov-Smirnov) test
- ✅ Multi-feature drift monitoring
- ✅ Concept drift detection
- ✅ Prediction drift monitoring
- ✅ Target variable drift
- ✅ Automated drift monitoring with alerts
- ✅ Drift correction strategies
- ✅ Drift monitoring dashboards

**Run example:**
```bash
python 03_drift_detection.py
```

**Key concepts:**
- Data distribution changes
- Model performance degradation
- Automated retraining triggers
- Real-time drift alerts

---

### 04. Feature Store
**File:** `04_feature_store.py`

Feature engineering and serving:
- ✅ Feature store setup (Redis, Cassandra)
- ✅ Feature definitions with validation
- ✅ Online features (low-latency serving)
- ✅ Offline features (batch training)
- ✅ Point-in-time correctness
- ✅ Feature engineering pipelines
- ✅ Feature versioning
- ✅ Feature quality monitoring
- ✅ Cross-team feature sharing
- ✅ Real-time aggregations

**Run example:**
```bash
python 04_feature_store.py
```

**Key concepts:**
- Feature reusability across teams
- Online vs. offline serving
- Point-in-time joins
- Feature quality monitoring

---

## Quick Start

### Run all MLOps examples
```bash
# Run all examples sequentially
for script in 0*.py; do
    echo "Running $script..."
    python "$script"
    echo ""
done
```

### Run specific example
```bash
# Example: Model registry
python 01_model_registry.py

# Example: A/B testing
python 02_ab_testing.py
```

## Prerequisites

Install required dependencies:

```bash
# Core MLOps dependencies
pip install mlflow
pip install scipy numpy pandas

# For model tracking
pip install dvc

# For feature store
pip install redis cassandra-driver

# For monitoring
pip install evidently alibi-detect
```

## Output Structure

Examples generate outputs in the `./output/` directory:

```
output/
├── models/
│   ├── churn-model/
│   ├── fraud-detection/
│   └── recommendation-engine/
├── ab_tests/
│   ├── test_results.json
│   └── statistical_reports/
├── drift_monitoring/
│   ├── drift_dashboard.html
│   ├── psi_reports/
│   └── alerts/
└── feature_store/
    ├── feature_catalog.json
    └── monitoring/
```

## MLOps Workflow

### 1. Model Development
```python
# Register model
from tools.ai_generator.mlops import ModelRegistry

registry = ModelRegistry(backend=MLBackend.MLFLOW)
registry.register_model(
    name="my-model",
    framework=ModelFramework.TENSORFLOW,
    metrics={"accuracy": 0.92}
)
```

### 2. A/B Testing
```python
# Test new model against production
from tools.ai_generator.mlops import ABTestFramework

framework = ABTestFramework()
result = framework.run_ab_test(
    control=prod_model_metrics,
    treatment=new_model_metrics,
    test_type=StatisticalTest.Z_TEST
)
```

### 3. Deployment & Monitoring
```python
# Promote to production
registry.transition_model_stage(
    name="my-model",
    version=2,
    stage=ModelStage.PRODUCTION
)

# Setup drift monitoring
detector = DriftDetector()
detector.setup_monitoring(features=["f1", "f2", "f3"])
```

### 4. Feature Management
```python
# Create and serve features
from tools.ai_generator.mlops import FeatureStore

store = FeatureStore(backend=FeatureStoreBackend.REDIS)
store.write_online_features(entity_id="user_123", features={...})
```

## Best Practices

### Model Registry
- ✅ Use semantic versioning (v1.0.0, v1.1.0, v2.0.0)
- ✅ Track comprehensive metadata (metrics, params, data info)
- ✅ Implement staging before production
- ✅ Document model lineage and dependencies
- ✅ Automate model governance workflows

### A/B Testing
- ✅ Define success metrics upfront
- ✅ Calculate required sample size
- ✅ Run for sufficient duration (consider weekly patterns)
- ✅ Use multiple metrics for evaluation
- ✅ Implement guardrails for business constraints
- ✅ Document all test parameters

### Drift Detection
- ✅ Monitor multiple drift types (data, concept, target)
- ✅ Set thresholds based on business impact
- ✅ Implement automated monitoring
- ✅ Track drift alongside model performance
- ✅ Document drift incidents
- ✅ Automate retraining when drift detected

### Feature Store
- ✅ Centralize feature definitions
- ✅ Ensure point-in-time correctness
- ✅ Monitor feature quality and freshness
- ✅ Version features with models
- ✅ Optimize for online and offline serving
- ✅ Document feature calculations
- ✅ Enable feature discovery and reuse

## Common Use Cases

### Model Lifecycle Management
```python
# Complete model lifecycle
registry = ModelRegistry(backend=MLBackend.MLFLOW)

# 1. Register new version
registry.register_model(name="model", version="2.0.0", ...)

# 2. A/B test
result = framework.run_ab_test(control=v1, treatment=v2)

# 3. Promote if better
if result.is_significant:
    registry.transition_model_stage("model", 2, ModelStage.PRODUCTION)

# 4. Monitor for drift
detector.setup_monitoring(model="model", version=2)
```

### Feature Engineering Pipeline
```python
# End-to-end feature pipeline
pipeline = FeaturePipeline(name="user-features")

# Define transformations
pipeline.add_step("calculate_recency", ...)
pipeline.add_step("calculate_frequency", ...)

# Execute and store
features = pipeline.execute(raw_data)
store.write_offline_features(features)
```

### Automated Model Retraining
```python
# Trigger retraining on drift
config = DriftConfig(
    psi_threshold=0.2,
    auto_retrain_on_drift=True
)

detector = DriftDetector(config)
detector.setup_monitoring(
    features=["f1", "f2"],
    on_drift_callback=trigger_retraining
)
```

## Troubleshooting

### MLflow Connection Issues
```
Issue: Cannot connect to MLflow tracking server
Solution: Verify MLFLOW_TRACKING_URI environment variable
```

### A/B Test Sample Size
```
Issue: Test taking too long
Solution: Run power analysis to optimize sample size
```

### Drift False Positives
```
Issue: Too many drift alerts
Solution: Adjust PSI/KS thresholds based on historical data
```

### Feature Store Latency
```
Issue: Slow online feature retrieval
Solution: Use Redis for hot features, implement caching
```

## Additional Resources

- [MLflow Documentation](https://mlflow.org/docs/latest/index.html)
- [Feature Store Concepts](https://www.featurestore.org/)
- [A/B Testing Guide](https://exp-platform.com/)
- [Drift Detection Methods](https://nannyml.readthedocs.io/)

## Metrics & KPIs

Track these MLOps metrics:

**Model Performance:**
- Model accuracy/F1/AUC over time
- Prediction latency (p50, p95, p99)
- Throughput (predictions/second)

**Operational:**
- Model deployment frequency
- Time to production
- Incident response time
- Model retraining frequency

**Data Quality:**
- Feature completeness
- Feature freshness
- Data drift severity
- Schema validation errors

---

**MLOps Examples** | Version 1.0.0 | Last Updated: 2026-01-25
