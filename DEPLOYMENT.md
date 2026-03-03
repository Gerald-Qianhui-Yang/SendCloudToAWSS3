# Deployment Guide

This guide covers deploying the SendCloud Email Webhook application to production.

## Pre-Deployment Checklist

### Code and Configuration
- [ ] All code changes have been reviewed
- [ ] `.env` file is configured with production values
- [ ] `.env` file is added to `.gitignore` (never commit sensitive data)
- [ ] `requirements.txt` is up to date
- [ ] All tests pass locally
- [ ] Code follows project standards

### SendCloud Configuration
- [ ] SendCloud Account is active
- [ ] APP_KEY has been obtained from SendCloud dashboard
- [ ] Webhook URL is configured in SendCloud
- [ ] Test events have been sent and received

### Logtail / Better Stack Configuration
- [ ] Logtail account is active at https://logs.betterstack.com
- [ ] A production Logtail source has been created (type: HTTP)
- [ ] `LOGTAIL_SOURCE_TOKEN` has been obtained from the source settings
- [ ] A separate source exists for development vs production (recommended)

### Infrastructure
- [ ] Production server/hosting is ready
- [ ] HTTPS/SSL certificate is installed
- [ ] Domain name is configured
- [ ] Firewall allows inbound traffic on port 443
- [ ] Firewall allows outbound traffic on port 443 (required for Logtail)
- [ ] Server has Python 3.7+ installed

---

## Deployment Steps

### Step 1: Server Setup

```bash
# SSH to production server
ssh user@your-production-server.com

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install python3 python3-pip python3-venv -y

# Create application directory
sudo mkdir -p /var/www/sendcloud-webhook
sudo chown $USER:$USER /var/www/sendcloud-webhook
cd /var/www/sendcloud-webhook
```

### Step 2: Deploy Application

```bash
# Clone or copy application
# Option 1: Git clone
git clone <your-repo-url> .

# Option 2: Or copy files
scp -r ./* user@server:/var/www/sendcloud-webhook/

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install production WSGI server
pip install gunicorn
```

### Step 3: Configure Environment

```bash
# Create .env file
nano .env
```

Add production configuration:

```env
# Flask Configuration
FLASK_ENV=production
FLASK_HOST=127.0.0.1
FLASK_PORT=5000
FLASK_DEBUG=False

# SendCloud Configuration
SENDCLOUD_APP_KEY=your_production_sendcloud_app_key

# Third-party Logging (Logtail / Better Stack)
# Get your source token from: https://logs.betterstack.com -> Sources
LOGTAIL_SOURCE_TOKEN=your_production_logtail_source_token
```

### Step 4: Setup Systemd Service

Create systemd service file:

```bash
sudo nano /etc/systemd/system/sendcloud-webhook.service
```

Add the following content:

```ini
[Unit]
Description=SendCloud Email Webhook Service
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/var/www/sendcloud-webhook
Environment="PATH=/var/www/sendcloud-webhook/venv/bin"
ExecStart=/var/www/sendcloud-webhook/venv/bin/gunicorn \
    --workers 4 \
    --worker-class sync \
    --bind 127.0.0.1:5000 \
    --timeout 30 \
    --access-logfile /var/log/sendcloud-webhook/access.log \
    --error-logfile /var/log/sendcloud-webhook/error.log \
    --log-level info \
    'app:create_app()'

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable sendcloud-webhook
sudo systemctl start sendcloud-webhook
sudo systemctl status sendcloud-webhook
```

### Step 5: Setup Nginx Reverse Proxy

Install Nginx:

```bash
sudo apt install nginx -y
```

Create Nginx configuration:

```bash
sudo nano /etc/nginx/sites-available/sendcloud-webhook
```

Add configuration:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    # SSL certificates (using Let's Encrypt with Certbot)
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    # SSL security headers
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Access logging
    access_log /var/log/nginx/sendcloud-webhook-access.log;
    error_log /var/log/nginx/sendcloud-webhook-error.log;

    # Proxy settings
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Health check endpoint
    location /health {
        proxy_pass http://127.0.0.1:5000;
        access_log off;
    }
}
```

Enable the configuration:

```bash
sudo ln -s /etc/nginx/sites-available/sendcloud-webhook /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Step 6: Setup SSL Certificate

Using Let's Encrypt with Certbot:

```bash
sudo apt install certbot python3-certbot-nginx -y

sudo certbot certonly --nginx -d your-domain.com

# Renew automatically
sudo certbot renew --dry-run
```

### Step 7: Create Log Directories

```bash
# Create log directory for application
mkdir -p /var/www/sendcloud-webhook/logs
sudo mkdir -p /var/log/sendcloud-webhook
sudo chown www-data:www-data /var/log/sendcloud-webhook

# Set permissions
chmod 755 /var/www/sendcloud-webhook/logs
sudo chmod 755 /var/log/sendcloud-webhook
```

### Step 8: Verify Deployment

```bash
# Check service status
sudo systemctl status sendcloud-webhook

# Test endpoint
curl https://your-domain.com/health

# Check local logs
tail -f /var/www/sendcloud-webhook/logs/app.log
sudo tail -f /var/log/nginx/sendcloud-webhook-access.log
```

---

## Post-Deployment Steps

### Configure SendCloud

1. Log in to SendCloud Dashboard
2. Go to **Mail** → **Send Settings** → **WebHook**
3. Update webhook URL to: `https://your-domain.com/webhook/sendcloud/email`
4. Verify URL by clicking "Test"
5. Select email events to monitor
6. Save configuration

### Test Webhook Delivery

1. Send a test email through SendCloud
2. Check local application logs for webhook events: `tail -f /var/www/sendcloud-webhook/logs/app.log`
3. Verify log entries appear in your Logtail dashboard at https://logs.betterstack.com
4. Confirm events are being tracked correctly

### Monitor Application

```bash
# Monitor local logs in real-time
tail -f /var/www/sendcloud-webhook/logs/app.log

# View structured logs in Logtail
# https://logs.betterstack.com

# Monitor Nginx
tail -f /var/log/nginx/sendcloud-webhook-access.log
```

---

## Backup and Recovery

### Backup Application

```bash
# Backup application code
tar -czf sendcloud-webhook-backup-$(date +%Y%m%d).tar.gz \
    /var/www/sendcloud-webhook/

# Backup .env file separately (secure)
cp /var/www/sendcloud-webhook/.env .env.backup
chmod 600 .env.backup
```

### Recovery Steps

```bash
# Stop service
sudo systemctl stop sendcloud-webhook

# Restore files
cd /var/www/sendcloud-webhook
tar -xzf sendcloud-webhook-backup-20260303.tar.gz

# Restart service
sudo systemctl start sendcloud-webhook

# Verify
sudo systemctl status sendcloud-webhook
```

---

## Monitoring and Alerts

### Setup Log Monitoring

```bash
# Monitor errors locally
sudo tail -f /var/log/sendcloud-webhook/error.log

# Count webhook events received
grep "Received SendCloud" /var/www/sendcloud-webhook/logs/app.log | wc -l

# Monitor log forwarding failures
grep "Failed to forward" /var/www/sendcloud-webhook/logs/app.log
```

### Logtail Alerts

Set up automated alerts directly in the Logtail / Better Stack dashboard:
1. Go to https://logs.betterstack.com → **Alerts**
2. Create an alert for log entries matching `"Failed to forward"` or `"ERROR"`
3. Configure notification channels (email, Slack, PagerDuty, etc.)

### Setup Local Email Alerts (Optional)

Install `mail-utils`:

```bash
sudo apt install mailutils -y
```

Create alert script (`/usr/local/bin/check-webhook.sh`):

```bash
#!/bin/bash

ERROR_LOG="/var/log/sendcloud-webhook/error.log"
EMAIL="admin@your-domain.com"
THRESHOLD=5

# Count errors in last 5 minutes
RECENT_ERRORS=$(tail -300 "$ERROR_LOG" | wc -l)

if [ "$RECENT_ERRORS" -gt "$THRESHOLD" ]; then
    echo "Alert: $RECENT_ERRORS errors detected in webhook service" | \
    mail -s "SendCloud Webhook Alert" "$EMAIL"
fi
```

Add to crontab:

```bash
sudo crontab -e

# Add line:
*/5 * * * * /usr/local/bin/check-webhook.sh
```

---

## Performance Optimization

### Gunicorn Workers

For production, calculate optimal worker count:

```
Workers = (2 × CPU cores) + 1
```

For 4 cores:
```
Workers = (2 × 4) + 1 = 9
```

Update systemd service:
```ini
ExecStart=/var/www/sendcloud-webhook/venv/bin/gunicorn \
    --workers 9 \
    ...
```

### Log Forwarding

The `LogForwarder` uses a synchronous HTTP POST with a 5-second timeout. For very high webhook volumes, consider moving log forwarding to a background thread or task queue (e.g. Celery) to reduce per-request latency.

### Database Indexing (if adding database storage)

If you add database storage, create indexes on:
- `event` - for filtering by event type
- `timestamp` - for time-range queries
- `email` - for user lookups

---

## Security Hardening

### Firewall Configuration

```bash
sudo ufw enable
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp      # SSH
sudo ufw allow 80/tcp      # HTTP
sudo ufw allow 443/tcp     # HTTPS
sudo ufw allow out 443/tcp # HTTPS for Logtail
```

### File Permissions

```bash
# Secure .env file
sudo chmod 600 /var/www/sendcloud-webhook/.env

# Secure logs
sudo chmod 750 /var/log/sendcloud-webhook
```

### Regular Updates

```bash
# Setup automatic security updates
sudo apt install unattended-upgrades -y
sudo systemctl enable unattended-upgrades
```

---

## Rollback Procedure

If deployment fails:

```bash
# Stop service
sudo systemctl stop sendcloud-webhook

# Restore previous version
cd /var/www/sendcloud-webhook
tar -xzf sendcloud-webhook-backup-previous.tar.gz

# Restart
sudo systemctl start sendcloud-webhook

# Verify
sudo systemctl status sendcloud-webhook
curl https://your-domain.com/health
```

---

## Maintenance Schedule

### Daily
- Monitor local error logs
- Check Logtail dashboard for anomalies
- Verify webhook delivery rate in SendCloud dashboard

### Weekly
- Review application performance
- Check certificate renewal status
- Audit access logs

### Monthly
- Backup application code and `.env`
- Review and rotate local logs
- Update Python dependencies: `pip install -r requirements.txt --upgrade`
- Security audit

### Quarterly
- Full disaster recovery test
- Performance optimization review
- Rotate `SENDCLOUD_APP_KEY` and `LOGTAIL_SOURCE_TOKEN`
- Security patches update

---

## Troubleshooting Deployment

### Service fails to start

```bash
# Check service logs
sudo systemctl status sendcloud-webhook -l

# Check Gunicorn output
sudo journalctl -u sendcloud-webhook -n 50
```

### Nginx returns 502 Bad Gateway

```bash
# Check Gunicorn is running
sudo systemctl status sendcloud-webhook

# Check socket is listening
sudo netstat -tlnp | grep 5000
```

### Webhooks not being received

```bash
# Check firewall
sudo ufw status

# Check Nginx logs
tail -f /var/log/nginx/sendcloud-webhook-error.log

# Test connectivity
curl -v https://your-domain.com/webhook/sendcloud/email
```

### Log entries not appearing in Logtail

```bash
# Check for forwarding errors in local logs
grep "Logtail" /var/www/sendcloud-webhook/logs/app.log

# Verify outbound HTTPS is allowed
curl -v https://in.logs.betterstack.com

# Check LOGTAIL_SOURCE_TOKEN is set
grep LOGTAIL /var/www/sendcloud-webhook/.env
```

---

## Support and Documentation

- **Production Server**: your-domain.com
- **Health Check**: https://your-domain.com/health
- **Application Logs**: /var/www/sendcloud-webhook/logs/app.log
- **Nginx Logs**: /var/log/nginx/sendcloud-webhook-*.log
- **Service Logs**: `journalctl -u sendcloud-webhook`
- **Logtail Dashboard**: https://logs.betterstack.com
