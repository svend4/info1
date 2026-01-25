#!/usr/bin/env python3
"""
LLM Content Generator (Фаза 4 ЭТАПА 9)

Генерация персонализированного контента для проектов:
- README.md с учётом параметров
- Примеры кода для технологий
- Чеклисты на основе фазы и параметров
- Документация (ARCHITECTURE.md, etc.)

Примечание: В production можно подключить Claude API для real-time генерации.
Текущая версия использует template-based подход с rich customization.
"""

import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pathlib import Path

try:
    from .enhanced_parameter_extractor import ExtractedParameters
    from .context_aware_adapter import AdaptedStructure
    from .multi_label_classifier import MultiLabelResult
except ImportError:
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from ai_generator.enhanced_parameter_extractor import ExtractedParameters
    from ai_generator.context_aware_adapter import AdaptedStructure
    from ai_generator.multi_label_classifier import MultiLabelResult


@dataclass
class GeneratedContent:
    """Сгенерированный контент для проекта"""
    readme: str
    architecture: Optional[str] = None
    contributing: Optional[str] = None
    checklist: Optional[str] = None
    code_examples: Dict[str, str] = None

    def __post_init__(self):
        if self.code_examples is None:
            self.code_examples = {}


class LLMContentGenerator:
    """
    Генератор персонализированного контента

    Использует template-based подход с параметрами для создания:
    - README.md (адаптированный под тип проекта)
    - Code examples (для specific tech stack)
    - Checklists (на основе phase, team, risk)
    - Documentation files
    """

    def __init__(self):
        """Инициализация генератора"""
        pass

    def generate_all(
        self,
        ml_result: MultiLabelResult,
        parameters: ExtractedParameters,
        adapted_structure: AdaptedStructure,
        project_name: str,
        description: str
    ) -> GeneratedContent:
        """
        Генерация всего контента для проекта

        Args:
            ml_result: Результат multi-label классификации
            parameters: Извлечённые параметры
            adapted_structure: Адаптированная структура
            project_name: Имя проекта
            description: Исходное описание

        Returns:
            GeneratedContent со всеми сгенерированными файлами
        """
        readme = self.generate_readme(
            ml_result, parameters, adapted_structure, project_name, description
        )

        architecture = None
        if parameters.scale == 'large' or (parameters.team_size and parameters.team_size >= 20):
            architecture = self.generate_architecture_doc(
                ml_result, parameters, project_name
            )

        contributing = None
        if parameters.team_size and parameters.team_size >= 5:
            contributing = self.generate_contributing_guide(parameters)

        checklist = self.generate_checklist(ml_result, parameters)

        code_examples = self.generate_code_examples(parameters)

        return GeneratedContent(
            readme=readme,
            architecture=architecture,
            contributing=contributing,
            checklist=checklist,
            code_examples=code_examples
        )

    def generate_readme(
        self,
        ml_result: MultiLabelResult,
        parameters: ExtractedParameters,
        adapted_structure: AdaptedStructure,
        project_name: str,
        description: str
    ) -> str:
        """Генерация персонализированного README.md"""

        # Header
        readme_parts = []
        readme_parts.append(f"# {project_name}")
        readme_parts.append("")
        readme_parts.append(f"*{description}*")
        readme_parts.append("")

        # Badges
        badges = self._generate_badges(ml_result, parameters)
        if badges:
            readme_parts.append(badges)
            readme_parts.append("")

        # Overview
        readme_parts.append("## 📋 Overview")
        readme_parts.append("")
        overview = self._generate_overview(ml_result, parameters)
        readme_parts.append(overview)
        readme_parts.append("")

        # Key Features (если есть вторичные типы)
        if ml_result.secondary_types:
            readme_parts.append("## ✨ Key Features")
            readme_parts.append("")
            features = self._generate_features(ml_result, parameters)
            readme_parts.extend(features)
            readme_parts.append("")

        # Tech Stack
        if parameters.technologies:
            readme_parts.append("## 🛠️ Tech Stack")
            readme_parts.append("")
            tech_stack = self._generate_tech_stack(parameters)
            readme_parts.extend(tech_stack)
            readme_parts.append("")

        # Getting Started
        readme_parts.append("## 🚀 Getting Started")
        readme_parts.append("")
        getting_started = self._generate_getting_started(parameters)
        readme_parts.extend(getting_started)
        readme_parts.append("")

        # Project Structure
        readme_parts.append("## 📁 Project Structure")
        readme_parts.append("")
        readme_parts.append("```")
        readme_parts.append(f"{project_name}/")
        for directory in adapted_structure.directories[:10]:  # Top 10
            readme_parts.append(f"├── {directory}")
        if len(adapted_structure.directories) > 10:
            readme_parts.append(f"└── ... ({len(adapted_structure.directories) - 10} more)")
        readme_parts.append("```")
        readme_parts.append("")

        # Development (если есть команда)
        if parameters.team_size and parameters.team_size >= 5:
            readme_parts.append("## 👥 Development")
            readme_parts.append("")
            readme_parts.append(f"This project is developed by a team of {parameters.team_size} members.")
            readme_parts.append("")
            readme_parts.append("See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines.")
            readme_parts.append("")

        # Timeline & Budget (если есть)
        if parameters.timeline or parameters.budget:
            readme_parts.append("## 📊 Project Info")
            readme_parts.append("")
            if parameters.timeline:
                readme_parts.append(f"- **Timeline:** {parameters.timeline['formatted']}")
            if parameters.budget:
                readme_parts.append(f"- **Budget:** {parameters.budget['formatted']}")
            if parameters.phase:
                readme_parts.append(f"- **Phase:** {parameters.phase.upper()}")
            readme_parts.append("")

        # License
        readme_parts.append("## 📄 License")
        readme_parts.append("")
        license_text = "MIT" if not parameters.is_nonprofit else "CC BY-NC-SA 4.0"
        readme_parts.append(f"This project is licensed under the {license_text} License.")
        readme_parts.append("")

        # Footer
        readme_parts.append("---")
        readme_parts.append("")
        readme_parts.append(f"Generated with AI-powered project generator")
        readme_parts.append("")

        return "\n".join(readme_parts)

    def _generate_badges(self, ml_result: MultiLabelResult, parameters: ExtractedParameters) -> str:
        """Генерация badges для README"""
        badges = []

        # Type badge
        badges.append(f"![Type](https://img.shields.io/badge/type-{ml_result.primary_type}-blue)")

        # Phase badge
        if parameters.phase:
            color = {
                'concept': 'lightgrey',
                'planning': 'yellow',
                'mvp': 'orange',
                'alpha': 'red',
                'beta': 'purple',
                'production': 'green',
                'scaling': 'brightgreen'
            }.get(parameters.phase, 'blue')
            badges.append(f"![Phase](https://img.shields.io/badge/phase-{parameters.phase}-{color})")

        # Priority badge
        if parameters.priority:
            color = {
                'low': 'lightgrey',
                'medium': 'yellow',
                'high': 'orange',
                'critical': 'red'
            }.get(parameters.priority, 'blue')
            badges.append(f"![Priority](https://img.shields.io/badge/priority-{parameters.priority}-{color})")

        return " ".join(badges)

    def _generate_overview(self, ml_result: MultiLabelResult, parameters: ExtractedParameters) -> str:
        """Генерация overview секции"""
        lines = []

        # Primary type description
        type_descriptions = {
            'software': 'A software development project focused on building scalable applications.',
            'research': 'A research project aimed at advancing knowledge in the field.',
            'business': 'A business venture focused on creating value and generating revenue.',
            'education': 'An educational initiative designed to teach and train participants.',
            'healthcare': 'A healthcare project improving patient care and medical services.',
            'finance': 'A financial project managing investments and monetary resources.',
            'legal': 'A legal services project providing consultation and support.',
            'arts': 'An artistic project showcasing creativity and cultural expression.',
            'government': 'A government initiative serving public needs and citizens.',
            'nonprofit': 'A nonprofit organization working towards social impact.',
            'manufacturing': 'A manufacturing project producing goods and materials.',
            'agriculture': 'An agricultural project focused on farming and food production.',
            'sports': 'A sports project promoting physical activity and competition.',
            'hospitality': 'A hospitality business providing services and accommodations.',
            'retail': 'A retail business selling products to consumers.',
            'hobby': 'A personal hobby project pursued for enjoyment and learning.',
        }

        lines.append(type_descriptions.get(ml_result.primary_type, 'A project focused on achieving its goals.'))
        lines.append("")

        # Hybrid nature
        if ml_result.is_hybrid:
            types_str = ", ".join(ml_result.secondary_types)
            lines.append(f"This is a **hybrid project** combining aspects of {ml_result.primary_type} with {types_str}.")
            lines.append("")

        # Target audience
        if parameters.target_audience:
            audience_str = ", ".join(parameters.target_audience)
            lines.append(f"**Target Audience:** {audience_str}")
            lines.append("")

        return "\n".join(lines)

    def _generate_features(self, ml_result: MultiLabelResult, parameters: ExtractedParameters) -> List[str]:
        """Генерация key features"""
        features = []

        # Features based on primary type
        type_features = {
            'software': ['🔧 Modern architecture', '⚡ High performance', '🔐 Secure by design'],
            'research': ['📊 Data-driven methodology', '🔬 Rigorous analysis', '📈 Reproducible results'],
            'business': ['💼 Revenue generation', '📈 Scalable model', '🎯 Market focused'],
            'education': ['📚 Comprehensive curriculum', '👨‍🎓 Student-centered', '✅ Progress tracking'],
            'healthcare': ['🏥 Patient-focused', '🔐 HIPAA compliant', '📋 Evidence-based'],
            'finance': ['💰 Risk management', '📊 Portfolio optimization', '🔒 Secure transactions'],
        }

        primary_features = type_features.get(ml_result.primary_type, ['✨ High quality', '🚀 Fast delivery'])
        features.extend([f"- {f}" for f in primary_features])

        # Add tech-specific features
        if 'react' in parameters.technologies:
            features.append("- ⚛️ Modern React UI")
        if 'docker' in parameters.technologies:
            features.append("- 🐳 Containerized deployment")
        if any(db in parameters.technologies for db in ['postgresql', 'mongodb']):
            features.append("- 🗄️ Robust database layer")

        return features

    def _generate_tech_stack(self, parameters: ExtractedParameters) -> List[str]:
        """Генерация tech stack списка"""
        tech_stack = []

        # Group by category
        frontend = [t for t in parameters.technologies if t in ['react', 'vue', 'angular', 'svelte']]
        backend = [t for t in parameters.technologies if t in ['node', 'python', 'django', 'flask', 'fastapi', 'go', 'java']]
        databases = [t for t in parameters.technologies if t in ['postgresql', 'mysql', 'mongodb', 'redis']]
        devops = [t for t in parameters.technologies if t in ['docker', 'kubernetes', 'aws', 'azure', 'gcp']]

        if frontend:
            tech_stack.append(f"- **Frontend:** {', '.join(frontend)}")
        if backend:
            tech_stack.append(f"- **Backend:** {', '.join(backend)}")
        if databases:
            tech_stack.append(f"- **Database:** {', '.join(databases)}")
        if devops:
            tech_stack.append(f"- **DevOps:** {', '.join(devops)}")

        return tech_stack

    def _generate_getting_started(self, parameters: ExtractedParameters) -> List[str]:
        """Генерация Getting Started секции"""
        lines = []

        # Prerequisites
        lines.append("### Prerequisites")
        lines.append("")

        if 'python' in parameters.technologies:
            lines.append("- Python 3.8+")
        if 'node' in parameters.technologies or 'react' in parameters.technologies:
            lines.append("- Node.js 16+")
        if 'docker' in parameters.technologies:
            lines.append("- Docker & Docker Compose")

        lines.append("")

        # Installation
        lines.append("### Installation")
        lines.append("")
        lines.append("```bash")
        lines.append("# Clone the repository")
        lines.append("git clone <repository-url>")
        lines.append("cd <project-directory>")
        lines.append("")

        if 'python' in parameters.technologies:
            lines.append("# Install Python dependencies")
            lines.append("pip install -r requirements.txt")
        elif 'node' in parameters.technologies or 'react' in parameters.technologies:
            lines.append("# Install Node dependencies")
            lines.append("npm install")

        if 'docker' in parameters.technologies:
            lines.append("")
            lines.append("# Run with Docker")
            lines.append("docker-compose up -d")

        lines.append("```")

        return lines

    def generate_architecture_doc(
        self,
        ml_result: MultiLabelResult,
        parameters: ExtractedParameters,
        project_name: str
    ) -> str:
        """Генерация ARCHITECTURE.md для крупных проектов"""
        lines = []

        lines.append(f"# {project_name} - Architecture")
        lines.append("")
        lines.append("## Overview")
        lines.append("")
        lines.append(f"This document describes the architecture of the {ml_result.primary_type} project.")
        lines.append("")

        # System Components
        lines.append("## System Components")
        lines.append("")

        if 'react' in parameters.technologies:
            lines.append("### Frontend Layer")
            lines.append("- **Framework:** React")
            lines.append("- **State Management:** Context API / Redux")
            lines.append("- **Routing:** React Router")
            lines.append("")

        if any(t in parameters.technologies for t in ['django', 'flask', 'fastapi', 'node']):
            lines.append("### Backend Layer")
            backend_tech = next((t for t in ['django', 'flask', 'fastapi', 'node'] if t in parameters.technologies), 'N/A')
            lines.append(f"- **Framework:** {backend_tech}")
            lines.append("- **API:** RESTful / GraphQL")
            lines.append("- **Authentication:** JWT / OAuth")
            lines.append("")

        if any(db in parameters.technologies for db in ['postgresql', 'mongodb', 'mysql']):
            lines.append("### Data Layer")
            db_tech = next((t for t in ['postgresql', 'mongodb', 'mysql'] if t in parameters.technologies), 'N/A')
            lines.append(f"- **Database:** {db_tech}")
            lines.append("- **ORM:** SQLAlchemy / Prisma")
            lines.append("- **Migrations:** Alembic / Flyway")
            lines.append("")

        # Deployment
        if 'docker' in parameters.technologies or 'kubernetes' in parameters.technologies:
            lines.append("## Deployment Architecture")
            lines.append("")
            if 'kubernetes' in parameters.technologies:
                lines.append("- **Orchestration:** Kubernetes")
                lines.append("- **Service Mesh:** Istio (optional)")
                lines.append("- **Monitoring:** Prometheus + Grafana")
            else:
                lines.append("- **Containerization:** Docker")
                lines.append("- **Deployment:** Docker Compose")
            lines.append("")

        # Scalability
        if parameters.scale == 'large':
            lines.append("## Scalability")
            lines.append("")
            lines.append("The system is designed to scale horizontally:")
            lines.append("- Stateless application tier")
            lines.append("- Database replication")
            lines.append("- Caching layer (Redis)")
            lines.append("- Load balancing")
            lines.append("")

        return "\n".join(lines)

    def generate_contributing_guide(self, parameters: ExtractedParameters) -> str:
        """Генерация CONTRIBUTING.md для команд"""
        lines = []

        lines.append("# Contributing Guide")
        lines.append("")
        lines.append(f"Thank you for contributing to this project! We're a team of {parameters.team_size} members.")
        lines.append("")

        # Code of Conduct
        lines.append("## Code of Conduct")
        lines.append("")
        lines.append("Please read and follow our [Code of Conduct](CODE-OF-CONDUCT.md).")
        lines.append("")

        # Development Process
        lines.append("## Development Process")
        lines.append("")
        lines.append("1. **Fork** the repository")
        lines.append("2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)")
        lines.append("3. **Commit** your changes (`git commit -m 'Add amazing feature'`)")
        lines.append("4. **Push** to the branch (`git push origin feature/amazing-feature`)")
        lines.append("5. **Open** a Pull Request")
        lines.append("")

        # Code Style
        lines.append("## Code Style")
        lines.append("")
        if 'python' in parameters.technologies:
            lines.append("- Follow PEP 8 style guide")
            lines.append("- Use type hints")
            lines.append("- Run `black` for formatting")
        elif 'react' in parameters.technologies or 'node' in parameters.technologies:
            lines.append("- Follow ESLint rules")
            lines.append("- Use Prettier for formatting")
            lines.append("- Prefer functional components")
        lines.append("")

        # Testing
        lines.append("## Testing")
        lines.append("")
        lines.append("- Write tests for new features")
        lines.append("- Ensure all tests pass before submitting PR")
        lines.append("- Maintain test coverage above 80%")
        lines.append("")

        # Pull Request Process
        if parameters.team_size >= 10:
            lines.append("## Pull Request Review")
            lines.append("")
            lines.append("- PRs require 2 approvals from team members")
            lines.append("- CI/CD checks must pass")
            lines.append("- Code review within 24-48 hours")
            lines.append("")

        return "\n".join(lines)

    def generate_checklist(self, ml_result: MultiLabelResult, parameters: ExtractedParameters) -> str:
        """Генерация персонализированного чеклиста"""
        lines = []

        lines.append("# Project Checklist")
        lines.append("")

        # Phase-specific checklist
        if parameters.phase == 'mvp':
            lines.append("## MVP Phase Checklist")
            lines.append("")
            lines.append("- [ ] Define core features")
            lines.append("- [ ] Create wireframes/mockups")
            lines.append("- [ ] Implement minimum viable features")
            lines.append("- [ ] Basic testing")
            lines.append("- [ ] Deploy to staging")
            lines.append("- [ ] Gather initial feedback")
            lines.append("")

        elif parameters.phase == 'production':
            lines.append("## Production Launch Checklist")
            lines.append("")
            lines.append("- [ ] Complete feature development")
            lines.append("- [ ] Comprehensive testing (unit, integration, e2e)")
            lines.append("- [ ] Security audit")
            lines.append("- [ ] Performance optimization")
            lines.append("- [ ] Documentation complete")
            lines.append("- [ ] Monitoring setup")
            lines.append("- [ ] Backup & disaster recovery plan")
            lines.append("- [ ] Deploy to production")
            lines.append("")

        # Team-specific items
        if parameters.team_size and parameters.team_size >= 10:
            lines.append("## Team Coordination")
            lines.append("")
            lines.append("- [ ] Onboarding documentation")
            lines.append("- [ ] Code review process")
            lines.append("- [ ] CI/CD pipeline setup")
            lines.append("- [ ] Team communication channels")
            lines.append("")

        # Tech-specific items
        if 'docker' in parameters.technologies:
            lines.append("## Containerization")
            lines.append("")
            lines.append("- [ ] Dockerfile created")
            lines.append("- [ ] Docker Compose configuration")
            lines.append("- [ ] Multi-stage builds optimized")
            lines.append("")

        if any(db in parameters.technologies for db in ['postgresql', 'mongodb']):
            lines.append("## Database")
            lines.append("")
            lines.append("- [ ] Schema design")
            lines.append("- [ ] Migrations setup")
            lines.append("- [ ] Backup strategy")
            lines.append("- [ ] Performance indexing")
            lines.append("")

        # Risk management (if high risk)
        if parameters.risk_level == 'high':
            lines.append("## Risk Management")
            lines.append("")
            lines.append("- [ ] Risk assessment document")
            lines.append("- [ ] Mitigation strategies")
            lines.append("- [ ] Contingency plans")
            lines.append("- [ ] Regular risk reviews")
            lines.append("")

        return "\n".join(lines)

    def generate_code_examples(self, parameters: ExtractedParameters) -> Dict[str, str]:
        """Генерация примеров кода для технологий"""
        examples = {}

        if 'react' in parameters.technologies:
            examples['react_component.jsx'] = self._react_example()

        if 'python' in parameters.technologies:
            examples['main.py'] = self._python_example()

        if 'django' in parameters.technologies:
            examples['models.py'] = self._django_model_example()

        if 'docker' in parameters.technologies:
            examples['Dockerfile'] = self._dockerfile_example(parameters)

        if 'fastapi' in parameters.technologies:
            examples['api.py'] = self._fastapi_example()

        return examples

    def _react_example(self) -> str:
        return """// Example React Component
import React, { useState } from 'react';

const ExampleComponent = () => {
  const [count, setCount] = useState(0);

  return (
    <div>
      <h1>Example Component</h1>
      <p>Count: {count}</p>
      <button onClick={() => setCount(count + 1)}>
        Increment
      </button>
    </div>
  );
};

export default ExampleComponent;
"""

    def _python_example(self) -> str:
        return """#!/usr/bin/env python3
\"\"\"
Example Python module
\"\"\"

from typing import List, Optional


class ExampleClass:
    \"\"\"Example class with type hints\"\"\"

    def __init__(self, name: str):
        self.name = name

    def process(self, items: List[str]) -> Optional[str]:
        \"\"\"Process items and return result\"\"\"
        if not items:
            return None
        return f"{self.name}: {', '.join(items)}"


def main():
    \"\"\"Main entry point\"\"\"
    example = ExampleClass("Demo")
    result = example.process(["item1", "item2"])
    print(result)


if __name__ == '__main__':
    main()
"""

    def _django_model_example(self) -> str:
        return """from django.db import models


class ExampleModel(models.Model):
    \"\"\"Example Django model\"\"\"

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Example'
        verbose_name_plural = 'Examples'

    def __str__(self):
        return self.name
"""

    def _dockerfile_example(self, parameters: ExtractedParameters) -> str:
        if 'python' in parameters.technologies:
            return """# Python Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "main.py"]
"""
        else:
            return """# Node.js Dockerfile
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production

COPY . .

EXPOSE 3000

CMD ["npm", "start"]
"""

    def _fastapi_example(self) -> str:
        return """from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


app = FastAPI(title="Example API")


class Item(BaseModel):
    name: str
    description: str = None


@app.get("/")
def read_root():
    return {"message": "Welcome to the API"}


@app.post("/items/")
def create_item(item: Item):
    return {"item": item, "status": "created"}


@app.get("/items/{item_id}")
def read_item(item_id: int):
    if item_id < 0:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"item_id": item_id}
"""


def main():
    """Тестирование LLM content generator"""
    from multi_label_classifier import MultiLabelClassifier
    from enhanced_parameter_extractor import EnhancedParameterExtractor
    from template_composer import TemplateComposer
    from context_aware_adapter import ContextAwareAdapter

    # Test case
    description = "Финтех MVP на React+FastAPI, бюджет 3 млн ₽, команда 8 человек, срок 4 месяца"
    project_name = "fintech-mvp"

    # Pipeline
    classifier = MultiLabelClassifier()
    extractor = EnhancedParameterExtractor()
    composer = TemplateComposer()
    adapter = ContextAwareAdapter()
    generator = LLMContentGenerator()

    print("="*70)
    print("LLM CONTENT GENERATOR - TESTING")
    print("="*70)
    print(f"\nProject: {project_name}")
    print(f"Description: {description}")
    print("\n" + "="*70)

    # Full pipeline
    ml_result = classifier.classify(description)
    params = extractor.extract(description)
    base_structure = composer.compose(ml_result)
    adapted = adapter.adapt(base_structure, params)

    # Generate content
    content = generator.generate_all(
        ml_result, params, adapted, project_name, description
    )

    print("\n📄 Generated README.md:")
    print("="*70)
    print(content.readme[:500] + "..." if len(content.readme) > 500 else content.readme)

    if content.checklist:
        print("\n✅ Generated CHECKLIST.md:")
        print("="*70)
        print(content.checklist[:300] + "..." if len(content.checklist) > 300 else content.checklist)

    if content.code_examples:
        print(f"\n💻 Generated {len(content.code_examples)} code examples:")
        for filename in content.code_examples.keys():
            print(f"   - {filename}")

    print("\n" + "="*70)
    print("✅ Content generation complete!")


if __name__ == '__main__':
    main()
