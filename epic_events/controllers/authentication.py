import logging
import os
from datetime import datetime, timedelta, timezone

import jwt
from dotenv import load_dotenv, set_key

from epic_events.models.database import Session
from epic_events.models.employee import Employee

from .token_manage import (delete_token, load_token_from_json,
                           save_token_to_json)

# Configuration du logger
logging.basicConfig(level=logging.INFO)

# Charge les variables d'environnement depuis le fichier .envrc
load_dotenv(".envrc")
SECRET_KEY = os.environ.get("SECRET_KEY")
TOKEN_EXPIRY = int(os.environ.get("TOKEN_EXPIRY"))


def authenticate(email, password):
    """
    Authentifie un utilisateur en vérifiant les informations d'identification dans la base de données.

    Args:
        email (str): Adresse e-mail de l'utilisateur.
        password (str): Mot de passe de l'utilisateur.

    Returns:
        tuple: Un tuple contenant un booléen indiquant si l'authentification réussit et l'ID de l'utilisateur
        s'il est authentifié.
    """
    try:
        session = Session()
        employee = session.query(Employee).filter_by(Email=email).first()
        if employee and employee.verify_password(password):
            return True, employee.Id
        else:
            return False, None
    except Exception as e:
        logging.error(f"\033[91mUne erreur s'est produite : {e}\033[0m")
        return False, None
    finally:
        if session:
            session.close()


def generate_jwt_token(user_id):
    """
    Génère un jeton JWT pour l'utilisateur authentifié.

    Args:
        user_id (int): L'ID de l'utilisateur.

    Returns:
        str: Le jeton JWT généré.
    """
    expiration_time = datetime.now() + timedelta(minutes=TOKEN_EXPIRY)

    payload = {"user_id": user_id, "exp": expiration_time}
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

    save_token_to_json(token)


def verify_and_decode_jwt_token():
    """
    Vérifie et décode un jeton JWT.
    Efface le Token s'il n'est plus valide.

    Returns:
        dict or None: Le contenu décodé du jeton JWT s'il est valide et non expiré, sinon None.
    """
    try:

        token = load_token_from_json()
        decoded_payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])

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
