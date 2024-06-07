import pytest
from collections import namedtuple
import pytest

from app.models.contract import Contract
from app.models.customer import Customer
from app.models.database import SessionLocal
from app.models.employee import Employee
from app.models.event import Event
from app.models.role import Role


@pytest.fixture()
def session():
    """
    Fixture pour obtenir une session de base de données.

    Cette fixture crée une nouvelle session SQLAlchemy et la passe aux tests.
    Une fois les tests terminés, la session est fermée.

    Yields:
        sqlalchemy.orm.Session: Une session SQLAlchemy.
    """
    session = SessionLocal()
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
    session.add(role)
    session.commit()

    employee = Employee(
        FirstName="test_employee_1",
        LastName="",
        Email="employee@email.com",
        PasswordHash="Password123",
        RoleId=role.Id,
    )
    session.add(employee)
    session.commit()

    customer = Customer(FirstName="test_customer_1", LastName="", Email="customer@email.com", CommercialId = employee.Id)
    session.add(customer)
    session.commit()

    contract = Contract(CustomerId=customer.Id, Title="test_contract", ContractSigned=True)
    session.add(contract)
    session.commit()

    event = Event(ContractId=contract.Id, Title="test_event")
    session.add(event)
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
    session.close()



def test_employee(session, create_test_data):
    """
    Vérifie la création et la mise à jour d'un employé.
    Vérifie l'unicité et la validité des emails.
    """

    test_data = create_test_data

    assert test_data.employee.Id is not None
    assert test_data.employee.FirstName == "test_employee_1"

    # test data update
    test_data.employee.FirstName = "test_update_FirstName"
    session.commit()
    updated_employee = session.query(Employee).filter_by(Id=test_data.employee.Id).first()

    assert updated_employee.FirstName == "test_update_FirstName"

    # Test de création d'employé avec un email existant
    with pytest.raises(Exception):
        employee_duplicate_email = Employee(
            FirstName="Duplicate",
            LastName="Employee",
            Email=test_data.employee.Email,  # Utilise l'email existant
            PasswordHash="Password123",
            RoleId=test_data.employee.RoleId,
        )
        session.add(employee_duplicate_email)
        session.commit()
    session.rollback()

    # Test de création d'employé avec un email non valide
    with pytest.raises(Exception):
        employee_invalid_email = Employee(
            FirstName="Duplicate",
            LastName="Employee",
            Email="fdsfdsfds",
            PasswordHash="Password123",
            RoleId=test_data.employee.RoleId,
        )
        session.add(employee_invalid_email)
        session.commit()
    session.rollback()


def test_customer(session, create_test_data):
    """
    Vérifie la création et la mise à jour d'un client.
    Vérifie la présence de l'email.
    """

    test_data = create_test_data

    assert test_data.customer.Id is not None

    # test data update
    test_data.customer.FirstName = "test_update_FirstName"
    session.commit()
    updated_customer = session.query(Customer).filter_by(Id=test_data.customer.Id).first()

    assert updated_customer.FirstName == "test_update_FirstName"

    # Test de création d'un client sans email
    with pytest.raises(Exception):
        customer_invalid_email = Customer(
            FirstName="Duplicate",
            LastName="Employee",
            Email=None,
        )
        session.add(customer_invalid_email)
        session.commit()
    session.rollback()


def test_contract(session, create_test_data):
    """
    Vérifie la création et la mise à jour d'un contrat.
    Test la création d'un contrat sans titre.
    """

    test_data = create_test_data

    assert test_data.contract.Id is not None

    # test data update
    test_data.contract.Title = "test_update_Title"
    session.commit()
    updated_contract = session.query(Contract).filter_by(Id=test_data.contract.Id).first()

    assert updated_contract.Title == "test_update_Title"

    # Test de création de contrat sans titre
    with pytest.raises(Exception):
        contract_missing_title = Contract(
            CustomerId=test_data.customer.Id, Title=None, ContractSigned=True  # Titre manquant
        )
        session.add(contract_missing_title)
        session.commit()
    session.rollback()


def test_event(session, create_test_data):
    """
    Vérifie la création et la mise à jour d'un événement.
    Test la création d'une date de fin non valide.
    """

    test_data = create_test_data

    assert test_data.event.Id is not None

    # test data update
    test_data.event.Title = "test_update_Title"
    session.commit()
    updated_event = session.query(Event).filter_by(Id=test_data.event.Id).first()

    assert updated_event.Title == "test_update_Title"

    # Test de création d'événement avec une date de début ultérieure à la date de fin
    with pytest.raises(Exception):
        event_invalid_date = Event(
            ContractId=test_data.contract.Id,
            Title="Invalid Date Event",
            DateStart="2024-05-15",
            DateEnd="2024-05-10",  # Date de fin antérieure à la date de début
        )
        session.add(event_invalid_date)
        session.commit()
    session.rollback()

if __name__ == "__main__":
    pytest.main([__file__])
