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
from app.dev.init_db import DatabaseInitializer
from app.models.database import DatabaseConfig
from app import main

# Charger les variables d'environnement pour les tests
load_dotenv()


# Créer une classe de test pour les fonctions
class TestApplication:
    """Tests unitaires pour les fonctions d'application"""

    @pytest.fixture(autouse=True)
    def setup_method(self):
        self.view = View()
        self.logger_config = LoggerConfig()
        self.logger = self.logger_config.get_logger()
        self.auth_manager = AuthenticationManager(self.view, self.logger)
        self.database = DatabaseConfig(Mock())
        self.session = Mock()
        self.employee = Mock(spec=Employee)
        self.role = Mock(spec=Role)

        self.mock_return_choice = patch.object(View, "return_choice").start()
        self.mock_prompt_wait_enter = patch.object(View, "prompt_wait_enter").start()
        self.mock_display_red_message = patch.object(View, "display_red_message").start()
        self.mock_display_green_message = patch.object(View, "display_green_message").start()
        self.mock_display_title_panel_color_fit = patch.object(View, "display_title_panel_color_fit").start()
        self.mock_display_table = patch.object(View, "display_table").start()
        self.mock_auth_authenticate = patch.object(AuthenticationManager, "authenticate").start()

        yield

        patch.stopall()

    def test_authenticate_success(self):

        # Arrang
        self.mock_return_choice.side_effect = ["test@email.com", "Password123"]
        result_success = (True, "employee", "role")
        self.mock_auth_authenticate.return_value = result_success

        # Act
        result = main.authenticate(self.view, self.auth_manager, self.session)

        # Assert
        assert result == result_success

    def test_authenticate_quit(self):
        """Test de la fonction authenticate lorsqu'on quitte en entrant un email vide"""

        # Arrang
        self.mock_return_choice.side_effect = ["", ""]

        # Act
        result = main.authenticate(self.view, self.auth_manager, self.session)

        # Assert
        assert result == ("quit", None, None)

    def test_authenticate_retry(self):
        """Test de la fonction authenticate avec un password vide"""
        # Arrang
        self.mock_return_choice.side_effect = ["tes@email.com", ""]

        # Act
        result = main.authenticate(self.view, self.auth_manager, self.session)

        # Assert
        assert result == ("retry", None, None)

    def test_main_success(self):

        with patch("app.main.run_menu") as mock_run_menu, \
         patch("app.main.authenticate") as mock_main_authenticate:

            # Arrang
            result_success = (True, "employee", "role")
            result_quit = ("quit", None, None)
            mock_main_authenticate.side_effect = [result_success, result_quit]

            # Act
            main.main(self.view, self.logger, self.session, self.auth_manager)

        # Assert
        self.mock_display_title_panel_color_fit.assert_called_with("Connexion Epic-Events", "magenta")
        mock_run_menu.assert_called_once_with(self.view, self.auth_manager, self.session, "employee", "role", self.logger)

    def test_run_menu(self):
        """Test de la fonction run_menu"""

        with patch("app.controllers.menu_manage.MenuManage.run") as mock_run, patch.object(
            AuthenticationManager, "generate_jwt_token"
        ) as mock_generate_jwt_token:

            main.run_menu(self.view, self.auth_manager, self.session, self.employee, self.role, self.logger)

        # Assert
        mock_generate_jwt_token.assert_called_once_with(self.employee.Id)
        mock_run.assert_called_once()

    def test_check_tables_exist(self):
        """Test de la fonction check_tables_exist"""
        # À faire
        pass


if __name__ == "__main__":
    pytest.main(["--cov=app/", "--cov-report=html", __file__])
