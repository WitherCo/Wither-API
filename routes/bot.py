import logging
import requests
from flask import Blueprint, request, jsonify, g, current_app
from werkzeug.exceptions import BadRequest
from models import db
from utils.auth import auth_required
from utils.rate_limit import rate_limit
from utils.logger import log_request

logger = logging.getLogger(__name__)
bot_bp = Blueprint('bot', __name__, url_prefix='/api/bot')

@bot_bp.route('/send-message', methods=['POST'])
@auth_required
@rate_limit
@log_request
def send_message():
    """Send a message using the configured bot"""
    data = request.get_json()
    
    if not data:
        raise BadRequest('Invalid JSON payload')
    
    # Validate required fields
    required_fields = ['channel', 'message']
    for field in required_fields:
        if field not in data:
            raise BadRequest(f'Missing required field: {field}')
    
    # Extract message details
    channel = data['channel']
    message = data['message']
    attachments = data.get('attachments', [])
    
    # Get bot configuration
    bot_token = current_app.config.get('BOT_TOKEN')
    api_base_url = current_app.config.get('BOT_API_BASE_URL')
    
    if not bot_token or not api_base_url:
        return jsonify({
            'status': 'error',
            'message': 'Bot is not configured'
        }), 500
    
    # Prepare payload
    payload = {
        'token': bot_token,
        'channel': channel,
        'text': message
    }
    
    if attachments:
        payload['attachments'] = attachments
    
    try:
        # Send message to bot API
        response = requests.post(
            f"{api_base_url}/chat.postMessage",
            json=payload,
            headers={'Content-Type': 'application/json'}
        )
        
        response_data = response.json()
        
        if response.status_code == 200 and response_data.get('ok'):
            return jsonify({
                'status': 'success',
                'message': 'Message sent successfully',
                'data': {
                    'channel': channel,
                    'ts': response_data.get('ts')
                }
            })
        else:
            error_msg = response_data.get('error', 'Unknown error')
            logger.error(f"Bot API error: {error_msg}")
            return jsonify({
                'status': 'error',
                'message': f'Failed to send message: {error_msg}'
            }), 500
            
    except requests.RequestException as e:
        logger.error(f"Error sending bot message: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Failed to send message: {str(e)}'
        }), 500


@bot_bp.route('/channels', methods=['GET'])
@auth_required
@rate_limit
@log_request
def get_channels():
    """Get list of available channels for the configured bot"""
    # Get bot configuration
    bot_token = current_app.config.get('BOT_TOKEN')
    api_base_url = current_app.config.get('BOT_API_BASE_URL')
    
    if not bot_token or not api_base_url:
        return jsonify({
            'status': 'error',
            'message': 'Bot is not configured'
        }), 500
    
    try:
        # Get channels from bot API
        response = requests.get(
            f"{api_base_url}/conversations.list",
            params={'token': bot_token, 'types': 'public_channel,private_channel'}
        )
        
        response_data = response.json()
        
        if response.status_code == 200 and response_data.get('ok'):
            channels = response_data.get('channels', [])
            return jsonify({
                'status': 'success',
                'data': [{
                    'id': channel.get('id'),
                    'name': channel.get('name'),
                    'is_private': channel.get('is_private', False)
                } for channel in channels]
            })
        else:
            error_msg = response_data.get('error', 'Unknown error')
            logger.error(f"Bot API error: {error_msg}")
            return jsonify({
                'status': 'error',
                'message': f'Failed to get channels: {error_msg}'
            }), 500
            
    except requests.RequestException as e:
        logger.error(f"Error getting bot channels: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Failed to get channels: {str(e)}'
        }), 500


@bot_bp.route('/webhook', methods=['POST'])
@log_request
def receive_webhook():
    """Receive webhook events from the bot platform"""
    data = request.get_json()
    
    if not data:
        raise BadRequest('Invalid JSON payload')
    
    # Verify request authenticity if needed
    # This depends on the bot platform, but typically involves checking a signature
    
    # Process different types of events
    event_type = data.get('type')
    
    if event_type == 'url_verification':
        # Handle URL verification challenge
        return jsonify({'challenge': data.get('challenge')})
    
    elif event_type == 'event_callback':
        # Handle event callback
        event = data.get('event', {})
        event_type = event.get('type')
        
        # Log the event
        logger.info(f"Received bot event: {event_type}")
        
        # Process event (implement your logic here)
        # For example, if it's a message event:
        if event_type == 'message':
            channel = event.get('channel')
            text = event.get('text')
            user = event.get('user')
            
            logger.info(f"Received message from {user} in {channel}: {text}")
            
            # Process the message (implement your logic here)
            
        return jsonify({
            'status': 'success',
            'message': 'Event received'
        })
    
    return jsonify({
        'status': 'success',
        'message': 'Webhook received'
    })


def register_bot_routes(app):
    """Register bot routes with the app"""
    app.register_blueprint(bot_bp)
