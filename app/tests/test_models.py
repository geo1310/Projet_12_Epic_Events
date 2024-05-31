import pytest

from app.models.contract import Contract
from app.models.customer import Customer
from app.models.employee import Employee
from app.models.event import Event

from . import create_test_data, session


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
            PasswordHash="password123",
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
            PasswordHash="password123",
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
