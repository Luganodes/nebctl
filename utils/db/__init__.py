import os
from sqlalchemy import create_engine
from .models import Base

NEBULA_CONTROL_DIR = os.environ.get("NEBULA_CONTROL_DIR")
DB_PATH = "store/db.sqlite"

# connect to the database
engine = create_engine(f"sqlite:///{NEBULA_CONTROL_DIR}/{DB_PATH}")

# generate schema
Base.metadata.create_all(engine)
