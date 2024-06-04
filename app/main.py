import os
import socket
from dotenv import load_dotenv
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration

from models.database import SessionLocal
from controllers.authentication import AuthenticationManager
from controllers.menu_manage import MenuManage
from views.views import View
from utils.token_manage_json import delete_token

import logging
from utils.logging_config import logger

load_dotenv()

sentry_sdk.init(
    dsn=os.environ.get("SENTRY_DSN"),
    environment=os.environ.get("ENVIRONMENT"),
    # Set traces_sample_rate to 1.0 to capture 100%
    traces_sample_rate=1.0,
    # Set profiles_sample_rate to 1.0 to profile 100%
    profiles_sample_rate=1.0,
    enable_tracing=True,

    # logger attach
    # level ERROR en event et level INFO en données agrégées par sentry
    integrations=[LoggingIntegration(
        level=logging.INFO, # Capture les événements info et plus
        event_level=logging.WARNING # Envoie les erreurs comme des événements
    )]

)

logger.info("Run App")
# informations sur la machine hote
hostname = socket.gethostname()
ip_address = socket.gethostbyname(hostname)

# Définir un tag avec l'adresse IP
with sentry_sdk.configure_scope() as scope:
    scope.set_tag("ip_address", ip_address)


# sys.path : liste contenant les répertoires ou python cherche les modules
#sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def main():
    """
    Point d'entrée principal pour l'authentification en ligne de commande.
    """

    view = View()
    auth_manager = AuthenticationManager(view)
    session = SessionLocal()

    while True:
        view.clear_screen()
        view.display_title_panel_color_fit("Connexion Epic-Events", "magenta")

        email = view.return_choice("Entrez votre email ( vide pour quitter )", False)
        if not email:
            break

        password = view.return_choice("Entrez votre mot de passe ( vide pour annuler )", True)
        
        if password:
            # authentifie l'utilisateur dans la base de données
            auth_success, employee, role = auth_manager.authenticate(email, password, session)

            if auth_success:

                auth_manager.generate_jwt_token(employee.Id)

                # lance l'application
                logger.info(f"Connexion: {employee.Email}", exc_info=False)
                app = MenuManage(view, auth_manager.verify_and_decode_jwt_token, delete_token, session, employee, role)
                app.run()

            else:
                logger.warning(f"Nom d'utilisateur ou mot de passe incorrect -> Email : {email}")
                # sentry_sdk.capture_message("Tentative de connexion : Nom d'utilisateur ou mot de passe incorrect.")

                view.prompt_wait_enter()

    logger.info("Close App")
    if session:
        session.close()


if __name__ == "__main__":
    delete_token()
    main()
