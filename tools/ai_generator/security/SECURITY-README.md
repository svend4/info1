# Advanced Security & Compliance Module

Enterprise-grade security система для AI Code Generator с поддержкой SSO, шифрования, compliance automation, vulnerability scanning, secrets management и security auditing.

## 📋 Содержание

- [Возможности](#возможности)
- [Компоненты](#компоненты)
- [Установка](#установка)
- [Быстрый старт](#быстрый-старт)
- [Примеры использования](#примеры-использования)
- [Security Best Practices](#security-best-practices)

## 🔐 Возможности

### SSO/SAML Integration
- ✅ Поддержка популярных SSO провайдеров (Okta, Azure AD, Google Workspace)
- ✅ SAML 2.0 authentication
- ✅ Single Sign-On (SSO) и Single Logout (SLO)
- ✅ Attribute mapping
- ✅ Session management

### Advanced Encryption
- ✅ AES-256-GCM, AES-256-CBC, ChaCha20-Poly1305
- ✅ Automatic key rotation
- ✅ Encryption at rest и in-transit
- ✅ HMAC для data integrity
- ✅ HSM integration support

### Compliance Automation
- ✅ SOC 2 Type II compliance
- ✅ ISO 27001 controls
- ✅ GDPR compliance checks
- ✅ HIPAA, PCI DSS, CCPA support
- ✅ Automated audit reports
- ✅ Real-time compliance monitoring

### Vulnerability Scanning
- ✅ Dependency vulnerability detection
- ✅ Code security analysis (SAST)
- ✅ Secrets exposure detection
- ✅ CVE и CWE mapping
- ✅ Integration с pip-audit, npm audit, govulncheck
- ✅ CVSS scoring

### Secrets Management
- ✅ HashiCorp Vault integration
- ✅ Automatic secrets rotation
- ✅ Secrets versioning
- ✅ Audit logging
- ✅ Encrypted storage
- ✅ Environment variable export

### Security Auditing
- ✅ Automated penetration testing
- ✅ OWASP Top 10 scanning
- ✅ SSL/TLS security testing
- ✅ Access control reviews
- ✅ Configuration audits
- ✅ Comprehensive reporting

## 📦 Компоненты

### 1. SSO Integration (`sso_integration.py`)

Интеграция с enterprise SSO providers для централизованной аутентификации.

**Основные классы:**
- `SSOIntegration` - Main SSO manager
- `SSOConfig` - SSO configuration
- `SAMLRequest/SAMLResponse` - SAML protocol handling
- `SSOSession` - Session management

**Пример:**
```python
from ai_generator.security import SSOIntegration, SSOConfig, SSOProvider

config = SSOConfig(
    provider=SSOProvider.OKTA,
    entity_id="https://myapp.com",
    sso_url="https://company.okta.com/app/sso",
    x509_cert="<IDP_CERTIFICATE>",
    sign_requests=True
)

sso = SSOIntegration(config)
login_url = sso.get_login_url("https://myapp.com/callback")
```

### 2. Encryption Manager (`encryption_manager.py`)

Advanced encryption с поддержкой multiple algorithms и key rotation.

**Основные классы:**
- `EncryptionManager` - Main encryption manager
- `EncryptionKey` - Key management
- `EncryptedData` - Encrypted data container

**Пример:**
```python
from ai_generator.security import EncryptionManager, EncryptionAlgorithm

manager = EncryptionManager(rotation_period_days=90)

# Encrypt data
data = b"Sensitive user information"
encrypted = manager.encrypt(data, EncryptionAlgorithm.AES_256_GCM)

# Decrypt data
decrypted = manager.decrypt(encrypted)

# Auto-rotation
rotations = manager.rotate_keys()
```

### 3. Compliance Automation (`compliance_automation.py`)

Automated compliance checking для multiple frameworks.

**Основные классы:**
- `ComplianceAutomation` - Main compliance manager
- `ComplianceControl` - Control definitions
- `ComplianceReport` - Audit reports

**Пример:**
```python
from ai_generator.security import ComplianceAutomation, ComplianceFramework
from pathlib import Path

compliance = ComplianceAutomation(Path("/path/to/project"))

# Run SOC 2 compliance check
results = compliance.run_compliance_check(ComplianceFramework.SOC2)

# Generate report
report = compliance.generate_compliance_report(ComplianceFramework.GDPR)

# Export report
compliance.export_report(report, Path("compliance-report.html"), format='html')
```

### 4. Vulnerability Scanner (`vulnerability_scanner.py`)

Comprehensive vulnerability scanning для dependencies и code.

**Основные классы:**
- `VulnerabilityScanner` - Main scanner
- `Vulnerability` - Vulnerability findings
- `ScanResult` - Scan results

**Пример:**
```python
from ai_generator.security import VulnerabilityScanner
from pathlib import Path

scanner = VulnerabilityScanner(Path("/path/to/project"))

# Scan dependencies
dep_results = scanner.scan_dependencies("requirements.txt")

# Scan code
code_results = scanner.scan_code()

# Scan for secrets
secret_results = scanner.scan_secrets()

# Run all scans
all_results = scanner.scan_all()

# Generate report
scanner.generate_report(all_results, Path("vulnerability-report.json"))
```

### 5. Secrets Manager (`secrets_manager.py`)

Centralized secrets management с rotation и auditing.

**Основные классы:**
- `SecretsManager` - Main secrets manager
- `Secret` - Secret entry
- `SecretVersion` - Version management

**Пример:**
```python
from ai_generator.security import SecretsManager, SecretType
from pathlib import Path

secrets = SecretsManager(
    storage_path=Path("/secure/secrets"),
    vault_url="https://vault.company.com"
)

# Create secret
api_key = secrets.create_secret(
    name="stripe_api_key",
    value="sk_live_1234567890",
    secret_type=SecretType.API_KEY,
    rotation_period_days=90
)

# Retrieve secret
secret = secrets.get_secret_by_name("stripe_api_key")
print(secret.value)

# Rotate secret
secrets.rotate_secret(api_key.secret_id)

# Auto-rotate all due secrets
rotated = secrets.rotate_all_due_secrets()
```

### 6. Security Auditor (`security_auditor.py`)

Automated security auditing и penetration testing.

**Основные классы:**
- `SecurityAuditor` - Main auditor
- `SecurityFinding` - Security findings
- `AuditReport` - Audit reports

**Пример:**
```python
from ai_generator.security import SecurityAuditor, AuditType
from pathlib import Path

auditor = SecurityAuditor(Path("/path/to/project"))

# Run security audit
report = auditor.run_security_audit(AuditType.SECURITY_SCAN)

# Run penetration test
pentest_report = auditor.run_automated_pentest()

# Get open findings
critical_findings = auditor.get_open_findings(FindingSeverity.CRITICAL)

# Resolve finding
auditor.resolve_finding("FINDING-001", "Fixed by updating library")

# Export report
auditor.export_report(report, Path("security-audit.json"))
```

## 🚀 Установка

```bash
# Install required dependencies
pip install cryptography python-saml hvac

# For vulnerability scanning
pip install pip-audit safety bandit

# For penetration testing (optional)
pip install requests sqlmap
```

## ⚡ Быстрый старт

### Complete Security Platform

```python
from pathlib import Path
from ai_generator.security import (
    SSOIntegration, SSOConfig, SSOProvider,
    EncryptionManager, EncryptionAlgorithm,
    ComplianceAutomation, ComplianceFramework,
    VulnerabilityScanner,
    SecretsManager, SecretType,
    SecurityAuditor, AuditType
)

# Project setup
project_path = Path("/path/to/project")

# 1. Setup SSO
sso_config = SSOConfig(
    provider=SSOProvider.OKTA,
    entity_id="https://myapp.com",
    sso_url="https://company.okta.com/app/sso",
    x509_cert="<CERTIFICATE>",
    sign_requests=True
)
sso = SSOIntegration(sso_config)

# 2. Setup Encryption
encryption = EncryptionManager(rotation_period_days=90)

# 3. Setup Secrets Management
secrets = SecretsManager(
    storage_path=project_path / ".secrets",
    vault_url="https://vault.company.com"
)

# 4. Run Compliance Check
compliance = ComplianceAutomation(project_path)
soc2_report = compliance.generate_compliance_report(ComplianceFramework.SOC2)
print(f"SOC 2 Compliance Score: {soc2_report.compliance_score:.1f}%")

# 5. Run Vulnerability Scan
scanner = VulnerabilityScanner(project_path)
vuln_results = scanner.scan_all()
for scan_type, result in vuln_results.items():
    print(f"{scan_type}: {result.total_vulnerabilities} vulnerabilities found")

# 6. Run Security Audit
auditor = SecurityAuditor(project_path)
audit_report = auditor.run_automated_pentest()
print(f"Security Risk Score: {audit_report.summary['risk_score']}")

# 7. Generate comprehensive report
print("\n=== Security Dashboard ===")
print(f"Compliance Score: {soc2_report.compliance_score:.1f}%")
print(f"Vulnerabilities: {sum(r.total_vulnerabilities for r in vuln_results.values())}")
print(f"Security Findings: {audit_report.total_findings}")
print(f"Critical Issues: {audit_report.critical_findings}")
```

## 📊 Security Best Practices

### 1. SSO Configuration
- ✅ Always enable `sign_requests` and `encrypt_assertions`
- ✅ Use strong X.509 certificates
- ✅ Implement session timeout and refresh
- ✅ Enable audit logging for all SSO events

### 2. Encryption
- ✅ Use AES-256-GCM for maximum security
- ✅ Rotate keys every 90 days
- ✅ Never hardcode encryption keys
- ✅ Use HSM for production key storage
- ✅ Implement key backup and recovery

### 3. Compliance
- ✅ Run compliance checks weekly
- ✅ Automate remediation where possible
- ✅ Maintain audit trail for all compliance activities
- ✅ Regular compliance training for team

### 4. Vulnerability Management
- ✅ Run dependency scans on every build
- ✅ Fix critical vulnerabilities within 24h
- ✅ Automate security updates
- ✅ Implement vulnerability disclosure policy

### 5. Secrets Management
- ✅ Never commit secrets to version control
- ✅ Use Vault or cloud secrets managers in production
- ✅ Rotate secrets automatically
- ✅ Audit all secret access
- ✅ Use short-lived credentials where possible

### 6. Security Auditing
- ✅ Run automated pentests monthly
- ✅ Schedule quarterly external audits
- ✅ Maintain incident response plan
- ✅ Track and resolve all findings
- ✅ Implement continuous monitoring

## 📈 Metrics

- **Total Lines of Code**: ~2,500
- **Security Controls**: 50+
- **Compliance Frameworks**: 6
- **Vulnerability Patterns**: 30+
- **Secret Patterns**: 10+
- **Audit Types**: 6

## 🔧 Architecture

```
security/
├── sso_integration.py       # SSO/SAML authentication (400 LOC)
├── encryption_manager.py    # Advanced encryption (520 LOC)
├── compliance_automation.py # Compliance automation (650 LOC)
├── vulnerability_scanner.py # Vulnerability scanning (490 LOC)
├── secrets_manager.py       # Secrets management (450 LOC)
└── security_auditor.py      # Security auditing (450 LOC)
```

## 🎯 Use Cases

### Enterprise SaaS Platform
```python
# Complete security stack for SaaS
sso = setup_sso_with_okta()
encryption = setup_encryption_with_hsm()
compliance = run_soc2_compliance()
secrets = setup_vault_integration()
audit = schedule_monthly_pentests()
```

### Financial Services
```python
# PCI DSS + SOX compliance
compliance_pci = run_pci_dss_compliance()
encryption_fips = setup_fips_encryption()
audit_financial = run_sox_controls()
```

### Healthcare Platform
```python
# HIPAA compliance
compliance_hipaa = run_hipaa_compliance()
encryption_phi = encrypt_protected_health_info()
audit_healthcare = run_hipaa_audits()
```

## 🔒 Security

Все модули следуют industry best practices:
- OWASP Top 10 защита
- NIST Cybersecurity Framework alignment
- CIS Controls implementation
- Zero Trust Architecture principles

## 📝 License

Part of AI Code Generator - Enterprise Security Module
Version 1.0.0
