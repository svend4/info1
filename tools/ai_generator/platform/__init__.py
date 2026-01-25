"""
Platform Expansion Package

SaaS, multi-cloud, on-premise и marketplace решения.
"""

from .saas_platform import (
    SaaSPlatform,
    Tenant,
    Subscription,
    PricingPlan,
    SubscriptionTier,
    BillingCycle,
    TenantStatus
)

from .cloud_deployment import (
    CloudDeploymentManager,
    CloudProvider,
    DeploymentConfig,
    Deployment,
    DeploymentRegion,
    DeploymentStatus,
    CloudCredentials
)

from .on_premise import (
    OnPremiseDeployment,
    OnPremiseConfig,
    DeploymentMode,
    DatabaseType
)

from .white_label import (
    WhiteLabelManager,
    WhiteLabelInstance,
    BrandingConfig
)

from .marketplace import (
    MarketplaceManager,
    MarketplaceListing,
    Purchase,
    ListingType,
    PricingModel
)

__all__ = [
    # SaaS Platform
    'SaaSPlatform',
    'Tenant',
    'Subscription',
    'PricingPlan',
    'SubscriptionTier',
    'BillingCycle',
    'TenantStatus',

    # Cloud Deployment
    'CloudDeploymentManager',
    'CloudProvider',
    'DeploymentConfig',
    'Deployment',
    'DeploymentRegion',
    'DeploymentStatus',
    'CloudCredentials',

    # On-Premise
    'OnPremiseDeployment',
    'OnPremiseConfig',
    'DeploymentMode',
    'DatabaseType',

    # White Label
    'WhiteLabelManager',
    'WhiteLabelInstance',
    'BrandingConfig',

    # Marketplace
    'MarketplaceManager',
    'MarketplaceListing',
    'Purchase',
    'ListingType',
    'PricingModel'
]

__version__ = '1.0.0'
