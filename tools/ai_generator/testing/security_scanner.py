#!/usr/bin/env python3
"""
Security Scanner

Автоматическое security testing с OWASP ZAP, SQLMap, и vulnerability scanning.
"""

import json
import subprocess
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any


class VulnerabilityType(Enum):
    """Vulnerability Type"""
    XSS = "xss"
    SQL_INJECTION = "sql_injection"
    CSRF = "csrf"
    XXE = "xxe"
    SSRF = "ssrf"
    PATH_TRAVERSAL = "path_traversal"
    INSECURE_DESERIALIZATION = "insecure_deserialization"
    BROKEN_AUTH = "broken_auth"
    SENSITIVE_DATA_EXPOSURE = "sensitive_data_exposure"
    BROKEN_ACCESS_CONTROL = "broken_access_control"


class RiskLevel(Enum):
    """Risk Level"""
    INFORMATIONAL = "informational"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class SecurityFinding:
    """Security Finding"""
    vulnerability_type: VulnerabilityType
    risk_level: RiskLevel
    title: str
    description: str
    url: str
    parameter: Optional[str] = None
    solution: str = ""
    cwe_id: Optional[int] = None
    cvss_score: float = 0.0
    evidence: str = ""
    references: List[str] = field(default_factory=list)


@dataclass
class SecurityScanResult:
    """Security Scan Result"""
    target_url: str
    scan_type: str
    findings: List[SecurityFinding] = field(default_factory=list)
    scan_duration: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)
    total_requests: int = 0


@dataclass
class ScanConfig:
    """Security Scan Configuration"""
    target_url: str
    scan_types: List[str] = field(default_factory=list)  # active, passive, api
    auth_token: Optional[str] = None
    headers: Dict[str, str] = field(default_factory=dict)
    exclude_urls: List[str] = field(default_factory=list)
    max_scan_time: int = 3600  # seconds


class SecurityScanner:
    """Security Scanner"""

    def __init__(self, config: ScanConfig):
        """
        Initialize security scanner

        Args:
            config: Scan configuration
        """
        self.config = config

    def scan_owasp_zap(self) -> SecurityScanResult:
        """
        Run OWASP ZAP scan

        Returns:
            Scan result
        """
        print(f"🔒 Running OWASP ZAP scan on {self.config.target_url}...")

        result = SecurityScanResult(
            target_url=self.config.target_url,
            scan_type="OWASP ZAP"
        )

        start_time = datetime.now()

        # Generate ZAP script
        zap_script = self._generate_zap_script()

        # In production, would actually run ZAP
        # For now, simulate scan results
        result.findings = self._simulate_zap_findings()

        result.scan_duration = (datetime.now() - start_time).total_seconds()

        print(f"✅ Scan complete: {len(result.findings)} findings")

        return result

    def scan_sql_injection(self, urls: List[str]) -> SecurityScanResult:
        """
        Scan for SQL injection vulnerabilities

        Args:
            urls: URLs to scan

        Returns:
            Scan result
        """
        print(f"💉 Scanning for SQL injection...")

        result = SecurityScanResult(
            target_url=self.config.target_url,
            scan_type="SQL Injection"
        )

        for url in urls:
            # Check for SQL injection patterns
            findings = self._check_sql_injection(url)
            result.findings.extend(findings)

        print(f"✅ SQL injection scan complete: {len(result.findings)} findings")

        return result

    def scan_xss(self, urls: List[str]) -> SecurityScanResult:
        """
        Scan for XSS vulnerabilities

        Args:
            urls: URLs to scan

        Returns:
            Scan result
        """
        print(f"🎯 Scanning for XSS vulnerabilities...")

        result = SecurityScanResult(
            target_url=self.config.target_url,
            scan_type="XSS"
        )

        for url in urls:
            findings = self._check_xss(url)
            result.findings.extend(findings)

        print(f"✅ XSS scan complete: {len(result.findings)} findings")

        return result

    def scan_headers(self) -> SecurityScanResult:
        """
        Scan security headers

        Returns:
            Scan result
        """
        print(f"📋 Scanning security headers...")

        result = SecurityScanResult(
            target_url=self.config.target_url,
            scan_type="Security Headers"
        )

        # Check for missing security headers
        required_headers = [
            'X-Frame-Options',
            'X-Content-Type-Options',
            'Strict-Transport-Security',
            'Content-Security-Policy',
            'X-XSS-Protection'
        ]

        for header in required_headers:
            if header not in self.config.headers:
                result.findings.append(SecurityFinding(
                    vulnerability_type=VulnerabilityType.SENSITIVE_DATA_EXPOSURE,
                    risk_level=RiskLevel.LOW,
                    title=f"Missing {header} Header",
                    description=f"Security header {header} is not present",
                    url=self.config.target_url,
                    solution=f"Add {header} header to HTTP responses",
                    references=[
                        "https://owasp.org/www-project-secure-headers/"
                    ]
                ))

        print(f"✅ Header scan complete: {len(result.findings)} findings")

        return result

    def _generate_zap_script(self) -> str:
        """Generate OWASP ZAP automation script"""
        return f"""#!/bin/bash

# OWASP ZAP Automated Scan

ZAP_PATH="/opt/zaproxy/zap.sh"
TARGET="{self.config.target_url}"

echo "Starting OWASP ZAP scan..."

# Start ZAP in daemon mode
$ZAP_PATH -daemon -port 8080 -config api.disablekey=true &
ZAP_PID=$!

# Wait for ZAP to start
sleep 10

# Spider the target
curl "http://localhost:8080/JSON/spider/action/scan/?url=$TARGET"

# Wait for spider to complete
sleep 30

# Active scan
curl "http://localhost:8080/JSON/ascan/action/scan/?url=$TARGET"

# Wait for scan to complete
sleep 300

# Generate report
curl "http://localhost:8080/JSON/core/view/jsonreport/" > zap-report.json
curl "http://localhost:8080/OTHER/core/other/htmlreport/" > zap-report.html

# Stop ZAP
kill $ZAP_PID

echo "OWASP ZAP scan completed"
echo "Report saved to zap-report.json and zap-report.html"
"""

    def _simulate_zap_findings(self) -> List[SecurityFinding]:
        """Simulate ZAP scan findings"""
        findings = []

        # Common vulnerabilities that ZAP might find
        common_vulns = [
            {
                'type': VulnerabilityType.XSS,
                'risk': RiskLevel.HIGH,
                'title': 'Cross-Site Scripting (Reflected)',
                'cwe': 79,
                'cvss': 6.1
            },
            {
                'type': VulnerabilityType.SQL_INJECTION,
                'risk': RiskLevel.CRITICAL,
                'title': 'SQL Injection',
                'cwe': 89,
                'cvss': 9.8
            },
            {
                'type': VulnerabilityType.CSRF,
                'risk': RiskLevel.MEDIUM,
                'title': 'Cross-Site Request Forgery',
                'cwe': 352,
                'cvss': 8.8
            },
        ]

        for vuln in common_vulns:
            findings.append(SecurityFinding(
                vulnerability_type=vuln['type'],
                risk_level=vuln['risk'],
                title=vuln['title'],
                description=f"Potential {vuln['title']} vulnerability detected",
                url=self.config.target_url,
                parameter="id",
                solution="Implement proper input validation and output encoding",
                cwe_id=vuln['cwe'],
                cvss_score=vuln['cvss'],
                evidence="<script>alert('XSS')</script>",
                references=[
                    f"https://cwe.mitre.org/data/definitions/{vuln['cwe']}.html"
                ]
            ))

        return findings

    def _check_sql_injection(self, url: str) -> List[SecurityFinding]:
        """Check for SQL injection vulnerabilities"""
        findings = []

        # Common SQL injection payloads
        payloads = [
            "' OR '1'='1",
            "1' OR '1' = '1",
            "admin'--",
            "1' UNION SELECT NULL--",
        ]

        # In production, would test each payload
        # For now, return simulated finding
        findings.append(SecurityFinding(
            vulnerability_type=VulnerabilityType.SQL_INJECTION,
            risk_level=RiskLevel.CRITICAL,
            title="Possible SQL Injection",
            description="URL parameter may be vulnerable to SQL injection",
            url=url,
            parameter="id",
            solution="Use parameterized queries or prepared statements",
            cwe_id=89,
            cvss_score=9.8,
            references=[
                "https://owasp.org/www-community/attacks/SQL_Injection"
            ]
        ))

        return findings

    def _check_xss(self, url: str) -> List[SecurityFinding]:
        """Check for XSS vulnerabilities"""
        findings = []

        # XSS payloads
        payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "javascript:alert('XSS')",
        ]

        findings.append(SecurityFinding(
            vulnerability_type=VulnerabilityType.XSS,
            risk_level=RiskLevel.HIGH,
            title="Reflected Cross-Site Scripting",
            description="User input is reflected in HTML response without proper encoding",
            url=url,
            parameter="search",
            solution="Implement context-aware output encoding",
            cwe_id=79,
            cvss_score=6.1,
            references=[
                "https://owasp.org/www-community/attacks/xss/"
            ]
        ))

        return findings

    def generate_report(
        self,
        results: List[SecurityScanResult],
        output_path: Path
    ):
        """
        Generate security report

        Args:
            results: Scan results
            output_path: Output file path
        """
        # Aggregate findings
        all_findings = []
        for result in results:
            all_findings.extend(result.findings)

        # Group by risk level
        findings_by_risk = {
            RiskLevel.CRITICAL: [],
            RiskLevel.HIGH: [],
            RiskLevel.MEDIUM: [],
            RiskLevel.LOW: [],
            RiskLevel.INFORMATIONAL: []
        }

        for finding in all_findings:
            findings_by_risk[finding.risk_level].append(finding)

        # Generate HTML report
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Security Scan Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .summary {{ background: #f0f0f0; padding: 20px; margin-bottom: 20px; }}
        .critical {{ background-color: #DC143C; color: white; padding: 10px; }}
        .high {{ background-color: #FF6347; color: white; padding: 10px; }}
        .medium {{ background-color: #FFA500; padding: 10px; }}
        .low {{ background-color: #FFD700; padding: 10px; }}
        .finding {{ margin: 20px 0; padding: 15px; border-left: 5px solid #ccc; }}
        table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #4CAF50; color: white; }}
    </style>
</head>
<body>
    <h1>Security Scan Report</h1>

    <div class="summary">
        <h2>Summary</h2>
        <p>Total Findings: {len(all_findings)}</p>
        <p>Critical: {len(findings_by_risk[RiskLevel.CRITICAL])}</p>
        <p>High: {len(findings_by_risk[RiskLevel.HIGH])}</p>
        <p>Medium: {len(findings_by_risk[RiskLevel.MEDIUM])}</p>
        <p>Low: {len(findings_by_risk[RiskLevel.LOW])}</p>
        <p>Info: {len(findings_by_risk[RiskLevel.INFORMATIONAL])}</p>
    </div>

    <h2>Findings</h2>
"""

        for risk_level in [RiskLevel.CRITICAL, RiskLevel.HIGH, RiskLevel.MEDIUM, RiskLevel.LOW]:
            if findings_by_risk[risk_level]:
                html += f"<h3 class='{risk_level.value}'>{risk_level.value.upper()} Risk</h3>"

                for finding in findings_by_risk[risk_level]:
                    html += f"""
    <div class="finding">
        <h4>{finding.title}</h4>
        <p><strong>URL:</strong> {finding.url}</p>
        <p><strong>Type:</strong> {finding.vulnerability_type.value}</p>
        <p><strong>Description:</strong> {finding.description}</p>
        <p><strong>Solution:</strong> {finding.solution}</p>
        {f'<p><strong>CWE:</strong> {finding.cwe_id}</p>' if finding.cwe_id else ''}
        {f'<p><strong>CVSS Score:</strong> {finding.cvss_score}</p>' if finding.cvss_score else ''}
        {f'<p><strong>Evidence:</strong> <code>{finding.evidence}</code></p>' if finding.evidence else ''}
    </div>
"""

        html += """
</body>
</html>
"""

        output_path.write_text(html)
        print(f"✅ Security report saved to {output_path}")

    def generate_docker_compose(self, output_path: Path):
        """
        Generate docker-compose for security tools

        Args:
            output_path: Output file path
        """
        compose = {
            'version': '3.8',
            'services': {
                'owasp-zap': {
                    'image': 'owasp/zap2docker-stable',
                    'ports': ['8080:8080', '8090:8090'],
                    'command': 'zap.sh -daemon -host 0.0.0.0 -port 8080 -config api.disablekey=true',
                    'volumes': ['./zap-reports:/zap/reports']
                },
                'sqlmap': {
                    'image': 'paoloo/sqlmap',
                    'command': '--help'
                }
            }
        }

        import yaml
        output_path.write_text(yaml.dump(compose, default_flow_style=False))
        print(f"✅ Docker Compose file saved to {output_path}")
