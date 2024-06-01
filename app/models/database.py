import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

"""
Ce module configure la connexion à une base de données PostgreSQL en utilisant SQLAlchemy.

Fonctionnalités :
- Charge les variables d'environnement depuis un fichier .env pour les informations de connexion à la base de données.
- Construit l'URL de connexion à la base de données PostgreSQL en utilisant les informations chargées.
- Crée un engine SQLAlchemy pour interagir avec la base de données.
- Définit une sessionmaker pour gérer les sessions de la base de données.
- Déclare une base de données SQLAlchemy pour être utilisée dans les modèles ORM.

Variables d'environnement attendues :
- DB_USE : Type d'utilisation de la base de données, "locale" pour une utilisation en local ou "render.com" pour une utilisation avec render.com.
- DB_USER : Nom d'utilisateur de la base de données.
- DB_PASSWORD_LOCAL : Mot de passe de la base de données pour une utilisation locale.
- DB_PASSWORD_RENDER : Mot de passe de la base de données pour une utilisation avec render.com.
- DB_HOST_LOCAL : Hôte de la base de données pour une utilisation locale.
- DB_HOST_RENDER : Hôte de la base de données pour une utilisation avec render.com.
- DB_PORT_POSTGRE : Port de la base de données PostgreSQL.
- DB_NAME : Nom de la base de données.

"""

# Charge les variables d'environnement depuis le fichier .env
load_dotenv(override=True)

# Informations de connexion à la base de données en locale ou à distance selon db_use
db_use = os.environ.get("DB_USE")
db_user = os.environ.get("DB_USER")
db_port = os.environ.get("DB_PORT_POSTGRE")
db_name = os.environ.get("DB_NAME")

if db_use == "local":
    db_password = os.environ.get("DB_PASSWORD_LOCAL")
    db_host = os.environ.get("DB_HOST_LOCAL")
elif db_use == "render.com":
    db_password = os.environ.get("DB_PASSWORD_RENDER")
    db_host = os.environ.get("DB_HOST_RENDER")


# URL de connexion à la base de données PostgreSQL
# psycopg2, pg8000: drivers python pour interagir avec des bases de données PostgreSQL.
db_url = f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}?client_encoding=utf8"


# Créer l'engine SQLAlchemy.
# L'engine est responsable de l'exécution des requêtes SQL et de la gestion des connexions à la base de données.
engine = create_engine(db_url)

# Créer une sessionmaker pour interagir avec la base de données.
# La fonction sessionmaker est utilisée pour créer un générateur de sessions SQLAlchemy.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Déclarer une base de données SQLAlchemy pour être utilisée dans les modèles
# Cela permet à SQLAlchemy de suivre les modifications apportées aux classes de modèle et de les refléter dans la base.
Base = declarative_base()
