#!/usr/bin/env python
"""Application entry point"""
import os
import sys
import logging
from app import create_app
from config.logger import setup_logger, CfcSocFormatter

logger = setup_logger(__name__, log_type="[Application]", use_soc_format=True)

def main():
    """Start the Flask application"""
    try:
        # Get environment configuration
        env = os.getenv('FLASK_ENV', 'production')
        host = os.getenv('FLASK_HOST', '0.0.0.0')
        port = int(os.getenv('FLASK_PORT', 5000))
        debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'

        # Create Flask app
        app = create_app(env)

        # Configure Flask's logger to use CFC SOC format
        # Disable Flask's default logging
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.WARNING)

        # Also configure Flask app logger
        app.logger.setLevel(logging.INFO)

        # Remove default handlers and add our CFC SOC formatter
        for handler in log.handlers[:]:
            log.removeHandler(handler)

        flask_handler = logging.StreamHandler(sys.stdout)
        flask_handler.setFormatter(CfcSocFormatter(log_type="[HTTP]", platform="CFC", app_name="SendCloudToAWSS3"))
        log.addHandler(flask_handler)

        logger.info(f"Starting Flask app - Environment: {env}, Host: {host}, Port: {port}, Debug: {debug}")

        # Run application (use_reloader=False to avoid duplicate logging on reload)
        app.run(host=host, port=port, debug=debug, use_reloader=False)

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
