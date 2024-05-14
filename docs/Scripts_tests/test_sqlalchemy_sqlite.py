from sqlalchemy import create_engine
from epic_events.models import Base

db_path = "sqlite:///test_alchemy.db"  # 3eme / pour stocker dans le même dossier que le script
engine = create_engine(db_path)
try:
    conn = engine.connect()
    Base.metadata.drop_all(bind=conn)
    Base.metadata.create_all(bind=conn)
    print("success !!!")
except Exception as ex:
    print(ex)
