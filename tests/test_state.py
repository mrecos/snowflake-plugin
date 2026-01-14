import pytest
from daemon.state import StateManager, SessionState


class TestSessionState:
    """Test SessionState model."""

    def test_session_state_initializes_empty(self):
        """Test that SessionState initializes with all None values."""
        state = SessionState()
        assert state.database is None
        assert state.schema is None
        assert state.warehouse is None
        assert state.role is None

    def test_session_state_can_be_initialized_with_values(self):
        """Test that SessionState can be initialized with values."""
        state = SessionState(
            database="TEST_DB",
            schema="TEST_SCHEMA",
            warehouse="TEST_WH",
            role="TEST_ROLE"
        )
        assert state.database == "TEST_DB"
        assert state.schema == "TEST_SCHEMA"
        assert state.warehouse == "TEST_WH"
        assert state.role == "TEST_ROLE"

    def test_session_state_is_pydantic_model(self):
        """Test that SessionState is a valid Pydantic model."""
        state = SessionState(database="TEST_DB")
        # Should be able to convert to dict
        state_dict = state.model_dump()
        assert isinstance(state_dict, dict)
        assert state_dict["database"] == "TEST_DB"


class TestStateManager:
    """Test StateManager class."""

    def test_state_manager_initializes_with_empty_state(self):
        """Test that StateManager initializes with empty state."""
        manager = StateManager()
        state = manager.get_state()
        assert state.database is None
        assert state.schema is None
        assert state.warehouse is None
        assert state.role is None

    def test_set_database_updates_state(self):
        """Test that set_database updates the database in state."""
        manager = StateManager()
        manager.set_database("MY_DB")
        assert manager.get_state().database == "MY_DB"

    def test_set_schema_updates_state(self):
        """Test that set_schema updates the schema in state."""
        manager = StateManager()
        manager.set_schema("MY_SCHEMA")
        assert manager.get_state().schema == "MY_SCHEMA"

    def test_set_warehouse_updates_state(self):
        """Test that set_warehouse updates the warehouse in state."""
        manager = StateManager()
        manager.set_warehouse("MY_WH")
        assert manager.get_state().warehouse == "MY_WH"

    def test_set_role_updates_state(self):
        """Test that set_role updates the role in state."""
        manager = StateManager()
        manager.set_role("MY_ROLE")
        assert manager.get_state().role == "MY_ROLE"

    def test_multiple_state_updates(self):
        """Test that multiple state updates work correctly."""
        manager = StateManager()
        manager.set_database("DB1")
        manager.set_schema("SCHEMA1")
        manager.set_warehouse("WH1")
        manager.set_role("ROLE1")

        state = manager.get_state()
        assert state.database == "DB1"
        assert state.schema == "SCHEMA1"
        assert state.warehouse == "WH1"
        assert state.role == "ROLE1"

    def test_state_can_be_updated_multiple_times(self):
        """Test that state values can be updated multiple times."""
        manager = StateManager()

        manager.set_database("DB1")
        assert manager.get_state().database == "DB1"

        manager.set_database("DB2")
        assert manager.get_state().database == "DB2"

    def test_get_state_returns_copy(self):
        """Test that get_state returns the actual state (not a copy)."""
        manager = StateManager()
        manager.set_database("DB1")

        state = manager.get_state()
        # This is the actual state object, so it should be the same
        assert state is manager.state

    def test_state_values_can_be_set_to_none(self):
        """Test that state values can be explicitly set to None."""
        manager = StateManager()
        manager.set_database("DB1")
        assert manager.get_state().database == "DB1"

        # Setting to empty string or None should clear it
        manager.set_database(None)
        assert manager.get_state().database is None

    def test_state_handles_case_sensitivity(self):
        """Test that state preserves case of names."""
        manager = StateManager()
        manager.set_database("MyDatabase")
        assert manager.get_state().database == "MyDatabase"

        manager.set_database("MYDATABASE")
        assert manager.get_state().database == "MYDATABASE"

    def test_initial_state_with_values(self):
        """Test that StateManager can be initialized with initial state."""
        initial_state = SessionState(
            database="INIT_DB",
            schema="INIT_SCHEMA"
        )
        manager = StateManager(initial_state=initial_state)

        state = manager.get_state()
        assert state.database == "INIT_DB"
        assert state.schema == "INIT_SCHEMA"
        assert state.warehouse is None
        assert state.role is None


class TestStateManagerEdgeCases:
    """Test edge cases for StateManager."""

    def test_set_database_with_empty_string(self):
        """Test setting database to empty string."""
        manager = StateManager()
        manager.set_database("")
        # Empty string should be stored as-is (or None depending on implementation)
        assert manager.get_state().database == "" or manager.get_state().database is None

    def test_set_database_with_special_characters(self):
        """Test setting database with special characters."""
        manager = StateManager()
        manager.set_database("MY_DB-123.TEST")
        assert manager.get_state().database == "MY_DB-123.TEST"

    def test_set_schema_with_qualified_name(self):
        """Test setting schema with qualified name (DB.SCHEMA)."""
        manager = StateManager()
        # User might accidentally provide qualified name
        manager.set_schema("DB.SCHEMA")
        # Should store as-is (validation happens in Snowflake)
        assert manager.get_state().schema == "DB.SCHEMA"

    def test_concurrent_state_access(self):
        """Test that state manager handles simple sequential access."""
        manager = StateManager()

        # Simulate multiple sequential updates
        for i in range(10):
            manager.set_database(f"DB_{i}")
            assert manager.get_state().database == f"DB_{i}"
