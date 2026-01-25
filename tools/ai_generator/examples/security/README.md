# Security & Compliance Examples

Comprehensive examples demonstrating all 6 security modules in the AI Generator Toolkit.

## Examples Overview

### 01. SSO/SAML Integration
**File:** `01_sso_integration.py`

Enterprise Single Sign-On integration examples:
- ✅ Okta SSO integration
- ✅ Azure AD SSO integration
- ✅ Google Workspace SSO
- ✅ Auth0 for Single Page Applications
- ✅ Multi-provider SSO setup
- ✅ SAML metadata export

**Run example:**
```bash
python 01_sso_integration.py
```

**Key features demonstrated:**
- SAML 2.0 configuration
- Multi-factor authentication (MFA)
- PKCE for SPAs
- Custom attribute mappings
- Multiple identity providers

---

### 02. Encryption Service
**File:** `02_encryption_service.py`

Encryption and cryptography examples:
- ✅ AES-256-GCM encryption
- ✅ RSA-4096 public key encryption
- ✅ ChaCha20-Poly1305 AEAD
- ✅ Argon2 password hashing
- ✅ Key rotation
- ✅ File encryption
- ✅ Database field encryption
- ✅ HSM integration

**Run example:**
```bash
python 02_encryption_service.py
```

**Key features demonstrated:**
- Symmetric encryption (AES-256-GCM, ChaCha20-Poly1305)
- Asymmetric encryption (RSA-4096)
- Password hashing (Argon2)
- Automated key rotation
- Hardware Security Module (HSM) support

---

### 03. Compliance Framework
**File:** `03_compliance_framework.py`

Compliance automation for major frameworks:
- ✅ SOC 2 Type II compliance
- ✅ ISO 27001:2022 compliance
- ✅ GDPR compliance
- ✅ HIPAA compliance
- ✅ Automated compliance audits
- ✅ Multi-framework compliance
- ✅ Evidence collection
- ✅ Continuous compliance monitoring

**Run example:**
```bash
python 03_compliance_framework.py
```

**Key features demonstrated:**
- Automated control documentation
- Policy templates
- Audit checklists
- Evidence collection
- Compliance dashboards

---

### 04. Vulnerability Scanner
**File:** `04_vulnerability_scanner.py`

Comprehensive security scanning examples:
- ✅ Dependency vulnerability scanning
- ✅ Static code analysis (SAST)
- ✅ Container image scanning
- ✅ Web application scanning (DAST)
- ✅ Cloud infrastructure scanning
- ✅ Secrets detection
- ✅ License compliance
- ✅ Comprehensive security reports
- ✅ CI/CD integration

**Run example:**
```bash
python 04_vulnerability_scanner.py
```

**Key features demonstrated:**
- CVE/CWE detection
- CVSS scoring
- OWASP Top 10 scanning
- Automated remediation advice
- SARIF report generation

---

### 05. Zero Trust Architecture
**File:** `05_zero_trust_architecture.py`

Zero Trust security implementation:
- ✅ Basic Zero Trust architecture
- ✅ Device trust verification
- ✅ Context-aware access control
- ✅ Network microsegmentation
- ✅ Identity-Aware Proxy (IAP)
- ✅ HashiCorp Boundary
- ✅ Continuous trust verification
- ✅ Workload identity
- ✅ Zero Trust monitoring

**Run example:**
```bash
python 05_zero_trust_architecture.py
```

**Key features demonstrated:**
- Never trust, always verify
- Device posture checking
- Context-based policies
- Microsegmentation
- Continuous verification

---

### 06. Secrets Manager
**File:** `06_secrets_manager.py`

Secrets management across multiple platforms:
- ✅ HashiCorp Vault setup
- ✅ Store and retrieve secrets
- ✅ Dynamic database credentials
- ✅ AWS Secrets Manager
- ✅ Azure Key Vault
- ✅ Secret rotation policies
- ✅ Encryption as a service (Transit)
- ✅ Access control policies
- ✅ Audit logging
- ✅ Kubernetes integration

**Run example:**
```bash
python 06_secrets_manager.py
```

**Key features demonstrated:**
- Multi-provider support (Vault, AWS, Azure)
- Dynamic credential generation
- Automatic secret rotation
- Encryption as a service
- Fine-grained access control

---

## Quick Start

### Run all examples
```bash
# Run all security examples
for script in *.py; do
    echo "Running $script..."
    python "$script"
    echo ""
done
```

### Run specific example
```bash
# Example: Run SSO integration
python 01_sso_integration.py

# Example: Run encryption service
python 02_encryption_service.py
```

## Prerequisites

Install required dependencies:

```bash
# Core dependencies
pip install cryptography
pip install pyjwt
pip install python-saml

# For Vault examples
pip install hvac

# For AWS examples
pip install boto3

# For Azure examples
pip install azure-identity azure-keyvault-secrets

# For scanning examples
pip install bandit safety
```

## Output Structure

All examples generate output in the `./output/` directory:

```
output/
├── okta-sso/
│   ├── config.py
│   ├── metadata.xml
│   └── README.md
├── encryption/
│   ├── test_document.txt.enc
│   └── keys/
├── compliance/
│   ├── soc2/
│   ├── iso27001/
│   ├── gdpr/
│   └── hipaa/
├── zero-trust/
│   ├── device-trust/
│   ├── iap/
│   └── monitoring/
└── vault/
    ├── policies/
    └── audit/
```

## Security Best Practices

### SSO/SAML
- ✅ Enable MFA for all users
- ✅ Use signed SAML assertions
- ✅ Implement PKCE for SPAs
- ✅ Regular certificate rotation
- ✅ Monitor failed authentication attempts

### Encryption
- ✅ Use authenticated encryption (GCM, Poly1305)
- ✅ Rotate keys every 90-180 days
- ✅ Use HSM for production environments
- ✅ Never log encryption keys
- ✅ Use Argon2 for password hashing

### Compliance
- ✅ Document all controls
- ✅ Collect evidence regularly
- ✅ Quarterly internal audits
- ✅ Keep policies updated
- ✅ Employee training programs

### Vulnerability Scanning
- ✅ Daily dependency scans
- ✅ SAST in CI/CD pipeline
- ✅ Weekly DAST on staging
- ✅ Never commit secrets
- ✅ < 24h SLA for critical vulnerabilities

### Zero Trust
- ✅ Never trust, always verify
- ✅ Device posture verification
- ✅ Continuous authentication
- ✅ Microsegmentation
- ✅ Monitor all access

### Secrets Management
- ✅ Never hardcode secrets
- ✅ Use dynamic credentials
- ✅ Rotate secrets regularly
- ✅ Least privilege access
- ✅ Enable audit logging

## Common Use Cases

### Enterprise Authentication
```python
# Implement SSO for enterprise app
from tools.ai_generator.security import SSOGenerator, SSOConfig, SSOProvider

config = SSOConfig(provider=SSOProvider.OKTA, ...)
generator = SSOGenerator(config)
files = generator.generate(Path("./sso"))
```

### Data Protection
```python
# Encrypt sensitive customer data
from tools.ai_generator.security import EncryptionService, EncryptionConfig

service = EncryptionService(config)
encrypted = service.encrypt(customer_data)
```

### Compliance Certification
```python
# Generate SOC 2 compliance documentation
from tools.ai_generator.security import ComplianceGenerator

generator = ComplianceGenerator(framework=ComplianceFramework.SOC2)
files = generator.generate(Path("./compliance"))
```

### Security Scanning
```python
# Scan codebase for vulnerabilities
from tools.ai_generator.security import VulnerabilityScanner

scanner = VulnerabilityScanner()
results = scanner.scan_code(directory=Path("./src"))
```

### Zero Trust Implementation
```python
# Deploy Zero Trust architecture
from tools.ai_generator.security import ZeroTrustGenerator

generator = ZeroTrustGenerator(config)
files = generator.generate(Path("./zero-trust"))
```

### Secrets Management
```python
# Setup HashiCorp Vault
from tools.ai_generator.security import SecretsManager

manager = SecretsManager(provider=SecretsProvider.HASHICORP_VAULT)
manager.store_secret("database/prod", credentials)
```

## Troubleshooting

### Common Issues

**SAML Configuration**
```
Issue: Invalid SAML response
Solution: Verify entity ID matches exactly
```

**Encryption Errors**
```
Issue: Decryption fails after key rotation
Solution: Keep old keys for graceful migration period
```

**Compliance Audit Failures**
```
Issue: Missing evidence for controls
Solution: Enable continuous evidence collection
```

**Vault Connection**
```
Issue: Unable to connect to Vault
Solution: Check VAULT_ADDR and authentication token
```

## Additional Resources

- [Security Module Documentation](../../security/README.md)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
- [CIS Benchmarks](https://www.cisecurity.org/cis-benchmarks/)
- [HashiCorp Vault Docs](https://www.vaultproject.io/docs)

## Support

For issues or questions:
- 📖 Documentation: [Main README](../../README.md)
- 🐛 Issues: [GitHub Issues](https://github.com/yourusername/info1/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/yourusername/info1/discussions)

---

**Security Examples** | Version 1.0.0 | Last Updated: 2026-01-25
