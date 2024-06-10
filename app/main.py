from typing import Tuple, Union
from dotenv import load_dotenv

from app.models.database import DatabaseConfig
from app.controllers.authentication import AuthenticationManager
from app.controllers.menu_manage import MenuManage
from app.views.views import View
from app.utils.token_manage_json import delete_token
from app.utils.logger_config import LoggerConfig
from app.utils.sentry_logger import SentryLogger
from app.models.employee import Employee
from app.models.role import Role

load_dotenv()

# Loggers
logger_config = LoggerConfig()
logger = logger_config.get_logger()
sentry_logger = SentryLogger()

logger.info("Run App")



def authenticate(view: View, auth_manager: AuthenticationManager, session)-> Tuple[Union[bool, None], Union[Employee, None], Union[Role, None]]:
    """
    Demande l'email et le mot de passe et Authentifie l'utilisateur.

    Args:
        view (View): L'objet de vue utilisé pour obtenir l'email et le mot de passe de l'utilisateur.
        auth_manager (AuthenticationManager): L'objet de gestion de l'authentification utilisé pour authentifier l'utilisateur.
        session: L'objet de session utilisé pour accéder à la base de données.

    Returns:
        Tuple[Union[bool, None], Union[Employee, None], Union[Role, None]]: Un tuple contenant le succès de l'authentification, l'objet Employee correspondant à l'utilisateur authentifié (s'il réussit) et le rôle de l'utilisateur (s'il réussit).
            - Si l'utilisateur quitte en entrant un email vide, retourne ("quit", None, None).
            - Si l'utilisateur quitte en entrant un mot de passe vide, retourne ("retry", None, None).
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
    Lance le menu principale et génère le token de la session.

    Args:
        view (View): L'objet de vue utilisé pour afficher le menu.
        auth_manager (AuthenticationManager): L'objet de gestion de l'authentification utilisé pour vérifier et décoder les jetons JWT.
        session : L'objet de session utilisé pour accéder à la base de données.
        employee (Employee): L'objet Employee représentant l'utilisateur actuellement connecté.
        role (Role): L'objet Role représentant le rôle de l'utilisateur actuellement connecté.
    """
    auth_manager.generate_jwt_token(employee.Id)
    logger.info(f"Connexion: {employee.Email}", exc_info=False)
    app = MenuManage(view, auth_manager.verify_and_decode_jwt_token, delete_token, session, employee, role, logger)
    app.run()

def main():
    """
    Point d'entrée principal pour l'authentification en ligne de commande.
    """
    view = View()
    auth_manager = AuthenticationManager(view, logger)
    session_config = DatabaseConfig(logger)
    session = session_config.db_session_local()

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
            logger.warning("Nom d'utilisateur ou mot de passe incorrect")
            view.prompt_wait_enter()

    logger.info("Close App")
    if session:
        session.close()

if __name__ == "__main__":
    delete_token()
    main()
