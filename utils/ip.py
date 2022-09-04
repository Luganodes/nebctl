#! /usr/bin/env python3

"""
depends on:
  - ipaddress
"""

from sqlalchemy import select
from sqlalchemy.orm import Session
from ipaddress import ip_address, ip_network

from .db import engine
from .db.models import Host

# get latest IP matching the given range (if any)
def generate_nebula_IP(network="0.0.0.0/24"):
    with Session(engine) as session:
        used_IPs_query = select(Host.nebula_ip)
        used_IPs = set(map(lambda ip: int(ip_address(ip)), session.scalars(used_IPs_query)))
        possible_IPs = set(map(int, ip_network(network).hosts()))
        return ip_address(sorted(possible_IPs - used_IPs)[0])
