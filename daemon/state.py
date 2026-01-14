from typing import Optional
from pydantic import BaseModel, ConfigDict


class SessionState(BaseModel):
    """Represents the current Snowflake session state."""
    model_config = ConfigDict(protected_namespaces=())

    database: Optional[str] = None
    schema: Optional[str] = None
    warehouse: Optional[str] = None
    role: Optional[str] = None


class StateManager:
    """Manages session state for Snowflake connection."""

    def __init__(self, initial_state: Optional[SessionState] = None):
        """Initialize state manager with optional initial state."""
        self.state = initial_state if initial_state is not None else SessionState()

    def get_state(self) -> SessionState:
        """Get current session state."""
        return self.state

    def set_database(self, database: Optional[str]):
        """Set current database."""
        self.state.database = database if database else None

    def set_schema(self, schema: Optional[str]):
        """Set current schema."""
        self.state.schema = schema if schema else None

    def set_warehouse(self, warehouse: Optional[str]):
        """Set current warehouse."""
        self.state.warehouse = warehouse if warehouse else None

    def set_role(self, role: Optional[str]):
        """Set current role."""
        self.state.role = role if role else None
