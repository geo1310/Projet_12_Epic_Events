import pytest
from unittest.mock import Mock
from app.controllers.menu_manage import MenuManage


class TestMenuManage:

    @pytest.fixture(autouse=True)
    def setup_method(self):

        self.view = Mock()
        self.verify_jwt = Mock()
        self.delete_token = Mock()
        self.session = Mock()
        self.employee = Mock()
        self.role = Mock()
        self.logger = Mock()

        self.employee.Id = 1
        self.employee.FirstName = "John"
        self.employee.LastName = "Doe"
        self.employee.Email = "john.doe@example.com"
        self.employee.RoleRel.RoleName = "Admin"

        self.menu_manage = MenuManage(
            self.view, self.verify_jwt, self.delete_token, self.session, self.employee, self.role, self.logger
        )

        return self.menu_manage

    def test_initialization(self):
        assert self.menu_manage.view is not None
        assert self.menu_manage.verify_jwt is not None
        assert self.menu_manage.delete_token is not None
        assert self.menu_manage.session is not None
        assert self.menu_manage.employee is not None
        assert self.menu_manage.role is not None
        assert self.menu_manage.logger is not None
        assert self.menu_manage.permissions is not None

    def test_run_invalid_user(self):
        self.menu_manage.verify_jwt.return_value = {"user_id": 2}
        self.menu_manage.view.display_red_message = Mock()
        self.menu_manage.view.prompt_wait_enter = Mock()
        self.menu_manage.logout = Mock()

        self.menu_manage.run()

        self.menu_manage.view.display_red_message.assert_called_once_with(
            "Authentification invalide pour cet utilisateur."
        )
        self.menu_manage.view.prompt_wait_enter.assert_called_once()
        self.menu_manage.logout.assert_called_once()

    def test_menu_main(self):
        self.menu_manage.permissions.can_read_employee = Mock(return_value=True)
        self.menu_manage.permissions.can_read_role = Mock(return_value=True)
        self.menu_manage.run_menu = Mock()

        self.menu_manage.menu_main()

        assert self.menu_manage.run_menu.called
        args, _ = self.menu_manage.run_menu.call_args
        assert "Gestion des clients" in args[0][1]
        assert "Gestion des contrats" in args[0][1]
        assert "Gestion des évènements" in args[0][1]
        assert "Gestion des employés" in args[0][1]
        assert "Gestion des permissions" in args[0][1]
        assert "Deconnexion" in args[0][1]

    def test_menu_customer(self):
        self.menu_manage.permissions.role_name = Mock(return_value="Commercial")
        self.menu_manage.permissions.can_update_customer = Mock(return_value=True)
        self.menu_manage.permissions.can_create_delete_customer = Mock(return_value=True)
        self.menu_manage.run_menu = Mock()

        self.menu_manage.menu_customer()

        assert self.menu_manage.run_menu.called
        args, _ = self.menu_manage.run_menu.call_args
        assert "Liste des clients" in args[0][1]
        assert "Liste de vos clients" in args[0][1]
        assert "Modifier un client" in args[0][1]
        assert "Créer un client" in args[0][1]
        assert "Supprimer un client" in args[0][1]

    def test_menu_contract(self):
        self.menu_manage.permissions.role_name = Mock(return_value="Commercial")
        self.menu_manage.permissions.can_update_contract = Mock(return_value=True)
        self.menu_manage.permissions.can_create_delete_contract = Mock(return_value=True)
        self.menu_manage.run_menu = Mock()

        self.menu_manage.menu_contract()

        assert self.menu_manage.run_menu.called
        args, _ = self.menu_manage.run_menu.call_args
        assert "Liste des contrats" in args[0][1]
        assert "Liste de vos contrats" in args[0][1]
        assert "Liste de vos contrats non signés" in args[0][1]
        assert "Liste de vos contrats non payés" in args[0][1]
        assert "Modifier un contrat" in args[0][1]
        assert "Créer un contrat" in args[0][1]
        assert "Supprimer un contrat" in args[0][1]

    def test_menu_event(self):
        self.menu_manage.permissions.role_name = Mock(return_value="Support")
        self.menu_manage.permissions.can_update_event = Mock(return_value=True)
        self.menu_manage.permissions.can_create_delete_event = Mock(return_value=True)
        self.menu_manage.run_menu = Mock()

        self.menu_manage.menu_event()

        assert self.menu_manage.run_menu.called
        args, _ = self.menu_manage.run_menu.call_args
        assert "Liste des évènements" in args[0][1]
        assert "Liste des évènements sans support" in args[0][1]
        assert "Liste de vos évènements" in args[0][1]
        assert "Modifier un évènement" in args[0][1]
        assert "Créer un évènement" in args[0][1]
        assert "Supprimer un évènement" in args[0][1]

    def test_menu_employee(self):
        self.menu_manage.permissions.can_read_employee = Mock(return_value=True)
        self.menu_manage.permissions.can_update_employee = Mock(return_value=True)
        self.menu_manage.permissions.can_create_delete_employee = Mock(return_value=True)
        self.menu_manage.run_menu = Mock()

        self.menu_manage.menu_employee()

        assert self.menu_manage.run_menu.called
        args, _ = self.menu_manage.run_menu.call_args
        assert "Liste des employés" in args[0][1]
        assert "Modifier un employé" in args[0][1]
        assert "Créer un employé" in args[0][1]
        assert "Supprimer un employé" in args[0][1]

    def test_menu_role(self):
        self.menu_manage.permissions.can_read_role = Mock(return_value=True)
        self.menu_manage.permissions.can_update_role = Mock(return_value=True)
        self.menu_manage.permissions.can_create_delete_role = Mock(return_value=True)
        self.menu_manage.run_menu = Mock()

        self.menu_manage.menu_role()

        assert self.menu_manage.run_menu.called
        args, _ = self.menu_manage.run_menu.call_args
        assert "Liste des permissions" in args[0][1]
        assert "Modifier une permission" in args[0][1]
        assert "Créer une permission" in args[0][1]
        assert "Supprimer une permission" in args[0][1]


if __name__ == "__main__":
    pytest.main(["--cov=app/controllers/", "--cov-report=html", __file__])
