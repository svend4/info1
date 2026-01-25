"""
Enterprise Features Package

Enterprise-grade возможности для корпоративного использования AI Generator.
"""

from .rbac import RBACManager, Permission, Role, User, require_permission
from .audit_log import AuditLogger, EventType, Severity, AuditEvent
from .organization import (
    OrganizationManager,
    Organization,
    Team,
    TeamMember,
    OrganizationPlan,
    TeamRole
)
from .template_policies import (
    TemplatePolicyManager,
    TemplateStatus,
    PolicyViolationSeverity,
    TemplateReview
)

__all__ = [
    # RBAC
    'RBACManager',
    'Permission',
    'Role',
    'User',
    'require_permission',

    # Audit
    'AuditLogger',
    'EventType',
    'Severity',
    'AuditEvent',

    # Organization
    'OrganizationManager',
    'Organization',
    'Team',
    'TeamMember',
    'OrganizationPlan',
    'TeamRole',

    # Policies
    'TemplatePolicyManager',
    'TemplateStatus',
    'PolicyViolationSeverity',
    'TemplateReview'
]

__version__ = '1.0.0'
