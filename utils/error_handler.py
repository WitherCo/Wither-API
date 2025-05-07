import logging
import traceback
from flask import jsonify, request

logger = logging.getLogger(__name__)

def handle_400_error(e):
    """Handle 400 Bad Request errors"""
    logger.warning(f"400 Bad Request: {str(e)}")
    return jsonify({
        'status': 'error',
        'message': str(e),
        'error_code': 'bad_request'
    }), 400

def handle_404_error(e):
    """Handle 404 Not Found errors"""
    logger.warning(f"404 Not Found: {request.path}")
    return jsonify({
        'status': 'error',
        'message': f"Resource not found: {request.path}",
        'error_code': 'not_found'
    }), 404

def handle_405_error(e):
    """Handle 405 Method Not Allowed errors"""
    logger.warning(f"405 Method Not Allowed: {request.method} {request.path}")
    return jsonify({
        'status': 'error',
        'message': f"Method {request.method} not allowed for {request.path}",
        'error_code': 'method_not_allowed'
    }), 405

def handle_429_error(e):
    """Handle 429 Too Many Requests errors"""
    logger.warning(f"429 Too Many Requests: {request.remote_addr}")
    return jsonify({
        'status': 'error',
        'message': "Rate limit exceeded. Please try again later.",
        'error_code': 'rate_limit_exceeded'
    }), 429

def handle_500_error(e):
    """Handle 500 Internal Server Error"""
    logger.error(f"500 Internal Server Error: {str(e)}\n{traceback.format_exc()}")
    return jsonify({
        'status': 'error',
        'message': "An internal server error occurred.",
        'error_code': 'internal_server_error'
    }), 500

def register_error_handlers(app):
    """Register error handlers with the Flask app"""
    app.register_error_handler(400, handle_400_error)
    app.register_error_handler(404, handle_404_error)
    app.register_error_handler(405, handle_405_error)
    app.register_error_handler(429, handle_429_error)
    app.register_error_handler(500, handle_500_error)
    
    # Register custom exception handlers
    from werkzeug.exceptions import BadRequest, NotFound, MethodNotAllowed, TooManyRequests
    
    app.register_error_handler(BadRequest, handle_400_error)
    app.register_error_handler(NotFound, handle_404_error)
    app.register_error_handler(MethodNotAllowed, handle_405_error)
    app.register_error_handler(TooManyRequests, handle_429_error)
    app.register_error_handler(Exception, handle_500_error)
