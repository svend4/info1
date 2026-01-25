#!/usr/bin/env python3
"""
Enterprise Integration Example

Демонстрация полного enterprise workflow с использованием всех модулей.
"""

from pathlib import Path
from datetime import datetime, timedelta

from rbac import RBACManager, Permission
from audit_log import AuditLogger, EventType, Severity
from organization import OrganizationManager, OrganizationPlan, TeamRole
from template_policies import TemplatePolicyManager, TemplateStatus


def main():
    print("="*70)
    print("ENTERPRISE INTEGRATION DEMO")
    print("="*70)

    # Initialize all managers
    rbac = RBACManager()
    audit = AuditLogger()
    org_manager = OrganizationManager()
    policies = TemplatePolicyManager()

    # ===== STEP 1: Setup Organization =====
    print("\n📊 Step 1: Setting up organization")

    org = org_manager.create_organization(
        name='Demo Corp',
        slug='demo-corp',
        owner_id='founder_123',
        plan=OrganizationPlan.PROFESSIONAL,
        billing_email='billing@democorp.com'
    )

    audit.log(
        event_type=EventType.ORG_CREATE,
        severity=Severity.INFO,
        action=f'Organization {org.name} created',
        user_id='founder_123',
        organization_id=org.id
    )

    # ===== STEP 2: Create Users =====
    print("\n👥 Step 2: Creating users")

    admin_user = rbac.create_user(
        email='admin@democorp.com',
        name='Admin User',
        roles=['admin'],
        organization_id=org.id
    )

    dev_user = rbac.create_user(
        email='developer@democorp.com',
        name='Developer User',
        roles=['developer'],
        organization_id=org.id
    )

    viewer_user = rbac.create_user(
        email='viewer@democorp.com',
        name='Viewer User',
        roles=['viewer'],
        organization_id=org.id
    )

    audit.log_user_action(
        user_id=admin_user.id,
        user_email=admin_user.email,
        action='Created user accounts',
        event_type=EventType.USER_CREATE
    )

    # ===== STEP 3: Create Team =====
    print("\n👨‍💻 Step 3: Creating team")

    team = org_manager.create_team(
        organization_id=org.id,
        name='Platform Engineering',
        description='Core platform development team',
        created_by=admin_user.id
    )

    org_manager.add_team_member(team.id, admin_user.id, TeamRole.OWNER)
    org_manager.add_team_member(team.id, dev_user.id, TeamRole.MEMBER)

    # ===== STEP 4: Permission Checks =====
    print("\n🔐 Step 4: Permission checks")

    permissions_to_check = [
        (dev_user.id, Permission.PROJECT_CREATE, 'Developer'),
        (viewer_user.id, Permission.PROJECT_CREATE, 'Viewer'),
        (admin_user.id, Permission.ORG_MANAGE, 'Admin')
    ]

    for user_id, permission, role_name in permissions_to_check:
        has_perm = rbac.has_permission(user_id, permission)
        status = "✅" if has_perm else "❌"
        print(f"  {status} {role_name} can {permission.value}: {has_perm}")

    # ===== STEP 5: Template Creation & Review =====
    print("\n📦 Step 5: Template creation and review")

    # Simulate template creation
    template_id = 'demo_template_456'

    audit.log_user_action(
        user_id=dev_user.id,
        user_email=dev_user.email,
        action='Created new template "React Starter"',
        event_type=EventType.TEMPLATE_CREATE,
        resource_type='template',
        resource_id=template_id,
        details={'framework': 'react', 'language': 'typescript'}
    )

    # Create temporary template directory for demo
    demo_template_path = Path('./demo_template_review')
    demo_template_path.mkdir(exist_ok=True)

    (demo_template_path / 'README.md').write_text('# React Starter Template\n\nA professional React starter.')
    (demo_template_path / 'LICENSE').write_text('MIT License')
    (demo_template_path / 'ARCHITECTURE.md').write_text('# Architecture\n\nComponent-based architecture.')

    # Policy review
    review = policies.review_template(
        template_id=template_id,
        template_path=demo_template_path,
        reviewer_id=admin_user.id,
        reviewer_email=admin_user.email,
        organization_id=org.id
    )

    print(f"\n  Review Status: {review.status.value}")
    print(f"  Violations: {len(review.violations)}")

    if review.violations:
        for violation in review.violations:
            print(f"    {violation.severity.value.upper()}: {violation.message}")
    else:
        print("  ✅ No violations found")

    # Log review result
    audit.log_user_action(
        user_id=admin_user.id,
        user_email=admin_user.email,
        action=f'Reviewed template: {review.status.value}',
        event_type=EventType.TEMPLATE_UPDATE,
        resource_id=template_id,
        details={'status': review.status.value, 'violations': len(review.violations)}
    )

    # ===== STEP 6: Organization Usage Stats =====
    print("\n📈 Step 6: Organization usage statistics")

    # Update quota (simulate usage)
    org.quota.current_users = 3
    org.quota.current_teams = 1
    org.quota.current_projects = 15

    stats = org_manager.get_usage_stats(org.id)

    print(f"\n  Organization: {org.name}")
    print(f"  Plan: {org.plan.value}")
    print(f"\n  Resource Usage:")
    print(f"    Users: {stats['users']['current']}/{stats['users']['limit']} ({stats['users']['percentage']}%)")
    print(f"    Teams: {stats['teams']['current']}/{stats['teams']['limit']} ({stats['teams']['percentage']}%)")
    print(f"    Projects: {stats['projects']['current']}/{stats['projects']['limit']} ({stats['projects']['percentage']}%)")

    # ===== STEP 7: Audit Trail =====
    print("\n📋 Step 7: Audit trail")

    recent_events = audit.query(
        organization_id=org.id,
        limit=10
    )

    print(f"\n  Recent events ({len(recent_events)}):")
    for event in recent_events[:5]:
        timestamp = event.timestamp[:19].replace('T', ' ')
        print(f"    {timestamp} - {event.event_type.value}")
        print(f"      User: {event.user_email or 'system'}")
        print(f"      Action: {event.action}")

    # ===== STEP 8: Security Events =====
    print("\n🔒 Step 8: Security monitoring")

    # Simulate failed login
    audit.log_security_event(
        action='Failed login attempt',
        event_type=EventType.AUTH_FAILED,
        user_id=viewer_user.id,
        ip_address='192.168.1.100',
        details={'reason': 'invalid_password', 'attempts': 2}
    )

    security_events = audit.get_security_events(days=1)

    print(f"\n  Security events (last 24h): {len(security_events)}")
    for event in security_events:
        print(f"    🚨 {event.event_type.value}: {event.action}")

    # ===== STEP 9: Compliance Report =====
    print("\n📊 Step 9: Compliance report")

    report = audit.generate_compliance_report(
        organization_id=org.id,
        start_date=datetime.now() - timedelta(days=1),
        end_date=datetime.now()
    )

    print(f"\n  Compliance Report:")
    print(f"    Period: Last 24 hours")
    print(f"    Total events: {report['summary']['total_events']}")
    print(f"    Unique users: {report['summary']['unique_users']}")
    print(f"    Security events: {report['summary']['security_events']}")
    print(f"    Failed actions: {report['summary']['failed_actions']}")

    # ===== STEP 10: Plan Upgrade =====
    print("\n⬆️  Step 10: Plan upgrade simulation")

    print(f"\n  Current plan: {org.plan.value}")
    print(f"  Current limits: {org.quota.max_users} users, {org.quota.max_projects} projects")

    # Simulate upgrade
    org_manager.upgrade_plan(org.id, OrganizationPlan.ENTERPRISE)

    updated_org = org_manager.organizations[org.id]
    print(f"\n  New plan: {updated_org.plan.value}")
    print(f"  New limits: {updated_org.quota.max_users} users, {updated_org.quota.max_projects} projects")

    audit.log(
        event_type=EventType.ORG_UPDATE,
        severity=Severity.INFO,
        action=f'Plan upgraded to {OrganizationPlan.ENTERPRISE.value}',
        user_id=admin_user.id,
        organization_id=org.id
    )

    # ===== Summary =====
    print("\n" + "="*70)
    print("✅ ENTERPRISE INTEGRATION DEMO COMPLETED")
    print("="*70)

    print(f"\nCreated:")
    print(f"  ✅ 1 Organization ({org.name})")
    print(f"  ✅ 3 Users (admin, developer, viewer)")
    print(f"  ✅ 1 Team ({team.name})")
    print(f"  ✅ 1 Template (reviewed and approved)")
    print(f"  ✅ {len(recent_events)} Audit events")

    print(f"\nEnterprise features demonstrated:")
    print(f"  ✅ RBAC - Role-based permissions")
    print(f"  ✅ Audit Logging - Full audit trail")
    print(f"  ✅ Organizations - Multi-tenant setup")
    print(f"  ✅ Template Policies - Governance")
    print(f"  ✅ Compliance Reporting")

    # Cleanup demo template
    import shutil
    if demo_template_path.exists():
        shutil.rmtree(demo_template_path)


if __name__ == '__main__':
    main()
