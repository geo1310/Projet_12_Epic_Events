import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, exc
from sqlalchemy.orm import declarative_base, sessionmaker
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

"""
Ce module configure la connexion à une base de données PostgreSQL en utilisant SQLAlchemy.

Fonctionnalités :
- Charge les variables d'environnement depuis un fichier .env pour les informations de connexion à la base de données.
- Construit l'URL de connexion à la base de données PostgreSQL en utilisant les informations chargées.
- Crée un engine SQLAlchemy pour interagir avec la base de données.
- Définit une sessionmaker pour gérer les sessions de la base de données.
- Déclare une base de données SQLAlchemy pour être utilisée dans les modèles ORM.
- Gère les exceptions liées à la configuration de la base de données et au chargement des variables d'environnement.

Variables d'environnement attendues :
- DB_USE : Type d'utilisation de la base de données, "local" pour une utilisation en local ou "render.com" pour une utilisation avec render.com.
- DB_USER : Nom d'utilisateur de la base de données.
- DB_PASSWORD_LOCAL : Mot de passe de la base de données pour une utilisation locale.
- DB_PASSWORD_RENDER : Mot de passe de la base de données pour une utilisation avec render.com.
- DB_HOST_LOCAL : Hôte de la base de données pour une utilisation locale.
- DB_HOST_RENDER : Hôte de la base de données pour une utilisation avec render.com.
- DB_PORT_POSTGRE : Port de la base de données PostgreSQL.
- DB_NAME : Nom de la base de données.

Exceptions gérées :
- KeyError : Levée si une variable d'environnement requise est manquante.
- ValueError : Levée si la valeur de DB_USE est invalide.
- SQLAlchemyError : Levée en cas d'erreur lors de la configuration de la connexion à la base de données.
- Exception : Levée pour toute autre erreur inattendue.
"""

# Charge les variables d'environnement depuis le fichier .env
load_dotenv(override=True)

try:
    # Informations de connexion à la base de données en locale ou à distance selon db_use
    db_use = os.environ['DB_USE']
    db_user = os.environ['DB_USER']
    db_port = os.environ['DB_PORT_POSTGRE']
    db_name = os.environ['DB_NAME']

    if db_use == "local":
        db_password = os.environ['DB_PASSWORD_LOCAL']
        db_host = os.environ['DB_HOST_LOCAL']
    elif db_use == "render.com":
        db_password = os.environ['DB_PASSWORD_RENDER']
        db_host = os.environ['DB_HOST_RENDER']
    else:
        raise ValueError("DB_USE must be either 'local' or 'render.com'")

    # URL de connexion à la base de données PostgreSQL
    db_url = f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}?client_encoding=utf8"

    # Créer l'engine SQLAlchemy.
    engine = create_engine(db_url)
    logger.info("Database engine created successfully")

    # Créer une sessionmaker pour interagir avec la base de données.
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    logger.info("Session maker created successfully")

    # Déclarer une base de données SQLAlchemy pour être utilisée dans les modèles
    Base = declarative_base()
    logger.info("Base declarative created successfully")

except KeyError as e:
    logger.error(f"Missing required environment variable: {e}")
    raise
except ValueError as e:
    logger.error(f"Invalid value for environment variable: {e}")
    raise
except exc.SQLAlchemyError as e:
    logger.error(f"An error occurred while setting up the database connection: {e}")
    raise
except Exception as e:
    logger.error(f"An unexpected error occurred: {e}")
    raise
