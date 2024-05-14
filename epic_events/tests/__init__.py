import pytest
from collections import namedtuple
from epic_events.models.database import Session
from epic_events.models.employee import Employee
from epic_events.models.customer import Customer
from epic_events.models.contract import Contract
from epic_events.models.event import Event
from epic_events.models.role import Role


# Fixture pour obtenir une session de base de données
@pytest.fixture(scope="function")
def session():
    session = Session()  # Créer une nouvelle session
    yield session  # Passer la session aux tests
    session.close()  # Fermer la session

@pytest.fixture
def create_test_data(session):
    # Création des données de tests
    role = Role(RoleName="test_role_1")
    employee = Employee(FirstName="test_employee_1", LastName="", Email="employee@email.com", PasswordHash="password123", RoleId=role.Id)
    customer = Customer(FirstName="test_customer_1", LastName="", Email="customer@email.com")
    contract = Contract(CustomerId=customer.Id, Title="test_contract", ContractSigned=True)
    event = Event(ContractId=contract.Id, Title="test_event")
        
    # Ajout les données à la session
    session.add_all([role, employee, customer, contract, event])
    session.commit()

    # Retourner les données de test
    yield role, employee, customer, contract, event

    # Nettoyer les données après chaque test
    session.delete(role)
    session.delete(employee)
    session.delete(customer)
    session.delete(contract)
    session.delete(event)
    session.commit()