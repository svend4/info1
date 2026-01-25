#!/usr/bin/env python3
"""
Example: Feature Store

This example demonstrates feature engineering, storage, and serving
using Redis, Cassandra, and feature pipelines.
"""

from pathlib import Path
import numpy as np
from datetime import datetime, timedelta
from tools.ai_generator.mlops import (
    FeatureStore,
    FeatureStoreBackend,
    FeatureDefinition,
    FeatureType,
    FeaturePipeline
)


def example_feature_store_setup():
    """Setup feature store with Redis backend"""
    print("=" * 60)
    print("Example 1: Feature Store Setup")
    print("=" * 60)

    store = FeatureStore(
        backend=FeatureStoreBackend.REDIS,
        redis_host="localhost",
        redis_port=6379
    )

    # Initialize feature store
    store.initialize()

    print("✅ Feature store initialized")
    print(f"   Backend: Redis")
    print(f"   Connection: localhost:6379")

    # Create feature groups
    feature_groups = [
        "user_features",
        "transaction_features",
        "product_features",
        "session_features"
    ]

    for group in feature_groups:
        store.create_feature_group(
            name=group,
            description=f"Feature group for {group.replace('_', ' ')}"
        )
        print(f"   ✅ Created feature group: {group}")
    print()


def example_feature_definition():
    """Define features with metadata"""
    print("=" * 60)
    print("Example 2: Feature Definitions")
    print("=" * 60)

    store = FeatureStore(backend=FeatureStoreBackend.REDIS)

    # Define user features
    user_features = [
        FeatureDefinition(
            name="user_age",
            feature_type=FeatureType.NUMERICAL,
            description="User age in years",
            default_value=0,
            validation_rules={"min": 0, "max": 120}
        ),
        FeatureDefinition(
            name="user_total_purchases",
            feature_type=FeatureType.NUMERICAL,
            description="Lifetime number of purchases",
            default_value=0,
            validation_rules={"min": 0}
        ),
        FeatureDefinition(
            name="user_avg_purchase_value",
            feature_type=FeatureType.NUMERICAL,
            description="Average purchase amount",
            default_value=0.0,
            validation_rules={"min": 0}
        ),
        FeatureDefinition(
            name="user_country",
            feature_type=FeatureType.CATEGORICAL,
            description="User country code",
            default_value="US",
            validation_rules={"allowed_values": ["US", "UK", "CA", "AU", "DE"]}
        ),
        FeatureDefinition(
            name="user_is_premium",
            feature_type=FeatureType.BOOLEAN,
            description="Whether user has premium subscription",
            default_value=False
        )
    ]

    print("📋 Feature Definitions:\n")
    for feature in user_features:
        store.register_feature(feature, feature_group="user_features")
        print(f"   ✅ {feature.name}")
        print(f"      Type: {feature.feature_type.value}")
        print(f"      Description: {feature.description}")
        print(f"      Validation: {feature.validation_rules}\n")
    print()


def example_online_features():
    """Online feature serving (low-latency)"""
    print("=" * 60)
    print("Example 3: Online Feature Serving")
    print("=" * 60)

    store = FeatureStore(backend=FeatureStoreBackend.REDIS)

    # Write online features
    user_id = "user_12345"

    features = {
        "user_age": 32,
        "user_total_purchases": 47,
        "user_avg_purchase_value": 89.50,
        "user_country": "US",
        "user_is_premium": True,
        "user_lifetime_value": 4206.50
    }

    store.write_online_features(
        entity_id=user_id,
        feature_group="user_features",
        features=features
    )

    print(f"✅ Features written for {user_id}")

    # Read online features (for real-time inference)
    retrieved_features = store.get_online_features(
        entity_id=user_id,
        feature_group="user_features",
        feature_names=["user_age", "user_total_purchases", "user_is_premium"]
    )

    print(f"\n📥 Retrieved features:")
    for name, value in retrieved_features.items():
        print(f"   {name}: {value}")

    # Measure latency
    import time
    start = time.time()
    store.get_online_features(user_id, "user_features")
    latency_ms = (time.time() - start) * 1000

    print(f"\n⚡ Retrieval latency: {latency_ms:.2f}ms")
    print()


def example_offline_features():
    """Offline feature serving (for training)"""
    print("=" * 60)
    print("Example 4: Offline Feature Serving")
    print("=" * 60)

    store = FeatureStore(backend=FeatureStoreBackend.CASSANDRA)

    # Write batch features for training
    training_data = []
    for i in range(1000):
        user_id = f"user_{i:05d}"
        timestamp = datetime.now() - timedelta(days=np.random.randint(0, 365))

        features = {
            "user_id": user_id,
            "timestamp": timestamp,
            "age": np.random.randint(18, 80),
            "total_purchases": np.random.randint(0, 200),
            "avg_purchase_value": np.random.uniform(10, 500),
            "days_since_last_purchase": np.random.randint(0, 365)
        }
        training_data.append(features)

    store.write_offline_features(
        feature_group="user_features",
        features=training_data
    )

    print(f"✅ Wrote {len(training_data)} feature records")

    # Query features for training
    training_features = store.get_offline_features(
        feature_group="user_features",
        start_date=datetime.now() - timedelta(days=90),
        end_date=datetime.now(),
        features=["age", "total_purchases", "avg_purchase_value"]
    )

    print(f"\n📊 Retrieved training data:")
    print(f"   Records: {len(training_features)}")
    print(f"   Features: {list(training_features[0].keys()) if training_features else []}")
    print(f"   Date range: Last 90 days")
    print()


def example_point_in_time_features():
    """Point-in-time correct features for training"""
    print("=" * 60)
    print("Example 5: Point-in-Time Correctness")
    print("=" * 60)

    store = FeatureStore(backend=FeatureStoreBackend.CASSANDRA)

    # Historical events (e.g., loan applications)
    loan_applications = [
        {"loan_id": "L001", "user_id": "user_001", "timestamp": "2025-01-15 10:00:00"},
        {"loan_id": "L002", "user_id": "user_002", "timestamp": "2025-02-20 14:30:00"},
        {"loan_id": "L003", "user_id": "user_003", "timestamp": "2025-03-10 09:15:00"},
    ]

    print("🕐 Point-in-Time Feature Retrieval:\n")

    for application in loan_applications:
        # Get features as they were at application time
        features_at_time = store.get_features_at_timestamp(
            entity_id=application["user_id"],
            feature_group="user_features",
            timestamp=application["timestamp"],
            features=["credit_score", "debt_to_income", "employment_length"]
        )

        print(f"   Loan {application['loan_id']} ({application['timestamp']}):")
        print(f"      User: {application['user_id']}")
        for feat_name, feat_value in features_at_time.items():
            print(f"      {feat_name}: {feat_value}")
        print()

    print("✅ Point-in-time correctness prevents data leakage")
    print("   Features reflect only information available at prediction time")
    print()


def example_feature_pipeline():
    """Feature engineering pipeline"""
    print("=" * 60)
    print("Example 6: Feature Engineering Pipeline")
    print("=" * 60)

    pipeline = FeaturePipeline(name="user_engagement_features")

    # Define transformation steps
    pipeline.add_step(
        name="calculate_recency",
        function=lambda df: (datetime.now() - df['last_purchase_date']).days,
        output_feature="days_since_last_purchase"
    )

    pipeline.add_step(
        name="calculate_frequency",
        function=lambda df: df['total_purchases'] / df['account_age_days'],
        output_feature="purchase_frequency"
    )

    pipeline.add_step(
        name="calculate_monetary",
        function=lambda df: df['total_spent'] / df['total_purchases'],
        output_feature="avg_order_value"
    )

    pipeline.add_step(
        name="calculate_rfm_score",
        function=lambda df: (
            df['recency_score'] * 0.3 +
            df['frequency_score'] * 0.3 +
            df['monetary_score'] * 0.4
        ),
        output_feature="rfm_score",
        dependencies=["recency_score", "frequency_score", "monetary_score"]
    )

    print("✅ Feature pipeline defined")
    print(f"\n📋 Pipeline steps:")
    for i, step in enumerate(pipeline.steps, 1):
        print(f"   {i}. {step['name']} → {step['output_feature']}")

    # Execute pipeline
    sample_data = {
        "user_id": "user_001",
        "last_purchase_date": datetime.now() - timedelta(days=30),
        "total_purchases": 25,
        "account_age_days": 365,
        "total_spent": 2500
    }

    features = pipeline.execute(sample_data)

    print(f"\n📊 Generated features:")
    for name, value in features.items():
        print(f"   {name}: {value:.2f}")
    print()


def example_feature_versioning():
    """Version control for features"""
    print("=" * 60)
    print("Example 7: Feature Versioning")
    print("=" * 60)

    store = FeatureStore(backend=FeatureStoreBackend.REDIS)

    # Register feature with versioning
    feature_versions = [
        {
            "version": "v1",
            "name": "user_risk_score",
            "calculation": "simple_rule_based",
            "accuracy": 0.72
        },
        {
            "version": "v2",
            "name": "user_risk_score",
            "calculation": "logistic_regression",
            "accuracy": 0.81
        },
        {
            "version": "v3",
            "name": "user_risk_score",
            "calculation": "gradient_boosting",
            "accuracy": 0.89
        }
    ]

    print("📦 Feature Versions:\n")

    for version_info in feature_versions:
        store.register_feature_version(
            name=version_info["name"],
            version=version_info["version"],
            calculation_logic=version_info["calculation"],
            metadata={"accuracy": version_info["accuracy"]}
        )

        print(f"   {version_info['version']}: {version_info['calculation']}")
        print(f"      Accuracy: {version_info['accuracy']:.2%}\n")

    # Use specific version
    user_id = "user_123"
    risk_score_v3 = store.get_feature(
        entity_id=user_id,
        feature_name="user_risk_score",
        version="v3"
    )

    print(f"✅ Retrieved feature version v3 for {user_id}")
    print(f"   Using best-performing calculation (89% accuracy)")
    print()


def example_feature_monitoring():
    """Monitor feature quality and freshness"""
    print("=" * 60)
    print("Example 8: Feature Monitoring")
    print("=" * 60)

    store = FeatureStore(backend=FeatureStoreBackend.REDIS)

    # Setup monitoring
    store.setup_monitoring(
        feature_group="user_features",
        metrics=[
            "completeness",  # % of non-null values
            "freshness",  # Time since last update
            "distribution",  # Statistical properties
            "validation_errors"  # Schema violations
        ]
    )

    print("✅ Feature monitoring configured")

    # Simulate monitoring report
    monitoring_report = {
        "user_age": {
            "completeness": 0.99,
            "avg_freshness_hours": 2.5,
            "validation_errors": 3,
            "distribution_drift": 0.08
        },
        "user_total_purchases": {
            "completeness": 1.00,
            "avg_freshness_hours": 1.2,
            "validation_errors": 0,
            "distribution_drift": 0.15
        },
        "user_country": {
            "completeness": 0.97,
            "avg_freshness_hours": 5.0,
            "validation_errors": 120,  # Invalid country codes
            "distribution_drift": 0.22
        }
    }

    print(f"\n📊 Feature Quality Report:\n")

    for feature_name, metrics in monitoring_report.items():
        status = "✅" if metrics["validation_errors"] == 0 else "⚠️"
        print(f"   {status} {feature_name}:")
        print(f"      Completeness: {metrics['completeness']:.1%}")
        print(f"      Freshness: {metrics['avg_freshness_hours']:.1f}h")
        print(f"      Validation errors: {metrics['validation_errors']}")
        print(f"      Distribution drift: {metrics['distribution_drift']:.2f}\n")

    issues_count = sum(1 for m in monitoring_report.values() if m["validation_errors"] > 0)
    print(f"⚠️ Features with issues: {issues_count}/{len(monitoring_report)}")
    print()


def example_feature_sharing():
    """Share features across teams and models"""
    print("=" * 60)
    print("Example 9: Cross-Team Feature Sharing")
    print("=" * 60)

    store = FeatureStore(backend=FeatureStoreBackend.REDIS)

    # Catalog of shared features
    feature_catalog = {
        "fraud_detection_team": [
            "transaction_velocity",
            "ip_risk_score",
            "device_fingerprint_age"
        ],
        "credit_risk_team": [
            "debt_to_income_ratio",
            "payment_history_score",
            "credit_utilization"
        ],
        "personalization_team": [
            "user_preferences_vector",
            "browsing_category_affinity",
            "purchase_propensity"
        ]
    }

    print("📚 Feature Catalog:\n")

    total_features = 0
    for team, features in feature_catalog.items():
        print(f"   {team}:")
        for feature in features:
            print(f"      - {feature}")
            total_features += 1
        print()

    print(f"🔄 Feature Reuse:")
    print(f"   Total teams: {len(feature_catalog)}")
    print(f"   Total features: {total_features}")
    print(f"   Avg features/team: {total_features / len(feature_catalog):.1f}")

    print(f"\n✨ Benefits:")
    print(f"   ✅ Avoid duplicate feature engineering")
    print(f"   ✅ Consistent feature definitions")
    print(f"   ✅ Faster model development")
    print(f"   ✅ Improved collaboration")
    print()


def example_real_time_aggregations():
    """Real-time feature aggregations"""
    print("=" * 60)
    print("Example 10: Real-Time Aggregations")
    print("=" * 60)

    store = FeatureStore(backend=FeatureStoreBackend.REDIS)

    # Define streaming aggregations
    aggregations = [
        {
            "name": "transactions_last_1h",
            "window": "1h",
            "aggregation": "count",
            "source": "transaction_stream"
        },
        {
            "name": "avg_transaction_amount_24h",
            "window": "24h",
            "aggregation": "mean",
            "source": "transaction_stream"
        },
        {
            "name": "unique_merchants_7d",
            "window": "7d",
            "aggregation": "count_distinct",
            "source": "transaction_stream"
        }
    ]

    print("⚡ Real-Time Aggregation Features:\n")

    for agg in aggregations:
        store.create_streaming_feature(
            name=agg["name"],
            window=agg["window"],
            aggregation=agg["aggregation"],
            source=agg["source"]
        )

        print(f"   ✅ {agg['name']}")
        print(f"      Window: {agg['window']}")
        print(f"      Aggregation: {agg['aggregation']}")
        print(f"      Source: {agg['source']}\n")

    # Simulate real-time retrieval
    user_id = "user_456"
    realtime_features = store.get_streaming_features(
        entity_id=user_id,
        feature_names=[agg["name"] for agg in aggregations]
    )

    print(f"📊 Real-time features for {user_id}:")
    for name, value in realtime_features.items():
        print(f"   {name}: {value}")

    print(f"\n⚡ Features computed in real-time from streams")
    print(f"   Latency: < 10ms")
    print()


if __name__ == "__main__":
    print("\n🗄️ Feature Store Examples")
    print("=" * 60)
    print()

    # Run all examples
    example_feature_store_setup()
    example_feature_definition()
    example_online_features()
    example_offline_features()
    example_point_in_time_features()
    example_feature_pipeline()
    example_feature_versioning()
    example_feature_monitoring()
    example_feature_sharing()
    example_real_time_aggregations()

    print("=" * 60)
    print("✅ All feature store examples completed!")
    print("=" * 60)
    print("\n📚 Feature Store Best Practices:")
    print("   1. Centralize feature definitions across teams")
    print("   2. Ensure point-in-time correctness for training")
    print("   3. Monitor feature quality and freshness")
    print("   4. Version features alongside models")
    print("   5. Optimize for both online (low-latency) and offline serving")
    print("   6. Document feature semantics and calculation logic")
    print("   7. Implement feature validation and schema enforcement")
    print("   8. Enable feature discovery and reuse across teams")
