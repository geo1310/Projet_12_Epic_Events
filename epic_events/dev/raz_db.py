import logging

from epic_events.models.contract import Contract
from epic_events.models.customer import Customer
from epic_events.models.database import Base, Session, engine
from epic_events.models.employee import Employee
from epic_events.models.event import Event
from epic_events.models.role import Role

# Configuration du logger
logging.basicConfig(level=logging.INFO)

# initialisation des tables
try:
    # Création des tables dans la base
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    logging.info("La Base a été initialisée avec succès !")

except Exception as e:
    logging.error(f"\033[91mUne erreur s'est produite : {e}\033[0m")

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
        Can_r_Customer=True,
        Can_ru_Customer=True,
        Can_crud_Customer=True,
        Can_r_Contract=True,
        Can_ru_Contract=True,
        Can_crud_Contract=True,
        Can_r_Event=True,
        Can_ru_Event=True,
        Can_crud_Event=True,
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
        Can_r_Customer=True,
        Can_ru_Customer=False,
        Can_crud_Customer=False,
        Can_r_Contract=True,
        Can_ru_Contract=False,
        Can_crud_Contract=False,
        Can_r_Event=True,
        Can_ru_Event=True,
        Can_crud_Event=False,
    )
    session.add(support)

    # rôle Management
    management = Role(
        RoleName="Management",
        Can_r_Employee=True,
        Can_ru_Employee=True,
        Can_crud_Employee=True,
        Can_r_Role=True,
        Can_ru_Role=True,
        Can_crud_Role=True,
        Can_r_Customer=True,
        Can_ru_Customer=True,
        Can_crud_Customer=True,
        Can_r_Contract=True,
        Can_ru_Contract=True,
        Can_crud_Contract=True,
        Can_r_Event=True,
        Can_ru_Event=True,
        Can_crud_Event=True,
    )
    session.add(management)

    session.commit()
    logging.info("Les rôles ont été créés avec succès !")

except Exception as e:
    session.rollback()
    logging.error(f"\033[91mUne erreur s'est produite : {e}\033[0m")

finally:
    session.close()


# création d'un employé et d'un client
try:
    session = Session()

    # Création d'un commercial
    commercial_1 = Employee(
        FirstName="commercial_1",
        LastName="",
        Email="commercial_1@email.com",
        PasswordHash="password123",
        RoleId=1,
    )
    session.add(commercial_1)

    # Création d'un commercial
    commercial_2 = Employee(
        FirstName="commercial_2",
        LastName="",
        Email="commercial_2@email.com",
        PasswordHash="password123",
        RoleId=1,
    )
    session.add(commercial_2)

    # Création d'un support
    support_1 = Employee(
        FirstName="support_1",
        LastName="",
        Email="support_1@email.com",
        PasswordHash="password123",
        RoleId=2,
    )
    session.add(support_1)

    # Création d'un support
    support_2 = Employee(
        FirstName="support_2",
        LastName="",
        Email="support_2@email.com",
        PasswordHash="password123",
        RoleId=2,
    )
    session.add(support_2)

    # Création d'un manager
    manager_1 = Employee(
        FirstName="manager_1",
        LastName="",
        Email="manager_1@email.com",
        PasswordHash="password123",
        RoleId=3,
    )
    session.add(manager_1)

    # Création d'un client
    customer_1 = Customer(
        FirstName="customer_1",
        LastName="",
        Email="customer_1@email.com",
        PhoneNumber="123456789",
        Society="society_1",
        CommercialId=1,
    )
    session.add(customer_1)

    # Création d'un client
    customer_2 = Customer(
        FirstName="customer_2",
        LastName="",
        Email="customer_2@email.com",
        PhoneNumber="123456789",
        Society="society_2",
        CommercialId=2,
    )
    session.add(customer_2)

    session.commit()

    logging.info("Employés et clients créés avec succès !")

except Exception as e:
    session.rollback()
    logging.error(f"\033[91mUne erreur s'est produite : {e}\033[0m")

finally:
    session.close()

# Création d'un contrat et d'un évènement
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

    # Création d'un événement associé au contrat
    new_event = Event(
        Title="Event_1",
        Contract=contract_1,
        Location="Lieu de l'événement",
        Attendees=20,
        DateStart="2024-05-14",
    )
    session.add(new_event)

    session.commit()

    logging.info("Contrat et événement créés avec succès !")

except Exception as e:
    session.rollback()
    logging.error(f"\033[91mUne erreur s'est produite : {e}\033[0m")

finally:
    session.close()
