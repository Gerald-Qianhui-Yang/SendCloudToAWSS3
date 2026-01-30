from flask import Flask
from flask_cors import CORS
from config.config import config
from app.webhook_routes import webhook_bp
from config.logger import setup_logger

logger = setup_logger(__name__)

def create_app(config_name='development'):
    """Application factory for creating Flask app instances"""
    app = Flask(__name__)

    # Load environment-specific configuration
    app.config.from_object(config[config_name])

    # Enable CORS for cross-origin requests
    CORS(app)

    # Register webhook blueprint
    app.register_blueprint(webhook_bp)

    # Health check endpoint
    @app.route('/health', methods=['GET'])
    def health_check():
        """Health check endpoint for monitoring"""
        return '', 200

    # 404 handler - resource not found
    @app.errorhandler(404)
    def not_found(error):
        logger.warning(f"404 Not Found: {error}")
        return '', 404

    # 500 handler - internal server error
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"500 Internal Server Error: {error}")
        return '', 500

    logger.info(f"Flask app created with config: {config_name}")

    return app
