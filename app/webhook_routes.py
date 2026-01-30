from flask import Blueprint, request
from app.webhook_validator import SendCloudWebhookValidator
from app.s3_manager import S3Manager
from config.logger import setup_logger
import os

webhook_bp = Blueprint('webhook', __name__, url_prefix='/webhook')
logger = setup_logger(__name__)
s3_manager = S3Manager()

@webhook_bp.route('/sendcloud/email', methods=['GET', 'POST'])
def handle_email_webhook():
    """
    Handle SendCloud email webhook events
    Supported events: request, deliver, open, click, unsubscribe, report_spam, invalid, soft_bounce, route

    Requirements:
    - Data format: application/x-www-form-urlencoded
    - Must return HTTP 200 within 3 seconds
    - Signature verification uses: SHA256(APP_KEY + token + timestamp)
    """
    try:
        # Handle GET requests for URL verification
        if request.method == 'GET':
            logger.info("Received webhook GET request for URL verification")
            return '', 200

        # Parse form data (application/x-www-form-urlencoded)
        data = request.form.to_dict()

        if not data:
            logger.warning("Webhook request with no form data")
            return '', 200

        # Extract required fields
        token = data.get('token')
        timestamp = data.get('timestamp')
        signature = data.get('signature')
        event = data.get('event')

        if not all([token, timestamp, signature, event]):
            logger.warning(f"Webhook missing required fields. Event: {event}")
            return '', 200

        # Verify event type is supported
        if not SendCloudWebhookValidator.is_valid_event(event):
            logger.warning(f"Unsupported webhook event type: {event}")
            return '', 200

        # Verify signature (optional but recommended)
        app_key = os.getenv('SENDCLOUD_APP_KEY')
        if app_key:
            if not SendCloudWebhookValidator.verify_signature(token, timestamp, signature, app_key):
                logger.warning(f"Invalid webhook signature for event: {event}")
                return '', 200
        else:
            logger.warning("SENDCLOUD_APP_KEY not configured, skipping signature verification")

        logger.info(f"Received SendCloud email webhook: {event}")

        # Upload webhook payload to S3 for audit trail
        s3_key = f"webhooks/sendcloud/email/{event}/{timestamp}_{token}.json"
        # s3_manager.upload_json(data, s3_key)

        # Process based on event type
        if event == 'request':
            process_request_event(data)
        elif event == 'deliver':
            process_deliver_event(data)
        elif event == 'open':
            process_open_event(data)
        elif event == 'click':
            process_click_event(data)
        elif event == 'unsubscribe':
            process_unsubscribe_event(data)
        elif event == 'report_spam':
            process_report_spam_event(data)
        elif event == 'invalid':
            process_invalid_event(data)
        elif event == 'soft_bounce':
            process_soft_bounce_event(data)
        elif event == 'route':
            process_route_event(data)

        # Must return HTTP 200 within 3 seconds to prevent resend
        return '', 200

    except Exception as e:
        logger.error(f"Webhook processing error: {str(e)}", exc_info=True)
        # Return 200 anyway to prevent SendCloud retry (fix error and check logs)
        return '', 200

# Event processing functions
def process_request_event(data):
    """Process request event - mail request successful"""
    logger.info(f"Processing request event: {data.get('email')}")

def process_deliver_event(data):
    """Process deliver event - email delivered successfully"""
    logger.info(f"Processing deliver event: {data.get('email')}")

def process_open_event(data):
    """Process open event - user opened email"""
    logger.info(f"Processing open event: {data.get('email')}")

def process_click_event(data):
    """Process click event - user clicked link"""
    logger.info(f"Processing click event: {data.get('email')}")

def process_unsubscribe_event(data):
    """Process unsubscribe event - user unsubscribed"""
    logger.info(f"Processing unsubscribe event: {data.get('email')}")

def process_report_spam_event(data):
    """Process report_spam event - user reported as spam"""
    logger.info(f"Processing report_spam event: {data.get('email')}")

def process_invalid_event(data):
    """Process invalid event - email failed to send"""
    logger.info(f"Processing invalid event: {data.get('email')}")

def process_soft_bounce_event(data):
    """Process soft_bounce event - recipient rejected email"""
    logger.info(f"Processing soft_bounce event: {data.get('email')}")

def process_route_event(data):
    """Process route event - mail routing/forwarding"""
    logger.info(f"Processing route event: {data.get('email')}")
