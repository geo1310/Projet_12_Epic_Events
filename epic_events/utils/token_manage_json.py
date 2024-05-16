import json
import os

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
file_path = os.path.join(project_root, "data", "token.json")


def save_token_to_json(token):
    """
    Enregistre un jeton (token) dans un fichier JSON.

    Args:
        token (str): Le jeton à enregistrer.
    """
    data = {"token": token}
    with open(file_path, "w") as file:
        json.dump(data, file)


def load_token_from_json():
    """
    Charge un jeton à partir d'un fichier JSON.

    Returns:
        str: Le jeton chargé depuis le fichier JSON.
    """
    if not os.path.exists(file_path):
        token = ""
        save_token_to_json(token)

    with open(file_path, "r") as file:
        data = json.load(file)
        return data.get("token")


def delete_token():
    """
    Supprime le jeton enregistré en le remplaçant par une chaîne vide dans le fichier JSON.
    """
    if os.path.exists(file_path):
        data = {"token": ""}
        with open(file_path, "w") as file:
            json.dump(data, file)
