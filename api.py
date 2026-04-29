"""
Smart Server Monitoring System - REST API
Serves read-only dashboard data from the SQLite database
"""

import json
from flask import Flask, jsonify
from flask_cors import CORS
import sqlite3
import os
import database as db

app = Flask(__name__)
# Enable CORS for all routes (in production, restrict origins)
CORS(app)

def get_db_connection():
    """Get a fresh DB connection for Flask requests"""
    try:
        conn = sqlite3.connect(db.DB_FILE)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        print(f"Flask DB Connection error: {e}")
        return None

@app.route('/api/status', methods=['GET'])
def get_overall_status():
    """Returns aggregated system health"""
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, last_status, last_check_time FROM servers")
        servers = cursor.fetchall()
        
        total_servers = len(servers)
        if total_servers == 0:
            return jsonify({"status": "Unknown", "message": "No servers configured", "total": 0})
            
        down_servers = sum(1 for s in servers if s['last_status'] == 'DOWN')
        warning_servers = sum(1 for s in servers if s['last_status'] == 'WARNING')
        
        if down_servers == total_servers:
            overall_status = "Major Outage"
        elif down_servers > 0:
            overall_status = "Partial Outage"
        elif warning_servers > 0:
            overall_status = "Degraded Performance"
        else:
            overall_status = "All Systems Operational"
            
        return jsonify({
            "status": overall_status,
            "total_servers": total_servers,
            "down_servers": down_servers,
            "warning_servers": warning_servers
        })
    finally:
        conn.close()

@app.route('/api/servers', methods=['GET'])
def get_servers():
    """Returns a list of all servers with their current state & uptime"""
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, url, created_at, last_check_time, last_status FROM servers")
        servers = [dict(row) for row in cursor.fetchall()]
        
        # Hydrate with uptime
        for server in servers:
            uptime = db.calculate_uptime_percentage(server['id'], days=1)
            server['uptime_24h'] = uptime if uptime is not None else 0.0
            
        return jsonify(servers)
    finally:
        conn.close()

@app.route('/api/metrics/<int:server_id>', methods=['GET'])
def get_server_metrics(server_id):
    """Returns the last 24 hours of metrics for a server"""
    # Specifically targeting response times and status
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
        
    try:
        cursor = conn.cursor()
        # Get checks from the last 24 hours, ordered chronologically
        cursor.execute('''
            SELECT timestamp, status, response_time, http_status_code 
            FROM monitoring_checks 
            WHERE server_id = ? AND timestamp > datetime('now', '-1 day')
            ORDER BY timestamp ASC
        ''', (server_id,))
        
        metrics = [dict(row) for row in cursor.fetchall()]
        return jsonify(metrics)
    finally:
        conn.close()

if __name__ == '__main__':
    # Retrieve port from config.json if available
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
            port = config.get("api_port", 5000)
    except Exception:
        port = 5000
    
    print(f"🚀 Starting Dashboard REST API on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
