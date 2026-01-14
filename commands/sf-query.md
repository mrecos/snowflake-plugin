---
description: Execute SQL query via persistent Snowflake daemon connection
---

# Snowflake Query (Daemon)

Execute SELECT queries against Snowflake using persistent daemon connection.

## Usage

```bash
./bin/sf-query "SELECT * FROM my_table" [limit]
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

```bash
# Simple query
./bin/sf-query "SELECT 1 as test"

# Query with custom limit
./bin/sf-query "SELECT * FROM customers" 50

# SHOW command
./bin/sf-query "SHOW TABLES"

# Current context
./bin/sf-query "SELECT CURRENT_DATABASE(), CURRENT_SCHEMA()"
```

## Example Output

```
id | name
---------
1  | Alice
2  | Bob

✓ 2 row(s) in 0.234s
```

## Error Handling

The command will fail with helpful errors if:

- **No SQL provided**: "Error: SQL query is required"
- **Daemon won't start**: "Failed to start daemon"
- **Invalid query**: "Only read-only queries allowed: INSERT"
- **Syntax error**: Snowflake error message
- **Permission denied**: Snowflake permission error

## Implementation

The executable script is located at `bin/sf-query`.
