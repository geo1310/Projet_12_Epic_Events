import os
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple, Dict

import jwt
from dotenv import load_dotenv
from sqlalchemy.orm import Session

from app.models.employee import Employee
from app.models.role import Role
from app.utils.token_manage_json import delete_token, load_token_from_json, save_token_to_json


class AuthenticationManager:
    """
    Gère l'authentification des utilisateurs et la gestion des tokens JWT.

    Attributes:
        view: Objet de vue pour afficher les messages.
        logger: Objet logger pour enregistrer les messages de log.
        SECRET_KEY (str): Clé secrète pour signer les tokens JWT.
        TOKEN_EXPIRY (int): Durée de validité des tokens JWT en minutes.
    """

    def __init__(self, view, logger):
        load_dotenv(override=True)
        self.view = view
        self.SECRET_KEY = os.environ.get("SECRET_KEY")
        self.TOKEN_EXPIRY = int(os.environ.get("TOKEN_EXPIRY"))
        self.logger = logger

    def authenticate(
        self, email: str, password: str, session: Session
    ) -> Tuple[bool, Optional[Employee], Optional[Role]]:
        """
        Authentifie un utilisateur en vérifiant les informations d'identification dans la base de données et
        récupère le rôle associé.

        Args:
            email (str): Adresse e-mail de l'utilisateur.
            password (str): Mot de passe de l'utilisateur.
            session (Session): La session SQLAlchemy à utiliser pour interagir avec la base de données.

        Returns:
            tuple: Un tuple contenant un booléen indiquant si l'authentification réussit, l'objet Employee
                correspondant s'il est authentifié, et l'objet Role associé. Retourne (False, None, None) en cas d'échec.

        Exceptions:
            Affiche un message d'erreur en cas d'exception et retourne (False, None, None).
        """
        try:
            self.view.display_green_message("Authentification en cours ...")
            with session.begin():
                employee = session.query(Employee).filter_by(Email=email).first()
                if employee and employee.verify_password(password):
                    role = session.query(Role).filter_by(Id=employee.RoleId).one()
                    return True, employee, role
                else:
                    return False, None, None
        except Exception as e:
            self.view.display_red_message(f"Une erreur s'est produite : {e}")
            session.close()
            return False, None, None

    def generate_jwt_token(self, user_id: int) -> None:
        """
        Génère un jeton JWT pour l'utilisateur authentifié.

        Cette méthode crée un jeton JWT avec l'ID de l'utilisateur et une date
        d'expiration. Le jeton est ensuite sauvegardé dans un fichier JSON à l'aide
        de la fonction save_token_to_json.

        Args:
            user_id (int): L'ID de l'utilisateur.

        Returns:
            None
        """

        expiration_time = datetime.now() + timedelta(minutes=self.TOKEN_EXPIRY)
        payload = {"user_id": user_id, "exp": expiration_time}
        token = jwt.encode(payload, self.SECRET_KEY, algorithm="HS256")
        save_token_to_json(token)

    def verify_and_decode_jwt_token(self) -> Optional[Dict]:
        """
        Vérifie et décode un jeton JWT.
        Efface le jeton s'il n'est plus valide.

        Returns:
            Optional[Dict]: Le contenu décodé du jeton JWT s'il est valide et non expiré, sinon None.
        """

        try:
            token = load_token_from_json()
            decoded_payload = jwt.decode(token, self.SECRET_KEY, algorithms=["HS256"])

            if datetime.now() > datetime.fromtimestamp(decoded_payload["exp"], tz=timezone.utc).replace(tzinfo=None):
                delete_token()
                return None

            return decoded_payload

        except jwt.ExpiredSignatureError:
            delete_token()
            return None
        except jwt.InvalidTokenError:
            delete_token()
            return None
