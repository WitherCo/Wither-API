import logging
from functools import wraps
from flask import request, jsonify, g
from models import User, ApiKey

logger = logging.getLogger(__name__)

def get_api_key_from_request():
    """Extract API key from the request"""
    # Try to get from header
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        return auth_header.split('Bearer ')[1]
    
    # Try to get from query parameter
    api_key = request.args.get('api_key')
    if api_key:
        return api_key
    
    return None

def validate_api_key(api_key):
    """Validate the API key and return the associated user if valid"""
    if not api_key:
        return None
    
    # Find the API key in the database
    api_key_obj = ApiKey.query.filter_by(key=api_key, is_active=True).first()
    
    if not api_key_obj:
        return None
    
    # Get the associated user
    user = User.query.filter_by(id=api_key_obj.user_id, is_active=True).first()
    
    if not user:
        return None
    
    # Update last used timestamp
    api_key_obj.update_last_used()
    
    return user

def auth_required(f):
    """Decorator to require API key authentication for a route"""
    @wraps(f)
    def decorated(*args, **kwargs):
        api_key = get_api_key_from_request()
        user = validate_api_key(api_key)
        
        if not user:
            return jsonify({
                'status': 'error',
                'message': 'Invalid or missing API key'
            }), 401
        
        # Store user in Flask's g object for access in the route function
        g.user = user
        
        return f(*args, **kwargs)
    
    return decorated
