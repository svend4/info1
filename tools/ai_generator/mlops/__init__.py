"""
Machine Learning Operations (MLOps) Package

Production-grade MLOps для model management, auto-retraining, A/B testing,
feature management, и drift detection.
"""

from .model_registry import (
    ModelRegistry,
    ModelVersion,
    ModelMetrics,
    ModelStage,
    ModelFramework,
    ModelPromotion
)

from .auto_retraining import (
    AutoRetrainingPipeline,
    RetrainingConfig,
    RetrainingJob,
    RetrainingTrigger,
    RetrainingStatus,
    RetrainingHistory
)

from .ab_testing import (
    ABTestingFramework,
    ABExperiment,
    ExperimentVariant,
    ExperimentMetrics,
    ExperimentStatus,
    VariantAssignment,
    StatisticalTest
)

from .feature_store import (
    MLFeatureStore,
    FeatureDefinition,
    FeatureValue,
    FeatureSet,
    FeatureType,
    FeatureStatus
)

from .drift_detector import (
    ModelDriftDetector,
    DriftReport,
    DriftMetrics,
    DriftType,
    DriftSeverity
)

__all__ = [
    # Model Registry
    'ModelRegistry',
    'ModelVersion',
    'ModelMetrics',
    'ModelStage',
    'ModelFramework',
    'ModelPromotion',

    # Auto-Retraining
    'AutoRetrainingPipeline',
    'RetrainingConfig',
    'RetrainingJob',
    'RetrainingTrigger',
    'RetrainingStatus',
    'RetrainingHistory',

    # A/B Testing
    'ABTestingFramework',
    'ABExperiment',
    'ExperimentVariant',
    'ExperimentMetrics',
    'ExperimentStatus',
    'VariantAssignment',
    'StatisticalTest',

    # Feature Store
    'MLFeatureStore',
    'FeatureDefinition',
    'FeatureValue',
    'FeatureSet',
    'FeatureType',
    'FeatureStatus',

    # Drift Detection
    'ModelDriftDetector',
    'DriftReport',
    'DriftMetrics',
    'DriftType',
    'DriftSeverity'
]

__version__ = '1.0.0'
