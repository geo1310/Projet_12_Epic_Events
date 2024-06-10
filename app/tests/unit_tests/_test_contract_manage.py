import pytest
from unittest.mock import patch, Mock
from sqlalchemy.exc import IntegrityError, NoResultFound
from rich.table import Table
from datetime import datetime
from app.models.employee import Employee
from app.models.role import Role
from app.models.contract import Contract
from app.models.customer import Customer
from app.views.views import View
from app.controllers.contract_manage import ContractManage


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
            DateCreated=datetime(2023, 1, 1)
        )
        
        self.test_employee = Employee(
            Id = 1,  # mettre index=True sur les champs ???
            FirstName = "first name",
            LastName = 'last name',
            Email = 'email@email.com',
            PasswordHash = 'Password123',
            RoleId = 1,
            DateCreated=datetime(2023, 1, 1)
        )

        self.test_customer = Customer(
            Id = 1,
            CommercialId = 1,
            FirstName = 'first name',
            LastName = 'last name',
            Email = 'email@email.com',
            PhoneNumber = '000',
            Company = 'company',
            DateCreated=datetime(2023, 1, 1),
            DateLastUpdate = datetime(2023, 1, 1)
        )

        self.test_contract = Contract(
            Id = 1,
            CustomerId = 1,
            Title = "title",
            Amount = 1000,
            AmountOutstanding = 1000,
            ContractSigned = False,
            DateCreated=datetime(2023, 1, 1),
        )

        self.contract_manage = ContractManage(self.session, self.test_employee, self.test_role)

        self.session.query.return_value.filter_by.return_value.one.return_value = self.test_contract

        self.mock_contract_class = patch("app.models.contract.Contract", autospec=True).start()
        self.mock_confirm_table_recap = patch.object(ContractManage, "confirm_table_recap").start()
        self.mock_return_choice = patch.object(View, "return_choice").start()
        self.mock_display_red_message = patch.object(View, "display_red_message").start()
        self.mock_display_green_message = patch.object(View, "display_green_message").start()
        self.mock_display_title_panel_color_fit = patch.object(View, "display_title_panel_color_fit").start()
        self.mock_display_table = patch.object(View, "display_table").start()
        self.mock_table_contract_create = patch.object(ContractManage, "table_contract_create").start()
        self.mock_get_permissions_contracts = patch.object(ContractManage, "get_permissions_contracts").start()
        self.mock_get_permissions_customers = patch.object(ContractManage, "get_permissions_customers").start()
        self.mock_valid_customer = patch.object(ContractManage, "valid_customer").start()
        self.mock_validation_amount = patch.object(ContractManage, "validation_amount").start()
        self.mock_str_to_bool = patch.object(ContractManage, "str_to_bool").start()

        yield

        patch.stopall()

    # test méthode list

    def test_list(self):
        """Test de la méthode list()"""
        with patch.object(ContractManage, "filter") as mock_filter:

            # Arrangement
            
            mock_contracts = [self.test_contract, self.test_contract ]
            mock_filter.return_value = mock_contracts
            mock_table = Mock()

            self.mock_table_contract_create.return_value = mock_table

            # Action
            self.contract_manage.list()

            # Assertions
            mock_filter.assert_called_once_with("All", None, Contract)
            self.mock_table_contract_create.assert_called_once_with(mock_contracts)
            self.mock_display_table.assert_called_once_with(mock_table, "Liste des Contrats")

    # test méthode create

    def test_create_success(self):

        # Arrange
            
            mock_customers = [Customer(), Customer()]
            self.contract_manage.get_permissions_customers.return_value = mock_customers
            self.contract_manage.view.return_choice.side_effect = ["contract_title", "1", "100", "50", "oui"]
            self.contract_manage.valid_customer.return_value = 1
            self.contract_manage.validation_amount.side_effect = ["100", "50"]
            self.contract_manage.str_to_bool.return_value = True
            self.contract_manage.confirm_table_recap.return_value = True
            
            # Act
            self.contract_manage.create()
            
            # Assert
            self.contract_manage.get_permissions_customers.assert_called_once()
            self.session.add.assert_called_once()
            self.session.flush.assert_called_once()
            self.session.commit.assert_called_once()
            self.contract_manage.view.display_green_message.assert_called_once_with("\nContrat créé avec succès !")

    def test_create_with_no_customers(self):

        # Arrange
            
            mock_customers = []
            self.contract_manage.get_permissions_customers.return_value = mock_customers
            
            # Act
            self.contract_manage.create()
            
            # Assert
            self.contract_manage.get_permissions_customers.assert_called_once()
            self.session.add.assert_not_called()
            self.contract_manage.view.display_red_message.assert_called_once_with("Aucuns clients autorisés pour le contrat !")
    
    # test méthode table_contract_create

    def test_table_contract_create(self):
        """Test de la méthode table_contract_create()"""

        # self.mock_table_role_create.stop()
        patch.stopall()

        contracts = [self.test_contract, self.test_contract]

        table = self.contract_manage.table_contract_create(contracts)

        assert isinstance(table, Table)
        assert len(table.columns) == 10
        assert len(table.rows) == 2

    # test filter

    def test_filter_no_filtering(self):
        """Test de la méthode filter() sans filtrage"""
        self.session.query.return_value.all.return_value = [self.test_contract]

        result = self.contract_manage.filter("All", None, Contract)

        self.session.query.assert_called_once_with(Contract)
        self.session.query.return_value.all.assert_called_once()
        assert result == [self.test_contract]

    def test_filter_with_filtering(self):
        """Test de la méthode filter() avec filtrage"""
        self.session.query.return_value.filter.return_value.all.return_value = [self.test_contract]

        result = self.contract_manage.filter("Title", "title", Contract)

        self.session.query.assert_called_once_with(Contract)
        self.session.query.return_value.filter.assert_called_once()
        self.session.query.return_value.all.assert_not_called()
        assert result == [self.test_contract]

    def test_filter_with_filtering_valuenone(self):
        """Test de la méthode filter() avec filtrage et valeur Null"""
        self.session.query.return_value.filter.return_value.all.return_value = None

        result = self.contract_manage.filter("Title", None, Contract)

        self.session.query.assert_called_once_with(Contract)
        self.session.query.return_value.filter.assert_called_once()
        self.session.query.return_value.all.assert_not_called()
        assert result is None
    
    # test format_date

    def test_format_date_with_valid_date(self):
        # Date valide
        test_date = datetime(2023, 6, 7, 15, 30)
        formatted_date = self.contract_manage.format_date(test_date)
        assert formatted_date == "07/06/2023 15:30"

    # test confirm table

    def test_confirm_table_recap_confirmation_yes(self):
        """Test de la méthode confirm_table_recap avec confirmation 'oui'"""

        patch.stopall()

        with patch.object(View, "return_choice") as mock_return_choice, patch.object(
            View, "display_red_message"
        ) as mock_display_red_message, patch.object(
            View, "display_title_panel_color_fit"
        ) as mock_display_title_panel_color_fit, patch.object(
            View, "display_table"
        ) as mock_display_table, patch.object(
            ContractManage, "table_contract_create"
        ) as mock_table_contract_create:

            mock_return_choice.side_effect = ["oui"]

            mock_table = Mock()
            mock_table_contract_create.return_value = mock_table

            contract = self.test_contract

            # Appel de la méthode confirm_table_recap
            result = self.contract_manage.confirm_table_recap(contract, "Suppression", "red")

            # Vérifications
            mock_display_title_panel_color_fit.assert_called_once_with("Suppression d'un contrat", "red", True)
            mock_display_table.assert_called_once()
            mock_return_choice.assert_called_once_with("Confirmation Suppression ? (oui/non)", False)
            mock_display_red_message.assert_not_called()
            assert result is True

    def test_confirm_table_recap_confirmation_no(self):
        """Test de la méthode confirm_table_recap avec annulation"""

        # self.mock_confirm_table_recap.stop()

        patch.stopall()

        with patch.object(View, "return_choice") as mock_return_choice, \
        patch.object(View, "display_red_message") as mock_display_red_message, \
        patch.object(View, "display_table") as mock_display_table, \
        patch.object(ContractManage, "table_contract_create") as mock_table_contract_create:

            mock_return_choice.side_effect = ["non"]
            mock_table = Mock()
            mock_display_table(mock_table)
            mock_table_contract_create.return_value = mock_table

            contract = self.test_contract

            # Appel de la méthode confirm_table_recap
            result = self.contract_manage.confirm_table_recap(contract, "Suppression", "red")

            # Vérifications
            mock_display_red_message.assert_called()
            assert result is False



if __name__ == "__main__":
    pytest.main([__file__])
