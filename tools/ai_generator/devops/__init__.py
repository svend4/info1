"""
DevOps Excellence Package

GitOps, Infrastructure as Code, Observability, и Policy as Code.
"""

from .gitops_generator import (
    GitOpsGenerator,
    GitOpsConfig,
    AppConfig,
    GitOpsTool,
    SyncPolicy
)

from .infrastructure_generator import (
    InfrastructureGenerator,
    IaCConfig,
    InfraResource,
    IaCTool,
    CloudProvider,
    ResourceType
)

from .observability_stack import (
    ObservabilityGenerator,
    ObservabilityConfig,
    PrometheusTarget,
    AlertRule,
    GrafanaDashboard,
    ObservabilityTool,
    MetricType
)

from .policy_as_code import (
    PolicyAsCodeGenerator,
    PolicyConfig,
    PolicyRule,
    PolicyEngine,
    PolicyAction,
    ResourceKind
)

__all__ = [
    # GitOps Generator
    'GitOpsGenerator',
    'GitOpsConfig',
    'AppConfig',
    'GitOpsTool',
    'SyncPolicy',

    # Infrastructure Generator
    'InfrastructureGenerator',
    'IaCConfig',
    'InfraResource',
    'IaCTool',
    'CloudProvider',
    'ResourceType',

    # Observability Stack
    'ObservabilityGenerator',
    'ObservabilityConfig',
    'PrometheusTarget',
    'AlertRule',
    'GrafanaDashboard',
    'ObservabilityTool',
    'MetricType',

    # Policy as Code
    'PolicyAsCodeGenerator',
    'PolicyConfig',
    'PolicyRule',
    'PolicyEngine',
    'PolicyAction',
    'ResourceKind'
]

__version__ = '1.0.0'
