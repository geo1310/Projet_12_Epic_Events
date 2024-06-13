from app.utils.logger_config import LoggerConfig
from app.utils.sentry_logger import SentryLogger
from app.models.contract import Contract
from app.models.customer import Customer
from app.models.database import DatabaseConfig
from app.models.employee import Employee
from app.models.event import Event
from app.models.role import Role


class DatabaseInitializer:
    """
    Classe pour initialiser et réinitialiser la base de données avec des rôles, utilisateurs, clients et contrats prédéfinis.

    Attributs:
        session (Session): Objet de session SQLAlchemy.
        engine (Engine): Objet engine SQLAlchemy.
        base (Base): Objet de base SQLAlchemy contenant les modèles.
        logger (Logger): Objet logger pour enregistrer les informations.

    Méthodes:
        create_roles(): Crée les rôles prédéfinis dans la base de données.
        create_users(): Crée les utilisateurs prédéfinis dans la base de données.
        create_customers(): Crée les clients prédéfinis dans la base de données.
        create_contracts(): Crée les contrats prédéfinis dans la base de données.
        drop_all_tables(): Supprime toutes les tables de la base de données.
        create_all_tables(): Crée toutes les tables dans la base de données.
        init_base(): Réinitialise la base de données et la peuple avec des données prédéfinies.
    """
    def __init__(self, session, engine, base, logger):

        self.session = session
        self.engine = engine
        self.base = base
        self.logger = logger

        self.ROLES = {
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

        self.USERS = {
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

        self.CUSTOMERS = {
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

        self.CONTRACTS = {
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

    def create_roles(self):
        try:
            for role_name, role_data in self.ROLES.items():
                role = Role(RoleName=role_name, **role_data)
                self.session.add(role)
            self.session.commit()
            self.logger.info("Roles have been successfully created!")
        except Exception as e:
            self.session.rollback()
            self.logger.error(f"An error occurred while creating roles: {e}")

    def create_users(self):
        try:
            for user_data in self.USERS.values():
                user = Employee(**user_data)
                self.session.add(user)
            self.session.commit()
            self.logger.info("Users have been successfully created!")
        except Exception as e:
            self.session.rollback()
            self.logger.error(f"An error occurred while creating users: {e}")

    def create_customers(self):
        try:
            for customer_data in self.CUSTOMERS.values():
                customer = Customer(**customer_data)
                self.session.add(customer)
            self.session.commit()
            self.logger.info("Customers have been successfully created!")
        except Exception as e:
            self.session.rollback()
            self.logger.error(f"An error occurred while creating customers: {e}")

    def create_contracts(self):
        try:
            for contract_data in self.CONTRACTS.values():
                contract = Contract(**contract_data)
                self.session.add(contract)
            self.session.commit()
            self.logger.info("Contracts have been successfully created!")
        except Exception as e:
            self.session.rollback()
            self.logger.error(f"An error occurred while creating contracts: {e}")

    def drop_all_tables(self):
        try:
            self.logger.info("Dropping all tables...")
            self.base.metadata.drop_all(bind=self.engine, checkfirst=True)
            self.logger.info("All tables dropped successfully.")
        except Exception as e:
            self.logger.error(f"An error has occurred while dropping the tables: {e}", exc_info=False)

    def create_all_tables(self):
        try:
            self.logger.info("Creating all tables...")
            self.base.metadata.create_all(bind=self.engine, checkfirst=True)
            self.logger.info("All tables created successfully.")
        except Exception as e:
            self.logger.error(f"An error has occurred while creating the tables: {e}", exc_info=False)

    def init_base(self):

        try:
            self.drop_all_tables()
            self.create_all_tables()
        except Exception as e:
            self.logger.error(f"An error has occurred while resetting the base: {e}", exc_info=False)
        else:
            self.create_roles()
            self.create_users()
            self.create_customers()
            self.create_contracts()
        finally:
            self.session.close()

if __name__ == "__main__":
    # Config Loggers
    logger_config = LoggerConfig()
    logger = logger_config.get_logger()
    sentry_logger = SentryLogger()

    # config session
    session_config = DatabaseConfig(logger)
    session = session_config.db_session_local()
    engine = session_config.engine
    base = session_config.BASE
    initializer = DatabaseInitializer(session, engine, base, logger)
    initializer.init_base()
