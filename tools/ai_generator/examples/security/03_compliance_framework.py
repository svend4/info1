#!/usr/bin/env python3
"""
Example: Compliance Framework

This example demonstrates automated compliance management
for SOC 2, ISO 27001, GDPR, and HIPAA.
"""

from pathlib import Path
from datetime import datetime, timedelta
from tools.ai_generator.security import (
    ComplianceGenerator,
    ComplianceFramework,
    ComplianceConfig,
    ComplianceControl,
    ComplianceAudit
)


def example_soc2_compliance():
    """Generate SOC 2 Type II compliance framework"""
    print("=" * 60)
    print("Example 1: SOC 2 Type II Compliance")
    print("=" * 60)

    config = ComplianceConfig(
        framework=ComplianceFramework.SOC2,
        organization="Acme Corp",
        scope="Cloud SaaS Platform"
    )

    generator = ComplianceGenerator(config)

    # Add Trust Services Criteria controls
    generator.add_control("Access Control", "CC6.1", "Implement logical access controls")
    generator.add_control("Encryption", "CC6.7", "Encrypt data in transit and at rest")
    generator.add_control("Change Management", "CC8.1", "Manage system changes")
    generator.add_control("Monitoring", "CC7.2", "Monitor system activities")
    generator.add_control("Backup", "A1.2", "Backup data regularly")

    files = generator.generate(Path("./output/compliance/soc2"))

    print(f"✅ Generated {len(files)} SOC 2 compliance files")
    print("\n📋 Files generated:")
    for filename in sorted(files.keys())[:10]:
        print(f"   - {filename}")

    print("\n🎯 SOC 2 Trust Services Criteria:")
    print("   ✓ Security (CC)")
    print("   ✓ Availability (A)")
    print("   ✓ Processing Integrity (PI)")
    print("   ✓ Confidentiality (C)")
    print("   ✓ Privacy (P)")
    print()


def example_iso27001_compliance():
    """Generate ISO 27001 compliance framework"""
    print("=" * 60)
    print("Example 2: ISO 27001:2022 Compliance")
    print("=" * 60)

    config = ComplianceConfig(
        framework=ComplianceFramework.ISO27001,
        organization="Global Enterprise Inc",
        scope="Information Security Management System"
    )

    generator = ComplianceGenerator(config)

    # Add Annex A controls
    generator.add_control("Information Security Policies", "A.5.1", "Policies for information security")
    generator.add_control("Asset Management", "A.8.1", "Responsibility for assets")
    generator.add_control("Access Control", "A.9.1", "Business requirements for access control")
    generator.add_control("Cryptography", "A.10.1", "Cryptographic controls")
    generator.add_control("Physical Security", "A.11.1", "Secure areas")
    generator.add_control("Operations Security", "A.12.1", "Operational procedures")
    generator.add_control("Incident Management", "A.16.1", "Management of incidents")

    files = generator.generate(Path("./output/compliance/iso27001"))

    print(f"✅ Generated {len(files)} ISO 27001 compliance files")
    print("\n📋 Includes:")
    print("   - Statement of Applicability (SoA)")
    print("   - Risk Assessment templates")
    print("   - Annex A controls documentation")
    print("   - Internal audit checklists")
    print("   - Management review templates")
    print()


def example_gdpr_compliance():
    """Generate GDPR compliance framework"""
    print("=" * 60)
    print("Example 3: GDPR Compliance")
    print("=" * 60)

    config = ComplianceConfig(
        framework=ComplianceFramework.GDPR,
        organization="EU Data Processor Ltd",
        scope="Personal Data Processing",
        data_protection_officer="dpo@example.com"
    )

    generator = ComplianceGenerator(config)

    # Add GDPR articles
    generator.add_control("Lawfulness of Processing", "Art. 6", "Legal basis for processing")
    generator.add_control("Data Subject Rights", "Art. 15-22", "Right to access, rectification, erasure")
    generator.add_control("Data Protection by Design", "Art. 25", "Privacy by design and default")
    generator.add_control("Data Breach Notification", "Art. 33", "72-hour breach notification")
    generator.add_control("Data Protection Impact Assessment", "Art. 35", "DPIA for high-risk processing")
    generator.add_control("International Transfers", "Art. 46", "Safeguards for data transfers")

    files = generator.generate(Path("./output/compliance/gdpr"))

    print(f"✅ Generated {len(files)} GDPR compliance files")
    print("\n📋 Key components:")
    print("   - Data Processing Agreement (DPA)")
    print("   - Privacy Policy template")
    print("   - Data Subject Request (DSR) forms")
    print("   - Consent management procedures")
    print("   - Data breach response plan")
    print("   - Record of Processing Activities (ROPA)")

    print("\n⚖️ GDPR Principles:")
    print("   ✓ Lawfulness, fairness, transparency")
    print("   ✓ Purpose limitation")
    print("   ✓ Data minimization")
    print("   ✓ Accuracy")
    print("   ✓ Storage limitation")
    print("   ✓ Integrity and confidentiality")
    print()


def example_hipaa_compliance():
    """Generate HIPAA compliance framework"""
    print("=" * 60)
    print("Example 4: HIPAA Compliance")
    print("=" * 60)

    config = ComplianceConfig(
        framework=ComplianceFramework.HIPAA,
        organization="HealthTech Solutions",
        scope="Protected Health Information (PHI)",
        covered_entity=True
    )

    generator = ComplianceGenerator(config)

    # Add HIPAA safeguards
    generator.add_control("Access Control", "§164.312(a)(1)", "Unique user identification")
    generator.add_control("Audit Controls", "§164.312(b)", "Hardware/software audit logs")
    generator.add_control("Encryption", "§164.312(a)(2)(iv)", "Encryption and decryption")
    generator.add_control("Transmission Security", "§164.312(e)(1)", "Integrity controls")
    generator.add_control("Emergency Access", "§164.312(a)(2)(ii)", "Emergency access procedures")
    generator.add_control("BAA Management", "§164.314(a)", "Business Associate Agreements")

    files = generator.generate(Path("./output/compliance/hipaa"))

    print(f"✅ Generated {len(files)} HIPAA compliance files")
    print("\n📋 HIPAA Safeguards:")
    print("   🔐 Administrative Safeguards")
    print("      - Security Management Process")
    print("      - Workforce Security")
    print("      - Information Access Management")
    print("   💻 Technical Safeguards")
    print("      - Access Control")
    print("      - Audit Controls")
    print("      - Integrity and Encryption")
    print("   🏢 Physical Safeguards")
    print("      - Facility Access Controls")
    print("      - Workstation Security")
    print("      - Device and Media Controls")
    print()


def example_compliance_audit():
    """Perform compliance audit"""
    print("=" * 60)
    print("Example 5: Automated Compliance Audit")
    print("=" * 60)

    config = ComplianceConfig(
        framework=ComplianceFramework.SOC2,
        organization="Tech Startup Inc"
    )

    generator = ComplianceGenerator(config)

    # Add controls
    controls = [
        ("Access Control", "CC6.1", "MFA implemented"),
        ("Encryption", "CC6.7", "TLS 1.3 for all traffic"),
        ("Monitoring", "CC7.2", "CloudWatch + DataDog"),
        ("Backup", "A1.2", "Daily automated backups"),
        ("Incident Response", "CC7.3", "24/7 on-call rotation")
    ]

    for name, control_id, description in controls:
        generator.add_control(name, control_id, description)

    # Run audit
    audit = generator.run_audit()

    print("✅ Compliance audit completed")
    print(f"\n📊 Audit Results:")
    print(f"   Total Controls: {audit.total_controls}")
    print(f"   Compliant: {audit.compliant_controls}")
    print(f"   Non-Compliant: {audit.non_compliant_controls}")
    print(f"   Compliance Rate: {audit.compliance_percentage:.1f}%")

    print(f"\n⚠️ Findings:")
    for finding in audit.findings:
        print(f"   - {finding.severity}: {finding.description}")

    print()


def example_multi_framework_compliance():
    """Implement multiple compliance frameworks"""
    print("=" * 60)
    print("Example 6: Multi-Framework Compliance")
    print("=" * 60)

    frameworks = [
        (ComplianceFramework.SOC2, "SOC 2 Type II"),
        (ComplianceFramework.ISO27001, "ISO 27001:2022"),
        (ComplianceFramework.GDPR, "GDPR"),
        (ComplianceFramework.HIPAA, "HIPAA")
    ]

    total_files = 0

    for framework, name in frameworks:
        config = ComplianceConfig(
            framework=framework,
            organization="Multi-Compliance Corp"
        )

        generator = ComplianceGenerator(config)

        # Add common security controls
        generator.add_control("MFA", "MFA-001", "Multi-factor authentication required")
        generator.add_control("Encryption", "ENC-001", "AES-256-GCM encryption")
        generator.add_control("Logging", "LOG-001", "Centralized audit logging")

        files = generator.generate(Path(f"./output/compliance/multi/{framework.value}"))
        total_files += len(files)

        print(f"✅ {name}: {len(files)} files")

    print(f"\n📦 Total files across all frameworks: {total_files}")
    print("🎯 Common controls mapped across frameworks")
    print()


def example_evidence_collection():
    """Automated evidence collection for audits"""
    print("=" * 60)
    print("Example 7: Evidence Collection")
    print("=" * 60)

    config = ComplianceConfig(
        framework=ComplianceFramework.SOC2,
        organization="Evidence Demo Corp"
    )

    generator = ComplianceGenerator(config)

    # Collect evidence
    evidence = generator.collect_evidence(
        control_id="CC6.1",
        evidence_type="screenshot",
        description="MFA configuration in AWS IAM"
    )

    print("✅ Evidence collected")
    print(f"📸 Type: {evidence.type}")
    print(f"📋 Control: {evidence.control_id}")
    print(f"📅 Timestamp: {evidence.timestamp}")
    print(f"🔗 Artifact: {evidence.artifact_path}")

    # Generate evidence report
    report = generator.generate_evidence_report(
        start_date=datetime.now() - timedelta(days=90),
        end_date=datetime.now()
    )

    print(f"\n📊 Evidence Report (90 days):")
    print(f"   Total Evidence Items: {report.total_items}")
    print(f"   Controls Covered: {report.controls_covered}")
    print(f"   Evidence Types: {', '.join(report.evidence_types)}")
    print()


def example_continuous_compliance():
    """Continuous compliance monitoring"""
    print("=" * 60)
    print("Example 8: Continuous Compliance Monitoring")
    print("=" * 60)

    config = ComplianceConfig(
        framework=ComplianceFramework.SOC2,
        organization="Always Compliant Inc",
        enable_continuous_monitoring=True
    )

    generator = ComplianceGenerator(config)

    # Setup monitoring
    generator.setup_monitoring(
        check_interval_hours=24,
        alert_email="compliance@example.com"
    )

    print("✅ Continuous compliance monitoring enabled")
    print("\n🔍 Monitoring configuration:")
    print("   - Daily automated compliance checks")
    print("   - Real-time control validation")
    print("   - Automated evidence collection")
    print("   - Email alerts for violations")

    print("\n📊 Monitored metrics:")
    print("   ✓ Access control effectiveness")
    print("   ✓ Encryption coverage")
    print("   ✓ Patch management status")
    print("   ✓ Backup success rate")
    print("   ✓ Incident response time")

    print("\n🔔 Alert triggers:")
    print("   ⚠️ Control failure detected")
    print("   ⚠️ Compliance score below threshold")
    print("   ⚠️ Missing evidence for >7 days")
    print("   ⚠️ Policy violation")
    print()


if __name__ == "__main__":
    print("\n⚖️ Compliance Framework Examples")
    print("=" * 60)
    print()

    # Run all examples
    example_soc2_compliance()
    example_iso27001_compliance()
    example_gdpr_compliance()
    example_hipaa_compliance()
    example_compliance_audit()
    example_multi_framework_compliance()
    example_evidence_collection()
    example_continuous_compliance()

    print("=" * 60)
    print("✅ All compliance examples completed!")
    print("=" * 60)
    print("\n📚 Compliance Best Practices:")
    print("   1. Document all security controls and policies")
    print("   2. Collect evidence regularly (not just before audits)")
    print("   3. Perform internal audits quarterly")
    print("   4. Keep policies updated with regulatory changes")
    print("   5. Train employees on compliance requirements")
    print("   6. Use automated tools for continuous monitoring")
    print("   7. Maintain vendor compliance documentation")
    print("   8. Review and update risk assessments annually")
