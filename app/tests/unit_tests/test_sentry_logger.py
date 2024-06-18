import os
import socket
from unittest.mock import MagicMock, patch

import pytest
from sentry_sdk import capture_event, configure_scope, init
from sentry_sdk.integrations.logging import LoggingIntegration

from app.utils.sentry_logger import SentryLogger


class TestSentryLogger:
    """Tests unitaires pour la classe SentryLogger"""

    @pytest.fixture(autouse=True)
    def setup_method(self):

        self.patcher_init = patch("sentry_sdk.init")
        self.patcher_configure_scope = patch("sentry_sdk.configure_scope")
        self.patcher_capture_event = patch("sentry_sdk.capture_event")

        self.mock_init = self.patcher_init.start()
        self.mock_configure_scope = self.patcher_configure_scope.start()
        self.mock_capture_event = self.patcher_capture_event.start()

        self.sentry_logger = SentryLogger()

        yield

        patch.stopall()

    def test_sentry_logger_init(self):

        # Arrang
        with patch("sentry_sdk.init") as mock_init:
            expected_dsn = os.environ.get("SENTRY_DSN")
            expected_environment = os.environ.get("ENVIRONMENT")
            expected_traces_sample_rate = 1.0
            expected_profiles_sample_rate = 1.0
            expected_enable_tracing = True

            # Act
            self.sentry_logger.__init__()

            # Assert
            _, called_kwargs = mock_init.call_args
            assert called_kwargs["dsn"] == expected_dsn
            assert called_kwargs["environment"] == expected_environment
            assert abs(called_kwargs["traces_sample_rate"] - expected_traces_sample_rate) < 1e-9
            assert abs(called_kwargs["profiles_sample_rate"] - expected_profiles_sample_rate) < 1e-9
            assert called_kwargs["enable_tracing"] == expected_enable_tracing

            # Vérifiez que l'intégration LoggingIntegration est présente
            logging_integration = [
                integration
                for integration in called_kwargs["integrations"]
                if isinstance(integration, LoggingIntegration)
            ]
            assert len(logging_integration) == 1

    def test_sentry_event(self):

        # Arrang
        mock_scope = MagicMock()
        self.mock_configure_scope.return_value.__enter__.return_value = mock_scope

        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)

        # Act
        self.sentry_logger.sentry_event(
            "user@example.com", "Ceci est un test pour un message d'erreur", "error", "TEST"
        )

        # Assert
        mock_scope.set_tag.assert_any_call("device", hostname)
        mock_scope.set_user.assert_called_once_with({"email": "user@example.com"})
        mock_scope.set_tag.assert_any_call("transaction", "TEST")
        mock_scope.set_tag.assert_any_call("ip_address", ip_address)

        self.mock_capture_event.assert_called_once_with(
            {"message": "Ceci est un test pour un message d'erreur", "level": "error"}
        )


if __name__ == "__main__":
    pytest.main(["--cov=app/utils/", "--cov-report=html", __file__])
