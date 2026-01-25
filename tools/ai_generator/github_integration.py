#!/usr/bin/env python3
"""
GitHub Integration Module

Автоматическое создание GitHub репозиториев с:
- Initial commit с сгенерированной структурой
- GitHub Projects setup
- Issue templates
- Branch protection rules
- CI/CD workflows
"""

import os
import json
import subprocess
from typing import Dict, List, Optional
from pathlib import Path
from dataclasses import dataclass
import requests
from datetime import datetime


@dataclass
class GitHubConfig:
    """Конфигурация GitHub"""
    token: str
    username: str
    organization: Optional[str] = None
    default_branch: str = "main"
    private: bool = False


@dataclass
class RepoInfo:
    """Информация о созданном репозитории"""
    name: str
    full_name: str
    html_url: str
    clone_url: str
    ssh_url: str
    default_branch: str
    created_at: str


class GitHubAPI:
    """
    GitHub API wrapper

    Provides methods for repository creation, content management,
    and project setup.
    """

    def __init__(self, config: GitHubConfig):
        """
        Args:
            config: GitHub configuration with token and username
        """
        self.config = config
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {config.token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "AI-Project-Generator"
        }

    def create_repository(
        self,
        name: str,
        description: str,
        private: bool = None,
        auto_init: bool = False,
        gitignore_template: Optional[str] = None,
        license_template: Optional[str] = None
    ) -> RepoInfo:
        """
        Создание нового GitHub репозитория

        Args:
            name: Название репозитория
            description: Описание
            private: Приватный или публичный
            auto_init: Создать README автоматически
            gitignore_template: Шаблон .gitignore (python, node, etc.)
            license_template: Шаблон лицензии (mit, apache-2.0, etc.)

        Returns:
            RepoInfo с информацией о созданном репозитории
        """
        if private is None:
            private = self.config.private

        # Определяем endpoint (user или organization)
        if self.config.organization:
            url = f"{self.base_url}/orgs/{self.config.organization}/repos"
        else:
            url = f"{self.base_url}/user/repos"

        payload = {
            "name": name,
            "description": description,
            "private": private,
            "auto_init": auto_init,
            "default_branch": self.config.default_branch
        }

        if gitignore_template:
            payload["gitignore_template"] = gitignore_template

        if license_template:
            payload["license_template"] = license_template

        response = requests.post(url, headers=self.headers, json=payload)

        if response.status_code == 201:
            data = response.json()
            return RepoInfo(
                name=data["name"],
                full_name=data["full_name"],
                html_url=data["html_url"],
                clone_url=data["clone_url"],
                ssh_url=data["ssh_url"],
                default_branch=data["default_branch"],
                created_at=data["created_at"]
            )
        else:
            raise Exception(f"Failed to create repository: {response.status_code} - {response.text}")

    def upload_file(
        self,
        repo_full_name: str,
        file_path: str,
        content: str,
        commit_message: str,
        branch: str = None
    ):
        """
        Загрузка файла в репозиторий

        Args:
            repo_full_name: Полное имя репозитория (username/repo)
            file_path: Путь к файлу в репозитории
            content: Содержимое файла
            commit_message: Сообщение коммита
            branch: Ветка (по умолчанию main)
        """
        if branch is None:
            branch = self.config.default_branch

        url = f"{self.base_url}/repos/{repo_full_name}/contents/{file_path}"

        # Кодируем content в base64
        import base64
        encoded_content = base64.b64encode(content.encode('utf-8')).decode('utf-8')

        payload = {
            "message": commit_message,
            "content": encoded_content,
            "branch": branch
        }

        response = requests.put(url, headers=self.headers, json=payload)

        if response.status_code not in [200, 201]:
            raise Exception(f"Failed to upload file: {response.status_code} - {response.text}")

        return response.json()

    def create_issue_template(
        self,
        repo_full_name: str,
        template_name: str,
        template_content: str
    ):
        """
        Создание issue template

        Args:
            repo_full_name: Полное имя репозитория
            template_name: Имя шаблона (bug_report.md, feature_request.md)
            template_content: Содержимое шаблона
        """
        file_path = f".github/ISSUE_TEMPLATE/{template_name}"
        return self.upload_file(
            repo_full_name,
            file_path,
            template_content,
            f"Add issue template: {template_name}"
        )

    def create_pr_template(
        self,
        repo_full_name: str,
        template_content: str
    ):
        """
        Создание Pull Request template

        Args:
            repo_full_name: Полное имя репозитория
            template_content: Содержимое шаблона
        """
        file_path = ".github/PULL_REQUEST_TEMPLATE.md"
        return self.upload_file(
            repo_full_name,
            file_path,
            template_content,
            "Add PR template"
        )

    def create_workflow(
        self,
        repo_full_name: str,
        workflow_name: str,
        workflow_content: str
    ):
        """
        Создание GitHub Actions workflow

        Args:
            repo_full_name: Полное имя репозитория
            workflow_name: Имя workflow файла
            workflow_content: YAML содержимое workflow
        """
        file_path = f".github/workflows/{workflow_name}"
        return self.upload_file(
            repo_full_name,
            file_path,
            workflow_content,
            f"Add GitHub Actions workflow: {workflow_name}"
        )

    def enable_branch_protection(
        self,
        repo_full_name: str,
        branch: str = None,
        require_reviews: bool = True,
        required_approvals: int = 1,
        dismiss_stale_reviews: bool = True,
        require_code_owner_reviews: bool = False,
        require_status_checks: bool = True,
        strict_status_checks: bool = True,
        status_checks: List[str] = None
    ):
        """
        Включение branch protection rules

        Args:
            repo_full_name: Полное имя репозитория
            branch: Ветка для защиты
            require_reviews: Требовать review перед merge
            required_approvals: Количество требуемых approvals
            dismiss_stale_reviews: Отклонять устаревшие reviews
            require_code_owner_reviews: Требовать review от code owners
            require_status_checks: Требовать прохождение CI
            strict_status_checks: Требовать актуальную ветку
            status_checks: Список обязательных checks
        """
        if branch is None:
            branch = self.config.default_branch

        if status_checks is None:
            status_checks = []

        url = f"{self.base_url}/repos/{repo_full_name}/branches/{branch}/protection"

        payload = {
            "required_status_checks": {
                "strict": strict_status_checks,
                "contexts": status_checks
            } if require_status_checks else None,
            "enforce_admins": False,
            "required_pull_request_reviews": {
                "dismissal_restrictions": {},
                "dismiss_stale_reviews": dismiss_stale_reviews,
                "require_code_owner_reviews": require_code_owner_reviews,
                "required_approving_review_count": required_approvals
            } if require_reviews else None,
            "restrictions": None
        }

        response = requests.put(url, headers=self.headers, json=payload)

        if response.status_code != 200:
            raise Exception(f"Failed to enable branch protection: {response.status_code} - {response.text}")

        return response.json()

    def create_project(
        self,
        repo_full_name: str,
        name: str,
        body: str = ""
    ):
        """
        Создание GitHub Project (Classic)

        Args:
            repo_full_name: Полное имя репозитория
            name: Название проекта
            body: Описание проекта
        """
        url = f"{self.base_url}/repos/{repo_full_name}/projects"

        payload = {
            "name": name,
            "body": body
        }

        # Требуется специальный Accept header для Projects API
        headers = self.headers.copy()
        headers["Accept"] = "application/vnd.github.inertia-preview+json"

        response = requests.post(url, headers=headers, json=payload)

        if response.status_code != 201:
            raise Exception(f"Failed to create project: {response.status_code} - {response.text}")

        return response.json()

    def create_project_columns(
        self,
        project_id: int,
        columns: List[str]
    ):
        """
        Создание колонок в GitHub Project

        Args:
            project_id: ID проекта
            columns: Список названий колонок
        """
        url = f"{self.base_url}/projects/{project_id}/columns"

        headers = self.headers.copy()
        headers["Accept"] = "application/vnd.github.inertia-preview+json"

        created_columns = []
        for column_name in columns:
            payload = {"name": column_name}
            response = requests.post(url, headers=headers, json=payload)

            if response.status_code == 201:
                created_columns.append(response.json())
            else:
                print(f"⚠️  Failed to create column '{column_name}': {response.status_code}")

        return created_columns

    def create_labels(
        self,
        repo_full_name: str,
        labels: List[Dict[str, str]]
    ):
        """
        Создание labels в репозитории

        Args:
            repo_full_name: Полное имя репозитория
            labels: Список labels с name, color, description
        """
        url = f"{self.base_url}/repos/{repo_full_name}/labels"

        created_labels = []
        for label in labels:
            response = requests.post(url, headers=self.headers, json=label)

            if response.status_code == 201:
                created_labels.append(response.json())
            elif response.status_code == 422:
                # Label уже существует
                print(f"ℹ️  Label '{label['name']}' already exists")
            else:
                print(f"⚠️  Failed to create label '{label['name']}': {response.status_code}")

        return created_labels


class LocalGitManager:
    """
    Управление локальным git репозиторием

    Handles local git operations before pushing to GitHub.
    """

    def __init__(self, project_path: Path):
        """
        Args:
            project_path: Путь к проекту
        """
        self.project_path = Path(project_path)

    def init_repo(self, default_branch: str = "main"):
        """Инициализация git репозитория"""
        if not (self.project_path / ".git").exists():
            subprocess.run(
                ["git", "init", "-b", default_branch],
                cwd=self.project_path,
                check=True,
                capture_output=True
            )
            print(f"✅ Initialized git repository in {self.project_path}")
        else:
            print(f"ℹ️  Git repository already exists in {self.project_path}")

    def add_all(self):
        """Добавить все файлы в staging"""
        subprocess.run(
            ["git", "add", "."],
            cwd=self.project_path,
            check=True,
            capture_output=True
        )
        print("✅ Added all files to staging")

    def commit(self, message: str):
        """Создать commit"""
        subprocess.run(
            ["git", "commit", "-m", message],
            cwd=self.project_path,
            check=True,
            capture_output=True
        )
        print(f"✅ Created commit: {message}")

    def add_remote(self, name: str, url: str):
        """Добавить remote"""
        # Проверяем существует ли remote
        result = subprocess.run(
            ["git", "remote", "get-url", name],
            cwd=self.project_path,
            capture_output=True
        )

        if result.returncode != 0:
            # Remote не существует, добавляем
            subprocess.run(
                ["git", "remote", "add", name, url],
                cwd=self.project_path,
                check=True,
                capture_output=True
            )
            print(f"✅ Added remote '{name}': {url}")
        else:
            print(f"ℹ️  Remote '{name}' already exists")

    def push(self, remote: str = "origin", branch: str = "main", set_upstream: bool = True):
        """Push в remote"""
        cmd = ["git", "push"]
        if set_upstream:
            cmd.extend(["-u", remote, branch])
        else:
            cmd.extend([remote, branch])

        subprocess.run(
            cmd,
            cwd=self.project_path,
            check=True,
            capture_output=True
        )
        print(f"✅ Pushed to {remote}/{branch}")

    def create_gitignore(self, template: str = "python"):
        """
        Создание .gitignore файла

        Args:
            template: Тип проекта (python, node, java, etc.)
        """
        gitignore_templates = {
            "python": """
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
env/
ENV/
.venv

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Environment variables
.env
.env.local

# Logs
*.log
""",
            "node": """
# Node
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*
.npm
.yarn/
package-lock.json
yarn.lock

# Build
dist/
build/
.next/
out/

# IDEs
.vscode/
.idea/

# OS
.DS_Store

# Environment
.env
.env.local
.env.production

# Logs
*.log
""",
            "java": """
# Java
*.class
*.jar
*.war
*.ear
target/
.gradle/
build/

# IDEs
.idea/
*.iml
.eclipse/
.vscode/

# OS
.DS_Store

# Logs
*.log
"""
        }

        content = gitignore_templates.get(template, gitignore_templates["python"])
        gitignore_path = self.project_path / ".gitignore"

        with open(gitignore_path, 'w', encoding='utf-8') as f:
            f.write(content.strip())

        print(f"✅ Created .gitignore ({template} template)")


def get_github_token() -> Optional[str]:
    """
    Получение GitHub token из environment variables

    Проверяет следующие переменные (в порядке приоритета):
    1. GITHUB_TOKEN
    2. GH_TOKEN
    3. ~/.config/gh/hosts.yml (GitHub CLI)
    """
    # Проверяем environment variables
    token = os.environ.get('GITHUB_TOKEN') or os.environ.get('GH_TOKEN')
    if token:
        return token

    # Проверяем GitHub CLI config
    gh_config_path = Path.home() / '.config' / 'gh' / 'hosts.yml'
    if gh_config_path.exists():
        try:
            import yaml
            with open(gh_config_path, 'r') as f:
                config = yaml.safe_load(f)
                if 'github.com' in config:
                    return config['github.com'].get('oauth_token')
        except Exception:
            pass

    return None


if __name__ == '__main__':
    print("="*70)
    print("GITHUB INTEGRATION MODULE")
    print("="*70)
    print("\nThis module provides GitHub API integration.")
    print("\nUsage:")
    print("  from github_integration import GitHubAPI, GitHubConfig")
    print("  config = GitHubConfig(token='...', username='...')")
    print("  api = GitHubAPI(config)")
    print("  repo = api.create_repository('my-project', 'Description')")
    print("\nSee github_project_creator.py for complete workflow.")
