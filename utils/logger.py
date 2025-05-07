import time
import logging
from functools import wraps
from flask import request, g
from models import db, RequestLog

logger = logging.getLogger(__name__)

def log_request(f):
    """Decorator to log API requests"""
    @wraps(f)
    def decorated(*args, **kwargs):
        # Get start time
        start_time = time.time()
        
        # Execute the request
        response = f(*args, **kwargs)
        
        # Calculate response time
        response_time = time.time() - start_time
        
        try:
            # Extract status code
            if isinstance(response, tuple):
                status_code = response[1] if len(response) >= 2 else 200
            else:
                status_code = 200
            
            # Create log entry
            log_entry = RequestLog(
                method=request.method,
                endpoint=request.path,
                ip_address=request.remote_addr,
                user_agent=request.user_agent.string,
                user_id=g.user.id if hasattr(g, 'user') else None,
                status_code=status_code,
                response_time=response_time
            )
            
            db.session.add(log_entry)
            db.session.commit()
            
        except Exception as e:
            logger.error(f"Failed to log request: {str(e)}")
            # Don't let logging failures affect the response
            db.session.rollback()
        
        return response
    
    return decorated
