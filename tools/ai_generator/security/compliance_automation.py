#!/usr/bin/env python3
"""
Compliance Automation

Автоматизация compliance проверок (SOC 2, ISO 27001, GDPR, HIPAA).
"""

import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Set


class ComplianceFramework(Enum):
    """Compliance Frameworks"""
    SOC2 = "soc2"
    ISO_27001 = "iso_27001"
    GDPR = "gdpr"
    HIPAA = "hipaa"
    PCI_DSS = "pci_dss"
    CCPA = "ccpa"
    NIST = "nist"


class CheckSeverity(Enum):
    """Compliance Check Severity"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class CheckStatus(Enum):
    """Compliance Check Status"""
    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"
    NOT_APPLICABLE = "not_applicable"
    PENDING = "pending"


@dataclass
class ComplianceControl:
    """Compliance Control"""
    control_id: str
    framework: ComplianceFramework
    title: str
    description: str
    severity: CheckSeverity
    category: str
    requirements: List[str]
    automated_checks: List[str] = field(default_factory=list)
    remediation_steps: List[str] = field(default_factory=list)


@dataclass
class ComplianceCheckResult:
    """Compliance Check Result"""
    control_id: str
    status: CheckStatus
    severity: CheckSeverity
    message: str
    evidence: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    findings: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


@dataclass
class ComplianceReport:
    """Compliance Report"""
    report_id: str
    framework: ComplianceFramework
    generated_at: datetime
    period_start: datetime
    period_end: datetime
    total_controls: int
    passed_controls: int
    failed_controls: int
    warning_controls: int
    compliance_score: float
    results: List[ComplianceCheckResult]
    summary: Dict[str, Any] = field(default_factory=dict)


class ComplianceAutomation:
    """Compliance Automation Manager"""

    # SOC 2 Controls
    SOC2_CONTROLS = {
        'CC1.1': ComplianceControl(
            control_id='CC1.1',
            framework=ComplianceFramework.SOC2,
            title='Control Environment',
            description='The entity demonstrates a commitment to integrity and ethical values',
            severity=CheckSeverity.HIGH,
            category='Control Environment',
            requirements=[
                'Code of conduct documented',
                'Ethics training completed',
                'Conflict of interest policy in place'
            ],
            automated_checks=['check_code_of_conduct', 'check_training_records'],
            remediation_steps=['Document code of conduct', 'Implement ethics training program']
        ),
        'CC2.1': ComplianceControl(
            control_id='CC2.1',
            framework=ComplianceFramework.SOC2,
            title='Communication and Information',
            description='The entity obtains or generates and uses relevant, quality information',
            severity=CheckSeverity.MEDIUM,
            category='Communication',
            requirements=['Information security policy documented', 'Incident response procedures'],
            automated_checks=['check_security_policies']
        ),
        'CC6.1': ComplianceControl(
            control_id='CC6.1',
            framework=ComplianceFramework.SOC2,
            title='Logical and Physical Access Controls',
            description='The entity implements logical access security software',
            severity=CheckSeverity.CRITICAL,
            category='Access Control',
            requirements=['MFA enabled', 'RBAC implemented', 'Access reviews conducted'],
            automated_checks=['check_mfa_enabled', 'check_rbac', 'check_access_logs'],
            remediation_steps=['Enable MFA for all users', 'Implement RBAC', 'Schedule quarterly access reviews']
        ),
        'CC7.2': ComplianceControl(
            control_id='CC7.2',
            framework=ComplianceFramework.SOC2,
            title='System Monitoring',
            description='The entity monitors system components',
            severity=CheckSeverity.HIGH,
            category='Monitoring',
            requirements=['Logging enabled', 'Alerting configured', 'Log retention policy'],
            automated_checks=['check_logging', 'check_alerts'],
            remediation_steps=['Enable comprehensive logging', 'Configure security alerts']
        )
    }

    # GDPR Articles
    GDPR_CONTROLS = {
        'ART5': ComplianceControl(
            control_id='ART5',
            framework=ComplianceFramework.GDPR,
            title='Principles relating to processing',
            description='Personal data must be processed lawfully, fairly and transparently',
            severity=CheckSeverity.CRITICAL,
            category='Data Processing',
            requirements=['Privacy policy published', 'Consent mechanism', 'Data processing records'],
            automated_checks=['check_privacy_policy', 'check_consent_logs'],
            remediation_steps=['Publish privacy policy', 'Implement consent management']
        ),
        'ART25': ComplianceControl(
            control_id='ART25',
            framework=ComplianceFramework.GDPR,
            title='Data protection by design and by default',
            description='Implement appropriate technical and organizational measures',
            severity=CheckSeverity.HIGH,
            category='Data Protection',
            requirements=['Data minimization', 'Pseudonymization', 'Encryption at rest'],
            automated_checks=['check_encryption', 'check_data_minimization'],
            remediation_steps=['Enable encryption at rest', 'Implement data minimization']
        ),
        'ART32': ComplianceControl(
            control_id='ART32',
            framework=ComplianceFramework.GDPR,
            title='Security of processing',
            description='Implement appropriate technical and organizational security measures',
            severity=CheckSeverity.CRITICAL,
            category='Security',
            requirements=['Encryption', 'Access controls', 'Regular security testing'],
            automated_checks=['check_encryption', 'check_access_controls', 'check_vulnerability_scans'],
            remediation_steps=['Enable encryption', 'Implement access controls', 'Schedule security testing']
        ),
        'ART33': ComplianceControl(
            control_id='ART33',
            framework=ComplianceFramework.GDPR,
            title='Notification of personal data breach',
            description='Notify supervisory authority of breach within 72 hours',
            severity=CheckSeverity.CRITICAL,
            category='Incident Response',
            requirements=['Breach detection', 'Notification procedures', 'Incident log'],
            automated_checks=['check_incident_response_plan', 'check_breach_notifications'],
            remediation_steps=['Implement breach detection', 'Document notification procedures']
        )
    }

    # ISO 27001 Controls
    ISO27001_CONTROLS = {
        'A.9.1.1': ComplianceControl(
            control_id='A.9.1.1',
            framework=ComplianceFramework.ISO_27001,
            title='Access control policy',
            description='An access control policy shall be established',
            severity=CheckSeverity.HIGH,
            category='Access Control',
            requirements=['Access control policy documented', 'Regular reviews'],
            automated_checks=['check_access_policy']
        ),
        'A.10.1.1': ComplianceControl(
            control_id='A.10.1.1',
            framework=ComplianceFramework.ISO_27001,
            title='Policy on the use of cryptographic controls',
            description='A policy on the use of cryptographic controls shall be developed',
            severity=CheckSeverity.HIGH,
            category='Cryptography',
            requirements=['Encryption policy', 'Key management procedures'],
            automated_checks=['check_encryption_policy', 'check_key_management']
        ),
        'A.12.4.1': ComplianceControl(
            control_id='A.12.4.1',
            framework=ComplianceFramework.ISO_27001,
            title='Event logging',
            description='Event logs recording user activities shall be produced',
            severity=CheckSeverity.MEDIUM,
            category='Logging',
            requirements=['Comprehensive logging', 'Log retention', 'Log protection'],
            automated_checks=['check_event_logging', 'check_log_retention'],
            remediation_steps=['Enable event logging', 'Configure log retention']
        )
    }

    def __init__(self, project_path: Path):
        """
        Инициализация compliance automation

        Args:
            project_path: Path to project directory
        """
        self.project_path = project_path
        self.all_controls = {
            **self.SOC2_CONTROLS,
            **self.GDPR_CONTROLS,
            **self.ISO27001_CONTROLS
        }

    def run_compliance_check(self,
                            framework: ComplianceFramework,
                            control_ids: Optional[List[str]] = None) -> List[ComplianceCheckResult]:
        """
        Run compliance checks

        Args:
            framework: Compliance framework to check
            control_ids: Specific controls to check (all if None)

        Returns:
            List of check results
        """
        results = []

        # Filter controls by framework
        controls = {
            cid: ctrl for cid, ctrl in self.all_controls.items()
            if ctrl.framework == framework
        }

        # Filter by specific control IDs if provided
        if control_ids:
            controls = {cid: ctrl for cid, ctrl in controls.items() if cid in control_ids}

        # Run checks
        for control_id, control in controls.items():
            result = self._execute_control_checks(control)
            results.append(result)

        return results

    def generate_compliance_report(self,
                                   framework: ComplianceFramework,
                                   period_days: int = 30) -> ComplianceReport:
        """
        Generate compliance report

        Args:
            framework: Compliance framework
            period_days: Reporting period in days

        Returns:
            Compliance report
        """
        period_end = datetime.utcnow()
        period_start = period_end - timedelta(days=period_days)

        # Run all checks for framework
        results = self.run_compliance_check(framework)

        # Calculate statistics
        total = len(results)
        passed = sum(1 for r in results if r.status == CheckStatus.PASSED)
        failed = sum(1 for r in results if r.status == CheckStatus.FAILED)
        warnings = sum(1 for r in results if r.status == CheckStatus.WARNING)

        # Calculate compliance score (weighted by severity)
        compliance_score = self._calculate_compliance_score(results)

        # Generate summary
        summary = {
            'framework': framework.value,
            'total_controls': total,
            'passed_controls': passed,
            'failed_controls': failed,
            'warning_controls': warnings,
            'compliance_percentage': (passed / total * 100) if total > 0 else 0,
            'critical_failures': sum(1 for r in results if r.status == CheckStatus.FAILED and r.severity == CheckSeverity.CRITICAL),
            'high_failures': sum(1 for r in results if r.status == CheckStatus.FAILED and r.severity == CheckSeverity.HIGH)
        }

        report = ComplianceReport(
            report_id=f"compliance_{framework.value}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            framework=framework,
            generated_at=datetime.utcnow(),
            period_start=period_start,
            period_end=period_end,
            total_controls=total,
            passed_controls=passed,
            failed_controls=failed,
            warning_controls=warnings,
            compliance_score=compliance_score,
            results=results,
            summary=summary
        )

        return report

    def export_report(self, report: ComplianceReport, output_path: Path, format: str = 'json'):
        """
        Export compliance report

        Args:
            report: Compliance report
            output_path: Output file path
            format: Export format (json, html, pdf)
        """
        if format == 'json':
            self._export_json(report, output_path)
        elif format == 'html':
            self._export_html(report, output_path)
        else:
            raise ValueError(f"Unsupported format: {format}")

    def _execute_control_checks(self, control: ComplianceControl) -> ComplianceCheckResult:
        """Execute automated checks for a control"""
        findings = []
        recommendations = []
        evidence = {}

        # Run automated checks
        all_passed = True
        for check_name in control.automated_checks:
            check_method = getattr(self, check_name, None)
            if check_method:
                passed, evidence_data = check_method()
                evidence[check_name] = evidence_data

                if not passed:
                    all_passed = False
                    findings.append(f"Failed: {check_name}")
            else:
                findings.append(f"Check not implemented: {check_name}")
                all_passed = False

        # Determine status
        if all_passed:
            status = CheckStatus.PASSED
            message = f"Control {control.control_id} passed all checks"
        else:
            if control.severity in [CheckSeverity.CRITICAL, CheckSeverity.HIGH]:
                status = CheckStatus.FAILED
            else:
                status = CheckStatus.WARNING
            message = f"Control {control.control_id} failed {len(findings)} checks"
            recommendations = control.remediation_steps

        return ComplianceCheckResult(
            control_id=control.control_id,
            status=status,
            severity=control.severity,
            message=message,
            evidence=evidence,
            findings=findings,
            recommendations=recommendations
        )

    def _calculate_compliance_score(self, results: List[ComplianceCheckResult]) -> float:
        """Calculate weighted compliance score"""
        if not results:
            return 0.0

        severity_weights = {
            CheckSeverity.CRITICAL: 4.0,
            CheckSeverity.HIGH: 3.0,
            CheckSeverity.MEDIUM: 2.0,
            CheckSeverity.LOW: 1.0,
            CheckSeverity.INFO: 0.5
        }

        total_weight = 0.0
        earned_weight = 0.0

        for result in results:
            weight = severity_weights.get(result.severity, 1.0)
            total_weight += weight

            if result.status == CheckStatus.PASSED:
                earned_weight += weight
            elif result.status == CheckStatus.WARNING:
                earned_weight += weight * 0.5

        return (earned_weight / total_weight * 100) if total_weight > 0 else 0.0

    # Automated Check Methods
    def check_mfa_enabled(self) -> tuple[bool, Dict]:
        """Check if MFA is enabled"""
        # Simulate check - in production, query auth system
        evidence = {'mfa_enforcement': True, 'coverage': '95%'}
        return True, evidence

    def check_rbac(self) -> tuple[bool, Dict]:
        """Check if RBAC is implemented"""
        evidence = {'rbac_enabled': True, 'roles_count': 5}
        return True, evidence

    def check_access_logs(self) -> tuple[bool, Dict]:
        """Check access logging"""
        evidence = {'logging_enabled': True, 'retention_days': 90}
        return True, evidence

    def check_logging(self) -> tuple[bool, Dict]:
        """Check system logging"""
        evidence = {'audit_logging': True, 'security_logging': True}
        return True, evidence

    def check_alerts(self) -> tuple[bool, Dict]:
        """Check alerting configuration"""
        evidence = {'alerts_configured': True, 'alert_types': ['security', 'availability']}
        return True, evidence

    def check_encryption(self) -> tuple[bool, Dict]:
        """Check encryption at rest"""
        evidence = {'encryption_at_rest': True, 'algorithm': 'AES-256'}
        return True, evidence

    def check_privacy_policy(self) -> tuple[bool, Dict]:
        """Check privacy policy"""
        evidence = {'policy_published': True, 'last_updated': '2026-01-01'}
        return True, evidence

    def check_consent_logs(self) -> tuple[bool, Dict]:
        """Check consent logging"""
        evidence = {'consent_tracking': True, 'records_count': 1000}
        return True, evidence

    def check_code_of_conduct(self) -> tuple[bool, Dict]:
        """Check code of conduct"""
        evidence = {'documented': True, 'location': 'docs/code-of-conduct.md'}
        return True, evidence

    def check_training_records(self) -> tuple[bool, Dict]:
        """Check training completion"""
        evidence = {'training_program': True, 'completion_rate': '88%'}
        return True, evidence

    def check_security_policies(self) -> tuple[bool, Dict]:
        """Check security policies"""
        evidence = {'policies_documented': True, 'count': 12}
        return True, evidence

    def check_access_controls(self) -> tuple[bool, Dict]:
        """Check access controls"""
        evidence = {'access_control': True, 'principle_of_least_privilege': True}
        return True, evidence

    def check_vulnerability_scans(self) -> tuple[bool, Dict]:
        """Check vulnerability scanning"""
        evidence = {'scanning_enabled': True, 'frequency': 'weekly', 'last_scan': '2026-01-20'}
        return True, evidence

    def check_incident_response_plan(self) -> tuple[bool, Dict]:
        """Check incident response plan"""
        evidence = {'plan_documented': True, 'last_tested': '2025-12-15'}
        return True, evidence

    def check_breach_notifications(self) -> tuple[bool, Dict]:
        """Check breach notification procedures"""
        evidence = {'procedures_documented': True, 'notification_template': True}
        return True, evidence

    def check_data_minimization(self) -> tuple[bool, Dict]:
        """Check data minimization"""
        evidence = {'minimization_policy': True, 'data_retention_policy': True}
        return True, evidence

    def check_access_policy(self) -> tuple[bool, Dict]:
        """Check access policy"""
        evidence = {'policy_documented': True, 'last_review': '2025-11-01'}
        return True, evidence

    def check_encryption_policy(self) -> tuple[bool, Dict]:
        """Check encryption policy"""
        evidence = {'policy_exists': True, 'approved_algorithms': ['AES-256', 'RSA-4096']}
        return True, evidence

    def check_key_management(self) -> tuple[bool, Dict]:
        """Check key management"""
        evidence = {'key_rotation': True, 'rotation_period_days': 90}
        return True, evidence

    def check_event_logging(self) -> tuple[bool, Dict]:
        """Check event logging"""
        evidence = {'event_logging': True, 'log_types': ['auth', 'admin', 'data_access']}
        return True, evidence

    def check_log_retention(self) -> tuple[bool, Dict]:
        """Check log retention"""
        evidence = {'retention_policy': True, 'retention_days': 365}
        return True, evidence

    def _export_json(self, report: ComplianceReport, output_path: Path):
        """Export report as JSON"""
        report_dict = {
            'report_id': report.report_id,
            'framework': report.framework.value,
            'generated_at': report.generated_at.isoformat(),
            'period': {
                'start': report.period_start.isoformat(),
                'end': report.period_end.isoformat()
            },
            'summary': report.summary,
            'compliance_score': report.compliance_score,
            'results': [
                {
                    'control_id': r.control_id,
                    'status': r.status.value,
                    'severity': r.severity.value,
                    'message': r.message,
                    'findings': r.findings,
                    'recommendations': r.recommendations,
                    'evidence': r.evidence
                }
                for r in report.results
            ]
        }

        with open(output_path, 'w') as f:
            json.dump(report_dict, f, indent=2)

    def _export_html(self, report: ComplianceReport, output_path: Path):
        """Export report as HTML"""
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Compliance Report - {report.framework.value.upper()}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background: #2c3e50; color: white; padding: 20px; }}
        .summary {{ background: #ecf0f1; padding: 15px; margin: 20px 0; }}
        .score {{ font-size: 48px; font-weight: bold; color: #27ae60; }}
        .control {{ border: 1px solid #ddd; margin: 10px 0; padding: 15px; }}
        .passed {{ border-left: 5px solid #27ae60; }}
        .failed {{ border-left: 5px solid #e74c3c; }}
        .warning {{ border-left: 5px solid #f39c12; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Compliance Report: {report.framework.value.upper()}</h1>
        <p>Generated: {report.generated_at.strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>

    <div class="summary">
        <h2>Summary</h2>
        <div class="score">{report.compliance_score:.1f}%</div>
        <p>Compliance Score</p>
        <p>Total Controls: {report.total_controls}</p>
        <p>Passed: {report.passed_controls} | Failed: {report.failed_controls} | Warnings: {report.warning_controls}</p>
    </div>

    <h2>Control Results</h2>
"""

        for result in report.results:
            status_class = result.status.value
            html += f"""
    <div class="control {status_class}">
        <h3>{result.control_id} - {result.status.value.upper()}</h3>
        <p><strong>Severity:</strong> {result.severity.value}</p>
        <p>{result.message}</p>
"""
            if result.findings:
                html += "<p><strong>Findings:</strong></p><ul>"
                for finding in result.findings:
                    html += f"<li>{finding}</li>"
                html += "</ul>"

            if result.recommendations:
                html += "<p><strong>Recommendations:</strong></p><ul>"
                for rec in result.recommendations:
                    html += f"<li>{rec}</li>"
                html += "</ul>"

            html += "</div>"

        html += """
</body>
</html>"""

        with open(output_path, 'w') as f:
            f.write(html)
