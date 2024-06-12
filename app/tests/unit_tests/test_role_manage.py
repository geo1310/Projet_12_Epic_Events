import pytest
from unittest.mock import patch, Mock
from datetime import datetime
from app.models.role import Role
from app.models.employee import Employee
from app.views.views import View
from app.controllers.role_manage import RoleManage
from app.controllers.utils_manage import UtilsManage


class TestRoleManage:
    """Tests unitaires pour la classe RoleManage"""

    @pytest.fixture(autouse=True)
    def setup_method(self):
        self.session = Mock()
        self.view = Mock()
        self.session.rollback = Mock()
        self.session.add = Mock()
        self.session.flush = Mock()
        self.session.commit = Mock()
        self.session.expunge = Mock()
        self.session.query = Mock()
        self.session.update = Mock()
        self.session.delete = Mock()
        self.employee = Mock(Employee)
        self.role_manage = RoleManage(self.session, self.employee)
        self.utils_manage = UtilsManage(self.employee)

        self.test_role = Role(
            Id=1,
            RoleName="Admin",
            Can_r_Employee=True,
            Can_ru_Employee=True,
            Can_crud_Employee=True,
            Can_r_Role=True,
            Can_ru_Role=True,
            Can_crud_Role=True,
            Can_ru_Customer=True,
            Can_crud_Customer=True,
            Can_access_all_Customer=True,
            Can_ru_Contract=True,
            Can_crud_Contract=True,
            Can_access_all_Contract=True,
            Can_ru_Event=True,
            Can_crud_Event=True,
            Can_access_all_Event=True,
            Can_access_support_Event=True,
            DateCreated=datetime(2023, 1, 1),
        )

        self.session.query.return_value.filter_by.return_value.one.return_value = self.test_role

        self.mock_role_class = patch("app.models.role.Role", autospec=True).start()
        self.mock_confirm_table_recap = patch.object(UtilsManage, "confirm_table_recap").start()
        self.mock_return_choice = patch.object(View, "return_choice").start()
        self.mock_display_red_message = patch.object(View, "display_red_message").start()
        self.mock_display_green_message = patch.object(View, "display_green_message").start()
        self.mock_display_title_panel_color_fit = patch.object(View, "display_title_panel_color_fit").start()
        self.mock_display_table = patch.object(View, "display_table").start()
        self.mock_table_create = patch.object(UtilsManage, "table_create").start()
        self.mock_filter = patch.object(UtilsManage, "filter").start()
        self.mock_valid_oper = patch.object(UtilsManage, "valid_oper").start()
        self.mock_valid_id = patch.object(UtilsManage, "valid_id").start()

        yield

        patch.stopall()

    # test méthode list

    def test_list(self):

        # Arrang
        mock_roles = [self.test_role]
        self.mock_filter.return_value = mock_roles
        mock_table = Mock()
        self.mock_table_create.return_value = mock_table

        # Act
        self.role_manage.list()

        # Assert
        self.mock_filter.assert_called_once_with(self.session, "All", None, Role)
        self.mock_table_create.assert_called_once_with("role", mock_roles)
        self.mock_display_table.assert_called_once_with(mock_table, "Liste des Roles")

    # test méthode create

    def test_create_success(self):
       
        # Arrang
        role_name = "Admin"
        self.mock_return_choice.side_effect = [
            role_name,
            "1",
            "1",
            "1",
            "1",
            "1",
            "1",
            "1",
            "1",
            "1",
            "1",
            "1",
            "1",
            "1",
            "1",
            "1",
            "1",
        ]

        self.mock_confirm_table_recap.return_value = True

        # Act
        self.role_manage.create()

        # Assert
        self.mock_return_choice.assert_any_call("Entrez le nom du role ( vide pour annuler )", False)
        self.mock_return_choice.assert_any_call("Liste des employés ( 0:non(défaut) / 1:oui )", False, "0")
        self.mock_return_choice.assert_any_call("Modification des employés ( 0:non(défaut) / 1:oui )", False, "0")
        self.mock_return_choice.assert_any_call(
            "Création et Suppression des employés ( 0:non(défaut) / 1:oui )", False, "0"
        )
        self.mock_return_choice.assert_any_call("Liste des roles ( 0:non(défaut) / 1:oui )", False, "0")
        self.mock_return_choice.assert_any_call("Modification des roles ( 0:non(défaut) / 1:oui )", False, "0")
        self.mock_return_choice.assert_any_call(
            "Création et Suppression des roles ( 0:non(défaut) / 1:oui )", False, "0"
        )
        self.mock_return_choice.assert_any_call("Modification des clients ( 0:non(défaut) / 1:oui )", False, "0")
        self.mock_return_choice.assert_any_call(
            "Création et Suppression des clients ( 0:non(défaut) / 1:oui )", False, "0"
        )
        self.mock_return_choice.assert_any_call("Acces à tous les clients ( 0:non(défaut) / 1:oui )", False, "0")
        self.mock_return_choice.assert_any_call("Modification des contrats ( 0:non(défaut) / 1:oui )", False, "0")
        self.mock_return_choice.assert_any_call(
            "Création et Suppression des contrats ( 0:non(défaut) / 1:oui )", False, "0"
        )
        self.mock_return_choice.assert_any_call("Acces à tous les contrats ( 0:non(défaut) / 1:oui )", False, "0")
        self.mock_return_choice.assert_any_call("Modification des évènements ( 0:non(défaut) / 1:oui )", False, "0")
        self.mock_return_choice.assert_any_call(
            "Création et Suppression des évènements ( 0:non(défaut) / 1:oui )", False, "0"
        )
        self.mock_return_choice.assert_any_call("Acces à tous les évènements ( 0:non(défaut) / 1:oui )", False, "0")
        self.mock_return_choice.assert_any_call(
            "Accés au support des évènements ( 0:non(défaut) / 1:oui )", False, "0"
        )

        self.mock_valid_oper.called_once()

    # test méthode update

    def test_update_success(self):

        # Arrang
        new_role_name = "New"
        self.mock_return_choice.side_effect = [
            str(self.test_role.Id),
            new_role_name,
            "1",
            "1",
            "1",
            "1",
            "1",
            "1",
            "1",
            "1",
            "1",
            "1",
            "1",
            "1",
            "1",
            "1",
            "1",
            "1",
        ]
        self.mock_valid_id.return_value = Mock()
        self.mock_confirm_table_recap.return_value = True

        # Act
        self.role_manage.update()

        # Assert
        self.mock_display_title_panel_color_fit.assert_called_with("Modification d'un role", "yellow", True)
        self.mock_valid_oper.called_once()

    def test_update_cancelled_due_to_empty_id(self):
        
        # Arrang
        self.mock_valid_id.return_value = None

        # Act
        self.role_manage.update()

        # Assert
        self.mock_confirm_table_recap.assert_not_called()
        self.mock_valid_oper.assert_not_called()

    def test_update_cancelled_due_to_confirmation(self):

        # Arrang
        new_role_name = "New"
        self.mock_return_choice.side_effect = [
            str(self.test_role.Id),
            new_role_name,
            "1",
            "1",
            "1",
            "1",
            "1",
            "1",
            "1",
            "1",
            "1",
            "1",
            "1",
            "1",
            "1",
            "1",
            "1",
            "1",
        ]
        self.mock_valid_id.return_value = Mock()
        self.mock_confirm_table_recap.return_value = False

        # Act
        self.role_manage.update()

        # Assert
        self.mock_valid_oper.assert_not_called()

    # test méthode delete

    def test_delete_success(self):
        
        # Arrang
        self.mock_valid_id.return_value = Mock()

        # Act
        self.role_manage.delete()

        # Assert
        self.mock_display_title_panel_color_fit.assert_called_with("Suppression d'un role", "red")
        self.mock_valid_oper.called_once()

    def test_delete_cancelled_due_to_empty_id(self):
        
        # Arrang
        self.mock_valid_id.return_value = None

        # Act
        self.role_manage.delete()

        # Assert
        self.mock_display_title_panel_color_fit.called_once()
        self.mock_valid_oper.assert_not_called()


if __name__ == "__main__":
    pytest.main(["--cov=app/controllers/", "--cov-report=html", __file__])
