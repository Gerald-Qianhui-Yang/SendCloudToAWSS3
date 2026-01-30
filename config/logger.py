import logging
from logging.handlers import RotatingFileHandler
import os

def setup_logger(name, log_file='logs/app.log'):
    """
    Setup application logger with file rotation

    Args:
        name: Logger name (typically __name__)
        log_file: Path to log file

    Returns:
        logging.Logger: Configured logger instance
    """
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)

    # Create logger
    logger = logging.getLogger(name)

    # Only add handlers if not already present (prevent duplicates)
    if logger.hasHandlers():
        return logger

    logger.setLevel(logging.INFO)

    # Create rotating file handler (10MB per file, 10 backups)
    handler = RotatingFileHandler(log_file, maxBytes=10485760, backupCount=10)

    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)

    # Add handler to logger
    logger.addHandler(handler)

    return logger
