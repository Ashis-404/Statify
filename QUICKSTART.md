# 🚀 Quick Reference Card

## Start Monitoring in 30 Seconds

### Install
```bash
pip install -r requirements.txt
```

### Configure
```bash
cp servers.json.example servers.json
cp config.json.example config.json
# Edit both files with your servers and SMTP details
```

### Run
```bash
python main.py
```

Done! System runs continuously. Press `Ctrl+C` to stop.

---

## Configuration Files

### servers.json — Your Servers
```json
{
  "servers": [
    {"name": "My API", "url": "https://api.example.com"},
    {"name": "My Website", "url": "https://example.com"}
  ]
}
```

### config.json — System Settings
```json
{
  "check_interval": 60,
  "response_timeout": 2,
  "smtp": {
    "host": "smtp.gmail.com",
    "port": 587,
    "username": "your@gmail.com",
    "password": "app-password",
    "from_email": "your@gmail.com",
    "to_email": "recipient@gmail.com"
  }
}
```

---

## What You'll See

```
🟢 Server UP: 0.234s          ← Server is healthy
🔴 Server DOWN: HTTP 500       ← Server is offline
⚡ Status change: UP → DOWN    ← Alert being sent
📊 Uptime: 98.5% (24h)         ← Historical metric
```

---

## Database & Logs

- `server_monitor.db` — SQLite database (auto-created)
- `logs/server_checker.log` — System log file

### Query Database
```bash
sqlite3 server_monitor.db "SELECT * FROM monitoring_checks LIMIT 10;"
```

### View Logs
```bash
tail -f logs/server_checker.log
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| No emails sending | Check SMTP config in config.json |
| Database locked | Only one main.py instance allowed |
| Servers not showing | Restart main.py after editing servers.json |
| Always showing DOWN | Increase response_timeout in config.json |

---

## Email Setup (Gmail Example)

1. Enable 2-Factor Authentication
2. Generate App Password: https://myaccount.google.com/apppasswords
3. Use in config.json:
   - `username`: your@gmail.com
   - `password`: 16-character app password

---

## Status Rules

| Condition | Result |
|-----------|--------|
| HTTP 200 + <2s response | ✅ UP |
| HTTP 500+ | ❌ DOWN |
| Timeout | ❌ DOWN |
| Connection error | ❌ DOWN |

---

## Files in the Package

**Core:**
- main.py, database.py, health_checker.py, alert_manager.py, uptime_calculator.py, logger.py

**Config:**
- servers.json, config.json, servers.json.example, config.json.example

**Docs:**
- README.md, SETUP.md, IMPLEMENTATION_SUMMARY.md (this file)

**Auto-created:**
- logs/ (directory), server_monitor.db (SQLite)

---

## Useful Commands

```bash
# Start monitoring
python main.py

# Verify database
python verify_db.py

# View recent logs
tail -20 logs/server_checker.log

# Query database
sqlite3 server_monitor.db ".schema"
sqlite3 server_monitor.db "SELECT * FROM servers;"
```

---

## Key Features Active Now

✅ Monitors multiple servers every 60s
✅ Logs all checks to SQLite
✅ Sends email alerts on status change
✅ Calculates uptime percentages
✅ Anti-spam (no duplicate emails)
✅ Graceful error handling
✅ Continuous operation

---

**Ready to deploy! Run `python main.py` 🎯**
