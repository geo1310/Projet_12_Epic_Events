import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from epic_events.models import Base, Employee

load_dotenv()

db_user = os.environ.get("DB_USER")
db_password = os.environ.get("DB_PASSWORD")
db_host = os.environ.get("DB_HOST")
db_port = os.environ.get("DB_PORT_POSTGRE")
db_name = os.environ.get("DB_NAME")
db_url = f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

engine = create_engine(db_url)

try:
    # Création des tables dans la base
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    print("success !!!")


except Exception as ex:
    print(ex)
