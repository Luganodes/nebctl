import yaml

from sqlalchemy import select
from sqlalchemy.orm import Session

from .db import engine
from .db.models import Host

CLIENT_CONFIG_PATH = "defaults/client.yml"
LIGHTHOUSE_CONFIG_PATH = "defaults/lighthouse.yml"

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
def generate_client_config(nebula_port, destination):
    with Session(engine) as session:
        config = load(CLIENT_CONFIG_PATH)
        lighthouses_query = select(Host).where(Host.is_lighthouse == True)
        lighthouses = session.scalars(lighthouses_query).all()

        # set port
        config["listen"]["port"] = nebula_port

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
