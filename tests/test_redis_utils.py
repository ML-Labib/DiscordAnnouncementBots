import unittest
from unittest.mock import patch

from redis_utils import ensure_redis_running


class _ContextManagerStub:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return False


class EnsureRedisRunningTests(unittest.TestCase):
    @patch("redis_utils.subprocess.run")
    @patch("redis_utils.shutil.which")
    @patch("redis_utils.socket.create_connection")
    def test_returns_true_when_redis_is_already_available(self, mock_create_connection, mock_which, mock_run):
        mock_create_connection.return_value.__enter__.return_value = object()

        result = ensure_redis_running("127.0.0.1", 6179)

        self.assertTrue(result)
        mock_which.assert_not_called()
        mock_run.assert_not_called()

    @patch("redis_utils.subprocess.run")
    @patch("redis_utils.shutil.which")
    @patch("redis_utils.socket.create_connection")
    def test_starts_redis_when_not_running(self, mock_create_connection, mock_which, mock_run):
        mock_create_connection.side_effect = [OSError("down"), OSError("down"), OSError("down"), _ContextManagerStub()]
        mock_which.return_value = "/usr/bin/redis-server"
        mock_run.return_value = type("Proc", (), {"returncode": 0})()

        result = ensure_redis_running("127.0.0.1", 6179)

        self.assertTrue(result)
        mock_run.assert_called_once()

    @patch("redis_utils.shutil.which")
    @patch("redis_utils.socket.create_connection")
    def test_raises_when_redis_server_binary_is_missing(self, mock_create_connection, mock_which):
        mock_create_connection.side_effect = OSError("down")
        mock_which.return_value = None

        with self.assertRaises(RuntimeError):
            ensure_redis_running("127.0.0.1", 6179)


if __name__ == "__main__":
    unittest.main()
