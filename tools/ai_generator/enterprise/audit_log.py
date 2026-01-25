#!/usr/bin/env python3
"""
Audit Logging System

Система аудита для отслеживания всех действий в системе:
- User actions logging
- API calls tracking
- Permission changes
- Resource modifications
- Security events
- Compliance reporting
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json
from pathlib import Path
import hashlib


class EventType(Enum):
    """Types of audit events"""
    # Authentication events
    AUTH_LOGIN = "auth.login"
    AUTH_LOGOUT = "auth.logout"
    AUTH_FAILED = "auth.failed"
    AUTH_PASSWORD_CHANGE = "auth.password_change"

    # User management events
    USER_CREATE = "user.create"
    USER_UPDATE = "user.update"
    USER_DELETE = "user.delete"
    USER_ACTIVATE = "user.activate"
    USER_DEACTIVATE = "user.deactivate"

    # Role management events
    ROLE_CREATE = "role.create"
    ROLE_UPDATE = "role.update"
    ROLE_DELETE = "role.delete"
    ROLE_ASSIGN = "role.assign"
    ROLE_REVOKE = "role.revoke"

    # Project events
    PROJECT_CREATE = "project.create"
    PROJECT_READ = "project.read"
    PROJECT_UPDATE = "project.update"
    PROJECT_DELETE = "project.delete"
    PROJECT_SHARE = "project.share"

    # Template events
    TEMPLATE_CREATE = "template.create"
    TEMPLATE_UPDATE = "template.update"
    TEMPLATE_DELETE = "template.delete"
    TEMPLATE_PUBLISH = "template.publish"
    TEMPLATE_DOWNLOAD = "template.download"

    # Organization events
    ORG_CREATE = "org.create"
    ORG_UPDATE = "org.update"
    ORG_SETTINGS_CHANGE = "org.settings.change"

    # API events
    API_KEY_CREATE = "api.key.create"
    API_KEY_REVOKE = "api.key.revoke"
    API_CALL = "api.call"
    API_RATE_LIMIT = "api.rate_limit"

    # Security events
    SECURITY_BREACH_ATTEMPT = "security.breach.attempt"
    SECURITY_PERMISSION_DENIED = "security.permission_denied"
    SECURITY_SUSPICIOUS_ACTIVITY = "security.suspicious"

    # System events
    SYSTEM_CONFIG_CHANGE = "system.config.change"
    SYSTEM_BACKUP = "system.backup"
    SYSTEM_RESTORE = "system.restore"


class Severity(Enum):
    """Event severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class AuditEvent:
    """Audit event record"""
    id: str
    timestamp: str
    event_type: EventType
    severity: Severity
    user_id: Optional[str]
    user_email: Optional[str]
    organization_id: Optional[str]
    resource_type: Optional[str]
    resource_id: Optional[str]
    action: str
    details: Dict[str, Any]
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    success: bool = True
    error_message: Optional[str] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'timestamp': self.timestamp,
            'event_type': self.event_type.value,
            'severity': self.severity.value,
            'user_id': self.user_id,
            'user_email': self.user_email,
            'organization_id': self.organization_id,
            'resource_type': self.resource_type,
            'resource_id': self.resource_id,
            'action': self.action,
            'details': self.details,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'success': self.success,
            'error_message': self.error_message
        }


class AuditLogger:
    """
    Audit Logger

    Centralized logging system for all audit events.
    """

    def __init__(self, storage_path: Optional[Path] = None):
        """
        Args:
            storage_path: Path to audit logs storage
        """
        self.storage_path = storage_path or Path.home() / '.ai_generator' / 'audit_logs'
        self.storage_path.mkdir(parents=True, exist_ok=True)

        self.current_log_file = self._get_current_log_file()
        self.events = []

    def _get_current_log_file(self) -> Path:
        """Get current log file (rotated daily)"""
        today = datetime.now().strftime('%Y-%m-%d')
        return self.storage_path / f'audit_{today}.jsonl'

    def _generate_event_id(self) -> str:
        """Generate unique event ID"""
        timestamp = datetime.now().isoformat()
        random_data = str(datetime.now().timestamp())
        return hashlib.sha256(f"{timestamp}{random_data}".encode()).hexdigest()[:16]

    def log(
        self,
        event_type: EventType,
        severity: Severity,
        action: str,
        user_id: Optional[str] = None,
        user_email: Optional[str] = None,
        organization_id: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        success: bool = True,
        error_message: Optional[str] = None
    ) -> AuditEvent:
        """
        Log an audit event

        Args:
            event_type: Type of event
            severity: Severity level
            action: Human-readable action description
            user_id: User ID who performed action
            user_email: User email
            organization_id: Organization ID
            resource_type: Type of resource affected
            resource_id: Resource ID
            details: Additional details
            ip_address: IP address
            user_agent: User agent string
            success: Whether action was successful
            error_message: Error message if failed

        Returns:
            Created AuditEvent
        """
        event = AuditEvent(
            id=self._generate_event_id(),
            timestamp=datetime.now().isoformat(),
            event_type=event_type,
            severity=severity,
            user_id=user_id,
            user_email=user_email,
            organization_id=organization_id,
            resource_type=resource_type,
            resource_id=resource_id,
            action=action,
            details=details or {},
            ip_address=ip_address,
            user_agent=user_agent,
            success=success,
            error_message=error_message
        )

        # Write to log file (JSONL format)
        with open(self.current_log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(event.to_dict()) + '\n')

        self.events.append(event)

        # Log to console if critical
        if severity == Severity.CRITICAL:
            print(f"🚨 CRITICAL: {action} by {user_email or user_id or 'system'}")

        return event

    def log_user_action(
        self,
        user_id: str,
        user_email: str,
        action: str,
        event_type: EventType,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        details: Optional[Dict] = None,
        success: bool = True
    ):
        """Log user action"""
        return self.log(
            event_type=event_type,
            severity=Severity.INFO if success else Severity.WARNING,
            action=action,
            user_id=user_id,
            user_email=user_email,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            success=success
        )

    def log_security_event(
        self,
        action: str,
        event_type: EventType = EventType.SECURITY_SUSPICIOUS_ACTIVITY,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        details: Optional[Dict] = None
    ):
        """Log security event"""
        return self.log(
            event_type=event_type,
            severity=Severity.CRITICAL,
            action=action,
            user_id=user_id,
            ip_address=ip_address,
            details=details,
            success=False
        )

    def query(
        self,
        user_id: Optional[str] = None,
        event_type: Optional[EventType] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        severity: Optional[Severity] = None,
        limit: int = 100
    ) -> List[AuditEvent]:
        """
        Query audit logs

        Args:
            user_id: Filter by user ID
            event_type: Filter by event type
            resource_type: Filter by resource type
            resource_id: Filter by resource ID
            start_date: Start date
            end_date: End date
            severity: Filter by severity
            limit: Max results

        Returns:
            List of matching events
        """
        results = []

        # Determine which log files to read
        if start_date and end_date:
            date_range = [start_date + timedelta(days=i)
                         for i in range((end_date - start_date).days + 1)]
            log_files = [
                self.storage_path / f'audit_{d.strftime("%Y-%m-%d")}.jsonl'
                for d in date_range
            ]
        else:
            # Read all log files
            log_files = list(self.storage_path.glob('audit_*.jsonl'))

        # Read and filter events
        for log_file in log_files:
            if not log_file.exists():
                continue

            with open(log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        data = json.loads(line)

                        # Apply filters
                        if user_id and data.get('user_id') != user_id:
                            continue

                        if event_type and data.get('event_type') != event_type.value:
                            continue

                        if resource_type and data.get('resource_type') != resource_type:
                            continue

                        if resource_id and data.get('resource_id') != resource_id:
                            continue

                        if severity and data.get('severity') != severity.value:
                            continue

                        # Parse timestamp and check date range
                        event_time = datetime.fromisoformat(data['timestamp'])
                        if start_date and event_time < start_date:
                            continue
                        if end_date and event_time > end_date:
                            continue

                        # Create AuditEvent object
                        event = AuditEvent(
                            id=data['id'],
                            timestamp=data['timestamp'],
                            event_type=EventType(data['event_type']),
                            severity=Severity(data['severity']),
                            user_id=data.get('user_id'),
                            user_email=data.get('user_email'),
                            organization_id=data.get('organization_id'),
                            resource_type=data.get('resource_type'),
                            resource_id=data.get('resource_id'),
                            action=data['action'],
                            details=data.get('details', {}),
                            ip_address=data.get('ip_address'),
                            user_agent=data.get('user_agent'),
                            success=data.get('success', True),
                            error_message=data.get('error_message')
                        )

                        results.append(event)

                        if len(results) >= limit:
                            break

                    except Exception:
                        # Skip malformed lines
                        continue

            if len(results) >= limit:
                break

        return results[:limit]

    def get_user_activity(
        self,
        user_id: str,
        days: int = 30
    ) -> List[AuditEvent]:
        """Get user activity for last N days"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        return self.query(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date
        )

    def get_security_events(
        self,
        days: int = 7
    ) -> List[AuditEvent]:
        """Get security events for last N days"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        events = []
        security_types = [
            EventType.SECURITY_BREACH_ATTEMPT,
            EventType.SECURITY_PERMISSION_DENIED,
            EventType.SECURITY_SUSPICIOUS_ACTIVITY,
            EventType.AUTH_FAILED
        ]

        for event_type in security_types:
            events.extend(self.query(
                event_type=event_type,
                start_date=start_date,
                end_date=end_date,
                limit=1000
            ))

        return sorted(events, key=lambda e: e.timestamp, reverse=True)

    def generate_compliance_report(
        self,
        organization_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> Dict:
        """
        Generate compliance report

        Args:
            organization_id: Organization ID
            start_date: Report start date
            end_date: Report end date

        Returns:
            Compliance report dictionary
        """
        all_events = self.query(
            start_date=start_date,
            end_date=end_date,
            limit=100000
        )

        # Filter by organization
        org_events = [e for e in all_events if e.organization_id == organization_id]

        # Categorize events
        user_actions = [e for e in org_events if e.event_type.value.startswith('user.')]
        project_actions = [e for e in org_events if e.event_type.value.startswith('project.')]
        security_events = [e for e in org_events if e.event_type.value.startswith('security.')]
        failed_actions = [e for e in org_events if not e.success]

        # Statistics
        unique_users = len(set(e.user_id for e in org_events if e.user_id))

        report = {
            'organization_id': organization_id,
            'period': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat()
            },
            'summary': {
                'total_events': len(org_events),
                'unique_users': unique_users,
                'user_management_events': len(user_actions),
                'project_events': len(project_actions),
                'security_events': len(security_events),
                'failed_actions': len(failed_actions)
            },
            'security': {
                'breach_attempts': len([e for e in security_events if e.event_type == EventType.SECURITY_BREACH_ATTEMPT]),
                'permission_denied': len([e for e in security_events if e.event_type == EventType.SECURITY_PERMISSION_DENIED]),
                'failed_logins': len([e for e in org_events if e.event_type == EventType.AUTH_FAILED])
            },
            'top_users': self._get_top_users(org_events, limit=10),
            'event_timeline': self._get_event_timeline(org_events)
        }

        return report

    def _get_top_users(self, events: List[AuditEvent], limit: int = 10) -> List[Dict]:
        """Get top active users"""
        user_counts = {}

        for event in events:
            if event.user_id:
                if event.user_id not in user_counts:
                    user_counts[event.user_id] = {
                        'user_id': event.user_id,
                        'user_email': event.user_email,
                        'event_count': 0
                    }
                user_counts[event.user_id]['event_count'] += 1

        sorted_users = sorted(
            user_counts.values(),
            key=lambda u: u['event_count'],
            reverse=True
        )

        return sorted_users[:limit]

    def _get_event_timeline(self, events: List[AuditEvent]) -> List[Dict]:
        """Get event timeline (daily counts)"""
        daily_counts = {}

        for event in events:
            date = event.timestamp[:10]  # YYYY-MM-DD
            if date not in daily_counts:
                daily_counts[date] = 0
            daily_counts[date] += 1

        timeline = [
            {'date': date, 'count': count}
            for date, count in sorted(daily_counts.items())
        ]

        return timeline

    def export_to_csv(
        self,
        events: List[AuditEvent],
        output_path: Path
    ):
        """Export events to CSV"""
        import csv

        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'id', 'timestamp', 'event_type', 'severity', 'user_email',
                'action', 'resource_type', 'resource_id', 'success'
            ])

            writer.writeheader()

            for event in events:
                writer.writerow({
                    'id': event.id,
                    'timestamp': event.timestamp,
                    'event_type': event.event_type.value,
                    'severity': event.severity.value,
                    'user_email': event.user_email or '',
                    'action': event.action,
                    'resource_type': event.resource_type or '',
                    'resource_id': event.resource_id or '',
                    'success': event.success
                })

        print(f"✅ Exported {len(events)} events to {output_path}")


if __name__ == '__main__':
    print("="*70)
    print("AUDIT LOGGING SYSTEM")
    print("="*70)

    # Demo
    logger = AuditLogger()

    # Log some events
    logger.log_user_action(
        user_id='user123',
        user_email='john@example.com',
        action='Created new project "AI Chatbot"',
        event_type=EventType.PROJECT_CREATE,
        resource_type='project',
        resource_id='proj456',
        details={'project_type': 'web_app', 'template': 'react-starter'}
    )

    logger.log_security_event(
        action='Failed login attempt',
        event_type=EventType.AUTH_FAILED,
        user_id='user123',
        ip_address='192.168.1.100',
        details={'reason': 'invalid_password', 'attempts': 3}
    )

    # Query recent events
    recent = logger.query(limit=10)
    print(f"\n📋 Recent events: {len(recent)}")

    for event in recent:
        print(f"\n  {event.timestamp[:19]}")
        print(f"  {event.event_type.value}: {event.action}")
        print(f"  User: {event.user_email or 'system'}")
        print(f"  Success: {event.success}")
