"""
Advanced Security & Compliance Package

Enterprise-grade безопасность: SSO/SAML, шифрование, compliance automation,
vulnerability scanning, secrets management, и security auditing.
"""

from .sso_integration import (
    SSOIntegration,
    SSOConfig,
    SSOProvider,
    SAMLRequest,
    SAMLResponse,
    SSOSession
)

from .encryption_manager import (
    EncryptionManager,
    EncryptionKey,
    EncryptedData,
    EncryptionAlgorithm,
    KeyType,
    KeyStatus
)

from .compliance_automation import (
    ComplianceAutomation,
    ComplianceFramework,
    ComplianceControl,
    ComplianceCheckResult,
    ComplianceReport,
    CheckSeverity,
    CheckStatus
)

from .vulnerability_scanner import (
    VulnerabilityScanner,
    Vulnerability,
    ScanResult,
    VulnerabilitySeverity,
    VulnerabilityType
)

from .secrets_manager import (
    SecretsManager,
    Secret,
    SecretType,
    SecretStatus,
    SecretVersion,
    SecretAuditLog
)

from .security_auditor import (
    SecurityAuditor,
    SecurityFinding,
    AuditReport,
    AuditType,
    FindingSeverity,
    FindingStatus
)

__all__ = [
    # SSO Integration
    'SSOIntegration',
    'SSOConfig',
    'SSOProvider',
    'SAMLRequest',
    'SAMLResponse',
    'SSOSession',

    # Encryption
    'EncryptionManager',
    'EncryptionKey',
    'EncryptedData',
    'EncryptionAlgorithm',
    'KeyType',
    'KeyStatus',

    # Compliance
    'ComplianceAutomation',
    'ComplianceFramework',
    'ComplianceControl',
    'ComplianceCheckResult',
    'ComplianceReport',
    'CheckSeverity',
    'CheckStatus',

    # Vulnerability Scanning
    'VulnerabilityScanner',
    'Vulnerability',
    'ScanResult',
    'VulnerabilitySeverity',
    'VulnerabilityType',

    # Secrets Management
    'SecretsManager',
    'Secret',
    'SecretType',
    'SecretStatus',
    'SecretVersion',
    'SecretAuditLog',

    # Security Auditing
    'SecurityAuditor',
    'SecurityFinding',
    'AuditReport',
    'AuditType',
    'FindingSeverity',
    'FindingStatus'
]

__version__ = '1.0.0'
