from datetime import datetime
from unittest.mock import Mock
import pytest
from app.controllers.utils_manage import UtilsManage
from app.utils.logger_config import LoggerConfig
from app.models.database import DatabaseConfig
from rich.table import Table
from app.models.contract import Contract


@pytest.fixture
def utils_manage():
    return UtilsManage(Mock())


@pytest.fixture()
def session():
    # Loggers
    logger_config = LoggerConfig()
    logger = logger_config.get_logger()
    session_config = DatabaseConfig(logger)
    session = session_config.db_session_local()
    yield session
    session.close()


@pytest.fixture
def create_test_data(session):

    contract1 = Contract(
        Id=1,
        Title="Contrat 1",
        CustomerRel=Mock(
            LastName="Client 1",
            Email="client1@example.com",
            CommercialRel=Mock(LastName="Commercial 1", Email="commercial1@example.com"),
        ),
        Amount=1000.0,
        AmountOutstanding=500.0,
        ContractSigned=True,
        DateCreated=datetime.now(),
    )

    session.add(contract1)
    session.commit()

    contract2 = Contract(
        Id=2,
        Title="Contrat 2",
        CustomerRel=None,
        Amount=2000.0,
        AmountOutstanding=1000.0,
        ContractSigned=False,
        DateCreated=datetime.now(),
    )

    session.add(contract2)
    session.commit()

    yield contract1, contract2

    # Nettoyer les données après chaque test
    session.delete(contract1)
    session.delete(contract2)
    session.commit()
    session.close()


def test_confirm_table_recap_yes_and_no(utils_manage):

    mock_instance = Mock()
    utils_manage.view.display_title_panel_color_fit = Mock()
    utils_manage.table_create = Mock(return_value="Summary Table")
    utils_manage.view.display_table = Mock()
    utils_manage.view.return_choice = Mock(return_value="oui")

    # Appel de la méthode confirm_table_recap
    result = utils_manage.confirm_table_recap("MockModel", mock_instance, "Création", "green")

    # Vérification des appels de méthode
    utils_manage.view.display_title_panel_color_fit.assert_called_once_with("MockModel - Création", "green", True)
    utils_manage.table_create.assert_called_once_with("MockModel", [mock_instance])
    utils_manage.view.display_table.assert_called_once_with("Summary Table", "Résumé - MockModel")
    utils_manage.view.return_choice.assert_called_once_with("Confirmation Création ? (oui/non)", False)
    # Vérification du résultat
    assert result is True

    utils_manage.view.return_choice = Mock(return_value="non")
    result = utils_manage.confirm_table_recap("MockModel", mock_instance, "Création", "green")
    # Vérification du résultat
    assert result is False


def test_table_create(utils_manage):

    # mocks
    utils_manage.table_event = Mock(return_value="Event Table")
    utils_manage.table_contract = Mock(return_value="Contract Table")
    utils_manage.table_customer = Mock(return_value="Customer Table")
    utils_manage.table_employee = Mock(return_value="Employee Table")
    utils_manage.table_role = Mock(return_value="Role Table")
    list_mock = [Mock(), Mock()]

    result = utils_manage.table_create("event", list_mock)
    utils_manage.table_event.assert_called_once_with(list_mock)
    assert result == "Event Table"

    result = utils_manage.table_create("contract", list_mock)
    utils_manage.table_contract.assert_called_once_with(list_mock)
    assert result == "Contract Table"

    result = utils_manage.table_create("customer", list_mock)
    utils_manage.table_customer.assert_called_once_with(list_mock)
    assert result == "Customer Table"

    result = utils_manage.table_create("employee", list_mock)
    utils_manage.table_employee.assert_called_once_with(list_mock)
    assert result == "Employee Table"

    result = utils_manage.table_create("role", list_mock)
    utils_manage.table_role.assert_called_once_with(list_mock)
    assert result == "Role Table"

    with pytest.raises(ValueError) as e:
        utils_manage.table_create("unknown_type", [Mock()])
    assert str(e.value) == "Unknown type: unknown_type"


def test_table_event(utils_manage):

    # mocks
    utils_manage.format_date = Mock(return_value="date formatée")

    # Créer des événements de test
    event1 = Mock(
        Id=1,
        Title="Event 1",
        Notes="Notes 1",
        Location="Location 1",
        Attendees=10,
        ContractRel=Mock(Title="Contract 1"),
        EmployeeSupportRel=Mock(FirstName="John"),
        DateStart="2024-06-15 10:00:00",
        DateEnd="2024-06-15 12:00:00",
        DateCreated="2024-06-10 08:00:00",
    )
    event2 = Mock(
        Id=2,
        Title="Event 2",
        Notes="Notes 2",
        Location="Location 2",
        Attendees=20,
        ContractRel=Mock(Title="Contract 1"),
        EmployeeSupportRel=Mock(FirstName="John"),
        DateStart="2024-06-20 09:00:00",
        DateEnd="2024-06-20 17:00:00",
        DateCreated="2024-06-12 10:00:00",
    )
    events = [event1, event2]

    # Appel de la méthode table_event
    table = utils_manage.table_event(events)

    # Vérification du type de retour
    assert isinstance(table, Table)
    assert len(table.rows) == 2


def test_table_contract(utils_manage):
    # Créer des contrats de test
    contract1 = Mock(
        Id=1,
        Title="Contrat 1",
        CustomerRel=Mock(
            LastName="Client 1",
            Email="client1@example.com",
            CommercialRel=Mock(LastName="Commercial 1", Email="commercial1@example.com"),
        ),
        Amount=1000.0,
        AmountOutstanding=500.0,
        ContractSigned=True,
        DateCreated=datetime.now(),
    )

    contract2 = Mock(
        Id=2,
        Title="Contrat 2",
        CustomerRel=None,
        Amount=2000.0,
        AmountOutstanding=1000.0,
        ContractSigned=False,
        DateCreated=datetime.now(),
    )

    # Appeler la méthode table_contract avec les contrats de test
    contracts = [contract1, contract2]
    table = utils_manage.table_contract(contracts)

    # Vérifier le contenu de la table générée
    assert isinstance(table, Table)
    assert len(table.rows) == 2


def test_table_customer(utils_manage):
    # Créer des clients de test
    customer1 = Mock(
        Id=1,
        FirstName="John",
        LastName="Doe",
        Email="john.doe@example.com",
        PhoneNumber="123456789",
        Company="ABC Inc.",
        CommercialRel=Mock(Email="commercial1@example.com"),
        DateCreated=datetime.now(),
        DateLastUpdate=datetime.now(),
    )

    customer2 = Mock(
        Id=2,
        FirstName="Alice",
        LastName="Smith",
        Email="alice.smith@example.com",
        PhoneNumber="987654321",
        Company="XYZ Corp.",
        CommercialRel=Mock(Email="commercial2@example.com"),
        DateCreated=datetime.now(),
        DateLastUpdate=datetime.now(),
    )

    # Appeler la méthode table_customer avec les clients de test
    customers = [customer1, customer2]
    table = utils_manage.table_customer(customers)

    # Vérifier le contenu de la table générée
    assert isinstance(table, Table)
    assert len(table.rows) == 2


def test_table_employee(utils_manage):
    # Créer des employés de test
    employee1 = Mock(
        Id=1,
        FirstName="John",
        LastName="Doe",
        Email="john.doe@example.com",
        RoleRel=Mock(RoleName="Manager"),
        CustomersRel=[Mock(FirstName="Customer1"), Mock(FirstName="Customer2")],
        EventsRel=[Mock(Title="Event1"), Mock(Title="Event2")],
        DateCreated=datetime(2024, 6, 15, 10, 0, 0),
    )

    employee2 = Mock(
        Id=2,
        FirstName="Alice",
        LastName="Smith",
        Email="alice.smith@example.com",
        RoleRel=Mock(RoleName="Employee"),
        CustomersRel=[Mock(FirstName="Customer3"), Mock(FirstName="Customer4")],
        EventsRel=[Mock(Title="Event3"), Mock(Title="Event4")],
        DateCreated=datetime(2024, 6, 10, 8, 0, 0),
    )

    # Appeler la méthode table_employee avec les employés de test
    employees = [employee1, employee2]
    table = utils_manage.table_employee(employees)

    # Vérifier le contenu de la table générée
    assert isinstance(table, Table)
    assert len(table.rows) == 2


def test_table_role(utils_manage):
    # Créer des rôles de test
    role1 = Mock(
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
        DateCreated=datetime.now(),
    )

    role2 = Mock(
        Id=2,
        RoleName="Employee",
        Can_r_Employee=False,
        Can_ru_Employee=False,
        Can_crud_Employee=False,
        Can_r_Role=False,
        Can_ru_Role=False,
        Can_crud_Role=False,
        Can_ru_Customer=False,
        Can_crud_Customer=False,
        Can_access_all_Customer=False,
        Can_ru_Contract=False,
        Can_crud_Contract=False,
        Can_access_all_Contract=False,
        Can_ru_Event=False,
        Can_crud_Event=False,
        Can_access_all_Event=False,
        Can_access_support_Event=False,
        DateCreated=datetime.now(),
    )

    # Appeler la méthode table_role avec les rôles de test
    roles = [role1, role2]
    table = utils_manage.table_role(roles)

    # Vérifier le contenu de la table générée
    assert isinstance(table, Table)
    assert len(table.rows) == 2


def test_format_date(utils_manage):

    # Tester avec une date valide
    date_str = "2024-06-15 10:00:00"
    expected_formatted_date = "15/06/2024 10:00"
    formatted_date = utils_manage.format_date(datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S"))
    assert formatted_date == expected_formatted_date

    # Tester avec une date None
    assert utils_manage.format_date(None) is None


def test_str_to_bool(utils_manage):

    # Tester avec des valeurs vraies
    assert utils_manage.str_to_bool("true") == True
    assert utils_manage.str_to_bool("True") == True
    assert utils_manage.str_to_bool("1") == True
    assert utils_manage.str_to_bool("oui") == True
    assert utils_manage.str_to_bool("Oui") == True

    # Tester avec des valeurs fausses
    assert utils_manage.str_to_bool("false") == False
    assert utils_manage.str_to_bool("False") == False
    assert utils_manage.str_to_bool("0") == False
    assert utils_manage.str_to_bool("non") == False
    assert utils_manage.str_to_bool("Non") == False

    # Tester avec d'autres valeurs
    assert utils_manage.str_to_bool("random_string") == False
    assert utils_manage.str_to_bool("") == False


if __name__ == "__main__":
    pytest.main(["--cov=app/controllers/", "--cov-report=html", __file__])
