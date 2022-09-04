from sqlalchemy import create_engine
from .models import Base

DB_PATH = "store/db.sqlite"

# connect to the database
engine = create_engine(f"sqlite:///{DB_PATH}")

# generate schema
Base.metadata.create_all(engine)
