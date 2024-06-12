import pytest
from unittest.mock import patch, Mock, MagicMock
from datetime import datetime
from app.models.employee import Employee
from app.models.role import Role
from app.models.contract import Contract
from app.models.customer import Customer
from app.views.views import View
from app.controllers.contract_manage import ContractManage
from app.controllers.utils_manage import UtilsManage
from app.permissions.permissions import Permissions


class TestContractManage:
    """Tests unitaires pour la classe ContractManage"""

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

        self.test_employee = Employee(
            Id=1,
            FirstName="first name",
            LastName="last name",
            Email="email@email.com",
            PasswordHash="Password123",
            RoleId=1,
            DateCreated=datetime(2023, 1, 1),
        )

        self.test_customer = Customer(
            Id=1,
            CommercialId=1,
            FirstName="first name",
            LastName="last name",
            Email="email@email.com",
            PhoneNumber="000",
            Company="company",
            DateCreated=datetime(2023, 1, 1),
            DateLastUpdate=datetime(2023, 1, 1),
        )

        self.test_contract = Contract(
            Id=1,
            CustomerId=1,
            Title="title",
            Amount=1000,
            AmountOutstanding=1000,
            ContractSigned=False,
            DateCreated=datetime(2023, 1, 1),
        )

        self.contract_manage = ContractManage(self.session, self.test_employee, self.test_role)

        self.session.query.return_value.filter_by.return_value.one.return_value = self.test_contract

        self.mock_contract_class = patch("app.models.contract.Contract", autospec=True).start()
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
        self.mock_str_to_bool = patch.object(UtilsManage, "str_to_bool").start()
        self.mock_get_permissions_contracts = patch.object(ContractManage, "get_permissions_contracts").start()
        self.mock_get_permissions_customers = patch.object(ContractManage, "get_permissions_customers").start()
        self.mock_valid_customer = patch.object(ContractManage, "valid_customer").start()
        self.mock_validation_amount = patch.object(ContractManage, "validation_amount").start()
        self.mock_permissions_role_name = patch.object(Permissions, "role_name").start()
        self.mock_contract_validate_amount = patch.object(Contract, "validate_amount").start()

        yield

        patch.stopall()

    # test méthode list

    def test_list(self):
        """Test de la méthode list()"""

        # Arrang

        mock_contracts = [self.test_contract, self.test_contract]
        self.mock_filter.return_value = mock_contracts
        mock_table = Mock()
        self.mock_table_create.return_value = mock_table

        # Act
        self.contract_manage.list()

        # Assert
        self.mock_filter.assert_called_once_with(self.session, "All", None, Contract)
        self.mock_table_create.assert_called_once_with("contract", mock_contracts)
        self.mock_display_table.assert_called_once_with(mock_table, "Liste des Contrats")

    def test_list_yours_contracts(self):

        # Arrang
        mock_contracts = [self.test_contract, self.test_contract]
        self.mock_get_permissions_contracts.return_value = mock_contracts
        mock_table = Mock()
        self.mock_table_create.return_value = mock_table

        # Act
        self.contract_manage.list_yours_contracts()

        # Assert
        self.mock_get_permissions_contracts.assert_called_once()
        self.mock_table_create.assert_called_once_with("contract", mock_contracts)
        self.mock_display_table.assert_called_once_with(mock_table, "Liste de vos Contrats")

    def test_list_yours_contracts_not_signed_and_not_payed(self):

        # Arrang
        mock_contracts = [self.test_contract, self.test_contract]

        # Configurez le comportement de la query
        mock_query = MagicMock()
        mock_join = MagicMock()
        mock_filter1 = MagicMock()
        mock_filter2 = MagicMock()

        self.session.query.return_value = mock_query
        mock_query.join.return_value = mock_join
        mock_join.filter.return_value = mock_filter1
        mock_filter1.filter.return_value = mock_filter2
        mock_filter2.all.return_value = mock_contracts

        mock_table = Mock()
        self.mock_table_create.return_value = mock_table

        # Act
        self.contract_manage.list_yours_contracts_not_signed()

        # Assert
        self.mock_table_create.assert_called_with("contract", mock_contracts)
        self.mock_display_table.assert_called_with(mock_table, "Liste de vos Contrats non signés")

        # Act
        self.contract_manage.list_yours_contracts_not_payed()

        # Assert
        self.mock_table_create.assert_called_with("contract", mock_contracts)
        self.mock_display_table.assert_called_with(mock_table, "Liste de vos Contrats non payés")

# test méthode create

    def test_create_success(self):

        # Arrange

        mock_customers = [Customer(), Customer()]
        self.mock_get_permissions_customers.return_value = mock_customers
        self.mock_return_choice.side_effect = ["contract_title", "1", "100", "50", "oui"]
        self.mock_valid_customer.return_value = 1
        self.mock_validation_amount.side_effect = ["100", "50"]
        self.mock_str_to_bool.return_value = True
        self.mock_confirm_table_recap.return_value = True
        self.mock_permissions_role_name = "Gestion"

        # Act
        self.contract_manage.create()

        # Assert
        self.contract_manage.get_permissions_customers.assert_called_once()
        self.mock_valid_oper.assert_called_once()

    def test_create_with_no_customers(self):

        # Arrange

        mock_customers = []
        self.mock_get_permissions_customers.return_value = mock_customers

        # Act
        self.contract_manage.create()

        # Assert
        self.contract_manage.get_permissions_customers.assert_called_once()
        self.contract_manage.view.display_red_message.assert_called_once_with(
            "Aucuns clients autorisés pour le contrat !"
        )
        self.mock_valid_oper.assert_not_called()

    def test_create_with_no_title(self):

        # Arrange
        self.mock_return_choice.side_effect = [""]

        # Act
        self.contract_manage.create()

        # Assert
        self.mock_valid_oper.assert_not_called()

    def test_create_with_no_customer_id(self):

        # Arrange
        mock_customers = [Customer(), Customer()]
        self.mock_get_permissions_customers.return_value = mock_customers
        self.mock_return_choice.side_effect = ["contract_title", "1", "100", "50", "oui"]
        self.mock_valid_customer.return_value = ""
        self.mock_str_to_bool.return_value = True

        # Act
        self.contract_manage.create()

        # Assert
        self.contract_manage.get_permissions_customers.assert_called_once()
        self.mock_valid_oper.assert_not_called()

    # méthode update

    def test_update_success(self):

        self.mock_return_choice.side_effect = ["contract_title", "1", "100", "50", "oui"]

        # Arrange
        mock_contracts = [Contract(), Contract()]
        self.mock_get_permissions_contracts.return_value = mock_contracts
        mock_customers = [Customer(), Customer()]
        self.mock_get_permissions_customers.return_value = mock_customers
        self.mock_valid_id.return_value = Mock()
        self.mock_confirm_table_recap.return_value = True
        self.mock_validation_amount.side_effect = ["100", "50"]
        self.mock_permissions_role_name = "Gestion"

        # Act
        self.contract_manage.update()

        # Assert
        self.contract_manage.get_permissions_customers.assert_called_once()
        self.contract_manage.get_permissions_contracts.assert_called_once()
        self.mock_display_title_panel_color_fit.assert_called_with("Modification d'un contrat", "yellow", True)
        self.mock_valid_oper.assert_called()

    def test_update_with_no_customers(self):

        # Arrange
        mock_contracts = [Contract(), Contract()]
        self.mock_get_permissions_contracts.return_value = mock_contracts
        mock_customers = []
        self.mock_get_permissions_customers.return_value = mock_customers

        # Act
        self.contract_manage.update()

        # Assert
        self.contract_manage.get_permissions_customers.assert_called_once()
        self.contract_manage.get_permissions_contracts.assert_called_once()
        self.mock_display_red_message.assert_called_once_with("Aucuns clients autorisés pour le contrat !")
        self.mock_valid_oper.assert_not_called()

    def test_update_with_no_contracts(self):

        # Arrange
        mock_contracts = []
        self.mock_get_permissions_contracts.return_value = mock_contracts
        mock_customers = [Customer()]
        self.mock_get_permissions_customers.return_value = mock_customers

        # Act
        self.contract_manage.update()

        # Assert
        self.contract_manage.get_permissions_customers.assert_called_once()
        self.contract_manage.get_permissions_contracts.assert_called_once()
        self.mock_display_red_message.assert_called_once_with("Vous n'avez aucuns contrats à modifier !!!")
        self.mock_valid_oper.assert_not_called()

    def test_update_with_no_contract_id(self):

        # Arrange
        mock_contracts = [Contract]
        self.mock_get_permissions_contracts.return_value = mock_contracts
        mock_customers = [Customer()]
        self.mock_get_permissions_customers.return_value = mock_customers
        self.mock_valid_id.return_value = None

        # Act
        self.contract_manage.update()

        # Assert
        self.mock_valid_oper.assert_not_called()

    def test_update_with_no_confirmation(self):

        # Arrange
        mock_contracts = [Contract]
        self.mock_get_permissions_contracts.return_value = mock_contracts
        mock_customers = [Customer()]
        self.mock_get_permissions_customers.return_value = mock_customers
        self.mock_valid_id.return_value = Mock()
        self.mock_confirm_table_recap.return_value = False

        # Act
        self.contract_manage.update()

        # Assert
        self.mock_valid_oper.assert_not_called()

    # méthode delete

    def test_delete_success(self):

        # Arrange
        mock_contracts = [Contract]
        self.mock_get_permissions_contracts.return_value = mock_contracts
        self.mock_valid_id.return_value = Mock()

        # Act
        self.contract_manage.delete()

        # Assert
        self.mock_valid_oper.assert_called()
        self.mock_display_title_panel_color_fit.assert_called_once_with("Suppression d'un contrat", "red")

    def test_delete_with_no_contract(self):

        # Arrange
        mock_contracts = []
        self.mock_get_permissions_contracts.return_value = mock_contracts
        self.mock_valid_id.return_value = None

        # Act
        self.contract_manage.delete()

        # Assert
        self.mock_valid_oper.assert_not_called()


if __name__ == "__main__":
    pytest.main(["--cov=app/controllers/", "--cov-report=html", __file__])
