from datetime import datetime
from unittest.mock import Mock, patch

import pytest

from app.controllers.employee_manage import EmployeeManage
from app.controllers.utils_manage import UtilsManage
from app.models.employee import Employee
from app.models.role import Role
from app.views.views import View


class TestEmployeeManage:
    """Tests unitaires pour la classe EmployeeManage"""

    @pytest.fixture(autouse=True)
    def setup_method(self):
        self.session = Mock()

        self.employee = Mock(Employee)
        self.role = Mock(Role)
        self.employee_manage = EmployeeManage(self.session, self.employee, self.role)

        self.test_employee = Employee(
            Id=1,
            FirstName="John",
            LastName="Doe",
            Email="johndoe@example.com",
            PasswordHash="Password123",
            RoleId=1,
            DateCreated=datetime(2023, 1, 1),
        )

        self.test_role = Role(
            Id=1,
            RoleName="Admin",
            DateCreated=datetime(2023, 1, 1),
        )

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
        self.mock_validation_email = patch.object(EmployeeManage, "validation_email").start()
        self.mock_validation_password = patch.object(EmployeeManage, "validation_password").start()
        self.mock_valid_role = patch.object(EmployeeManage, "valid_role").start()
        self.mock_employee_validate_email = patch.object(Employee, "validate_email").start()

        yield

        patch.stopall()

    # test méthode list

    def test_list(self):

        # Arrang
        mock_employees = [self.test_employee]
        self.mock_filter.return_value = mock_employees
        mock_table = Mock()
        self.mock_table_create.return_value = mock_table

        # Act
        self.employee_manage.list()

        # Assert
        self.mock_filter.assert_called_once_with(self.session, "All", None, Employee)
        self.mock_table_create.assert_called_once_with("employee", mock_employees)
        self.mock_display_table.assert_called_once_with(mock_table, "Liste des Employés")

    # test méthode create

    def test_create_success(self):

        # Arrang
        first_name = "John"
        last_name = "Doe"
        email = "email@email.com"
        password = "Password123"

        self.mock_return_choice.side_effect = [
            first_name,
            last_name,
        ]

        self.mock_validation_email.return_value = email
        self.mock_validation_password.return_value = password
        self.mock_valid_role.return_value = 1
        self.mock_confirm_table_recap.return_value = True
        self.mock_valid_oper.return_value = True

        # Act
        self.employee_manage.create()

        # Assert
        self.mock_valid_oper.assert_called_once()

    def test_create_with_no_email(self):

        # Arrang
        first_name = "John"
        last_name = "Doe"

        self.mock_return_choice.side_effect = [
            first_name,
            last_name,
        ]

        self.mock_validation_email.return_value = None

        # Act
        self.employee_manage.create()

        # Assert
        self.mock_valid_oper.assert_not_called()
        self.mock_display_red_message.assert_not_called()

    def test_create_with_no_password(self):

        # Arrang
        first_name = "John"
        last_name = "Doe"
        email = "email@email.com"

        self.mock_return_choice.side_effect = [
            first_name,
            last_name,
        ]

        self.mock_validation_email.return_value = email
        self.mock_validation_password.return_value = None

        # Act
        self.employee_manage.create()

        # Assert
        self.mock_valid_oper.assert_not_called()
        self.mock_display_red_message.assert_not_called()

    def test_create_with_no_role(self):

        # Arrang
        first_name = "John"
        last_name = "Doe"
        email = "email@email.com"
        password = "Password123"

        self.mock_return_choice.side_effect = [
            first_name,
            last_name,
        ]

        self.mock_validation_email.return_value = email
        self.mock_validation_password.return_value = password
        self.mock_valid_role.return_value = None

        # Act
        self.employee_manage.create()

        # Assert
        self.mock_valid_oper.assert_not_called()

    # test méthode update

    def test_update_success(self):

        # Arrang
        new_first_name = "Jane"
        new_last_name = "Smith"
        new_email = "email@email.com"

        self.mock_return_choice.side_effect = [new_first_name, new_last_name, new_email, "oui"]
        self.mock_valid_id.return_value = self.test_employee
        self.mock_confirm_table_recap.return_value = True
        self.mock_validation_email.return_value = "email@email.com"
        self.mock_validation_password.return_value = "Password123"
        self.mock_valid_role.return_value = 1

        # Act
        self.employee_manage.update()

        # Assert
        self.mock_display_title_panel_color_fit.assert_called_with("Modification d'un employé", "yellow", True)
        self.mock_valid_oper.assert_called_once()

    def test_update_with_no_employee(self):

        # Arrang
        self.mock_valid_id.return_value = None

        # Act
        self.employee_manage.update()

        # Assert
        self.mock_display_title_panel_color_fit.assert_called_with("Modification d'un employé", "yellow")
        self.mock_valid_oper.assert_not_called()

    def test_update_with_no_validation(self):

        # Arrang
        self.mock_valid_id.return_value = self.employee
        self.mock_confirm_table_recap.return_value = False

        # Act
        self.employee_manage.update()

        # Assert
        self.mock_display_title_panel_color_fit.assert_called_with("Modification d'un employé", "yellow")
        self.mock_valid_oper.assert_not_called()

    def test_update_with_no_role_id(self):

        # Arrang
        new_first_name = "Jane"
        new_last_name = "Smith"
        new_email = "email@email.com"

        self.mock_return_choice.side_effect = [new_first_name, new_last_name, new_email, "non"]
        self.mock_valid_id.return_value = self.test_employee
        self.mock_confirm_table_recap.return_value = True
        self.mock_validation_email.return_value = "email@email.com"
        self.mock_validation_password.return_value = "Password123"
        self.mock_valid_role.return_value = None

        # Act
        self.employee_manage.update()

        # Assert
        self.mock_valid_oper.assert_not_called()

    def test_update_with_no_password(self):

        # Arrang
        new_first_name = "Jane"
        new_last_name = "Smith"
        new_email = "email@email.com"

        self.mock_return_choice.side_effect = [new_first_name, new_last_name, new_email, "oui"]
        self.mock_valid_id.return_value = self.test_employee
        self.mock_confirm_table_recap.return_value = True
        self.mock_validation_email.return_value = "email@email.com"
        self.mock_validation_password.return_value = None
        self.mock_valid_role.return_value = 1

        # Act
        self.employee_manage.update()

        # Assert
        self.mock_valid_oper.assert_not_called()

    # méthode delete

    def test_delete_success(self):

        # Arrang
        self.mock_valid_id.return_value = self.test_employee

        # Act
        self.employee_manage.delete()

        # Assert
        self.mock_valid_oper.assert_called_once()

    def test_delete_with_no_employee(self):

        # Arrang
        self.mock_valid_id.return_value = None

        # Act
        self.employee_manage.delete()

        # Assert
        self.mock_valid_oper.assert_not_called()

    def test_validation_password(self):

        # Arrang 1 success
        patch.stopall()
        mock_return_choice = patch.object(View, "return_choice").start()
        mock_validate_password_hash = patch.object(Employee, "validate_password_hash").start()
        mock_display_red_message = patch.object(View, "display_red_message").start()
        password = "Password123"
        mock_return_choice.side_effect = [password, password, ""]
        mock_validate_password_hash.return_value = password

        # Act 1 success
        result = self.employee_manage.validation_password()

        # Assert 1 sucess
        assert result == password

        # Arrang 2 fail no password
        password = ""
        mock_return_choice.side_effect = [password, ""]
        mock_validate_password_hash.return_value = password

        # Arrang 2 fail no password
        result = self.employee_manage.validation_password()

        # Arrang 2 fail no password
        assert result == None

        # Arrang 3 fail no confirm password
        password = "Password123"
        mock_return_choice.side_effect = [password, "", ""]
        mock_validate_password_hash.return_value = password

        # Arrang 3 fail no confirm password
        result = self.employee_manage.validation_password()

        # Arrang 3 fail no confirm password
        assert result == None

        # Arrang 4 fail password != confirm password
        password = "Password123"
        mock_return_choice.side_effect = [password, password + "xxx", ""]
        mock_validate_password_hash.return_value = password

        # Arrang 4 fail password != confirm password
        result = self.employee_manage.validation_password()

        # Arrang 4 fail password != confirm password
        assert result == None
        mock_display_red_message.assert_called_with("Les mots de passe ne correspondent pas.")

        # Arrang 5 fail validate_password_hash
        password = "Password123"
        mock_return_choice.side_effect = [password, password, ""]
        mock_validate_password_hash.side_effect = ValueError("Invalid password")

        # Act 5 fail validate_password_hash
        result = self.employee_manage.validation_password()

        # Assert 5 fail validate_password_hash
        assert result == None
        mock_display_red_message.assert_called_with("Erreur de validation : Invalid password")

    def test_validation_email(self):

        # Arrang 1 success
        patch.stopall()
        mock_return_choice = patch.object(View, "return_choice").start()
        mock_validate_email = patch.object(Employee, "validate_email").start()
        mock_display_red_message = patch.object(View, "display_red_message").start()
        email = "EMAIL@email.com"
        mock_return_choice.side_effect = [email, ""]
        mock_validate_email.return_value = email.lower()

        # Act 1 success
        result = self.employee_manage.validation_email()

        # Assert 1 sucess
        assert result == email

        # Arrang 2 fail no email
        email = ""
        mock_return_choice.side_effect = [email, ""]

        # Act 2 fail no email
        result = self.employee_manage.validation_email()

        # Assert 2 fail no email
        assert result == None

        # Arrang 3 fail bad email
        email = "EMAIL@email.com"
        mock_return_choice.side_effect = [email, ""]
        mock_validate_email.side_effect = ValueError("Invalid email")

        # Act 3 fail bad email
        result = self.employee_manage.validation_email()

        # Assert 3 fail bad email
        assert result == None
        mock_display_red_message.assert_called_with("Erreur de validation : Invalid email")


if __name__ == "__main__":
    pytest.main(["--cov=app/controllers/", "--cov-report=html", __file__])
