---
description: Execute SQL query via persistent Snowflake daemon connection
---

# Snowflake Query (Daemon)

Execute SELECT queries against Snowflake using persistent daemon connection.

## Usage

```bash
/snowflake-daemon:sf-query <sql>
/snowflake-daemon:sf-query <sql> [limit]
```

## Arguments

- `sql` (required): SQL query to execute (SELECT, SHOW, DESCRIBE, DESC)
- `limit` (optional): Maximum number of rows to return (default: 100)

## Features

- **Read-only queries**: Only SELECT, SHOW, DESCRIBE, DESC are allowed
- **Automatic LIMIT**: Adds LIMIT clause to SELECT queries if not present
- **Persistent connection**: Uses daemon's persistent connection (context preserved)
- **Auto-start**: Starts daemon automatically if not running
- **Formatted output**: Returns results in a readable table format

## Examples

### Basic query

```bash
/snowflake-daemon:sf-query "SELECT 1 as test"
```

### Query with custom limit

```bash
/snowflake-daemon:sf-query "SELECT * FROM customers" 50
```

### SHOW command

```bash
/snowflake-daemon:sf-query "SHOW TABLES"
```

### Current context

```bash
/snowflake-daemon:sf-query "SELECT CURRENT_DATABASE(), CURRENT_SCHEMA()"
```

### Query from specific database

```bash
/snowflake-daemon:sf-query "SELECT COUNT(*) FROM MYDB.MYSCHEMA.MYTABLE"
```

## Implementation

```bash
#!/usr/bin/env bash

# Get SQL from first argument (required)
SQL="$1"
# Get limit from second argument (optional, defaults to 100)
LIMIT="${2:-100}"

if [ -z "$SQL" ]; then
    echo "Error: SQL query is required"
    echo "Usage: /snowflake-daemon:sf-query <sql> [limit]"
    exit 1
fi

python3 << PYTHON_SCRIPT
import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from daemon.client import DaemonClient

client = DaemonClient()
sql = """$SQL"""
limit = int("$LIMIT")

result = client.query(sql, limit=limit)

if not result.get('success'):
    print(f"❌ Query failed: {result.get('error', 'Unknown error')}")
    sys.exit(1)

# Display results
data = result.get('data', [])
columns = result.get('columns', [])
row_count = result.get('row_count', 0)
exec_time = result.get('execution_time', 0)

if row_count == 0:
    print("No results returned")
else:
    # Print column headers
    if columns:
        header = " | ".join(str(col) for col in columns)
        print(header)
        print("-" * len(header))

    # Print data rows
    for row in data:
        print(" | ".join(str(val) if val is not None else "NULL" for val in row))

print(f"\n✓ {row_count} row(s) in {exec_time:.3f}s")

PYTHON_SCRIPT
```

## Error Handling

The command will fail with helpful errors if:

- **No SQL provided**: "Error: SQL query is required"
- **Daemon won't start**: "Failed to start daemon"
- **Invalid query**: "Only read-only queries allowed: INSERT"
- **Syntax error**: Snowflake error message
- **Permission denied**: Snowflake permission error
- **Table not found**: "Object does not exist"

## Notes

- Write operations (INSERT, UPDATE, DELETE, etc.) are blocked for safety
- SELECT queries automatically get a LIMIT clause if not specified
- SHOW/DESCRIBE commands don't get LIMIT added
- The daemon maintains a persistent connection, so context is preserved
- Query timeout is 5 minutes for long-running queries

## See Also

- `/snowflake-daemon:sf-connect` - Test connection
- `INTEGRATION_TEST.md` - Full testing guide
