#!/usr/bin/env python3
"""
Usage Analytics

Аналитика использования платформы.
"""

import json
from typing import Dict, List, Any
from datetime import datetime, timedelta
from collections import defaultdict
from dataclasses import dataclass, asdict


@dataclass
class UsageEvent:
    """Событие использования"""
    event_id: str
    user_id: str
    event_type: str
    timestamp: str
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict:
        return asdict(self)


class UsageAnalytics:
    """Usage Analytics Manager"""

    def __init__(self, storage_path: str = './analytics_data'):
        """Инициализация"""
        from pathlib import Path
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.events: List[UsageEvent] = []
        self._load_events()

    def _load_events(self):
        """Загрузка событий"""
        events_file = self.storage_path / 'events.jsonl'
        if events_file.exists():
            with open(events_file) as f:
                for line in f:
                    data = json.loads(line)
                    self.events.append(UsageEvent(**data))

    def track_event(self, user_id: str, event_type: str, metadata: Dict = None):
        """Отслеживание события"""
        import uuid
        event = UsageEvent(
            event_id=str(uuid.uuid4()),
            user_id=user_id,
            event_type=event_type,
            timestamp=datetime.now().isoformat(),
            metadata=metadata or {}
        )
        self.events.append(event)

        # Append to JSONL
        with open(self.storage_path / 'events.jsonl', 'a') as f:
            f.write(json.dumps(event.to_dict()) + '\n')

    def get_dau(self, date: str = None) -> int:
        """Daily Active Users"""
        target_date = date or datetime.now().date().isoformat()
        users = set()
        for event in self.events:
            event_date = datetime.fromisoformat(event.timestamp).date().isoformat()
            if event_date == target_date:
                users.add(event.user_id)
        return len(users)

    def get_mau(self) -> int:
        """Monthly Active Users"""
        month_ago = datetime.now() - timedelta(days=30)
        users = set()
        for event in self.events:
            if datetime.fromisoformat(event.timestamp) >= month_ago:
                users.add(event.user_id)
        return len(users)

    def get_event_counts(self) -> Dict[str, int]:
        """Подсчет событий по типам"""
        counts = defaultdict(int)
        for event in self.events:
            counts[event.event_type] += 1
        return dict(counts)

    def get_user_journey(self, user_id: str) -> List[Dict]:
        """Journey пользователя"""
        user_events = [e for e in self.events if e.user_id == user_id]
        user_events.sort(key=lambda x: x.timestamp)
        return [e.to_dict() for e in user_events]

    def get_retention_rate(self, cohort_days: int = 7) -> float:
        """Retention rate"""
        cohort_start = datetime.now() - timedelta(days=cohort_days)
        cohort_users = set()
        retained_users = set()

        for event in self.events:
            event_time = datetime.fromisoformat(event.timestamp)
            if event_time >= cohort_start - timedelta(days=1) and event_time < cohort_start:
                cohort_users.add(event.user_id)
            elif event_time >= cohort_start:
                if event.user_id in cohort_users:
                    retained_users.add(event.user_id)

        return (len(retained_users) / len(cohort_users) * 100) if cohort_users else 0.0

    def generate_report(self) -> Dict[str, Any]:
        """Генерация отчета"""
        return {
            'total_events': len(self.events),
            'dau': self.get_dau(),
            'mau': self.get_mau(),
            'event_counts': self.get_event_counts(),
            'retention_7d': round(self.get_retention_rate(7), 2),
            'retention_30d': round(self.get_retention_rate(30), 2)
        }
