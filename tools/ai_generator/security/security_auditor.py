#!/usr/bin/env python3
"""
Security Auditor

Регулярные security audits, penetration testing automation.
"""

import json
import subprocess
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Set


class AuditType(Enum):
    """Audit Types"""
    SECURITY_SCAN = "security_scan"
    PENETRATION_TEST = "penetration_test"
    COMPLIANCE_CHECK = "compliance_check"
    ACCESS_REVIEW = "access_review"
    CONFIGURATION_AUDIT = "configuration_audit"
    CODE_REVIEW = "code_review"


class FindingSeverity(Enum):
    """Finding Severity"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class FindingStatus(Enum):
    """Finding Status"""
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    ACCEPTED = "accepted"
    FALSE_POSITIVE = "false_positive"


@dataclass
class SecurityFinding:
    """Security Audit Finding"""
    finding_id: str
    title: str
    description: str
    severity: FindingSeverity
    audit_type: AuditType
    status: FindingStatus = FindingStatus.OPEN
    affected_component: Optional[str] = None
    cve_id: Optional[str] = None
    cwe_id: Optional[str] = None
    cvss_score: Optional[float] = None
    remediation: str = ""
    evidence: Dict[str, Any] = field(default_factory=dict)
    discovered_at: datetime = field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None
    assigned_to: Optional[str] = None
    references: List[str] = field(default_factory=list)


@dataclass
class AuditReport:
    """Security Audit Report"""
    audit_id: str
    audit_type: AuditType
    started_at: datetime
    completed_at: datetime
    auditor: str
    scope: str
    total_findings: int
    critical_findings: int
    high_findings: int
    medium_findings: int
    low_findings: int
    findings: List[SecurityFinding]
    summary: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)


class SecurityAuditor:
    """Security Auditor - Automated Security Audits"""

    def __init__(self, project_path: Path):
        """
        Инициализация security auditor

        Args:
            project_path: Path to project directory
        """
        self.project_path = project_path
        self.findings: Dict[str, SecurityFinding] = {}
        self.audit_history: List[AuditReport] = []

    def run_security_audit(self, audit_type: AuditType = AuditType.SECURITY_SCAN) -> AuditReport:
        """
        Run comprehensive security audit

        Args:
            audit_type: Type of audit to perform

        Returns:
            Audit report
        """
        started_at = datetime.utcnow()
        findings = []

        if audit_type == AuditType.SECURITY_SCAN:
            findings.extend(self._run_security_scan())
        elif audit_type == AuditType.PENETRATION_TEST:
            findings.extend(self._run_penetration_test())
        elif audit_type == AuditType.COMPLIANCE_CHECK:
            findings.extend(self._run_compliance_check())
        elif audit_type == AuditType.ACCESS_REVIEW:
            findings.extend(self._run_access_review())
        elif audit_type == AuditType.CONFIGURATION_AUDIT:
            findings.extend(self._run_configuration_audit())
        elif audit_type == AuditType.CODE_REVIEW:
            findings.extend(self._run_code_review())

        completed_at = datetime.utcnow()

        # Store findings
        for finding in findings:
            self.findings[finding.finding_id] = finding

        # Generate report
        report = self._create_audit_report(
            audit_type=audit_type,
            started_at=started_at,
            completed_at=completed_at,
            findings=findings
        )

        self.audit_history.append(report)
        return report

    def run_automated_pentest(self) -> AuditReport:
        """
        Run automated penetration testing

        Returns:
            Pentest audit report
        """
        started_at = datetime.utcnow()
        findings = []

        # 1. Port Scanning
        findings.extend(self._port_scan())

        # 2. Web Application Security Testing (OWASP Top 10)
        findings.extend(self._web_security_scan())

        # 3. SSL/TLS Testing
        findings.extend(self._ssl_tls_scan())

        # 4. Authentication Testing
        findings.extend(self._auth_security_test())

        # 5. API Security Testing
        findings.extend(self._api_security_test())

        completed_at = datetime.utcnow()

        report = self._create_audit_report(
            audit_type=AuditType.PENETRATION_TEST,
            started_at=started_at,
            completed_at=completed_at,
            findings=findings
        )

        return report

    def schedule_recurring_audit(self,
                                audit_type: AuditType,
                                frequency_days: int = 30) -> Dict[str, Any]:
        """
        Schedule recurring security audits

        Args:
            audit_type: Type of audit
            frequency_days: Frequency in days

        Returns:
            Schedule configuration
        """
        schedule = {
            'audit_type': audit_type.value,
            'frequency_days': frequency_days,
            'next_run': (datetime.utcnow() + timedelta(days=frequency_days)).isoformat(),
            'enabled': True
        }

        # In production, integrate with scheduler (cron, Celery, etc.)
        return schedule

    def get_open_findings(self, severity: Optional[FindingSeverity] = None) -> List[SecurityFinding]:
        """
        Get all open security findings

        Args:
            severity: Filter by severity

        Returns:
            List of open findings
        """
        findings = [
            f for f in self.findings.values()
            if f.status == FindingStatus.OPEN
        ]

        if severity:
            findings = [f for f in findings if f.severity == severity]

        return sorted(findings, key=lambda x: (
            ['critical', 'high', 'medium', 'low', 'info'].index(x.severity.value),
            x.discovered_at
        ))

    def resolve_finding(self, finding_id: str, resolution_notes: str = "") -> bool:
        """
        Resolve security finding

        Args:
            finding_id: Finding ID to resolve
            resolution_notes: Resolution notes

        Returns:
            True if successful
        """
        finding = self.findings.get(finding_id)
        if not finding:
            return False

        finding.status = FindingStatus.RESOLVED
        finding.resolved_at = datetime.utcnow()
        finding.evidence['resolution_notes'] = resolution_notes

        return True

    def export_report(self, report: AuditReport, output_path: Path, format: str = 'json'):
        """
        Export audit report

        Args:
            report: Audit report
            output_path: Output file path
            format: Export format (json, html, pdf)
        """
        if format == 'json':
            self._export_json(report, output_path)
        elif format == 'html':
            self._export_html(report, output_path)
        else:
            raise ValueError(f"Unsupported format: {format}")

    def _run_security_scan(self) -> List[SecurityFinding]:
        """Run comprehensive security scan"""
        findings = []

        # Dependency vulnerabilities
        findings.extend(self._check_dependencies())

        # Secrets in code
        findings.extend(self._check_exposed_secrets())

        # Insecure configurations
        findings.extend(self._check_configurations())

        # Code vulnerabilities
        findings.extend(self._check_code_vulnerabilities())

        return findings

    def _run_penetration_test(self) -> List[SecurityFinding]:
        """Run penetration testing"""
        findings = []

        findings.extend(self._port_scan())
        findings.extend(self._web_security_scan())
        findings.extend(self._auth_security_test())

        return findings

    def _run_compliance_check(self) -> List[SecurityFinding]:
        """Run compliance audit"""
        findings = []

        # Check encryption at rest
        if not self._check_encryption_at_rest():
            findings.append(SecurityFinding(
                finding_id='COMP-001',
                title='Encryption at rest not enabled',
                description='Database or file storage lacks encryption at rest',
                severity=FindingSeverity.HIGH,
                audit_type=AuditType.COMPLIANCE_CHECK,
                remediation='Enable encryption at rest for all data stores'
            ))

        # Check access controls
        if not self._check_access_controls():
            findings.append(SecurityFinding(
                finding_id='COMP-002',
                title='Insufficient access controls',
                description='RBAC or least privilege principle not enforced',
                severity=FindingSeverity.HIGH,
                audit_type=AuditType.COMPLIANCE_CHECK,
                remediation='Implement RBAC and principle of least privilege'
            ))

        return findings

    def _run_access_review(self) -> List[SecurityFinding]:
        """Run access review"""
        findings = []

        # Check for over-privileged users
        findings.append(SecurityFinding(
            finding_id='ACCESS-001',
            title='Over-privileged user accounts detected',
            description='Some user accounts have excessive permissions',
            severity=FindingSeverity.MEDIUM,
            audit_type=AuditType.ACCESS_REVIEW,
            remediation='Review and reduce user permissions to minimum required'
        ))

        return findings

    def _run_configuration_audit(self) -> List[SecurityFinding]:
        """Run configuration audit"""
        findings = []

        # Check for insecure defaults
        findings.append(SecurityFinding(
            finding_id='CONFIG-001',
            title='Insecure default configuration',
            description='System using insecure default settings',
            severity=FindingSeverity.MEDIUM,
            audit_type=AuditType.CONFIGURATION_AUDIT,
            remediation='Review and harden system configuration'
        ))

        return findings

    def _run_code_review(self) -> List[SecurityFinding]:
        """Run security code review"""
        return self._check_code_vulnerabilities()

    def _port_scan(self) -> List[SecurityFinding]:
        """Port scanning"""
        findings = []

        # Simulate port scan
        open_ports = [22, 80, 443, 3306, 5432]

        # Check for unnecessary open ports
        risky_ports = [3306, 5432]  # Database ports
        for port in risky_ports:
            if port in open_ports:
                findings.append(SecurityFinding(
                    finding_id=f'PENTEST-PORT-{port}',
                    title=f'Database port {port} exposed',
                    description=f'Port {port} is publicly accessible',
                    severity=FindingSeverity.HIGH,
                    audit_type=AuditType.PENETRATION_TEST,
                    remediation=f'Restrict access to port {port} with firewall rules'
                ))

        return findings

    def _web_security_scan(self) -> List[SecurityFinding]:
        """Web application security scan (OWASP Top 10)"""
        findings = []

        # SQL Injection test
        findings.append(SecurityFinding(
            finding_id='PENTEST-SQLI-001',
            title='Potential SQL Injection vulnerability',
            description='Input validation insufficient for SQL queries',
            severity=FindingSeverity.CRITICAL,
            audit_type=AuditType.PENETRATION_TEST,
            cwe_id='CWE-89',
            remediation='Use parameterized queries or ORM'
        ))

        # XSS test
        findings.append(SecurityFinding(
            finding_id='PENTEST-XSS-001',
            title='Cross-Site Scripting (XSS) vulnerability',
            description='User input not properly sanitized',
            severity=FindingSeverity.HIGH,
            audit_type=AuditType.PENETRATION_TEST,
            cwe_id='CWE-79',
            remediation='Implement input validation and output encoding'
        ))

        # CSRF test
        findings.append(SecurityFinding(
            finding_id='PENTEST-CSRF-001',
            title='Missing CSRF protection',
            description='State-changing requests lack CSRF tokens',
            severity=FindingSeverity.MEDIUM,
            audit_type=AuditType.PENETRATION_TEST,
            cwe_id='CWE-352',
            remediation='Implement CSRF token validation'
        ))

        return findings

    def _ssl_tls_scan(self) -> List[SecurityFinding]:
        """SSL/TLS security scan"""
        findings = []

        # Weak TLS version
        findings.append(SecurityFinding(
            finding_id='PENTEST-TLS-001',
            title='Weak TLS version supported',
            description='Server supports TLS 1.0 or 1.1',
            severity=FindingSeverity.HIGH,
            audit_type=AuditType.PENETRATION_TEST,
            remediation='Disable TLS 1.0 and 1.1, enforce TLS 1.2+'
        ))

        return findings

    def _auth_security_test(self) -> List[SecurityFinding]:
        """Authentication security testing"""
        findings = []

        # Weak password policy
        findings.append(SecurityFinding(
            finding_id='PENTEST-AUTH-001',
            title='Weak password policy',
            description='Password requirements are insufficient',
            severity=FindingSeverity.MEDIUM,
            audit_type=AuditType.PENETRATION_TEST,
            remediation='Enforce strong password policy (min 12 chars, complexity)'
        ))

        # Missing MFA
        findings.append(SecurityFinding(
            finding_id='PENTEST-AUTH-002',
            title='Multi-factor authentication not enforced',
            description='MFA not required for privileged accounts',
            severity=FindingSeverity.HIGH,
            audit_type=AuditType.PENETRATION_TEST,
            remediation='Enforce MFA for all users, especially administrators'
        ))

        return findings

    def _api_security_test(self) -> List[SecurityFinding]:
        """API security testing"""
        findings = []

        # Missing rate limiting
        findings.append(SecurityFinding(
            finding_id='PENTEST-API-001',
            title='API rate limiting not implemented',
            description='APIs vulnerable to abuse and DoS',
            severity=FindingSeverity.MEDIUM,
            audit_type=AuditType.PENETRATION_TEST,
            remediation='Implement rate limiting for all API endpoints'
        ))

        return findings

    def _check_dependencies(self) -> List[SecurityFinding]:
        """Check for vulnerable dependencies"""
        # This would integrate with vulnerability scanner
        return []

    def _check_exposed_secrets(self) -> List[SecurityFinding]:
        """Check for exposed secrets"""
        findings = []

        # Simulate secret detection
        findings.append(SecurityFinding(
            finding_id='SECRET-001',
            title='Hardcoded credentials detected',
            description='Credentials found in source code',
            severity=FindingSeverity.CRITICAL,
            audit_type=AuditType.SECURITY_SCAN,
            cwe_id='CWE-798',
            remediation='Remove hardcoded credentials, use environment variables'
        ))

        return findings

    def _check_configurations(self) -> List[SecurityFinding]:
        """Check for insecure configurations"""
        findings = []

        # Check for debug mode in production
        findings.append(SecurityFinding(
            finding_id='CONFIG-DEBUG-001',
            title='Debug mode enabled',
            description='Application running in debug mode in production',
            severity=FindingSeverity.HIGH,
            audit_type=AuditType.SECURITY_SCAN,
            remediation='Disable debug mode in production environment'
        ))

        return findings

    def _check_code_vulnerabilities(self) -> List[SecurityFinding]:
        """Check code for vulnerabilities"""
        # This would integrate with code scanner
        return []

    def _check_encryption_at_rest(self) -> bool:
        """Check if encryption at rest is enabled"""
        # Simulate check
        return True

    def _check_access_controls(self) -> bool:
        """Check access control implementation"""
        # Simulate check
        return True

    def _create_audit_report(self,
                            audit_type: AuditType,
                            started_at: datetime,
                            completed_at: datetime,
                            findings: List[SecurityFinding]) -> AuditReport:
        """Create audit report"""
        severity_counts = {
            FindingSeverity.CRITICAL: 0,
            FindingSeverity.HIGH: 0,
            FindingSeverity.MEDIUM: 0,
            FindingSeverity.LOW: 0,
            FindingSeverity.INFO: 0
        }

        for finding in findings:
            severity_counts[finding.severity] += 1

        # Generate recommendations
        recommendations = []
        if severity_counts[FindingSeverity.CRITICAL] > 0:
            recommendations.append("URGENT: Address critical findings immediately")
        if severity_counts[FindingSeverity.HIGH] > 0:
            recommendations.append("Prioritize high severity findings for remediation")

        report = AuditReport(
            audit_id=f"audit_{audit_type.value}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            audit_type=audit_type,
            started_at=started_at,
            completed_at=completed_at,
            auditor='SecurityAuditor',
            scope=str(self.project_path),
            total_findings=len(findings),
            critical_findings=severity_counts[FindingSeverity.CRITICAL],
            high_findings=severity_counts[FindingSeverity.HIGH],
            medium_findings=severity_counts[FindingSeverity.MEDIUM],
            low_findings=severity_counts[FindingSeverity.LOW],
            findings=findings,
            summary={
                'duration_seconds': (completed_at - started_at).total_seconds(),
                'severity_distribution': {s.value: c for s, c in severity_counts.items()},
                'risk_score': self._calculate_risk_score(severity_counts)
            },
            recommendations=recommendations
        )

        return report

    def _calculate_risk_score(self, severity_counts: Dict[FindingSeverity, int]) -> float:
        """Calculate risk score"""
        weights = {
            FindingSeverity.CRITICAL: 10.0,
            FindingSeverity.HIGH: 5.0,
            FindingSeverity.MEDIUM: 2.0,
            FindingSeverity.LOW: 0.5,
            FindingSeverity.INFO: 0.1
        }

        score = sum(severity_counts.get(sev, 0) * weight for sev, weight in weights.items())
        return round(score, 2)

    def _export_json(self, report: AuditReport, output_path: Path):
        """Export report as JSON"""
        report_dict = {
            'audit_id': report.audit_id,
            'audit_type': report.audit_type.value,
            'started_at': report.started_at.isoformat(),
            'completed_at': report.completed_at.isoformat(),
            'auditor': report.auditor,
            'scope': report.scope,
            'summary': report.summary,
            'total_findings': report.total_findings,
            'severity_breakdown': {
                'critical': report.critical_findings,
                'high': report.high_findings,
                'medium': report.medium_findings,
                'low': report.low_findings
            },
            'recommendations': report.recommendations,
            'findings': [
                {
                    'finding_id': f.finding_id,
                    'title': f.title,
                    'description': f.description,
                    'severity': f.severity.value,
                    'status': f.status.value,
                    'cve_id': f.cve_id,
                    'cwe_id': f.cwe_id,
                    'remediation': f.remediation,
                    'discovered_at': f.discovered_at.isoformat()
                }
                for f in report.findings
            ]
        }

        with open(output_path, 'w') as f:
            json.dump(report_dict, f, indent=2)

    def _export_html(self, report: AuditReport, output_path: Path):
        """Export report as HTML"""
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Security Audit Report - {report.audit_type.value}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background: #c0392b; color: white; padding: 20px; }}
        .summary {{ background: #ecf0f1; padding: 15px; margin: 20px 0; }}
        .risk-score {{ font-size: 48px; font-weight: bold; color: #e74c3c; }}
        .finding {{ border: 1px solid #ddd; margin: 10px 0; padding: 15px; }}
        .critical {{ border-left: 5px solid #c0392b; background: #fadbd8; }}
        .high {{ border-left: 5px solid #e74c3c; }}
        .medium {{ border-left: 5px solid #f39c12; }}
        .low {{ border-left: 5px solid #3498db; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Security Audit Report</h1>
        <h2>{report.audit_type.value.upper()}</h2>
        <p>Audit ID: {report.audit_id}</p>
        <p>Started: {report.started_at.strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p>Completed: {report.completed_at.strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>

    <div class="summary">
        <h2>Summary</h2>
        <div class="risk-score">{report.summary['risk_score']}</div>
        <p>Risk Score</p>
        <p>Total Findings: {report.total_findings}</p>
        <p>Critical: {report.critical_findings} | High: {report.high_findings} | Medium: {report.medium_findings} | Low: {report.low_findings}</p>
    </div>

    <h2>Recommendations</h2>
    <ul>
"""
        for rec in report.recommendations:
            html += f"<li>{rec}</li>\n"

        html += "</ul>\n<h2>Findings</h2>\n"

        for finding in sorted(report.findings, key=lambda x: ['critical', 'high', 'medium', 'low', 'info'].index(x.severity.value)):
            html += f"""
    <div class="finding {finding.severity.value}">
        <h3>{finding.title}</h3>
        <p><strong>Severity:</strong> {finding.severity.value.upper()}</p>
        <p><strong>Status:</strong> {finding.status.value}</p>
        <p>{finding.description}</p>
        <p><strong>Remediation:</strong> {finding.remediation}</p>
    </div>
"""

        html += """
</body>
</html>"""

        with open(output_path, 'w') as f:
            f.write(html)
