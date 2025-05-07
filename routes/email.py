import logging
from flask import Blueprint, request, jsonify, g
from werkzeug.exceptions import BadRequest
from models import db, EmailTemplate
from utils.auth import auth_required
from utils.rate_limit import rate_limit
from utils.logger import log_request
from utils.email_service import send_email

logger = logging.getLogger(__name__)
email_bp = Blueprint('email', __name__, url_prefix='/api/email')

@email_bp.route('/send', methods=['POST'])
@auth_required
@rate_limit
@log_request
def send_email_api():
    """Send an email"""
    data = request.get_json()
    
    if not data:
        raise BadRequest('Invalid JSON payload')
    
    # Validate required fields
    required_fields = ['to', 'subject', 'body']
    for field in required_fields:
        if field not in data:
            raise BadRequest(f'Missing required field: {field}')
    
    # Extract email details
    to = data['to']
    subject = data['subject']
    body = data['body']
    html = data.get('html')
    cc = data.get('cc', [])
    bcc = data.get('bcc', [])
    reply_to = data.get('reply_to')
    
    # Send email
    result = send_email(to, subject, body, html, cc, bcc, reply_to)
    
    if result['status'] == 'success':
        return jsonify({
            'status': 'success',
            'message': 'Email sent successfully'
        })
    else:
        return jsonify({
            'status': 'error',
            'message': 'Failed to send email',
            'error': result['error']
        }), 500


@email_bp.route('/templates', methods=['GET'])
@auth_required
@rate_limit
@log_request
def get_templates():
    """Get all email templates for the authenticated user"""
    templates = EmailTemplate.query.filter_by(user_id=g.user.id).all()
    
    return jsonify({
        'status': 'success',
        'data': [{
            'id': template.id,
            'name': template.name,
            'subject': template.subject,
            'created_at': template.created_at.isoformat()
        } for template in templates]
    })


@email_bp.route('/templates', methods=['POST'])
@auth_required
@rate_limit
@log_request
def create_template():
    """Create a new email template"""
    data = request.get_json()
    
    if not data:
        raise BadRequest('Invalid JSON payload')
    
    # Validate required fields
    required_fields = ['name', 'subject', 'body']
    for field in required_fields:
        if field not in data:
            raise BadRequest(f'Missing required field: {field}')
    
    # Create template
    template = EmailTemplate(
        name=data['name'],
        subject=data['subject'],
        body=data['body'],
        user_id=g.user.id
    )
    
    db.session.add(template)
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': 'Email template created successfully',
        'data': {
            'id': template.id,
            'name': template.name,
            'subject': template.subject,
            'created_at': template.created_at.isoformat()
        }
    }), 201


@email_bp.route('/templates/<int:template_id>', methods=['GET'])
@auth_required
@rate_limit
@log_request
def get_template(template_id):
    """Get details of a specific email template"""
    template = EmailTemplate.query.filter_by(id=template_id, user_id=g.user.id).first()
    
    if not template:
        return jsonify({
            'status': 'error',
            'message': 'Email template not found'
        }), 404
    
    return jsonify({
        'status': 'success',
        'data': {
            'id': template.id,
            'name': template.name,
            'subject': template.subject,
            'body': template.body,
            'created_at': template.created_at.isoformat()
        }
    })


@email_bp.route('/templates/<int:template_id>', methods=['PUT'])
@auth_required
@rate_limit
@log_request
def update_template(template_id):
    """Update a specific email template"""
    template = EmailTemplate.query.filter_by(id=template_id, user_id=g.user.id).first()
    
    if not template:
        return jsonify({
            'status': 'error',
            'message': 'Email template not found'
        }), 404
    
    data = request.get_json()
    
    if not data:
        raise BadRequest('Invalid JSON payload')
    
    # Update template fields
    if 'name' in data:
        template.name = data['name']
    if 'subject' in data:
        template.subject = data['subject']
    if 'body' in data:
        template.body = data['body']
    
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': 'Email template updated successfully',
        'data': {
            'id': template.id,
            'name': template.name,
            'subject': template.subject
        }
    })


@email_bp.route('/templates/<int:template_id>', methods=['DELETE'])
@auth_required
@rate_limit
@log_request
def delete_template(template_id):
    """Delete a specific email template"""
    template = EmailTemplate.query.filter_by(id=template_id, user_id=g.user.id).first()
    
    if not template:
        return jsonify({
            'status': 'error',
            'message': 'Email template not found'
        }), 404
    
    db.session.delete(template)
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': 'Email template deleted successfully'
    })


@email_bp.route('/send-template/<int:template_id>', methods=['POST'])
@auth_required
@rate_limit
@log_request
def send_template(template_id):
    """Send an email using a template"""
    template = EmailTemplate.query.filter_by(id=template_id, user_id=g.user.id).first()
    
    if not template:
        return jsonify({
            'status': 'error',
            'message': 'Email template not found'
        }), 404
    
    data = request.get_json()
    
    if not data:
        raise BadRequest('Invalid JSON payload')
    
    # Validate required fields
    if 'to' not in data:
        raise BadRequest('Missing required field: to')
    
    # Extract email details
    to = data['to']
    cc = data.get('cc', [])
    bcc = data.get('bcc', [])
    reply_to = data.get('reply_to')
    
    # Process template variables
    subject = template.subject
    body = template.body
    
    # Replace variables in subject and body
    variables = data.get('variables', {})
    for key, value in variables.items():
        placeholder = f'{{{{{key}}}}}'
        subject = subject.replace(placeholder, str(value))
        body = body.replace(placeholder, str(value))
    
    # Send email
    result = send_email(to, subject, body, body, cc, bcc, reply_to)
    
    if result['status'] == 'success':
        return jsonify({
            'status': 'success',
            'message': 'Email sent successfully'
        })
    else:
        return jsonify({
            'status': 'error',
            'message': 'Failed to send email',
            'error': result['error']
        }), 500


def register_email_routes(app):
    """Register email routes with the app"""
    app.register_blueprint(email_bp)
