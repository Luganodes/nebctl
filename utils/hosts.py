from sqlalchemy import select, delete, and_
from sqlalchemy.orm import Session

from .db import engine
from .db.models import Host, HostGroup

# get host by name
def get(name):
    with Session(engine) as session:
        target_host_query = select(Host).where(Host.name == name)
        target_host = session.scalars(target_host_query).one_or_none()
        return target_host


# get all hosts
def get_all():
    with Session(engine) as session:
        target_hosts_query = select(Host)
        target_hosts = session.scalars(target_hosts_query).all()
        return target_hosts


# get all groups of host
def get_groups(host_id):
    with Session(engine) as session:
        target_groups_query = select(HostGroup).where(HostGroup.host_id == host_id)
        target_groups = session.scalars(target_groups_query).all()
        return target_groups


# add new host to db
def add_host(
    name,
    public_ip,
    nebula_ip,
    nebula_port=4242,
    ssh_user="root",
    ssh_port=22,
    is_lighthouse=False,
    groups=[],
):

    with Session(engine) as session:
        # try:
        # create host
        new_host = Host(
            name=name,
            public_ip=public_ip,
            nebula_ip=nebula_ip,
            nebula_port=nebula_port,
            ssh_user=ssh_user,
            ssh_port=ssh_port,
            is_lighthouse=is_lighthouse,
        )
        session.add(new_host)
        session.commit()

        # add groups to host
        for group in groups:
            new_group = HostGroup(
                host_id=new_host.id,
                name=group,
            )
            session.add(new_group)
        session.commit()
        # except:
        #     session.rollback()


# edit details of the given host
def edit_host(
    id,
    name=None,
    public_ip=None,
    nebula_ip=None,
    nebula_port=None,
    ssh_user=None,
    ssh_port=None,
    is_lighthouse=None,
):
    with Session(engine) as session:
        try:
            target_host_query = select(Host).where(Host.id == id)
            target_host = session.scalars(target_host_query).one()

            if name is not None:
                target_host.name = name
            if public_ip is not None:
                target_host.public_ip = public_ip
            if nebula_ip is not None:
                target_host.nebula_ip = nebula_ip
            if nebula_port is not None:
                target_host.nebula_port = nebula_port
            if ssh_user is not None:
                target_host.ssh_user = ssh_user
            if ssh_port is not None:
                target_host.ssh_port = ssh_port
            if is_lighthouse is not None:
                target_host.is_lighthouse = is_lighthouse

            session.commit()
        except:
            session.rollback()


# delete host
def delete_host(id):
    with Session(engine) as session:
        try:
            target_host_query = delete(Host).where(Host.id == id)
            session.execute(target_host_query)
            session.commit()

            target_group_query = delete(HostGroup).where(HostGroup.host_id == id)
            session.execute(target_group_query)
            session.commit()
        except:
            session.rollback()


# add host to group
def add_group(host_id, group_name):
    with Session(engine) as session:
        try:
            new_group = HostGroup(
                host_id=host_id,
                name=group_name,
            )
            session.add(new_group)
            session.commit()
        except:
            session.rollback()


# remove host from group
def remove_group(host_id, group_name):
    with Session(engine) as session:
        try:
            target_group_query = delete(HostGroup).where(
                and_(HostGroup.host_id == host_id, HostGroup.name == group_name)
            )
            session.execute(target_group_query)
            session.commit()
        except:
            session.rollback()
