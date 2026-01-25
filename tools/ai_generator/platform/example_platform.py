#!/usr/bin/env python3
"""
Platform Expansion - Complete Example

Демонстрация SaaS, Cloud, On-Premise, White-Label и Marketplace.
"""

from platform import (
    SaaSPlatform,
    CloudDeploymentManager,
    OnPremiseDeployment,
    WhiteLabelManager,
    MarketplaceManager,
    SubscriptionTier,
    CloudProvider,
    DeploymentMode,
    DatabaseType,
    BrandingConfig,
    ListingType,
    PricingModel
)


def demo_saas_platform():
    """Демонстрация SaaS платформы"""
    print("=" * 70)
    print("SaaS PLATFORM DEMO")
    print("=" * 70)

    saas = SaaSPlatform()

    # Создание тенанта
    tenant = saas.create_tenant(
        organization_name="Acme Corp",
        admin_email="admin@acme.com",
        tier=SubscriptionTier.PROFESSIONAL,
        trial_days=14
    )

    print(f"\n✅ Created tenant: {tenant.organization_name}")
    print(f"   Domain: {tenant.domain}")
    print(f"   Tier: {tenant.subscription_tier.value}")
    print(f"   Status: {tenant.status.value}")

    # Отслеживание использования
    saas.track_usage(tenant.tenant_id, 'projects_created', 5)
    saas.track_usage(tenant.tenant_id, 'api_calls', 150)

    # Аналитика
    analytics = saas.get_tenant_analytics(tenant.tenant_id)
    print(f"\n📊 Analytics:")
    print(f"   Projects: {analytics['usage_stats']['projects_created']}")
    print(f"   API Calls: {analytics['usage_stats']['api_calls']}")

    # Platform stats
    stats = saas.get_platform_stats()
    print(f"\n🌐 Platform Stats:")
    print(f"   Total Tenants: {stats['total_tenants']}")
    print(f"   Monthly Revenue: ${stats['monthly_revenue']:.2f}")


def demo_cloud_deployment():
    """Демонстрация Cloud Deployment"""
    print("\n" + "=" * 70)
    print("MULTI-CLOUD DEPLOYMENT DEMO")
    print("=" * 70)

    cloud = CloudDeploymentManager()

    # Конфигурация для AWS
    config = cloud.create_deployment_config(
        app_name="aigenerator-prod",
        provider=CloudProvider.AWS,
        region="us-east-1",
        size='medium',
        auto_scaling=True
    )

    print(f"\n✅ Created deployment config:")
    print(f"   Provider: {config.provider.value}")
    print(f"   Region: {config.region}")
    print(f"   Instance: {config.instance_type}")
    print(f"   Auto-scaling: {config.auto_scaling}")

    # Развертывание
    deployment = cloud.deploy(
        tenant_id="tenant-123",
        config=config
    )

    print(f"\n🚀 Deployment complete:")
    print(f"   ID: {deployment.deployment_id}")
    print(f"   Status: {deployment.status.value}")
    print(f"   URL: {deployment.endpoint_url}")
    print(f"   Monthly cost: ${deployment.cost_estimate:.2f}")

    # Terraform config
    terraform = cloud.generate_terraform_config(config)
    print(f"\n📄 Terraform config generated ({len(terraform)} chars)")


def demo_onpremise():
    """Демонстрация On-Premise"""
    print("\n" + "=" * 70)
    print("ON-PREMISE DEPLOYMENT DEMO")
    print("=" * 70)

    onprem = OnPremiseDeployment()

    from platform.on_premise import OnPremiseConfig

    config = OnPremiseConfig(
        installation_name="aigenerator-enterprise",
        deployment_mode=DeploymentMode.KUBERNETES,
        database=DatabaseType.POSTGRESQL,
        high_availability=True,
        backup_enabled=True,
        monitoring_enabled=True,
        load_balancer=True,
        ssl_enabled=True,
        custom_domain="ai.company.com"
    )

    print(f"\n✅ On-Premise Configuration:")
    print(f"   Mode: {config.deployment_mode.value}")
    print(f"   Database: {config.database.value}")
    print(f"   HA: {config.high_availability}")
    print(f"   Domain: {config.custom_domain}")

    # Генерация манифестов
    manifests = onprem.generate_kubernetes_manifests(config)
    print(f"\n📦 Generated {len(manifests)} Kubernetes manifests:")
    for filename in manifests.keys():
        print(f"   - {filename}")

    # Docker Compose
    compose = onprem.generate_docker_compose(config)
    print(f"\n🐳 Docker Compose: {len(compose)} chars")

    # Installation package
    onprem.save_installation_package(config, './onprem_package')
    print(f"\n✅ Installation package saved")


def demo_white_label():
    """Демонстрация White Label"""
    print("\n" + "=" * 70)
    print("WHITE LABEL DEMO")
    print("=" * 70)

    wl = WhiteLabelManager()

    branding = BrandingConfig(
        partner_name="TechPartner Inc",
        company_name="AI Solutions Pro",
        logo_url="https://partner.com/logo.png",
        favicon_url="https://partner.com/favicon.ico",
        primary_color="#0066cc",
        secondary_color="#00cc66",
        custom_domain="aisolutions.pro",
        support_email="support@aisolutions.pro"
    )

    instance = wl.create_instance(
        partner_id="partner-123",
        branding=branding,
        features=['ai_generation', 'templates', 'analytics']
    )

    print(f"\n✅ Created white-label instance:")
    print(f"   Partner: {branding.partner_name}")
    print(f"   Brand: {branding.company_name}")
    print(f"   Domain: {branding.custom_domain}")
    print(f"   Features: {len(instance.features_enabled)}")

    # CSS
    css = wl.generate_custom_css(branding)
    print(f"\n🎨 Custom CSS: {len(css)} chars")

    # Export
    wl.export_package(instance.instance_id, './whitelabel_package')
    print(f"✅ Package exported")


def demo_marketplace():
    """Демонстрация Marketplace"""
    print("\n" + "=" * 70)
    print("MARKETPLACE & MONETIZATION DEMO")
    print("=" * 70)

    marketplace = MarketplaceManager()

    # Создание листингов
    template1 = marketplace.create_listing(
        seller_id="seller-1",
        title="Professional React Template",
        description="Full-stack React template with TypeScript",
        listing_type=ListingType.TEMPLATE,
        price=49.99,
        pricing_model=PricingModel.ONE_TIME,
        commission_rate=30.0
    )

    plugin1 = marketplace.create_listing(
        seller_id="seller-2",
        title="AI Code Reviewer Plugin",
        description="Automated code review with AI",
        listing_type=ListingType.PLUGIN,
        price=9.99,
        pricing_model=PricingModel.SUBSCRIPTION,
        commission_rate=25.0
    )

    print(f"\n✅ Created listings:")
    print(f"   Template: {template1.title} - ${template1.price}")
    print(f"   Plugin: {plugin1.title} - ${plugin1.price}/mo")

    # Покупка
    purchase = marketplace.purchase_listing(
        listing_id=template1.listing_id,
        buyer_id="buyer-123"
    )

    print(f"\n💰 Purchase completed:")
    print(f"   Amount: ${purchase.amount}")
    print(f"   Commission: ${purchase.commission}")
    print(f"   Seller payout: ${purchase.seller_payout}")

    # Seller earnings
    earnings = marketplace.get_seller_earnings("seller-1")
    print(f"\n📊 Seller Earnings:")
    print(f"   Revenue: ${earnings['total_revenue']:.2f}")
    print(f"   Payout: ${earnings['total_payout']:.2f}")
    print(f"   Sales: {earnings['total_sales']}")

    # Marketplace stats
    stats = marketplace.get_marketplace_stats()
    print(f"\n🏪 Marketplace Stats:")
    print(f"   Listings: {stats['total_listings']}")
    print(f"   Purchases: {stats['total_purchases']}")
    print(f"   Revenue: ${stats['total_revenue']:.2f}")


def main():
    """Главная демонстрация"""
    print("\n" + "=" * 70)
    print("PLATFORM EXPANSION - COMPLETE DEMO")
    print("=" * 70)

    try:
        demo_saas_platform()
        demo_cloud_deployment()
        demo_onpremise()
        demo_white_label()
        demo_marketplace()

        print("\n" + "=" * 70)
        print("✅ ALL DEMOS COMPLETE")
        print("=" * 70)
        print("\n🎉 Platform Expansion modules fully functional!")
        print("\nModules demonstrated:")
        print("  ✅ SaaS Platform - Multi-tenant SaaS with billing")
        print("  ✅ Cloud Deployment - AWS/GCP/Azure deployment")
        print("  ✅ On-Premise - Enterprise self-hosted solution")
        print("  ✅ White Label - Partner customization")
        print("  ✅ Marketplace - Monetization & template sales")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
