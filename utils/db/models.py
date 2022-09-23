from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

# base class for declarative functions
Base = declarative_base()

# hosts relation
class Host(Base):
    __tablename__ = "host"

    id = Column(Integer, primary_key=True)
    name = Column(String(256), nullable=False)
    public_ip = Column(String(20), nullable=True)
    nebula_ip = Column(String(20), nullable=False)
    nebula_port = Column(Integer, nullable=False, default=4242)
    ssh_user = Column(String(256), nullable=False, default="root")
    ssh_port = Column(Integer, nullable=False, default=22)
    is_lighthouse = Column(Boolean, default=False)
    groups = relationship("HostGroup", cascade="all, delete", passive_deletes=True)


# host groups relation model
class HostGroup(Base):
    __tablename__ = "hostgroup"

    id = Column(Integer, primary_key=True)
    host_id = Column(Integer, ForeignKey("host.id", ondelete="CASCADE"))
    name = Column(String(256))
