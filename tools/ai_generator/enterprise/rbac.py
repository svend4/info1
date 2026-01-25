#!/usr/bin/env python3
"""
Role-Based Access Control (RBAC) System

Система управления правами доступа для enterprise deployment:
- Role definitions (Admin, Developer, Viewer, etc.)
- Permission management
- User-role assignments
- Resource-level permissions
- Permission inheritance
"""

from enum import Enum
from typing import List, Set, Dict, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json
from pathlib import Path


class Permission(Enum):
    """Доступные permissions"""
    # Project permissions
    PROJECT_CREATE = "project:create"
    PROJECT_READ = "project:read"
    PROJECT_UPDATE = "project:update"
    PROJECT_DELETE = "project:delete"

    # Template permissions
    TEMPLATE_CREATE = "template:create"
    TEMPLATE_READ = "template:read"
    TEMPLATE_UPDATE = "template:update"
    TEMPLATE_DELETE = "template:delete"
    TEMPLATE_PUBLISH = "template:publish"

    # Organization permissions
    ORG_MANAGE = "org:manage"
    ORG_SETTINGS = "org:settings"
    ORG_BILLING = "org:billing"

    # User management permissions
    USER_CREATE = "user:create"
    USER_READ = "user:read"
    USER_UPDATE = "user:update"
    USER_DELETE = "user:delete"
    USER_INVITE = "user:invite"

    # Team permissions
    TEAM_CREATE = "team:create"
    TEAM_MANAGE = "team:manage"
    TEAM_DELETE = "team:delete"

    # API permissions
    API_KEY_CREATE = "api:key:create"
    API_KEY_REVOKE = "api:key:revoke"
    API_ADMIN = "api:admin"

    # Audit permissions
    AUDIT_READ = "audit:read"
    AUDIT_EXPORT = "audit:export"

    # Analytics permissions
    ANALYTICS_READ = "analytics:read"
    ANALYTICS_EXPORT = "analytics:export"


@dataclass
class Role:
    """Role definition"""
    name: str
    description: str
    permissions: Set[Permission]
    inherits_from: Optional[str] = None
    is_system: bool = False  # System roles нельзя удалить
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class User:
    """User entity"""
    id: str
    email: str
    name: str
    roles: List[str] = field(default_factory=list)
    organization_id: Optional[str] = None
    team_ids: List[str] = field(default_factory=list)
    is_active: bool = True
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    last_login: Optional[str] = None


@dataclass
class ResourcePermission:
    """Resource-level permission"""
    resource_type: str  # project, template, team
    resource_id: str
    user_id: str
    permissions: Set[Permission]
    granted_by: str
    granted_at: str = field(default_factory=lambda: datetime.now().isoformat())


class RBACManager:
    """
    RBAC Manager

    Manages roles, permissions, and access control.
    """

    # Predefined system roles
    SYSTEM_ROLES = {
        'admin': Role(
            name='admin',
            description='Full system access',
            permissions={
                Permission.PROJECT_CREATE, Permission.PROJECT_READ,
                Permission.PROJECT_UPDATE, Permission.PROJECT_DELETE,
                Permission.TEMPLATE_CREATE, Permission.TEMPLATE_READ,
                Permission.TEMPLATE_UPDATE, Permission.TEMPLATE_DELETE,
                Permission.TEMPLATE_PUBLISH,
                Permission.ORG_MANAGE, Permission.ORG_SETTINGS, Permission.ORG_BILLING,
                Permission.USER_CREATE, Permission.USER_READ,
                Permission.USER_UPDATE, Permission.USER_DELETE, Permission.USER_INVITE,
                Permission.TEAM_CREATE, Permission.TEAM_MANAGE, Permission.TEAM_DELETE,
                Permission.API_KEY_CREATE, Permission.API_KEY_REVOKE, Permission.API_ADMIN,
                Permission.AUDIT_READ, Permission.AUDIT_EXPORT,
                Permission.ANALYTICS_READ, Permission.ANALYTICS_EXPORT
            },
            is_system=True
        ),
        'developer': Role(
            name='developer',
            description='Can create and manage projects and templates',
            permissions={
                Permission.PROJECT_CREATE, Permission.PROJECT_READ,
                Permission.PROJECT_UPDATE, Permission.PROJECT_DELETE,
                Permission.TEMPLATE_CREATE, Permission.TEMPLATE_READ,
                Permission.TEMPLATE_UPDATE, Permission.TEMPLATE_DELETE,
                Permission.TEMPLATE_PUBLISH,
                Permission.USER_READ,
                Permission.ANALYTICS_READ
            },
            is_system=True
        ),
        'viewer': Role(
            name='viewer',
            description='Read-only access',
            permissions={
                Permission.PROJECT_READ,
                Permission.TEMPLATE_READ,
                Permission.USER_READ,
                Permission.ANALYTICS_READ
            },
            is_system=True
        ),
        'team_lead': Role(
            name='team_lead',
            description='Can manage team and projects',
            permissions={
                Permission.PROJECT_CREATE, Permission.PROJECT_READ,
                Permission.PROJECT_UPDATE,
                Permission.TEMPLATE_CREATE, Permission.TEMPLATE_READ,
                Permission.TEMPLATE_UPDATE,
                Permission.TEAM_MANAGE,
                Permission.USER_READ, Permission.USER_INVITE,
                Permission.ANALYTICS_READ
            },
            is_system=True
        )
    }

    def __init__(self, config_path: Optional[Path] = None):
        """
        Args:
            config_path: Path to RBAC configuration
        """
        self.config_path = config_path or Path.home() / '.ai_generator' / 'rbac'
        self.config_path.mkdir(parents=True, exist_ok=True)

        self.roles_file = self.config_path / 'roles.json'
        self.users_file = self.config_path / 'users.json'
        self.resource_perms_file = self.config_path / 'resource_permissions.json'

        # Load data
        self.roles = self._load_roles()
        self.users = self._load_users()
        self.resource_permissions = self._load_resource_permissions()

        # Ensure system roles exist
        self._ensure_system_roles()

    def _load_roles(self) -> Dict[str, Role]:
        """Load roles from file"""
        if self.roles_file.exists():
            with open(self.roles_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                roles = {}
                for name, role_data in data.items():
                    # Convert permission strings to Permission enum
                    perms = {Permission(p) for p in role_data['permissions']}
                    roles[name] = Role(
                        name=role_data['name'],
                        description=role_data['description'],
                        permissions=perms,
                        inherits_from=role_data.get('inherits_from'),
                        is_system=role_data.get('is_system', False),
                        created_at=role_data.get('created_at', datetime.now().isoformat())
                    )
                return roles
        return {}

    def _save_roles(self):
        """Save roles to file"""
        data = {}
        for name, role in self.roles.items():
            data[name] = {
                'name': role.name,
                'description': role.description,
                'permissions': [p.value for p in role.permissions],
                'inherits_from': role.inherits_from,
                'is_system': role.is_system,
                'created_at': role.created_at
            }

        with open(self.roles_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

    def _load_users(self) -> Dict[str, User]:
        """Load users from file"""
        if self.users_file.exists():
            with open(self.users_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return {
                    uid: User(**user_data)
                    for uid, user_data in data.items()
                }
        return {}

    def _save_users(self):
        """Save users to file"""
        data = {
            uid: {
                'id': user.id,
                'email': user.email,
                'name': user.name,
                'roles': user.roles,
                'organization_id': user.organization_id,
                'team_ids': user.team_ids,
                'is_active': user.is_active,
                'created_at': user.created_at,
                'last_login': user.last_login
            }
            for uid, user in self.users.items()
        }

        with open(self.users_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

    def _load_resource_permissions(self) -> List[ResourcePermission]:
        """Load resource permissions from file"""
        if self.resource_perms_file.exists():
            with open(self.resource_perms_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return [
                    ResourcePermission(
                        resource_type=item['resource_type'],
                        resource_id=item['resource_id'],
                        user_id=item['user_id'],
                        permissions={Permission(p) for p in item['permissions']},
                        granted_by=item['granted_by'],
                        granted_at=item['granted_at']
                    )
                    for item in data
                ]
        return []

    def _save_resource_permissions(self):
        """Save resource permissions to file"""
        data = [
            {
                'resource_type': rp.resource_type,
                'resource_id': rp.resource_id,
                'user_id': rp.user_id,
                'permissions': [p.value for p in rp.permissions],
                'granted_by': rp.granted_by,
                'granted_at': rp.granted_at
            }
            for rp in self.resource_permissions
        ]

        with open(self.resource_perms_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

    def _ensure_system_roles(self):
        """Ensure system roles exist"""
        for role_name, role in self.SYSTEM_ROLES.items():
            if role_name not in self.roles:
                self.roles[role_name] = role

        self._save_roles()

    def create_role(
        self,
        name: str,
        description: str,
        permissions: Set[Permission],
        inherits_from: Optional[str] = None
    ) -> Role:
        """
        Create a new role

        Args:
            name: Role name
            description: Role description
            permissions: Set of permissions
            inherits_from: Parent role to inherit from

        Returns:
            Created role
        """
        if name in self.roles:
            raise ValueError(f"Role {name} already exists")

        # If inherits, merge permissions
        if inherits_from:
            if inherits_from not in self.roles:
                raise ValueError(f"Parent role {inherits_from} not found")

            parent_perms = self._get_all_permissions(self.roles[inherits_from])
            permissions = permissions.union(parent_perms)

        role = Role(
            name=name,
            description=description,
            permissions=permissions,
            inherits_from=inherits_from,
            is_system=False
        )

        self.roles[name] = role
        self._save_roles()

        print(f"✅ Role created: {name}")
        return role

    def _get_all_permissions(self, role: Role) -> Set[Permission]:
        """Get all permissions including inherited"""
        perms = role.permissions.copy()

        if role.inherits_from and role.inherits_from in self.roles:
            parent = self.roles[role.inherits_from]
            perms = perms.union(self._get_all_permissions(parent))

        return perms

    def create_user(
        self,
        email: str,
        name: str,
        roles: List[str],
        organization_id: Optional[str] = None
    ) -> User:
        """
        Create a new user

        Args:
            email: User email
            name: User name
            roles: List of role names
            organization_id: Organization ID

        Returns:
            Created user
        """
        import hashlib
        user_id = hashlib.md5(email.encode()).hexdigest()[:12]

        if user_id in self.users:
            raise ValueError(f"User {email} already exists")

        # Validate roles
        for role_name in roles:
            if role_name not in self.roles:
                raise ValueError(f"Role {role_name} not found")

        user = User(
            id=user_id,
            email=email,
            name=name,
            roles=roles,
            organization_id=organization_id
        )

        self.users[user_id] = user
        self._save_users()

        print(f"✅ User created: {email} ({user_id})")
        return user

    def assign_role(self, user_id: str, role_name: str):
        """Assign role to user"""
        if user_id not in self.users:
            raise ValueError(f"User {user_id} not found")

        if role_name not in self.roles:
            raise ValueError(f"Role {role_name} not found")

        user = self.users[user_id]
        if role_name not in user.roles:
            user.roles.append(role_name)
            self._save_users()
            print(f"✅ Role {role_name} assigned to {user.email}")

    def revoke_role(self, user_id: str, role_name: str):
        """Revoke role from user"""
        if user_id not in self.users:
            raise ValueError(f"User {user_id} not found")

        user = self.users[user_id]
        if role_name in user.roles:
            user.roles.remove(role_name)
            self._save_users()
            print(f"✅ Role {role_name} revoked from {user.email}")

    def has_permission(self, user_id: str, permission: Permission) -> bool:
        """
        Check if user has permission

        Args:
            user_id: User ID
            permission: Permission to check

        Returns:
            True if user has permission
        """
        if user_id not in self.users:
            return False

        user = self.users[user_id]

        # Check role-based permissions
        for role_name in user.roles:
            if role_name in self.roles:
                role = self.roles[role_name]
                all_perms = self._get_all_permissions(role)
                if permission in all_perms:
                    return True

        return False

    def grant_resource_permission(
        self,
        resource_type: str,
        resource_id: str,
        user_id: str,
        permissions: Set[Permission],
        granted_by: str
    ):
        """
        Grant resource-specific permission

        Args:
            resource_type: Type of resource (project, template, etc.)
            resource_id: Resource ID
            user_id: User ID
            permissions: Permissions to grant
            granted_by: User ID who granted permission
        """
        rp = ResourcePermission(
            resource_type=resource_type,
            resource_id=resource_id,
            user_id=user_id,
            permissions=permissions,
            granted_by=granted_by
        )

        self.resource_permissions.append(rp)
        self._save_resource_permissions()

        print(f"✅ Resource permission granted to {user_id}")

    def has_resource_permission(
        self,
        user_id: str,
        resource_type: str,
        resource_id: str,
        permission: Permission
    ) -> bool:
        """Check if user has permission for specific resource"""
        # First check global permission
        if self.has_permission(user_id, permission):
            return True

        # Then check resource-specific permission
        for rp in self.resource_permissions:
            if (rp.user_id == user_id and
                rp.resource_type == resource_type and
                rp.resource_id == resource_id and
                permission in rp.permissions):
                return True

        return False

    def get_user_permissions(self, user_id: str) -> Set[Permission]:
        """Get all permissions for user"""
        if user_id not in self.users:
            return set()

        user = self.users[user_id]
        all_perms = set()

        for role_name in user.roles:
            if role_name in self.roles:
                role = self.roles[role_name]
                all_perms = all_perms.union(self._get_all_permissions(role))

        return all_perms

    def get_role_hierarchy(self) -> Dict[str, List[str]]:
        """Get role inheritance hierarchy"""
        hierarchy = {}

        for role_name, role in self.roles.items():
            if role.inherits_from:
                if role.inherits_from not in hierarchy:
                    hierarchy[role.inherits_from] = []
                hierarchy[role.inherits_from].append(role_name)

        return hierarchy


def require_permission(permission: Permission):
    """
    Decorator для проверки permissions

    Usage:
        @require_permission(Permission.PROJECT_CREATE)
        def create_project(user_id, ...):
            pass
    """
    def decorator(func):
        def wrapper(user_id: str, *args, **kwargs):
            # Assume rbac_manager is accessible
            # In real app, get from context
            from flask import g
            rbac = g.get('rbac_manager')

            if not rbac or not rbac.has_permission(user_id, permission):
                raise PermissionError(f"User {user_id} lacks permission: {permission.value}")

            return func(user_id, *args, **kwargs)

        return wrapper
    return decorator


if __name__ == '__main__':
    print("="*70)
    print("RBAC SYSTEM - Role-Based Access Control")
    print("="*70)

    # Demo
    rbac = RBACManager()

    # Create user
    user = rbac.create_user(
        email='john@example.com',
        name='John Doe',
        roles=['developer']
    )

    # Check permissions
    print(f"\nUser: {user.email}")
    print(f"Roles: {user.roles}")

    can_create = rbac.has_permission(user.id, Permission.PROJECT_CREATE)
    can_delete_user = rbac.has_permission(user.id, Permission.USER_DELETE)

    print(f"\nCan create project: {can_create}")
    print(f"Can delete user: {can_delete_user}")

    # Get all permissions
    perms = rbac.get_user_permissions(user.id)
    print(f"\nAll permissions ({len(perms)}):")
    for perm in sorted(perms, key=lambda p: p.value):
        print(f"  - {perm.value}")
