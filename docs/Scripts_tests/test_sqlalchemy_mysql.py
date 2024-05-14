import os
from dotenv import load_dotenv
import pymysql
from sqlalchemy import create_engine
from epic_events.models import Base

load_dotenv()
pymysql.install_as_MySQLdb()

db_user = os.environ.get("DB_USER")
db_password = os.environ.get("DB_PASSWORD")
db_host = os.environ.get("DB_HOST")
db_port = os.environ.get("DB_PORT_MYSQL")
db_name = os.environ.get("DB_NAME")
db_url = f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

engine = create_engine(db_url)

try:
    conn = engine.connect()
    Base.metadata.drop_all(bind=conn)
    Base.metadata.create_all(bind=conn)
    print("success !!!")
except Exception as ex:
    print(ex)
