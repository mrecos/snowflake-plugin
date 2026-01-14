---
description: Test connection to Snowflake daemon and verify credentials
---

# Test Snowflake Daemon Connection

Check if daemon is running and can connect to Snowflake.

## Usage

```bash
./bin/sf-connect
```

## What It Does

1. Checks if the daemon is running (starts it if not)
2. Verifies Snowflake credentials are configured
3. Tests the connection by querying Snowflake version and current user
4. Reports connection status and basic info

## Example Output

```
✓ Daemon is running
  Status: healthy
  Connection count: 1
  Uptime: 5.2s

✓ Connected to Snowflake
  Version: 8.45.0
  User: YOUR_USERNAME
  Role: YOUR_ROLE
  Database: YOUR_DATABASE
  Schema: YOUR_SCHEMA
  Warehouse: YOUR_WAREHOUSE
```

## Implementation

The executable script is located at `bin/sf-connect`.
