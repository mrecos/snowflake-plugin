import pytest
from unittest.mock import Mock, patch
from daemon.connection import SnowflakeConnection


@pytest.fixture
def mock_env(monkeypatch):
    """Set up mock environment variables for testing."""
    # Clear all Snowflake env vars first
    for var in ['SNOWFLAKE_ACCOUNT', 'SNOWFLAKE_USER', 'SNOWFLAKE_PAT',
                'SNOWFLAKE_WAREHOUSE', 'SNOWFLAKE_DATABASE', 'SNOWFLAKE_SCHEMA', 'SNOWFLAKE_ROLE']:
        monkeypatch.delenv(var, raising=False)

    # Set required vars
    monkeypatch.setenv('SNOWFLAKE_ACCOUNT', 'test_account')
    monkeypatch.setenv('SNOWFLAKE_USER', 'test_user')
    monkeypatch.setenv('SNOWFLAKE_PAT', 'test_token')


def test_connection_validation_fails_without_credentials(monkeypatch):
    """Test that connection validation fails when required env vars are missing."""
    # Clear all Snowflake env vars
    for var in ['SNOWFLAKE_ACCOUNT', 'SNOWFLAKE_USER', 'SNOWFLAKE_PAT',
                'SNOWFLAKE_WAREHOUSE', 'SNOWFLAKE_DATABASE', 'SNOWFLAKE_SCHEMA', 'SNOWFLAKE_ROLE']:
        monkeypatch.delenv(var, raising=False)

    with pytest.raises(ValueError, match="Missing required env vars"):
        SnowflakeConnection()


def test_connection_validation_succeeds(mock_env):
    """Test that connection validation succeeds with required env vars."""
    conn = SnowflakeConnection()
    assert conn.account == 'test_account'
    assert conn.user == 'test_user'
    assert conn.password == 'test_token'


def test_connection_validation_fails_with_partial_credentials(monkeypatch):
    """Test that connection validation fails with only some required env vars."""
    # Clear all Snowflake env vars first
    for var in ['SNOWFLAKE_ACCOUNT', 'SNOWFLAKE_USER', 'SNOWFLAKE_PAT',
                'SNOWFLAKE_WAREHOUSE', 'SNOWFLAKE_DATABASE', 'SNOWFLAKE_SCHEMA', 'SNOWFLAKE_ROLE']:
        monkeypatch.delenv(var, raising=False)

    # Set only some required vars
    monkeypatch.setenv('SNOWFLAKE_ACCOUNT', 'test_account')
    monkeypatch.setenv('SNOWFLAKE_USER', 'test_user')
    # Missing SNOWFLAKE_PAT

    with pytest.raises(ValueError, match="Missing required env vars"):
        SnowflakeConnection()


@patch('snowflake.connector.connect')
def test_connect_creates_connection(mock_connect, mock_env):
    """Test that connect() creates a new Snowflake connection."""
    mock_connect.return_value = Mock()
    conn = SnowflakeConnection()
    result = conn.connect()

    assert result is not None
    mock_connect.assert_called_once()

    # Verify connection parameters
    call_kwargs = mock_connect.call_args.kwargs
    assert call_kwargs['account'] == 'test_account'
    assert call_kwargs['user'] == 'test_user'
    assert call_kwargs['password'] == 'test_token'


@patch('snowflake.connector.connect')
def test_connect_reuses_existing_connection(mock_connect, mock_env):
    """Test that connect() reuses an existing active connection."""
    mock_conn = Mock()
    mock_conn.is_closed.return_value = False
    mock_connect.return_value = mock_conn

    conn = SnowflakeConnection()
    result1 = conn.connect()
    result2 = conn.connect()

    # Should only call connect once
    assert mock_connect.call_count == 1
    assert result1 is result2


@patch('snowflake.connector.connect')
def test_connect_reconnects_when_closed(mock_connect, mock_env):
    """Test that connect() creates a new connection when existing one is closed."""
    mock_conn1 = Mock()
    mock_conn1.is_closed.return_value = True
    mock_conn2 = Mock()
    mock_conn2.is_closed.return_value = False

    mock_connect.side_effect = [mock_conn1, mock_conn2]

    conn = SnowflakeConnection()
    result1 = conn.connect()
    result2 = conn.connect()

    # Should call connect twice since first connection was closed
    assert mock_connect.call_count == 2


@patch('snowflake.connector.connect')
def test_close_connection(mock_connect, mock_env):
    """Test that close() properly closes the connection."""
    mock_conn = Mock()
    mock_conn.is_closed.return_value = False
    mock_connect.return_value = mock_conn

    conn = SnowflakeConnection()
    conn.connect()
    conn.close()

    mock_conn.close.assert_called_once()


@patch('snowflake.connector.connect')
def test_is_healthy_returns_true_for_active_connection(mock_connect, mock_env):
    """Test that is_healthy() returns True for an active connection."""
    mock_cursor = Mock()
    mock_conn = Mock()
    mock_conn.is_closed.return_value = False
    mock_conn.cursor.return_value = mock_cursor
    mock_connect.return_value = mock_conn

    conn = SnowflakeConnection()
    conn.connect()

    assert conn.is_healthy() is True
    mock_cursor.execute.assert_called_once_with("SELECT 1")
    mock_cursor.close.assert_called_once()


@patch('snowflake.connector.connect')
def test_is_healthy_returns_false_for_closed_connection(mock_connect, mock_env):
    """Test that is_healthy() returns False when connection is closed."""
    mock_conn = Mock()
    mock_conn.is_closed.return_value = True
    mock_connect.return_value = mock_conn

    conn = SnowflakeConnection()
    conn.connect()

    assert conn.is_healthy() is False


@patch('snowflake.connector.connect')
def test_is_healthy_returns_false_when_query_fails(mock_connect, mock_env):
    """Test that is_healthy() returns False when health check query fails."""
    mock_cursor = Mock()
    mock_cursor.execute.side_effect = Exception("Connection lost")
    mock_conn = Mock()
    mock_conn.is_closed.return_value = False
    mock_conn.cursor.return_value = mock_cursor
    mock_connect.return_value = mock_conn

    conn = SnowflakeConnection()
    conn.connect()

    assert conn.is_healthy() is False


@patch('snowflake.connector.connect')
def test_is_healthy_returns_false_when_no_connection(mock_connect, mock_env):
    """Test that is_healthy() returns False when connection is None."""
    conn = SnowflakeConnection()
    # Don't call connect()

    assert conn.is_healthy() is False


def test_optional_config_values_set_correctly(mock_env, monkeypatch):
    """Test that optional config values (warehouse, database, schema, role) are set."""
    monkeypatch.setenv('SNOWFLAKE_WAREHOUSE', 'TEST_WH')
    monkeypatch.setenv('SNOWFLAKE_DATABASE', 'TEST_DB')
    monkeypatch.setenv('SNOWFLAKE_SCHEMA', 'TEST_SCHEMA')
    monkeypatch.setenv('SNOWFLAKE_ROLE', 'TEST_ROLE')

    conn = SnowflakeConnection()

    assert conn.warehouse == 'TEST_WH'
    assert conn.database == 'TEST_DB'
    assert conn.schema == 'TEST_SCHEMA'
    assert conn.role == 'TEST_ROLE'


def test_optional_config_values_can_be_none(mock_env):
    """Test that optional config values can be None."""
    conn = SnowflakeConnection()

    assert conn.warehouse is None
    assert conn.database is None
    assert conn.schema is None
    assert conn.role is None
