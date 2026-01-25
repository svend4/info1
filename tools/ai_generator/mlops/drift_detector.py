#!/usr/bin/env python3
"""
Model Drift Detector

Обнаружение data drift и model drift для production моделей.
"""

import json
import math
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import statistics


class DriftType(Enum):
    """Drift Type"""
    DATA_DRIFT = "data_drift"
    PREDICTION_DRIFT = "prediction_drift"
    CONCEPT_DRIFT = "concept_drift"
    LABEL_DRIFT = "label_drift"


class DriftSeverity(Enum):
    """Drift Severity"""
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class DriftMetrics:
    """Drift Detection Metrics"""
    feature_name: str
    drift_score: float  # 0-1, higher = more drift
    drift_severity: DriftSeverity
    statistical_test: str  # e.g., "KS test", "PSI", "Chi-squared"
    p_value: Optional[float] = None
    reference_mean: Optional[float] = None
    current_mean: Optional[float] = None
    reference_std: Optional[float] = None
    current_std: Optional[float] = None


@dataclass
class DriftReport:
    """Drift Detection Report"""
    report_id: str
    model_name: str
    timestamp: datetime
    drift_type: DriftType
    overall_drift_score: float
    drift_severity: DriftSeverity
    drifted_features: List[DriftMetrics]
    total_features: int
    reference_period_start: datetime
    reference_period_end: datetime
    current_period_start: datetime
    current_period_end: datetime
    alert_triggered: bool = False
    recommendations: List[str] = field(default_factory=list)


class ModelDriftDetector:
    """Model Drift Detector"""

    def __init__(self, storage_path: Path):
        """
        Инициализация drift detector

        Args:
            storage_path: Path for storing drift data
        """
        self.storage_path = storage_path
        self.storage_path.mkdir(parents=True, exist_ok=True)

        # Reference distributions for each model
        self.reference_distributions: Dict[str, Dict[str, Any]] = {}

        # Drift detection thresholds
        self.thresholds = {
            'low': 0.1,
            'medium': 0.2,
            'high': 0.3,
            'critical': 0.4
        }

        self.drift_reports: List[DriftReport] = []

        self._load_reference_distributions()

    def set_reference_distribution(self,
                                   model_name: str,
                                   reference_data: Dict[str, List[Any]]):
        """
        Set reference distribution for drift detection

        Args:
            model_name: Model name
            reference_data: Dictionary of feature_name -> list of values
        """
        reference = {
            'model_name': model_name,
            'timestamp': datetime.utcnow(),
            'features': {}
        }

        for feature_name, values in reference_data.items():
            # Calculate statistics
            numeric_values = [v for v in values if isinstance(v, (int, float))]

            if numeric_values:
                reference['features'][feature_name] = {
                    'mean': statistics.mean(numeric_values),
                    'std': statistics.stdev(numeric_values) if len(numeric_values) > 1 else 0,
                    'min': min(numeric_values),
                    'max': max(numeric_values),
                    'percentiles': self._calculate_percentiles(numeric_values),
                    'histogram': self._calculate_histogram(numeric_values),
                    'type': 'numeric'
                }
            else:
                # Categorical feature
                value_counts = {}
                for v in values:
                    value_counts[str(v)] = value_counts.get(str(v), 0) + 1

                reference['features'][feature_name] = {
                    'value_counts': value_counts,
                    'unique_values': len(value_counts),
                    'type': 'categorical'
                }

        self.reference_distributions[model_name] = reference
        self._save_reference_distribution(model_name, reference)

        print(f"✅ Set reference distribution for {model_name} ({len(reference_data)} features)")

    def detect_drift(self,
                    model_name: str,
                    current_data: Dict[str, List[Any]],
                    drift_type: DriftType = DriftType.DATA_DRIFT) -> DriftReport:
        """
        Detect drift in current data

        Args:
            model_name: Model name
            current_data: Current data to check for drift
            drift_type: Type of drift to detect

        Returns:
            Drift report
        """
        reference = self.reference_distributions.get(model_name)
        if not reference:
            raise ValueError(f"No reference distribution for {model_name}. Set one first.")

        drifted_features = []
        total_drift_score = 0.0

        # Check each feature
        for feature_name, current_values in current_data.items():
            if feature_name not in reference['features']:
                continue

            ref_stats = reference['features'][feature_name]

            # Detect drift based on feature type
            if ref_stats['type'] == 'numeric':
                drift_metrics = self._detect_numeric_drift(
                    feature_name,
                    ref_stats,
                    current_values
                )
            else:
                drift_metrics = self._detect_categorical_drift(
                    feature_name,
                    ref_stats,
                    current_values
                )

            if drift_metrics.drift_severity != DriftSeverity.NONE:
                drifted_features.append(drift_metrics)

            total_drift_score += drift_metrics.drift_score

        # Calculate overall drift
        avg_drift_score = total_drift_score / len(current_data) if current_data else 0
        overall_severity = self._classify_severity(avg_drift_score)

        # Determine if alert should be triggered
        alert_triggered = overall_severity in [DriftSeverity.HIGH, DriftSeverity.CRITICAL]

        # Generate recommendations
        recommendations = self._generate_recommendations(
            drifted_features,
            overall_severity
        )

        # Create report
        report = DriftReport(
            report_id=f"drift_{model_name}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            model_name=model_name,
            timestamp=datetime.utcnow(),
            drift_type=drift_type,
            overall_drift_score=avg_drift_score,
            drift_severity=overall_severity,
            drifted_features=drifted_features,
            total_features=len(current_data),
            reference_period_start=reference['timestamp'] - timedelta(days=30),
            reference_period_end=reference['timestamp'],
            current_period_start=datetime.utcnow() - timedelta(days=7),
            current_period_end=datetime.utcnow(),
            alert_triggered=alert_triggered,
            recommendations=recommendations
        )

        self.drift_reports.append(report)
        self._save_drift_report(report)

        if alert_triggered:
            print(f"🚨 DRIFT ALERT: {model_name} - {overall_severity.value.upper()} drift detected!")
        else:
            print(f"✅ Drift check passed for {model_name}")

        return report

    def monitor_prediction_drift(self,
                                model_name: str,
                                reference_predictions: List[float],
                                current_predictions: List[float]) -> DriftReport:
        """
        Monitor prediction drift (distribution of predictions)

        Args:
            model_name: Model name
            reference_predictions: Reference predictions
            current_predictions: Current predictions

        Returns:
            Drift report
        """
        drift_metrics = self._detect_numeric_drift(
            "predictions",
            {
                'mean': statistics.mean(reference_predictions),
                'std': statistics.stdev(reference_predictions),
                'histogram': self._calculate_histogram(reference_predictions),
                'type': 'numeric'
            },
            current_predictions
        )

        report = DriftReport(
            report_id=f"pred_drift_{model_name}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            model_name=model_name,
            timestamp=datetime.utcnow(),
            drift_type=DriftType.PREDICTION_DRIFT,
            overall_drift_score=drift_metrics.drift_score,
            drift_severity=drift_metrics.drift_severity,
            drifted_features=[drift_metrics],
            total_features=1,
            reference_period_start=datetime.utcnow() - timedelta(days=30),
            reference_period_end=datetime.utcnow() - timedelta(days=7),
            current_period_start=datetime.utcnow() - timedelta(days=7),
            current_period_end=datetime.utcnow(),
            alert_triggered=drift_metrics.drift_severity in [DriftSeverity.HIGH, DriftSeverity.CRITICAL]
        )

        return report

    def get_drift_history(self,
                         model_name: str,
                         days: int = 30) -> List[DriftReport]:
        """
        Get drift detection history

        Args:
            model_name: Model name
            days: Number of days to look back

        Returns:
            List of drift reports
        """
        cutoff = datetime.utcnow() - timedelta(days=days)
        return [
            r for r in self.drift_reports
            if r.model_name == model_name and r.timestamp >= cutoff
        ]

    def _detect_numeric_drift(self,
                             feature_name: str,
                             reference_stats: Dict[str, Any],
                             current_values: List[Any]) -> DriftMetrics:
        """Detect drift in numeric feature using KS test"""
        numeric_values = [v for v in current_values if isinstance(v, (int, float))]

        if not numeric_values:
            return DriftMetrics(
                feature_name=feature_name,
                drift_score=0.0,
                drift_severity=DriftSeverity.NONE,
                statistical_test="none"
            )

        # Calculate current statistics
        current_mean = statistics.mean(numeric_values)
        current_std = statistics.stdev(numeric_values) if len(numeric_values) > 1 else 0

        # Perform Kolmogorov-Smirnov test (simplified)
        ks_statistic = self._ks_test(
            reference_stats.get('histogram', {}),
            self._calculate_histogram(numeric_values)
        )

        # Calculate Population Stability Index (PSI)
        psi_score = self._calculate_psi(
            reference_stats.get('histogram', {}),
            self._calculate_histogram(numeric_values)
        )

        # Use PSI as drift score
        drift_score = psi_score
        severity = self._classify_severity(drift_score)

        return DriftMetrics(
            feature_name=feature_name,
            drift_score=drift_score,
            drift_severity=severity,
            statistical_test="PSI",
            p_value=ks_statistic,
            reference_mean=reference_stats.get('mean'),
            current_mean=current_mean,
            reference_std=reference_stats.get('std'),
            current_std=current_std
        )

    def _detect_categorical_drift(self,
                                  feature_name: str,
                                  reference_stats: Dict[str, Any],
                                  current_values: List[Any]) -> DriftMetrics:
        """Detect drift in categorical feature using Chi-squared test"""
        # Count current values
        current_counts = {}
        for v in current_values:
            current_counts[str(v)] = current_counts.get(str(v), 0) + 1

        # Calculate chi-squared statistic (simplified)
        chi_squared = 0.0
        ref_counts = reference_stats.get('value_counts', {})
        ref_total = sum(ref_counts.values())
        current_total = len(current_values)

        all_values = set(ref_counts.keys()) | set(current_counts.keys())

        for value in all_values:
            ref_freq = ref_counts.get(value, 0) / ref_total if ref_total > 0 else 0
            current_freq = current_counts.get(value, 0) / current_total if current_total > 0 else 0

            if ref_freq > 0:
                chi_squared += ((current_freq - ref_freq) ** 2) / ref_freq

        # Normalize to 0-1 range
        drift_score = min(chi_squared / len(all_values), 1.0) if all_values else 0.0
        severity = self._classify_severity(drift_score)

        return DriftMetrics(
            feature_name=feature_name,
            drift_score=drift_score,
            drift_severity=severity,
            statistical_test="Chi-squared",
            p_value=chi_squared
        )

    def _calculate_psi(self, reference_hist: Dict, current_hist: Dict) -> float:
        """Calculate Population Stability Index"""
        if not reference_hist or not current_hist:
            return 0.0

        psi = 0.0
        all_bins = set(reference_hist.keys()) | set(current_hist.keys())

        ref_total = sum(reference_hist.values())
        current_total = sum(current_hist.values())

        for bin_name in all_bins:
            ref_pct = reference_hist.get(bin_name, 0) / ref_total if ref_total > 0 else 0
            current_pct = current_hist.get(bin_name, 0) / current_total if current_total > 0 else 0

            # Avoid log(0)
            if ref_pct > 0 and current_pct > 0:
                psi += (current_pct - ref_pct) * math.log(current_pct / ref_pct)

        return abs(psi)

    def _ks_test(self, reference_hist: Dict, current_hist: Dict) -> float:
        """Simplified Kolmogorov-Smirnov test"""
        if not reference_hist or not current_hist:
            return 0.0

        # Calculate cumulative distributions
        all_bins = sorted(set(reference_hist.keys()) | set(current_hist.keys()))

        ref_total = sum(reference_hist.values())
        current_total = sum(current_hist.values())

        ref_cumulative = 0.0
        current_cumulative = 0.0
        max_diff = 0.0

        for bin_name in all_bins:
            ref_cumulative += reference_hist.get(bin_name, 0) / ref_total if ref_total > 0 else 0
            current_cumulative += current_hist.get(bin_name, 0) / current_total if current_total > 0 else 0

            diff = abs(ref_cumulative - current_cumulative)
            max_diff = max(max_diff, diff)

        return max_diff

    def _calculate_histogram(self, values: List[float], bins: int = 10) -> Dict[str, int]:
        """Calculate histogram"""
        if not values:
            return {}

        min_val = min(values)
        max_val = max(values)

        if min_val == max_val:
            return {"0": len(values)}

        bin_width = (max_val - min_val) / bins
        histogram = {}

        for value in values:
            bin_idx = min(int((value - min_val) / bin_width), bins - 1)
            bin_name = f"{bin_idx}"
            histogram[bin_name] = histogram.get(bin_name, 0) + 1

        return histogram

    def _calculate_percentiles(self, values: List[float]) -> Dict[str, float]:
        """Calculate percentiles"""
        sorted_values = sorted(values)
        n = len(sorted_values)

        percentiles = {}
        for p in [25, 50, 75, 90, 95, 99]:
            idx = int(n * p / 100)
            percentiles[f"p{p}"] = sorted_values[min(idx, n - 1)]

        return percentiles

    def _classify_severity(self, drift_score: float) -> DriftSeverity:
        """Classify drift severity"""
        if drift_score >= self.thresholds['critical']:
            return DriftSeverity.CRITICAL
        elif drift_score >= self.thresholds['high']:
            return DriftSeverity.HIGH
        elif drift_score >= self.thresholds['medium']:
            return DriftSeverity.MEDIUM
        elif drift_score >= self.thresholds['low']:
            return DriftSeverity.LOW
        else:
            return DriftSeverity.NONE

    def _generate_recommendations(self,
                                 drifted_features: List[DriftMetrics],
                                 overall_severity: DriftSeverity) -> List[str]:
        """Generate recommendations based on drift"""
        recommendations = []

        if overall_severity == DriftSeverity.CRITICAL:
            recommendations.append("🚨 URGENT: Retrain model immediately")
            recommendations.append("Consider rolling back to previous version")
            recommendations.append("Investigate root cause of drift")

        elif overall_severity == DriftSeverity.HIGH:
            recommendations.append("⚠️  Schedule model retraining soon")
            recommendations.append("Monitor model performance closely")

        elif overall_severity == DriftSeverity.MEDIUM:
            recommendations.append("📊 Plan model retraining in next cycle")
            recommendations.append("Review feature engineering")

        elif overall_severity == DriftSeverity.LOW:
            recommendations.append("✅ Continue monitoring")

        # Feature-specific recommendations
        high_drift_features = [f for f in drifted_features if f.drift_severity in [DriftSeverity.HIGH, DriftSeverity.CRITICAL]]

        if high_drift_features:
            feature_names = ", ".join(f.feature_name for f in high_drift_features[:3])
            recommendations.append(f"Focus on features: {feature_names}")

        return recommendations

    def _save_reference_distribution(self, model_name: str, reference: Dict):
        """Save reference distribution"""
        ref_path = self.storage_path / f"{model_name}_reference.json"

        ref_dict = {
            'model_name': reference['model_name'],
            'timestamp': reference['timestamp'].isoformat(),
            'features': reference['features']
        }

        with open(ref_path, 'w') as f:
            json.dump(ref_dict, f, indent=2, default=str)

    def _save_drift_report(self, report: DriftReport):
        """Save drift report"""
        report_path = self.storage_path / f"{report.report_id}.json"

        report_dict = {
            'report_id': report.report_id,
            'model_name': report.model_name,
            'timestamp': report.timestamp.isoformat(),
            'drift_type': report.drift_type.value,
            'overall_drift_score': report.overall_drift_score,
            'drift_severity': report.drift_severity.value,
            'drifted_features': [
                {
                    'feature_name': f.feature_name,
                    'drift_score': f.drift_score,
                    'drift_severity': f.drift_severity.value,
                    'statistical_test': f.statistical_test,
                    'p_value': f.p_value,
                    'reference_mean': f.reference_mean,
                    'current_mean': f.current_mean
                }
                for f in report.drifted_features
            ],
            'total_features': report.total_features,
            'alert_triggered': report.alert_triggered,
            'recommendations': report.recommendations
        }

        with open(report_path, 'w') as f:
            json.dump(report_dict, f, indent=2)

    def _load_reference_distributions(self):
        """Load reference distributions"""
        for ref_file in self.storage_path.glob("*_reference.json"):
            try:
                with open(ref_file) as f:
                    data = json.load(f)

                reference = {
                    'model_name': data['model_name'],
                    'timestamp': datetime.fromisoformat(data['timestamp']),
                    'features': data['features']
                }

                self.reference_distributions[data['model_name']] = reference

            except Exception as e:
                print(f"Warning: Failed to load {ref_file}: {e}")
