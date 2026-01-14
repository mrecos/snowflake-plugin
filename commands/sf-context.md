---
description: Show current Snowflake session context (database, schema, warehouse, role)
---

# Show Snowflake Context

Display the current session context maintained by the daemon.

## Usage

```bash
./bin/sf-context
```

## What It Does

Shows the current Snowflake session state that the daemon is tracking:
- **Database**: Current active database
- **Schema**: Current active schema
- **Warehouse**: Current active warehouse
- **Role**: Current active role

## Example Output

```
Current Snowflake Session Context:

  Database:  CLAUDE_DB
  Schema:    PUBLIC
  Warehouse: COMPUTE_WH
  Role:      SYSADMIN
```

If no context has been set:
```
Current Snowflake Session Context:

  Database:  (not set)
  Schema:    (not set)
  Warehouse: (not set)
  Role:      (not set)
```

## How Session State Works

The daemon tracks your session context when you execute USE commands:

```bash
# Switch database
./bin/sf-query "USE DATABASE CLAUDE_DB"

# Switch schema
./bin/sf-query "USE SCHEMA PUBLIC"

# Switch warehouse
./bin/sf-query "USE WAREHOUSE COMPUTE_WH"

# Switch role
./bin/sf-query "USE ROLE SYSADMIN"

# Check current context
./bin/sf-context
```

The context persists across query executions, so you don't need to specify the full path every time.

## Implementation

The executable script is located at `bin/sf-context`.
