import pytest
from dotenv import load_dotenv
from unittest.mock import Mock, patch
from app.controllers.authentication import AuthenticationManager
from app.controllers.menu_manage import MenuManage
from app.views.views import View
from app.utils.token_manage_json import delete_token
from app.utils.logger_config import LoggerConfig
from app.models.employee import Employee
from app.models.role import Role
from app import main

# Charger les variables d'environnement pour les tests
load_dotenv()


# Créer une classe de test pour les fonctions
class TestApplication:
    """Tests unitaires pour les fonctions d'application"""

    @pytest.fixture(autouse=True)
    def setup_method(self):
        self.view = Mock(spec=View)
        self.logger_config = LoggerConfig()
        self.logger = self.logger_config.get_logger()
        self.auth_manager = AuthenticationManager(self.view, self.logger)
        self.session = Mock()
        self.employee = Mock(spec=Employee)
        self.role = Mock(spec=Role)

        self.mock_return_choice = patch.object(View, "return_choice").start()
        self.mock_display_red_message = patch.object(View, "display_red_message").start()
        self.mock_display_green_message = patch.object(View, "display_green_message").start()
        self.mock_display_title_panel_color_fit = patch.object(View, "display_title_panel_color_fit").start()
        self.mock_display_table = patch.object(View, "display_table").start()
        self.mock_authenticate = patch.object(AuthenticationManager, "authenticate").start()

        yield

        patch.stopall()

    def test_imports(self):
        try:
            from dotenv import load_dotenv
            from app.models.database import DatabaseConfig
            from app.controllers.authentication import AuthenticationManager
            from app.controllers.menu_manage import MenuManage
            from app.views.views import View
            from app.utils.token_manage_json import delete_token
            from app.utils.logger_config import LoggerConfig
            from app.utils.sentry_logger import SentryLogger
            from app.models.employee import Employee
            from app.models.role import Role

            assert True

        except ImportError:
            assert False

    def test_authenticate_quit(self):
        """Test de la fonction authenticate lorsqu'on quitte en entrant un email vide"""

        self.mock_return_choice.side_effect = ["", ""]
        self.mock_authenticate.return_value = ["quit", None, None]

        result = main.authenticate(self.view, self.auth_manager, self.session)

        assert result == ("quit", None, None)

    def test_authenticate_retry(self):
        """Test de la fonction authenticate lorsqu'on entre un mot de passe vide"""
        self.view.return_choice.side_effect = ["test@example.com", ""]

        result = main.authenticate(self.view, self.auth_manager, self.session)
        assert result == ("retry", None, None)

    def test_authenticate_success(self):
        """Test de la fonction authenticate avec succès"""
        self.view.return_choice.side_effect = ["test@example.com", "password"]
        self.auth_manager.authenticate.return_value = (True, self.employee, self.role)

        result = main.authenticate(self.view, self.auth_manager, self.session)
        assert result == (True, self.employee, self.role)

    def test_authenticate_failure(self):
        """Test de la fonction authenticate en cas d'échec"""
        self.view.return_choice.side_effect = ["test@example.com", "wrongpassword"]
        self.auth_manager.authenticate.return_value = (False, None, None)

        result = main.authenticate(self.view, self.auth_manager, self.session)
        assert result == (False, None, None)

    @patch("app.controllers.menu_manage.MenuManage.run")
    def test_run_menu(self, mock_run):
        """Test de la fonction run_menu"""
        with patch.object(AuthenticationManager, "generate_jwt_token") as mock_generate_jwt_token:
            main.run_menu(self.view, self.auth_manager, self.session, self.employee, self.role, self.logger)

            mock_generate_jwt_token.assert_called_once_with(self.employee.Id)
            mock_run.assert_called_once()


if __name__ == "__main__":
    pytest.main(["--cov=app/", "--cov-report=html", __file__])
