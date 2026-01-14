import pytest
from unittest.mock import Mock, patch, MagicMock
from daemon.client import DaemonClient
import httpx


@pytest.fixture
def client():
    """Create a DaemonClient instance."""
    return DaemonClient()


class TestIsRunning:
    """Test daemon running detection."""

    @patch('httpx.get')
    def test_is_running_returns_true_when_daemon_responds(self, mock_get, client):
        """Test that is_running returns True when daemon responds with 200."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        assert client.is_running() is True
        mock_get.assert_called_once_with("http://127.0.0.1:8765/health", timeout=1.0)

    @patch('httpx.get')
    def test_is_running_returns_false_on_connection_error(self, mock_get, client):
        """Test that is_running returns False on connection error."""
        mock_get.side_effect = httpx.ConnectError("Connection refused")

        assert client.is_running() is False

    @patch('httpx.get')
    def test_is_running_returns_false_on_timeout(self, mock_get, client):
        """Test that is_running returns False on timeout."""
        mock_get.side_effect = httpx.TimeoutException("Timeout")

        assert client.is_running() is False

    @patch('httpx.get')
    def test_is_running_returns_false_on_non_200_status(self, mock_get, client):
        """Test that is_running returns False on non-200 status."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        assert client.is_running() is False


class TestStartDaemon:
    """Test daemon startup logic."""

    @patch('daemon.client.DaemonClient.is_running')
    def test_start_daemon_returns_true_if_already_running(self, mock_is_running, client):
        """Test that start_daemon returns True if daemon is already running."""
        mock_is_running.return_value = True

        result = client.start_daemon()

        assert result is True
        mock_is_running.assert_called_once()

    @patch('daemon.client.DaemonClient.is_running')
    @patch('subprocess.Popen')
    @patch('time.sleep')
    def test_start_daemon_launches_process(self, mock_sleep, mock_popen, mock_is_running, client):
        """Test that start_daemon launches uvicorn process."""
        # First call returns False (not running), subsequent calls return True
        mock_is_running.side_effect = [False, True]

        result = client.start_daemon()

        assert result is True
        mock_popen.assert_called_once()
        call_args = mock_popen.call_args
        assert "python" in call_args[0][0]
        assert "-m" in call_args[0][0]
        assert "uvicorn" in call_args[0][0]

    @patch('daemon.client.DaemonClient.is_running')
    @patch('subprocess.Popen')
    @patch('time.sleep')
    def test_start_daemon_returns_false_if_startup_fails(self, mock_sleep, mock_popen, mock_is_running, client):
        """Test that start_daemon returns False if daemon doesn't start."""
        # Always returns False (daemon never starts)
        mock_is_running.return_value = False

        result = client.start_daemon()

        assert result is False
        mock_popen.assert_called_once()


class TestHealth:
    """Test health endpoint."""

    @patch('daemon.client.DaemonClient.start_daemon')
    @patch('httpx.get')
    def test_health_returns_status_when_daemon_running(self, mock_get, mock_start, client):
        """Test that health returns status from daemon."""
        mock_start.return_value = True
        mock_response = Mock()
        mock_response.json.return_value = {
            "status": "healthy",
            "uptime_seconds": 10.5,
            "connection_count": 1,
            "active_queries": 0
        }
        mock_get.return_value = mock_response

        result = client.health()

        assert result["status"] == "healthy"
        assert "uptime_seconds" in result
        mock_start.assert_called_once()
        mock_get.assert_called_once()

    @patch('daemon.client.DaemonClient.start_daemon')
    def test_health_returns_error_if_daemon_wont_start(self, mock_start, client):
        """Test that health returns error if daemon won't start."""
        mock_start.return_value = False

        result = client.health()

        assert result["status"] == "unavailable"
        assert "error" in result

    @patch('daemon.client.DaemonClient.start_daemon')
    @patch('httpx.get')
    def test_health_handles_exception(self, mock_get, mock_start, client):
        """Test that health handles exceptions gracefully."""
        mock_start.return_value = True
        mock_get.side_effect = Exception("Connection error")

        result = client.health()

        assert result["status"] == "error"
        assert "Connection error" in result["error"]


class TestQuery:
    """Test query execution."""

    @patch('daemon.client.DaemonClient.start_daemon')
    @patch('httpx.post')
    def test_query_executes_successfully(self, mock_post, mock_start, client):
        """Test that query executes and returns results."""
        mock_start.return_value = True
        mock_response = Mock()
        mock_response.json.return_value = {
            "success": True,
            "data": [[1, "Alice"], [2, "Bob"]],
            "columns": ["id", "name"],
            "row_count": 2,
            "execution_time": 0.123
        }
        mock_post.return_value = mock_response

        result = client.query("SELECT * FROM users", limit=10)

        assert result["success"] is True
        assert result["row_count"] == 2
        mock_start.assert_called_once()
        mock_post.assert_called_once()

        # Verify request payload
        call_kwargs = mock_post.call_args.kwargs
        assert call_kwargs["json"]["sql"] == "SELECT * FROM users"
        assert call_kwargs["json"]["limit"] == 10

    @patch('daemon.client.DaemonClient.start_daemon')
    @patch('httpx.post')
    def test_query_uses_default_limit(self, mock_post, mock_start, client):
        """Test that query uses default limit of 100."""
        mock_start.return_value = True
        mock_response = Mock()
        mock_response.json.return_value = {"success": True}
        mock_post.return_value = mock_response

        client.query("SELECT * FROM table")

        call_kwargs = mock_post.call_args.kwargs
        assert call_kwargs["json"]["limit"] == 100

    @patch('daemon.client.DaemonClient.start_daemon')
    def test_query_returns_error_if_daemon_wont_start(self, mock_start, client):
        """Test that query returns error if daemon won't start."""
        mock_start.return_value = False

        result = client.query("SELECT 1")

        assert result["success"] is False
        assert "Failed to start daemon" in result["error"]

    @patch('daemon.client.DaemonClient.start_daemon')
    @patch('httpx.post')
    def test_query_handles_timeout(self, mock_post, mock_start, client):
        """Test that query handles timeout exceptions."""
        mock_start.return_value = True
        mock_post.side_effect = httpx.TimeoutException("Query timeout")

        result = client.query("SELECT * FROM huge_table")

        assert result["success"] is False
        assert "timeout" in result["error"].lower()

    @patch('daemon.client.DaemonClient.start_daemon')
    @patch('httpx.post')
    def test_query_handles_exception(self, mock_post, mock_start, client):
        """Test that query handles exceptions gracefully."""
        mock_start.return_value = True
        mock_post.side_effect = Exception("Network error")

        result = client.query("SELECT 1")

        assert result["success"] is False
        assert "Network error" in result["error"]

    @patch('daemon.client.DaemonClient.start_daemon')
    @patch('httpx.post')
    def test_query_timeout_is_5_minutes(self, mock_post, mock_start, client):
        """Test that query timeout is set to 5 minutes (300 seconds)."""
        mock_start.return_value = True
        mock_response = Mock()
        mock_response.json.return_value = {"success": True}
        mock_post.return_value = mock_response

        client.query("SELECT 1")

        call_kwargs = mock_post.call_args.kwargs
        assert call_kwargs["timeout"] == 300.0


class TestCustomBaseUrl:
    """Test custom base URL."""

    @patch('httpx.get')
    def test_client_uses_custom_base_url(self, mock_get):
        """Test that client can use custom base URL."""
        custom_url = "http://localhost:9999"
        client = DaemonClient(base_url=custom_url)

        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        client.is_running()

        mock_get.assert_called_once_with(f"{custom_url}/health", timeout=1.0)
