"""
Flask REST API для карточной системы

Пример интеграции карточной системы в веб-приложение.

Установка:
    pip install flask flask-cors

Запуск:
    python flask_api_example.py

API будет доступен на http://localhost:5000
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from pathlib import Path
import sys

# Добавляем путь к card_system
sys.path.insert(0, str(Path(__file__).parent.parent / "card_system"))

from card import TaskCard, MedicineCard, ContactCard, CardType
from card_manager import CardManager

app = Flask(__name__)
CORS(app)  # Разрешаем CORS для frontend

# Инициализация менеджера карточек
CARDS_DIR = Path(__file__).parent / "api_cards"
CARDS_DIR.mkdir(exist_ok=True)
manager = CardManager(CARDS_DIR)


# ============================================================================
# GET endpoints — Получение данных
# ============================================================================

@app.route('/api/cards', methods=['GET'])
def get_cards():
    """
    Получить все карточки

    Query parameters:
    - type: фильтр по типу (task, medicine, contact, etc.)
    - status: фильтр по статусу (pending, completed, etc.)
    - limit: лимит количества (по умолчанию: все)

    Example:
        GET /api/cards?type=task&status=pending
    """
    card_type = request.args.get('type')
    status = request.args.get('status')
    limit = request.args.get('limit', type=int)

    # Поиск с фильтрами
    filters = {}
    if card_type:
        filters['card_type'] = card_type
    if status:
        filters['status'] = status

    cards = manager.search(**filters)

    # Применяем limit
    if limit:
        cards = cards[:limit]

    # Конвертируем в JSON
    result = [{
        'id': card.id,
        'type': card.type.value,
        'title': card.title,
        'created_at': card.created_at.isoformat(),
        'updated_at': card.updated_at.isoformat() if card.updated_at else None,
        'tags': card.tags,
        **card.to_dict()  # Дополнительные поля
    } for card in cards]

    return jsonify({
        'success': True,
        'count': len(result),
        'cards': result
    })


@app.route('/api/cards/<card_id>', methods=['GET'])
def get_card(card_id):
    """
    Получить карточку по ID

    Example:
        GET /api/cards/550e8400-e29b-41d4-a716-446655440000
    """
    try:
        card = manager.read(card_id)
        return jsonify({
            'success': True,
            'card': {
                'id': card.id,
                'type': card.type.value,
                'title': card.title,
                'created_at': card.created_at.isoformat(),
                'updated_at': card.updated_at.isoformat() if card.updated_at else None,
                'tags': card.tags,
                **card.to_dict()
            }
        })
    except FileNotFoundError:
        return jsonify({
            'success': False,
            'error': 'Card not found'
        }), 404


@app.route('/api/cards/<card_id>/related', methods=['GET'])
def get_related_cards(card_id):
    """
    Получить связанные карточки

    Example:
        GET /api/cards/550e8400-e29b-41d4-a716-446655440000/related
    """
    try:
        related = manager.get_related(card_id)
        result = {}
        for rel_type, cards in related.items():
            result[rel_type] = [{
                'id': card.id,
                'type': card.type.value,
                'title': card.title
            } for card in cards]

        return jsonify({
            'success': True,
            'related': result
        })
    except FileNotFoundError:
        return jsonify({
            'success': False,
            'error': 'Card not found'
        }), 404


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """
    Получить статистику

    Example:
        GET /api/stats
    """
    stats = manager.get_stats()
    return jsonify({
        'success': True,
        'stats': stats
    })


# ============================================================================
# POST endpoints — Создание данных
# ============================================================================

@app.route('/api/cards', methods=['POST'])
def create_card():
    """
    Создать новую карточку

    Request body:
    {
        "type": "task",
        "title": "Купить молоко",
        "description": "2 литра обезжиренного",
        "priority": "high"
    }

    Example:
        POST /api/cards
        Content-Type: application/json
    """
    data = request.json

    # Валидация
    if not data or 'type' not in data or 'title' not in data:
        return jsonify({
            'success': False,
            'error': 'Missing required fields: type, title'
        }), 400

    # Создание карточки по типу
    card_type = data.pop('type')
    card_class_map = {
        'task': TaskCard,
        'medicine': MedicineCard,
        'contact': ContactCard,
    }

    card_class = card_class_map.get(card_type)
    if not card_class:
        return jsonify({
            'success': False,
            'error': f'Unknown card type: {card_type}'
        }), 400

    try:
        card = card_class(**data)
        created = manager.create(card)

        return jsonify({
            'success': True,
            'card': {
                'id': created.id,
                'type': created.type.value,
                'title': created.title,
                'created_at': created.created_at.isoformat()
            }
        }), 201
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/api/cards/<card_id>/links', methods=['POST'])
def create_link(card_id):
    """
    Создать связь между карточками

    Request body:
    {
        "target_id": "другая-карточка-id",
        "relation": "prescribed_by"
    }

    Example:
        POST /api/cards/550e8400-.../links
    """
    data = request.json
    target_id = data.get('target_id')
    relation = data.get('relation', 'related')

    if not target_id:
        return jsonify({
            'success': False,
            'error': 'Missing target_id'
        }), 400

    try:
        manager.link(card_id, target_id, relation)
        return jsonify({
            'success': True,
            'message': 'Link created'
        }), 201
    except FileNotFoundError:
        return jsonify({
            'success': False,
            'error': 'Card not found'
        }), 404


# ============================================================================
# PUT/PATCH endpoints — Обновление данных
# ============================================================================

@app.route('/api/cards/<card_id>', methods=['PUT', 'PATCH'])
def update_card(card_id):
    """
    Обновить карточку

    Request body:
    {
        "status": "completed"
    }

    Example:
        PATCH /api/cards/550e8400-.../
    """
    data = request.json

    try:
        card = manager.read(card_id)

        # Обновляем поля
        for key, value in data.items():
            if hasattr(card, key):
                setattr(card, key, value)

        updated = manager.update(card)

        return jsonify({
            'success': True,
            'card': {
                'id': updated.id,
                'title': updated.title,
                'updated_at': updated.updated_at.isoformat() if updated.updated_at else None
            }
        })
    except FileNotFoundError:
        return jsonify({
            'success': False,
            'error': 'Card not found'
        }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


# ============================================================================
# DELETE endpoints — Удаление данных
# ============================================================================

@app.route('/api/cards/<card_id>', methods=['DELETE'])
def delete_card(card_id):
    """
    Удалить карточку

    Example:
        DELETE /api/cards/550e8400-.../
    """
    try:
        manager.delete(card_id)
        return jsonify({
            'success': True,
            'message': 'Card deleted'
        })
    except FileNotFoundError:
        return jsonify({
            'success': False,
            'error': 'Card not found'
        }), 404


# ============================================================================
# Дополнительные endpoints
# ============================================================================

@app.route('/api/search', methods=['GET'])
def search_cards():
    """
    Поиск карточек по тексту

    Query parameters:
    - q: поисковый запрос

    Example:
        GET /api/search?q=молоко
    """
    query = request.args.get('q', '')

    if not query:
        return jsonify({
            'success': False,
            'error': 'Missing search query (q parameter)'
        }), 400

    cards = manager.search()
    # Простой текстовый поиск
    results = [card for card in cards
               if query.lower() in card.title.lower()]

    return jsonify({
        'success': True,
        'count': len(results),
        'results': [{
            'id': card.id,
            'type': card.type.value,
            'title': card.title
        } for card in results]
    })


@app.route('/api/health', methods=['GET'])
def health_check():
    """
    Health check endpoint

    Example:
        GET /api/health
    """
    return jsonify({
        'status': 'ok',
        'version': '1.0',
        'cards_dir': str(CARDS_DIR)
    })


# ============================================================================
# Запуск сервера
# ============================================================================

if __name__ == '__main__':
    print("=" * 60)
    print("Flask API для карточной системы")
    print("=" * 60)
    print(f"Карточки хранятся в: {CARDS_DIR}")
    print("API endpoints:")
    print("  GET    /api/cards              - Все карточки")
    print("  POST   /api/cards              - Создать карточку")
    print("  GET    /api/cards/<id>         - Карточка по ID")
    print("  PATCH  /api/cards/<id>         - Обновить карточку")
    print("  DELETE /api/cards/<id>         - Удалить карточку")
    print("  GET    /api/cards/<id>/related - Связанные карточки")
    print("  POST   /api/cards/<id>/links   - Создать связь")
    print("  GET    /api/search?q=text      - Поиск")
    print("  GET    /api/stats              - Статистика")
    print("  GET    /api/health             - Health check")
    print("=" * 60)

    app.run(debug=True, port=5000)
