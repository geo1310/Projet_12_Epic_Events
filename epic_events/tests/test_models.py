from . import session, create_test_data
from epic_events.models.employee import Employee
from epic_events.models.customer import Customer
from epic_events.models.contract import Contract
from epic_events.models.event import Event
from epic_events.models.role import Role


# Test pour vérifier la création d'un employé
def test_employee(session, create_test_data):

    test_data = create_test_data
    role, employee, customer, contract, event = test_data
    
    assert employee.Id is not None
    assert employee.FirstName == "test_employee_1"
    

# Test pour vérifier la création d'un contrat
def test_contract(session, create_test_data):
    
    test_data = create_test_data
    role, employee, customer, contract, event = test_data

    assert contract.Id is not None

    
# Test pour vérifier la création d'un événement
def test_create_event(session, create_test_data):
   
    test_data = create_test_data
    role, employee, customer, contract, event = test_data

    assert event.Id is not None

    

