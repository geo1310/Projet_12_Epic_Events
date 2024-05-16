import json
import os

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
file_path = os.path.join(project_root, "data", "token.json")


def save_token_to_json(token):
    data = {"token": token}
    with open(file_path, "w") as file:
        json.dump(data, file)


def load_token_from_json():
    if not os.path.exists(file_path):
        token = ""
        save_token_to_json(token)

    with open(file_path, "r") as file:
        data = json.load(file)
        return data.get("token")


def delete_token():
    if os.path.exists(file_path):
        data = {"token": ""}
        with open(file_path, "w") as file:
            json.dump(data, file)
