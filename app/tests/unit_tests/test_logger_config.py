import pytest
import logging
from unittest.mock import patch, MagicMock
import sys
from app.utils.logger_config import LoggerConfig


class TestLoggerConfig:
    """
    Tests unitaires pour la classe LoggerConfig.
    """

    @pytest.fixture(autouse=True)
    def setup_method(self):
        """
        Configuration des mocks pour les tests et nettoyage après chaque test.
        """
        self.mock_get_logger = patch("logging.getLogger").start()
        self.mock_stream_handler = patch("logging.StreamHandler").start()
        self.mock_file_handler = patch("logging.handlers.RotatingFileHandler").start()
        self.mock_colored_formatter = patch("colorlog.ColoredFormatter").start()

        self.mock_logger = MagicMock()
        self.mock_logger.level = logging.DEBUG
        self.mock_get_logger.return_value = self.mock_logger

        self.logger_config = LoggerConfig()

        yield

        patch.stopall()

    def test_logger_initialization(self):
        """Test de l'initialisation du logger."""
        logger = self.logger_config.get_logger()
        assert self.logger_config.logger is logger
        assert logger.level == logging.DEBUG

    def test_global_exception_handler(self):
        """Test du gestionnaire d'exceptions global."""
        assert sys.excepthook == self.logger_config.handle_exception

    def test_handle_exception(self):
        """Test du gestionnaire d'exceptions."""
        logger = self.logger_config.get_logger()

        exc_type, exc_value, exc_traceback = RuntimeError, RuntimeError("Test Error"), None

        with patch.object(logger, "error") as mock_error:
            self.logger_config.handle_exception(exc_type, exc_value, exc_traceback)
            mock_error.assert_called_once_with("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))


if __name__ == "__main__":
    pytest.main(["-s", "--cov=app/utils/", "--cov-report=html", __file__])
