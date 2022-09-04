from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

# base class for declarative functions
Base = declarative_base()

# hosts relation
class Host(Base):
    __tablename__ = "host"

    id = Column(Integer, primary_key=True)
    name = Column(String(256), nullable=False)
    public_ip = Column(String(20), nullable=False)
    nebula_ip = Column(String(20), nullable=False)
    nebula_port = Column(Integer, nullable=False, default=4242)
    ssh_user = Column(String(256), nullable=False, default="root")
    ssh_port = Column(Integer, nullable=False, default=22)
    is_lighthouse = Column(Boolean, default=False)
    groups = relationship("Group", cascade="all, delete")


# groups relation model
class Group(Base):
    __tablename__ = "group"

    id = Column(Integer, primary_key=True)
    host_id = Column(Integer, ForeignKey("host.id"))
    group_name = Column(String(256))
