import argparse
import getpass

from epic_events.controllers.authentication import authenticate, generate_jwt_token
from epic_events.controllers.token_manage import delete_token

    
def main():
    """
    Point d'entrée principal pour l'authentification en ligne de commande.
    """
    parser = argparse.ArgumentParser(description='Authentification en ligne de commande')
    parser.add_argument('username', type=str, help='Nom d\'utilisateur')
    args = parser.parse_args()
    password = getpass.getpass(prompt='Mot de passe: ')

    auth_success, user_id = authenticate(args.username, password)

    if auth_success:
        generate_jwt_token(user_id)
        print("Authentification réussie")
           
    else:
        print("\033[91mNom d'utilisateur ou mot de passe incorrect\033[0m")


if __name__ == "__main__":
    delete_token()
    main()
