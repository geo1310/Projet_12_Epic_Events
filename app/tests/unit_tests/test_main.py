import pytest
from unittest.mock import MagicMock
from app.main import authenticate, run_menu

@pytest.fixture
def mock_view():
    return MagicMock()

@pytest.fixture
def mock_auth_manager():
    return MagicMock()

@pytest.fixture
def mock_session():
    return MagicMock()

@pytest.fixture
def mock_employee():
    return MagicMock()

@pytest.fixture
def mock_role():
    return MagicMock()

def test_authenticate_successful(mock_view, mock_auth_manager, mock_session, mock_employee, mock_role):
    """Teste le cas où l'authentification réussit."""
    mock_view.return_choice.side_effect = ["test@example.com", "password"]
    mock_auth_manager.authenticate.return_value = (True, mock_employee, mock_role)

    auth_success, employee, role = authenticate(mock_view, mock_auth_manager, mock_session)

    assert auth_success
    assert employee == mock_employee
    assert role == mock_role

def test_authenticate_unsuccessful(mock_view, mock_auth_manager, mock_session, mock_employee, mock_role):
    """Teste le cas où l'authentification échoue."""
    mock_view.return_choice.return_value = "test@example.com"
    mock_auth_manager.authenticate.return_value = (False, None, None)

    auth_success, employee, role = authenticate(mock_view, mock_auth_manager, mock_session)

    assert not auth_success
    assert employee is None
    assert role is None

def test_run_menu(mock_view, mock_auth_manager, mock_session, mock_employee, mock_role):
    """Teste la fonction de démarrage du menu."""
    mock_employee.Id = 123
    mock_view.return_choice.side_effect = ["test@example.com", "password"]
    mock_auth_manager.authenticate.return_value = (True, mock_employee, mock_role)

    with pytest.raises(SystemExit):
        run_menu(mock_view, mock_auth_manager, mock_session, mock_employee, mock_role)


