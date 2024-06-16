import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, exc
from sqlalchemy.orm import declarative_base, sessionmaker

from utils.logger_config import LoggerConfig


class DatabaseConfig:
    """
    Classe pour la configuration et la connexion à une base de données PostgreSQL en utilisant SQLAlchemy.

    Attributs:
        BASE (DeclarativeMeta): Classe de base pour les modèles SQLAlchemy.
        logger (Logger): Logger pour enregistrer les messages de journalisation.
        db_use (str): Type d'utilisation de la base de données ("local" ou "render.com").
        db_user (str): Nom d'utilisateur de la base de données.
        db_port (str): Port de la base de données PostgreSQL.
        db_name (str): Nom de la base de données.
        db_password (str): Mot de passe de la base de données.
        db_host (str): Hôte de la base de données.
        db_url (str): URL de connexion à la base de données PostgreSQL.
        engine (Engine): Engine SQLAlchemy pour interagir avec la base de données.
        db_session_local (sessionmaker): Sessionmaker pour gérer les sessions de la base de données.
    """

    BASE = declarative_base()

    def __init__(self, logger):
        self.logger = logger
        self._load_env_variables()
        self._configure_database()

    def _load_env_variables(self):
        try:
            file_env_path = Path(__file__).parent.parent / ".env"
            if not os.path.exists(file_env_path):
                raise FileNotFoundError(f"File {file_env_path} not found.")

            load_dotenv(file_env_path, override=True)

            self.db_use = os.environ["DB_USE"]
            self.db_user = os.environ["DB_USER"]
            self.db_port = os.environ["DB_PORT_POSTGRE"]
            self.db_name = os.environ["DB_NAME"]

            self.logger.info(f"Variables d'environnement chargées depuis {file_env_path}")
        except FileNotFoundError as e:
            self.logger.error(e)
            sys.exit(1)
        except KeyError as e:
            self.logger.error(f"Erreur lors du chargement des variables d'environnement depuis {file_env_path}: {e}")
            sys.exit(1)

    def _configure_database(self):
        """
        Configure la connexion à la base de données PostgreSQL en utilisant les variables d'environnement chargées.
        """
        try:
            if self.db_use == "local":
                self.db_password = os.environ["DB_PASSWORD_LOCAL"]
                self.db_host = os.environ["DB_HOST_LOCAL"]
            elif self.db_use == "render.com":
                self.db_password = os.environ["DB_PASSWORD_RENDER"]
                self.db_host = os.environ["DB_HOST_RENDER"]
            else:
                raise ValueError("DB_USE must be either 'local' or 'render.com'")

            self.db_url = f"postgresql+psycopg2://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}?client_encoding=utf8"
            self.engine = create_engine(self.db_url)

            self._test_connection()

            self.db_session_local = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

        except KeyError as e:
            self.logger.error(f"Missing required environment variable: {e}")
            sys.exit(1)
        except ValueError as e:
            self.logger.error(f"Invalid value for environment variable: {e}")
            sys.exit(1)
        except Exception as e:
            self.logger.error(f"An unexpected error occurred: {e}")
            sys.exit(1)

    def _test_connection(self):
        """
        Teste la connexion à la base de données et enregistre un message de succès ou d'échec.
        """
        try:
            connection = self.engine.connect()
            self.logger.info("Database connection successful")
            connection.close()
        except exc.SQLAlchemyError as e:
            self.logger.error(f"An error occurred during the database connection test: {e}")
            sys.exit(1)


# Utilisation de la classe DatabaseConfig
if __name__ == "__main__":
    logger_config = LoggerConfig()
    logger = logger_config.get_logger()
    db_config = DatabaseConfig(logger)
