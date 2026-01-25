#!/usr/bin/env python3
"""
Example: Zero Trust Architecture

This example demonstrates implementing Zero Trust security
with BeyondCorp, Google BeyondCorp, and HashiCorp Boundary.
"""

from pathlib import Path
from tools.ai_generator.security import (
    ZeroTrustGenerator,
    ZeroTrustConfig,
    ZeroTrustProvider,
    AccessPolicy,
    IdentityProvider,
    TrustLevel
)


def example_basic_zero_trust():
    """Basic Zero Trust architecture setup"""
    print("=" * 60)
    print("Example 1: Basic Zero Trust Architecture")
    print("=" * 60)

    config = ZeroTrustConfig(
        provider=ZeroTrustProvider.BEYONDCORP,
        organization="Acme Corp",
        enable_device_trust=True,
        enable_user_trust=True,
        enable_network_microsegmentation=True
    )

    generator = ZeroTrustGenerator(config)

    # Generate Zero Trust configuration
    files = generator.generate(Path("./output/zero-trust/basic"))

    print(f"✅ Zero Trust architecture generated")
    print(f"📋 Files created: {len(files)}")

    print(f"\n🔐 Zero Trust Principles:")
    print(f"   1. ✓ Never trust, always verify")
    print(f"   2. ✓ Assume breach")
    print(f"   3. ✓ Verify explicitly")
    print(f"   4. ✓ Use least privilege access")
    print(f"   5. ✓ Minimize blast radius")
    print()


def example_device_trust():
    """Implement device trust verification"""
    print("=" * 60)
    print("Example 2: Device Trust Verification")
    print("=" * 60)

    config = ZeroTrustConfig(
        provider=ZeroTrustProvider.BEYONDCORP,
        enable_device_trust=True
    )

    generator = ZeroTrustGenerator(config)

    # Configure device trust policies
    generator.add_device_requirement("os_version", "Windows 11 or macOS 13+")
    generator.add_device_requirement("encryption", "Full disk encryption required")
    generator.add_device_requirement("antivirus", "Real-time protection enabled")
    generator.add_device_requirement("patch_level", "Security patches < 30 days old")
    generator.add_device_requirement("screen_lock", "Auto-lock after 5 minutes")

    files = generator.generate(Path("./output/zero-trust/device-trust"))

    print(f"✅ Device trust configuration generated")

    print(f"\n🖥️ Device requirements:")
    print(f"   ✓ Managed device (MDM enrolled)")
    print(f"   ✓ Up-to-date OS and security patches")
    print(f"   ✓ Disk encryption enabled")
    print(f"   ✓ Antivirus/EDR active")
    print(f"   ✓ Screen lock configured")
    print(f"   ✓ No jailbreak/root detection")

    print(f"\n📱 Supported platforms:")
    print(f"   - Windows (Intune MDM)")
    print(f"   - macOS (Jamf/Intune)")
    print(f"   - iOS/iPadOS")
    print(f"   - Android (Android Enterprise)")
    print()


def example_user_context():
    """User and context-based access control"""
    print("=" * 60)
    print("Example 3: Context-Aware Access Control")
    print("=" * 60)

    config = ZeroTrustConfig(
        provider=ZeroTrustProvider.BEYONDCORP,
        enable_user_trust=True,
        enable_context_awareness=True
    )

    generator = ZeroTrustGenerator(config)

    # Define access policies
    policies = [
        AccessPolicy(
            name="corporate-network",
            description="Access from corporate network",
            trust_level=TrustLevel.HIGH,
            conditions={
                "network": "corporate_wifi",
                "location": "office",
                "device": "managed"
            },
            allowed_actions=["read", "write", "delete"]
        ),
        AccessPolicy(
            name="remote-access",
            description="Remote work access",
            trust_level=TrustLevel.MEDIUM,
            conditions={
                "network": "home_or_vpn",
                "location": "home_country",
                "device": "managed",
                "mfa": True
            },
            allowed_actions=["read", "write"]
        ),
        AccessPolicy(
            name="public-wifi",
            description="Access from public WiFi",
            trust_level=TrustLevel.LOW,
            conditions={
                "network": "public",
                "mfa": True,
                "device": "managed"
            },
            allowed_actions=["read"]
        )
    ]

    for policy in policies:
        generator.add_access_policy(policy)

    files = generator.generate(Path("./output/zero-trust/context-aware"))

    print(f"✅ Context-aware policies configured")

    print(f"\n🎯 Access contexts:")
    for policy in policies:
        print(f"\n   Policy: {policy.name}")
        print(f"   Trust Level: {policy.trust_level.value}")
        print(f"   Allowed Actions: {', '.join(policy.allowed_actions)}")
    print()


def example_network_microsegmentation():
    """Network microsegmentation for Zero Trust"""
    print("=" * 60)
    print("Example 4: Network Microsegmentation")
    print("=" * 60)

    config = ZeroTrustConfig(
        provider=ZeroTrustProvider.BEYONDCORP,
        enable_network_microsegmentation=True
    )

    generator = ZeroTrustGenerator(config)

    # Define network segments
    generator.add_segment("dmz", "Public-facing services", ["web", "api-gateway"])
    generator.add_segment("app", "Application tier", ["app-server", "cache"])
    generator.add_segment("data", "Data tier", ["database", "analytics"])
    generator.add_segment("management", "Management plane", ["admin", "monitoring"])

    # Define allowed traffic flows
    generator.add_traffic_rule("internet", "dmz", ports=[80, 443])
    generator.add_traffic_rule("dmz", "app", ports=[8080])
    generator.add_traffic_rule("app", "data", ports=[5432, 6379])
    generator.add_traffic_rule("management", "*", ports=[22], protocol="ssh")

    files = generator.generate(Path("./output/zero-trust/microsegmentation"))

    print(f"✅ Microsegmentation configured")

    print(f"\n🌐 Network segments:")
    print(f"   - DMZ (public-facing)")
    print(f"   - Application tier (internal)")
    print(f"   - Data tier (protected)")
    print(f"   - Management plane (admin-only)")

    print(f"\n🔒 Default policy: DENY ALL")
    print(f"   Allow only explicitly permitted traffic")
    print()


def example_identity_aware_proxy():
    """Identity-Aware Proxy (IAP) configuration"""
    print("=" * 60)
    print("Example 5: Identity-Aware Proxy")
    print("=" * 60)

    config = ZeroTrustConfig(
        provider=ZeroTrustProvider.GOOGLE_BEYONDCORP,
        identity_provider=IdentityProvider.GOOGLE_WORKSPACE
    )

    generator = ZeroTrustGenerator(config)

    # Configure IAP for applications
    apps = [
        {"name": "admin-panel", "url": "https://admin.example.com", "groups": ["admins"]},
        {"name": "dashboard", "url": "https://dashboard.example.com", "groups": ["employees"]},
        {"name": "api", "url": "https://api.example.com", "groups": ["developers", "services"]}
    ]

    for app in apps:
        generator.configure_iap(
            app_name=app["name"],
            backend_url=app["url"],
            allowed_groups=app["groups"]
        )

    files = generator.generate(Path("./output/zero-trust/iap"))

    print(f"✅ Identity-Aware Proxy configured")

    print(f"\n🔐 IAP Protection:")
    for app in apps:
        print(f"\n   App: {app['name']}")
        print(f"   URL: {app['url']}")
        print(f"   Access: {', '.join(app['groups'])}")

    print(f"\n✨ Benefits:")
    print(f"   - No VPN required")
    print(f"   - Centralized access control")
    print(f"   - Automatic TLS termination")
    print(f"   - DDoS protection")
    print()


def example_hashicorp_boundary():
    """HashiCorp Boundary for infrastructure access"""
    print("=" * 60)
    print("Example 6: HashiCorp Boundary")
    print("=" * 60)

    config = ZeroTrustConfig(
        provider=ZeroTrustProvider.HASHICORP_BOUNDARY,
        enable_session_recording=True
    )

    generator = ZeroTrustGenerator(config)

    # Configure targets
    generator.add_target("prod-db", "postgresql", host="db.prod.internal", port=5432)
    generator.add_target("prod-redis", "redis", host="cache.prod.internal", port=6379)
    generator.add_target("ssh-bastion", "ssh", host="bastion.prod.internal", port=22)
    generator.add_target("k8s-api", "kubernetes", host="k8s.prod.internal", port=6443)

    # Configure host catalogs
    generator.add_host_catalog("aws-prod", provider="aws", region="us-east-1")
    generator.add_host_catalog("on-prem", provider="static")

    files = generator.generate(Path("./output/zero-trust/boundary"))

    print(f"✅ HashiCorp Boundary configured")

    print(f"\n🎯 Access targets:")
    print(f"   - Production databases")
    print(f"   - Cache servers")
    print(f"   - SSH bastions")
    print(f"   - Kubernetes clusters")

    print(f"\n🔒 Security features:")
    print(f"   ✓ No credential exposure")
    print(f"   ✓ Just-in-time access")
    print(f"   ✓ Session recording")
    print(f"   ✓ MFA enforcement")
    print(f"   ✓ Audit logging")
    print()


def example_continuous_verification():
    """Continuous trust verification"""
    print("=" * 60)
    print("Example 7: Continuous Trust Verification")
    print("=" * 60)

    config = ZeroTrustConfig(
        provider=ZeroTrustProvider.BEYONDCORP,
        enable_continuous_verification=True,
        verification_interval_minutes=5
    )

    generator = ZeroTrustGenerator(config)

    # Configure verification checks
    generator.add_verification_check("device_health", interval=5)
    generator.add_verification_check("user_behavior", interval=10)
    generator.add_verification_check("network_anomaly", interval=1)
    generator.add_verification_check("threat_intelligence", interval=15)

    files = generator.generate(Path("./output/zero-trust/continuous-verification"))

    print(f"✅ Continuous verification enabled")

    print(f"\n🔍 Real-time checks:")
    print(f"   Every 1 min: Network anomaly detection")
    print(f"   Every 5 min: Device health verification")
    print(f"   Every 10 min: User behavior analysis")
    print(f"   Every 15 min: Threat intelligence updates")

    print(f"\n⚡ Automated responses:")
    print(f"   - Step-up authentication for risky actions")
    print(f"   - Session termination on policy violation")
    print(f"   - Device quarantine on compromise")
    print(f"   - Alert security team")
    print()


def example_workload_identity():
    """Workload identity for service-to-service auth"""
    print("=" * 60)
    print("Example 8: Workload Identity")
    print("=" * 60)

    config = ZeroTrustConfig(
        provider=ZeroTrustProvider.BEYONDCORP,
        enable_workload_identity=True
    )

    generator = ZeroTrustGenerator(config)

    # Define workloads
    workloads = [
        {"name": "frontend", "namespace": "prod", "access": ["api", "auth"]},
        {"name": "api", "namespace": "prod", "access": ["database", "cache"]},
        {"name": "worker", "namespace": "prod", "access": ["queue", "database"]},
    ]

    for workload in workloads:
        generator.add_workload(
            name=workload["name"],
            namespace=workload["namespace"],
            allowed_destinations=workload["access"]
        )

    files = generator.generate(Path("./output/zero-trust/workload-identity"))

    print(f"✅ Workload identity configured")

    print(f"\n🔐 Service mesh integration:")
    print(f"   - mTLS for all service-to-service communication")
    print(f"   - SPIFFE/SPIRE for identity")
    print(f"   - Fine-grained authorization policies")

    print(f"\n📊 Workload access matrix:")
    for workload in workloads:
        print(f"\n   {workload['name']} → {', '.join(workload['access'])}")
    print()


def example_zero_trust_monitoring():
    """Zero Trust monitoring and analytics"""
    print("=" * 60)
    print("Example 9: Zero Trust Monitoring")
    print("=" * 60)

    config = ZeroTrustConfig(
        provider=ZeroTrustProvider.BEYONDCORP,
        enable_monitoring=True,
        enable_analytics=True
    )

    generator = ZeroTrustGenerator(config)

    # Configure monitoring
    generator.configure_monitoring(
        log_all_access_decisions=True,
        alert_on_policy_violations=True,
        alert_on_anomalies=True
    )

    # Generate dashboards
    generator.create_dashboard("access-analytics")
    generator.create_dashboard("trust-scores")
    generator.create_dashboard("threat-detection")

    files = generator.generate(Path("./output/zero-trust/monitoring"))

    print(f"✅ Zero Trust monitoring configured")

    print(f"\n📊 Dashboards:")
    print(f"   - Access Analytics")
    print(f"     • Access attempts by user/device/location")
    print(f"     • Policy decisions (allow/deny)")
    print(f"     • Top accessed resources")

    print(f"\n   - Trust Scores")
    print(f"     • User trust score trends")
    print(f"     • Device compliance status")
    print(f"     • Context risk levels")

    print(f"\n   - Threat Detection")
    print(f"     • Anomalous access patterns")
    print(f"     • Failed authentication attempts")
    print(f"     • Compromised device alerts")

    print(f"\n🔔 Alerts configured:")
    print(f"   ⚠️ Policy violation detected")
    print(f"   ⚠️ Unusual access pattern")
    print(f"   ⚠️ Device compliance failure")
    print(f"   ⚠️ Geographical anomaly")
    print()


if __name__ == "__main__":
    print("\n🛡️ Zero Trust Architecture Examples")
    print("=" * 60)
    print()

    # Run all examples
    example_basic_zero_trust()
    example_device_trust()
    example_user_context()
    example_network_microsegmentation()
    example_identity_aware_proxy()
    example_hashicorp_boundary()
    example_continuous_verification()
    example_workload_identity()
    example_zero_trust_monitoring()

    print("=" * 60)
    print("✅ All Zero Trust examples completed!")
    print("=" * 60)
    print("\n🔐 Zero Trust Implementation Roadmap:")
    print("   Phase 1: Identity & Device Trust")
    print("      - Deploy identity provider (Okta/Azure AD)")
    print("      - Implement MDM for device management")
    print("      - Enable MFA for all users")
    print("\n   Phase 2: Network Segmentation")
    print("      - Implement microsegmentation")
    print("      - Deploy Identity-Aware Proxy")
    print("      - Remove VPN access")
    print("\n   Phase 3: Continuous Verification")
    print("      - Enable real-time trust evaluation")
    print("      - Implement behavioral analytics")
    print("      - Deploy automated response")
    print("\n   Phase 4: Monitoring & Optimization")
    print("      - Deploy dashboards and alerts")
    print("      - Fine-tune policies")
    print("      - Regular security assessments")
