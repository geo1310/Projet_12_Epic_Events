import pytest
from unittest.mock import patch, Mock
from datetime import datetime
from app.models.customer import Customer
from app.models.employee import Employee
from app.models.role import Role
from app.views.views import View
from app.controllers.customer_manage import CustomerManage
from app.controllers.utils_manage import UtilsManage
from app.permissions.permissions import Permissions


class TestCustomerManage:
    """Tests unitaires pour la classe CustomerManage"""

    @pytest.fixture(autouse=True)
    def setup_method(self):

        self.session = Mock()
        self.customer = Mock(Customer)
        self.employee = Mock(Employee)
        self.role = Mock(Role)
        self.customer_manage = CustomerManage(self.session, self.employee, self.role)

        self.test_customer = Customer(
            Id=1,
            CommercialId=1,
            FirstName="John",
            LastName="Doe",
            Email="johndoe@example.com",
            PhoneNumber="000",
            Company="company",
            DateCreated=datetime.now(),
            DateLastUpdate=datetime.now(),
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
        self.mock_validation_email = patch.object(CustomerManage, "validation_email").start()
        self.mock_customer_validate_email = patch.object(Customer, "validate_email").start()
        self.mock_permissions_role_name = patch.object(Permissions, "role_name").start()

        yield

        patch.stopall()

    # méthode list

    def test_list(self):

        # Arrang
        mock_customers = [Mock(), Mock()]
        self.mock_filter.return_value = mock_customers
        self.mock_table_create.return_value = Mock()

        # Act
        self.customer_manage.list()

        # Assert
        self.mock_filter.assert_called_once_with(self.session, "All", None, Customer)
        self.mock_table_create.assert_called_once_with("customer", mock_customers)
        self.mock_display_table.assert_called_once()

    def test_list_yours_customers(self):

        # Arrang
        mock_customers = [Mock(), Mock()]
        self.mock_permissions_role_name.return_value = "Commercial"
        self.mock_filter.return_value = mock_customers
        self.mock_table_create.return_value = Mock()

        # Act
        self.customer_manage.list_yours_customers()

        # Assert
        self.mock_permissions_role_name.assert_called_once_with(self.role)
        self.mock_filter.assert_called_once_with(self.session, "CommercialId", self.employee.Id, Customer)
        self.mock_table_create.assert_called_once_with("customer", mock_customers)
        self.mock_display_table.assert_called_once()

    # méthode create

    def test_create_success(self):

        # Arrang
        self.mock_return_choice.side_effect = ["John", "Doe", "123456789", "ABC Inc."]
        self.mock_validation_email.return_value = "email@email.com"

        # Act
        self.customer_manage.create()

        # Assert
        self.mock_display_green_message.assert_called_once_with("Email validé !")
        self.mock_return_choice.assert_called()
        self.mock_valid_oper.assert_called()

    def test_create_with_no_email(self):

        # Arrang
        self.mock_return_choice.side_effect = ["John", "Doe"]
        self.mock_validation_email.return_value = None

        # Act
        self.customer_manage.create()

        # Assert
        self.mock_valid_oper.assert_not_called()

    # méthode update

    def test_update_success(self):

        # Arrang
        self.mock_return_choice.side_effect = ["John", "Doe", "eamil@email.com", "123456789", "ABC Inc."]
        self.mock_valid_id.return_value = self.test_customer
        self.mock_confirm_table_recap.return_value = True
        self.mock_validation_email.return_value = "email@email.com"

        # Act
        self.customer_manage.update()

        # Assert
        self.mock_display_title_panel_color_fit.assert_called()
        self.mock_return_choice.assert_called()
        self.mock_valid_oper.assert_called()

    def test_update_with_no_customer(self):

        # Arrang
        self.mock_valid_id.return_value = None

        # Act
        self.customer_manage.update()

        # Assert
        self.mock_display_title_panel_color_fit.assert_called()
        self.mock_return_choice.assert_not_called()
        self.mock_valid_oper.assert_not_called()

    def test_update_with_no_validation(self):

        # Arrang
        self.mock_valid_id.return_value = self.test_customer
        self.mock_confirm_table_recap.return_value = False

        # Act
        self.customer_manage.update()

        # Assert
        self.mock_return_choice.assert_not_called()
        self.mock_valid_oper.assert_not_called()

    # méthode delete

    def test_delete_success(self):

        # Arrang
        self.mock_valid_id.return_value = self.test_customer

        # Act
        self.customer_manage.delete()

        # Assert
        self.mock_display_title_panel_color_fit.assert_called_once_with("Suppression d'un client", "red")
        self.mock_valid_oper.assert_called()

    def test_delete_with_no_customer(self):

        # Arrang
        self.mock_valid_id.return_value = None

        # Act
        self.customer_manage.delete()

        # Assert
        self.mock_valid_oper.assert_not_called()


if __name__ == "__main__":
    pytest.main(["--cov=app/controllers/", "--cov-report=html", __file__])
