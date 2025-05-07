import time
from functools import wraps
from flask import request, jsonify, g
import logging

logger = logging.getLogger(__name__)

# Simple in-memory rate limiting storage
rate_limit_store = {}

def get_rate_limit_key(request):
    """Get a unique key for rate limiting based on API key or IP address"""
    # If authenticated, use API key
    if hasattr(g, 'user'):
        return f"user:{g.user.id}"
    
    # Otherwise, use IP address
    return f"ip:{request.remote_addr}"

def rate_limit(f):
    """Decorator to apply rate limiting to a route"""
    @wraps(f)
    def decorated(*args, **kwargs):
        key = get_rate_limit_key(request)
        
        # Get current time
        now = time.time()
        
        # Clean up old requests
        clean_rate_limit_store(now)
        
        # Get rate limit settings
        # Different limits for authenticated vs unauthenticated requests
        if hasattr(g, 'user'):
            # Authenticated users get higher limits
            max_requests = 100
            window_size = 60  # 1 minute
        else:
            # Unauthenticated users get lower limits
            max_requests = 20
            window_size = 60  # 1 minute
        
        # Initialize or get the requests for this key
        if key not in rate_limit_store:
            rate_limit_store[key] = []
        
        # Get requests in the current time window
        requests_in_window = [req_time for req_time in rate_limit_store[key] if req_time > now - window_size]
        
        # Check if rate limit is exceeded
        if len(requests_in_window) >= max_requests:
            # Calculate time until reset
            reset_time = min(rate_limit_store[key]) + window_size - now
            
            # Set rate limit headers
            headers = {
                'X-RateLimit-Limit': str(max_requests),
                'X-RateLimit-Remaining': '0',
                'X-RateLimit-Reset': str(int(reset_time)),
                'Retry-After': str(int(reset_time))
            }
            
            logger.warning(f"Rate limit exceeded for {key}")
            
            return jsonify({
                'status': 'error',
                'message': 'Rate limit exceeded. Please try again later.'
            }), 429, headers
        
        # Add current request to the store
        rate_limit_store[key].append(now)
        
        # Set rate limit headers
        remaining = max_requests - len(requests_in_window) - 1
        headers = {
            'X-RateLimit-Limit': str(max_requests),
            'X-RateLimit-Remaining': str(remaining),
            'X-RateLimit-Reset': str(int(now + window_size))
        }
        
        # Call the original function
        response = f(*args, **kwargs)
        
        # Add headers to the response
        if isinstance(response, tuple):
            # Response with status code (and possibly headers)
            if len(response) == 3:
                # Response, status code, headers
                resp, status, resp_headers = response
                resp_headers.update(headers)
                return resp, status, resp_headers
            else:
                # Response, status code
                resp, status = response
                return resp, status, headers
        else:
            # Only response object
            return response, 200, headers
    
    return decorated

def clean_rate_limit_store(now):
    """Clean up old requests from the rate limit store"""
    # Maximum age to keep in store (2 hours)
    max_age = 7200
    
    for key in list(rate_limit_store.keys()):
        # Filter out old requests
        rate_limit_store[key] = [req_time for req_time in rate_limit_store[key] if req_time > now - max_age]
        
        # Remove empty keys
        if not rate_limit_store[key]:
            del rate_limit_store[key]
