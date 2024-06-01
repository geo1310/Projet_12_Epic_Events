import sys
import os
import socket
import sentry_sdk
from dotenv import load_dotenv

from controllers.authentication import AuthenticationManager
from controllers.menu_manage import MenuManage
from views.views import View
from utils.token_manage_json import delete_token

load_dotenv()

sentry_sdk.init(
    dsn=os.environ.get("SENTRY_DSN"),
    environment="development",
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    traces_sample_rate=1.0,
    # Set profiles_sample_rate to 1.0 to profile 100%
    # of sampled transactions.
    # We recommend adjusting this value in production.
    profiles_sample_rate=1.0,
    enable_tracing=True,
)


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

    view.clear_screen()

    email = view.return_choice("Entrez votre email", False)
    password = view.return_choice("Entrez votre mot de passe", True)

    # authentifie l'utilisateur dans la base de données
    auth_success, employee = auth_manager.authenticate(email, password)

    if auth_success:

        auth_manager.generate_jwt_token(employee.Id)

        # lance l'application
        app = MenuManage(view, auth_manager.verify_and_decode_jwt_token, delete_token, employee.Id)
        app.run()

    else:
        print(hostname)
        view.display_red_message("Nom d'utilisateur ou mot de passe incorrect\n")
        sentry_sdk.capture_message("Tentative de connexion : Nom d'utilisateur ou mot de passe incorrect.")


if __name__ == "__main__":
    delete_token()
    main()