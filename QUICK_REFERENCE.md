# SendCloud Email Webhook - Quick Reference

## Setup (5 minutes)

1. **Copy environment template**
   ```bash
   cp .env.example .env
   ```

2. **Update `.env` with your values**
   ```env
   SENDCLOUD_APP_KEY=your_app_key_from_sendcloud
   LOGTAIL_SOURCE_TOKEN=your_logtail_source_token
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Start application**
   ```bash
   python3 run.py
   ```

5. **Configure in SendCloud**
   - Dashboard → Mail → Send Settings → WebHook
   - Set URL: `http://your-domain.com/webhook/sendcloud/email`
   - Select events to monitor
   - Save

---

## API Endpoint

```
POST /webhook/sendcloud/email
Content-Type: application/x-www-form-urlencoded

Response: HTTP 200 (empty body)
```

---

## Webhook Data Format

SendCloud sends form-urlencoded data:
```
token=xxxxx
timestamp=1234567890
signature=SHA256_HASH
event=deliver
email=recipient@example.com
[other fields...]
```

---

## Signature Verification

```python
signature = SHA256(APP_KEY + token + timestamp)
```

Application automatically verifies if `SENDCLOUD_APP_KEY` is set.

---

## Supported Events

| Event | Description |
|-------|-------------|
| `request` | Mail request successful |
| `deliver` | Email delivered |
| `open` | Email opened |
| `click` | Link clicked |
| `unsubscribe` | User unsubscribed |
| `report_spam` | Reported as spam |
| `invalid` | Failed to send |
| `soft_bounce` | Temporary rejection |
| `route` | Mail routing |

---

## Response Requirements

✓ HTTP 200 status code
✓ Within 3 seconds
✓ Empty response body
✓ Required by SendCloud (or message will retry)

---

## Testing Webhook

1. **Verify URL works**
   ```bash
   curl http://localhost:5000/health
   ```

2. **Test with curl**
   ```bash
   curl -X POST http://localhost:5000/webhook/sendcloud/email \
     -d "event=deliver&token=test&timestamp=$(date +%s)&signature=test&email=user@example.com"
   ```

3. **Use Python test script**
   - See `WEBHOOK_GUIDE.md` for detailed test script

---

## Custom Event Processing

Edit `app/webhook_routes.py` to add custom logic:

```python
def process_deliver_event(data):
    """Process delivery event"""
    email = data.get('email')
    # Add your business logic here
    logger.info(f"Email delivered to: {email}")
```

---

## View Logs

```bash
# Real-time local logs
tail -f logs/app.log

# Filter by event type
grep "deliver" logs/app.log

# View structured logs online
# Visit: https://logs.betterstack.com
```

---

## Configuration Files

- `run.py` - Application entry point
- `app/__init__.py` - Flask app setup
- `app/webhook_routes.py` - Webhook handler (edit for custom logic)
- `app/webhook_validator.py` - Signature verification
- `app/log_forwarder.py` - Logtail / Better Stack log forwarding
- `config/config.py` - Environment configuration
- `config/logger.py` - Local logging setup

---

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `SENDCLOUD_APP_KEY` | SendCloud APP KEY | Yes* |
| `LOGTAIL_SOURCE_TOKEN` | Logtail / Better Stack source token | Yes |
| `FLASK_ENV` | Environment (development/production) | No |
| `FLASK_HOST` | Server host | No (default: 0.0.0.0) |
| `FLASK_PORT` | Server port | No (default: 5000) |
| `FLASK_DEBUG` | Debug mode | No (default: False) |

*Optional — but recommended for security

---

## Log Forwarding

Every webhook event is forwarded to Logtail as a structured JSON entry:

```json
{
  "message": "SendCloud webhook event: deliver",
  "event": "deliver",
  "email": "recipient@example.com",
  "token": "xxxxx",
  "timestamp": "1234567890",
  "data": { ... }
}
```

View logs at: **https://logs.betterstack.com**

---

## Common Issues

| Issue | Solution |
|-------|----------|
| 404 when accessing endpoint | Ensure application is running |
| Signature verification failures | Check `SENDCLOUD_APP_KEY` matches dashboard |
| Log forwarding errors | Verify `LOGTAIL_SOURCE_TOKEN` and network access |
| Slow responses | Check server resources, optimize processing |
| No local logs generated | Ensure `logs/` directory is writable |

---

## Production Deployment

```bash
# Using Gunicorn
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 'app:create_app()'

# Environment
export FLASK_ENV=production
export FLASK_DEBUG=False
```

---

## Security Checklist

- [ ] `SENDCLOUD_APP_KEY` is set
- [ ] `LOGTAIL_SOURCE_TOKEN` is set
- [ ] `.env` file is not in git (add to `.gitignore`)
- [ ] Use HTTPS in production
- [ ] Logtail source token is kept secret
- [ ] Use separate Logtail sources for dev and production
- [ ] Check logs regularly
- [ ] Monitor failed webhook attempts

---

## Useful Commands

```bash
# Start application
python3 run.py

# Check health
curl http://localhost:5000/health

# View local logs
tail -f logs/app.log

# Test webhook
curl -X POST http://localhost:5000/webhook/sendcloud/email \
  -d "event=deliver&token=test&timestamp=$(date +%s)&signature=test&email=user@example.com"

# Install/update dependencies
pip install -r requirements.txt
```

---

## Documentation

- **README.md** - Full project documentation
- **WEBHOOK_GUIDE.md** - Detailed testing and configuration guide
- **DEPLOYMENT.md** - Production deployment guide

---

## Support

1. Check local application logs: `logs/app.log`
2. Review `WEBHOOK_GUIDE.md` troubleshooting section
3. Verify SendCloud webhook delivery logs in dashboard
4. Check Logtail dashboard for forwarded events
5. Test with curl command above
