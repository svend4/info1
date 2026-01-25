#!/usr/bin/env python3
"""
Example: Enterprise SSO/SAML Integration

This example demonstrates how to generate SSO integration code
for Auth0, Okta, Azure AD, and Google Workspace.
"""

from pathlib import Path
from tools.ai_generator.security import (
    SSOGenerator,
    SSOConfig,
    SSOProvider,
    SAMLConfig
)


def example_okta_integration():
    """Generate Okta SSO integration"""
    print("=" * 60)
    print("Example 1: Okta SSO Integration")
    print("=" * 60)

    config = SSOConfig(
        provider=SSOProvider.OKTA,
        entity_id="https://myapp.example.com",
        acs_url="https://myapp.example.com/saml/acs",
        slo_url="https://myapp.example.com/saml/slo",
        enable_encryption=True
    )

    generator = SSOGenerator(config)
    files = generator.generate(Path("./output/okta-sso"))

    print(f"\n✅ Generated {len(files)} files:")
    for filename in files.keys():
        print(f"   - {filename}")
    print()


def example_azure_ad_integration():
    """Generate Azure AD SSO integration"""
    print("=" * 60)
    print("Example 2: Azure AD SSO Integration")
    print("=" * 60)

    config = SSOConfig(
        provider=SSOProvider.AZURE_AD,
        entity_id="https://enterprise-app.com",
        acs_url="https://enterprise-app.com/saml/acs",
        enable_mfa=True,
        require_signed_assertions=True
    )

    generator = SSOGenerator(config)
    files = generator.generate(Path("./output/azure-ad-sso"))

    print(f"\n✅ Generated {len(files)} files")
    print("📝 Configuration includes:")
    print("   - Multi-factor authentication (MFA)")
    print("   - Signed SAML assertions")
    print("   - Azure AD-specific claim mappings")
    print()


def example_google_workspace():
    """Generate Google Workspace SSO integration"""
    print("=" * 60)
    print("Example 3: Google Workspace SSO")
    print("=" * 60)

    config = SSOConfig(
        provider=SSOProvider.GOOGLE_WORKSPACE,
        entity_id="https://saas-app.example.com",
        acs_url="https://saas-app.example.com/saml/acs"
    )

    generator = SSOGenerator(config)

    # Add custom attribute mappings
    generator.add_attribute_mapping("email", "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress")
    generator.add_attribute_mapping("firstName", "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/givenname")
    generator.add_attribute_mapping("lastName", "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/surname")

    files = generator.generate(Path("./output/google-workspace-sso"))

    print(f"\n✅ Generated {len(files)} files")
    print("📋 Custom attribute mappings configured")
    print()


def example_auth0_with_spa():
    """Generate Auth0 integration for Single Page Application"""
    print("=" * 60)
    print("Example 4: Auth0 for SPA (React)")
    print("=" * 60)

    config = SSOConfig(
        provider=SSOProvider.AUTH0,
        entity_id="https://spa.example.com",
        acs_url="https://spa.example.com/callback",
        enable_pkce=True  # PKCE for SPAs
    )

    generator = SSOGenerator(config)
    files = generator.generate(Path("./output/auth0-spa"))

    print(f"\n✅ Generated {len(files)} files:")
    for filename in files.keys():
        print(f"   - {filename}")

    print("\n🔒 Security features enabled:")
    print("   - PKCE (Proof Key for Code Exchange)")
    print("   - Token rotation")
    print("   - Refresh token handling")
    print()


def example_multi_provider_setup():
    """Generate configuration for multiple SSO providers"""
    print("=" * 60)
    print("Example 5: Multi-Provider SSO Setup")
    print("=" * 60)

    providers = [
        (SSOProvider.OKTA, "Enterprise customers"),
        (SSOProvider.GOOGLE_WORKSPACE, "Google Workspace users"),
        (SSOProvider.AZURE_AD, "Microsoft 365 users")
    ]

    for provider, description in providers:
        config = SSOConfig(
            provider=provider,
            entity_id=f"https://app.example.com/{provider.value}",
            acs_url=f"https://app.example.com/saml/{provider.value}/acs"
        )

        generator = SSOGenerator(config)
        files = generator.generate(Path(f"./output/multi-sso/{provider.value}"))

        print(f"✅ {provider.value.upper()}: {len(files)} files - {description}")

    print("\n📦 Multi-provider SSO configured successfully")
    print()


def example_saml_metadata():
    """Generate and export SAML metadata"""
    print("=" * 60)
    print("Example 6: SAML Metadata Export")
    print("=" * 60)

    config = SSOConfig(
        provider=SSOProvider.OKTA,
        entity_id="https://myapp.example.com",
        acs_url="https://myapp.example.com/saml/acs",
        slo_url="https://myapp.example.com/saml/slo"
    )

    generator = SSOGenerator(config)

    # Generate metadata
    metadata = generator.generate_metadata()

    print("✅ SAML Metadata generated")
    print(f"📄 Metadata length: {len(metadata)} characters")
    print("\n🔑 Metadata includes:")
    print("   - Entity ID and service endpoints")
    print("   - X.509 certificate for signature validation")
    print("   - Supported NameID formats")
    print("   - Assertion Consumer Service (ACS) bindings")
    print()


if __name__ == "__main__":
    print("\n🔐 SSO/SAML Integration Examples")
    print("=" * 60)
    print()

    # Run all examples
    example_okta_integration()
    example_azure_ad_integration()
    example_google_workspace()
    example_auth0_with_spa()
    example_multi_provider_setup()
    example_saml_metadata()

    print("=" * 60)
    print("✅ All SSO integration examples completed!")
    print("=" * 60)
    print("\n📁 Generated files in ./output/ directory")
    print("📚 Next steps:")
    print("   1. Review generated configuration files")
    print("   2. Update with your actual SSO provider credentials")
    print("   3. Deploy to your application")
    print("   4. Test SSO flow end-to-end")
