import argparse
from dotenv import load_dotenv

from epic_events.controllers.authentication import AuthenticationManager
from epic_events.controllers.menu_manage import MenuManage
from epic_events.views.views import View
from epic_events.utils.token_manage_json import delete_token

view = View()
auth_manager = AuthenticationManager(view)


def main():
    """
    Point d'entrée principal pour l'authentification en ligne de commande.
    """

    # crée l'argument user_email
    parser = argparse.ArgumentParser(description="Authentification en ligne de commande")
    parser.add_argument("user_email", type=str, help="Email d'utilisateur")
    args = parser.parse_args()
    view.clear_screen()
    password = view.return_choice(f"{args.user_email} entrez votre mot de passe : ", True)

    # authentifie l'utilisateur dans la base de données
    auth_success, employee = auth_manager.authenticate(args.user_email, password)

    if auth_success:
        
        auth_manager.generate_jwt_token(employee.Id)

        # lance l'application
        app = MenuManage(view, auth_manager.verify_and_decode_jwt_token, delete_token, employee.Id)
        app.run()

    else:

        view.display_red_message("Nom d'utilisateur ou mot de passe incorrect\n")


if __name__ == "__main__":
    delete_token()
    main()
