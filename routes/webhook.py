import json
import hmac
import hashlib
import requests
import logging
from flask import Blueprint, request, jsonify, g, current_app
from werkzeug.exceptions import BadRequest
from models import db, WebhookEndpoint
from utils.auth import auth_required
from utils.rate_limit import rate_limit
from utils.logger import log_request

logger = logging.getLogger(__name__)
webhook_bp = Blueprint('webhook', __name__, url_prefix='/api/webhooks')

@webhook_bp.route('/', methods=['GET'])
@auth_required
@rate_limit
@log_request
def get_webhooks():
    """Get all webhook endpoints for the authenticated user"""
    webhooks = WebhookEndpoint.query.filter_by(user_id=g.user.id).all()
    
    return jsonify({
        'status': 'success',
        'data': [{
            'id': webhook.id,
            'name': webhook.name,
            'url': webhook.url,
            'events': webhook.events.split(','),
            'created_at': webhook.created_at.isoformat(),
            'is_active': webhook.is_active
        } for webhook in webhooks]
    })


@webhook_bp.route('/', methods=['POST'])
@auth_required
@rate_limit
@log_request
def create_webhook():
    """Create a new webhook endpoint"""
    data = request.get_json()
    
    if not data:
        raise BadRequest('Invalid JSON payload')
    
    # Validate required fields
    required_fields = ['name', 'url', 'events']
    for field in required_fields:
        if field not in data:
            raise BadRequest(f'Missing required field: {field}')
    
    # Create webhook endpoint
    webhook = WebhookEndpoint(
        name=data['name'],
        url=data['url'],
        user_id=g.user.id,
        events=','.join(data['events']),
        secret=data.get('secret')
    )
    
    db.session.add(webhook)
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': 'Webhook endpoint created successfully',
        'data': {
            'id': webhook.id,
            'name': webhook.name,
            'url': webhook.url,
            'events': webhook.events.split(','),
            'created_at': webhook.created_at.isoformat()
        }
    }), 201


@webhook_bp.route('/<int:webhook_id>', methods=['GET'])
@auth_required
@rate_limit
@log_request
def get_webhook(webhook_id):
    """Get details of a specific webhook endpoint"""
    webhook = WebhookEndpoint.query.filter_by(id=webhook_id, user_id=g.user.id).first()
    
    if not webhook:
        return jsonify({
            'status': 'error',
            'message': 'Webhook endpoint not found'
        }), 404
    
    return jsonify({
        'status': 'success',
        'data': {
            'id': webhook.id,
            'name': webhook.name,
            'url': webhook.url,
            'events': webhook.events.split(','),
            'created_at': webhook.created_at.isoformat(),
            'is_active': webhook.is_active
        }
    })


@webhook_bp.route('/<int:webhook_id>', methods=['PUT'])
@auth_required
@rate_limit
@log_request
def update_webhook(webhook_id):
    """Update a specific webhook endpoint"""
    webhook = WebhookEndpoint.query.filter_by(id=webhook_id, user_id=g.user.id).first()
    
    if not webhook:
        return jsonify({
            'status': 'error',
            'message': 'Webhook endpoint not found'
        }), 404
    
    data = request.get_json()
    
    if not data:
        raise BadRequest('Invalid JSON payload')
    
    # Update webhook fields
    if 'name' in data:
        webhook.name = data['name']
    if 'url' in data:
        webhook.url = data['url']
    if 'events' in data:
        webhook.events = ','.join(data['events'])
    if 'secret' in data:
        webhook.secret = data['secret']
    if 'is_active' in data:
        webhook.is_active = data['is_active']
    
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': 'Webhook endpoint updated successfully',
        'data': {
            'id': webhook.id,
            'name': webhook.name,
            'url': webhook.url,
            'events': webhook.events.split(','),
            'is_active': webhook.is_active
        }
    })


@webhook_bp.route('/<int:webhook_id>', methods=['DELETE'])
@auth_required
@rate_limit
@log_request
def delete_webhook(webhook_id):
    """Delete a specific webhook endpoint"""
    webhook = WebhookEndpoint.query.filter_by(id=webhook_id, user_id=g.user.id).first()
    
    if not webhook:
        return jsonify({
            'status': 'error',
            'message': 'Webhook endpoint not found'
        }), 404
    
    db.session.delete(webhook)
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': 'Webhook endpoint deleted successfully'
    })


@webhook_bp.route('/receive/<string:event_type>', methods=['POST'])
@rate_limit
@log_request
def receive_webhook(event_type):
    """Receive a webhook and dispatch it to registered endpoints"""
    data = request.get_json()
    
    if not data:
        raise BadRequest('Invalid JSON payload')
    
    # Find all active webhook endpoints for this event
    webhooks = WebhookEndpoint.query.filter(
        WebhookEndpoint.is_active == True,
        WebhookEndpoint.events.like(f'%{event_type}%')
    ).all()
    
    if not webhooks:
        return jsonify({
            'status': 'success',
            'message': 'No webhook endpoints registered for this event',
            'event': event_type
        })
    
    # Dispatch webhook to all registered endpoints
    results = []
    for webhook in webhooks:
        try:
            # Prepare payload with event type
            payload = {
                'event': event_type,
                'data': data,
                'timestamp': request.headers.get('X-Request-Timestamp', '')
            }
            
            headers = {'Content-Type': 'application/json'}
            
            # Add signature if secret is set
            if webhook.secret:
                payload_bytes = json.dumps(payload).encode('utf-8')
                signature = hmac.new(
                    webhook.secret.encode('utf-8'),
                    payload_bytes,
                    hashlib.sha256
                ).hexdigest()
                headers['X-Webhook-Signature'] = signature
            
            # Send webhook
            response = requests.post(
                webhook.url,
                json=payload,
                headers=headers,
                timeout=current_app.config.get('WEBHOOK_TIMEOUT', 5)
            )
            
            results.append({
                'webhook_id': webhook.id,
                'status': 'success' if response.status_code < 400 else 'error',
                'status_code': response.status_code
            })
            
        except requests.RequestException as e:
            logger.error(f"Error dispatching webhook to {webhook.url}: {str(e)}")
            results.append({
                'webhook_id': webhook.id,
                'status': 'error',
                'error': str(e)
            })
    
    return jsonify({
        'status': 'success',
        'message': 'Webhook received and dispatched',
        'event': event_type,
        'results': results
    })


def register_webhook_routes(app):
    """Register webhook routes with the app"""
    app.register_blueprint(webhook_bp)
