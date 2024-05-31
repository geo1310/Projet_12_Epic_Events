import sentry_sdk
import socket


def sentry_event(user_connected_email: str, message: str, transaction: str = None, level: str = "info") -> None:
    """
    Envoie un événement à Sentry pour journaliser une action ou une information dans l'application.
    Ajoute les tags : 
        device : hostname de la machine
        user: email de l'user
        transaction: le type de transaction
        level : Le niveau de gravité de l'événement

    Args:
        user_connected_email (str): L'adresse e-mail de l'utilisateur connecté qui effectue l'action.
        message (str): Le message décrivant l'action ou l'information à journaliser.
        transaction (str, optional): Le type de transaction associée à l'événement. 
            Par défaut, None.
        level (str, optional): Le niveau de gravité de l'événement. 
            Les valeurs possibles sont 'info', 'warning', 'error' ou 'fatal'. 
            Par défaut, 'info'.

    Returns:
        None
    """

    hostname = socket.gethostname()

    sentry_sdk.set_tag("device", hostname)
    sentry_sdk.set_user({"email": user_connected_email})
    if transaction:
        sentry_sdk.set_tag("transaction", transaction)

    event = {
        "message": f"{message}",
        "level": level,  # Niveau de gravité de l'événement
    }
    sentry_sdk.capture_event(event)
