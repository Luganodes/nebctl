"""
depends on:
  - ipaddress
"""

import numpy as np

from sqlalchemy import select
from sqlalchemy.orm import Session
from ipaddress import ip_address, ip_network

from .db import engine
from .db.models import Host

# get latest IP matching the given range (if any)
def generate_nebula_IP(net_ip="0.0.0.0", net_mask="255.255.0.0", lighthouse=False):
    with Session(engine) as session:
        used_IPs_query = select(Host.nebula_ip)
        used_IPs = set(map(lambda ip: int(ip_address(ip)), session.scalars(used_IPs_query)))
        possible_IPs = set(map(int, ip_network(f"{net_ip}/{net_mask}").hosts()))
        available_IPs = np.array(sorted(possible_IPs - used_IPs), dtype=int)

        # reserve first 255 addresses for lighthouses
        if lighthouse:
            target_IPs = available_IPs[available_IPs < (min(possible_IPs) + 255)]
        else:
            target_IPs = available_IPs[available_IPs >= (min(possible_IPs) + 255)]

        # throw error if all IPs exhausted
        if len(target_IPs) == 0:
            raise Exception(f"Unable to autogenerate nebula IP: range exhausted!")

        return str(ip_address(int(target_IPs[0])))
