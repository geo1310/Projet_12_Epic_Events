import logging
import os
import socket

import sentry_sdk
from dotenv import load_dotenv
from sentry_sdk.integrations.logging import LoggingIntegration


class SentryLogger:
    """
    Gestion des événements Sentry.
    """

    def __init__(self):
        """
        Initialise la configuration Sentry.
        """

        load_dotenv()

        sentry_sdk.init(
            dsn=os.environ.get("SENTRY_DSN"),
            environment=os.environ.get("ENVIRONMENT"),
            traces_sample_rate=1.0,  # Capture 100% des traces
            profiles_sample_rate=1.0,  # Profilage à 100%
            enable_tracing=True,
            integrations=[
                LoggingIntegration(
                    level=logging.INFO,  # Capture les événements info et plus
                    event_level=logging.WARNING,  # Envoie les erreurs comme des événements
                )
            ],
        )

    def sentry_event(
        self, user_connected_email: str, message: str, level: str = "info", transaction: str = None
    ) -> None:
        """
        Envoie un événement à Sentry pour journaliser une action ou une information dans l'application.

        Args:
            user_connected_email (str): L'adresse e-mail de l'utilisateur connecté qui effectue l'action.
            message (str): Le message décrivant l'action ou l'information à journaliser.
            transaction (str, optional): Le type de transaction associée à l'événement.
                Par défaut, None.
            level (str, optional): Le niveau de gravité de l'événement.
                Les valeurs possibles sont 'info', 'warning', 'error' ou 'fatal'.
                Par défaut, 'info'.
            ip_address (str, optional): L'adresse IP de l'utilisateur.
                Par défaut, None.

        Returns:
            None
        """
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)

        with sentry_sdk.configure_scope() as scope:
            scope.set_tag("device", hostname)
            scope.set_user({"email": user_connected_email})
            if transaction:
                scope.set_tag("transaction", transaction)
            if ip_address:
                scope.set_tag("ip_address", ip_address)

        event = {
            "message": f"{message}",
            "level": level,  # Niveau de gravité de l'événement
        }
        sentry_sdk.capture_event(event)


# Exemple d'utilisation :
if __name__ == "__main__":
    sentry_logger = SentryLogger()
    sentry_logger.sentry_event("user@example.com", "Ceci est un test pour un message d'erreur", "error", "TEST")
