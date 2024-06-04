import logging

from models.contract import Contract
from models.customer import Customer
from models.database import Base, SessionLocal, engine
from models.employee import Employee
from models.role import Role

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s:%(message)s')

ROLES = {
    "Commercial": {
        "Can_r_Employee": False,
        "Can_ru_Employee": False,
        "Can_crud_Employee": False,
        "Can_r_Role": False,
        "Can_ru_Role": False,
        "Can_crud_Role": False,
        "Can_ru_Customer": True,
        "Can_crud_Customer": True,
        "Can_access_all_Customer": False,
        "Can_ru_Contract": True,
        "Can_crud_Contract": False,
        "Can_access_all_Contract": False,
        "Can_ru_Event": True,
        "Can_crud_Event": True,
        "Can_access_all_Event": False,
        "Can_access_support_Event": False,
    },
    "Support": {
        "Can_r_Employee": False,
        "Can_ru_Employee": False,
        "Can_crud_Employee": False,
        "Can_r_Role": False,
        "Can_ru_Role": False,
        "Can_crud_Role": False,
        "Can_ru_Customer": False,
        "Can_crud_Customer": False,
        "Can_access_all_Customer": False,
        "Can_ru_Contract": False,
        "Can_crud_Contract": False,
        "Can_access_all_Contract": False,
        "Can_ru_Event": True,
        "Can_crud_Event": False,
        "Can_access_all_Event": False,
        "Can_access_support_Event": False,
    },
    "Gestion": {
        "Can_r_Employee": True,
        "Can_ru_Employee": True,
        "Can_crud_Employee": True,
        "Can_r_Role": True,
        "Can_ru_Role": True,
        "Can_crud_Role": True,
        "Can_ru_Customer": False,
        "Can_crud_Customer": False,
        "Can_access_all_Customer": True,
        "Can_ru_Contract": True,
        "Can_crud_Contract": True,
        "Can_access_all_Contract": True,
        "Can_ru_Event": True,
        "Can_crud_Event": False,
        "Can_access_all_Event": True,
        "Can_access_support_Event": True,
    },
}

USERS = {
    "commercial_1": {
        "FirstName": "commercial_1",
        "LastName": "commercial_1",
        "Email": "commercial_1@email.com",
        "PasswordHash": "Password123",
        "RoleId": 1,
    },
    "commercial_2": {
        "FirstName": "commercial_2",
        "LastName": "commercial_2",
        "Email": "commercial_2@email.com",
        "PasswordHash": "Password123",
        "RoleId": 1,
    },
    "support_1": {
        "FirstName": "support_1",
        "LastName": "support_1",
        "Email": "support_1@email.com",
        "PasswordHash": "Password123",
        "RoleId": 2,
    },
    "support_2": {
        "FirstName": "support_2",
        "LastName": "support_2",
        "Email": "support_2@email.com",
        "PasswordHash": "Password123",
        "RoleId": 2,
    },
    "gestion_1": {
        "FirstName": "gestion_1",
        "LastName": "gestion_1",
        "Email": "gestion_1@email.com",
        "PasswordHash": "Password123",
        "RoleId": 3,
    },
}

CUSTOMERS = {
    "customer_1": {
        "FirstName": "customer_1",
        "LastName": "customer_1",
        "Email": "customer_1@email.com",
        "PhoneNumber": "123456789",
        "Company": "Company_1",
        "CommercialId": 1,
    },
    "customer_2": {
        "FirstName": "customer_2",
        "LastName": "customer_2",
        "Email": "customer_2@email.com",
        "PhoneNumber": "123456789",
        "Company": "Company_2",
        "CommercialId": 2,
    },
}

CONTRACTS = {
    "Contract_1": {
        "Title": "Contract_1",
        "Amount": 1000.0,
        "AmountOutstanding": 500.0,
        "CustomerId": 1,
        "ContractSigned": True,
    },
    "Contract_2": {
        "Title": "Contract_2",
        "Amount": 5000.0,
        "AmountOutstanding": 5000.0,
        "CustomerId": 2,
        "ContractSigned": False,
    },
}


def create_roles(session):
    try:
        for role_name, role_data in ROLES.items():
            role = Role(RoleName=role_name, **role_data)
            session.add(role)
        session.commit()
        logging.info("Roles have been successfully created!")
    except Exception as e:
        session.rollback()
        logging.error(f"An error occurred while creating roles: {e}")


def create_users(session):
    try:
        for user_data in USERS.values():
            user = Employee(**user_data)
            session.add(user)
        session.commit()
        logging.info("Users have been successfully created!")
    except Exception as e:
        session.rollback()
        logging.error(f"An error occurred while creating users: {e}")


def create_customers(session):
    try:
        for customer_data in CUSTOMERS.values():
            customer = Customer(**customer_data)
            session.add(customer)
        session.commit()
        logging.info("Customers have been successfully created!")
    except Exception as e:
        session.rollback()
        logging.error(f"An error occurred while creating customers: {e}")


def create_contracts(session):
    try:
        for contract_data in CONTRACTS.values():
            contract = Contract(**contract_data)
            session.add(contract)
        session.commit()
        logging.info("Contracts have been successfully created!")
    except Exception as e:
        session.rollback()
        logging.error(f"An error occurred while creating contracts: {e}")


def init_base():
    try:
        session = SessionLocal()

        logging.info("Dropping all tables...")
        # Drop all tables
        Base.metadata.drop_all(bind=engine)
        logging.info("All tables dropped successfully.")

        logging.info("Creating all tables...")
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logging.info("All tables created successfully.")

    except Exception as e:
        logging.error(f"An error has occurred while resetting the base: {e}", exc_info=False)
    else:
        create_roles(session)
        create_users(session)
        create_customers(session)
        create_contracts(session)
    finally:
        session.close()


if __name__ == "__main__":
    init_base()
