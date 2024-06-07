from unittest.mock import patch, MagicMock
from sqlalchemy.exc import IntegrityError
from app.models.contract import Contract
from app.models.customer import Customer
from app.views.views import View
from app.permissions.permissions import Permissions
from app.models.database import SessionLocal
from app.controllers.contract_manage import ContractManage

class TestContractManage():
    """Tests unitaires pour la classe ContractManage"""

    def test_list(self):
        """Test de la méthode list()"""
        with patch.object(ContractManage, 'filter'), \
             patch.object(ContractManage, 'table_contract_create'), \
             patch.object(View, 'display_table'):
            
            # Arrange
            contract_manage = ContractManage(self.session, self.employee, self.role)
            mock_contracts = [Contract(), Contract()]
            contract_manage.filter.return_value = mock_contracts
            mock_table = MagicMock()
            contract_manage.table_contract_create.return_value = mock_table
            
            # Act
            contract_manage.list()
            
            # Assert
            contract_manage.filter.assert_called_once_with("All", None, Contract)
            contract_manage.table_contract_create.assert_called_once_with(mock_contracts)
            contract_manage.view.display_table.assert_called_once_with(mock_table, "Liste des Contrats")

    def test_list_yours_contracts(self):
        """Test de la méthode list_yours_contracts()"""
        with patch.object(ContractManage, 'get_permissions_contracts'), \
             patch.object(ContractManage, 'table_contract_create'), \
             patch.object(View, 'display_table'):
            
            # Arrange
            contract_manage = ContractManage(self.session, self.employee, self.role)
            mock_contracts = [Contract(), Contract()]
            contract_manage.get_permissions_contracts.return_value = mock_contracts
            mock_table = MagicMock()
            contract_manage.table_contract_create.return_value = mock_table
            
            # Act
            contract_manage.list_yours_contracts()
            
            # Assert
            contract_manage.get_permissions_contracts.assert_called_once()
            contract_manage.table_contract_create.assert_called_once_with(mock_contracts)
            contract_manage.view.display_table.assert_called_once_with(mock_table, "Liste de vos Contrats")

    def test_create(self):
        """Test de la méthode create()"""
        with patch.object(ContractManage, 'get_permissions_customers'), \
             patch.object(View, 'return_choice'), \
             patch.object(ContractManage, 'valid_customer'), \
             patch.object(ContractManage, 'validation_amount'), \
             patch.object(ContractManage, 'str_to_bool'), \
             patch.object(ContractManage, 'confirm_table_recap'), \
             patch.object(SessionLocal, 'add'), \
             patch.object(SessionLocal, 'flush'), \
             patch.object(SessionLocal, 'commit'), \
             patch.object(View, 'display_green_message'), \
             patch.object(SessionLocal, 'rollback'), \
             patch.object(View, 'display_red_message'), \
             patch.object(ContractManage, 'permissions'), \
             patch.object(ContractManage, 'sentry_event'):
            
            # Arrange
            contract_manage = ContractManage(self.session, self.employee, self.role)
            mock_customers = [Customer(), Customer()]
            contract_manage.get_permissions_customers.return_value = mock_customers
            contract_manage.view.return_choice.side_effect = ["contract_title", "1", "100", "50", "oui"]
            contract_manage.valid_customer.return_value = 1
            contract_manage.validation_amount.side_effect = ["100", "50"]
            contract_manage.str_to_bool.return_value = True
            contract_manage.confirm_table_recap.return_value = True
            
            # Act
            contract_manage.create()
            
            # Assert
            contract_manage.get_permissions_customers.assert_called_once()
            assert contract_manage.contract.Title == "contract_title"
            assert contract_manage.contract.CustomerId == 1
            assert contract_manage.contract.Amount == 100
            assert contract_manage.contract.AmountOutstanding == 50
            assert contract_manage.contract.ContractSigned == True
            self.session.add.assert_called_once_with(contract_manage.contract)
            self.session.flush.assert_called_once()
            self.session.commit.assert_called_once()
            contract_manage.view.display_green_message.assert_called_once_with("\nContrat créé avec succès !")
            contract_manage.sentry_event.assert_called_once_with(self.employee.Email, f"Contrat Signé: Titre: {contract_manage.contract.Title} - Email du Client: {contract_manage.contract.CustomerRel.Email}", "Contract_signed")

    def test_update(self):
        """Test de la méthode update()"""
        with patch.object(ContractManage, 'get_permissions_contracts'), \
             patch.object(ContractManage, 'get_permissions_customers'), \
             patch.object(View, 'return_choice'), \
             patch.object(View, 'display_title_panel_color_fit'), \
             patch.object(SessionLocal, 'query'), \
             patch.object(ContractManage, 'confirm_table_recap'), \
             patch.object(SessionLocal, 'commit'), \
             patch.object(View, 'display_green_message'), \
             patch.object(SessionLocal, 'rollback'), \
             patch.object(View, 'display_red_message'), \
             patch.object(ContractManage, 'validation_amount'), \
             patch.object(ContractManage, 'str_to_bool'), \
             patch.object(ContractManage, 'permissions'):
            
            # Arrange
            contract_manage = ContractManage(self.session, self.employee, self.role)
            mock_contracts = [Contract(Id=1, Title="contract_title", Amount=100, AmountOutstanding=50, ContractSigned=False)]
            contract_manage.get_permissions_contracts.return_value = mock_contracts
            mock_customers = [Customer(), Customer()]
            contract_manage.get_permissions_customers.return_value = mock_customers
            contract_manage.view.return_choice.side_effect = ["1", "new_title", "150", "25", "oui"]
            contract_manage.session.query().filter_by().one.return_value = mock_contracts[[1]]
            contract_manage.validation_amount.side_effect = ["150", "25"]
            contract_manage.str_to_bool.return_value = True
            contract_manage.confirm_table_recap.return_value = True
            
            # Act
            contract_manage.update()
            
            # Assert
            contract_manage.get_permissions_contracts.assert_called_once()
            contract_manage.get_permissions_customers.assert_called_once()
            self.session.query.assert_called_once_with(Contract)
            self.session.query().filter_by.assert_called_once_with(Id=1)
            self.session.commit.assert_called_once()
            assert contract_manage.contract.Title == "new_title"
            assert contract_manage.contract.Amount == 150
            assert contract_manage.contract.AmountOutstanding == 25
            assert contract_manage.contract.ContractSigned == True
            contract_manage.view.display_green_message.assert_called_once_with("\nContrat modifié avec succès !")
            contract_manage.sentry_event.assert_called_once_with(self.employee.Email, f"Contrat Signé: Titre: {contract_manage.contract.Title} - Email du Client: {contract_manage.contract.CustomerRel.Email}", "Contract_signed")

    def test_delete(self):
        """Test de la méthode delete()"""
        with patch.object(ContractManage, 'get_permissions_contracts'), \
             patch.object(View, 'return_choice'), \
             patch.object(View, 'display_title_panel_color_fit'), \
             patch.object(SessionLocal, 'query'), \
             patch.object(ContractManage, 'confirm_table_recap'), \
             patch.object(SessionLocal, 'delete'), \
             patch.object(SessionLocal, 'commit'), \
             patch.object(View, 'display_red_message'), \
             patch.object(SessionLocal, 'rollback'):
            
            # Arrange
            contract_manage = ContractManage(self.session, self.employee, self.role)
            mock_contracts = [Contract(Id=1, Title="contract_title")]
            contract_manage.get_permissions_contracts.return_value = mock_contracts
            contract_manage.view.return_choice.return_value = "1"
            contract_manage.session.query().filter_by().one.return_value = mock_contracts[[1]]
            contract_manage.confirm_table_recap.return_value = True
            
            # Act
            contract_manage.delete()
            
            # Assert
            contract_manage.get_permissions_contracts.assert_called_once()
            self.session.query.assert_called_once_with(Contract)
            self.session.query().filter_by.assert_called_once_with(Id=1)
            self.session.delete.assert_called_once_with(mock_contracts[[1]])
            self.session.commit.assert_called_once()
            contract_manage.view.display_red_message.assert_called_once_with("Contrat supprimé avec succès !")

