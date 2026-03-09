import logging
import sys
from logging.handlers import RotatingFileHandler
import os
from datetime import datetime


class CfcSocFormatter(logging.Formatter):
    """
    Formatter that outputs logs in CFC SOC format per CFC SOC Logging Guidelines 4.0.
    Format: timestamp [AUDIT] [type] platform app_name user_id ip_address level message
    Separators: Single space (per LOG-8 requirement)
    """

    def __init__(self, log_type="[Application]", platform="CFC", app_name="SendCloudToAWSS3"):
        super().__init__()
        self.log_type = log_type
        self.platform = platform
        self.app_name = app_name

    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record in CFC SOC space-separated format.
        Timestamp Platform App LogType Level Message
        """
        # Get timestamp in ISO format with milliseconds
        timestamp = datetime.fromtimestamp(record.created).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

        # Create space-separated log line (per LOG-8: single space separator)
        log_entry = " ".join([
            timestamp,
            self.platform,
            self.app_name,
            self.log_type,
            record.levelname,
            record.getMessage()
        ])

        return log_entry


def setup_logger(name, log_file='logs/app.log', log_type="[Application]",
                 platform="CFC", app_name="SendCloudToAWSS3", use_soc_format=True):
    """
    Setup application logger with file rotation.
    Optionally uses CFC SOC format per CFC SOC Logging Guidelines 4.0.

    Args:
        name: Logger name (typically __name__)
        log_file: Path to log file
        log_type: Log type tag (e.g., [Application], [Webhook], [API])
        platform: Platform identifier (default: CFC)
        app_name: Application name
        use_soc_format: Use CFC SOC format if True, standard format if False

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
    logger.propagate = False  # Prevent propagation to parent loggers

    # Create rotating file handler (10MB per file, 10 backups)
    handler = RotatingFileHandler(log_file, maxBytes=10485760, backupCount=10)

    # Create formatter based on use_soc_format flag
    if use_soc_format:
        formatter = CfcSocFormatter(log_type=log_type, platform=platform, app_name=app_name)
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

    handler.setFormatter(formatter)

    # Add handler to logger
    logger.addHandler(handler)
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    return logger
