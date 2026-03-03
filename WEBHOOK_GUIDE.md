# SendCloud Email Webhook Integration Guide

This guide explains how to configure, test, and troubleshoot SendCloud email webhooks with this application.

## Table of Contents
1. [Configuration](#configuration)
2. [Webhook Data Format](#webhook-data-format)
3. [Testing](#testing)
4. [Troubleshooting](#troubleshooting)
5. [Event Details](#event-details)

---

## Configuration

### Step 1: Get SendCloud APP_KEY

1. Log in to SendCloud Dashboard
2. Navigate to: **Mail → Send Settings → WebHook**
3. Look for **APP KEY** in the configuration section
4. Copy the APP KEY

### Step 2: Get Logtail Source Token

1. Sign up or log in at https://logs.betterstack.com
2. Go to **Logs → Sources → Create source**
3. Choose **HTTP** as the platform
4. Copy the **Source Token**

### Step 3: Configure Application

Update your `.env` file:

```env
SENDCLOUD_APP_KEY=your_app_key_from_sendcloud
LOGTAIL_SOURCE_TOKEN=your_logtail_source_token
```

### Step 4: Configure Webhook in SendCloud Dashboard

1. In SendCloud Dashboard: **Mail → Send Settings → WebHook**
2. Set webhook URL to your server: `http://your-domain.com/webhook/sendcloud/email`
3. Select email events you want to monitor:
   - ☐ request (邮件请求成功)
   - ☐ deliver (邮件送达)
   - ☐ open (邮件打开)
   - ☐ click (链接点击)
   - ☐ unsubscribe (取消订阅)
   - ☐ report_spam (举报垃圾)
   - ☐ invalid (无效邮件)
   - ☐ soft_bounce (软退信)
   - ☐ route (转信)
4. Save configuration

### Step 5: Test URL Verification

SendCloud will verify your webhook URL by sending a GET request. The application automatically responds with HTTP 200.

Check logs to confirm:
```bash
tail -f logs/app.log
```

You should see:
```
Received webhook GET request for URL verification
```

---

## Webhook Data Format

### SendCloud Request Format

SendCloud sends webhook data as **application/x-www-form-urlencoded**:

```
POST /webhook/sendcloud/email HTTP/1.1
Content-Type: application/x-www-form-urlencoded

token=xxxxxxxxxxxxx
timestamp=1234567890
signature=SHA256_HASH
event=deliver
email=recipient@example.com
[other event-specific fields]
```

### Signature Verification

The `signature` field is calculated as:

```
signature = SHA256(APP_KEY + token + timestamp)
```

Example calculation:
```python
import hashlib

app_key = "your_app_key"
token = "webhook_token"
timestamp = "1234567890"

message = f"{app_key}{token}{timestamp}"
signature = hashlib.sha256(message.encode()).hexdigest()
```

---

## Testing

### Test 1: Verify Webhook URL

Use curl to simulate SendCloud's URL verification:

```bash
curl -X GET http://localhost:5000/webhook/sendcloud/email -v
```

Expected response:
```
HTTP/1.1 200 OK
```

Check logs:
```bash
tail -f logs/app.log | grep "GET request"
```

### Test 2: Send Test Webhook

Create a test script `test_webhook.py`:

```python
import requests
import hashlib
import time

# Configuration
BASE_URL = "http://localhost:5000"
WEBHOOK_URL = f"{BASE_URL}/webhook/sendcloud/email"
APP_KEY = "your_app_key_here"  # Update with your APP_KEY

def generate_signature(app_key, token, timestamp):
    """Generate SHA256 signature for webhook"""
    message = f"{app_key}{token}{timestamp}"
    return hashlib.sha256(message.encode()).hexdigest()

def test_webhook(event_type):
    """Test webhook with sample event"""
    token = "test_token_12345"
    timestamp = str(int(time.time()))
    signature = generate_signature(APP_KEY, token, timestamp)

    # Sample data for different events
    event_data = {
        'deliver': {
            'event': 'deliver',
            'token': token,
            'timestamp': timestamp,
            'signature': signature,
            'email': 'recipient@example.com',
            'mailfrom': 'sender@example.com',
            'subject': 'Test Email',
        },
        'open': {
            'event': 'open',
            'token': token,
            'timestamp': timestamp,
            'signature': signature,
            'email': 'recipient@example.com',
            'mailfrom': 'sender@example.com',
        },
        'click': {
            'event': 'click',
            'token': token,
            'timestamp': timestamp,
            'signature': signature,
            'email': 'recipient@example.com',
            'url': 'https://example.com/link',
        },
        'unsubscribe': {
            'event': 'unsubscribe',
            'token': token,
            'timestamp': timestamp,
            'signature': signature,
            'email': 'recipient@example.com',
        },
    }

    data = event_data.get(event_type, event_data['deliver'])
    data['event'] = event_type

    # Send webhook
    print(f"\nTesting {event_type} webhook...")
    print(f"Data: {data}")

    response = requests.post(WEBHOOK_URL, data=data)

    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")

    return response.status_code == 200

if __name__ == '__main__':
    # Test each event type
    events = ['deliver', 'open', 'click', 'unsubscribe']

    print("=" * 50)
    print("SendCloud Webhook Test Suite")
    print("=" * 50)

    results = {}
    for event in events:
        results[event] = test_webhook(event)
        time.sleep(0.5)

    print("\n" + "=" * 50)
    print("Test Results:")
    print("=" * 50)
    for event, passed in results.items():
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{event}: {status}")
```

Run the test:

```bash
python3 test_webhook.py
```

Expected output:
```
==================================================
SendCloud Webhook Test Suite
==================================================

Testing deliver webhook...
Data: {...}
Status Code: 200
Response:

Testing open webhook...
Data: {...}
Status Code: 200
Response:

==================================================
Test Results:
==================================================
deliver: ✓ PASSED
open: ✓ PASSED
click: ✓ PASSED
unsubscribe: ✓ PASSED
```

Check local application logs:
```bash
tail -f logs/app.log
```

You should see entries like:
```
2026-03-03 12:30:45,123 - app.webhook_routes - INFO - Received SendCloud email webhook: deliver
2026-03-03 12:30:45,234 - app.log_forwarder - INFO - Log forwarded to Logtail: event=deliver
2026-03-03 12:30:45,235 - app.webhook_routes - INFO - Processing deliver event: recipient@example.com
```

You can also verify the forwarded log entries in your Logtail dashboard at https://logs.betterstack.com.

### Test 3: Invalid Signature Test

Test with an incorrect signature to verify validation:

```bash
curl -X POST http://localhost:5000/webhook/sendcloud/email \
  -d "event=deliver&token=test&timestamp=$(date +%s)&signature=invalid_signature&email=test@example.com"
```

Expected behavior:
- HTTP 200 response (to prevent SendCloud retries)
- Warning logged: `"Invalid webhook signature for event: deliver"`

---

## Troubleshooting

### Issue: Webhook URL verification fails

**Symptoms:**
- SendCloud shows "URL verification failed"
- GET request to webhook URL returns error

**Solution:**
1. Verify application is running: `curl http://localhost:5000/health`
2. Check logs: `tail -f logs/app.log`
3. Verify firewall allows incoming connections
4. For production, ensure HTTPS is configured

### Issue: Webhook events not received

**Symptoms:**
- SendCloud shows "Webhook configured" but no events arrive
- Application logs don't show incoming webhooks

**Solution:**
1. Verify webhook is enabled in SendCloud dashboard
2. Check that required events are selected
3. Verify webhook URL is correct and accessible
4. Check application is running and accepting POST requests
5. Review SendCloud webhook delivery logs in dashboard

### Issue: Signature verification failures

**Symptoms:**
- Logs show: `"Invalid webhook signature for event"`
- All webhooks are received but marked as invalid

**Solution:**
1. Verify `SENDCLOUD_APP_KEY` in `.env` matches SendCloud dashboard
2. Check if APP_KEY was recently rotated in SendCloud
3. Verify signature calculation formula: `SHA256(APP_KEY + token + timestamp)`
4. Check for whitespace or encoding issues in APP_KEY

### Issue: Log forwarding failures

**Symptoms:**
- Logs show: `"Logtail rejected log entry"` or `"Failed to forward log to Logtail"`
- Webhooks are received and processed, but entries don't appear in Logtail

**Solution:**
1. Verify `LOGTAIL_SOURCE_TOKEN` in `.env` is correct
2. Confirm the Logtail source is active at https://logs.betterstack.com
3. Check network connectivity to `https://in.logs.betterstack.com`
4. Ensure outbound HTTPS (port 443) is allowed by your firewall
5. Check local `logs/app.log` for detailed error messages

### Issue: Slow webhook processing

**Symptoms:**
- Webhooks take longer than 3 seconds to respond
- SendCloud reports webhook failures

**Solution:**
1. Log forwarding has a 5-second timeout and is non-blocking — it won't prevent HTTP 200 from being returned
2. Profile application: check server CPU and memory
3. Reduce processing in event handler functions
4. Consider using a task queue for any heavy background operations

---

## Event Details

### Event: request
**Trigger:** Mail request successful

```python
{
    'event': 'request',
    'email': 'recipient@example.com',
    'mailfrom': 'sender@example.com',
    'subject': 'Email Subject'
}
```

### Event: deliver
**Trigger:** Email delivered successfully

```python
{
    'event': 'deliver',
    'email': 'recipient@example.com',
    'mailfrom': 'sender@example.com',
    'subject': 'Email Subject',
    'sendtime': '1234567890'
}
```

### Event: open
**Trigger:** User opened email

```python
{
    'event': 'open',
    'email': 'recipient@example.com',
    'mailfrom': 'sender@example.com',
    'opentime': '1234567890'
}
```

### Event: click
**Trigger:** User clicked link

```python
{
    'event': 'click',
    'email': 'recipient@example.com',
    'mailfrom': 'sender@example.com',
    'url': 'https://example.com/link',
    'clicktime': '1234567890'
}
```

### Event: unsubscribe
**Trigger:** User unsubscribed

```python
{
    'event': 'unsubscribe',
    'email': 'recipient@example.com',
    'mailfrom': 'sender@example.com',
    'unsubscribetime': '1234567890'
}
```

### Event: report_spam
**Trigger:** User reported as spam

```python
{
    'event': 'report_spam',
    'email': 'recipient@example.com',
    'mailfrom': 'sender@example.com',
    'reporttime': '1234567890'
}
```

### Event: invalid
**Trigger:** Email failed to send

```python
{
    'event': 'invalid',
    'email': 'invalid@example.com',
    'mailfrom': 'sender@example.com',
    'subject': 'Email Subject',
    'reason': 'Email address invalid'
}
```

### Event: soft_bounce
**Trigger:** Recipient rejected email

```python
{
    'event': 'soft_bounce',
    'email': 'recipient@example.com',
    'mailfrom': 'sender@example.com',
    'reason': 'Mailbox full',
    'bouncetime': '1234567890'
}
```

### Event: route
**Trigger:** Mail routing/forwarding

```python
{
    'event': 'route',
    'email': 'recipient@example.com',
    'mailfrom': 'sender@example.com',
    'routetime': '1234567890'
}
```

---

## Monitoring and Logs

### View Real-time Local Logs

```bash
tail -f logs/app.log
```

### Filter Logs by Event Type

```bash
grep "deliver" logs/app.log
grep "open" logs/app.log
grep "click" logs/app.log
```

### View Structured Logs in Logtail

1. Visit https://logs.betterstack.com
2. Select your source
3. Use the search bar to filter by `event`, `email`, or any field
4. Set time range to find recent webhook events

### Sample Log Output (local)

```
2026-03-03 12:30:45,123 - app.webhook_routes - INFO - Received SendCloud email webhook: deliver
2026-03-03 12:30:45,234 - app.log_forwarder - INFO - Log forwarded to Logtail: event=deliver
2026-03-03 12:30:45,235 - app.webhook_routes - INFO - Processing deliver event: user@example.com
```

### Forwarded Log Entry (Logtail / Better Stack)

```json
{
  "message": "SendCloud webhook event: deliver",
  "event": "deliver",
  "email": "user@example.com",
  "token": "xxxxx",
  "timestamp": "1234567890",
  "data": {
    "event": "deliver",
    "email": "user@example.com",
    "mailfrom": "sender@example.com",
    "subject": "Test Email"
  }
}
```

---

## Performance Considerations

- **Response Time**: Application responds within 3 seconds as required
- **Log Forwarding Timeout**: 5-second timeout on Logtail requests; failures are caught and logged locally without blocking the response
- **Local Logging**: Rotating file handler prevents disk space issues
- **Rate Limiting**: Consider implementing rate limiting for production

---

## Security Reminders

✓ Verify webhook signatures
✓ Use HTTPS in production
✓ Store APP_KEY and LOGTAIL_SOURCE_TOKEN securely in environment variables
✓ Never commit `.env` file to version control
✓ Rotate LOGTAIL_SOURCE_TOKEN if compromised
✓ Use separate Logtail sources for development and production
✓ Monitor logs for suspicious activity
✓ Rotate APP_KEY periodically
