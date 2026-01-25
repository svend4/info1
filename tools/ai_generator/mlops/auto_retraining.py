#!/usr/bin/env python3
"""
Auto-Retraining Pipeline

Автоматическая переобучение моделей на новых данных с мониторингом производительности.
"""

import json
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable


class RetrainingTrigger(Enum):
    """Retraining Trigger Types"""
    SCHEDULED = "scheduled"
    PERFORMANCE_DEGRADATION = "performance_degradation"
    DATA_DRIFT = "data_drift"
    MANUAL = "manual"
    NEW_DATA_THRESHOLD = "new_data_threshold"


class RetrainingStatus(Enum):
    """Retraining Job Status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class RetrainingConfig:
    """Retraining Configuration"""
    model_name: str
    schedule_cron: Optional[str] = None  # e.g., "0 2 * * 0" (weekly at 2am)
    performance_threshold: float = 0.85  # Retrain if performance drops below
    drift_threshold: float = 0.1  # Retrain if drift exceeds this
    min_new_samples: int = 1000  # Minimum new samples to trigger retraining
    max_training_time_minutes: int = 120
    validation_split: float = 0.2
    auto_promote: bool = False  # Auto-promote if better than current production
    notification_email: Optional[str] = None


@dataclass
class RetrainingJob:
    """Retraining Job"""
    job_id: str
    model_name: str
    trigger: RetrainingTrigger
    status: RetrainingStatus
    config: RetrainingConfig
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    training_samples: int = 0
    validation_samples: int = 0
    old_metrics: Dict[str, float] = field(default_factory=dict)
    new_metrics: Dict[str, float] = field(default_factory=dict)
    improvement: Optional[float] = None
    new_version: Optional[int] = None
    error_message: Optional[str] = None
    logs: List[str] = field(default_factory=list)


@dataclass
class RetrainingHistory:
    """Retraining History Entry"""
    timestamp: datetime
    model_name: str
    trigger: RetrainingTrigger
    old_version: int
    new_version: int
    performance_improvement: float
    promoted_to_production: bool


class AutoRetrainingPipeline:
    """Auto-Retraining Pipeline Manager"""

    def __init__(self, storage_path: Path):
        """
        Инициализация auto-retraining pipeline

        Args:
            storage_path: Path for storing retraining data
        """
        self.storage_path = storage_path
        self.storage_path.mkdir(parents=True, exist_ok=True)

        self.configs: Dict[str, RetrainingConfig] = {}
        self.jobs: Dict[str, RetrainingJob] = {}
        self.history: List[RetrainingHistory] = []

        self._load_configs()

    def configure_retraining(self, config: RetrainingConfig):
        """
        Configure auto-retraining for a model

        Args:
            config: Retraining configuration
        """
        self.configs[config.model_name] = config
        self._save_config(config)
        print(f"✅ Configured auto-retraining for {config.model_name}")

    def trigger_retraining(self,
                          model_name: str,
                          trigger: RetrainingTrigger,
                          training_data: Any,
                          training_func: Callable) -> RetrainingJob:
        """
        Trigger model retraining

        Args:
            model_name: Model to retrain
            trigger: Trigger reason
            training_data: Training dataset
            training_func: Function to train the model

        Returns:
            Retraining job
        """
        config = self.configs.get(model_name)
        if not config:
            raise ValueError(f"No retraining config for {model_name}")

        # Create job
        job = RetrainingJob(
            job_id=f"retrain_{model_name}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            model_name=model_name,
            trigger=trigger,
            status=RetrainingStatus.PENDING,
            config=config
        )

        self.jobs[job.job_id] = job
        job.logs.append(f"Job created: {job.job_id}")
        job.logs.append(f"Trigger: {trigger.value}")

        # Execute retraining
        self._execute_retraining(job, training_data, training_func)

        return job

    def check_performance_degradation(self,
                                     model_name: str,
                                     current_metrics: Dict[str, float]) -> bool:
        """
        Check if model performance has degraded

        Args:
            model_name: Model name
            current_metrics: Current performance metrics

        Returns:
            True if retraining should be triggered
        """
        config = self.configs.get(model_name)
        if not config:
            return False

        # Check primary metric (accuracy or lowest error)
        primary_metric = current_metrics.get('accuracy') or current_metrics.get('f1_score')
        if primary_metric is None:
            primary_metric = 1.0 - (current_metrics.get('mse', 0) or current_metrics.get('mae', 0))

        if primary_metric < config.performance_threshold:
            print(f"⚠️  Performance degradation detected for {model_name}: {primary_metric:.3f} < {config.performance_threshold}")
            return True

        return False

    def check_new_data_threshold(self,
                                model_name: str,
                                new_samples_count: int) -> bool:
        """
        Check if enough new data is available

        Args:
            model_name: Model name
            new_samples_count: Number of new samples

        Returns:
            True if retraining should be triggered
        """
        config = self.configs.get(model_name)
        if not config:
            return False

        if new_samples_count >= config.min_new_samples:
            print(f"✅ New data threshold reached for {model_name}: {new_samples_count} samples")
            return True

        return False

    def get_scheduled_jobs(self) -> List[str]:
        """
        Get models that should be retrained based on schedule

        Returns:
            List of model names
        """
        scheduled = []
        current_time = datetime.utcnow()

        for model_name, config in self.configs.items():
            if config.schedule_cron:
                # Check if scheduled retraining is due
                # In production, use croniter or APScheduler
                last_training = self._get_last_training_time(model_name)
                if not last_training or (current_time - last_training) > timedelta(days=7):
                    scheduled.append(model_name)

        return scheduled

    def get_job_status(self, job_id: str) -> Optional[RetrainingJob]:
        """
        Get retraining job status

        Args:
            job_id: Job ID

        Returns:
            Retraining job or None
        """
        return self.jobs.get(job_id)

    def get_retraining_history(self,
                               model_name: Optional[str] = None,
                               limit: int = 10) -> List[RetrainingHistory]:
        """
        Get retraining history

        Args:
            model_name: Filter by model name
            limit: Maximum number of entries

        Returns:
            Retraining history
        """
        history = self.history

        if model_name:
            history = [h for h in history if h.model_name == model_name]

        return sorted(history, key=lambda h: h.timestamp, reverse=True)[:limit]

    def cancel_job(self, job_id: str) -> bool:
        """
        Cancel retraining job

        Args:
            job_id: Job ID to cancel

        Returns:
            True if successful
        """
        job = self.jobs.get(job_id)
        if not job:
            return False

        if job.status in [RetrainingStatus.PENDING, RetrainingStatus.RUNNING]:
            job.status = RetrainingStatus.CANCELLED
            job.logs.append(f"Job cancelled at {datetime.utcnow()}")
            return True

        return False

    def _execute_retraining(self,
                           job: RetrainingJob,
                           training_data: Any,
                           training_func: Callable):
        """Execute retraining job"""
        try:
            job.status = RetrainingStatus.RUNNING
            job.started_at = datetime.utcnow()
            job.logs.append(f"Training started at {job.started_at}")

            # Split data
            train_size = int(len(training_data) * (1 - job.config.validation_split))
            X_train = training_data[:train_size]
            X_val = training_data[train_size:]

            job.training_samples = len(X_train)
            job.validation_samples = len(X_val)
            job.logs.append(f"Training samples: {job.training_samples}")
            job.logs.append(f"Validation samples: {job.validation_samples}")

            # Train model
            job.logs.append("Training model...")
            model, metrics = training_func(X_train, X_val)

            job.new_metrics = metrics
            job.logs.append(f"Training completed. Metrics: {metrics}")

            # Calculate improvement
            if job.old_metrics:
                primary_old = job.old_metrics.get('accuracy', 0)
                primary_new = metrics.get('accuracy', 0)
                job.improvement = ((primary_new - primary_old) / primary_old * 100) if primary_old > 0 else 0
                job.logs.append(f"Performance improvement: {job.improvement:.2f}%")

            # Auto-promote if configured and improved
            if job.config.auto_promote and (job.improvement or 0) > 0:
                job.logs.append("Auto-promoting to production...")
                # Would call model_registry.promote_model here

            job.status = RetrainingStatus.COMPLETED
            job.completed_at = datetime.utcnow()
            job.logs.append(f"Job completed at {job.completed_at}")

            # Record history
            if job.new_version:
                self.history.append(RetrainingHistory(
                    timestamp=job.completed_at,
                    model_name=job.model_name,
                    trigger=job.trigger,
                    old_version=0,  # Would get from model registry
                    new_version=job.new_version,
                    performance_improvement=job.improvement or 0,
                    promoted_to_production=job.config.auto_promote
                ))

        except Exception as e:
            job.status = RetrainingStatus.FAILED
            job.error_message = str(e)
            job.logs.append(f"Error: {e}")
            job.completed_at = datetime.utcnow()

    def _get_last_training_time(self, model_name: str) -> Optional[datetime]:
        """Get last training time for a model"""
        model_history = [h for h in self.history if h.model_name == model_name]
        if model_history:
            return max(h.timestamp for h in model_history)
        return None

    def _save_config(self, config: RetrainingConfig):
        """Save retraining configuration"""
        config_path = self.storage_path / f"{config.model_name}_retraining_config.json"

        config_dict = {
            'model_name': config.model_name,
            'schedule_cron': config.schedule_cron,
            'performance_threshold': config.performance_threshold,
            'drift_threshold': config.drift_threshold,
            'min_new_samples': config.min_new_samples,
            'max_training_time_minutes': config.max_training_time_minutes,
            'validation_split': config.validation_split,
            'auto_promote': config.auto_promote,
            'notification_email': config.notification_email
        }

        with open(config_path, 'w') as f:
            json.dump(config_dict, f, indent=2)

    def _load_configs(self):
        """Load retraining configurations"""
        for config_file in self.storage_path.glob("*_retraining_config.json"):
            try:
                with open(config_file) as f:
                    data = json.load(f)

                config = RetrainingConfig(
                    model_name=data['model_name'],
                    schedule_cron=data.get('schedule_cron'),
                    performance_threshold=data.get('performance_threshold', 0.85),
                    drift_threshold=data.get('drift_threshold', 0.1),
                    min_new_samples=data.get('min_new_samples', 1000),
                    max_training_time_minutes=data.get('max_training_time_minutes', 120),
                    validation_split=data.get('validation_split', 0.2),
                    auto_promote=data.get('auto_promote', False),
                    notification_email=data.get('notification_email')
                )

                self.configs[config.model_name] = config

            except Exception as e:
                print(f"Warning: Failed to load {config_file}: {e}")
