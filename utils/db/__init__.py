import os
from sqlalchemy import create_engine
from .models import Base

NEBULA_CONTROL_DIR = os.environ.get("NEBULA_CONTROL_DIR")
DB_PATH = f"{NEBULA_CONTROL_DIR}/store/db.sqlite"

# connect to the database
engine = create_engine(f"sqlite:///{DB_PATH}")

# generate schema
Base.metadata.create_all(engine)
