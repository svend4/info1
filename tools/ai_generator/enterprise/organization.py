#!/usr/bin/env python3
"""
Organization & Team Management

Система управления организациями и командами:
- Organization creation and management
- Team structure
- Member management
- Organization settings
- Billing management
- Resource quotas
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set
from datetime import datetime
from enum import Enum
import json
from pathlib import Path
import hashlib


class OrganizationPlan(Enum):
    """Organization subscription plans"""
    FREE = "free"
    STARTER = "starter"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


class TeamRole(Enum):
    """Team member roles"""
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"
    VIEWER = "viewer"


@dataclass
class OrganizationSettings:
    """Organization settings"""
    allow_public_templates: bool = True
    require_2fa: bool = False
    allowed_domains: List[str] = field(default_factory=list)
    sso_enabled: bool = False
    sso_provider: Optional[str] = None
    audit_retention_days: int = 90
    custom_branding: bool = False
    api_rate_limit: int = 1000  # requests per hour


@dataclass
class ResourceQuota:
    """Resource usage quotas"""
    max_users: int
    max_teams: int
    max_projects: int
    max_templates: int
    max_api_calls_per_month: int
    max_storage_gb: int

    # Current usage
    current_users: int = 0
    current_teams: int = 0
    current_projects: int = 0
    current_templates: int = 0
    current_api_calls_this_month: int = 0
    current_storage_gb: float = 0.0

    def is_at_limit(self, resource: str) -> bool:
        """Check if at resource limit"""
        limits = {
            'users': (self.current_users, self.max_users),
            'teams': (self.current_teams, self.max_teams),
            'projects': (self.current_projects, self.max_projects),
            'templates': (self.current_templates, self.max_templates),
            'api_calls': (self.current_api_calls_this_month, self.max_api_calls_per_month),
            'storage': (self.current_storage_gb, self.max_storage_gb)
        }

        if resource in limits:
            current, maximum = limits[resource]
            return current >= maximum

        return False


@dataclass
class Organization:
    """Organization entity"""
    id: str
    name: str
    slug: str  # URL-friendly name
    plan: OrganizationPlan
    owner_id: str
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    settings: OrganizationSettings = field(default_factory=OrganizationSettings)
    quota: Optional[ResourceQuota] = None
    billing_email: Optional[str] = None
    is_active: bool = True


@dataclass
class Team:
    """Team within organization"""
    id: str
    organization_id: str
    name: str
    description: str
    created_by: str
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    is_active: bool = True


@dataclass
class TeamMember:
    """Team member"""
    team_id: str
    user_id: str
    role: TeamRole
    joined_at: str = field(default_factory=lambda: datetime.now().isoformat())


class OrganizationManager:
    """
    Organization Manager

    Manages organizations, teams, and members.
    """

    # Plan-specific quotas
    PLAN_QUOTAS = {
        OrganizationPlan.FREE: ResourceQuota(
            max_users=5,
            max_teams=1,
            max_projects=10,
            max_templates=5,
            max_api_calls_per_month=1000,
            max_storage_gb=1
        ),
        OrganizationPlan.STARTER: ResourceQuota(
            max_users=20,
            max_teams=5,
            max_projects=50,
            max_templates=20,
            max_api_calls_per_month=10000,
            max_storage_gb=10
        ),
        OrganizationPlan.PROFESSIONAL: ResourceQuota(
            max_users=100,
            max_teams=20,
            max_projects=500,
            max_templates=100,
            max_api_calls_per_month=100000,
            max_storage_gb=100
        ),
        OrganizationPlan.ENTERPRISE: ResourceQuota(
            max_users=1000,
            max_teams=100,
            max_projects=10000,
            max_templates=1000,
            max_api_calls_per_month=1000000,
            max_storage_gb=1000
        )
    }

    def __init__(self, storage_path: Optional[Path] = None):
        """
        Args:
            storage_path: Path to storage directory
        """
        self.storage_path = storage_path or Path.home() / '.ai_generator' / 'organizations'
        self.storage_path.mkdir(parents=True, exist_ok=True)

        self.orgs_file = self.storage_path / 'organizations.json'
        self.teams_file = self.storage_path / 'teams.json'
        self.team_members_file = self.storage_path / 'team_members.json'

        self.organizations = self._load_organizations()
        self.teams = self._load_teams()
        self.team_members = self._load_team_members()

    def _load_organizations(self) -> Dict[str, Organization]:
        """Load organizations"""
        if self.orgs_file.exists():
            with open(self.orgs_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                orgs = {}
                for org_id, org_data in data.items():
                    # Parse settings
                    settings_data = org_data.get('settings', {})
                    settings = OrganizationSettings(**settings_data)

                    # Parse quota
                    quota_data = org_data.get('quota')
                    quota = ResourceQuota(**quota_data) if quota_data else None

                    orgs[org_id] = Organization(
                        id=org_data['id'],
                        name=org_data['name'],
                        slug=org_data['slug'],
                        plan=OrganizationPlan(org_data['plan']),
                        owner_id=org_data['owner_id'],
                        created_at=org_data['created_at'],
                        settings=settings,
                        quota=quota,
                        billing_email=org_data.get('billing_email'),
                        is_active=org_data.get('is_active', True)
                    )
                return orgs
        return {}

    def _save_organizations(self):
        """Save organizations"""
        data = {}
        for org_id, org in self.organizations.items():
            data[org_id] = {
                'id': org.id,
                'name': org.name,
                'slug': org.slug,
                'plan': org.plan.value,
                'owner_id': org.owner_id,
                'created_at': org.created_at,
                'settings': {
                    'allow_public_templates': org.settings.allow_public_templates,
                    'require_2fa': org.settings.require_2fa,
                    'allowed_domains': org.settings.allowed_domains,
                    'sso_enabled': org.settings.sso_enabled,
                    'sso_provider': org.settings.sso_provider,
                    'audit_retention_days': org.settings.audit_retention_days,
                    'custom_branding': org.settings.custom_branding,
                    'api_rate_limit': org.settings.api_rate_limit
                },
                'quota': {
                    'max_users': org.quota.max_users,
                    'max_teams': org.quota.max_teams,
                    'max_projects': org.quota.max_projects,
                    'max_templates': org.quota.max_templates,
                    'max_api_calls_per_month': org.quota.max_api_calls_per_month,
                    'max_storage_gb': org.quota.max_storage_gb,
                    'current_users': org.quota.current_users,
                    'current_teams': org.quota.current_teams,
                    'current_projects': org.quota.current_projects,
                    'current_templates': org.quota.current_templates,
                    'current_api_calls_this_month': org.quota.current_api_calls_this_month,
                    'current_storage_gb': org.quota.current_storage_gb
                } if org.quota else None,
                'billing_email': org.billing_email,
                'is_active': org.is_active
            }

        with open(self.orgs_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

    def _load_teams(self) -> Dict[str, Team]:
        """Load teams"""
        if self.teams_file.exists():
            with open(self.teams_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return {
                    team_id: Team(**team_data)
                    for team_id, team_data in data.items()
                }
        return {}

    def _save_teams(self):
        """Save teams"""
        data = {
            team_id: {
                'id': team.id,
                'organization_id': team.organization_id,
                'name': team.name,
                'description': team.description,
                'created_by': team.created_by,
                'created_at': team.created_at,
                'is_active': team.is_active
            }
            for team_id, team in self.teams.items()
        }

        with open(self.teams_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

    def _load_team_members(self) -> List[TeamMember]:
        """Load team members"""
        if self.team_members_file.exists():
            with open(self.team_members_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return [
                    TeamMember(
                        team_id=item['team_id'],
                        user_id=item['user_id'],
                        role=TeamRole(item['role']),
                        joined_at=item['joined_at']
                    )
                    for item in data
                ]
        return []

    def _save_team_members(self):
        """Save team members"""
        data = [
            {
                'team_id': member.team_id,
                'user_id': member.user_id,
                'role': member.role.value,
                'joined_at': member.joined_at
            }
            for member in self.team_members
        ]

        with open(self.team_members_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

    def create_organization(
        self,
        name: str,
        slug: str,
        owner_id: str,
        plan: OrganizationPlan = OrganizationPlan.FREE,
        billing_email: Optional[str] = None
    ) -> Organization:
        """
        Create new organization

        Args:
            name: Organization name
            slug: URL-friendly slug
            owner_id: Owner user ID
            plan: Subscription plan
            billing_email: Billing email

        Returns:
            Created organization
        """
        # Check if slug already exists
        for org in self.organizations.values():
            if org.slug == slug:
                raise ValueError(f"Organization slug '{slug}' already exists")

        # Generate ID
        org_id = hashlib.md5(f"{name}{datetime.now().isoformat()}".encode()).hexdigest()[:12]

        # Get plan quota
        quota = self.PLAN_QUOTAS[plan]

        org = Organization(
            id=org_id,
            name=name,
            slug=slug,
            plan=plan,
            owner_id=owner_id,
            quota=quota,
            billing_email=billing_email or None
        )

        self.organizations[org_id] = org
        self._save_organizations()

        print(f"✅ Organization created: {name} ({org_id})")
        print(f"   Plan: {plan.value}")
        print(f"   Quotas: {quota.max_users} users, {quota.max_projects} projects")

        return org

    def create_team(
        self,
        organization_id: str,
        name: str,
        description: str,
        created_by: str
    ) -> Team:
        """
        Create team within organization

        Args:
            organization_id: Organization ID
            name: Team name
            description: Team description
            created_by: User ID creating team

        Returns:
            Created team
        """
        if organization_id not in self.organizations:
            raise ValueError(f"Organization {organization_id} not found")

        org = self.organizations[organization_id]

        # Check quota
        if org.quota and org.quota.is_at_limit('teams'):
            raise ValueError(f"Team limit reached ({org.quota.max_teams})")

        # Generate ID
        team_id = hashlib.md5(f"{name}{datetime.now().isoformat()}".encode()).hexdigest()[:12]

        team = Team(
            id=team_id,
            organization_id=organization_id,
            name=name,
            description=description,
            created_by=created_by
        )

        self.teams[team_id] = team

        # Update quota
        if org.quota:
            org.quota.current_teams += 1

        self._save_teams()
        self._save_organizations()

        print(f"✅ Team created: {name} ({team_id})")

        return team

    def add_team_member(
        self,
        team_id: str,
        user_id: str,
        role: TeamRole = TeamRole.MEMBER
    ):
        """
        Add member to team

        Args:
            team_id: Team ID
            user_id: User ID
            role: Team role
        """
        if team_id not in self.teams:
            raise ValueError(f"Team {team_id} not found")

        # Check if already member
        for member in self.team_members:
            if member.team_id == team_id and member.user_id == user_id:
                raise ValueError(f"User {user_id} already in team")

        member = TeamMember(
            team_id=team_id,
            user_id=user_id,
            role=role
        )

        self.team_members.append(member)
        self._save_team_members()

        print(f"✅ User {user_id} added to team {self.teams[team_id].name} as {role.value}")

    def remove_team_member(self, team_id: str, user_id: str):
        """Remove member from team"""
        self.team_members = [
            m for m in self.team_members
            if not (m.team_id == team_id and m.user_id == user_id)
        ]
        self._save_team_members()

        print(f"✅ User {user_id} removed from team")

    def get_team_members(self, team_id: str) -> List[TeamMember]:
        """Get all members of a team"""
        return [m for m in self.team_members if m.team_id == team_id]

    def get_user_teams(self, user_id: str) -> List[Team]:
        """Get all teams user is member of"""
        team_ids = set(m.team_id for m in self.team_members if m.user_id == user_id)
        return [self.teams[tid] for tid in team_ids if tid in self.teams]

    def get_organization_teams(self, organization_id: str) -> List[Team]:
        """Get all teams in organization"""
        return [
            team for team in self.teams.values()
            if team.organization_id == organization_id
        ]

    def update_organization_settings(
        self,
        organization_id: str,
        settings: Dict
    ):
        """
        Update organization settings

        Args:
            organization_id: Organization ID
            settings: Settings to update
        """
        if organization_id not in self.organizations:
            raise ValueError(f"Organization {organization_id} not found")

        org = self.organizations[organization_id]

        # Update settings
        for key, value in settings.items():
            if hasattr(org.settings, key):
                setattr(org.settings, key, value)

        self._save_organizations()
        print(f"✅ Organization settings updated")

    def upgrade_plan(
        self,
        organization_id: str,
        new_plan: OrganizationPlan
    ):
        """
        Upgrade organization plan

        Args:
            organization_id: Organization ID
            new_plan: New plan
        """
        if organization_id not in self.organizations:
            raise ValueError(f"Organization {organization_id} not found")

        org = self.organizations[organization_id]

        # Get new quota
        new_quota = self.PLAN_QUOTAS[new_plan]

        # Preserve current usage
        new_quota.current_users = org.quota.current_users if org.quota else 0
        new_quota.current_teams = org.quota.current_teams if org.quota else 0
        new_quota.current_projects = org.quota.current_projects if org.quota else 0
        new_quota.current_templates = org.quota.current_templates if org.quota else 0
        new_quota.current_api_calls_this_month = org.quota.current_api_calls_this_month if org.quota else 0
        new_quota.current_storage_gb = org.quota.current_storage_gb if org.quota else 0

        org.plan = new_plan
        org.quota = new_quota

        self._save_organizations()

        print(f"✅ Organization upgraded to {new_plan.value}")
        print(f"   New quotas: {new_quota.max_users} users, {new_quota.max_projects} projects")

    def get_usage_stats(self, organization_id: str) -> Dict:
        """Get organization usage statistics"""
        if organization_id not in self.organizations:
            raise ValueError(f"Organization {organization_id} not found")

        org = self.organizations[organization_id]
        quota = org.quota

        if not quota:
            return {}

        return {
            'users': {
                'current': quota.current_users,
                'limit': quota.max_users,
                'percentage': round(quota.current_users / quota.max_users * 100, 1)
            },
            'teams': {
                'current': quota.current_teams,
                'limit': quota.max_teams,
                'percentage': round(quota.current_teams / quota.max_teams * 100, 1) if quota.max_teams > 0 else 0
            },
            'projects': {
                'current': quota.current_projects,
                'limit': quota.max_projects,
                'percentage': round(quota.current_projects / quota.max_projects * 100, 1)
            },
            'api_calls_this_month': {
                'current': quota.current_api_calls_this_month,
                'limit': quota.max_api_calls_per_month,
                'percentage': round(quota.current_api_calls_this_month / quota.max_api_calls_per_month * 100, 1)
            }
        }


if __name__ == '__main__':
    print("="*70)
    print("ORGANIZATION & TEAM MANAGEMENT")
    print("="*70)

    # Demo
    org_manager = OrganizationManager()

    # Create organization
    org = org_manager.create_organization(
        name='Acme Corp',
        slug='acme-corp',
        owner_id='user123',
        plan=OrganizationPlan.PROFESSIONAL,
        billing_email='billing@acme.com'
    )

    # Create team
    team = org_manager.create_team(
        organization_id=org.id,
        name='Engineering',
        description='Engineering team',
        created_by='user123'
    )

    # Add members
    org_manager.add_team_member(team.id, 'user456', TeamRole.ADMIN)
    org_manager.add_team_member(team.id, 'user789', TeamRole.MEMBER)

    # Get usage stats
    stats = org_manager.get_usage_stats(org.id)
    print(f"\n📊 Usage Statistics:")
    print(f"   Teams: {stats['teams']['current']}/{stats['teams']['limit']} ({stats['teams']['percentage']}%)")
    print(f"   Projects: {stats['projects']['current']}/{stats['projects']['limit']}")
