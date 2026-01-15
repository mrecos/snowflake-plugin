"""SQL query validators for different permission levels."""
from abc import ABC, abstractmethod
from typing import Tuple, Optional, List


class BaseValidator(ABC):
    """Base class for SQL query validators."""

    @abstractmethod
    def validate(self, sql: str) -> Tuple[bool, Optional[str]]:
        """
        Validate SQL query.

        Returns:
            Tuple of (is_valid, error_message)
            - (True, None) if query is valid
            - (False, error_message) if query is invalid
        """
        pass


class ReadOnlyValidator(BaseValidator):
    """Validator that allows only read-only queries."""

    ALLOWED_COMMANDS = [
        'SELECT',
        'WITH',      # Common Table Expressions
        'SHOW',      # SHOW TABLES, SHOW DATABASES, etc.
        'DESCRIBE',
        'DESC',
        'USE',       # USE DATABASE, USE SCHEMA, etc.
        'LIST',      # LIST @stage
        'GET',       # GET @stage (read-only operation)
    ]

    def validate(self, sql: str) -> Tuple[bool, Optional[str]]:
        """Validate that query is read-only."""
        sql_upper = sql.strip().upper()

        if not sql_upper:
            return False, "Empty query"

        # Check if query starts with allowed command
        for allowed_cmd in self.ALLOWED_COMMANDS:
            if sql_upper.startswith(allowed_cmd):
                return True, None

        # Extract the command for error message
        command = sql_upper.split()[0] if sql_upper else "UNKNOWN"
        return False, f"Only read-only queries allowed. '{command}' is not permitted."


class DMLValidator(BaseValidator):
    """Validator that allows DML operations (INSERT, UPDATE, DELETE)."""

    ALLOWED_COMMANDS = [
        # Read-only commands
        'SELECT',
        'WITH',
        'SHOW',
        'DESCRIBE',
        'DESC',
        'USE',
        'LIST',
        'GET',
        # DML commands
        'INSERT',
        'UPDATE',
        'DELETE',
        'MERGE',     # MERGE statement
        'COPY',      # COPY INTO (data loading)
    ]

    def validate(self, sql: str) -> Tuple[bool, Optional[str]]:
        """Validate that query is a read or DML operation."""
        sql_upper = sql.strip().upper()

        if not sql_upper:
            return False, "Empty query"

        # Check if query starts with allowed command
        for allowed_cmd in self.ALLOWED_COMMANDS:
            if sql_upper.startswith(allowed_cmd):
                return True, None

        # Extract the command for error message
        command = sql_upper.split()[0] if sql_upper else "UNKNOWN"
        return False, f"Command '{command}' is not permitted. Only read and DML operations allowed."


class DDLValidator(BaseValidator):
    """Validator that allows DDL operations (CREATE, DROP, ALTER)."""

    ALLOWED_COMMANDS = [
        # Read-only commands
        'SELECT',
        'WITH',
        'SHOW',
        'DESCRIBE',
        'DESC',
        'USE',
        'LIST',
        'GET',
        # DDL commands
        'CREATE',
        'DROP',
        'ALTER',
        'TRUNCATE',
        'RENAME',
        'COMMENT',
    ]

    def validate(self, sql: str) -> Tuple[bool, Optional[str]]:
        """Validate that query is a read or DDL operation."""
        sql_upper = sql.strip().upper()

        if not sql_upper:
            return False, "Empty query"

        # Check if query starts with allowed command
        for allowed_cmd in self.ALLOWED_COMMANDS:
            if sql_upper.startswith(allowed_cmd):
                return True, None

        # Extract the command for error message
        command = sql_upper.split()[0] if sql_upper else "UNKNOWN"
        return False, f"Command '{command}' is not permitted. Only read and DDL operations allowed."


class WriteValidator(BaseValidator):
    """Validator that allows all operations (read, DML, and DDL)."""

    ALLOWED_COMMANDS = [
        # Read-only commands
        'SELECT',
        'WITH',
        'SHOW',
        'DESCRIBE',
        'DESC',
        'USE',
        'LIST',
        'GET',
        # DML commands
        'INSERT',
        'UPDATE',
        'DELETE',
        'MERGE',
        'COPY',
        # DDL commands
        'CREATE',
        'DROP',
        'ALTER',
        'TRUNCATE',
        'RENAME',
        'COMMENT',
        # Transaction control
        'BEGIN',
        'COMMIT',
        'ROLLBACK',
        'START',     # START TRANSACTION
        # Other
        'GRANT',
        'REVOKE',
        'CALL',      # Stored procedures
        'EXECUTE',   # Execute immediate
    ]

    DANGEROUS_COMMANDS = [
        'DROP DATABASE',
        'DROP SCHEMA',
        'TRUNCATE',
        'DELETE FROM',
    ]

    def validate(self, sql: str) -> Tuple[bool, Optional[str]]:
        """
        Validate that query is allowed.

        Allows all operations but provides warnings for dangerous commands.
        """
        sql_upper = sql.strip().upper()

        if not sql_upper:
            return False, "Empty query"

        # Check if query starts with allowed command
        for allowed_cmd in self.ALLOWED_COMMANDS:
            if sql_upper.startswith(allowed_cmd):
                # Check for dangerous commands and add warning in the future
                # For now, all commands are allowed
                return True, None

        # Extract the command for error message
        command = sql_upper.split()[0] if sql_upper else "UNKNOWN"
        return False, f"Command '{command}' is not recognized as a valid SQL command."


class TransactionValidator(BaseValidator):
    """Validator for transaction control commands."""

    ALLOWED_COMMANDS = [
        'BEGIN',
        'COMMIT',
        'ROLLBACK',
        'START',     # START TRANSACTION
    ]

    def validate(self, sql: str) -> Tuple[bool, Optional[str]]:
        """Validate that query is a transaction control command."""
        sql_upper = sql.strip().upper()

        if not sql_upper:
            return False, "Empty query"

        # Check if query starts with allowed command
        for allowed_cmd in self.ALLOWED_COMMANDS:
            if sql_upper.startswith(allowed_cmd):
                return True, None

        # Extract the command for error message
        command = sql_upper.split()[0] if sql_upper else "UNKNOWN"
        return False, f"Command '{command}' is not a transaction control command."
