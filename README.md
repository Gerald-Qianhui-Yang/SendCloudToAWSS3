# SendCloud Email Webhook Handler

A Flask application that receives SendCloud email webhook events and forwards them to a third-party logging service (Logtail / Better Stack) for structured log storage and audit trails.

## Overview

This application implements SendCloud email webhook integration with the following features:
- Receives and validates SendCloud email events (deliver, open, click, unsubscribe, etc.)
- SHA256 signature verification for webhook security
- Structured log forwarding to Logtail / Better Stack via HTTP
- Comprehensive local logging and error handling
- Fast response times (returns HTTP 200 within 3 seconds as required by SendCloud)

## Features

- **Email Event Handling**: Supports 9 SendCloud email events (request, deliver, open, click, unsubscribe, report_spam, invalid, soft_bounce, route)
- **Webhook Validation**: SHA256-based signature verification using SendCloud APP_KEY
- **Third-Party Log Forwarding**: Structured JSON log entries sent to Logtail / Better Stack for audit trails and monitoring
- **Form-URLEncoded Support**: Handles SendCloud's `application/x-www-form-urlencoded` data format
- **Fast Response Times**: Guarantees HTTP 200 response within 3 seconds to prevent SendCloud retries
- **Comprehensive Logging**: Local rotating file-based logging (10MB per file, up to 10 backups)
- **CORS Support**: Configured for cross-origin requests

## Setup Instructions

### 1. Create and Activate Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Configuration

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```env
# Flask Configuration
FLASK_ENV=development
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
FLASK_DEBUG=False

# SendCloud Email Webhook
# Get APP_KEY from: SendCloud Dashboard > Mail > Send Settings > WebHook
SENDCLOUD_APP_KEY=your_sendcloud_app_key_here

# Third-party Logging (Logtail / Better Stack)
# Get your source token from: https://logs.betterstack.com -> Sources -> Create source
LOGTAIL_SOURCE_TOKEN=your_logtail_source_token_here
```

### 4. Configure SendCloud Webhook

1. Log in to SendCloud Dashboard
2. Go to **Mail** > **Send Settings** > **WebHook**
3. Select email events you want to receive:
   - request (邮件请求成功)
   - deliver (邮件送达)
   - open (邮件打开)
   - click (链接点击)
   - unsubscribe (取消订阅)
   - report_spam (举报垃圾)
   - invalid (无效邮件)
   - soft_bounce (软退信)
   - route (转信)
4. Set webhook URL to: `http://your-domain.com/webhook/sendcloud/email`
5. Copy the APP_KEY and add to your `.env` file

## Running the Application

```bash
python3 run.py
```

The API will be available at `http://localhost:5000`

## API Endpoints

### Health Check
```
GET /health

Response: HTTP 200
```

### SendCloud Email Webhook
```
POST /webhook/sendcloud/email

Content-Type: application/x-www-form-urlencoded

Data:
- event: email event type (deliver, open, click, etc.)
- token: unique token for this webhook
- timestamp: Unix timestamp
- signature: SHA256 hash for verification
- [other event-specific fields]

Response: HTTP 200
```

### URL Verification
```
GET /webhook/sendcloud/email

Response: HTTP 200
```

## Supported SendCloud Email Events

| Event | Description | Trigger |
|-------|-------------|---------|
| `request` | Mail request successful | Email request accepted |
| `deliver` | Email delivered | Email successfully delivered |
| `open` | User opened email | Email opened by recipient |
| `click` | User clicked link | Recipient clicked a link |
| `unsubscribe` | User unsubscribed | Recipient unsubscribed |
| `report_spam` | User reported spam | Recipient reported as spam |
| `invalid` | Email failed to send | Invalid email or delivery failed |
| `soft_bounce` | Recipient rejected | Temporary rejection |
| `route` | Mail routing | Email routing/forwarding |

## SendCloud Webhook Specifications

### Data Format
- **Content-Type**: `application/x-www-form-urlencoded`
- **Method**: POST (with GET support for URL verification)
- **Response Requirement**: Must return HTTP 200 within **3 seconds**

### Signature Verification
SendCloud uses SHA256 signature verification:
```
signature = SHA256(APP_KEY + token + timestamp)
```

The webhook POST data includes:
- `token`: Unique identifier for this webhook
- `timestamp`: Unix timestamp when webhook was sent
- `signature`: SHA256 hash for verification

### Retry Mechanism
If the server doesn't return HTTP 200 within 3 seconds, SendCloud will retry:
- Max retries: 7 attempts
- Retry intervals: 3min → 10min → 30min → 1h → 6h → 12h → 24h
- Message retention: 15 days (can request re-push after)

## Project Structure

```
SendCloudToAWSS3/
├── app/
│   ├── __init__.py              # Flask app factory
│   ├── webhook_routes.py        # Email webhook endpoints
│   ├── webhook_validator.py     # SendCloud signature verification
│   └── log_forwarder.py         # Third-party log forwarding (Logtail)
├── config/
│   ├── config.py                # Environment-based configuration
│   └── logger.py                # Local logging setup
├── logs/                         # Local application logs directory
├── venv/                         # Virtual environment
├── .env                          # Environment variables (not in git)
├── .env.example                  # Environment template
├── requirements.txt              # Python dependencies
├── run.py                        # Application entry point
└── README.md                     # This file
```

## How It Works

```
SendCloud Service
    ↓
POST /webhook/sendcloud/email (form-urlencoded)
    ↓
webhook_routes.py (receives request)
    ↓
webhook_validator.py (verifies SHA256 signature)
    ↓
log_forwarder.py (forwards structured log entry to Logtail)
    ↓
process_*_event() (custom event handling)
    ↓
Return HTTP 200 (within 3 seconds)
```

## Error Handling

- **Invalid signatures**: Returns HTTP 200 (prevents retries), logs warning
- **Processing errors**: Returns HTTP 200, logs error
- **Missing fields**: Returns HTTP 200, logs warning
- **Log forwarding failures**: Logged locally but doesn't block webhook processing

This approach ensures SendCloud doesn't retry on errors, allowing time to fix issues and review logs.

## Security Best Practices

1. **Always verify signatures**: Enable signature verification in production
2. **Use HTTPS**: Configure HTTPS in production environments
3. **Secure environment variables**:
   - Never commit `.env` file to version control
   - Use secure secret management in production
4. **Logtail Security**:
   - Rotate your source token if compromised
   - Use separate sources for development and production
5. **Application Security**:
   - Keep dependencies updated
   - Review logs regularly for suspicious activity

## Logging

### Local Logs
Application logs are stored in `logs/app.log` with automatic rotation:
- **Max file size**: 10 MB
- **Backup files**: Up to 10 rotated logs
- **Log level**: INFO and above
- **Format**: `timestamp - logger_name - level - message`

```bash
tail -f logs/app.log
```

### Third-Party Logs (Logtail / Better Stack)
Every incoming webhook event is forwarded as a structured JSON log entry to Logtail:
- View and search logs at: https://logs.betterstack.com
- Each entry includes: `event`, `email`, `token`, `timestamp`, and full `data` payload

## Troubleshooting

### Webhook not being received
1. Verify webhook URL in SendCloud dashboard is correct
2. Check that application is running and accessible: `curl http://localhost:5000/health`
3. Ensure firewall/security groups allow incoming connections
4. Check application logs: `tail -f logs/app.log`

### Signature verification failures
1. Confirm `SENDCLOUD_APP_KEY` is correct in `.env`
2. Verify the key hasn't been rotated in SendCloud dashboard
3. Check application logs for verification errors

### Log forwarding failures
1. Verify `LOGTAIL_SOURCE_TOKEN` is set correctly in `.env`
2. Check network connectivity to `https://in.logs.betterstack.com`
3. Confirm your Logtail source is active in the dashboard
4. Check local `logs/app.log` for forwarding error messages

### Slow response times
1. Log forwarding has a 5-second timeout — if Logtail is unreachable, requests will still complete
2. Check application server resources (CPU, memory)
3. Consider async processing for heavy operations

## Development

To add custom event handling:

1. Open `app/webhook_routes.py`
2. Edit the `process_*_event()` function for the event type
3. Add your business logic (database writes, notifications, etc.)
4. Ensure processing completes quickly to stay within 3-second limit

Example:
```python
def process_deliver_event(data):
    """Process delivery event"""
    email = data.get('email')
    # Add your logic here
    logger.info(f"Email delivered to: {email}")
```

## Dependencies

- **Flask**: Web framework
- **Flask-CORS**: Cross-origin resource sharing
- **python-dotenv**: Environment variable management
- **requests**: HTTP client for log forwarding to Logtail
- **Werkzeug**: WSGI utilities

See `requirements.txt` for versions.

## License

[Your License Here]

## Support

For issues or questions:
1. Check application logs: `logs/app.log`
2. Review SendCloud webhook documentation
3. Verify Logtail source token and network connectivity
4. Check SendCloud dashboard for webhook delivery status
