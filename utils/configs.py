import os
import yaml
import configparser

from sqlalchemy import select
from sqlalchemy.orm import Session

from .db import engine
from .db.models import Host

from . import settings

NEBULA_CONTROL_DIR = os.environ.get("NEBULA_CONTROL_DIR")
CLIENT_CONFIG_PATH = f"{NEBULA_CONTROL_DIR}/defaults/client.yml"
LIGHTHOUSE_CONFIG_PATH = f"{NEBULA_CONTROL_DIR}/defaults/lighthouse.yml"
NETWORK_CONFIG_PATH = f"{NEBULA_CONTROL_DIR}/defaults/nebula1.network"
MAC_NETWORK_CONFIG_PATH = f"{NEBULA_CONTROL_DIR}/defaults/nebula"

# load config yml
def load(path):
    with open(path, "r") as yf:
        config_yml = list(yaml.safe_load_all(yf))

    # assert successful load
    if not config_yml:
        raise Exception(f"Failed to load {path}")

    return config_yml[0]


# dump config yml
def dump(config, path):
    with open(path, "w") as yf:
        yaml.dump(config, yf, default_flow_style=False, sort_keys=False)

# generate client config by populating it with existing lighthouses
def generate_client_config(nebula_port, destination, no_admin):
    with Session(engine) as session:
        config = load(CLIENT_CONFIG_PATH)
        lighthouses_query = select(Host).where(Host.is_lighthouse == True)
        lighthouses = session.scalars(lighthouses_query).all()

        # set port
        config["listen"]["port"] = nebula_port

        # add admin access if allowed
        if no_admin:
            config["firewall"]["inbound"] = [{"port":"any","proto":"icmp","group":"any"}]
        # initialize static host map
        if not config["static_host_map"]:
            config["static_host_map"] = dict()

        # initialize lighthouse hosts
        if not config["lighthouse"]["hosts"]:
            config["lighthouse"]["hosts"] = list()

        # add all lighthouse info to static host map and hosts
        for lighthouse in lighthouses:
            config["static_host_map"][lighthouse.nebula_ip] = [
                f"{lighthouse.public_ip}:{lighthouse.nebula_port}"
            ]
            config["lighthouse"]["hosts"].append(lighthouse.nebula_ip)

        dump(config, destination)


# generate lighthouse config by populating it with existing lighthouses
def generate_lighthouse_config(public_ip, nebula_ip, nebula_port, destination):
    with Session(engine) as session:
        config = load(LIGHTHOUSE_CONFIG_PATH)
        lighthouses_query = select(Host).where(Host.is_lighthouse == True)
        lighthouses = session.scalars(lighthouses_query).all()

        # set port
        config["listen"]["port"] = nebula_port

        # set dns host
        config["lighthouse"]["dns"]["host"] = nebula_ip

        # initialize static host map
        if not config["static_host_map"]:
            config["static_host_map"] = {nebula_ip: [f"{public_ip}:{nebula_port}"]}

        # add all lighthouse info to statis host map and hosts
        for lighthouse in lighthouses:
            config["static_host_map"][lighthouse.nebula_ip] = [
                f"{lighthouse.public_ip}:{lighthouse.nebula_port}"
            ]

        dump(config, destination)


# generate network config
def generate_network_config(destination, node_config, mac_os):
    with Session(engine) as session:
        network_config = configparser.ConfigParser()
        network_config.optionxform = str
        network_config.read(NETWORK_CONFIG_PATH)

        lighthouses_query = select(Host).where(Host.is_lighthouse == True)
        lighthouses = session.scalars(lighthouses_query).all()

        # check if current node is a lighthouse and is serving dns; if yes add to resolvers
        node = load(node_config)["lighthouse"]
        if node["am_lighthouse"]:
            if node["serve_dns"]:
                # network_config["Network"]["DNS"] += f"{node['dns']['host']}:{node['dns']['port']} "
                network_config["Network"]["DNS"] += f"{node['dns']['host']} "

        # for each lighhouse in db, check if it is serving dns; if yes add to resolvers
        for lighthouse in lighthouses:
            lighthouse_config = load(f"{NEBULA_CONTROL_DIR}/hosts/{lighthouse.name}/config.yml")[
                "lighthouse"
            ]
            if lighthouse_config["serve_dns"]:
                network_config["Network"][
                    "DNS"
                ] += f"{lighthouse_config['dns']['host']} "

        network_config["Network"]["Domains"] = settings.get("domain")

        if not mac_os:
            with open(destination, "w") as cf:
                network_config.write(cf)

        if mac_os:
            config_string = ""
            for lighthouse in lighthouses:
                lighthouse_config = load(f"{NEBULA_CONTROL_DIR}/hosts/{lighthouse.name}/config.yml")[
                    "lighthouse"
                        ]
                if lighthouse_config["serve_dns"]:
                    config_string+="nameserver "+lighthouse_config['dns']['host']+"\n"
            with open(destination, "w") as cf:
                cf.write(config_string)


def generate_dnsmasq_config(domain_name, nebula_ip, nebula_port, destination):
    config_string = "port=53\nresolv-file=/opt/upstream-dns.conf\nserver="
    config_string += f"/{domain_name}/{nebula_ip}#{nebula_port}"
    with open(destination, "w") as cf:
                cf.write(config_string)