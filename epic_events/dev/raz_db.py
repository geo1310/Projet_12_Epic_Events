import logging

from epic_events.models.contract import Contract
from epic_events.models.customer import Customer
from epic_events.models.database import Base, Session, engine
from epic_events.models.employee import Employee
from epic_events.models.event import Event
from epic_events.models.role import Role


def init_base():
    # Configuration du logger
    logging.basicConfig(level=logging.INFO)

    # initialisation des tables
    try:
        # Création des tables dans la base
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)

        logging.info("base successfully reset !")

    except Exception as e:
        logging.error(f"\033[91man error has occurred : {e}\033[0m")

    # création des roles
    try:
        session = Session()
        # rôle Commercial
        commercial = Role(
            RoleName="Commercial",
            Can_r_Employee=False,
            Can_ru_Employee=False,
            Can_crud_Employee=False,
            Can_r_Role=False,
            Can_ru_Role=False,
            Can_crud_Role=False,
            Can_ru_Customer=True,
            Can_crud_Customer=True,
            Can_access_all_Customer=False,
            Can_ru_Contract=True,
            Can_crud_Contract=False,
            Can_access_all_Contract=False,
            Can_ru_Event=True,
            Can_crud_Event=True,
            Can_access_all_Event=False,
            Can_access_support_Event=False,
        )
        session.add(commercial)

        # rôle Support
        support = Role(
            RoleName="Support",
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
            Can_ru_Event=True,
            Can_crud_Event=False,
            Can_access_all_Event=False,
            Can_access_support_Event=False,
        )
        session.add(support)

        # rôle gestion
        gestion = Role(
            RoleName="Gestion",
            Can_r_Employee=True,
            Can_ru_Employee=True,
            Can_crud_Employee=True,
            Can_r_Role=True,
            Can_ru_Role=True,
            Can_crud_Role=True,
            Can_ru_Customer=False,
            Can_crud_Customer=False,
            Can_access_all_Customer=False,
            Can_ru_Contract=True,
            Can_crud_Contract=True,
            Can_access_all_Contract=True,
            Can_ru_Event=True,
            Can_crud_Event=False,
            Can_access_all_Event=True,
            Can_access_support_Event=True,
        )
        session.add(gestion)

        session.commit()
        logging.info("the roles have been successfully created !")

    except Exception as e:
        session.rollback()
        logging.error(f"\033[91man error has occurred : {e}\033[0m")

    finally:
        session.close()

    # création d'un employé et d'un client
    try:
        session = Session()

        # Création d'un membre commercial
        commercial_1 = Employee(
            FirstName="commercial_1",
            LastName="commercial_1",
            Email="commercial_1@email.com",
            PasswordHash="Password123",
            RoleId=1,
        )
        session.add(commercial_1)

        # Création d'un membre commercial
        commercial_2 = Employee(
            FirstName="commercial_2",
            LastName="commercial_2",
            Email="commercial_2@email.com",
            PasswordHash="Password123",
            RoleId=1,
        )
        session.add(commercial_2)

        # Création d'un membre support
        support_1 = Employee(
            FirstName="support_1",
            LastName="support_1",
            Email="support_1@email.com",
            PasswordHash="Password123",
            RoleId=2,
        )
        session.add(support_1)

        # Création d'un membre support
        support_2 = Employee(
            FirstName="support_2",
            LastName="support_2",
            Email="support_2@email.com",
            PasswordHash="Password123",
            RoleId=2,
        )
        session.add(support_2)

        # Création d'un membre gestion
        manager_1 = Employee(
            FirstName="gestion_1",
            LastName="gestion_1",
            Email="gestion_1@email.com",
            PasswordHash="Password123",
            RoleId=3,
        )
        session.add(manager_1)

        # Création d'un client
        customer_1 = Customer(
            FirstName="customer_1",
            LastName="customer_1",
            Email="customer_1@email.com",
            PhoneNumber="123456789",
            Company="Company_1",
            CommercialId=1,
        )
        session.add(customer_1)

        # Création d'un client
        customer_2 = Customer(
            FirstName="customer_2",
            LastName="customer_2",
            Email="customer_2@email.com",
            PhoneNumber="123456789",
            Company="Company_2",
            CommercialId=2,
        )
        session.add(customer_2)

        session.commit()

        logging.info("users have been successfully created !")

    except Exception as e:
        session.rollback()
        logging.error(f"\033[91man error has occurred : {e}\033[0m")

    finally:
        session.close()

    # Création des contrats
    try:
        session = Session()
        # Création d'un contrat
        contract_1 = Contract(
            Title="Contract_1", Amount=1000.0, AmountOutstanding=500.0, CustomerId=1, ContractSigned=True
        )
        session.add(contract_1)

        # Création d'un contrat
        contract_2 = Contract(
            Title="Contract_2", Amount=5000.0, AmountOutstanding=5000.0, CustomerId=2, ContractSigned=False
        )
        session.add(contract_2)

        session.commit()

        logging.info("contracts have been successfully created !")

    except Exception as e:
        session.rollback()
        logging.error(f"\033[91man error has occurred : {e}\033[0m")

    finally:
        session.close()


if __name__ == "__main__":
    init_base()
