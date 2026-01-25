"""
Flask API для AI-powered генератора проектов

Endpoint для интеграции с веб-интерфейсом.
Обрабатывает natural language описания и возвращает структуру проекта.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os
from pathlib import Path
import tempfile
import shutil

# Добавляем путь к ai_generator
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from tools.ai_generator.multi_label_classifier import MultiLabelClassifier
from tools.ai_generator.template_composer import TemplateComposer
from tools.ai_generator.enhanced_parameter_extractor import EnhancedParameterExtractor
from tools.ai_generator.context_aware_adapter import ContextAwareAdapter
from tools.ai_generator.llm_content_generator import LLMContentGenerator

app = Flask(__name__)
CORS(app)  # Разрешаем CORS для локальной разработки

# Инициализация AI компонентов при старте
print("🔧 Инициализация AI компонентов...")
classifier = MultiLabelClassifier()
composer = TemplateComposer()
extractor = EnhancedParameterExtractor()
adapter = ContextAwareAdapter()
generator = LLMContentGenerator()
print("✅ AI компоненты готовы!")


@app.route('/api/ai/analyze', methods=['POST'])
def analyze_description():
    """
    Анализ описания проекта без создания файлов

    POST /api/ai/analyze
    {
        "description": "Финтех MVP на React, бюджет 3 млн ₽"
    }

    Returns:
    {
        "classification": {...},
        "parameters": {...},
        "structure": {...},
        "adaptations": [...],
        "content_preview": {...}
    }
    """
    try:
        data = request.json
        description = data.get('description', '')

        if not description:
            return jsonify({'error': 'Description is required'}), 400

        # Phase 1-2: Classification
        ml_result = classifier.classify(description)

        # Phase 3: Parameter extraction
        params = extractor.extract(description)

        # Phase 3: Template composition
        base_structure = composer.compose(ml_result)

        # Phase 3: Context-aware adaptation
        adapted = adapter.adapt(base_structure, params)

        # Prepare response
        response = {
            'classification': {
                'primary_type': ml_result.primary_type,
                'primary_confidence': ml_result.primary_confidence,
                'secondary_types': ml_result.secondary_types,
                'secondary_confidences': ml_result.secondary_confidences,
                'is_hybrid': ml_result.is_hybrid,
            },
            'parameters': {
                'budget': params.budget,
                'timeline': params.timeline,
                'team_size': params.team_size,
                'phase': params.phase,
                'technologies': params.technologies,
                'priority': params.priority,
                'risk_level': params.risk_level,
                'industry': params.industry,
                'scale': params.scale,
                'is_funded': params.is_funded,
                'is_commercial': params.is_commercial,
                'is_nonprofit': params.is_nonprofit,
            },
            'structure': {
                'strategy': base_structure.strategy,
                'merged_types': base_structure.merged_types,
                'base_directories': base_structure.directories,
                'base_files': base_structure.files,
                'adapted_directories': adapted.directories,
                'adapted_files': adapted.files,
                'growth_percent': round(
                    (len(adapted.directories) - len(base_structure.directories)) /
                    len(base_structure.directories) * 100
                ) if len(base_structure.directories) > 0 else 0
            },
            'adaptations': adapted.adaptations,
            'recommendations': adapted.recommendations if hasattr(adapted, 'recommendations') else []
        }

        return jsonify(response), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/ai/generate', methods=['POST'])
def generate_project():
    """
    Генерация проекта с созданием файлов

    POST /api/ai/generate
    {
        "description": "Финтех MVP на React",
        "project_name": "my-fintech-app",
        "generate_content": true
    }

    Returns:
    {
        "success": true,
        "project_path": "/tmp/my-fintech-app",
        "structure": {...},
        "generated_files": [...]
    }
    """
    try:
        data = request.json
        description = data.get('description', '')
        project_name = data.get('project_name')
        generate_content = data.get('generate_content', True)

        if not description:
            return jsonify({'error': 'Description is required'}), 400

        # Анализ
        ml_result = classifier.classify(description)
        params = extractor.extract(description)
        base_structure = composer.compose(ml_result)
        adapted = adapter.adapt(base_structure, params)

        # Генерация имени если не указано
        if not project_name:
            from tools.ai_generator.classifier import ProjectClassifier
            temp_classifier = ProjectClassifier()
            temp_spec = temp_classifier.classify(description)
            project_name = temp_spec.name

        # Создаем временную директорию
        temp_dir = tempfile.mkdtemp()
        project_path = Path(temp_dir) / project_name

        # Вызываем генератор проектов
        import subprocess
        generator_path = Path(__file__).parent.parent.parent / 'tools' / 'project_template_generator.py'

        cmd = [
            sys.executable,
            str(generator_path),
            '--name', project_name,
            '--type', ml_result.primary_type,
            '--output', temp_dir
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, check=True)

        generated_files = []

        # Генерация контента если включено
        if generate_content:
            content = generator.generate_all(
                ml_result, params, adapted, project_name, description
            )

            # Сохраняем README
            readme_path = project_path / "README.md"
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(content.readme)
            generated_files.append('README.md')

            # ARCHITECTURE
            if content.architecture:
                arch_path = project_path / "ARCHITECTURE.md"
                with open(arch_path, 'w', encoding='utf-8') as f:
                    f.write(content.architecture)
                generated_files.append('ARCHITECTURE.md')

            # CONTRIBUTING
            if content.contributing:
                contrib_path = project_path / "CONTRIBUTING.md"
                with open(contrib_path, 'w', encoding='utf-8') as f:
                    f.write(content.contributing)
                generated_files.append('CONTRIBUTING.md')

            # CHECKLIST
            if content.checklist:
                checklist_path = project_path / "CHECKLIST.md"
                with open(checklist_path, 'w', encoding='utf-8') as f:
                    f.write(content.checklist)
                generated_files.append('CHECKLIST.md')

            # Code examples
            if content.code_examples:
                examples_dir = project_path / "examples"
                examples_dir.mkdir(exist_ok=True)
                for filename, code in content.code_examples.items():
                    example_path = examples_dir / filename
                    with open(example_path, 'w', encoding='utf-8') as f:
                        f.write(code)
                    generated_files.append(f'examples/{filename}')

        response = {
            'success': True,
            'project_name': project_name,
            'project_path': str(project_path),
            'classification': {
                'primary_type': ml_result.primary_type,
                'secondary_types': ml_result.secondary_types,
            },
            'structure': {
                'directories': len(adapted.directories),
                'files': len(adapted.files),
                'adaptations': len(adapted.adaptations),
            },
            'generated_files': generated_files
        }

        return jsonify(response), 200

    except subprocess.CalledProcessError as e:
        return jsonify({'error': f'Project generation failed: {e.stderr}'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/ai/preview', methods=['POST'])
def preview_content():
    """
    Preview генерируемого контента (README, CHECKLIST, etc.)

    POST /api/ai/preview
    {
        "description": "...",
        "project_name": "...",
        "content_type": "readme" | "architecture" | "contributing" | "checklist"
    }
    """
    try:
        data = request.json
        description = data.get('description', '')
        project_name = data.get('project_name', 'my-project')
        content_type = data.get('content_type', 'readme')

        if not description:
            return jsonify({'error': 'Description is required'}), 400

        # Анализ
        ml_result = classifier.classify(description)
        params = extractor.extract(description)
        base_structure = composer.compose(ml_result)
        adapted = adapter.adapt(base_structure, params)

        # Генерация контента
        content = generator.generate_all(
            ml_result, params, adapted, project_name, description
        )

        # Выбираем нужный тип контента
        content_map = {
            'readme': content.readme,
            'architecture': content.architecture,
            'contributing': content.contributing,
            'checklist': content.checklist,
        }

        selected_content = content_map.get(content_type)

        if selected_content is None:
            return jsonify({
                'content': None,
                'message': f'{content_type} not generated for this project'
            }), 200

        return jsonify({
            'content': selected_content,
            'content_type': content_type
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/ai/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'ai_components': 'ready',
        'ml_model': 'loaded' if classifier.ml_classifier.is_trained else 'not_loaded'
    }), 200


if __name__ == '__main__':
    print("="*70)
    print("🚀 AI Generator API Server")
    print("="*70)
    print("\nEndpoints:")
    print("  POST /api/ai/analyze  - Analyze project description")
    print("  POST /api/ai/generate - Generate project files")
    print("  POST /api/ai/preview  - Preview generated content")
    print("  GET  /api/ai/health   - Health check")
    print("\nStarting server on http://localhost:5001")
    print("="*70)

    app.run(debug=True, port=5001, host='0.0.0.0')
