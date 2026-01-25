#!/usr/bin/env python3
"""
A/B Testing Framework

A/B тестирование моделей в production с statistical significance testing.
"""

import json
import random
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import math


class ExperimentStatus(Enum):
    """A/B Experiment Status"""
    DRAFT = "draft"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class VariantAssignment(Enum):
    """Traffic Assignment Strategy"""
    RANDOM = "random"
    DETERMINISTIC = "deterministic"  # Based on user ID hash
    WEIGHTED = "weighted"


@dataclass
class ExperimentVariant:
    """A/B Test Variant"""
    variant_id: str
    name: str
    model_version: int
    traffic_percentage: float  # 0-100
    description: str = ""
    is_control: bool = False


@dataclass
class ExperimentMetrics:
    """Metrics for a variant"""
    variant_id: str
    total_requests: int = 0
    total_predictions: int = 0
    success_count: int = 0
    error_count: int = 0
    avg_latency_ms: float = 0.0
    p95_latency_ms: float = 0.0
    custom_metrics: Dict[str, float] = field(default_factory=dict)

    def success_rate(self) -> float:
        """Calculate success rate"""
        if self.total_requests == 0:
            return 0.0
        return self.success_count / self.total_requests


@dataclass
class ABExperiment:
    """A/B Test Experiment"""
    experiment_id: str
    name: str
    model_name: str
    status: ExperimentStatus
    variants: List[ExperimentVariant]
    assignment_strategy: VariantAssignment
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    min_sample_size: int = 1000  # Minimum samples per variant
    confidence_level: float = 0.95  # 95% confidence
    metrics: Dict[str, ExperimentMetrics] = field(default_factory=dict)
    winner: Optional[str] = None
    description: str = ""


@dataclass
class StatisticalTest:
    """Statistical Test Result"""
    variant_a: str
    variant_b: str
    metric: str
    value_a: float
    value_b: float
    difference: float
    p_value: float
    is_significant: bool
    confidence_level: float
    sample_size_a: int
    sample_size_b: int


class ABTestingFramework:
    """A/B Testing Framework for Models"""

    def __init__(self, storage_path: Path):
        """
        Инициализация A/B testing framework

        Args:
            storage_path: Path for storing experiment data
        """
        self.storage_path = storage_path
        self.storage_path.mkdir(parents=True, exist_ok=True)

        self.experiments: Dict[str, ABExperiment] = {}
        self.user_assignments: Dict[str, Dict[str, str]] = {}  # {experiment_id: {user_id: variant_id}}

        self._load_experiments()

    def create_experiment(self,
                         name: str,
                         model_name: str,
                         variants: List[ExperimentVariant],
                         assignment_strategy: VariantAssignment = VariantAssignment.RANDOM,
                         min_sample_size: int = 1000,
                         confidence_level: float = 0.95,
                         description: str = "") -> ABExperiment:
        """
        Create A/B test experiment

        Args:
            name: Experiment name
            model_name: Model being tested
            variants: List of variants
            assignment_strategy: Traffic assignment strategy
            min_sample_size: Minimum samples per variant
            confidence_level: Statistical confidence level
            description: Experiment description

        Returns:
            Created experiment
        """
        # Validate traffic allocation
        total_traffic = sum(v.traffic_percentage for v in variants)
        if not (99.0 <= total_traffic <= 101.0):  # Allow 1% tolerance
            raise ValueError(f"Traffic allocation must sum to 100%, got {total_traffic}%")

        # Ensure exactly one control variant
        control_count = sum(1 for v in variants if v.is_control)
        if control_count != 1:
            raise ValueError("Experiment must have exactly one control variant")

        experiment = ABExperiment(
            experiment_id=f"exp_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            name=name,
            model_name=model_name,
            status=ExperimentStatus.DRAFT,
            variants=variants,
            assignment_strategy=assignment_strategy,
            created_at=datetime.utcnow(),
            min_sample_size=min_sample_size,
            confidence_level=confidence_level,
            description=description
        )

        # Initialize metrics for each variant
        for variant in variants:
            experiment.metrics[variant.variant_id] = ExperimentMetrics(variant_id=variant.variant_id)

        self.experiments[experiment.experiment_id] = experiment
        self.user_assignments[experiment.experiment_id] = {}

        self._save_experiment(experiment)
        print(f"✅ Created experiment: {experiment.experiment_id} - {name}")

        return experiment

    def start_experiment(self, experiment_id: str) -> bool:
        """
        Start A/B experiment

        Args:
            experiment_id: Experiment ID

        Returns:
            True if successful
        """
        experiment = self.experiments.get(experiment_id)
        if not experiment:
            return False

        if experiment.status != ExperimentStatus.DRAFT:
            raise ValueError(f"Can only start DRAFT experiments, current status: {experiment.status.value}")

        experiment.status = ExperimentStatus.RUNNING
        experiment.started_at = datetime.utcnow()

        self._save_experiment(experiment)
        print(f"✅ Started experiment: {experiment_id}")

        return True

    def assign_variant(self, experiment_id: str, user_id: str) -> Optional[ExperimentVariant]:
        """
        Assign user to variant

        Args:
            experiment_id: Experiment ID
            user_id: User ID

        Returns:
            Assigned variant or None
        """
        experiment = self.experiments.get(experiment_id)
        if not experiment or experiment.status != ExperimentStatus.RUNNING:
            return None

        # Check if user already assigned
        if user_id in self.user_assignments[experiment_id]:
            variant_id = self.user_assignments[experiment_id][user_id]
            return next((v for v in experiment.variants if v.variant_id == variant_id), None)

        # Assign based on strategy
        if experiment.assignment_strategy == VariantAssignment.RANDOM:
            variant = self._random_assignment(experiment)
        elif experiment.assignment_strategy == VariantAssignment.DETERMINISTIC:
            variant = self._deterministic_assignment(experiment, user_id)
        else:
            variant = self._weighted_assignment(experiment)

        # Store assignment
        self.user_assignments[experiment_id][user_id] = variant.variant_id

        return variant

    def record_prediction(self,
                         experiment_id: str,
                         variant_id: str,
                         success: bool,
                         latency_ms: float,
                         custom_metrics: Dict[str, float] = None):
        """
        Record prediction result

        Args:
            experiment_id: Experiment ID
            variant_id: Variant ID
            success: Whether prediction was successful
            latency_ms: Prediction latency
            custom_metrics: Additional metrics
        """
        experiment = self.experiments.get(experiment_id)
        if not experiment:
            return

        metrics = experiment.metrics.get(variant_id)
        if not metrics:
            return

        # Update metrics
        metrics.total_requests += 1
        metrics.total_predictions += 1

        if success:
            metrics.success_count += 1
        else:
            metrics.error_count += 1

        # Update latency (running average)
        n = metrics.total_requests
        metrics.avg_latency_ms = ((metrics.avg_latency_ms * (n - 1)) + latency_ms) / n

        # Update custom metrics
        if custom_metrics:
            for key, value in custom_metrics.items():
                if key not in metrics.custom_metrics:
                    metrics.custom_metrics[key] = value
                else:
                    # Running average
                    metrics.custom_metrics[key] = ((metrics.custom_metrics[key] * (n - 1)) + value) / n

        # Check if experiment is ready to analyze
        if self._is_ready_to_analyze(experiment):
            self._auto_analyze(experiment)

    def analyze_experiment(self, experiment_id: str) -> Dict[str, Any]:
        """
        Analyze A/B experiment results

        Args:
            experiment_id: Experiment ID

        Returns:
            Analysis results
        """
        experiment = self.experiments.get(experiment_id)
        if not experiment:
            raise ValueError(f"Experiment not found: {experiment_id}")

        # Get control variant
        control = next((v for v in experiment.variants if v.is_control), None)
        if not control:
            raise ValueError("No control variant found")

        control_metrics = experiment.metrics[control.variant_id]

        # Analyze each variant against control
        results = {
            'experiment_id': experiment_id,
            'name': experiment.name,
            'status': experiment.status.value,
            'duration_hours': self._get_duration_hours(experiment),
            'variants': {},
            'statistical_tests': [],
            'recommendation': None,
            'winner': None
        }

        for variant in experiment.variants:
            if variant.variant_id == control.variant_id:
                continue

            variant_metrics = experiment.metrics[variant.variant_id]

            # Perform statistical test
            test = self._perform_z_test(
                control_metrics,
                variant_metrics,
                experiment.confidence_level
            )

            results['statistical_tests'].append({
                'variant': variant.name,
                'metric': 'success_rate',
                'control_value': control_metrics.success_rate(),
                'variant_value': variant_metrics.success_rate(),
                'difference_percent': test.difference * 100,
                'p_value': test.p_value,
                'is_significant': test.is_significant,
                'sample_size': variant_metrics.total_requests
            })

            # Store variant summary
            results['variants'][variant.variant_id] = {
                'name': variant.name,
                'model_version': variant.model_version,
                'total_requests': variant_metrics.total_requests,
                'success_rate': variant_metrics.success_rate(),
                'avg_latency_ms': variant_metrics.avg_latency_ms,
                'is_control': variant.is_control
            }

        # Determine winner
        winner_variant = self._determine_winner(experiment, results['statistical_tests'])
        if winner_variant:
            experiment.winner = winner_variant.variant_id
            results['winner'] = winner_variant.name
            results['recommendation'] = f"Promote {winner_variant.name} (v{winner_variant.model_version}) to production"
        else:
            results['recommendation'] = "No statistically significant winner. Continue experiment or keep control."

        self._save_experiment(experiment)

        return results

    def complete_experiment(self, experiment_id: str) -> bool:
        """
        Complete A/B experiment

        Args:
            experiment_id: Experiment ID

        Returns:
            True if successful
        """
        experiment = self.experiments.get(experiment_id)
        if not experiment:
            return False

        experiment.status = ExperimentStatus.COMPLETED
        experiment.completed_at = datetime.utcnow()

        self._save_experiment(experiment)
        print(f"✅ Completed experiment: {experiment_id}")

        return True

    def get_experiment_summary(self, experiment_id: str) -> Dict[str, Any]:
        """
        Get experiment summary

        Args:
            experiment_id: Experiment ID

        Returns:
            Experiment summary
        """
        experiment = self.experiments.get(experiment_id)
        if not experiment:
            return {}

        summary = {
            'experiment_id': experiment_id,
            'name': experiment.name,
            'status': experiment.status.value,
            'created_at': experiment.created_at.isoformat(),
            'started_at': experiment.started_at.isoformat() if experiment.started_at else None,
            'variants': []
        }

        for variant in experiment.variants:
            metrics = experiment.metrics[variant.variant_id]
            summary['variants'].append({
                'name': variant.name,
                'is_control': variant.is_control,
                'traffic_percentage': variant.traffic_percentage,
                'total_requests': metrics.total_requests,
                'success_rate': f"{metrics.success_rate() * 100:.2f}%",
                'avg_latency_ms': f"{metrics.avg_latency_ms:.2f}"
            })

        return summary

    def _random_assignment(self, experiment: ABExperiment) -> ExperimentVariant:
        """Randomly assign variant based on traffic percentages"""
        rand = random.random() * 100
        cumulative = 0.0

        for variant in experiment.variants:
            cumulative += variant.traffic_percentage
            if rand <= cumulative:
                return variant

        return experiment.variants[0]

    def _deterministic_assignment(self, experiment: ABExperiment, user_id: str) -> ExperimentVariant:
        """Deterministically assign variant based on user ID hash"""
        # Hash user ID to get consistent assignment
        hash_val = hash(user_id) % 100

        cumulative = 0.0
        for variant in experiment.variants:
            cumulative += variant.traffic_percentage
            if hash_val < cumulative:
                return variant

        return experiment.variants[0]

    def _weighted_assignment(self, experiment: ABExperiment) -> ExperimentVariant:
        """Weighted random assignment"""
        return self._random_assignment(experiment)

    def _perform_z_test(self,
                       control_metrics: ExperimentMetrics,
                       variant_metrics: ExperimentMetrics,
                       confidence_level: float) -> StatisticalTest:
        """Perform two-proportion z-test"""
        n1 = control_metrics.total_requests
        n2 = variant_metrics.total_requests

        p1 = control_metrics.success_rate()
        p2 = variant_metrics.success_rate()

        # Calculate pooled proportion
        p_pool = (control_metrics.success_count + variant_metrics.success_count) / (n1 + n2)

        # Calculate standard error
        se = math.sqrt(p_pool * (1 - p_pool) * (1/n1 + 1/n2))

        # Calculate z-score
        z = (p2 - p1) / se if se > 0 else 0

        # Calculate p-value (two-tailed test)
        p_value = 2 * (1 - self._standard_normal_cdf(abs(z)))

        # Check significance
        alpha = 1 - confidence_level
        is_significant = p_value < alpha

        return StatisticalTest(
            variant_a="control",
            variant_b="variant",
            metric="success_rate",
            value_a=p1,
            value_b=p2,
            difference=(p2 - p1) / p1 if p1 > 0 else 0,
            p_value=p_value,
            is_significant=is_significant,
            confidence_level=confidence_level,
            sample_size_a=n1,
            sample_size_b=n2
        )

    def _standard_normal_cdf(self, x: float) -> float:
        """Standard normal cumulative distribution function"""
        # Approximation using error function
        return 0.5 * (1 + math.erf(x / math.sqrt(2)))

    def _determine_winner(self,
                         experiment: ABExperiment,
                         statistical_tests: List[Dict]) -> Optional[ExperimentVariant]:
        """Determine winning variant"""
        significant_improvements = []

        for test in statistical_tests:
            if test['is_significant'] and test['difference_percent'] > 0:
                significant_improvements.append(test)

        if not significant_improvements:
            return None

        # Return variant with highest improvement
        best_test = max(significant_improvements, key=lambda t: t['difference_percent'])
        return next((v for v in experiment.variants if v.name == best_test['variant']), None)

    def _is_ready_to_analyze(self, experiment: ABExperiment) -> bool:
        """Check if experiment has enough samples"""
        for metrics in experiment.metrics.values():
            if metrics.total_requests < experiment.min_sample_size:
                return False
        return True

    def _auto_analyze(self, experiment: ABExperiment):
        """Auto-analyze experiment when ready"""
        if experiment.status == ExperimentStatus.RUNNING and self._is_ready_to_analyze(experiment):
            results = self.analyze_experiment(experiment.experiment_id)
            if results.get('winner'):
                print(f"🎯 Experiment {experiment.experiment_id} has a winner: {results['winner']}")

    def _get_duration_hours(self, experiment: ABExperiment) -> float:
        """Get experiment duration in hours"""
        if not experiment.started_at:
            return 0.0

        end_time = experiment.completed_at or datetime.utcnow()
        duration = end_time - experiment.started_at
        return duration.total_seconds() / 3600

    def _save_experiment(self, experiment: ABExperiment):
        """Save experiment to disk"""
        exp_path = self.storage_path / f"{experiment.experiment_id}.json"

        exp_dict = {
            'experiment_id': experiment.experiment_id,
            'name': experiment.name,
            'model_name': experiment.model_name,
            'status': experiment.status.value,
            'assignment_strategy': experiment.assignment_strategy.value,
            'created_at': experiment.created_at.isoformat(),
            'started_at': experiment.started_at.isoformat() if experiment.started_at else None,
            'completed_at': experiment.completed_at.isoformat() if experiment.completed_at else None,
            'min_sample_size': experiment.min_sample_size,
            'confidence_level': experiment.confidence_level,
            'winner': experiment.winner,
            'description': experiment.description,
            'variants': [
                {
                    'variant_id': v.variant_id,
                    'name': v.name,
                    'model_version': v.model_version,
                    'traffic_percentage': v.traffic_percentage,
                    'is_control': v.is_control,
                    'description': v.description
                }
                for v in experiment.variants
            ],
            'metrics': {
                vid: {
                    'total_requests': m.total_requests,
                    'success_count': m.success_count,
                    'error_count': m.error_count,
                    'avg_latency_ms': m.avg_latency_ms,
                    'custom_metrics': m.custom_metrics
                }
                for vid, m in experiment.metrics.items()
            }
        }

        with open(exp_path, 'w') as f:
            json.dump(exp_dict, f, indent=2)

    def _load_experiments(self):
        """Load experiments from disk"""
        for exp_file in self.storage_path.glob("exp_*.json"):
            try:
                with open(exp_file) as f:
                    data = json.load(f)

                variants = [
                    ExperimentVariant(
                        variant_id=v['variant_id'],
                        name=v['name'],
                        model_version=v['model_version'],
                        traffic_percentage=v['traffic_percentage'],
                        is_control=v.get('is_control', False),
                        description=v.get('description', '')
                    )
                    for v in data['variants']
                ]

                experiment = ABExperiment(
                    experiment_id=data['experiment_id'],
                    name=data['name'],
                    model_name=data['model_name'],
                    status=ExperimentStatus(data['status']),
                    variants=variants,
                    assignment_strategy=VariantAssignment(data['assignment_strategy']),
                    created_at=datetime.fromisoformat(data['created_at']),
                    started_at=datetime.fromisoformat(data['started_at']) if data.get('started_at') else None,
                    completed_at=datetime.fromisoformat(data['completed_at']) if data.get('completed_at') else None,
                    min_sample_size=data.get('min_sample_size', 1000),
                    confidence_level=data.get('confidence_level', 0.95),
                    winner=data.get('winner'),
                    description=data.get('description', '')
                )

                # Load metrics
                for vid, metrics_data in data.get('metrics', {}).items():
                    experiment.metrics[vid] = ExperimentMetrics(
                        variant_id=vid,
                        total_requests=metrics_data['total_requests'],
                        success_count=metrics_data['success_count'],
                        error_count=metrics_data['error_count'],
                        avg_latency_ms=metrics_data['avg_latency_ms'],
                        custom_metrics=metrics_data.get('custom_metrics', {})
                    )

                self.experiments[experiment.experiment_id] = experiment
                self.user_assignments[experiment.experiment_id] = {}

            except Exception as e:
                print(f"Warning: Failed to load {exp_file}: {e}")
