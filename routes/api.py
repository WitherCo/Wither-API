from flask import request, jsonify, g
from flask_restful import Resource, reqparse
import datetime
import logging
from utils.auth import auth_required
from utils.rate_limit import rate_limit
from utils.logger import log_request
from models import db, User, ApiKey

logger = logging.getLogger(__name__)

class ApiKeyResource(Resource):
    """Resource for managing API keys"""
    
    @auth_required
    @rate_limit
    @log_request
    def get(self):
        """Get all API keys for the authenticated user"""
        api_keys = ApiKey.query.filter_by(user_id=g.user.id).all()
        return jsonify({
            'status': 'success',
            'data': [{
                'id': key.id,
                'name': key.name,
                'key': key.key,
                'created_at': key.created_at.isoformat(),
                'last_used_at': key.last_used_at.isoformat() if key.last_used_at else None,
                'is_active': key.is_active
            } for key in api_keys]
        })
    
    @auth_required
    @rate_limit
    @log_request
    def post(self):
        """Create a new API key for the authenticated user"""
        parser = reqparse.RequestParser()
        parser.add_argument('name', required=True, help='API key name is required')
        args = parser.parse_args()
        
        api_key = ApiKey(user_id=g.user.id, name=args['name'])
        
        db.session.add(api_key)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'API key created successfully',
            'data': {
                'id': api_key.id,
                'name': api_key.name,
                'key': api_key.key,
                'created_at': api_key.created_at.isoformat()
            }
        }), 201


class ApiKeyDetailResource(Resource):
    """Resource for managing a specific API key"""
    
    @auth_required
    @rate_limit
    @log_request
    def get(self, key_id):
        """Get details of a specific API key"""
        api_key = ApiKey.query.filter_by(id=key_id, user_id=g.user.id).first()
        
        if not api_key:
            return jsonify({
                'status': 'error',
                'message': 'API key not found'
            }), 404
        
        return jsonify({
            'status': 'success',
            'data': {
                'id': api_key.id,
                'name': api_key.name,
                'key': api_key.key,
                'created_at': api_key.created_at.isoformat(),
                'last_used_at': api_key.last_used_at.isoformat() if api_key.last_used_at else None,
                'is_active': api_key.is_active
            }
        })
    
    @auth_required
    @rate_limit
    @log_request
    def put(self, key_id):
        """Update a specific API key"""
        api_key = ApiKey.query.filter_by(id=key_id, user_id=g.user.id).first()
        
        if not api_key:
            return jsonify({
                'status': 'error',
                'message': 'API key not found'
            }), 404
        
        parser = reqparse.RequestParser()
        parser.add_argument('name', required=True, help='API key name is required')
        parser.add_argument('is_active', type=bool, required=True, help='Active status is required')
        args = parser.parse_args()
        
        api_key.name = args['name']
        api_key.is_active = args['is_active']
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'API key updated successfully',
            'data': {
                'id': api_key.id,
                'name': api_key.name,
                'key': api_key.key,
                'is_active': api_key.is_active
            }
        })
    
    @auth_required
    @rate_limit
    @log_request
    def delete(self, key_id):
        """Delete a specific API key"""
        api_key = ApiKey.query.filter_by(id=key_id, user_id=g.user.id).first()
        
        if not api_key:
            return jsonify({
                'status': 'error',
                'message': 'API key not found'
            }), 404
        
        db.session.delete(api_key)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'API key deleted successfully'
        })


class HealthCheckResource(Resource):
    """Resource for checking API health"""
    
    def get(self):
        """Get API health status"""
        return jsonify({
            'status': 'success',
            'message': 'API is running',
            'timestamp': datetime.datetime.now().isoformat()
        })


def register_api_routes(api):
    """Register all API routes"""
    api.add_resource(HealthCheckResource, '/api/health')
    api.add_resource(ApiKeyResource, '/api/keys')
    api.add_resource(ApiKeyDetailResource, '/api/keys/<int:key_id>')
