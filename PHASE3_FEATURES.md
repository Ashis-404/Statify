# 🎯 Phase 3: User-Driven Monitoring Platform (Statify)

## Overview

The Smart Server Monitoring System has been transformed from a **hardcoded monitoring tool** into a **user-driven platform** where users can dynamically add servers, receive personalized alerts, and view real-time status through an intuitive dashboard.

---

## 🚀 Core Transformation

### Before (Phase 1 & 2)
- ❌ Servers configured in JSON files
- ❌ Global email for all alerts
- ❌ Manual configuration updates

### After (Phase 3)
- ✅ **Dynamic server addition** via web form
- ✅ **User-specific emails** per server
- ✅ **Real-time dashboard** with auto-refresh
- ✅ **Rich monitoring history** with charts
- ✅ **One-click server deletion**

---

## 📋 Feature Documentation

### 1. **Add Server (Dynamic Input)**

#### UI Location
- Dashboard form at the top labeled "➕ Add New Server"

#### Input Fields
| Field | Type | Validation | Example |
|-------|------|-----------|---------|
| Server Name | Text | 2+ characters, unique | "My Website" |
| Server URL | URL | Must start with `http://` or `https://` | `https://example.com` |
| Alert Email | Email | Valid email format | `ashis9903550174@gmail.com` |

#### Backend API
```http
POST /api/servers
Content-Type: application/json

{
  "name": "My Website",
  "url": "https://example.com",
  "email": "ashis9903550174@gmail.com"
}
```

#### Response
**Success (201):**
```json
{
  "message": "Server added successfully",
  "server_id": 1
}
```

**Error (400):**
```json
{
  "error": "URL must start with http:// or https://"
}
```

#### Error Handling
- Toast notification shows success or error message
- Inline form validation before submission
- Server-side validation prevents duplicates and invalid data

---

### 2. **View All Servers**

#### UI Location
- Main dashboard table after the "Add New Server" form

#### Table Columns
| Column | Description | Data Type |
|--------|-------------|-----------|
| **Name** | Server name + clickable URL | String |
| **Status** | Current state badge (🟢 UP / 🔴 DOWN / 🟡 WARNING) | Badge |
| **Response Time** | Load indicator bar | Visual |
| **Last Checked** | Timestamp of last health check | Time |
| **Uptime (24h)** | Percentage bar + value | Progress Bar |
| **Email** | Alert recipient email | Email |
| **Actions** | History & Delete buttons | Buttons |

#### Backend API
```http
GET /api/servers
```

**Response (200):**
```json
[
  {
    "id": 1,
    "name": "My Website",
    "url": "https://example.com",
    "email": "ashis9903550174@gmail.com",
    "last_status": "UP",
    "last_check_time": "2026-04-29T10:30:45",
    "uptime_24h": 99.5
  }
]
```

---

### 3. **Real-Time Status Updates**

#### Auto-Refresh Behavior
- Dashboard refreshes **every 10 seconds**
- Status indicators update live:
  - 🟢 **UP** (Green) - Server responding normally
  - 🟡 **WARNING** (Yellow) - Performance degradation
  - 🔴 **DOWN** (Red) - No response / Timeout / Error

#### Overall System Status
- Aggregated indicator at the top of the dashboard
- Shows:
  - "All Systems Operational" ✅
  - "Partial Outage" ⚠️
  - "Major Outage" ❌
  - "Degraded Performance" 🟡

#### Backend API
```http
GET /api/status
```

**Response:**
```json
{
  "status": "Partial Outage",
  "total_servers": 4,
  "down_servers": 1,
  "warning_servers": 0
}
```

---

### 4. **Email Alerts (User-Specific)**

#### Alert Logic
Each server now has its own **dedicated email address** for receiving alerts.

#### When Alerts Are Sent
1. **DOWN Alert** 🔴
   - Triggered when server transitions from UP → DOWN
   - Contains error details and timestamp
   - Subject: `⚠️ ALERT: {ServerName} is DOWN`

2. **UP Recovery Alert** ✅
   - Triggered when server transitions from DOWN → UP
   - Confirms recovery and response time
   - Subject: `✅ RECOVERED: {ServerName} is UP`

3. **WARNING Alert** (Disabled)
   - No alert sent for WARNING status by default
   - Prevents alert fatigue

#### Anti-Spam Protection
- Same alert type not sent twice within **5 minutes**
- Reduces duplicate email notifications

#### Backend Implementation
```python
# From alert_manager.py
alert_manager.attempt_alert(
    config,
    server_id,
    server_name,
    user_email,  # Now per-server
    alert_type,
    alert_details,
    cooldown_minutes=5
)
```

#### Database Schema
```sql
ALTER TABLE servers ADD COLUMN email TEXT NOT NULL DEFAULT 'ashis9903550174@gmail.com'
```

---

### 5. **Delete Server**

#### UI Location
- Red "🗑️ Delete" button in each server row

#### Behavior
1. Click delete button
2. Confirmation dialog appears
3. If confirmed:
   - Server record deleted
   - All monitoring records deleted
   - All alerts cleared
   - Dashboard updates automatically

#### Backend API
```http
DELETE /api/servers/<id>
```

**Response (200):**
```json
{
  "message": "Server deleted successfully"
}
```

---

### 6. **Server History (Monitoring History)**

#### UI Location
- Blue "📊 History" button in each server row

#### What It Shows
- Modal with last 100 monitoring checks
- Chronological order (newest first)
- Columns:
  - **Timestamp** - When check was performed
  - **Status** - UP / DOWN / WARNING
  - **Response Time** - In seconds
  - **HTTP Code** - e.g., 200, 500, timeout

#### Backend API
```http
GET /api/history/<server_id>
```

**Response:**
```json
{
  "server": {
    "id": 1,
    "name": "My Website",
    "url": "https://example.com"
  },
  "history": [
    {
      "timestamp": "2026-04-29T10:30:45",
      "status": "UP",
      "response_time": 0.234,
      "http_status_code": 200
    }
  ]
}
```

---

## 🗄️ Database Schema Updates

### Servers Table
```sql
CREATE TABLE servers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    url TEXT NOT NULL,
    email TEXT NOT NULL DEFAULT 'ashis9903550174@gmail.com',  -- NEW
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_check_time TIMESTAMP,
    last_status TEXT CHECK(last_status IN ('UP', 'DOWN', 'WARNING'))
)
```

### Migration
- Existing databases automatically migrated
- `email` column added with default value
- No data loss

---

## 🎨 UI/UX Design Details

### Layout Structure

```
┌─────────────────────────────────────────────┐
│ Header: "🔍 Server Monitor"                 │
│ Subtitle: Real-time monitoring              │
│ Last updated: [timestamp]                   │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│ Overall Status Card                          │
│ Status: "All Systems Operational" ✅         │
│ 4 services monitored • 0 down                │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│ ➕ Add New Server Form                       │
│ [Server Name] [URL] [Email] [Add Button]    │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│ 📋 Monitored Services Table                  │
│ Name | Status | Response | Last Check | ... │
│ ─────────────────────────────────────────── │
│ Server 1 ...                                 │
│ Server 2 ...                                 │
└─────────────────────────────────────────────┘

[Toast Notifications - Bottom Right]
```

### Color Scheme
- **Green (#10B981)** - UP / Success
- **Red (#EF4444)** - DOWN / Error
- **Yellow (#F59E0B)** - WARNING / Caution
- **Blue (#3B82F6)** - Primary / Interactive
- **Gray (#6B7280)** - Neutral / Secondary

### Animations
- ✨ Smooth fade-in for toast notifications
- 🔄 Rotation spinner while loading
- 📊 Progress bars for uptime visualization
- 🎯 Hover effects on buttons and rows

### Typography
- **Headings:** Bold, larger font weights (600-700)
- **Body:** Medium weight (400-500)
- **Labels:** Small, medium weight (500)

---

## 🔐 Validation & Security

### Input Validation

#### Server Name
- Min length: 2 characters
- Max length: 255 characters (DB limit)
- Must be unique
- Client-side validation shows error inline

#### URL Validation
- Must start with `http://` or `https://`
- Server-side validation prevents invalid URLs
- Duplicate URLs prevented

#### Email Validation
- Must match regex: `^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`
- Required field
- Validated both client and server-side

### Data Protection
- Sanitized user input on both client and server
- SQLite parameterized queries prevent SQL injection
- CORS enabled for API requests
- Email addresses stored safely (no encryption needed for dynamic system)

---

## 📊 Monitoring Workflow

```
User Action          Backend Logic           Frontend Update
───────────────────────────────────────────────────────────

1. Add Server   →  POST /api/servers   →   Form clears
                └─ DB insert           └─ Toast shows "Added successfully"
                └─ Validation          └─ Table refreshes

2. Monitor Runs →  Continuous loop     →   Every 10s: GET /api/servers
                └─ HTTP check          └─ Status colors update
                └─ DB log check        └─ Last checked time updates
                └─ Send email alert    └─ Uptime % recalculates

3. View History →  GET /api/history    →   Modal shows last 100 checks
                └─ Query DB            └─ Timestamps formatted
                └─ Format response     └─ Color-coded statuses

4. Delete Server→  DELETE /api/servers →   Server row disappears
                └─ Delete all records  └─ Toast confirms deletion
                └─ Clear alerts        └─ Dashboard refreshes
```

---

## 🧪 Testing the User Flow

### Test Scenario 1: Add and Monitor Server
```bash
1. Open dashboard at http://localhost:5173
2. Fill form:
   - Name: "Test API"
   - URL: "https://httpbin.org/status/200"
   - Email: "your-email@example.com"
3. Click "Add Server"
4. Observe:
   ✓ Toast shows "Server added successfully!"
   ✓ Table shows new row with status "UP"
   ✓ Uptime starts at 100%
   ✓ Last check time updates
```

### Test Scenario 2: Receive Alert
```bash
1. Add server with your real email
2. Wait 30 seconds for monitoring
3. Server status changes to DOWN
4. Check email for alert within 2 minutes
5. Status changes back to UP
6. Check email for recovery alert
```

### Test Scenario 3: View History
```bash
1. Click "📊 History" on a server
2. Modal opens showing last 100 checks
3. Columns show timestamp, status, response time
4. Close modal by clicking "Close" or ✕
```

### Test Scenario 4: Delete Server
```bash
1. Click "🗑️ Delete" on a server
2. Confirm deletion in dialog
3. Server immediately removed from table
4. Toast shows "Server deleted successfully"
```

---

## 🚀 Running the Complete System

### Terminal 1: Monitoring Engine
```bash
python main.py
```
- Continuously checks all servers
- Sends emails on status changes
- Updates database every 60 seconds (configurable)

### Terminal 2: REST API
```bash
python api.py
```
- Runs on `http://localhost:5000`
- Serves all dashboard endpoints
- Handles POST/DELETE for dynamic servers

### Terminal 3: React Dashboard
```bash
cd frontend
npm run dev
```
- Runs on `http://localhost:5173`
- Auto-refreshes every 10 seconds
- Shows real-time status and history

---

## 📈 Files Modified & Created

### Modified Files
- ✏️ `database.py` - Added email column & new methods
- ✏️ `api.py` - Added POST, DELETE, history endpoints
- ✏️ `alert_manager.py` - Updated to use per-server emails
- ✏️ `main.py` - Passes server-specific emails to alerts

### New Files
- 📄 `frontend/src/components/AddServerForm.tsx` - Form component
- 📄 `frontend/src/components/ServerTable.tsx` - Table component
- 📄 `frontend/src/components/Toast.tsx` - Notification component
- 📄 `frontend/src/components/HistoryModal.tsx` - History viewer

---

## 🎯 Success Criteria (All ✅)

- ✅ User can add server dynamically via form
- ✅ Status updates in real-time (every 10s)
- ✅ Alerts sent to user-specific emails
- ✅ UI is clean, responsive, and uses Tailwind CSS
- ✅ Delete functionality works seamlessly
- ✅ History viewing shows 100 last checks
- ✅ Toast notifications confirm all actions
- ✅ Database migration handles existing data
- ✅ Input validation prevents invalid data
- ✅ Full user workflow is intuitive

---

## 🔮 Future Enhancements

- Multiple emails per server
- User authentication & multi-tenancy
- Public status page (unauthenticated)
- Graph analytics with charts (Chart.js)
- Webhook integrations (Slack, Discord)
- SMS alerts
- Custom alert thresholds
- Server groups/categories

