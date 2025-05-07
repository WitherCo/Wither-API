import os
import logging
from flask import Flask
from flask_restful import Api
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev_secret_key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Load configuration
app.config.from_object('config.Config')

# Enable CORS
CORS(app)

# Initialize Flask-RESTful API
api = Api(app)

# Import and register routes
from routes.api import register_api_routes
from routes.webhook import register_webhook_routes
from routes.email import register_email_routes
from routes.bot import register_bot_routes
from routes.main import register_main_routes
from utils.error_handler import register_error_handlers

# Register routes
register_api_routes(api)
register_webhook_routes(app)
register_email_routes(app)
register_bot_routes(app)
register_main_routes(app)
register_error_handlers(app)

# Import and register models
from models import User, ApiKey

logger.info("API Gateway initialized successfully")
