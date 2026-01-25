#!/usr/bin/env python3
"""
Template Policies & Governance

Система управления политиками для шаблонов:
- Template approval workflows
- Security scanning
- License compliance
- Quality gates
- Publishing policies
- Version control policies
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set
from datetime import datetime
import json
from pathlib import Path


class TemplateStatus(Enum):
    """Template review status"""
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    PUBLISHED = "published"
    DEPRECATED = "deprecated"


class PolicyViolationSeverity(Enum):
    """Severity of policy violations"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class SecurityScan:
    """Security scan result"""
    scan_id: str
    template_id: str
    scanned_at: str
    scanner: str  # tool name
    passed: bool
    vulnerabilities: List[Dict] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


@dataclass
class LicenseCheck:
    """License compliance check"""
    template_id: str
    license_type: str
    is_compliant: bool
    allowed_licenses: List[str]
    issues: List[str] = field(default_factory=list)


@dataclass
class QualityGate:
    """Quality gate check"""
    name: str
    description: str
    passed: bool
    score: float  # 0-100
    threshold: float
    details: Dict = field(default_factory=dict)


@dataclass
class PolicyViolation:
    """Policy violation"""
    policy_name: str
    severity: PolicyViolationSeverity
    message: str
    details: Dict = field(default_factory=dict)
    can_override: bool = False


@dataclass
class TemplateReview:
    """Template review record"""
    review_id: str
    template_id: str
    reviewer_id: str
    reviewer_email: str
    status: TemplateStatus
    comments: str
    reviewed_at: str = field(default_factory=lambda: datetime.now().isoformat())
    security_scan: Optional[SecurityScan] = None
    license_check: Optional[LicenseCheck] = None
    quality_gates: List[QualityGate] = field(default_factory=list)
    violations: List[PolicyViolation] = field(default_factory=list)


@dataclass
class TemplatePolicy:
    """Template policy definition"""
    id: str
    organization_id: str
    name: str
    description: str
    rules: Dict[str, any]
    is_active: bool = True
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


class TemplatePolicyManager:
    """
    Template Policy Manager

    Enforces policies for template publishing and usage.
    """

    # Default policies
    DEFAULT_POLICIES = {
        'security_scan_required': {
            'name': 'Security Scan Required',
            'description': 'All templates must pass security scan',
            'severity': 'error',
            'enabled': True
        },
        'license_compliance': {
            'name': 'License Compliance',
            'description': 'Only approved licenses allowed',
            'allowed_licenses': ['MIT', 'Apache-2.0', 'BSD-3-Clause', 'GPL-3.0'],
            'severity': 'error',
            'enabled': True
        },
        'code_quality_threshold': {
            'name': 'Code Quality Threshold',
            'description': 'Minimum code quality score',
            'threshold': 70.0,
            'severity': 'warning',
            'enabled': True
        },
        'documentation_required': {
            'name': 'Documentation Required',
            'description': 'README and docs must be present',
            'required_files': ['README.md', 'ARCHITECTURE.md'],
            'severity': 'warning',
            'enabled': True
        },
        'no_hardcoded_secrets': {
            'name': 'No Hardcoded Secrets',
            'description': 'No API keys, passwords in code',
            'patterns': [
                r'api[_-]?key.*=',
                r'password.*=',
                r'secret.*=',
                r'token.*='
            ],
            'severity': 'critical',
            'enabled': True
        }
    }

    def __init__(self, storage_path: Optional[Path] = None):
        """
        Args:
            storage_path: Path to storage directory
        """
        self.storage_path = storage_path or Path.home() / '.ai_generator' / 'policies'
        self.storage_path.mkdir(parents=True, exist_ok=True)

        self.policies_file = self.storage_path / 'policies.json'
        self.reviews_file = self.storage_path / 'reviews.json'

        self.policies = self._load_policies()
        self.reviews = self._load_reviews()

    def _load_policies(self) -> Dict[str, TemplatePolicy]:
        """Load policies"""
        if self.policies_file.exists():
            with open(self.policies_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return {
                    pid: TemplatePolicy(**policy_data)
                    for pid, policy_data in data.items()
                }
        return {}

    def _save_policies(self):
        """Save policies"""
        data = {
            pid: {
                'id': policy.id,
                'organization_id': policy.organization_id,
                'name': policy.name,
                'description': policy.description,
                'rules': policy.rules,
                'is_active': policy.is_active,
                'created_at': policy.created_at
            }
            for pid, policy in self.policies.items()
        }

        with open(self.policies_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

    def _load_reviews(self) -> List[TemplateReview]:
        """Load reviews"""
        if self.reviews_file.exists():
            with open(self.reviews_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                reviews = []
                for review_data in data:
                    # Parse nested objects
                    security_scan = None
                    if review_data.get('security_scan'):
                        security_scan = SecurityScan(**review_data['security_scan'])

                    license_check = None
                    if review_data.get('license_check'):
                        license_check = LicenseCheck(**review_data['license_check'])

                    quality_gates = [
                        QualityGate(**qg)
                        for qg in review_data.get('quality_gates', [])
                    ]

                    violations = [
                        PolicyViolation(
                            policy_name=v['policy_name'],
                            severity=PolicyViolationSeverity(v['severity']),
                            message=v['message'],
                            details=v.get('details', {}),
                            can_override=v.get('can_override', False)
                        )
                        for v in review_data.get('violations', [])
                    ]

                    review = TemplateReview(
                        review_id=review_data['review_id'],
                        template_id=review_data['template_id'],
                        reviewer_id=review_data['reviewer_id'],
                        reviewer_email=review_data['reviewer_email'],
                        status=TemplateStatus(review_data['status']),
                        comments=review_data['comments'],
                        reviewed_at=review_data['reviewed_at'],
                        security_scan=security_scan,
                        license_check=license_check,
                        quality_gates=quality_gates,
                        violations=violations
                    )
                    reviews.append(review)
                return reviews
        return []

    def _save_reviews(self):
        """Save reviews"""
        data = []
        for review in self.reviews:
            review_dict = {
                'review_id': review.review_id,
                'template_id': review.template_id,
                'reviewer_id': review.reviewer_id,
                'reviewer_email': review.reviewer_email,
                'status': review.status.value,
                'comments': review.comments,
                'reviewed_at': review.reviewed_at
            }

            if review.security_scan:
                review_dict['security_scan'] = {
                    'scan_id': review.security_scan.scan_id,
                    'template_id': review.security_scan.template_id,
                    'scanned_at': review.security_scan.scanned_at,
                    'scanner': review.security_scan.scanner,
                    'passed': review.security_scan.passed,
                    'vulnerabilities': review.security_scan.vulnerabilities,
                    'warnings': review.security_scan.warnings
                }

            if review.license_check:
                review_dict['license_check'] = {
                    'template_id': review.license_check.template_id,
                    'license_type': review.license_check.license_type,
                    'is_compliant': review.license_check.is_compliant,
                    'allowed_licenses': review.license_check.allowed_licenses,
                    'issues': review.license_check.issues
                }

            review_dict['quality_gates'] = [
                {
                    'name': qg.name,
                    'description': qg.description,
                    'passed': qg.passed,
                    'score': qg.score,
                    'threshold': qg.threshold,
                    'details': qg.details
                }
                for qg in review.quality_gates
            ]

            review_dict['violations'] = [
                {
                    'policy_name': v.policy_name,
                    'severity': v.severity.value,
                    'message': v.message,
                    'details': v.details,
                    'can_override': v.can_override
                }
                for v in review.violations
            ]

            data.append(review_dict)

        with open(self.reviews_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

    def review_template(
        self,
        template_id: str,
        template_path: Path,
        reviewer_id: str,
        reviewer_email: str,
        organization_id: Optional[str] = None
    ) -> TemplateReview:
        """
        Review template against policies

        Args:
            template_id: Template ID
            template_path: Path to template directory
            reviewer_id: Reviewer user ID
            reviewer_email: Reviewer email
            organization_id: Organization ID (for org-specific policies)

        Returns:
            TemplateReview with results
        """
        import hashlib
        review_id = hashlib.md5(f"{template_id}{datetime.now().isoformat()}".encode()).hexdigest()[:12]

        violations = []
        quality_gates = []

        # Security scan
        security_scan = self._run_security_scan(template_id, template_path)
        if not security_scan.passed:
            violations.append(PolicyViolation(
                policy_name='security_scan_required',
                severity=PolicyViolationSeverity.CRITICAL,
                message='Security scan failed',
                details={'vulnerabilities': len(security_scan.vulnerabilities)}
            ))

        # License check
        license_check = self._check_license(template_id, template_path)
        if not license_check.is_compliant:
            violations.append(PolicyViolation(
                policy_name='license_compliance',
                severity=PolicyViolationSeverity.ERROR,
                message='License not compliant',
                details={'license': license_check.license_type, 'issues': license_check.issues}
            ))

        # Quality gates
        quality_gates.extend(self._check_quality_gates(template_path))

        for qg in quality_gates:
            if not qg.passed:
                violations.append(PolicyViolation(
                    policy_name=qg.name,
                    severity=PolicyViolationSeverity.WARNING,
                    message=f'{qg.name} failed (score: {qg.score:.1f}, threshold: {qg.threshold})',
                    details=qg.details,
                    can_override=True
                ))

        # Check for hardcoded secrets
        secrets_check = self._check_hardcoded_secrets(template_path)
        if secrets_check['found']:
            violations.append(PolicyViolation(
                policy_name='no_hardcoded_secrets',
                severity=PolicyViolationSeverity.CRITICAL,
                message='Hardcoded secrets detected',
                details=secrets_check
            ))

        # Determine status
        has_critical = any(v.severity == PolicyViolationSeverity.CRITICAL for v in violations)
        has_error = any(v.severity == PolicyViolationSeverity.ERROR for v in violations)

        if has_critical or has_error:
            status = TemplateStatus.REJECTED
        else:
            status = TemplateStatus.APPROVED

        review = TemplateReview(
            review_id=review_id,
            template_id=template_id,
            reviewer_id=reviewer_id,
            reviewer_email=reviewer_email,
            status=status,
            comments='Automated review',
            security_scan=security_scan,
            license_check=license_check,
            quality_gates=quality_gates,
            violations=violations
        )

        self.reviews.append(review)
        self._save_reviews()

        return review

    def _run_security_scan(self, template_id: str, template_path: Path) -> SecurityScan:
        """Run security scan on template"""
        import hashlib
        scan_id = hashlib.md5(f"scan_{template_id}_{datetime.now().isoformat()}".encode()).hexdigest()[:12]

        # Simplified scan (in production, use tools like bandit, safety, etc.)
        vulnerabilities = []
        warnings = []

        # Check for suspicious patterns
        for file_path in template_path.rglob('*'):
            if file_path.is_file() and file_path.suffix in ['.py', '.js', '.ts', '.java']:
                try:
                    content = file_path.read_text(encoding='utf-8', errors='ignore')

                    # Check for eval usage
                    if 'eval(' in content:
                        vulnerabilities.append({
                            'file': str(file_path.relative_to(template_path)),
                            'issue': 'Use of eval() detected',
                            'severity': 'high'
                        })

                    # Check for SQL injection patterns
                    if 'execute(' in content and '"SELECT' in content:
                        warnings.append(f'Possible SQL injection in {file_path.name}')

                except Exception:
                    pass

        passed = len(vulnerabilities) == 0

        return SecurityScan(
            scan_id=scan_id,
            template_id=template_id,
            scanned_at=datetime.now().isoformat(),
            scanner='internal',
            passed=passed,
            vulnerabilities=vulnerabilities,
            warnings=warnings
        )

    def _check_license(self, template_id: str, template_path: Path) -> LicenseCheck:
        """Check license compliance"""
        allowed_licenses = self.DEFAULT_POLICIES['license_compliance']['allowed_licenses']

        # Look for LICENSE file
        license_file = None
        for name in ['LICENSE', 'LICENSE.txt', 'LICENSE.md']:
            potential = template_path / name
            if potential.exists():
                license_file = potential
                break

        if not license_file:
            return LicenseCheck(
                template_id=template_id,
                license_type='unknown',
                is_compliant=False,
                allowed_licenses=allowed_licenses,
                issues=['No LICENSE file found']
            )

        # Read and detect license
        content = license_file.read_text(encoding='utf-8')
        detected_license = 'unknown'

        for license_type in allowed_licenses:
            if license_type in content:
                detected_license = license_type
                break

        is_compliant = detected_license in allowed_licenses

        return LicenseCheck(
            template_id=template_id,
            license_type=detected_license,
            is_compliant=is_compliant,
            allowed_licenses=allowed_licenses,
            issues=[] if is_compliant else [f'License {detected_license} not in allowed list']
        )

    def _check_quality_gates(self, template_path: Path) -> List[QualityGate]:
        """Check quality gates"""
        gates = []

        # Documentation gate
        has_readme = (template_path / 'README.md').exists()
        has_arch = (template_path / 'ARCHITECTURE.md').exists()

        doc_score = 0
        if has_readme:
            doc_score += 50
        if has_arch:
            doc_score += 50

        gates.append(QualityGate(
            name='documentation_required',
            description='Documentation completeness',
            passed=doc_score >= 70,
            score=doc_score,
            threshold=70.0,
            details={'has_readme': has_readme, 'has_architecture': has_arch}
        ))

        # Code quality gate (simplified)
        py_files = list(template_path.rglob('*.py'))
        if py_files:
            total_lines = 0
            comment_lines = 0

            for py_file in py_files:
                try:
                    lines = py_file.read_text(encoding='utf-8').split('\n')
                    total_lines += len(lines)
                    comment_lines += sum(1 for line in lines if line.strip().startswith('#'))
                except Exception:
                    pass

            comment_ratio = (comment_lines / total_lines * 100) if total_lines > 0 else 0
            quality_score = min(100, comment_ratio * 2)  # Simplified

            gates.append(QualityGate(
                name='code_quality_threshold',
                description='Code quality score',
                passed=quality_score >= 70,
                score=quality_score,
                threshold=70.0,
                details={'comment_ratio': round(comment_ratio, 2)}
            ))

        return gates

    def _check_hardcoded_secrets(self, template_path: Path) -> Dict:
        """Check for hardcoded secrets"""
        import re

        patterns = [
            (r'api[_-]?key\s*=\s*["\'][^"\']+["\']', 'API key'),
            (r'password\s*=\s*["\'][^"\']+["\']', 'Password'),
            (r'secret\s*=\s*["\'][^"\']+["\']', 'Secret'),
            (r'token\s*=\s*["\'][^"\']+["\']', 'Token')
        ]

        findings = []

        for file_path in template_path.rglob('*'):
            if file_path.is_file() and file_path.suffix in ['.py', '.js', '.ts', '.java', '.yml', '.yaml']:
                try:
                    content = file_path.read_text(encoding='utf-8', errors='ignore')

                    for pattern, secret_type in patterns:
                        matches = re.finditer(pattern, content, re.IGNORECASE)
                        for match in matches:
                            findings.append({
                                'file': str(file_path.relative_to(template_path)),
                                'type': secret_type,
                                'line': content[:match.start()].count('\n') + 1
                            })

                except Exception:
                    pass

        return {
            'found': len(findings) > 0,
            'count': len(findings),
            'findings': findings
        }

    def get_template_reviews(self, template_id: str) -> List[TemplateReview]:
        """Get all reviews for a template"""
        return [r for r in self.reviews if r.template_id == template_id]

    def approve_override(
        self,
        review_id: str,
        approver_id: str,
        reason: str
    ):
        """Override rejection and approve template"""
        for review in self.reviews:
            if review.review_id == review_id:
                review.status = TemplateStatus.APPROVED
                review.comments += f"\n\nOverride approved by {approver_id}: {reason}"
                self._save_reviews()
                print(f"✅ Review {review_id} override approved")
                return

        raise ValueError(f"Review {review_id} not found")


if __name__ == '__main__':
    print("="*70)
    print("TEMPLATE POLICIES & GOVERNANCE")
    print("="*70)

    # Demo
    policy_manager = TemplatePolicyManager()

    # Review a template
    template_path = Path('./demo_template')
    template_path.mkdir(exist_ok=True)
    (template_path / 'README.md').write_text('# Demo Template')
    (template_path / 'LICENSE').write_text('MIT License')

    review = policy_manager.review_template(
        template_id='tmpl123',
        template_path=template_path,
        reviewer_id='reviewer456',
        reviewer_email='reviewer@example.com'
    )

    print(f"\n📋 Review Result:")
    print(f"   Status: {review.status.value}")
    print(f"   Violations: {len(review.violations)}")

    for violation in review.violations:
        print(f"\n   {violation.severity.value.upper()}: {violation.policy_name}")
        print(f"   {violation.message}")
