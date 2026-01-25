"""
Integration Ecosystem Package

Интеграции с популярными платформами и сервисами.
"""

from .jira_integration import JiraIntegration
from .slack_integration import SlackIntegration
from .gitlab_integration import GitLabIntegration
from .notion_integration import NotionIntegration

__all__ = [
    'JiraIntegration',
    'SlackIntegration',
    'GitLabIntegration',
    'NotionIntegration'
]

__version__ = '1.0.0'
