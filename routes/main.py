import logging
from flask import Blueprint, render_template

logger = logging.getLogger(__name__)
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Render the home page"""
    return render_template('index.html')

@main_bp.route('/documentation')
def documentation():
    """Render the documentation page"""
    return render_template('documentation.html')

def register_main_routes(app):
    """Register main routes with the app"""
    app.register_blueprint(main_bp)