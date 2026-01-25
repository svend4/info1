"""
Production-ready Flask API для AI-powered генератора проектов

Включает:
- API Key authentication
- Rate limiting
- Request validation
- Error handling
- Logging
- Metrics
"""

from flask import Flask, request, jsonify, g
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import sys
import os
from pathlib import Path
import tempfile
import logging
from functools import wraps
from datetime import datetime
import hashlib

# Добавляем путь к ai_generator
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from tools.ai_generator.multi_label_classifier import MultiLabelClassifier
from tools.ai_generator.template_composer import TemplateComposer
from tools.ai_generator.enhanced_parameter_extractor import EnhancedParameterExtractor
from tools.ai_generator.context_aware_adapter import ContextAwareAdapter
from tools.ai_generator.llm_content_generator import LLMContentGenerator

# Конфигурация
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    API_KEYS = os.environ.get('API_KEYS', 'demo-key-123').split(',')
    RATE_LIMIT_DEFAULT = "100 per hour"
    RATE_LIMIT_ANALYZE = "50 per hour"
    RATE_LIMIT_GENERATE = "20 per hour"
    MAX_DESCRIPTION_LENGTH = 2000
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

# Logging
logging.basicConfig(
    level=getattr(logging, app.config['LOG_LEVEL']),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Rate limiting
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=[Config.RATE_LIMIT_DEFAULT],
    storage_uri="memory://"
)

# Метрики
class Metrics:
    def __init__(self):
        self.requests_total = 0
        self.requests_success = 0
        self.requests_error = 0
        self.analyze_count = 0
        self.generate_count = 0
        self.start_time = datetime.now()

    def record_request(self, success=True):
        self.requests_total += 1
        if success:
            self.requests_success += 1
        else:
            self.requests_error += 1

    def to_dict(self):
        uptime = (datetime.now() - self.start_time).total_seconds()
        return {
            'requests_total': self.requests_total,
            'requests_success': self.requests_success,
            'requests_error': self.requests_error,
            'analyze_count': self.analyze_count,
            'generate_count': self.generate_count,
            'uptime_seconds': int(uptime),
            'success_rate': round(self.requests_success / self.requests_total * 100, 2) if self.requests_total > 0 else 0
        }

metrics = Metrics()

# Инициализация AI компонентов
logger.info("Initializing AI components...")
classifier = MultiLabelClassifier()
composer = TemplateComposer()
extractor = EnhancedParameterExtractor()
adapter = ContextAwareAdapter()
generator = LLMContentGenerator()
logger.info("AI components initialized successfully")


# API Key authentication decorator
def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')

        if not api_key:
            api_key = request.args.get('api_key')

        if not api_key or api_key not in app.config['API_KEYS']:
            logger.warning(f"Unauthorized access attempt from {get_remote_address(request)}")
            return jsonify({'error': 'Invalid or missing API key'}), 401

        g.api_key = api_key
        return f(*args, **kwargs)

    return decorated_function


# Request validation
def validate_description(description):
    """Валидация описания проекта"""
    if not description:
        return False, "Description is required"

    if len(description) > Config.MAX_DESCRIPTION_LENGTH:
        return False, f"Description too long (max {Config.MAX_DESCRIPTION_LENGTH} chars)"

    if len(description.strip()) < 10:
        return False, "Description too short (min 10 chars)"

    return True, None


# Request logging
@app.before_request
def before_request():
    g.start_time = datetime.now()
    logger.info(f"{request.method} {request.path} from {get_remote_address(request)}")


@app.after_request
def after_request(response):
    if hasattr(g, 'start_time'):
        elapsed = (datetime.now() - g.start_time).total_seconds()
        logger.info(f"{request.method} {request.path} completed in {elapsed:.3f}s with status {response.status_code}")

    return response


@app.route('/api/ai/analyze', methods=['POST'])
@limiter.limit(Config.RATE_LIMIT_ANALYZE)
@require_api_key
def analyze_description():
    """Анализ описания проекта"""
    try:
        data = request.json
        description = data.get('description', '')

        # Валидация
        valid, error = validate_description(description)
        if not valid:
            metrics.record_request(success=False)
            return jsonify({'error': error}), 400

        logger.info(f"Analyzing project: {description[:50]}...")

        # Анализ
        ml_result = classifier.classify(description)
        params = extractor.extract(description)
        base_structure = composer.compose(ml_result)
        adapted = adapter.adapt(base_structure, params)

        # Формируем ответ
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

        metrics.record_request(success=True)
        metrics.analyze_count += 1

        logger.info(f"Analysis completed: {ml_result.primary_type} ({len(adapted.directories)} dirs)")

        return jsonify(response), 200

    except Exception as e:
        logger.error(f"Error in analyze endpoint: {str(e)}", exc_info=True)
        metrics.record_request(success=False)
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/ai/generate', methods=['POST'])
@limiter.limit(Config.RATE_LIMIT_GENERATE)
@require_api_key
def generate_project():
    """Генерация проекта (более строгий rate limit)"""
    try:
        data = request.json
        description = data.get('description', '')
        project_name = data.get('project_name')
        generate_content = data.get('generate_content', True)

        # Валидация
        valid, error = validate_description(description)
        if not valid:
            metrics.record_request(success=False)
            return jsonify({'error': error}), 400

        logger.info(f"Generating project: {description[:50]}...")

        # ... (остальной код такой же как в ai_api.py)
        ml_result = classifier.classify(description)
        params = extractor.extract(description)
        base_structure = composer.compose(ml_result)
        adapted = adapter.adapt(base_structure, params)

        if not project_name:
            from tools.ai_generator.classifier import ProjectClassifier
            temp_classifier = ProjectClassifier()
            temp_spec = temp_classifier.classify(description)
            project_name = temp_spec.name

        # Создаем проект...
        temp_dir = tempfile.mkdtemp()
        project_path = Path(temp_dir) / project_name

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

        if generate_content:
            content = generator.generate_all(
                ml_result, params, adapted, project_name, description
            )

            # Сохранение файлов...
            readme_path = project_path / "README.md"
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(content.readme)
            generated_files.append('README.md')

            if content.architecture:
                arch_path = project_path / "ARCHITECTURE.md"
                with open(arch_path, 'w', encoding='utf-8') as f:
                    f.write(content.architecture)
                generated_files.append('ARCHITECTURE.md')

            if content.contributing:
                contrib_path = project_path / "CONTRIBUTING.md"
                with open(contrib_path, 'w', encoding='utf-8') as f:
                    f.write(content.contributing)
                generated_files.append('CONTRIBUTING.md')

            if content.checklist:
                checklist_path = project_path / "CHECKLIST.md"
                with open(checklist_path, 'w', encoding='utf-8') as f:
                    f.write(content.checklist)
                generated_files.append('CHECKLIST.md')

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

        metrics.record_request(success=True)
        metrics.generate_count += 1

        logger.info(f"Project generated: {project_name} ({len(generated_files)} files)")

        return jsonify(response), 200

    except subprocess.CalledProcessError as e:
        logger.error(f"Project generation failed: {e.stderr}")
        metrics.record_request(success=False)
        return jsonify({'error': f'Project generation failed: {e.stderr}'}), 500
    except Exception as e:
        logger.error(f"Error in generate endpoint: {str(e)}", exc_info=True)
        metrics.record_request(success=False)
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/ai/health', methods=['GET'])
def health_check():
    """Health check (без требования API key)"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'ai_components': 'ready',
        'ml_model': 'loaded' if classifier.ml_classifier.is_trained else 'not_loaded'
    }), 200


@app.route('/api/ai/metrics', methods=['GET'])
@require_api_key
def get_metrics():
    """Получение метрик (требует API key)"""
    return jsonify(metrics.to_dict()), 200


@app.errorhandler(429)
def ratelimit_handler(e):
    """Rate limit error handler"""
    logger.warning(f"Rate limit exceeded for {get_remote_address(request)}")
    return jsonify({
        'error': 'Rate limit exceeded',
        'message': str(e.description)
    }), 429


@app.errorhandler(500)
def internal_error(e):
    """Internal server error handler"""
    logger.error(f"Internal server error: {str(e)}", exc_info=True)
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    print("="*70)
    print("🚀 AI Generator API Server (Production)")
    print("="*70)
    print("\nConfiguration:")
    print(f"  Rate Limits:")
    print(f"    - Default: {Config.RATE_LIMIT_DEFAULT}")
    print(f"    - Analyze: {Config.RATE_LIMIT_ANALYZE}")
    print(f"    - Generate: {Config.RATE_LIMIT_GENERATE}")
    print(f"  API Keys: {len(app.config['API_KEYS'])} configured")
    print(f"  Log Level: {Config.LOG_LEVEL}")
    print("\nEndpoints:")
    print("  POST /api/ai/analyze  - Analyze project (requires API key)")
    print("  POST /api/ai/generate - Generate project (requires API key)")
    print("  GET  /api/ai/health   - Health check (public)")
    print("  GET  /api/ai/metrics  - Get metrics (requires API key)")
    print("\nAuthentication:")
    print("  Header: X-API-Key: your-api-key")
    print("  or Query: ?api_key=your-api-key")
    print("\nStarting server on http://0.0.0.0:5001")
    print("="*70)

    # Production server (use gunicorn в реальной prod)
    app.run(debug=False, port=5001, host='0.0.0.0')
