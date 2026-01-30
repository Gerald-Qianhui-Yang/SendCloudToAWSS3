#!/usr/bin/env python
"""Application entry point"""
import os
import sys
from app import create_app
from config.logger import setup_logger

logger = setup_logger(__name__)

def main():
    """Start the Flask application"""
    try:
        # Get environment configuration
        env = os.getenv('FLASK_ENV', 'development')
        host = os.getenv('FLASK_HOST', '0.0.0.0')
        port = int(os.getenv('FLASK_PORT', 5000))
        debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'

        # Create Flask app
        app = create_app(env)

        logger.info(f"Starting Flask app - Environment: {env}, Host: {host}, Port: {port}, Debug: {debug}")

        # Run application
        app.run(host=host, port=port, debug=debug)

    except KeyError as e:
        logger.error(f"Missing environment variable: {str(e)}")
        sys.exit(1)
    except ValueError as e:
        logger.error(f"Invalid configuration value: {str(e)}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Failed to start application: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == '__main__':
    main()
