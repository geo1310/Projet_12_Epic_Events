import os
import json
import tempfile
import pytest
from unittest.mock import patch
from app.utils import token_manage_json


@pytest.fixture
def mock_path():
    # crée un repertoire temporaire, supprimé aprés le bloc test
    with tempfile.TemporaryDirectory() as tempdir:
        file_path = os.path.join(tempdir, "token.json")
        yield file_path


@pytest.fixture
def mock_token():
    return "mock_token_value"


def test_save_token_to_json(mock_token, mock_path):

    token_manage_json.save_token_to_json(mock_token, mock_path)

    # vérification
    with open(mock_path, "r") as file:
        data = json.load(file)
        assert data["token"] == mock_token


def test_load_token_from_json(mock_token, mock_path):

    token_manage_json.save_token_to_json(mock_token, mock_path)
    loaded_token = token_manage_json.load_token_from_json(mock_path)

    assert loaded_token == mock_token


def test_delete_token(mock_token, mock_path):

    token_manage_json.save_token_to_json(mock_token, mock_path)
    token_manage_json.delete_token(mock_path)

    with open(mock_path, "r") as file:
        data = json.load(file)
        assert data["token"] == ""


def test_load_token_to_json_file_not_exists(mock_token, mock_path):

    token_manage_json.save_token_to_json(mock_token, mock_path)

    # Utiliser le monkeypatch pour simuler l'absence du fichier
    with patch("os.path.exists", return_value=False):
        token_manage_json.save_token_to_json("", mock_path)
        loaded_token = token_manage_json.load_token_from_json(mock_path)

    assert loaded_token == ""


def test_delete_token_to_json_file_not_exists(mock_token, mock_path):

    token_manage_json.save_token_to_json(mock_token, mock_path)

    # Utiliser le monkeypatch pour simuler l'absence du fichier
    with patch("os.path.exists", return_value=False):
        token_manage_json.delete_token(mock_path)

    loaded_token = token_manage_json.load_token_from_json(mock_path)

    assert loaded_token != ""


if __name__ == "__main__":
    pytest.main(["--cov=app/utils/", "--cov-report=html", __file__])
