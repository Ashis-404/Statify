"""
Smart Server Monitoring System - Main Scheduler
Continuously monitors server health, logs checks, detects state changes, and sends alerts
"""

import json
import time
import sys
from datetime import datetime
import database as db
import health_checker
import alert_manager
import uptime_calculator
import logger as logger_module


CONFIG_FILE = "config.json"
SERVERS_FILE = "servers.json"


def load_config() -> dict:
    """Load configuration from config.json"""
    try:
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
        print(f"✓ Config loaded: {CONFIG_FILE}")
        return config
    except FileNotFoundError:
        print(f"✗ Config file not found: {CONFIG_FILE}")
        print(f"  Please copy {CONFIG_FILE}.example to {CONFIG_FILE} and configure it")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"✗ Invalid JSON in {CONFIG_FILE}: {e}")
        sys.exit(1)


def load_servers() -> list:
    """Load servers from servers.json"""
    try:
        with open(SERVERS_FILE, 'r') as f:
            data = json.load(f)
        
        servers = data.get("servers", [])
        print(f"✓ Servers loaded: {len(servers)} server(s)")
        
        for server in servers:
            print(f"  - {server.get('name', 'Unknown')} ({server.get('url', 'N/A')})")
        
        return servers
    except FileNotFoundError:
        print(f"✗ Servers file not found: {SERVERS_FILE}")
        print(f"  Please copy {SERVERS_FILE}.example to {SERVERS_FILE} and add your servers")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"✗ Invalid JSON in {SERVERS_FILE}: {e}")
        sys.exit(1)


def initialize_servers_in_db(servers: list):
    """Add servers to database if not already present"""
    for server in servers:
        name = server.get("name")
        url = server.get("url")
        
        if not name or not url:
            print(f"✗ Invalid server entry (missing name or url): {server}")
            continue
        
        # Check if server already exists
        existing_servers = db.get_all_servers()
        server_exists = any(s["name"] == name for s in existing_servers)
        
        if not server_exists:
            db.add_server(name, url)


def monitor_servers(config: dict, servers: list, log):
    """Main monitoring loop"""
    
    check_interval = config.get("check_interval", 60)
    cooldown_minutes = config.get("alert_cooldown_minutes", 5)
    
    print(f"\n🚀 Starting monitoring (interval: {check_interval}s, alert cooldown: {cooldown_minutes}m)")
    print("=" * 60)
    print("Press Ctrl+C to stop\n")
    
    try:
        iteration = 0
        last_purge_time = 0
        purge_interval = 86400  # 24 hours
        
        while True:
            iteration += 1
            current_time = time.time()
            if current_time - last_purge_time > purge_interval:
                db.purge_old_records(days=30)
                last_purge_time = current_time

            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"\n[Check #{iteration}] {timestamp}")
            print("-" * 60)
            
            # Fetch latest servers from database
            db_servers = db.get_all_servers()
            
            for server in db_servers:
                server_id = server["id"]
                server_name = server["name"]
                server_url = server["url"]
                
                # Check server health
                check_result = health_checker.check_server_health(
                    server_url,
                    config.get("response_timeout", 2)
                )
                
                # Print result
                print(health_checker.format_health_check_result(check_result, server_name))
                
                # Log check to database
                db.log_check(
                    server_id=server_id,
                    status=check_result["status"],
                    response_time=check_result["response_time"],
                    http_status_code=check_result["http_status_code"],
                    error_message=check_result["error"]
                )
                
                # Get previous status
                previous_status = db.get_last_status(server_id)
                current_status = check_result["status"]
                
                # Detect status transition
                if previous_status != current_status:
                    print(f"  ⚡ Status change: {previous_status or 'UNKNOWN'} → {current_status}")
                    
                    # Prepare alert details
                    alert_details = {
                        "url": server_url,
                        "response_time": check_result["response_time"],
                        "error": check_result["error"]
                    }
                    
                    # Send alert
                    alert_manager.attempt_alert(
                        config,
                        server_id,
                        server_name,
                        current_status,
                        alert_details,
                        cooldown_minutes
                    )
            
            # Print uptime stats
            print("\n📊 Uptime Summary:")
            for server in db_servers:
                uptime = db.calculate_uptime_percentage(server["id"], days=1)
                if uptime is not None:
                    print(f"  {server['name']}: {uptime}% (24h)")
            
            print(f"\n⏳ Next check in {check_interval} seconds...", end="", flush=True)
            
            # Sleep before next iteration
            time.sleep(check_interval)
    
    except KeyboardInterrupt:
        print("\n\n" + "=" * 60)
        print("🛑 Monitoring stopped by user")
        print("=" * 60)


def main():
    """Main entry point"""
    
    print("\n" + "=" * 60)
    print("🔍 Smart Server Monitoring System")
    print("=" * 60)
    
    # Setup logging
    log = logger_module.setup_logger()
    log.info("System started")
    
    # Load configuration
    config = load_config()
    
    # Load servers from config file
    servers = load_servers()
    
    if not servers:
        print("✗ No servers configured")
        sys.exit(1)
    
    # Initialize database
    db.init_db()
    
    # Add servers to database
    initialize_servers_in_db(servers)
    
    # Start monitoring loop
    try:
        monitor_servers(config, servers, log)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        log.error(f"Unexpected error: {e}")
        sys.exit(1)
    finally:
        log.info("System stopped")


if __name__ == "__main__":
    main()
