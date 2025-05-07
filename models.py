import uuid
import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    """User model for API authentication and management"""
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    api_keys = db.relationship('ApiKey', backref='user', lazy='dynamic')
    
    def set_password(self, password):
        """Set the password hash for the user"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if the provided password matches the hash"""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'


class ApiKey(db.Model):
    """API Key model for authenticating API requests"""
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(64), unique=True, nullable=False, index=True)
    name = db.Column(db.String(64), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    last_used_at = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    
    def __init__(self, user_id, name):
        self.user_id = user_id
        self.name = name
        self.key = self.generate_key()
    
    @staticmethod
    def generate_key():
        """Generate a unique API key"""
        return str(uuid.uuid4())
    
    def update_last_used(self):
        """Update the last used timestamp"""
        self.last_used_at = datetime.datetime.utcnow()
        db.session.commit()
    
    def __repr__(self):
        return f'<ApiKey {self.name}>'


class WebhookEndpoint(db.Model):
    """Webhook endpoint configuration for receiving and dispatching webhooks"""
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    url = db.Column(db.String(256), nullable=False)
    secret = db.Column(db.String(64), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    events = db.Column(db.String(256), nullable=False)  # Comma-separated list of events
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f'<WebhookEndpoint {self.name}>'


class EmailTemplate(db.Model):
    """Email template model for storing reusable email templates"""
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    subject = db.Column(db.String(128), nullable=False)
    body = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    
    def __repr__(self):
        return f'<EmailTemplate {self.name}>'


class RequestLog(db.Model):
    """Request log model for tracking API requests"""
    
    id = db.Column(db.Integer, primary_key=True)
    method = db.Column(db.String(10), nullable=False)
    endpoint = db.Column(db.String(256), nullable=False)
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.String(256), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    status_code = db.Column(db.Integer, nullable=False)
    response_time = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    
    def __repr__(self):
        return f'<RequestLog {self.method} {self.endpoint} {self.status_code}>'
