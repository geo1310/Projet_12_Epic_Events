from typing import Tuple, Union
import os
import socket
from dotenv import load_dotenv
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration
import logging

from app.models.database import SessionLocal
from app.controllers.authentication import AuthenticationManager
from app.controllers.menu_manage import MenuManage
from app.views.views import View
from app.utils.token_manage_json import delete_token
from app.utils.logging_config import logger
from app.models.employee import Employee
from app.models.role import Role

load_dotenv()

sentry_sdk.init(
    dsn=os.environ.get("SENTRY_DSN"),
    environment=os.environ.get("ENVIRONMENT"),
    # Set traces_sample_rate to 1.0 to capture 100% ( performances)
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
hostname = socket.gethostname()
ip_address = socket.gethostbyname(hostname)

with sentry_sdk.configure_scope() as scope:
    scope.set_tag("ip_address", ip_address)

def authenticate(view: View, auth_manager: AuthenticationManager, session)-> Tuple[Union[bool, None], Union[Employee, None], Union[Role, None]]:
    """
    Authentifie l'utilisateur.

    Args:
        view (View): L'objet de vue utilisé pour obtenir l'email et le mot de passe de l'utilisateur.
        auth_manager (AuthenticationManager): L'objet de gestion de l'authentification utilisé pour authentifier l'utilisateur.
        session (SessionLocal): L'objet de session utilisé pour accéder à la base de données.

    Returns:
        Tuple[Union[bool, None], Union[Employee, None], Union[Role, None]]: Un tuple contenant le succès de l'authentification, l'objet Employee correspondant à l'utilisateur authentifié (s'il réussit) et le rôle de l'utilisateur (s'il réussit).
            - Si l'utilisateur quitte en entrant un email vide, retourne (None, None, None).
            - Si l'utilisateur quitte en entrant un mot de passe vide, retourne (False, None, None).
            - Si l'authentification réussit, retourne (True, employee, role), où employee est l'objet Employee correspondant à l'utilisateur et role est son rôle.
            - Si l'authentification échoue, retourne (False, None, None).
    """
    email = view.return_choice("Entrez votre email ( vide pour quitter )", False)
    if not email:
        return "quit", None, None

    password = view.return_choice("Entrez votre mot de passe ( vide pour annuler )", True)

    if password:
        auth_success, employee, role = auth_manager.authenticate(email, password, session)
        return auth_success, employee, role
    else:
        return "retry", None, None

def run_menu(view: View, auth_manager: AuthenticationManager, session, employee: Employee, role: Role) -> None:
    """
    Lance le menu.

    Args:
        view (View): L'objet de vue utilisé pour afficher le menu.
        auth_manager (AuthenticationManager): L'objet de gestion de l'authentification utilisé pour vérifier et décoder les jetons JWT.
        session (SessionLocal): L'objet de session utilisé pour accéder à la base de données.
        employee (Employee): L'objet Employee représentant l'utilisateur actuellement connecté.
        role (Role): L'objet Role représentant le rôle de l'utilisateur actuellement connecté.
    """
    auth_manager.generate_jwt_token(employee.Id)
    logger.info(f"Connexion: {employee.Email}", exc_info=False)
    app = MenuManage(view, auth_manager.verify_and_decode_jwt_token, delete_token, session, employee, role)
    app.run()

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

        auth_success, employee, role = authenticate(view, auth_manager, session)
        
        if auth_success:
            if auth_success == 'quit':
                break
            elif auth_success != 'retry':
                run_menu(view, auth_manager, session, employee, role)
            
        else:
            logger.warning("Nom d'utilisateur ou mot de passe incorrect !")
            view.prompt_wait_enter()

    logger.info("Close App")
    if session:
        session.close()

if __name__ == "__main__":
    delete_token()
    main()
