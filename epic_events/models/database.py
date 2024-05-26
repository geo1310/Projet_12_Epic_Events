import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Charge les variables d'environnement depuis le fichier .envrc
load_dotenv(override=True)

# Informations de connexion à la base de données depuis les variables d'environnement
db_user = os.environ.get("DB_USER")
db_password = os.environ.get("DB_PASSWORD")
db_host = os.environ.get("DB_HOST")
db_port = os.environ.get("DB_PORT_POSTGRE")
db_name = os.environ.get("DB_NAME")

# URL de connexion à la base de données PostgreSQL
db_url = f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

# Créer l'engine SQLAlchemy
engine = create_engine(db_url)

# Créer une sessionmaker pour interagir avec la base de données
Session = sessionmaker(bind=engine)

# Déclarer une base de données SQLAlchemy pour être utilisée dans les modèles
Base = declarative_base()
