#!/usr/bin/env python3
"""
Example: Model Registry

This example demonstrates ML model versioning and management
using MLflow, Kubeflow, and DVC.
"""

from pathlib import Path
import numpy as np
from tools.ai_generator.mlops import (
    ModelRegistry,
    MLBackend,
    ModelMetadata,
    ModelFramework,
    ModelStage
)


def example_mlflow_registry():
    """MLflow model registry setup"""
    print("=" * 60)
    print("Example 1: MLflow Model Registry")
    print("=" * 60)

    registry = ModelRegistry(backend=MLBackend.MLFLOW)

    # Register model
    model_info = registry.register_model(
        name="customer-churn-predictor",
        framework=ModelFramework.TENSORFLOW,
        model_path="./models/churn-model",
        metrics={
            "accuracy": 0.94,
            "precision": 0.92,
            "recall": 0.91,
            "f1_score": 0.915,
            "auc_roc": 0.96
        },
        parameters={
            "learning_rate": 0.001,
            "batch_size": 32,
            "epochs": 100,
            "optimizer": "adam"
        },
        tags={
            "team": "data-science",
            "project": "customer-retention",
            "version": "v2.1.0"
        }
    )

    print(f"✅ Model registered: {model_info['name']}")
    print(f"📦 Version: {model_info['version']}")
    print(f"🔖 Run ID: {model_info['run_id']}")

    print(f"\n📊 Metrics:")
    for metric, value in model_info['metrics'].items():
        print(f"   {metric}: {value:.4f}")

    print(f"\n⚙️ Parameters:")
    for param, value in model_info['parameters'].items():
        print(f"   {param}: {value}")
    print()


def example_model_versioning():
    """Model version management"""
    print("=" * 60)
    print("Example 2: Model Versioning")
    print("=" * 60)

    registry = ModelRegistry(backend=MLBackend.MLFLOW)

    model_name = "fraud-detection"

    # Register multiple versions
    versions = [
        {"version": "1.0.0", "accuracy": 0.85, "framework": ModelFramework.SKLEARN},
        {"version": "1.1.0", "accuracy": 0.89, "framework": ModelFramework.SKLEARN},
        {"version": "2.0.0", "accuracy": 0.93, "framework": ModelFramework.PYTORCH},
        {"version": "2.1.0", "accuracy": 0.95, "framework": ModelFramework.PYTORCH},
    ]

    for v in versions:
        registry.register_model(
            name=model_name,
            framework=v["framework"],
            model_path=f"./models/{model_name}-{v['version']}",
            metrics={"accuracy": v["accuracy"]},
            tags={"version": v["version"]}
        )
        print(f"✅ Registered: {model_name} v{v['version']} (accuracy: {v['accuracy']:.2f})")

    # List all versions
    all_versions = registry.list_model_versions(model_name)

    print(f"\n📋 All versions of '{model_name}':")
    for version in all_versions:
        print(f"   v{version['version']}: {version['current_stage']}")

    # Get latest version
    latest = registry.get_latest_version(model_name)
    print(f"\n🚀 Latest version: v{latest['version']}")
    print()


def example_model_stages():
    """Promote models through stages"""
    print("=" * 60)
    print("Example 3: Model Stage Management")
    print("=" * 60)

    registry = ModelRegistry(backend=MLBackend.MLFLOW)

    model_name = "recommendation-engine"

    # Register model
    registry.register_model(
        name=model_name,
        framework=ModelFramework.TENSORFLOW,
        model_path="./models/recommender",
        metrics={"ndcg@10": 0.82, "precision@10": 0.75}
    )

    print(f"✅ Model registered: {model_name}")

    # Transition through stages
    stages = [
        (ModelStage.STAGING, "Model passed validation tests"),
        (ModelStage.PRODUCTION, "A/B test shows 15% improvement"),
    ]

    for stage, comment in stages:
        registry.transition_model_stage(
            name=model_name,
            version=1,
            stage=stage,
            archive_existing_versions=False
        )
        print(f"📊 Transitioned to: {stage.value} - {comment}")

    # Get production model
    prod_model = registry.get_model_by_stage(model_name, ModelStage.PRODUCTION)
    print(f"\n🚀 Production model: v{prod_model['version']}")
    print(f"📈 Metrics: {prod_model['metrics']}")
    print()


def example_model_comparison():
    """Compare different model versions"""
    print("=" * 60)
    print("Example 4: Model Comparison")
    print("=" * 60)

    registry = ModelRegistry(backend=MLBackend.MLFLOW)

    # Register competing models
    models = [
        {
            "name": "sentiment-classifier",
            "framework": ModelFramework.SKLEARN,
            "algorithm": "LogisticRegression",
            "metrics": {"accuracy": 0.82, "f1": 0.80}
        },
        {
            "name": "sentiment-classifier",
            "framework": ModelFramework.SKLEARN,
            "algorithm": "RandomForest",
            "metrics": {"accuracy": 0.87, "f1": 0.85}
        },
        {
            "name": "sentiment-classifier",
            "framework": ModelFramework.PYTORCH,
            "algorithm": "BERT",
            "metrics": {"accuracy": 0.94, "f1": 0.93}
        }
    ]

    for model in models:
        registry.register_model(
            name=model["name"],
            framework=model["framework"],
            model_path=f"./models/{model['algorithm'].lower()}",
            metrics=model["metrics"],
            tags={"algorithm": model["algorithm"]}
        )

    # Compare models
    comparison = registry.compare_models(
        model_name="sentiment-classifier",
        metric="f1"
    )

    print("📊 Model Comparison (by F1 score):")
    for i, model in enumerate(comparison, 1):
        print(f"\n   {i}. {model['algorithm']}")
        print(f"      Framework: {model['framework']}")
        print(f"      Accuracy: {model['metrics']['accuracy']:.2f}")
        print(f"      F1 Score: {model['metrics']['f1']:.2f}")

    best = comparison[0]
    print(f"\n🏆 Best model: {best['algorithm']} (F1: {best['metrics']['f1']:.2f})")
    print()


def example_kubeflow_registry():
    """Kubeflow model registry integration"""
    print("=" * 60)
    print("Example 5: Kubeflow Model Registry")
    print("=" * 60)

    registry = ModelRegistry(backend=MLBackend.KUBEFLOW)

    # Register model with Kubeflow
    model_info = registry.register_model(
        name="image-classifier",
        framework=ModelFramework.TENSORFLOW,
        model_path="s3://ml-models/image-classifier/v1",
        metrics={
            "top1_accuracy": 0.92,
            "top5_accuracy": 0.98
        },
        serving_config={
            "runtime": "tensorflow-serving",
            "resources": {
                "cpu": "2",
                "memory": "4Gi",
                "gpu": "1"
            }
        }
    )

    print(f"✅ Model registered in Kubeflow")
    print(f"📦 Model URI: {model_info['model_uri']}")
    print(f"🎯 Serving runtime: {model_info['serving_config']['runtime']}")

    # Deploy model
    deployment = registry.deploy_model(
        name="image-classifier",
        version=1,
        replicas=3,
        autoscaling=True,
        min_replicas=1,
        max_replicas=10,
        target_cpu_utilization=70
    )

    print(f"\n🚀 Model deployed:")
    print(f"   Endpoint: {deployment['endpoint']}")
    print(f"   Replicas: {deployment['replicas']}")
    print(f"   Autoscaling: {deployment['autoscaling']}")
    print()


def example_dvc_tracking():
    """DVC for model versioning"""
    print("=" * 60)
    print("Example 6: DVC Model Tracking")
    print("=" * 60)

    registry = ModelRegistry(backend=MLBackend.DVC)

    # Track model with DVC
    registry.track_model(
        name="time-series-forecaster",
        model_path="./models/forecaster.pkl",
        remote_storage="s3://ml-models-bucket",
        metadata={
            "framework": "prophet",
            "mae": 125.3,
            "rmse": 189.7,
            "mape": 0.08
        }
    )

    print("✅ Model tracked with DVC")
    print("📦 Remote storage: s3://ml-models-bucket")

    # Create DVC pipeline
    pipeline = registry.create_pipeline(
        name="forecasting-pipeline",
        stages=[
            {"name": "data-prep", "cmd": "python prepare_data.py", "deps": ["data/raw"], "outs": ["data/processed"]},
            {"name": "train", "cmd": "python train.py", "deps": ["data/processed"], "outs": ["models/forecaster.pkl"]},
            {"name": "evaluate", "cmd": "python evaluate.py", "deps": ["models/forecaster.pkl"], "metrics": ["metrics.json"]}
        ]
    )

    print(f"\n📋 DVC Pipeline created:")
    for stage in pipeline['stages']:
        print(f"   - {stage['name']}: {stage['cmd']}")
    print()


def example_model_metadata():
    """Rich model metadata management"""
    print("=" * 60)
    print("Example 7: Model Metadata Management")
    print("=" * 60)

    registry = ModelRegistry(backend=MLBackend.MLFLOW)

    # Register model with extensive metadata
    metadata = ModelMetadata(
        name="credit-risk-model",
        framework=ModelFramework.XGBOOST,
        version="3.2.0",
        description="Credit risk assessment model using gradient boosting",
        author="data-science-team@example.com",
        created_date="2026-01-15",
        training_data={
            "dataset": "credit-history-2025",
            "samples": 1_500_000,
            "features": 87,
            "date_range": "2023-01-01 to 2025-12-31"
        },
        metrics={
            "auc_roc": 0.89,
            "precision": 0.82,
            "recall": 0.78,
            "f1_score": 0.80,
            "gini": 0.78
        },
        hyperparameters={
            "max_depth": 6,
            "learning_rate": 0.1,
            "n_estimators": 100,
            "subsample": 0.8,
            "colsample_bytree": 0.8
        },
        feature_importance={
            "payment_history": 0.32,
            "credit_utilization": 0.24,
            "account_age": 0.15,
            "total_debt": 0.12,
            "income": 0.10
        },
        business_metrics={
            "expected_default_reduction": "12%",
            "estimated_annual_savings": "$2.4M",
            "processing_time": "< 100ms"
        },
        compliance={
            "fair_lending_approved": True,
            "model_documentation": "docs/credit-risk-v3.2.pdf",
            "validation_report": "reports/validation-2026-01.pdf"
        }
    )

    registry.register_model_with_metadata(metadata)

    print("✅ Model registered with comprehensive metadata")

    print(f"\n📊 Training Data:")
    print(f"   Dataset: {metadata.training_data['dataset']}")
    print(f"   Samples: {metadata.training_data['samples']:,}")
    print(f"   Features: {metadata.training_data['features']}")

    print(f"\n🎯 Top 3 Features:")
    for feature, importance in list(metadata.feature_importance.items())[:3]:
        print(f"   {feature}: {importance:.2%}")

    print(f"\n💰 Business Impact:")
    print(f"   Default reduction: {metadata.business_metrics['expected_default_reduction']}")
    print(f"   Annual savings: {metadata.business_metrics['estimated_annual_savings']}")
    print()


def example_model_lineage():
    """Track model lineage and dependencies"""
    print("=" * 60)
    print("Example 8: Model Lineage Tracking")
    print("=" * 60)

    registry = ModelRegistry(backend=MLBackend.MLFLOW)

    # Register models with lineage
    base_model = registry.register_model(
        name="base-language-model",
        framework=ModelFramework.PYTORCH,
        model_path="./models/bert-base",
        metrics={"perplexity": 12.5}
    )

    fine_tuned = registry.register_model(
        name="domain-specific-nlp",
        framework=ModelFramework.PYTORCH,
        model_path="./models/bert-finetuned",
        metrics={"accuracy": 0.91},
        parent_model=base_model['run_id'],
        lineage={
            "base_model": "base-language-model:v1",
            "fine_tuning_data": "medical-texts-2025",
            "fine_tuning_steps": 10000
        }
    )

    print("✅ Model lineage tracked")
    print(f"\n📊 Lineage chain:")
    print(f"   Base: {base_model['name']}")
    print(f"   ↓ Fine-tuned on medical texts")
    print(f"   Derived: {fine_tuned['name']}")

    # Get model ancestry
    ancestry = registry.get_model_lineage("domain-specific-nlp")
    print(f"\n🌳 Full lineage:")
    for level, model in enumerate(ancestry):
        indent = "  " * level
        print(f"   {indent}- {model['name']} (v{model['version']})")
    print()


if __name__ == "__main__":
    print("\n📦 Model Registry Examples")
    print("=" * 60)
    print()

    # Run all examples
    example_mlflow_registry()
    example_model_versioning()
    example_model_stages()
    example_model_comparison()
    example_kubeflow_registry()
    example_dvc_tracking()
    example_model_metadata()
    example_model_lineage()

    print("=" * 60)
    print("✅ All model registry examples completed!")
    print("=" * 60)
    print("\n📚 Best Practices:")
    print("   1. Version all models with semantic versioning")
    print("   2. Track comprehensive metadata (metrics, params, data)")
    print("   3. Use staging environments before production")
    print("   4. Document model lineage and dependencies")
    print("   5. Implement model governance and approval workflows")
    print("   6. Monitor model performance in production")
    print("   7. Automate model retraining pipelines")
    print("   8. Maintain model cards for transparency")
