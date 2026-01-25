#!/usr/bin/env python3
"""
GitHub Project Creator

Полный workflow для создания GitHub проекта:
1. Генерация структуры через AI Generator
2. Создание GitHub репозитория
3. Initial commit с сгенерированной структурой
4. Setup issue templates, workflows, labels
5. Настройка GitHub Project board
"""

import sys
import os
from pathlib import Path
import argparse
import subprocess
from typing import Optional

# Добавляем путь к модулям
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tools.ai_generator.github_integration import (
    GitHubAPI,
    GitHubConfig,
    LocalGitManager,
    get_github_token
)
from tools.ai_generator.multi_label_classifier import MultiLabelClassifier
from tools.ai_generator.enhanced_parameter_extractor import EnhancedParameterExtractor
from tools.ai_generator.template_composer import TemplateComposer
from tools.ai_generator.context_aware_adapter import ContextAwareAdapter
from tools.ai_generator.llm_content_generator import LLMContentGenerator


class GitHubProjectCreator:
    """
    Создание полного GitHub проекта с AI-generated структурой
    """

    def __init__(self, github_config: GitHubConfig):
        """
        Args:
            github_config: Конфигурация GitHub
        """
        self.github_api = GitHubAPI(github_config)
        self.github_config = github_config

        # AI компоненты
        self.classifier = MultiLabelClassifier()
        self.extractor = EnhancedParameterExtractor()
        self.composer = TemplateComposer()
        self.adapter = ContextAwareAdapter()
        self.generator = LLMContentGenerator()

    def create_complete_project(
        self,
        description: str,
        project_name: Optional[str] = None,
        private: bool = False,
        output_dir: Optional[Path] = None,
        push_to_github: bool = True,
        setup_project_board: bool = True
    ):
        """
        Создание полного проекта от анализа до GitHub

        Args:
            description: Описание проекта
            project_name: Название (auto-generate если None)
            private: Приватный репозиторий
            output_dir: Директория для локального проекта
            push_to_github: Push в GitHub
            setup_project_board: Создать GitHub Project board

        Returns:
            Информация о созданном проекте
        """
        print("="*70)
        print("🚀 GITHUB PROJECT CREATOR")
        print("="*70)

        # 1. Анализ через AI
        print("\n📊 Step 1: AI Analysis")
        print(f"Description: {description[:80]}...")

        ml_result = self.classifier.classify(description)
        params = self.extractor.extract(description)
        base_structure = self.composer.compose(ml_result)
        adapted = self.adapter.adapt(base_structure, params)

        print(f"✅ Classification: {ml_result.primary_type}")
        print(f"   Confidence: {ml_result.primary_confidence:.2%}")
        if ml_result.is_hybrid:
            print(f"   Hybrid: {', '.join(ml_result.secondary_types[:2])}")

        # 2. Генерация имени проекта
        if not project_name:
            from tools.ai_generator.classifier import ProjectClassifier
            temp_classifier = ProjectClassifier()
            temp_spec = temp_classifier.classify(description)
            project_name = temp_spec.name

        print(f"\n📦 Project name: {project_name}")

        # 3. Создание локальной структуры
        print("\n🏗️  Step 2: Generating Local Structure")

        if output_dir is None:
            import tempfile
            output_dir = Path(tempfile.mkdtemp())

        project_path = output_dir / project_name

        # Используем project_template_generator.py
        generator_path = Path(__file__).parent.parent / 'project_template_generator.py'

        cmd = [
            sys.executable,
            str(generator_path),
            '--name', project_name,
            '--type', ml_result.primary_type,
            '--output', str(output_dir)
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"✅ Generated structure: {len(adapted.directories)} directories, {len(adapted.files)} files")

        # 4. Генерация content через LLM
        print("\n📝 Step 3: Generating Content (LLM)")

        content = self.generator.generate_all(
            ml_result, params, adapted, project_name, description
        )

        # Сохранение документации
        docs_to_save = [
            ("README.md", content.readme),
            ("ARCHITECTURE.md", content.architecture),
            ("CONTRIBUTING.md", content.contributing),
            ("CHECKLIST.md", content.checklist)
        ]

        for filename, doc_content in docs_to_save:
            if doc_content:
                doc_path = project_path / filename
                with open(doc_path, 'w', encoding='utf-8') as f:
                    f.write(doc_content)
                print(f"✅ {filename}")

        # Сохранение code examples
        if content.code_examples:
            examples_dir = project_path / "examples"
            examples_dir.mkdir(exist_ok=True)
            for filename, code in content.code_examples.items():
                example_path = examples_dir / filename
                with open(example_path, 'w', encoding='utf-8') as f:
                    f.write(code)
            print(f"✅ examples/ ({len(content.code_examples)} files)")

        # 5. Создание GitHub репозитория
        print(f"\n🐙 Step 4: Creating GitHub Repository")

        repo_info = self.github_api.create_repository(
            name=project_name,
            description=description[:100],  # GitHub limit
            private=private,
            auto_init=False  # Мы сами создадим initial commit
        )

        print(f"✅ Created: {repo_info.html_url}")

        # 6. Setup issue templates
        print("\n📋 Step 5: Setting Up Issue Templates")
        self._create_issue_templates(repo_info.full_name, ml_result.primary_type)

        # 7. Setup workflows
        print("\n⚙️  Step 6: Setting Up GitHub Actions")
        self._create_workflows(repo_info.full_name, ml_result.primary_type, params)

        # 8. Setup labels
        print("\n🏷️  Step 7: Creating Labels")
        self._create_labels(repo_info.full_name)

        # 9. Local git setup
        print("\n🔧 Step 8: Local Git Setup")
        git_manager = LocalGitManager(project_path)
        git_manager.init_repo(default_branch=self.github_config.default_branch)
        git_manager.create_gitignore(self._get_gitignore_type(ml_result.primary_type))
        git_manager.add_all()
        git_manager.commit(f"Initial commit: AI-generated {ml_result.primary_type} project")

        # 10. Push to GitHub
        if push_to_github:
            print("\n📤 Step 9: Pushing to GitHub")
            git_manager.add_remote("origin", repo_info.clone_url)
            git_manager.push(
                remote="origin",
                branch=self.github_config.default_branch,
                set_upstream=True
            )
            print(f"✅ Pushed to {repo_info.html_url}")

        # 11. Setup GitHub Project board
        if setup_project_board:
            print("\n📊 Step 10: Creating Project Board")
            self._create_project_board(repo_info.full_name, project_name, ml_result.primary_type)

        # Summary
        print("\n" + "="*70)
        print("✅ PROJECT CREATED SUCCESSFULLY!")
        print("="*70)
        print(f"\n🌐 GitHub URL: {repo_info.html_url}")
        print(f"📁 Local path: {project_path}")
        print(f"\n📊 Statistics:")
        print(f"   Type: {ml_result.primary_type}")
        print(f"   Directories: {len(adapted.directories)}")
        print(f"   Files: {len(adapted.files)}")
        print(f"   Adaptations: {len(adapted.adaptations)}")

        return {
            'repo_info': repo_info,
            'project_path': project_path,
            'classification': ml_result,
            'structure': adapted
        }

    def _create_issue_templates(self, repo_full_name: str, project_type: str):
        """Создание issue templates"""

        # Bug report template
        bug_template = """---
name: Bug Report
about: Report a bug or unexpected behavior
title: '[BUG] '
labels: bug
assignees: ''
---

## Bug Description
A clear and concise description of the bug.

## Steps to Reproduce
1. Go to '...'
2. Click on '...'
3. See error

## Expected Behavior
What you expected to happen.

## Actual Behavior
What actually happened.

## Environment
- OS: [e.g., Ubuntu 22.04]
- Version: [e.g., 1.0.0]
- Browser (if applicable): [e.g., Chrome 120]

## Additional Context
Add any other context about the problem here.

## Screenshots
If applicable, add screenshots to help explain your problem.
"""

        # Feature request template
        feature_template = """---
name: Feature Request
about: Suggest an idea for this project
title: '[FEATURE] '
labels: enhancement
assignees: ''
---

## Feature Description
A clear and concise description of the feature you'd like.

## Problem it Solves
Explain what problem this feature would solve.

## Proposed Solution
Describe how you envision this feature working.

## Alternatives Considered
Describe any alternative solutions you've considered.

## Additional Context
Add any other context or screenshots about the feature request.

## Priority
- [ ] High
- [ ] Medium
- [ ] Low
"""

        # Question template
        question_template = """---
name: Question
about: Ask a question about the project
title: '[QUESTION] '
labels: question
assignees: ''
---

## Question
Your question here.

## Context
Any additional context that might help answer your question.

## What I've Tried
What you've already attempted or researched.
"""

        templates = [
            ("bug_report.md", bug_template),
            ("feature_request.md", feature_template),
            ("question.md", question_template)
        ]

        for template_name, template_content in templates:
            try:
                self.github_api.create_issue_template(
                    repo_full_name,
                    template_name,
                    template_content
                )
                print(f"✅ Issue template: {template_name}")
            except Exception as e:
                print(f"⚠️  Failed to create {template_name}: {str(e)}")

        # PR template
        pr_template = """## Description
Brief description of the changes in this PR.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update
- [ ] Refactoring
- [ ] Performance improvement

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review performed
- [ ] Comments added for complex code
- [ ] Documentation updated
- [ ] Tests added/updated
- [ ] All tests passing
- [ ] No new warnings

## Testing
Describe how you tested these changes.

## Related Issues
Closes #(issue number)

## Screenshots (if applicable)
Add screenshots to demonstrate the changes.
"""

        try:
            self.github_api.create_pr_template(repo_full_name, pr_template)
            print(f"✅ PR template")
        except Exception as e:
            print(f"⚠️  Failed to create PR template: {str(e)}")

    def _create_workflows(self, repo_full_name: str, project_type: str, params):
        """Создание GitHub Actions workflows"""

        # CI workflow
        ci_workflow = self._generate_ci_workflow(project_type)

        try:
            self.github_api.create_workflow(
                repo_full_name,
                "ci.yml",
                ci_workflow
            )
            print(f"✅ Workflow: ci.yml")
        except Exception as e:
            print(f"⚠️  Failed to create CI workflow: {str(e)}")

    def _generate_ci_workflow(self, project_type: str) -> str:
        """Генерация CI workflow на основе типа проекта"""

        # Python project
        if project_type in ['ml_system', 'data_analytics', 'automation', 'api_service']:
            return """name: CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest

    strategy:
      matrix:
        python-version: ['3.9', '3.10', '3.11']

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-cov flake8

    - name: Lint with flake8
      run: |
        flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
        flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

    - name: Test with pytest
      run: |
        pytest --cov=. --cov-report=xml

    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
"""

        # Node.js project
        elif project_type in ['web_app', 'mobile_app']:
            return """name: CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest

    strategy:
      matrix:
        node-version: [16.x, 18.x, 20.x]

    steps:
    - uses: actions/checkout@v3

    - name: Use Node.js ${{ matrix.node-version }}
      uses: actions/setup-node@v3
      with:
        node-version: ${{ matrix.node-version }}

    - name: Install dependencies
      run: npm ci

    - name: Lint
      run: npm run lint

    - name: Test
      run: npm test

    - name: Build
      run: npm run build
"""

        # Default generic workflow
        else:
            return """name: CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Run tests
      run: echo "Configure tests for your project"

    - name: Build
      run: echo "Configure build for your project"
"""

    def _create_labels(self, repo_full_name: str):
        """Создание стандартных labels"""

        labels = [
            {"name": "bug", "color": "d73a4a", "description": "Something isn't working"},
            {"name": "enhancement", "color": "a2eeef", "description": "New feature or request"},
            {"name": "documentation", "color": "0075ca", "description": "Documentation improvements"},
            {"name": "question", "color": "d876e3", "description": "Further information requested"},
            {"name": "good first issue", "color": "7057ff", "description": "Good for newcomers"},
            {"name": "help wanted", "color": "008672", "description": "Extra attention needed"},
            {"name": "priority: high", "color": "e11d21", "description": "High priority"},
            {"name": "priority: medium", "color": "fbca04", "description": "Medium priority"},
            {"name": "priority: low", "color": "0e8a16", "description": "Low priority"},
            {"name": "status: in progress", "color": "1d76db", "description": "Currently being worked on"},
            {"name": "status: blocked", "color": "b60205", "description": "Blocked by something"},
        ]

        created = self.github_api.create_labels(repo_full_name, labels)
        print(f"✅ Created {len(created)} labels")

    def _create_project_board(self, repo_full_name: str, project_name: str, project_type: str):
        """Создание GitHub Project board"""

        try:
            project = self.github_api.create_project(
                repo_full_name,
                name=f"{project_name} Development",
                body=f"Project board for {project_name} ({project_type})"
            )

            # Создание колонок
            columns = ["Backlog", "To Do", "In Progress", "Review", "Done"]
            created_columns = self.github_api.create_project_columns(
                project['id'],
                columns
            )

            print(f"✅ Created project board with {len(created_columns)} columns")

        except Exception as e:
            print(f"⚠️  Failed to create project board: {str(e)}")

    def _get_gitignore_type(self, project_type: str) -> str:
        """Определение типа .gitignore на основе типа проекта"""

        python_types = ['ml_system', 'data_analytics', 'automation', 'api_service', 'blockchain']
        node_types = ['web_app', 'mobile_app', 'game']
        java_types = ['enterprise_system']

        if project_type in python_types:
            return "python"
        elif project_type in node_types:
            return "node"
        elif project_type in java_types:
            return "java"
        else:
            return "python"  # Default


def main():
    """CLI interface"""
    parser = argparse.ArgumentParser(
        description="Create GitHub project with AI-generated structure"
    )
    parser.add_argument(
        '--description',
        required=True,
        help='Project description for AI analysis'
    )
    parser.add_argument(
        '--name',
        help='Project name (auto-generated if not provided)'
    )
    parser.add_argument(
        '--username',
        help='GitHub username (defaults to GITHUB_USERNAME env var)'
    )
    parser.add_argument(
        '--organization',
        help='GitHub organization (optional)'
    )
    parser.add_argument(
        '--private',
        action='store_true',
        help='Create private repository'
    )
    parser.add_argument(
        '--output',
        type=Path,
        help='Output directory for local project'
    )
    parser.add_argument(
        '--no-push',
        action='store_true',
        help='Do not push to GitHub (local only)'
    )
    parser.add_argument(
        '--no-project-board',
        action='store_true',
        help='Do not create GitHub Project board'
    )

    args = parser.parse_args()

    # Получение GitHub token
    token = get_github_token()
    if not token:
        print("❌ GitHub token not found!")
        print("\nPlease set one of the following:")
        print("  - GITHUB_TOKEN environment variable")
        print("  - GH_TOKEN environment variable")
        print("  - Install GitHub CLI (gh) and run: gh auth login")
        sys.exit(1)

    # Получение username
    username = args.username or os.environ.get('GITHUB_USERNAME')
    if not username:
        print("❌ GitHub username not provided!")
        print("\nPlease provide via:")
        print("  --username flag")
        print("  or GITHUB_USERNAME environment variable")
        sys.exit(1)

    # Создание конфигурации
    config = GitHubConfig(
        token=token,
        username=username,
        organization=args.organization,
        private=args.private
    )

    # Создание проекта
    creator = GitHubProjectCreator(config)

    try:
        result = creator.create_complete_project(
            description=args.description,
            project_name=args.name,
            private=args.private,
            output_dir=args.output,
            push_to_github=not args.no_push,
            setup_project_board=not args.no_project_board
        )

        print("\n🎉 Success! Your project is ready.")
        print(f"\nNext steps:")
        print(f"  cd {result['project_path']}")
        print(f"  # Start coding!")

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
