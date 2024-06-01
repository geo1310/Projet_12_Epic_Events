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
- DB_USER : Nom d'utilisateur de la base de données.
- DB_PASSWORD : Mot de passe de la base de données.
- DB_HOST : Hôte de la base de données.
- DB_PORT_POSTGRE : Port de la base de données PostgreSQL.
- DB_NAME : Nom de la base de données.

"""

# Charge les variables d'environnement depuis le fichier .env
load_dotenv(override=True)

# Informations de connexion à la base de données depuis les variables d'environnement
db_user = os.environ.get("DB_USER")
db_password = os.environ.get("DB_PASSWORD")
db_host = os.environ.get("DB_HOST")
db_port = os.environ.get("DB_PORT_POSTGRE")
db_name = os.environ.get("DB_NAME")

# URL de connexion à la base de données PostgreSQL
db_url = f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}?client_encoding=utf8"
#db_url = f"postgresql+pg8000://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

# Créer l'engine SQLAlchemy
engine = create_engine(db_url)

# Créer une sessionmaker pour interagir avec la base de données
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Déclarer une base de données SQLAlchemy pour être utilisée dans les modèles
Base = declarative_base()
