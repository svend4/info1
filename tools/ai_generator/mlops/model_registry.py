#!/usr/bin/env python3
"""
Model Registry

MLflow-based model registry для versioning, deployment, и lifecycle management.
"""

import json
import pickle
import hashlib
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any


class ModelStage(Enum):
    """Model Deployment Stage"""
    NONE = "none"
    STAGING = "staging"
    PRODUCTION = "production"
    ARCHIVED = "archived"


class ModelFramework(Enum):
    """ML Framework"""
    SCIKIT_LEARN = "sklearn"
    TENSORFLOW = "tensorflow"
    PYTORCH = "pytorch"
    XGBOOST = "xgboost"
    LIGHTGBM = "lightgbm"
    CUSTOM = "custom"


@dataclass
class ModelMetrics:
    """Model Performance Metrics"""
    accuracy: Optional[float] = None
    precision: Optional[float] = None
    recall: Optional[float] = None
    f1_score: Optional[float] = None
    auc_roc: Optional[float] = None
    mse: Optional[float] = None
    mae: Optional[float] = None
    r2_score: Optional[float] = None
    custom_metrics: Dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        metrics = {}
        if self.accuracy is not None:
            metrics['accuracy'] = self.accuracy
        if self.precision is not None:
            metrics['precision'] = self.precision
        if self.recall is not None:
            metrics['recall'] = self.recall
        if self.f1_score is not None:
            metrics['f1_score'] = self.f1_score
        if self.auc_roc is not None:
            metrics['auc_roc'] = self.auc_roc
        if self.mse is not None:
            metrics['mse'] = self.mse
        if self.mae is not None:
            metrics['mae'] = self.mae
        if self.r2_score is not None:
            metrics['r2_score'] = self.r2_score
        metrics.update(self.custom_metrics)
        return metrics


@dataclass
class ModelVersion:
    """Model Version Information"""
    version_id: str
    model_name: str
    version_number: int
    framework: ModelFramework
    stage: ModelStage
    metrics: ModelMetrics
    model_path: Path
    created_at: datetime
    created_by: str
    description: str = ""
    tags: Dict[str, str] = field(default_factory=dict)
    parameters: Dict[str, Any] = field(default_factory=dict)
    signature: Optional[str] = None  # Model signature/checksum
    size_bytes: int = 0
    training_dataset: Optional[str] = None
    features: List[str] = field(default_factory=list)


@dataclass
class ModelPromotion:
    """Model Promotion Event"""
    promotion_id: str
    model_name: str
    version_number: int
    from_stage: ModelStage
    to_stage: ModelStage
    promoted_at: datetime
    promoted_by: str
    reason: str = ""
    approval_required: bool = False
    approved_by: Optional[str] = None


class ModelRegistry:
    """Model Registry - MLflow-based Model Management"""

    def __init__(self, storage_path: Path, mlflow_tracking_uri: Optional[str] = None):
        """
        Инициализация model registry

        Args:
            storage_path: Path for model storage
            mlflow_tracking_uri: MLflow tracking server URI
        """
        self.storage_path = storage_path
        self.mlflow_tracking_uri = mlflow_tracking_uri
        self.use_mlflow = mlflow_tracking_uri is not None

        # Create storage directories
        self.storage_path.mkdir(parents=True, exist_ok=True)
        (self.storage_path / "models").mkdir(exist_ok=True)
        (self.storage_path / "metadata").mkdir(exist_ok=True)

        # In-memory registry
        self.models: Dict[str, List[ModelVersion]] = {}
        self.promotions: List[ModelPromotion] = []

        # Load existing models
        self._load_registry()

    def register_model(self,
                      model_name: str,
                      model: Any,
                      framework: ModelFramework,
                      metrics: ModelMetrics,
                      created_by: str,
                      description: str = "",
                      tags: Dict[str, str] = None,
                      parameters: Dict[str, Any] = None,
                      features: List[str] = None,
                      training_dataset: Optional[str] = None) -> ModelVersion:
        """
        Register new model version

        Args:
            model_name: Model name
            model: Model object
            framework: ML framework
            metrics: Model performance metrics
            created_by: User who created the model
            description: Model description
            tags: Model tags
            parameters: Model parameters/config
            features: Feature names
            training_dataset: Training dataset reference

        Returns:
            Registered model version
        """
        # Determine version number
        version_number = 1
        if model_name in self.models:
            version_number = max(v.version_number for v in self.models[model_name]) + 1

        # Generate version ID
        version_id = f"{model_name}_v{version_number}"

        # Save model to disk
        model_path = self._save_model(model_name, version_number, model, framework)

        # Calculate model signature
        signature = self._calculate_signature(model_path)

        # Create model version
        model_version = ModelVersion(
            version_id=version_id,
            model_name=model_name,
            version_number=version_number,
            framework=framework,
            stage=ModelStage.NONE,
            metrics=metrics,
            model_path=model_path,
            created_at=datetime.utcnow(),
            created_by=created_by,
            description=description,
            tags=tags or {},
            parameters=parameters or {},
            signature=signature,
            size_bytes=model_path.stat().st_size,
            training_dataset=training_dataset,
            features=features or []
        )

        # Store in registry
        if model_name not in self.models:
            self.models[model_name] = []
        self.models[model_name].append(model_version)

        # Save metadata
        self._save_metadata(model_version)

        # Log to MLflow if enabled
        if self.use_mlflow:
            self._log_to_mlflow(model_version, model)

        print(f"✅ Registered {model_name} v{version_number} ({signature[:8]})")
        return model_version

    def get_model(self,
                  model_name: str,
                  version: Optional[int] = None,
                  stage: Optional[ModelStage] = None) -> Optional[ModelVersion]:
        """
        Get model version

        Args:
            model_name: Model name
            version: Specific version number (latest if None)
            stage: Get model in specific stage

        Returns:
            Model version or None
        """
        if model_name not in self.models:
            return None

        versions = self.models[model_name]

        # Filter by stage if specified
        if stage:
            versions = [v for v in versions if v.stage == stage]
            if not versions:
                return None

        # Get specific version or latest
        if version is not None:
            for v in versions:
                if v.version_number == version:
                    return v
            return None
        else:
            return max(versions, key=lambda v: v.version_number)

    def load_model(self, model_version: ModelVersion) -> Any:
        """
        Load model from storage

        Args:
            model_version: Model version to load

        Returns:
            Loaded model object
        """
        if not model_version.model_path.exists():
            raise FileNotFoundError(f"Model not found: {model_version.model_path}")

        # Verify signature
        current_signature = self._calculate_signature(model_version.model_path)
        if current_signature != model_version.signature:
            raise ValueError("Model signature mismatch - file may be corrupted")

        # Load based on framework
        if model_version.framework == ModelFramework.SCIKIT_LEARN:
            with open(model_version.model_path, 'rb') as f:
                return pickle.load(f)
        elif model_version.framework == ModelFramework.TENSORFLOW:
            # Would use tensorflow.keras.models.load_model
            with open(model_version.model_path, 'rb') as f:
                return pickle.load(f)  # Simplified
        elif model_version.framework == ModelFramework.PYTORCH:
            # Would use torch.load
            with open(model_version.model_path, 'rb') as f:
                return pickle.load(f)  # Simplified
        else:
            with open(model_version.model_path, 'rb') as f:
                return pickle.load(f)

    def promote_model(self,
                     model_name: str,
                     version: int,
                     to_stage: ModelStage,
                     promoted_by: str,
                     reason: str = "") -> ModelPromotion:
        """
        Promote model to different stage

        Args:
            model_name: Model name
            version: Version to promote
            to_stage: Target stage
            promoted_by: User promoting the model
            reason: Promotion reason

        Returns:
            Promotion event
        """
        model_version = self.get_model(model_name, version=version)
        if not model_version:
            raise ValueError(f"Model {model_name} v{version} not found")

        from_stage = model_version.stage

        # If promoting to production, demote current production model
        if to_stage == ModelStage.PRODUCTION:
            current_prod = self.get_model(model_name, stage=ModelStage.PRODUCTION)
            if current_prod and current_prod.version_number != version:
                current_prod.stage = ModelStage.ARCHIVED
                self._save_metadata(current_prod)

        # Update stage
        model_version.stage = to_stage
        self._save_metadata(model_version)

        # Record promotion
        promotion = ModelPromotion(
            promotion_id=f"promo_{len(self.promotions) + 1}",
            model_name=model_name,
            version_number=version,
            from_stage=from_stage,
            to_stage=to_stage,
            promoted_at=datetime.utcnow(),
            promoted_by=promoted_by,
            reason=reason
        )
        self.promotions.append(promotion)

        print(f"✅ Promoted {model_name} v{version}: {from_stage.value} → {to_stage.value}")
        return promotion

    def list_models(self, stage: Optional[ModelStage] = None) -> List[ModelVersion]:
        """
        List all models

        Args:
            stage: Filter by stage

        Returns:
            List of model versions
        """
        all_versions = []
        for versions in self.models.values():
            all_versions.extend(versions)

        if stage:
            all_versions = [v for v in all_versions if v.stage == stage]

        return sorted(all_versions, key=lambda v: v.created_at, reverse=True)

    def compare_models(self, model_name: str, version1: int, version2: int) -> Dict[str, Any]:
        """
        Compare two model versions

        Args:
            model_name: Model name
            version1: First version
            version2: Second version

        Returns:
            Comparison results
        """
        v1 = self.get_model(model_name, version=version1)
        v2 = self.get_model(model_name, version=version2)

        if not v1 or not v2:
            raise ValueError("One or both versions not found")

        comparison = {
            'model_name': model_name,
            'version1': version1,
            'version2': version2,
            'metrics_comparison': {},
            'winner': None
        }

        # Compare metrics
        metrics1 = v1.metrics.to_dict()
        metrics2 = v2.metrics.to_dict()

        all_metric_names = set(metrics1.keys()) | set(metrics2.keys())

        for metric in all_metric_names:
            val1 = metrics1.get(metric)
            val2 = metrics2.get(metric)

            comparison['metrics_comparison'][metric] = {
                'version1': val1,
                'version2': val2,
                'difference': (val2 - val1) if (val1 and val2) else None
            }

        # Determine winner based on primary metric (accuracy or lowest error)
        if 'accuracy' in metrics1 and 'accuracy' in metrics2:
            comparison['winner'] = version1 if metrics1['accuracy'] > metrics2['accuracy'] else version2
        elif 'mse' in metrics1 and 'mse' in metrics2:
            comparison['winner'] = version1 if metrics1['mse'] < metrics2['mse'] else version2

        return comparison

    def delete_model_version(self, model_name: str, version: int) -> bool:
        """
        Delete model version

        Args:
            model_name: Model name
            version: Version to delete

        Returns:
            True if successful
        """
        if model_name not in self.models:
            return False

        # Find version
        version_to_delete = None
        for v in self.models[model_name]:
            if v.version_number == version:
                version_to_delete = v
                break

        if not version_to_delete:
            return False

        # Cannot delete production models
        if version_to_delete.stage == ModelStage.PRODUCTION:
            raise ValueError("Cannot delete production model")

        # Remove from registry
        self.models[model_name].remove(version_to_delete)

        # Delete files
        if version_to_delete.model_path.exists():
            version_to_delete.model_path.unlink()

        metadata_path = self.storage_path / "metadata" / f"{version_to_delete.version_id}.json"
        if metadata_path.exists():
            metadata_path.unlink()

        print(f"✅ Deleted {model_name} v{version}")
        return True

    def _save_model(self, model_name: str, version: int, model: Any, framework: ModelFramework) -> Path:
        """Save model to disk"""
        model_dir = self.storage_path / "models" / model_name
        model_dir.mkdir(parents=True, exist_ok=True)

        model_path = model_dir / f"v{version}.pkl"

        # Save based on framework
        with open(model_path, 'wb') as f:
            pickle.dump(model, f)

        return model_path

    def _save_metadata(self, model_version: ModelVersion):
        """Save model metadata"""
        metadata_path = self.storage_path / "metadata" / f"{model_version.version_id}.json"

        metadata = {
            'version_id': model_version.version_id,
            'model_name': model_version.model_name,
            'version_number': model_version.version_number,
            'framework': model_version.framework.value,
            'stage': model_version.stage.value,
            'metrics': model_version.metrics.to_dict(),
            'model_path': str(model_version.model_path),
            'created_at': model_version.created_at.isoformat(),
            'created_by': model_version.created_by,
            'description': model_version.description,
            'tags': model_version.tags,
            'parameters': model_version.parameters,
            'signature': model_version.signature,
            'size_bytes': model_version.size_bytes,
            'training_dataset': model_version.training_dataset,
            'features': model_version.features
        }

        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)

    def _load_registry(self):
        """Load registry from disk"""
        metadata_dir = self.storage_path / "metadata"
        if not metadata_dir.exists():
            return

        for metadata_file in metadata_dir.glob("*.json"):
            try:
                with open(metadata_file) as f:
                    data = json.load(f)

                metrics = ModelMetrics(
                    accuracy=data['metrics'].get('accuracy'),
                    precision=data['metrics'].get('precision'),
                    recall=data['metrics'].get('recall'),
                    f1_score=data['metrics'].get('f1_score'),
                    auc_roc=data['metrics'].get('auc_roc'),
                    mse=data['metrics'].get('mse'),
                    mae=data['metrics'].get('mae'),
                    r2_score=data['metrics'].get('r2_score'),
                    custom_metrics={k: v for k, v in data['metrics'].items()
                                   if k not in ['accuracy', 'precision', 'recall', 'f1_score',
                                              'auc_roc', 'mse', 'mae', 'r2_score']}
                )

                model_version = ModelVersion(
                    version_id=data['version_id'],
                    model_name=data['model_name'],
                    version_number=data['version_number'],
                    framework=ModelFramework(data['framework']),
                    stage=ModelStage(data['stage']),
                    metrics=metrics,
                    model_path=Path(data['model_path']),
                    created_at=datetime.fromisoformat(data['created_at']),
                    created_by=data['created_by'],
                    description=data.get('description', ''),
                    tags=data.get('tags', {}),
                    parameters=data.get('parameters', {}),
                    signature=data.get('signature'),
                    size_bytes=data.get('size_bytes', 0),
                    training_dataset=data.get('training_dataset'),
                    features=data.get('features', [])
                )

                if model_version.model_name not in self.models:
                    self.models[model_version.model_name] = []
                self.models[model_version.model_name].append(model_version)

            except Exception as e:
                print(f"Warning: Failed to load {metadata_file}: {e}")

    def _calculate_signature(self, file_path: Path) -> str:
        """Calculate file signature/checksum"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def _log_to_mlflow(self, model_version: ModelVersion, model: Any):
        """Log model to MLflow"""
        try:
            import mlflow
            import mlflow.sklearn

            mlflow.set_tracking_uri(self.mlflow_tracking_uri)

            with mlflow.start_run(run_name=f"{model_version.model_name}_v{model_version.version_number}"):
                # Log parameters
                for key, value in model_version.parameters.items():
                    mlflow.log_param(key, value)

                # Log metrics
                for key, value in model_version.metrics.to_dict().items():
                    if value is not None:
                        mlflow.log_metric(key, value)

                # Log model
                if model_version.framework == ModelFramework.SCIKIT_LEARN:
                    mlflow.sklearn.log_model(model, "model")
                else:
                    mlflow.log_artifact(str(model_version.model_path))

                # Log tags
                for key, value in model_version.tags.items():
                    mlflow.set_tag(key, value)

        except ImportError:
            print("Warning: MLflow not installed, skipping MLflow logging")
        except Exception as e:
            print(f"Warning: MLflow logging failed: {e}")
