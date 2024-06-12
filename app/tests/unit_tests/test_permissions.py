import pytest
from app.models.role import Role
from app.permissions.permissions import Permissions


@pytest.fixture
def mock_role_1():
    role = Role()
    # Configuration des autorisations du rôle
    role.Can_r_Employee = False
    role.Can_ru_Employee = False
    role.Can_crud_Employee = False
    role.Can_r_Role = False
    role.Can_ru_Role = False
    role.Can_crud_Role = False
    role.Can_ru_Customer = False
    role.Can_crud_Customer = False
    role.Can_access_all_Customer = False
    role.Can_ru_Contract = False
    role.Can_crud_Contract = False
    role.Can_access_all_Contract = False
    role.Can_access_support_Event = False
    role.Can_ru_Event = False
    role.Can_crud_Event = False
    role.Can_access_all_Event = False
    role.RoleName = "Mock Role 1"
    yield role


@pytest.fixture
def mock_role_2():
    role = Role()
    # Configuration des autorisations du rôle
    role.Can_r_Employee = True
    role.Can_ru_Employee = True
    role.Can_crud_Employee = True
    role.Can_r_Role = True
    role.Can_ru_Role = True
    role.Can_crud_Role = True
    role.Can_ru_Customer = True
    role.Can_crud_Customer = True
    role.Can_access_all_Customer = True
    role.Can_ru_Contract = True
    role.Can_crud_Contract = True
    role.Can_access_all_Contract = True
    role.Can_access_support_Event = True
    role.Can_ru_Event = True
    role.Can_crud_Event = True
    role.Can_access_all_Event = True
    role.RoleName = "Mock Role 2"
    yield role


def test_can_read_employee(mock_role_1, mock_role_2):
    assert not Permissions.can_read_employee(mock_role_1)
    assert Permissions.can_read_employee(mock_role_2)


def test_can_update_employee(mock_role_1, mock_role_2):
    assert not Permissions.can_update_employee(mock_role_1)
    assert Permissions.can_update_employee(mock_role_2)


def test_can_create_delete_employee(mock_role_1, mock_role_2):
    assert not Permissions.can_create_delete_employee(mock_role_1)
    assert Permissions.can_create_delete_employee(mock_role_2)


def test_can_read_role(mock_role_1, mock_role_2):
    assert not Permissions.can_read_role(mock_role_1)
    assert Permissions.can_read_role(mock_role_2)


def test_can_update_role(mock_role_1, mock_role_2):
    assert not Permissions.can_update_role(mock_role_1)
    assert Permissions.can_update_role(mock_role_2)


def test_can_create_delete_role(mock_role_1, mock_role_2):
    assert not Permissions.can_create_delete_role(mock_role_1)
    assert Permissions.can_create_delete_role(mock_role_2)


def test_can_update_customer(mock_role_1, mock_role_2):
    assert not Permissions.can_update_customer(mock_role_1)
    assert Permissions.can_update_customer(mock_role_2)


def test_can_create_delete_customer(mock_role_1, mock_role_2):
    assert not Permissions.can_create_delete_customer(mock_role_1)
    assert Permissions.can_create_delete_customer(mock_role_2)


def test_all_customer(mock_role_1, mock_role_2):
    assert not Permissions.all_customer(mock_role_1)
    assert Permissions.all_customer(mock_role_2)


def test_can_update_contract(mock_role_1, mock_role_2):
    assert not Permissions.can_update_contract(mock_role_1)
    assert Permissions.can_update_contract(mock_role_2)


def test_can_create_delete_contract(mock_role_1, mock_role_2):
    assert not Permissions.can_create_delete_contract(mock_role_1)
    assert Permissions.can_create_delete_contract(mock_role_2)


def test_all_contract(mock_role_1, mock_role_2):
    assert not Permissions.all_contract(mock_role_1)
    assert Permissions.all_contract(mock_role_2)


def test_can_access_support(mock_role_1, mock_role_2):
    assert not Permissions.can_access_support(mock_role_1)
    assert Permissions.can_access_support(mock_role_2)


def test_can_update_event(mock_role_1, mock_role_2):
    assert not Permissions.can_update_event(mock_role_1)
    assert Permissions.can_update_event(mock_role_2)


def test_can_create_delete_event(mock_role_1, mock_role_2):
    assert not Permissions.can_create_delete_event(mock_role_1)
    assert Permissions.can_create_delete_event(mock_role_2)


def test_all_event(mock_role_1, mock_role_2):
    assert not Permissions.all_event(mock_role_1)
    assert Permissions.all_event(mock_role_2)


def test_role_name(mock_role_1, mock_role_2):
    assert Permissions.role_name(mock_role_1) == "Mock Role 1"
    assert Permissions.role_name(mock_role_2) == "Mock Role 2"


if __name__ == "__main__":
    pytest.main(["--cov=app/permissions/", "--cov-report=html", __file__])
