import os
from typing import Optional
import snowflake.connector
from dotenv import load_dotenv

load_dotenv()


class SnowflakeConnection:
    """Manages a single Snowflake connection with session state."""

    def __init__(self):
        self.account = os.getenv('SNOWFLAKE_ACCOUNT')
        self.user = os.getenv('SNOWFLAKE_USER')
        self.password = os.getenv('SNOWFLAKE_PAT')
        self.warehouse = os.getenv('SNOWFLAKE_WAREHOUSE')
        self.database = os.getenv('SNOWFLAKE_DATABASE')
        self.schema = os.getenv('SNOWFLAKE_SCHEMA')
        self.role = os.getenv('SNOWFLAKE_ROLE')

        self._connection: Optional[snowflake.connector.SnowflakeConnection] = None
        self._validate_config()

    def _validate_config(self):
        """Validate required configuration."""
        required = ['SNOWFLAKE_ACCOUNT', 'SNOWFLAKE_USER', 'SNOWFLAKE_PAT']
        missing = [var for var in required if not os.getenv(var)]
        if missing:
            raise ValueError(f"Missing required env vars: {', '.join(missing)}")

    def connect(self) -> snowflake.connector.SnowflakeConnection:
        """Establish connection to Snowflake."""
        if self._connection is None or self._connection.is_closed():
            self._connection = snowflake.connector.connect(
                account=self.account,
                user=self.user,
                password=self.password,
                warehouse=self.warehouse,
                database=self.database,
                schema=self.schema,
                role=self.role
            )
        return self._connection

    def close(self):
        """Close the connection."""
        if self._connection and not self._connection.is_closed():
            self._connection.close()
            self._connection = None

    def is_healthy(self) -> bool:
        """Check if connection is active and healthy."""
        try:
            if self._connection is None or self._connection.is_closed():
                return False
            cursor = self._connection.cursor()
            cursor.execute("SELECT 1")
            cursor.close()
            return True
        except Exception:
            return False
