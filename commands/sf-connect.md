---
description: Test connection to Snowflake daemon and verify credentials
---

# Test Snowflake Daemon Connection

Check if daemon is running and can connect to Snowflake.

## Usage

```bash
/snowflake-daemon:sf-connect
```

## What It Does

1. Checks if the daemon is running (starts it if not)
2. Verifies Snowflake credentials are configured
3. Tests the connection by querying Snowflake version and current user
4. Reports connection status and basic info

## Example Output

```
✓ Daemon is running
✓ Connected to Snowflake
  Version: 8.45.0
  User: YOUR_USERNAME
  Role: YOUR_ROLE
  Database: YOUR_DATABASE
  Schema: YOUR_SCHEMA
  Warehouse: YOUR_WAREHOUSE
```

## Implementation

```bash
#!/usr/bin/env bash
python3 << 'PYTHON_SCRIPT'
import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from daemon.client import DaemonClient

client = DaemonClient()

# Check daemon health
health = client.health()

if health.get("status") == "unavailable":
    print("❌ Failed to start daemon")
    print(f"   Error: {health.get('error', 'Unknown error')}")
    sys.exit(1)

if health.get("status") == "error":
    print("❌ Daemon error")
    print(f"   Error: {health.get('error', 'Unknown error')}")
    sys.exit(1)

print(f"✓ Daemon is running")
print(f"  Status: {health.get('status', 'unknown')}")
print(f"  Connection count: {health.get('connection_count', 0)}")
print(f"  Uptime: {health.get('uptime_seconds', 0):.1f}s")

# Test actual Snowflake connection
result = client.query("""
    SELECT
        CURRENT_VERSION() as version,
        CURRENT_USER() as user,
        CURRENT_ROLE() as role,
        CURRENT_DATABASE() as database,
        CURRENT_SCHEMA() as schema,
        CURRENT_WAREHOUSE() as warehouse
""")

if not result.get('success'):
    print("\n❌ Connection failed")
    print(f"   Error: {result.get('error', 'Unknown error')}")
    sys.exit(1)

# Extract connection info
data = result.get('data', [[None] * 6])[0]
version, user, role, database, schema, warehouse = data

print("\n✓ Connected to Snowflake")
print(f"  Version: {version}")
print(f"  User: {user}")
print(f"  Role: {role}")
print(f"  Database: {database if database else '(not set)'}")
print(f"  Schema: {schema if schema else '(not set)'}")
print(f"  Warehouse: {warehouse if warehouse else '(not set)'}")

PYTHON_SCRIPT
```
