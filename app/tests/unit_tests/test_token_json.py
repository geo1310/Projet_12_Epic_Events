import os
import json
import tempfile
import pytest
from app.utils.token_manage_json import save_token_to_json, load_token_from_json, delete_token

@pytest.fixture
def mock_token():
    return "mock_token_value"

def test_save_token_to_json(mock_token):
    # crée un repertoire temporaire, supprimé aprés le bloc test
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = os.path.join(tmpdir, "token.json")
        save_token_to_json(mock_token, file_path)
        with open(file_path, "r") as file:
            data = json.load(file)
            assert data["token"] == mock_token

def test_load_token_from_json(mock_token):
    # crée un repertoire temporaire, supprimé aprés le bloc test
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = os.path.join(tmpdir, "token.json")
        save_token_to_json(mock_token, file_path)
        loaded_token = load_token_from_json(file_path)
        assert loaded_token == mock_token

def test_delete_token(mock_token):
    # crée un repertoire temporaire, supprimé aprés le bloc test
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = os.path.join(tmpdir, "token.json")
        save_token_to_json(mock_token, file_path)
        delete_token(file_path)
        with open(file_path, "r") as file:
            data = json.load(file)
            assert data["token"] == ""
