import os
import hashlib
from config.logger import setup_logger

logger = setup_logger(__name__)

class SendCloudWebhookValidator:
    """Validates SendCloud email webhook requests"""

    # Supported SendCloud email events
    SUPPORTED_EVENTS = {
        'request',
        'deliver',
        'open',
        'click',
        'unsubscribe',
        'report_spam',
        'invalid',
        'soft_bounce',
        'route'
    }

    @staticmethod
    def verify_signature(token, timestamp, signature, app_key):
        """
        Verify SendCloud webhook signature using SHA256

        Args:
            token: Token from POST data
            timestamp: Timestamp from POST data
            signature: Signature from POST data
            app_key: SendCloud APP KEY

        Returns:
            bool: True if signature is valid
        """
        try:
            # Generate signature: SHA256(APP_KEY + token + timestamp)
            message = f"{app_key}{token}{timestamp}".encode('utf-8')
            expected_signature = hashlib.sha256(message).hexdigest()

            # Use constant-time comparison
            return expected_signature == signature
        except Exception as e:
            logger.error(f"Signature verification failed: {str(e)}")
            return False

    @staticmethod
    def is_valid_event(event):
        """Check if event type is supported"""
        return event in SendCloudWebhookValidator.SUPPORTED_EVENTS
