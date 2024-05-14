import logging
from epic_events.models.database import Base, engine, Session
from epic_events.models.employee import Employee
from epic_events.models.role import Role
from epic_events.models.customer import Customer
from epic_events.models.contract import Contract
from epic_events.models.event import Event

# Configuration du logger
logging.basicConfig(level=logging.INFO)

# initilaisation des tables 
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
        Can_r_Employee=True,
        Can_ru_Employee=False,
        Can_crud_Employee=False,
        Can_r_role=False,
        Can_ru_role=False,
        Can_crud_role=False,
        Can_r_Customer=True,
        Can_ru_customer=True,
        Can_crud_Customer=True,
        Can_r_Contract=True,
        Can_ru_Contract=True,
        Can_crud_Contract=True,
        Can_r_Event=True,
        Can_ru_Event=True,
        Can_crud_Event=True,
    )
    session.add(commercial)

    #rôle Support
    support = Role(
        RoleName="Support",
        Can_r_Employee=True,
        Can_ru_Employee=False,
        Can_crud_Employee=False,
        Can_r_role=False,
        Can_ru_role=False,
        Can_crud_role=False,
        Can_r_Customer=True,
        Can_ru_customer=False,
        Can_crud_Customer=False,
        Can_r_Contract=True,
        Can_ru_Contract=False,
        Can_crud_Contract=False,
        Can_r_Event=True,
        Can_ru_Event=True,
        Can_crud_Event=False,
    )
    session.add(support)

    # Créer le rôle Management
    management = Role(
        RoleName="Management",
        Can_r_Employee=True,
        Can_ru_Employee=True,
        Can_crud_Employee=True,
        Can_r_role=True,
        Can_ru_role=True,
        Can_crud_role=True,
        Can_r_Customer=True,
        Can_ru_customer=True,
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

    # Création d'un employé
    new_employee = Employee(
        FirstName="John",
        LastName="Doe",
        Email="john.doe@example.com",
        PasswordHash="password123",
        RoleId=1,
    )
    session.add(new_employee)
    session.commit()

    # Création d'un client
    new_customer = Customer(
        FirstName="Alice",
        LastName="Smith",
        Email="alice.smith@example.com",
        PhoneNumber="123456789",
        Society="ABC Inc.",
    )
    session.add(new_customer)
    session.commit()

    logging.info("L'employé et le client ont été créés avec succès !")

except Exception as e:
    session.rollback()
    logging.error(f"\033[91mUne erreur s'est produite : {e}\033[0m")

finally:
    session.close()

# Création d'un contrat et d'un évènement
try:
    session = Session()
    # Création d'un contrat
    new_contract = Contract(
        Title="Contrat de test",
        Amount=1000.0,
        AmountOutstanding=1000.0,
        ContractSigned=True
    )
    session.add(new_contract)
    session.commit()

    # Création d'un événement associé au contrat
    new_event = Event(
        Title="Événement de test",
        Contract=new_contract,
        Location="Lieu de l'événement",
        Attendees = 20,
        DateStart="2024-05-14",
        DateEnd="2024-05-15"
    )
    session.add(new_event)
    session.commit()

    logging.info("Contrat et événement créés avec succès !")

except Exception as e:
    session.rollback()
    logging.error(f"\033[91mUne erreur s'est produite : {e}\033[0m")

finally:
    session.close()
