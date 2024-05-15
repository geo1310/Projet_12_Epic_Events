from collections import namedtuple

import pytest

from epic_events.models.contract import Contract
from epic_events.models.customer import Customer
from epic_events.models.database import Session
from epic_events.models.employee import Employee
from epic_events.models.event import Event
from epic_events.models.role import Role


@pytest.fixture(scope="function")
def session():
    """
    Fixture pour obtenir une session de base de données.

    Cette fixture crée une nouvelle session SQLAlchemy et la passe aux tests.
    Une fois les tests terminés, la session est fermée.

    Yields:
        sqlalchemy.orm.Session: Une session SQLAlchemy.
    """
    session = Session()
    yield session
    session.close()


@pytest.fixture
def create_test_data(session):
    """
    Fixture pour créer des données de test dans la base de données.

    Cette fixture crée des données de test pour les modèles de votre application,
    les ajoute à la session SQLAlchemy et les retourne pour être utilisées dans les tests.
    Une fois les tests terminés, les données de test sont nettoyées de la base de données.

    Args:
        session (sqlalchemy.orm.Session): Session SQLAlchemy pour interagir avec la base de données.

    Yields:
        tuple: Un namedtuple contenant les données de test pour les modèles.
    """

    TestData = namedtuple("TestData", ["role", "employee", "customer", "contract", "event"])

    role = Role(RoleName="test_role_1")

    employee = Employee(
        FirstName="test_employee_1",
        LastName="",
        Email="employee@email.com",
        PasswordHash="password123",
        RoleId=role.Id,
    )

    customer = Customer(FirstName="test_customer_1", LastName="", Email="customer@email.com")

    contract = Contract(CustomerId=customer.Id, Title="test_contract", ContractSigned=True)

    event = Event(ContractId=contract.Id, Title="test_event")

    # Ajout les données à la session
    session.add_all([role, employee, customer, contract, event])
    session.commit()

    # Retourne les données de test
    yield TestData(role, employee, customer, contract, event)

    # Nettoyer les données après chaque test
    session.delete(role)
    session.delete(employee)
    session.delete(customer)
    session.delete(contract)
    session.delete(event)
    session.commit()
