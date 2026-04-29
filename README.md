# Smart Server Monitoring System

A lightweight Python-based system that continuously monitors multiple servers/websites, logs their availability and performance, detects status changes, and sends email alerts when issues occur.

## Features

✅ **Multi-Server Support** — Monitor unlimited servers from a simple JSON config  
✅ **HTTP Health Checks** — GET requests with timeout detection and status code analysis  
✅ **SQLite Logging** — All checks logged to database for historical analysis  
✅ **Email Alerts** — Automatic alerts on UP→DOWN and DOWN→UP transitions  
✅ **Anti-Spam Logic** — Prevents duplicate alerts for the same event within cooldown period  
✅ **Uptime Calculation** — Track daily, weekly, monthly, and overall uptime percentages  
✅ **Graceful Error Handling** — Network failures don't crash the system  
✅ **Simple Scheduler** — Configurable check intervals via `time.sleep()` loop  

## Architecture

```
config.json → servers.json → main.py (scheduler loop)
                                ↓
                            health_checker.py (HTTP checks)
                                ↓
                            database.py (SQLite logging)
                                ↓
                            alert_manager.py (email alerts)
                                ↓
                            uptime_calculator.py (metrics)
```

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Servers

Copy and edit the servers configuration:

```bash
cp servers.json.example servers.json
```

Edit `servers.json` to add your servers:

```json
{
  "servers": [
    {
      "name": "My Website",
      "url": "https://example.com"
    },
    {
      "name": "API Server",
      "url": "https://api.example.com/health"
    }
  ]
}
```

### 3. Configure SMTP for Alerts

Copy and edit the system configuration:

```bash
cp config.json.example config.json
```

Edit `config.json` to add your SMTP credentials:

```json
{
  "check_interval": 60,
  "response_timeout": 2,
  "smtp": {
    "host": "smtp.gmail.com",
    "port": 587,
    "use_tls": true,
    "username": "your-email@gmail.com",
    "password": "your-app-password",
    "from_email": "your-email@gmail.com",
    "to_email": "recipient@example.com"
  },
  "alert_cooldown_minutes": 5
}
```

### 4. Run the System

```bash
python main.py
```

You'll see real-time monitoring output:

```
🔍 Smart Server Monitoring System
============================================================
✓ Config loaded: config.json
✓ Servers loaded: 2 server(s)
  - My Website (https://example.com)
  - API Server (https://api.example.com/health)
✓ Database initialized: server_monitor.db

🚀 Starting monitoring (interval: 60s, alert cooldown: 5m)
============================================================
Press Ctrl+C to stop

[Check #1] 2026-04-26 12:30:45
────────────────────────────────────────────────────────────
🟢 My Website: UP (0.245s)
🟢 API Server: UP (0.187s)

📊 Uptime Summary:
  My Website: 100% (24h)
  API Server: 100% (24h)

⏳ Next check in 60 seconds...
```

## Configuration Guide

### servers.json

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Friendly name for the server (unique) |
| `url` | string | Full URL to check (http:// or https://) |

### config.json

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `check_interval` | int | 60 | Seconds between health checks |
| `response_timeout` | int | 2 | Timeout for HTTP requests (seconds) |
| `alert_cooldown_minutes` | int | 5 | Prevent duplicate alerts within X minutes |
| `smtp.host` | string | - | SMTP server hostname |
| `smtp.port` | int | - | SMTP server port (usually 587 for TLS) |
| `smtp.use_tls` | bool | true | Enable TLS encryption |
| `smtp.username` | string | - | Email account username |
| `smtp.password` | string | - | Email account password (or app-specific password) |
| `smtp.from_email` | string | - | Sender email address |
| `smtp.to_email` | string | - | Recipient email address for alerts |

## Status Detection Rules

Server Status Determination:

- **UP** ✅  
  - HTTP status code = 200 (exact)
  - Response time < timeout threshold
  
- **DOWN** ❌  
  - HTTP timeout
  - Connection failure (DNS, reset, refused)
  - HTTP status code ≥ 500
  - Response time ≥ timeout threshold

## Email Alerts

Alerts are sent when:

- **Server transitions UP → DOWN**: Immediate alert with error details
- **Server transitions DOWN → UP**: Recovery notification
- **Same state repeats**: No duplicate alert (anti-spam)

**Alert Cooldown**: By default, only one alert per server/type within 5 minutes (configurable).

## Database Schema

Three main tables track everything:

### servers
```
id (PK) | name | url | created_at | last_check_time | last_status
```

### monitoring_checks
```
id (PK) | server_id (FK) | timestamp | status | response_time | http_status_code | error_message
```

### alerts
```
id (PK) | server_id (FK) | timestamp | alert_type | message | sent_at
```

## Logs

All activity is logged to `logs/server_checker.log`:

```
2026-04-26 12:30:45 - INFO - 🟢 My Website: UP (0.245s)
2026-04-26 12:31:05 - INFO - 🔴 API Server: DOWN - Connection failed
2026-04-26 12:31:05 - WARNING - ⚡ Status change: UP → DOWN
2026-04-26 12:31:06 - INFO - ✓ Alert email sent for API Server (DOWN)
```

## Uptime Calculation

Uptime % is calculated based on check history:

```
Uptime % = (UP checks / Total checks) × 100
```

Available periods:
- **Daily**: Last 24 hours
- **Weekly**: Last 7 days
- **Monthly**: Last 30 days
- **Overall**: All available data

## Gmail Setup (Common Configuration)

1. **Enable 2-Factor Authentication** on your Google account
2. **Create an App Password**: https://myaccount.google.com/apppasswords
3. **Use in config.json**:
   ```json
   "smtp": {
     "host": "smtp.gmail.com",
     "port": 587,
     "use_tls": true,
     "username": "your-email@gmail.com",
     "password": "your-app-password",
     "from_email": "your-email@gmail.com",
     "to_email": "recipient@gmail.com"
   }
   ```

## Troubleshooting

### No emails being sent
- ✓ Verify SMTP credentials in `config.json`
- ✓ Check if 2FA is enabled (Gmail requires app password)
- ✓ Ensure firewall allows outbound SMTP (port 587)
- ✓ Check `logs/server_checker.log` for detailed errors

### Database locked errors
- ✓ Only one instance of `main.py` should run at a time
- ✓ Kill any stuck Python processes: `taskkill /IM python.exe`
- ✓ Delete corrupted database: `rm server_monitor.db` (data will be lost)

### Servers showing as DOWN incorrectly
- ✓ Increase `response_timeout` in `config.json` (e.g., to 5 seconds)
- ✓ Verify server URL is correct and accessible
- ✓ Check if server is behind a CDN/load balancer

## Performance Notes

- **Server Limit**: Tested with 50+ servers
- **Optimal Interval**: 60-300 seconds (balance between detection speed and load)
- **Database Size**: ~1KB per check; ~100KB per server per month

## Future Enhancements (Phase 3+)

- 🎨 Web Dashboard (React)
- 🔌 REST API (Flask)
- 📱 Telegram/Discord alerts
- 🔐 User authentication
- 🛡️ SSL certificate monitoring
- 🔄 Retry logic (3 checks before marking DOWN)
- 📊 Public status page
- 🗑️ Automatic log rotation/cleanup

## License

MIT

## Support

For issues or questions, check `logs/server_checker.log` for detailed error messages.
