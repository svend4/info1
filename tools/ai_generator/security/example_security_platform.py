#!/usr/bin/env python3
"""
Example: Complete Security Platform Integration

Демонстрация использования всех security модулей вместе.
"""

from pathlib import Path
from datetime import datetime

from sso_integration import SSOIntegration, SSOConfig, SSOProvider
from encryption_manager import EncryptionManager, EncryptionAlgorithm
from compliance_automation import ComplianceAutomation, ComplianceFramework
from vulnerability_scanner import VulnerabilityScanner
from secrets_manager import SecretsManager, SecretType
from security_auditor import SecurityAuditor, AuditType


class SecurityPlatform:
    """Complete Security Platform"""

    def __init__(self, project_path: Path):
        """
        Инициализация security platform

        Args:
            project_path: Path to project
        """
        self.project_path = project_path

        # Initialize all security components
        self.sso = self._setup_sso()
        self.encryption = self._setup_encryption()
        self.compliance = self._setup_compliance()
        self.scanner = self._setup_scanner()
        self.secrets = self._setup_secrets()
        self.auditor = self._setup_auditor()

        print("✅ Security Platform initialized")

    def _setup_sso(self) -> SSOIntegration:
        """Setup SSO integration"""
        config = SSOConfig(
            provider=SSOProvider.OKTA,
            entity_id="https://myapp.example.com",
            sso_url="https://company.okta.com/app/myapp/sso/saml",
            slo_url="https://company.okta.com/app/myapp/slo/saml",
            x509_cert="<IDP_CERTIFICATE>",
            sign_requests=True,
            encrypt_assertions=True
        )
        return SSOIntegration(config)

    def _setup_encryption(self) -> EncryptionManager:
        """Setup encryption manager"""
        return EncryptionManager(
            rotation_period_days=90,
            use_hsm=False  # Set True for production with HSM
        )

    def _setup_compliance(self) -> ComplianceAutomation:
        """Setup compliance automation"""
        return ComplianceAutomation(self.project_path)

    def _setup_scanner(self) -> VulnerabilityScanner:
        """Setup vulnerability scanner"""
        return VulnerabilityScanner(self.project_path)

    def _setup_secrets(self) -> SecretsManager:
        """Setup secrets manager"""
        return SecretsManager(
            storage_path=self.project_path / ".secrets",
            vault_url=None,  # Set for Vault integration
            vault_token=None
        )

    def _setup_auditor(self) -> SecurityAuditor:
        """Setup security auditor"""
        return SecurityAuditor(self.project_path)

    def authenticate_user(self, return_url: str) -> str:
        """
        Authenticate user via SSO

        Args:
            return_url: Return URL after authentication

        Returns:
            SSO login URL
        """
        print("\n🔐 Initiating SSO authentication...")
        login_url = self.sso.get_login_url(return_url)
        print(f"✅ Login URL generated: {login_url[:50]}...")
        return login_url

    def encrypt_sensitive_data(self, data: str) -> dict:
        """
        Encrypt sensitive data

        Args:
            data: Data to encrypt

        Returns:
            Encrypted data dictionary
        """
        print("\n🔒 Encrypting sensitive data...")
        encrypted = self.encryption.encrypt(
            data.encode(),
            EncryptionAlgorithm.AES_256_GCM
        )
        print(f"✅ Data encrypted with key: {encrypted.key_id}")
        return encrypted.to_dict()

    def run_compliance_audit(self, framework: ComplianceFramework) -> dict:
        """
        Run compliance audit

        Args:
            framework: Compliance framework to check

        Returns:
            Compliance report summary
        """
        print(f"\n📋 Running {framework.value.upper()} compliance audit...")
        report = self.compliance.generate_compliance_report(framework)

        print(f"✅ Compliance Score: {report.compliance_score:.1f}%")
        print(f"   Total Controls: {report.total_controls}")
        print(f"   Passed: {report.passed_controls}")
        print(f"   Failed: {report.failed_controls}")

        return {
            'score': report.compliance_score,
            'total': report.total_controls,
            'passed': report.passed_controls,
            'failed': report.failed_controls
        }

    def scan_vulnerabilities(self) -> dict:
        """
        Scan for vulnerabilities

        Returns:
            Vulnerability scan summary
        """
        print("\n🔍 Scanning for vulnerabilities...")
        results = self.scanner.scan_all()

        total_vulns = sum(r.total_vulnerabilities for r in results.values())
        critical_vulns = sum(r.critical_count for r in results.values())

        print(f"✅ Scan complete:")
        for scan_type, result in results.items():
            print(f"   {scan_type}: {result.total_vulnerabilities} vulnerabilities")
        print(f"   Total: {total_vulns} vulnerabilities")
        print(f"   Critical: {critical_vulns}")

        return {
            'total': total_vulns,
            'critical': critical_vulns,
            'by_type': {k: v.total_vulnerabilities for k, v in results.items()}
        }

    def manage_secrets(self) -> dict:
        """
        Demonstrate secrets management

        Returns:
            Secrets management summary
        """
        print("\n🔑 Managing secrets...")

        # Create secrets
        api_key = self.secrets.create_secret(
            name="stripe_api_key",
            value="sk_live_example_1234567890",
            secret_type=SecretType.API_KEY,
            rotation_period_days=90,
            tags=['payment', 'production']
        )

        db_cred = self.secrets.create_secret(
            name="database_password",
            value="postgres_secure_password_123",
            secret_type=SecretType.DATABASE_CREDENTIAL,
            rotation_period_days=30,
            tags=['database', 'production']
        )

        print(f"✅ Created {len(self.secrets.list_secrets())} secrets")

        # Rotate secrets
        rotated = self.secrets.rotate_all_due_secrets()
        print(f"✅ Rotated {len(rotated)} secrets")

        return {
            'total_secrets': len(self.secrets.list_secrets()),
            'rotated': len(rotated)
        }

    def run_security_audit(self) -> dict:
        """
        Run security audit

        Returns:
            Audit summary
        """
        print("\n🛡️ Running security audit...")
        report = self.auditor.run_automated_pentest()

        print(f"✅ Audit complete:")
        print(f"   Total Findings: {report.total_findings}")
        print(f"   Critical: {report.critical_findings}")
        print(f"   High: {report.high_findings}")
        print(f"   Risk Score: {report.summary['risk_score']}")

        return {
            'total_findings': report.total_findings,
            'critical': report.critical_findings,
            'high': report.high_findings,
            'risk_score': report.summary['risk_score']
        }

    def generate_security_dashboard(self) -> dict:
        """
        Generate complete security dashboard

        Returns:
            Dashboard data
        """
        print("\n" + "="*60)
        print("SECURITY PLATFORM DASHBOARD")
        print("="*60)

        dashboard = {
            'timestamp': datetime.utcnow().isoformat(),
            'sso_enabled': True,
            'encryption_enabled': True
        }

        # Run all checks
        dashboard['compliance'] = self.run_compliance_audit(ComplianceFramework.SOC2)
        dashboard['vulnerabilities'] = self.scan_vulnerabilities()
        dashboard['secrets'] = self.manage_secrets()
        dashboard['audit'] = self.run_security_audit()

        # Calculate overall security score
        compliance_score = dashboard['compliance']['score']
        vuln_penalty = min(50, dashboard['vulnerabilities']['critical'] * 10)
        audit_penalty = min(30, dashboard['audit']['critical'] * 5)

        overall_score = max(0, compliance_score - vuln_penalty - audit_penalty)
        dashboard['overall_security_score'] = overall_score

        print("\n" + "="*60)
        print(f"OVERALL SECURITY SCORE: {overall_score:.1f}%")
        print("="*60)

        return dashboard


def main():
    """Main demonstration"""
    print("🚀 Starting Security Platform Demo\n")

    # Initialize platform
    project_path = Path(".")
    platform = SecurityPlatform(project_path)

    # 1. SSO Authentication
    login_url = platform.authenticate_user("https://myapp.example.com/callback")

    # 2. Encrypt data
    encrypted = platform.encrypt_sensitive_data("Credit card: 4532-1234-5678-9010")

    # 3. Generate security dashboard
    dashboard = platform.generate_security_dashboard()

    # 4. Export dashboard
    output_file = Path("security-dashboard.json")
    import json
    with open(output_file, 'w') as f:
        json.dump(dashboard, f, indent=2)

    print(f"\n✅ Dashboard exported to {output_file}")
    print("\n🎉 Security Platform Demo Complete!")


if __name__ == '__main__':
    main()
